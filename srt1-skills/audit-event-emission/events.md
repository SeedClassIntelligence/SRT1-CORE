# Audit Event Emission — Events (Meta)

These are events *about the audit system itself*:

| Event | Severity | Emitter | Status |
|-------|----------|---------|--------|
| `audit_export_generation` | WARNING | `public event log` | ✅ Exists |
| `signature_applied` | CRITICAL | `public event log` | ❌ Needs implementation |
| `external_signature_requested` | WARNING | `public event log` | ❌ Needs implementation |
| `chain_verification_passed` | INFO | `public event log` | ❌ Needs implementation |
| `chain_verification_failed` | CRITICAL | `public event log` | ❌ Needs implementation |

## Hash Chain Mechanics

Every event is linked via:
```
event_hash     = sha256(component + operation + timestamp + detail_json)
chain_hash     = sha256(previous_chain_hash + event_hash)
```

This produces a tamper-evident append-only chain. `event_log.verify_chain()` walks the entire history and detects modification or reordering.
