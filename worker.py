import threading
import os
import shutil
import time
from models import db, Job
from generator import generate_scad

# Global lock to ensure only one generation happens at a time
generation_lock = threading.Lock()

def process_job(app, job_id, resume=False):
    """
    Background task to run the generation pipeline.
    """
    prompt_text = ""
    
    # 1. Update status to processing and fetch prompt
    with app.app_context():
        job = db.session.get(Job, job_id)
        if not job:
            return
        prompt_text = job.prompt # Copy prompt to local variable
        print(f"Starting job {job_id} (resume={resume}): {prompt_text[:30]}...")
        job.status = 'processing'
        db.session.commit()

    # Define output directory for this job
    job_dir = os.path.join(app.static_folder, 'jobs', str(job_id))
    os.makedirs(job_dir, exist_ok=True)

    # Expected file locations in job_dir
    scad_file = os.path.join(job_dir, 'model.scad')
    stl_file = os.path.join(job_dir, 'output.stl')
    png_file = os.path.join(job_dir, 'preview.png')

    error_msg = None
    scad_code = None

    try:
        with generation_lock:
            # 1. Generate SCAD Code (and files via MCP)
            # Pass job_dir as work_dir so agent writes files there directly.
            # Pass resume_session flag.
            scad_code, err = generate_scad(prompt_text, job_dir, resume_session=resume)
            
            if err:
                raise Exception(err)
            
            if not scad_code:
                # If no code returned but file exists, read it
                if os.path.exists(scad_file):
                    with open(scad_file, 'r') as f:
                        scad_code = f.read()
                else:
                    raise Exception("No SCAD code generated.")

            # 2. Files are already in place if the agent followed instructions.
            # We just verify and log warnings.
            
            if not os.path.exists(png_file):
                print(f"Warning: {png_file} not found.")

            if not os.path.exists(stl_file):
                print(f"Warning: {stl_file} not found.")

    except Exception as e:
        error_msg = str(e)
        print(f"Job {job_id} failed: {e}")

    # 3. Update DB with results
    with app.app_context():
        job = db.session.get(Job, job_id)
        if not job:
            return 

        if error_msg:
            job.status = 'failed'
            job.error_message = error_msg
        else:
            job.status = 'completed'
            job.scad_code = scad_code
            # Paths relative to static/
            job.scad_filename = f'jobs/{job_id}/model.scad'
            job.stl_filename = f'jobs/{job_id}/output.stl'
            job.png_filename = f'jobs/{job_id}/preview.png'
        
        db.session.commit()
        print(f"Job {job_id} finished with status: {job.status}")

def start_worker(app, job_id, resume=False):
    thread = threading.Thread(target=process_job, args=(app, job_id, resume))
    thread.start()
