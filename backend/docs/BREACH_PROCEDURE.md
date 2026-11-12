# Data Breach Response Procedure

In the event of a suspected data breach, the following protocol must be executed within **6 hours** of discovery, in compliance with CERT-In directives and DPDP 2023.

## Phase 1: Identification & Containment
1. Freeze affected database shards.
2. Rotate all `SECRET_KEY` and `ENCRYPTION_KEY` environment variables.
3. Force expiration of all active JWTs by incrementing the token generation epoch.

## Phase 2: Assessment
1. Determine if PII (Phone numbers, Trusted Contacts) was exposed. *Note: PII is encrypted at-rest using AES-128. Assess if the Fernet key was compromised.*
2. Check `app/utils/logger.py` audit trails to trace the exfiltration vector.

## Phase 3: Notification
1. Notify the Data Protection Board of India.
2. Notify affected Data Principals via SMS within 72 hours, stating the nature of the breach and steps they should take.

## Phase 4: Eradication & Recovery
1. Patch the vulnerability.
2. Restore systems from secure, offline backups if integrity was compromised.
