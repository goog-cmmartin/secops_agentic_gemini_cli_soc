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

### 1. Unified State Interaction
Read the value of the **`STORAGE_PROVIDER`** and **`SESSION_ID`** environment variables before every interaction. 

**If `STORAGE_PROVIDER=native` (Default / Cloud-Native Mode):**
Do NOT use local shell commands. You MUST document your activity by calling the Google SecOps MCP tools directly for EVERY write:
- **To Log Activity:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting **`TIMELINE_DATA_TABLE`**. Include the `SESSION_ID`.
- **To Register IOCs:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting **`IOC_DATA_TABLE`**. Include the `SESSION_ID`.
- **To Propose Tuning:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting **`TUNING_DATA_TABLE`**. Include the `SESSION_ID`.
- **To Read Context:** Use `mcp_GoogleSecOps_list_data_table_rows` with a filter for the **`incident_id` AND `session_id`**.

**If `STORAGE_PROVIDER=sqlite` (Portable Local Mode):**
Use the `sqlite3` CLI. **CRITICAL:** Use the project's temporary directory for the database file.
- **CONCURRENCY LIMITATION:** SQLite is a single-user format and does NOT support concurrent writes from multiple processes. 
- **ERROR HANDLING:** If you receive a "database is locked" error, wait 2 seconds and retry.
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/investigation.db \"YOUR_SQL_QUERY\"")`

**If `STORAGE_PROVIDER=dolt` (Versioned Local Mode):**
Use the `dolt` CLI:
`run_shell_command("dolt sql -q \"YOUR_SQL_QUERY\"")`

### 2. Standardized Data Taxonomy (Strict Auditing)
Regardless of the provider, you MUST adhere to the following schema and columns:

- **`actor`**: The User OAuth identity (email), provided as **`USER_ID`**.
- **`agent`**: Your sub-agent name (e.g., `triage`, `analysis`, `remediation`, `scribe`, `sre`, `detection_engineer`).
- **`session_id`**: The unique namespace for the current investigation, provided as **`SESSION_ID`**.
- **`action_taken`**: Do NOT use generic terms. You MUST provide a **concise summary of your findings or actions**.
- **Status Enum:** Only use `NEW`, `TRIAGE`, `ANALYSIS`, `REMEDIATION`, `REPORTING`, `CLOSED`.
- **Indicator Types:** Only use `IP`, `DOMAIN`, `URL`, `HASH_SHA256`, `HASH_MD5`, `USER`, `HOSTNAME`, `FILE_PATH`.
- **Exclusion Types:** Only use `URL_PATH_REGEX`, `SAFE_IP_CIDR`, `AUTHORIZED_USER`, `TRUSTED_DOMAIN`.
- **Time Format:** You MUST use ISO 8601 UTC format (**`YYYY-MM-DDTHH:MM:SSZ`**) for every timestamp.

### 3. Auditing & Multi-Tenancy
- **Identification:** Include the **`USER_ID`** in the **`actor`** column for every write.
- **Namespacing:** Include the **`SESSION_ID`** in the **`session_id`** column for every write. Every query MUST filter by `session_id` to prevent cross-talk in shared environments.

### 4. Special Handling: Branching (Dolt Only)
If using **Dolt**, you should use branching for speculative work:
`run_shell_command("dolt checkout -b investigation/INC-123")`

### 5. Initialization
If in `sqlite` or `dolt` mode and the DB doesn't exist, use `schema.sql` to initialize it.
In `native` mode, the **Scribe Agent** handles table creation during its final export/cleanup if they don't already exist.
