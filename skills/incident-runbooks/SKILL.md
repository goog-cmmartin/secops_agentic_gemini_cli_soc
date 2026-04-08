# Skill: Incident Runbooks

You are accessing standard operating procedures (SOPs) and runbooks for specific types of security incidents. 
Apply these guidelines when analyzing cases or recommending containment actions.

## 1. Phishing / Suspicious Email
- Verify the sender address and domain reputation.
- Check headers (SPF, DKIM, DMARC) if available.
- Extract any embedded URLs or attachments.
- **Containment:** If malicious, block the sender domain and purge the email from user inboxes. Recommend password reset if a credential harvesting link was clicked.

## 2. Malware / Suspicious Process
- Analyze the file hash (MD5, SHA256) against threat intelligence.
- Review process execution logs to identify the parent process and any lateral movement.
- **Containment:** Isolate the infected host from the network immediately. Block the hash across the EDR.

## 3. Impossible Travel / Suspicious Login
- Check the source IP reputation.
- Look for successful authentications followed by anomalous administrative actions.
- **Containment:** Revoke active sessions, disable the compromised account temporarily, and force MFA re-registration.
