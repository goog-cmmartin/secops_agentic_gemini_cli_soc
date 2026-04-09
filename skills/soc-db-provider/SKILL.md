---
name: soc-db-provider
description: Abstracts local database access for the Agentic SOC, supporting both Dolt (versioned) and SQLite (portable).
---

# SOC Database Provider Skill

This skill provides a unified interface for sub-agents to read and write to the local "System of Record" database. It dynamically handles the syntax differences between **Dolt** and **SQLite** based on the `STORAGE_PROVIDER` setting.

## Configuration Context
- `STORAGE_PROVIDER`: (Values: `dolt`, `sqlite`) The active database backend.
- `DOLT_BINARY_PATH`: The path to the `dolt` binary (if using Dolt).

## Instructions for the Model

### 1. Unified SQL Execution
When you need to perform a database action (Querying incidents, logging to the timeline, inserting IOCs), use the following logic to construct your shell command:

**If `STORAGE_PROVIDER=dolt`:**
Use the `dolt` CLI:
`run_shell_command("dolt sql -q \"YOUR_SQL_QUERY\"")`

**If `STORAGE_PROVIDER=sqlite`:**
Use the `sqlite3` CLI. **CRITICAL:** Use the project's temporary directory for the database file to avoid cluttering the workspace:
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/investigation.db \"YOUR_SQL_QUERY\"")`

### 2. Table Schema
Assume the following tables are available regardless of the provider:
- `incidents`: `incident_id`, `title`, `severity`, `status`, `resolution`, `summary`
- `iocs`: `ioc_id`, `incident_id`, `indicator_type`, `indicator_value`, `is_malicious`
- `investigation_timeline`: `event_id`, `incident_id`, `actor`, `action_taken`, `timestamp`

### 3. Special Handling: Branching (Dolt Only)
If you are using **Dolt** and performing a "Meta-Investigation," you should use branching for speculative work:
`run_shell_command("dolt checkout -b investigation/INC-123")`

**Note:** If using **SQLite**, skip the branching step as it is not supported. Log directly to the main timeline.

### 4. Initialization
If the database file or Dolt repository doesn't exist, use the provided `schema.sql` to initialize it:

**For SQLite:**
`run_shell_command("sqlite3 \$GEMINI_TMP_DIR/investigation.db < schema.sql")`

**For Dolt:**
`run_shell_command("dolt init && dolt sql < schema.sql")`
