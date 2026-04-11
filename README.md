# Agentic SOC Governor Extension for Gemini CLI

This is a custom Gemini CLI extension that implements the **Governor Agent** for orchestrating security investigations in an Agentic SOC environment. It follows the **NIST SP 800-61r3** framework and uses **Google SecOps Data Tables**, **SQLite**, or **Dolt** as its system of record for incident tracking and timeline management.

## Features

- **Strategic Orchestration:** Coordinates multi-alert "Meta-Investigations" by delegating to specialized sub-agents.
- **Incident State Management:** Supports three storage modes:
    - **Native (Default):** Zero-install, shared cloud state using Google SecOps Data Tables.
    - **SQLite:** Portable local SQL database.
    - **Dolt:** Versioned and branchable local SQL database.
- **Performance Metrics:** Automatically calculates investigation **Runtime** and **Agent Step Count** to measure SOC efficiency.
- **NIST Alignment:** Orchestrates investigations across Preparation, Detection & Analysis, Containment, Eradication & Recovery, and Post-Incident phases.
- **Sub-Agent Delegation:** Includes pre-defined sub-agents: `triage`, `analysis`, `remediation`, `scribe`, `detection_engineer`, and `sre`.
- **Closed-Loop Feedback:** Automatically drafts new YARA-L detection rules based on attack paths and posts them back to the SOAR case and Data Tables.

## Extension Components

- `gemini-extension.json`: Root manifest defining the extension name, version, and capabilities.
- `GEMINI.md`: Core system instructions and context for the Governor Agent.
- `agents/`: Definitions for specialized sub-agents.
- `skills/`: Custom Agent Skills for incident runbooks and database abstraction.
- `schema.sql`: SQL schema for the local database.

## Installation

To install this extension in your local Gemini CLI environment, run:

```bash
gemini extension install https://github.com/goog-cmmartin/secops_agentic_gemini_cli_soc.git
```

*Note: The `git` binary must be installed on your system for the CLI to clone and manage the extension.*

## Prerequisites

- **SQLite:** Standard **sqlite3** is required for local state management (if not using Native mode). Install it via your package manager (e.g., `sudo apt install sqlite3` on Debian/Ubuntu).
- **Dolt (Optional):** If you wish to use versioned data, install [Dolt](https://docs.dolthub.com/introduction/installation).
- **Google SecOps:** Requires access to a Google SecOps (Chronicle) environment.
- **RBAC Permissions:** To automatically create and manage Data Tables, your Google Cloud identity must have administrative roles, such as **Chronicle API Admin** and **Chronicle SOAR Admin**.
- **Authentication:** You must be authenticated to Google Cloud. Run `gcloud auth application-default login` to ensure the CLI can access your SecOps and Cloud Logging data.

## Configuration

This extension uses several Google-hosted MCP servers. When you install the extension, you will be prompted to provide the following settings:

- **Storage Provider** (`STORAGE_PROVIDER`): The local storage backend for investigation state (defaults to **`native`**, can be set to `sqlite` or `dolt`).
- **Dolt Binary Path** (`DOLT_BINARY_PATH`): The path to your `dolt` binary (Optional: Only required if `STORAGE_PROVIDER` is set to `dolt`).
- **Google Cloud Project ID** (`GCP_PROJECT_ID`): The project ID where your SecOps instance and logs are located.
- **SecOps Region** (`SECOPS_REGION`): The region for your SecOps instance (e.g., `us`).
- **SecOps Customer ID** (`SECOPS_CUSTOMER_ID`): The UUID for your SecOps customer.
- **Analyst Email** (`ANALYST_EMAIL`): Your official email address. If provided, this is used for case assignment and auditing. If empty, the extension will attempt to retrieve your `gcloud` identity.
- **Timeline Data Table Name** (`TIMELINE_DATA_TABLE`): The name of the SecOps Data Table for investigation timelines (defaults to `investigation_timeline`).
- **IOC Data Table Name** (`IOC_DATA_TABLE`): The name of the SecOps Data Table for malicious IOCs (defaults to `malicious_iocs`).
- **Detection Tuning Data Table Name** (`TUNING_DATA_TABLE`): The name of the SecOps Data Table for drafted YARA-L rules (defaults to `detection_tuning`).

*Note: You can accept the default Data Table names by pressing Enter during setup. The sub-agents will automatically create these tables in your Google SecOps instance if they do not exist.*

### Manual Tool Configuration

This extension depends on several Google-hosted MCP servers. Before running the extension, ensure these are configured in your `~/.gemini/settings.json`. Replace `YOUR_PROJECT_ID` with the project ID you used during the extension setup:

```json
{
  "mcpServers": {
    "GoogleSecOps": {
      "httpUrl": "https://us-chronicle.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": [
          "https://www.googleapis.com/auth/cloud-platform"
        ]
      },
      "timeout": 30000,
      "headers": {
        "x-goog-user-project": "YOUR_PROJECT_ID"
      }
    },
    "CloudLogging": {
      "httpUrl": "https://logging.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": [
          "https://www.googleapis.com/auth/cloud-platform"
        ]
      },
      "headers": {
        "x-goog-user-project": "YOUR_PROJECT_ID"
      }
    },
    "CloudMonitoring": {
      "httpUrl": "https://monitoring.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": [
          "https://www.googleapis.com/auth/cloud-platform"
        ]
      },
      "headers": {
        "x-goog-user-project": "YOUR_PROJECT_ID"
      }
    },
    "DeveloperKnowledge": {
      "authProviderType": "google_credentials"
    }
  }
}
```

## Automation & Hands-Free Operation

By default, this extension includes a safety policy that **forces** an approval prompt for high-risk actions (SecOps API calls, shell commands). 

If you want a truly "hands-free" experience without prompts:
1.  **Remove** the `[[rule]]` blocks from the installed extension's `policies/safety.toml`.
2.  **Add** the following to your global `~/.gemini/settings.json` under the `allowedTools` key:

```json
{
  "allowedTools": [
    "mcp_GoogleSecOps_*",
    "mcp_CloudLogging_*",
    "mcp_CloudMonitoring_*",
    "mcp_DeveloperKnowledge_*",
    "run_shell_command"
  ]
}
```

## Maintenance and Reset

### Resetting Investigation State
If you need to clear your investigation history and start fresh, you can reset the state depending on your storage mode.

**For Native (Default):**
Investigation state is managed directly in your Google SecOps Data Tables. To clear it, use the SecOps UI or the `mcp_GoogleSecOps_delete_data_table_rows` tool.

**For SQLite:**
Simply delete the database file in your project's temporary directory. The extension will automatically re-initialize it during the next run.
```bash
rm $GEMINI_TMP_DIR/investigation.db
```

**For Dolt:**
You can reset the local Dolt repository by running:
```bash
dolt table drop investigation_timeline iocs incidents
```

## Known Limitations

- **Global Locking Race Condition:** While the extension implements a "Global Lock" via SecOps Data Tables to prevent analysts from investigating the same case, there is a theoretical race condition. Because the check (`list_data_table_rows`) and the lock acquisition (`add_rows_to_data_table`) are not an atomic transaction, two agents could potentially check a clear table at the same millisecond and both proceed to claim the case. This is an accepted risk for this Proof of Concept.
- **Local Database Concurrency:** The `sqlite` and `dolt` storage providers are intended for local, single-session use. SQLite, in particular, does not support concurrent writes from multiple processes. If you attempt to run parallel investigations using a local provider, you may encounter "database is locked" errors. **Native Cloud Mode** is the only mode recommended for true multi-analyst collaboration.

## System Check

Upon activation, the **Governor Agent** will automatically check for the presence of these MCP tools. If any are missing, it will provide instructions on how to enable them.

## License

Apache 2.0
