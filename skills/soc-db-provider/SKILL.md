---
name: soc-db-provider
description: Abstracts database access for the Agentic SOC, supporting Native SecOps Data Tables, SQLite, and Dolt.
---

# SOC Database Provider Skill

This skill provides a unified interface for sub-agents to read and write investigation state. It dynamically handles the syntax differences based on the **`STORAGE_PROVIDER`** and **`SESSION_ID`** environment variables, which are your **SINGLE SOURCE OF TRUTH**. 

## Configuration Context
- `STORAGE_PROVIDER`: (Values: `native`, `sqlite`, `dolt`) MUST be used to determine the backend.
- `SESSION_ID`: Unique namespace for the current investigation session.
- `TIMELINE_DATA_TABLE`: Name of the shared SecOps timeline table.
- `IOC_DATA_TABLE`: Name of the shared SecOps IOC table.
- `TUNING_DATA_TABLE`: Name of the shared SecOps tuning/suppression table.

## Instructions for the Model

### 1. Unified ID Generation (MANDATORY)
To ensure each record is globally unique and searchable, you MUST use the following format for all Primary Keys (`event_id`, `ioc_id`, `tuning_id`):
- **Format:** `[SESSION_ID]-[AGENT_NAME]-[SEQUENCE]`
- **Sequence Padding:** You MUST use two-digit padding for the sequence (e.g., `-01`, `-02`... `-99`).
- **Examples:** `20260412-89667-TRIAGE-01`, `20260412-89667-ANALYSIS-05`.

### 2. Incident Identification
- **Incident ID Format:** The `incident_id` MUST be the **numeric-only Case ID** from Google SecOps (e.g., `89667`). Do NOT add "INC-" prefixes or other strings.

### 3. Real-Time Clock Anchoring
To ensure an accurate and professional timeline, you MUST NOT guess the current time. 
**MANDATORY:** Before every write operation (database or Data Table), you MUST run the following command to get the official UTC timestamp:
`run_shell_command("date -u +'%Y-%m-%dT%H:%M:%SZ'")`
Use the output of this command as the value for all `timestamp` fields.

### 4. Unified State Interaction
Read the value of the **`STORAGE_PROVIDER`** and **`SESSION_ID`** environment variables before every interaction. 

**If `STORAGE_PROVIDER=native` (Default / Cloud-Native Mode):**
Do NOT use local shell commands for storage. You MUST document your activity by calling the Google SecOps MCP tools directly for EVERY write.
- **NO GUESSING:** You are STRICTLY FORBIDDEN from using hardcoded table names like `investigation_timeline` or `malicious_iocs`. You MUST use the EXACT values provided in the **`TIMELINE_DATA_TABLE`**, **`IOC_DATA_TABLE`**, and **`TUNING_DATA_TABLE`** environment variables.
- **STRICT COLUMN ORDERING:** You MUST follow the exact column order defined below in your JSON payload. 

- **To Log Activity:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting the table name in **`TIMELINE_DATA_TABLE`**.
  **Mandatory JSON Template:**
  ```json
  {
    "session_id": "SESSION_ID",
    "event_id": "[SESSION_ID]-[AGENT]-01",
    "incident_id": "89667",
    "timestamp": "[RESULT_OF_DATE_COMMAND]",
    "actor": "USER_ID",
    "agent": "your_agent_name",
    "action_taken": "Your concise summary",
    "duration_sec": "0",
    "step_count": "0"
  }
  ```

- **To Register IOCs:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting the table name in **`IOC_DATA_TABLE`**.
  **Mandatory JSON Template:**
  ```json
  {
    "session_id": "SESSION_ID",
    "ioc_id": "[SESSION_ID]-[AGENT]-IOC-01",
    "incident_id": "89667",
    "indicator_type": "IP",
    "indicator_value": "1.2.3.4",
    "is_malicious": "TRUE",
    "actor": "USER_ID",
    "agent": "your_agent_name"
  }
  ```

- **To Propose Tuning:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting the table name in **`TUNING_DATA_TABLE`**.
  **Mandatory JSON Template:**
  ```json
  {
    "session_id": "SESSION_ID",
    "tuning_id": "[SESSION_ID]-[AGENT]-TUNE-01",
    "incident_id": "89667",
    "rule_name": "RuleName",
    "exclusion_type": "ExclusionType",
    "exclusion_value": "ExclusionValue",
    "rule_logic": "YARA-L Snippet",
    "rationale": "Your rationale",
    "actor": "USER_ID",
    "agent": "your_agent_name"
  }
  ```

- **To Read Context:** Use `mcp_GoogleSecOps_list_data_table_rows` with a filter for the **`incident_id` AND `SESSION_ID`**.

**If `STORAGE_PROVIDER=sqlite` (Portable Local Mode):**
Use the `sqlite3` CLI. **CRITICAL:** Use the project's temporary directory for the database file:
- **CONCURRENCY LIMITATION:** SQLite is a single-user format. 
- **ERROR HANDLING:** If you receive a "database is locked" error, wait 2 seconds and retry.
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/soc_system_of_record.db \"YOUR_SQL_QUERY\"")`

**If `STORAGE_PROVIDER=dolt` (Versioned Local Mode):**
Use the `dolt` CLI:
`run_shell_command("dolt sql -q \"YOUR_SQL_QUERY\"")`

### 5. Standardized Data Taxonomy (Strict Auditing)
Regardless of the provider, you MUST adhere to the following schema and columns:

- **`actor`**: The User OAuth identity (email), provided as **`USER_ID`**.
- **`agent`**: Your sub-agent name (e.g., `triage`, `analysis`, `remediation`, `scribe`, `sre`, `detection_engineer`).
- **`session_id`**: The unique namespace for the current investigation, provided as **`SESSION_ID`**.
- **`action_taken`**: Do NOT use generic terms. You MUST provide a **concise summary of your findings or actions**.
- **Status Enum:** Only use `NEW`, `TRIAGE`, `ANALYSIS`, `REMEDIATION`, `REPORTING`, `CLOSED`.
- **Indicator Types:** Only use `IP`, `DOMAIN`, `URL`, `HASH_SHA256`, `HASH_MD5`, `USER`, `HOSTNAME`, `FILE_PATH`.
- **Exclusion Types:** Only use `URL_PATH_REGEX`, `SAFE_IP_CIDR`, `AUTHORIZED_USER`, `TRUSTED_DOMAIN`.
- **Time Format:** You MUST use ISO 8601 UTC format (**`YYYY-MM-DDTHH:MM:SSZ`**) for every timestamp.

### 6. Auditing & Multi-Tenancy
- **Identification:** Include the **`USER_ID`** in the **`actor`** column for every write.
- **Namespacing:** Include the **`SESSION_ID`** in the **`session_id`** column for every write. Every query MUST filter by `session_id`.

### 7. Special Handling: Branching (Dolt Only)
If using **Dolt**, you should use branching for speculative work:
`run_shell_command("dolt checkout -b investigation/INC-123")`

### 8. Initialization
If in `sqlite` or `dolt` mode and the DB doesn't exist, use `schema.sql` to initialize it.
**For SQLite:**
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/soc_system_of_record.db < schema.sql")`
In `native` mode, the **Scribe Agent** handles table creation during its final export/cleanup if they don't already exist.
