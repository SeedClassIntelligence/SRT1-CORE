# AST Analysis — Events

## Emitted Events

AST Analysis runs as a subset of the repository indexing pipeline and does not emit dedicated event log events on a per-file basis to avoid database bloat. 

Its execution is recorded within the broader indexing lifecycle:

| Lifecycle Event | Severity | Emitter |
|---|---|---|
| `repo_index_started` | INFO | `SRT1Engine` |
| `repo_index_completed` | INFO | `SRT1Engine` |
| `repo_index_failed` | HIGH | `SRT1Engine` |

## Expected Detail Payload

Any exceptions or parsing failures caught during AST Analysis are logged as warning details in the `repo_index_completed` or `repo_index_failed` event payloads.
