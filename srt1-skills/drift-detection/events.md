# Drift Detection — Events

## Emitted Events

The Drift Detection system uses Tracing and Auditing lifecycle events:

| Event | Severity | Emitter | Status |
|-------|----------|---------|--------|
| `trace_start` | INFO | `TracingSystem` | ✅ Exists |
| `trace_complete` | INFO | `TracingSystem` | ✅ Exists |
| `coherence_checkpoint_fired` | INFO | `SRT` | ❌ Needs implementation (suggested) |

## Expected Detail Payload

For a suggested `coherence_checkpoint_fired` event:
```json
{
  "checkpoint_id": "checkpoint_abc123...",
  "seed_id": "seed_0001_abc12345",
  "coherence_score": 0.85,
  "coherence_status": "ON_TASK",
  "drift_indicators": [],
  "ops_analyzed": ["repo_indexer.index_repository", "ast_analysis.parse"]
}
```
