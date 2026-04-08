# Skill: Query Case History

You are checking the Dolt SQL database (`main` branch) to find historical context for your current investigation. Use the `run_shell_command` tool to execute `dolt sql -q "..."`.

## Available Tables
* `incidents`: `incident_id`, `title`, `severity`, `status`, `resolution`, `summary`, `created_at`, `updated_at`
* `iocs`: `ioc_id`, `incident_id`, `indicator_type`, `indicator_value`, `is_malicious`, `first_seen`
* `investigation_timeline`: `event_id`, `incident_id`, `actor`, `action_taken`, `timestamp`

## Common Operations

### 1. Check if an IOC has been seen before
```bash
dolt sql -q "SELECT c.incident_id, c.title, c.resolution, i.first_seen FROM iocs i JOIN incidents c ON i.incident_id = c.incident_id WHERE i.indicator_value = '<INDICATOR_VALUE>' AND active_branch() = 'main';"
```

### 2. Retrieve the summary of a specific historical case
```bash
dolt sql -q "SELECT summary, resolution FROM incidents WHERE incident_id = '<CASE_ID>';"
```

### 3. Find past cases by keyword (Poor man's RAG)
```bash
dolt sql -q "SELECT incident_id, title FROM incidents WHERE summary LIKE '%<KEYWORD>%';"
```
