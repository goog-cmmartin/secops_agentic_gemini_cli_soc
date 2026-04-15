# Agentic SOC Governor Extension for Gemini CLI

This is a custom Gemini CLI extension that implements the **Governor Agent** for orchestrating security investigations in an Agentic SOC environment. It follows the **NIST SP 800-61r3** framework and uses **Google SecOps Data Tables**, **SQLite**, or **Dolt** as its system of record for incident tracking and timeline management.

## Features

- **Slash Command Interface:** Use `/investigate [Case ID]` to anchor the model strictly into the Governor Agent workflow.
- **Strategic Orchestration:** Coordinates multi-alert "Meta-Investigations" by delegating to specialized sub-agents.
- **Agentic Telemetry & Unit Cost Audit:** Captures real-time metadata for every MCP tool call and model response via **Synchronous Hooks**, providing full transparency into token usage and per-agent cost attribution.
- **Nuanced Resolution Taxonomy (MTTX):** Implements high-fidelity investigative outcomes: `TRUE_POSITIVE_MALICIOUS`, `TRUE_POSITIVE_BENIGN`, `FALSE_POSITIVE_NOISE`, and `FALSE_POSITIVE_EXPECTED`.
- **Self-Healing Detection Engineering:** Automatically drafts and validates YARA-L rules, with an autonomous loop that fixes syntax errors (up to 5 retries) using the SecOps validation API.
- **SecOps Reliability Engineering (SRE):** Includes a specialized agent for investigating SOAR system health, playbook failures, and SIEM ingestion errors using dedicated LQL templates.
- **Agentic Continuity:** Utilizes the **`SaveMemory`** tool to persist structural configuration (Project IDs, Table Names) across sessions, enabling faster startups and environment awareness.
- **Performance & Efficiency Metrics:** Automatically calculates investigation **Runtime** and **Agent Step Count**, surfacing definitive benchmarking data in the final investigation summary.
- **Session Hygiene:** Automatically archives telemetry logs upon investigation closure and provides **Context Compaction Guidance** (`/clear`) to prevent sliding window bloat.
- **Incident State Management:** Supports three storage modes:
    - **Native (Default):** Zero-install, shared cloud state using Google SecOps Data Tables.
    - **SQLite:** Portable local SQL database (`soc_system_of_record.db`).
    - **Dolt:** Versioned and branchable local SQL database.

## Extension Components

- `gemini-extension.json`: Root manifest defining the extension name, version, and capabilities.
- `GEMINI.md`: Core system instructions and context for the Governor Agent.
- `agents/`: Definitions for specialized sub-agents (`triage`, `analysis`, `remediation`, `scribe`, `sre`, `detection_engineer`).
- `commands/`: Custom slash commands (e.g., `/investigate`).
- `hooks/`: Synchronous interceptors for telemetry and auditing.
- `skills/`: Custom Agent Skills for incident runbooks and database abstraction.
- `schema.sql`: Standardized SQL schema for the local and cloud databases.

## Installation

To install this extension in your local Gemini CLI environment, run:

```bash
gemini extension install https://github.com/goog-cmmartin/secops_agentic_gemini_cli_soc.git
```

## Usage

Initiate an investigation by using the slash command:
```bash
/investigate [Case ID]
```

## Prerequisites

- **SQLite:** Standard **sqlite3** is required for local state management (if not using Native mode). 
- **Google SecOps:** Requires access to a Google SecOps (Chronicle) environment.
- **RBAC Permissions:** To automatically manage Data Tables, your identity requires **Chronicle API Admin** and **Chronicle SOAR Admin** roles.
- **Authentication:** Run `gcloud auth application-default login` to ensure the CLI can access your SecOps and Cloud Logging data.

## Configuration

When you install the extension, you will be prompted to provide the following settings:

- **Storage Provider** (`STORAGE_PROVIDER`): The backend for investigation state (defaults to **`native`**).
- **Google Cloud Project ID** (`GCP_PROJECT_ID`): The project ID where your SecOps instance and logs are located.
- **SecOps Customer ID** (`SECOPS_CUSTOMER_ID`): The UUID for your SecOps customer.
- **Timeline Data Table Name** (`TIMELINE_DATA_TABLE`): Defaults to `asoc_investigation_timeline`.
- **IOC Data Table Name** (`IOC_DATA_TABLE`): Defaults to `asoc_malicious_iocs`.
- **Detection Tuning Data Table Name** (`TUNING_DATA_TABLE`): Defaults to `asoc_detection_tuning`.

## Maintenance and Reset

### Resetting Investigation State
**For Native (Default):**
Investigation state is managed directly in your Google SecOps Data Tables. To clear it, use the SecOps UI or the `mcp_GoogleSecOps_delete_data_table_rows` tool.

**For SQLite:**
Delete the database file in your project's temporary directory:
```bash
rm $GEMINI_TMP_DIR/soc_system_of_record.db
```

### Telemetry Logs
Raw telemetry is stored in `.gemini/telemetry/events.jsonl`. Finalized investigations are automatically moved to `.gemini/telemetry/archive/` to maintain performance.

## License

Apache 2.0
