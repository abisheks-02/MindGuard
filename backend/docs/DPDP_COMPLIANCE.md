# DPDP Act 2023 Compliance Framework

This document outlines MindGuard's adherence to the Digital Personal Data Protection Act of India.

## 1. Notice & Consent
Users are presented with explicit, granular consent toggles during the Onboarding flow.
- Consent for Support Messages
- Consent for Trusted Contact Notification
- Consent for Anonymous Research

## 2. Data Principal Rights
- **Right to Erasure**: Fully implemented via `DELETE /api/v1/auth/me`.
- **Right to Nomination**: Trusted Contact feature serves as a form of emergency data access/nomination.

## 3. Data Fiduciary Obligations
- **Data Minimization**: Logs are actively scrubbed of PII (Phone, Emails) before writing to disk using `PIIFilter` in `logger.py`.
- **Security Safeguards**: `EncryptedString` (Fernet symmetric encryption) is applied to all sensitive database columns. API endpoints are secured with Short-Lived JWTs and Strict CORS.
