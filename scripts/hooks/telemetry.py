#!/usr/bin/env python3
import sys
import json
import os
import re
from datetime import datetime

# Debug log location
DEBUG_LOG = "/tmp/asoc_telemetry_debug.log"

# Map of Agent Codes to Human Names
AGENT_MAP = {
    "PR-CDA-001": "triage",
    "AN-TWA-001": "analysis",
    "PR-CIR-001": "remediation",
    "OM-ANA-001": "scribe",
    "OM-STS-001": "sre",
    "ED-SCD-001": "detection_engineer"
}

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

def attribute_agent(payload):
    """Attempt to identify which sub-agent is running based on its unique code in the prompt."""
    try:
        # Search all messages (including system instructions if provided)
        messages = payload.get("llm_request", {}).get("messages", [])
        text_blob = ""
        for msg in messages:
            text_blob += msg.get("content", "")
        
        for code, name in AGENT_MAP.items():
            if code in text_blob:
                return name
    except:
        pass
    return "governor" # Default to governor if no sub-agent code found

def log_telemetry(event_type, data, raw_payload):
    project_dir = os.environ.get('GEMINI_PROJECT_DIR', os.getcwd())
    log_dir = os.path.join(project_dir, '.gemini', 'telemetry')
    
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'events.jsonl')
        
        soc_session_id = extract_soc_session_id(raw_payload)
        agent_name = attribute_agent(raw_payload)
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "internal_session_id": raw_payload.get("session_id") or os.environ.get('GEMINI_SESSION_ID', 'unknown'),
            "soc_session_id": soc_session_id,
            "attributed_agent": agent_name,
            "event_type": event_type,
            "data": data
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        debug(f"Logged {event_type} for Agent: {agent_name} (SOC ID: {soc_session_id})")
    except Exception as e:
        debug(f"Failed to write log: {str(e)}")

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            return

        payload = json.loads(input_data)
        event_name = payload.get("hook_event_name", "Advisory")
        telemetry_data = {}

        # AfterTool Schema Handling
        if "tool_name" in payload:
            telemetry_data = {
                "tool": payload.get("tool_name"),
                "status": "success" if not payload.get("tool_response", {}).get("error") else "error"
            }
        
        # AfterModel Schema Handling
        response_obj = payload.get("llm_response", {})
        usage = response_obj.get("usageMetadata") or response_obj.get("usage_metadata") or payload.get("usage_metadata", {})
        
        if usage:
            telemetry_data.update({
                "input_tokens": usage.get("promptTokenCount") or usage.get("prompt_token_count") or 0,
                "output_tokens": usage.get("candidatesTokenCount") or usage.get("candidates_token_count") or 0,
                "total_tokens": usage.get("totalTokenCount") or usage.get("total_token_count") or 0
            })

        log_telemetry(event_name, telemetry_data, payload)
        print(json.dumps(payload))

    except Exception as e:
        debug(f"Critical Hook Error: {str(e)}")
        if 'input_data' in locals():
            print(input_data)

if __name__ == "__main__":
    main()
