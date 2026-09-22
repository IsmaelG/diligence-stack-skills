# GDPR questionnaire — send as-is to the Target's CTO or DPO

1. Do you have an up-to-date record of processing activities (Art. 30 GDPR)? Yes / No / Partial
2. Is a DPO appointed, internal or external? If yes, who?
3. Where is your data hosted (country / region)?
4. Do you have signed Data Processing Agreements (DPAs) with your processors (host, email
   provider, support tooling...)? Yes / No / Partial
5. What is your customer data retention policy (duration, automatic purge)?
6. Have you had a data breach or a notification to a data protection authority in the last 24
   months? Yes / No
7. Is MFA enabled on your GitHub/GitLab organization and your main cloud provider? Yes / No

PCI-DSS and HIPAA deliberately excluded — add them only if a target genuinely touches payments or
health data.

## Expected combined output (questionnaire + compliance_selfrun.sh, assembled by hand for now)

```json
{
  "gdpr": {
    "processing_record": "Yes",
    "dpo_appointed": "Yes — external firm",
    "hosting": "EU (specify provider)",
    "processor_dpas": "Partial",
    "retention_policy": "24 months, automatic purge",
    "recent_breach": "No",
    "mfa_enabled": "Yes"
  },
  "file_detectors": {
    "security_md_present": true,
    "dependabot_config_present": true,
    "codeowners_present": false
  }
}
```
