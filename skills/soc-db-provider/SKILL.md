---
name: soc-db-provider
description: Abstracts database access for the Agentic SOC, supporting Native SecOps Data Tables, SQLite, and Dolt.
---

# SOC Database Provider Skill

This skill provides a unified interface for sub-agents to read and write investigation state. It dynamically handles the syntax differences based on the **`STORAGE_PROVIDER`** environment variable, which is your **SINGLE SOURCE OF TRUTH**. 

## Configuration Context
- `STORAGE_PROVIDER`: (Values: `native`, `sqlite`, `dolt`) MUST be used to determine the backend. Do not search for files or binaries.
- `TIMELINE_DATA_TABLE`: Name of the shared SecOps timeline table.
- `IOC_DATA_TABLE`: Name of the shared SecOps IOC table.
- `TUNING_DATA_TABLE`: Name of the shared SecOps tuning/suppression table.

## Instructions for the Model

### 1. Unified State Interaction
Read the value of the **`STORAGE_PROVIDER`** environment variable before every interaction. Do not guess.

**If `STORAGE_PROVIDER=sqlite` (Portable Local Mode):**
Use the `sqlite3` CLI. **CRITICAL:** Use the project's temporary directory for the database file.
- **CONCURRENCY LIMITATION:** SQLite is a single-user format and does NOT support concurrent writes from multiple processes or agents. 
- **ERROR HANDLING:** If you receive a "database is locked" error, wait 2 seconds and retry the command. If it fails after 3 retries, inform the Governor of a local resource conflict.
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/investigation.db \"YOUR_SQL_QUERY\"")`

**If `STORAGE_PROVIDER=dolt` (Versioned Local Mode):**
Use the `dolt` CLI.
- **CONCURRENCY:** Supports concurrent reads, but simultaneous writes to the same branch may result in blocked commits or conflicts.
`run_shell_command("dolt sql -q \"YOUR_SQL_QUERY\"")`

**If `STORAGE_PROVIDER=native` (Default / Cloud-Native Mode):**
Do NOT use local shell commands. You MUST document your activity by calling the Google SecOps MCP tools directly for EVERY write.
- **SHARED STATE:** This is the ONLY mode recommended for concurrent multi-analyst collaboration. Google SecOps Data Tables handle concurrent writes natively at the API level.
- **To Log Activity:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting **`TIMELINE_DATA_TABLE`**.

### 2. Standardized Data Taxonomy (Strict Auditing)
Regardless of the provider, you MUST adhere to the following schema and columns:

- **`actor`**: The User OAuth identity (email), provided as **`USER_ID`**.
- **`agent`**: Your sub-agent name (e.g., `triage`, `analysis`, `remediation`, `scribe`, `sre`, `detection_engineer`).
- **`action_taken`**: Do NOT use generic terms. You MUST provide a **concise summary of your findings or actions** (e.g., "Identified 3 malicious hashes and linked them to host X").
- **Status Enum:** Only use `NEW`, `TRIAGE`, `ANALYSIS`, `REMEDIATION`, `REPORTING`, `CLOSED`.
- **Indicator Types:** Only use `IP`, `DOMAIN`, `URL`, `HASH_SHA256`, `HASH_MD5`, `USER`, `HOSTNAME`, `FILE_PATH`.
- **Exclusion Types:** Only use `URL_PATH_REGEX`, `SAFE_IP_CIDR`, `AUTHORIZED_USER`, `TRUSTED_DOMAIN`.
- **Time Format:** You MUST use ISO 8601 UTC format (**`YYYY-MM-DDTHH:MM:SSZ`**) for every timestamp. Do not use raw epoch integers.

### 3. Special Handling: Branching (Dolt Only)
If using **Dolt**, you should use branching for speculative work:
`run_shell_command("dolt checkout -b investigation/INC-123")`

### 4. Initialization
If in `sqlite` or `dolt` mode and the DB doesn't exist, use `schema.sql` to initialize it.
In `native` mode, the **Scribe Agent** handles table creation during its final export/cleanup if they don't already exist.
