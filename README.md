# Agentic SOC Governor Extension for Gemini CLI

This is a custom Gemini CLI extension that implements the **Governor Agent** for orchestrating security investigations in an Agentic SOC environment. It follows the **NIST SP 800-61r3** framework and uses **SQLite** or **Dolt** as its system of record for incident tracking and timeline management.

## Features

- **Strategic Orchestration:** Coordinates multi-alert "Meta-Investigations" by delegating to specialized sub-agents.
- **Incident State Management:** Uses a local SQL database (SQLite default or Dolt) to maintain current state, IOCs, and investigative timelines.
- **NIST Alignment:** Orchestrates investigations across Preparation, Detection & Analysis, Containment, Eradication & Recovery, and Post-Incident phases.
- **Sub-Agent Delegation:** Includes pre-defined sub-agents: `triage`, `analysis`, `remediation`, `scribe`, and `sre`.
- **Native SecOps Export:** Automatically mirrors investigation state to Google SecOps Data Tables for use by detection rules and dashboards.

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

- **Dolt (Optional):** If you wish to use versioned data, install [Dolt](https://docs.dolthub.com/introduction/installation). Otherwise, the extension will default to standard **SQLite**.
- **Google SecOps:** Requires access to a Google SecOps (Chronicle) environment.
- **Authentication:** You must be authenticated to Google Cloud. Run `gcloud auth application-default login` to ensure the CLI can access your SecOps and Cloud Logging data.

## Configuration

This extension uses several Google-hosted MCP servers. When you install the extension, you will be prompted to provide the following settings:

- **Storage Provider** (`STORAGE_PROVIDER`): The local storage backend for investigation state (defaults to `sqlite`, can be set to `dolt`).
- **Dolt Binary Path** (`DOLT_BINARY_PATH`): The path to your `dolt` binary (Optional: Only required if `STORAGE_PROVIDER` is set to `dolt`).
- **Google Cloud Project ID** (`GCP_PROJECT_ID`): The project ID where your SecOps instance and logs are located.
- **SecOps Region** (`SECOPS_REGION`): The region for your SecOps instance (e.g., `us`).
- **SecOps Customer ID** (`SECOPS_CUSTOMER_ID`): The UUID for your SecOps customer.
- **Timeline Data Table Name** (`TIMELINE_DATA_TABLE`): The name of the SecOps Data Table for investigation timelines (defaults to `investigation_timeline`).
- **IOC Data Table Name** (`IOC_DATA_TABLE`): The name of the SecOps Data Table for malicious IOCs (defaults to `malicious_iocs`).

*Note: You can accept the default Data Table names by pressing Enter during setup. The Scribe Agent will automatically create these tables in your Google SecOps instance if they do not exist.*

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

## System Check

Upon activation, the **Governor Agent** will automatically check for the presence of these MCP tools. If any are missing, it will provide instructions on how to enable them.

## License

Apache 2.0
