-- SQL Schema for Agentic SOC (Standardized for Cloud & Local Storage)

CREATE TABLE incidents (
    incident_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL, -- Unique ID for the current analysis session
    title TEXT NOT NULL,
    severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'NEW', -- e.g., 'NEW', 'TRIAGE', 'ANALYSIS', 'CLOSED'
    resolution VARCHAR(255), -- e.g., 'TRUE_POSITIVE', 'FALSE_POSITIVE'
    summary TEXT,
    actor VARCHAR(255), -- The User OAuth identity (email)
    agent VARCHAR(100), -- The agent that performed the last update
    start_time TIMESTAMP, -- When the investigation began
    end_time TIMESTAMP, -- When the report was finalized
    duration_sec INT, -- Total runtime in seconds
    step_count INT DEFAULT 0, -- Total number of agent handoffs/interactions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE iocs (
    ioc_id VARCHAR(255) PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL, -- Namespace for multi-tenancy
    indicator_type VARCHAR(50) NOT NULL, -- e.g., 'IP', 'DOMAIN', 'HASH_SHA256'
    indicator_value VARCHAR(255) NOT NULL,
    is_malicious BOOLEAN DEFAULT FALSE,
    actor VARCHAR(255), -- The User OAuth identity (email)
    agent VARCHAR(100), -- The agent that identified the IOC
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

CREATE TABLE investigation_timeline (
    event_id VARCHAR(255) PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL, -- Namespace for multi-tenancy
    action_taken TEXT NOT NULL, -- Detailed summary of activity
    actor VARCHAR(255) NOT NULL, -- The User OAuth identity (email)
    agent VARCHAR(100) NOT NULL, -- The agent performing the action (e.g., 'triage', 'analysis')
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

CREATE TABLE detection_tuning (
    tuning_id VARCHAR(255) PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL, -- Namespace for multi-tenancy
    rule_name VARCHAR(255) NOT NULL,
    exclusion_type VARCHAR(50) NOT NULL, -- e.g., 'URL_PATH_REGEX', 'SAFE_IP_CIDR'
    exclusion_value TEXT NOT NULL,
    rule_logic TEXT, -- The proposed YARA-L snippet
    reasoning TEXT,
    actor VARCHAR(255),
    agent VARCHAR(100),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);
