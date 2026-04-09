---
name: soc-db-provider
description: Abstracts local database access for the Agentic SOC, supporting both SQLite (portable) and Dolt (versioned).
---

# SOC Database Provider Skill

This skill provides a unified interface for sub-agents to read and write to the local "System of Record" database. It dynamically handles the syntax differences between **SQLite** and **Dolt** based on the `STORAGE_PROVIDER` setting.

## Configuration Context
- `STORAGE_PROVIDER`: (Values: `sqlite`, `dolt`) The active database backend.
- `DOLT_BINARY_PATH`: The path to the `dolt` binary (if using Dolt).

## Instructions for the Model

### 1. Unified SQL Execution
When you need to perform a database action (Querying incidents, logging to the timeline, inserting IOCs), use the following logic:

**If `STORAGE_PROVIDER=sqlite` (Default / Portable Mode):**
Use the `sqlite3` CLI. **CRITICAL:** Use the project's temporary directory for the database file to avoid cluttering the workspace:
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/investigation.db \"YOUR_SQL_QUERY\"")`

**If `STORAGE_PROVIDER=dolt` (Versioned Mode):**
Use the `dolt` CLI:
`run_shell_command("dolt sql -q \"YOUR_SQL_QUERY\"")`

### 2. Table Schema
Assume the following tables are available regardless of the provider:
- `incidents`: `incident_id`, `title`, `severity`, `status`, `resolution`, `summary`, `performed_by`, `created_at`, `updated_at`
- `iocs`: `ioc_id`, `incident_id`, `indicator_type`, `indicator_value`, `is_malicious`, `performed_by`, `first_seen`
- `investigation_timeline`: `event_id`, `incident_id`, `actor`, `action_taken`, `performed_by`, `timestamp`

### 3. Auditing (Who performed the action)
When writing to any of the tables above, you MUST include the **`USER_ID`** (retrieved by the Governor) in the **`performed_by`** column. This ensures a complete audit trail of the OAuth identity that initiated the agentic workflow.

### 4. Special Handling: Branching (Dolt Only)
If you are using **Dolt** and performing a "Meta-Investigation," you should use branching for speculative work:
`run_shell_command("dolt checkout -b investigation/INC-123")`

**Note:** If using **SQLite**, skip the branching step as it is not supported. Log directly to the main timeline.

### 5. Initialization
If the database file or Dolt repository doesn't exist, use the provided `schema.sql` to initialize it:

**For SQLite:**
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/investigation.db < schema.sql")`

**For Dolt:**
`run_shell_command("dolt init && dolt sql < schema.sql")`
