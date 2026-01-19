from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Job
from worker import start_worker
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stl_generator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_request
def create_tables():
    # Create tables if they don't exist
    # In production, use migrations (Flask-Migrate)
    db.create_all()

@app.route('/')
def index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('index.html', jobs=jobs)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            job = Job(prompt=prompt)
            db.session.add(job)
            db.session.commit()
            # New job: resume=False
            start_worker(app, job.id, resume=False)
            flash('Job started!', 'success')
            return redirect(url_for('detail', job_id=job.id))
    return render_template('create.html')

@app.route('/job/<int:job_id>')
def detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('detail.html', job=job)

@app.route('/job/<int:job_id>/revise', methods=['POST'])
def revise(job_id):
    job = Job.query.get_or_404(job_id)
    new_prompt = request.form.get('prompt')
    
    if new_prompt:
        # Update existing job prompt and status
        job.prompt = new_prompt
        job.status = 'pending'
        job.error_message = None
        db.session.commit()
        
        # Resume session with 'latest'
        start_worker(app, job.id, resume='latest')
        
        flash('Job revision started!', 'success')
        return redirect(url_for('detail', job_id=job.id))
    
    return redirect(url_for('detail', job_id=job_id))

@app.route('/job/<int:job_id>/retry', methods=['POST'])
def retry(job_id):
    job = Job.query.get_or_404(job_id)
    if job.status in ['failed', 'completed']:
        job.status = 'pending'
        job.error_message = None
        db.session.commit()
        # Retry uses default resume=False (restart session?) 
        # or we could make it configurable. 
        # For now, restart fresh seems safer for "Retry".
        start_worker(app, job.id, resume=False)
        flash('Retrying job...', 'info')
    return redirect(url_for('detail', job_id=job.id))

@app.route('/job/<int:job_id>/delete', methods=['POST'])
def delete(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    # Optionally delete files here
    flash('Job deleted.', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure static/jobs exists
    os.makedirs(os.path.join(app.static_folder, 'jobs'), exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)