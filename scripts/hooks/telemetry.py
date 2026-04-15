#!/usr/bin/env python3
import sys
import json
import os
from datetime import datetime

def log_telemetry(event_type, data):
    # Log to a file in the project directory
    project_dir = os.environ.get('GEMINI_PROJECT_DIR', '.')
    log_dir = os.path.join(project_dir, '.gemini', 'telemetry')
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

def main():
    try:
        # Read the JSON payload from stdin
        input_data = sys.stdin.read()
        if not input_data:
            # Silence is mandatory for hooks if no action is taken
            return

        payload = json.loads(input_data)
        
        # Identify the event type based on the structure
        # (Simplified for the prototype)
        event_type = "unknown"
        if "tool" in payload:
            event_type = "AfterTool"
            telemetry_data = {
                "tool": payload.get("tool"),
                "arguments": payload.get("arguments"),
                "status": "success" if not payload.get("isError") else "error"
            }
        elif "response" in payload:
            event_type = "AfterModel"
            usage = payload.get("usage_metadata", {})
            telemetry_data = {
                "input_tokens": usage.get("prompt_token_count", 0),
                "output_tokens": usage.get("candidates_token_count", 0),
                "total_tokens": usage.get("total_token_count", 0)
            }
        else:
            telemetry_data = payload

        log_telemetry(event_type, telemetry_data)

        # MANDATORY: Print original or modified JSON back to stdout
        # For logging-only hooks, we just pass through the input
        print(json.dumps(payload))

    except Exception as e:
        # Debug via stderr only
        print(f"Telemetry Hook Error: {str(e)}", file=sys.stderr)
        # Even on error, pass through original data if possible to not break the loop
        if 'input_data' in locals():
            print(input_data)

if __name__ == "__main__":
    main()
