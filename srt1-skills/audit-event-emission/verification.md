# Audit Event Emission — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Event persisted | Row exists in `event log` after `record()` call |
| Hash chain intact | `event_log.verify_chain()` returns True for all events |
| CRITICAL events queued | Events with `CRITICAL` severity have entries in `external_signing_handoff` |
| No modification | Re-running `verify_chain()` produces identical result |

## Failure Indicators

| Indicator | Meaning |
|-----------|-------|
| `verify_chain()` returns False | Chain tampered with, rows deleted, or events reordered |
| Missing rows | DB write failed silently |
| No external signing handoff entries for CRITICAL | Signature workflow not wired up |
