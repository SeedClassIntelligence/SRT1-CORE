# Post-Execution Verification — Events

## Emitted Events

| Event | Severity | Emitter | Status |
|-------|----------|---------|--------|
| `post_execution_snapshot_taken` | INFO | `PostExecutionVerifier` | ✅ Exists |
| `verification_passed` | CRITICAL | `PostExecutionVerifier` | ✅ Exists |
| `verification_failed` | CRITICAL | `PostExecutionVerifier` | ✅ Exists |
| `post_execution_verification_started` | INFO | `ExecutionBridge` | ❌ Needs implementation |
| `post_execution_reindex_started` | INFO | Engine | ❌ Needs implementation |
| `post_execution_reindex_completed` | INFO | Engine | ❌ Needs implementation |
| `verification_scope_violation` | CRITICAL | `PostExecutionVerifier` | ❌ Needs implementation |
| `verification_collateral_damage` | CRITICAL | `PostExecutionVerifier` | ❌ Needs implementation |
| `verification_returned_for_revision` | CRITICAL | `PostExecutionVerifier` | ❌ Needs implementation |

## Expected Detail Payload

For `verification_passed`:
```json
{
  "proposal_id": "prop_abc123...",
  "files_expected_to_change": 2,
  "files_actually_changed": 2,
  "files_protected": 3,
  "scope_violations": 0,
  "collateral_damage_count": 0,
  "structural_warnings": 0
}
```

For `verification_failed`:
```json
{
  "proposal_id": "prop_abc123...",
  "scope_violations": [{"file": "/absolute/path", "reason": "File modified but not authorized"}],
  "collateral_damage": []
}
```
