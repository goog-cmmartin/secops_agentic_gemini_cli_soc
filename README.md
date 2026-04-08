# Agentic SOC Governor Extension for Gemini CLI

This is a custom Gemini CLI extension that implements the **Governor Agent** for orchestrating security investigations in an Agentic SOC environment. It follows the **NIST SP 800-61r3** framework and uses **Dolt** as its system of record for incident tracking and timeline management.

## Features

- **Strategic Orchestration:** Coordinates multi-alert "Meta-Investigations" by delegating to specialized sub-agents.
- **Incident State Management:** Uses a Dolt SQL database to maintain current state, IOCs, and investigative timelines.
- **NIST Alignment:** Orchestrates investigations across Preparation, Detection & Analysis, Containment, Eradication & Recovery, and Post-Incident phases.
- **Sub-Agent Delegation:** Includes pre-defined sub-agents: `triage`, `analysis`, `remediation`, `scribe`, and `sre`.

## Extension Components

- `gemini-extension.json`: Root manifest defining the extension name, version, and capabilities.
- `GEMINI.md`: Core system instructions and context for the Governor Agent.
- `agents/`: Definitions for specialized sub-agents.
- `skills/`: Custom Agent Skills for incident runbooks and querying investigative history.
- `schema.sql`: SQL schema for the Dolt database.

## Installation

To install this extension in your local Gemini CLI environment, run:

```bash
gemini extension install https://github.com/gus-sdl/secops_agentic_gemini_cli_soc
```

*Note: Ensure you have the `gemini-cli-extension` topic added to your repository for it to be indexed in the extension gallery.*

## Prerequisites

- **Dolt:** This extension requires [Dolt](https://docs.dolthub.com/introduction/installation) to be installed on your system.
- **Google SecOps:** Requires access to a Google SecOps (Chronicle) environment.

## Settings

The following setting can be configured in your `config.toml` or as an environment variable:

- `DOLT_BINARY_PATH` (Default: `dolt`): The path to the `dolt` binary on your system.

## License

MIT
