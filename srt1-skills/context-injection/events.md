# Context Injection — Events

## Emitted Events

The context injection system reports formatting and document synchronization events:

| Event | Severity | Emitter | Status |
|-------|----------|---------|--------|
| `context_injection_updated` | INFO | `SRT1Engine` | ❌ Needs implementation |
| `context_injection_seed_added` | INFO | `ExecutionBridge` | ❌ Needs implementation |
| `context_injection_seed_removed` | INFO | `ExecutionBridge` | ❌ Needs implementation |
| `context_injection_failed` | WARNING | `SRT1Engine` | ❌ Needs implementation |

## Expected Detail Payload

For `context_injection_updated`:
```json
{
  "files_updated": ["AGENTS.md", "CLAUDE.md", ".cursorrules"],
  "symbol_count": 640,
  "timestamp": "2026-06-11T17:12:20.572957"
}
```
For `context_injection_seed_added`:
```json
{
  "seed_id": "seed_0001_abc12345",
  "injected_files": ["AGENTS.md", "pending_seed.md"]
}
```
