#!/usr/bin/env python3
import sys
import json
import os
import re
from datetime import datetime

# Debug log location
DEBUG_LOG = "/tmp/asoc_telemetry_debug.log"

def debug(msg):
    with open(DEBUG_LOG, 'a') as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {msg}\n")

def extract_soc_session_id(payload):
    """Attempt to find the SESS-YYYYMMDD-ID identifier in the prompt text."""
    try:
        messages = payload.get("llm_request", {}).get("messages", [])
        for msg in messages:
            content = msg.get("content", "")
            match = re.search(r"(SESS-\d{8}-\d+)", content)
            if match:
                return match.group(1)
    except:
        pass
    return None

def log_telemetry(event_type, data, raw_payload):
    # Use GEMINI_PROJECT_DIR if available, otherwise current directory
    project_dir = os.environ.get('GEMINI_PROJECT_DIR', os.getcwd())
    log_dir = os.path.join(project_dir, '.gemini', 'telemetry')
    
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'events.jsonl')
        
        # Try to find our SOC Session ID to link it to the incident
        soc_session_id = extract_soc_session_id(raw_payload)
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "internal_session_id": raw_payload.get("session_id") or os.environ.get('GEMINI_SESSION_ID', 'unknown'),
            "soc_session_id": soc_session_id,
            "event_type": event_type,
            "data": data
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        debug(f"Logged {event_type} (SOC ID: {soc_session_id}) to {log_file}")
    except Exception as e:
        debug(f"Failed to write log: {str(e)}")

def main():
    try:
        # Read the JSON payload from stdin
        input_data = sys.stdin.read()
        if not input_data:
            return

        payload = json.loads(input_data)
        
        # Determine the event type from the official hook_event_name
        event_name = payload.get("hook_event_name", "Advisory")
        telemetry_data = {}

        # Handle AfterTool structure
        if "tool_name" in payload:
            telemetry_data = {
                "tool": payload.get("tool_name"),
                "status": "success" if not payload.get("tool_response", {}).get("error") else "error"
            }
        
        # Handle AfterModel structure (including the nested llm_response)
        response_obj = payload.get("llm_response", {})
        usage = response_obj.get("usageMetadata") or response_obj.get("usage_metadata") or payload.get("usage_metadata", {})
        
        if usage:
            telemetry_data.update({
                "input_tokens": usage.get("promptTokenCount") or usage.get("prompt_token_count") or 0,
                "output_tokens": usage.get("candidatesTokenCount") or usage.get("candidates_token_count") or 0,
                "total_tokens": usage.get("totalTokenCount") or usage.get("total_token_count") or 0
            })

        # Log the synthesized telemetry
        log_telemetry(event_name, telemetry_data, payload)

        # MANDATORY: Print original JSON back to stdout
        print(json.dumps(payload))

    except Exception as e:
        debug(f"Critical Hook Error: {str(e)}")
        if 'input_data' in locals():
            print(input_data)

if __name__ == "__main__":
    main()
