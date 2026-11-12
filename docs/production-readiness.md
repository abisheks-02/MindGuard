# MindGuard production-readiness assessment

## Current status: not approved for clinical deployment

MindGuard is suitable for a **research prototype / supervised pilot** after the
engineering fixes in this repository. It is not ready to be marketed as a
diagnostic, crisis-response, or autonomous mental-health service.

## Verified engineering changes

- The frontend now calls the implemented `POST /api/v1/chat/stream` endpoint.
  The server emits JSON Server-Sent Events, matching the client's stream parser.
- The kNN detector abstains when it has no meaningful anchor similarity. It no
  longer converts an unknown input into an arbitrary severity vote.
- Negation is scoped to nearby self-harm terms. A remote "don't" no longer
  suppresses a later risk statement; post-phrase Tanglish negation is retained.
- Explicit first-person self-harm intent and high-precision acute lexicon
  matches are not diluted by abstaining auxiliary detectors. Such results are
  marked `needs_review: true`.
- Legacy network-dependent and stale tests were replaced with offline tests of
  the current application structure.
- Required runtime packages for the active code paths are declared in
  `backend/requirements.txt`.
- Chat transcripts are not persisted by default. Production configuration fails
  if transcript retention is enabled without replacing this gate with approved
  consent, access-control, retention, and deletion controls.

## Measured internal result

On the repository's `backend/data/test_cases.csv` test split, the current
heuristic ensemble produced:

| Metric | Before fixes | After fixes |
|---|---:|---:|
| Macro F1 | 0.62 | 0.78 |
| Severe recall | 0.29 | 0.83 |

This is a small internal benchmark with repeated examples. It is **not** a
clinical validation study and must not be used in sales, safety, or medical
performance claims.

## Required before any company launch

1. **Clinical validation** — create a locked, representative, independently
   labelled Tanglish test set; pre-register intended use, error tolerances,
   subgroups, and safety thresholds. Evaluate recall, precision, calibration,
   false-negative severity, and performance drift after every model/data change.
2. **Human escalation workflow** — define who reviews a high-risk result, their
   response SLA, operating hours, jurisdiction, and documented failure path.
   Never represent the application as contacting emergency services or a trusted
   contact unless that delivery, consent, and acknowledgement are real.
3. **Crisis content review** — have qualified local clinicians review every
   crisis response, local helpline, language translation, and UI pathway. Verify
   numbers regularly and show location-aware resources only where verified.
4. **Identity and access** — replace demo user IDs, demo PINs, and anonymous
   shared sessions with authenticated users, role-based clinician access, audit
   logs, rate limits, account recovery, and tested authorization boundaries.
5. **Data protection** — move secrets from local files into a managed secret
   store, use PostgreSQL in production, encrypt data in transit and at rest,
   conduct retention/deletion tests, and obtain legal review for consent,
   notices, processor contracts, and incident response.
6. **Operations** — use a container build with pinned dependencies, CI that
   blocks release on tests and security scans, structured monitoring, incident
   runbooks, backups/restore drills, uptime targets, and a rollback plan.
7. **Model lifecycle** — replace the rule/anchor prototype with a versioned,
   clinically evaluated classifier. Track data provenance, version every model
   and prompt, monitor calibration/drift by language subgroup, and require a
   human go/no-go decision for each release.

## Deployment gate

Do not deploy beyond a supervised pilot until every item above has an owner,
evidence artifact, review date, and written sign-off from clinical, privacy,
security, and product leadership.
