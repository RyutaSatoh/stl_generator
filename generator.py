import sys
import os
import re
import time
import datetime

# Add gemini_proxy to path
proxy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_proxy", "src")
sys.path.append(proxy_path)

try:
    from gemini_proxy.core import GeminiProxy
except ImportError:
    raise ImportError("Could not import GeminiProxy. Check path: " + proxy_path)

def log_debug(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("generator_debug.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def generate_scad(prompt, work_dir, resume_session=False, system_prompt_path="OPENSCAD_PROMPT.md"):
    log_debug(f"Starting generation for prompt: {prompt[:50]}... in {work_dir} (resume={resume_session})")
    
    # Clean previous outputs in work_dir if not resuming (or even if resuming, maybe we want fresh files?)
    # If resuming, we might want to keep old files as history? 
    # But the agent overwrites model.scad.
    # Let's clear specific target files to ensure we detect new ones.
    target_files = ["model.scad", "preview.png", "output.stl"]
    for f in target_files:
        p = os.path.join(work_dir, f)
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass

    with open(system_prompt_path, "r") as f:
        system_content = f.read()
    
    # Initialize Proxy
    # cwd=work_dir ensures the session history is stored there
    proxy = GeminiProxy(cwd=work_dir, resume_session=resume_session, cols=150, rows=500, debug=True)
    
    response_text = ""
    error_msg = None
    
    try:
        # Start Gemini
        log_debug("Starting Gemini Proxy process...")
        proxy.start(timeout=60)
        
        # Send command asynchronously
        log_debug("Sending prompt...")
        
        combined_prompt = f"{system_content}\n\nUser Request: {prompt}"
        
        proxy.send_command(combined_prompt, wait_for_response=False)
        log_debug("Prompt sent. Entering interaction loop.")
        
        # Interaction loop
        start_wait = time.time()
        last_action_time = time.time()
        
        while time.time() - start_wait < 300: # 5 minute total timeout
            lines = proxy.get_screen_content()
            screen_text = "\n".join(lines)
            
            # Check for final prompt (task completion)
            is_prompt_visible = "Type your message" in screen_text
            is_done_message_visible = "Generated Files:" in screen_text and "3." in screen_text
            
            if (is_prompt_visible or is_done_message_visible) and (time.time() - proxy._last_screen_update > 2.0):
                if "```" in screen_text or "User Request:" in screen_text:
                     log_debug("Final prompt or completion message detected.")
                     response_text = screen_text
                     break
            
            # Check for tool confirmation
            tool_keywords = ["WriteFile", "render_views", "export_stl"]
            has_tool = any(k in screen_text for k in tool_keywords)
            
            if has_tool and "Type your message" not in screen_text:
                if time.time() - proxy._last_screen_update > 2.0:
                    log_debug("Tool confirmation detected! Approving...")
                    proxy.send_input("y\r")
                    last_action_time = time.time()
                    time.sleep(2.0)
                    
            time.sleep(0.5)
            
        if not response_text:
             log_debug("Timeout reached. No final response text found.")
             response_text = "\n".join(proxy.get_screen_content())
             if "```" not in response_text:
                 error_msg = "Timeout or no code generated."

    except Exception as e:
        log_debug(f"Exception detected: {str(e)}")
        error_msg = f"Error using GeminiProxy: {str(e)}"
    finally:
        proxy.stop()
        log_debug("Gemini Proxy stopped.")

    if error_msg:
        return None, error_msg

    # Parse Code
    # Check for generated file in work_dir
    output_scad = os.path.join(work_dir, "model.scad")
    if os.path.exists(output_scad):
        try:
             with open(output_scad, "r") as f:
                 code = f.read()
             if code.strip():
                 log_debug(f"Found generated file {output_scad}.")
                 return code, None
        except Exception as e:
            log_debug(f"Failed to read {output_scad}: {e}")

    # Fallback to regex
    pattern = r"```(?:scad)?(.*?)```"
    matches = re.findall(pattern, response_text, re.DOTALL)
    
    if matches:
        matches.sort(key=len, reverse=True)
        code = matches[0].strip()
        log_debug("Code extracted from regex.")
        # If regex found code but file wasn't written, write it now?
        # The agent should have written it.
        return code, None
    else:
        debug_log_path = os.path.join(work_dir, "debug_response.log")
        with open(debug_log_path, "w") as f:
            f.write(response_text)
        log_debug(f"No code found. Response written to {debug_log_path}")
        return None, "No OpenSCAD code found in response or output file."
