# Audit Event Emission — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Any `event_logger.record()` call | Any component emitting events | Per significant operation |
| `tracing_system.create_universal_trace()` | `SRT1TracingSystem` | Per traced operation |
| Governance Monitor scan | `GovernanceMonitor.run_scan()` | Periodic (configurable interval) |
| Critical actions | `execution_authorization`, `file_write_commit`, `action_blocked` | On each occurrence |
| Lease lifecycle | `LeaseManager.grant_lease()`, `revoke_lease()`, `complete_lease()` | On each occurrence |

## Pre-conditions

- event log store is initialized and accessible at `{state_dir}/audit/event_log`.
- Chain hash from previous event is available (or genesis hash for first event).
- Component and operation identifiers are provided.

## Post-conditions

- Event row written to SQLite with hash chain entry.
- `CRITICAL` severity events marked for external Seed Signature signing.
- Chain hash updated for subsequent events.
