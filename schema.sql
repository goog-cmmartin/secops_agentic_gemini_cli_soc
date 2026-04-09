-- Dolt Database Schema for Agentic SOC

CREATE TABLE incidents (
    incident_id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'new', -- e.g., 'new', 'triage', 'analysis', 'containment', 'closed'
    resolution VARCHAR(255), -- e.g., 'true_positive', 'false_positive'
    summary TEXT,
    performed_by VARCHAR(255), -- The OAuth identity/user email
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE iocs (
    ioc_id VARCHAR(255) PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL,
    indicator_type VARCHAR(50) NOT NULL, -- e.g., 'IP', 'DOMAIN', 'HASH', 'USER'
    indicator_value VARCHAR(255) NOT NULL,
    is_malicious BOOLEAN DEFAULT FALSE,
    performed_by VARCHAR(255), -- The OAuth identity/user email
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

CREATE TABLE investigation_timeline (
    event_id VARCHAR(255) PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL,
    actor VARCHAR(100) NOT NULL, -- e.g., 'Governor', 'triage_agent', 'analysis_agent'
    action_taken TEXT NOT NULL,
    performed_by VARCHAR(255), -- The OAuth identity/user email
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);
