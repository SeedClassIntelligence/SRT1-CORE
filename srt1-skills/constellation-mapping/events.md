# Constellation Mapping — Events

## Emitted Events

| Event | Severity | Emitter | Status |
|-------|----------|---------|--------|
| `constellation_peer_discovered` | INFO | `SRT1Engine` | ❌ Needs implementation |
| `constellation_peer_lost` | WARNING | `SRT1Engine` | ❌ Needs implementation |
| `workspace_scan_completed` | INFO | `WorkspaceConnector` | ❌ Needs implementation |
| `repo_sandbox_registered` | INFO | `SRT1Engine` | ❌ Needs implementation |
| `repo_sandbox_heartbeat` | DEBUG | `SRT1Engine` | ❌ Needs implementation |

## Expected Detail Payload

For `constellation_peer_discovered`:
```json
{
  "peer_port": 7486,
  "peer_repo": "/path/to/peer/repo",
  "file_count": 87,
  "symbol_count": 540,
  "discovered_at": "2026-06-11T17:12:20Z"
}
```
