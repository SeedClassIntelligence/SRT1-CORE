# Repo Indexing — Events

## Emitted Events

| Event | Severity | Status |
|-------|----------|--------|
| `repo_index_started` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `repo_index_completed` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `repo_index_failed` | HIGH | ❌ NEEDS_IMPLEMENTATION |
| `context_docs_generated` | INFO | ❌ NEEDS_IMPLEMENTATION |

## Expected Detail Payload

```json
{
  "repo_index_started": {
    "workspace_root": "/path/to/repo",
    "trigger": "startup|file_watcher|manual",
    "file_count_estimate": 87
  },
  "repo_index_completed": {
    "workspace_root": "/path/to/repo",
    "files_indexed": 87,
    "symbols_found": 640,
    "classes_found": 98,
    "functions_found": 542,
    "duration_ms": 3200,
    "manifest_hash": "abc123..."
  }
}
```
