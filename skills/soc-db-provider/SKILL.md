---
name: soc-db-provider
description: Abstracts database access for the Agentic SOC, supporting Native SecOps Data Tables, SQLite, and Dolt.
---

# SOC Database Provider Skill

This skill provides a unified interface for sub-agents to read and write investigation state. It dynamically handles the syntax differences between **Google SecOps Data Tables**, **SQLite**, and **Dolt** based on the `STORAGE_PROVIDER` setting.

## Configuration Context
- `STORAGE_PROVIDER`: (Values: `native`, `sqlite`, `dolt`) The active database backend.
- `TIMELINE_DATA_TABLE`: Name of the shared SecOps timeline table.
- `IOC_DATA_TABLE`: Name of the shared SecOps IOC table.

## Instructions for the Model

### 1. Unified State Interaction
When you need to log an action, insert an IOC, or query investigation history, use the following logic:

**If `STORAGE_PROVIDER=native` (Default / Cloud-Native Mode):**
Do NOT use local shell commands. You MUST document your activity by calling the Google SecOps MCP tools directly for EVERY write:
- **To Log Activity:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting **`TIMELINE_DATA_TABLE`**.
- **To Register IOCs:** Use `mcp_GoogleSecOps_add_rows_to_data_table` targeting **`IOC_DATA_TABLE`**.
- **To Read Context:** Use `mcp_GoogleSecOps_list_data_table_rows` with a filter for the `incident_id`.

**If `STORAGE_PROVIDER=sqlite` (Portable Local Mode):**
Use the `sqlite3` CLI. **CRITICAL:** Use the project's temporary directory for the database file:
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/investigation.db \"YOUR_SQL_QUERY\"")`

**If `STORAGE_PROVIDER=dolt` (Versioned Local Mode):**
Use the `dolt` CLI:
`run_shell_command("dolt sql -q \"YOUR_SQL_QUERY\"")`

### 2. Standardized Data Taxonomy
Regardless of the provider, you MUST adhere to the following schema and terms:

- **Actor Format:** Use `[USER_ID]:[AGENT_NAME]` (e.g., `analyst@company.com:triage`).
- **Status Enum:** Use only `NEW`, `TRIAGE`, `ANALYSIS`, `REMEDIATION`, `REPORTING`, `CLOSED`.
- **Indicator Types:** Use only `IP`, `DOMAIN`, `URL`, `HASH_SHA256`, `HASH_MD5`, `USER`, `HOSTNAME`, `FILE_PATH`.
- **Action Taken:** Concise, uppercase phrases (e.g., `IDENTIFIED_IOCS`, `PERFORMED_UDM_SEARCH`, `EXECUTED_CONTAINMENT`).

### 3. Auditing (Who performed the action)
Include the **`USER_ID`** (retrieved by the Governor) in the **`performed_by`** column for every write.

### 4. Special Handling: Branching (Dolt Only)
If using **Dolt**, you should use branching for speculative work:
`run_shell_command("dolt checkout -b investigation/INC-123")`

### 5. Initialization
If in `sqlite` or `dolt` mode and the DB doesn't exist, use `schema.sql` to initialize it.
In `native` mode, the **Scribe Agent** handles table creation during its final export/cleanup if they don't already exist.
