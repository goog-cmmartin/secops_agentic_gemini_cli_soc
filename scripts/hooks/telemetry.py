#!/usr/bin/env python3
import sys
import json
import os
from datetime import datetime

# Debug log location
DEBUG_LOG = "/tmp/asoc_telemetry_debug.log"

def debug(msg):
    with open(DEBUG_LOG, 'a') as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {msg}\n")

def log_telemetry(event_type, data):
    # Log to a file in the project directory
    project_dir = os.environ.get('GEMINI_PROJECT_DIR', os.getcwd())
    log_dir = os.path.join(project_dir, '.gemini', 'telemetry')
    
    debug(f"Attempting to log {event_type} to {log_dir}")
    
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'events.jsonl')
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": os.environ.get('GEMINI_SESSION_ID', 'unknown'),
            "event_type": event_type,
            "data": data
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        debug("Log entry written successfully.")
    except Exception as e:
        debug(f"Failed to write log: {str(e)}")

def main():
    debug("Hook triggered.")
    try:
        # Read the JSON payload from stdin
        input_data = sys.stdin.read()
        if not input_data:
            debug("Empty input received.")
            return

        payload = json.loads(input_data)
        debug(f"Payload parsed successfully. Keys: {list(payload.keys())}")
        
        event_type = "unknown"
        if "tool" in payload:
            event_type = "AfterTool"
            telemetry_data = {
                "tool": payload.get("tool"),
                "status": "success" if not payload.get("isError") else "error"
            }
        elif "response" in payload:
            event_type = "AfterModel"
            usage = payload.get("usage_metadata", {})
            telemetry_data = {
                "input_tokens": usage.get("prompt_token_count", 0),
                "output_tokens": usage.get("candidates_token_count", 0)
            }
        else:
            telemetry_data = {"raw_keys": list(payload.keys())}

        log_telemetry(event_type, telemetry_data)

        # MANDATORY: Print original JSON back to stdout
        print(json.dumps(payload))

    except Exception as e:
        debug(f"Critical Main Error: {str(e)}")
        # Pass through input to not break CLI loop
        if 'input_data' in locals():
            print(input_data)

if __name__ == "__main__":
    main()
