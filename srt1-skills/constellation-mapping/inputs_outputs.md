# Constellation Mapping — Inputs & Outputs

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| `OperationalRegistry` | Global file | `~/.srt1/registry.json` | Registry of all active engines |
| Peer engine HTTP endpoints | HTTP GET | `http://127.0.0.1:{port}/api/status` | Status from each registered peer |
| Workspace root directories | `List[str]` | Registry or CLI arguments | Paths to scan for cross-module dependencies |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| Peer list | `List[Dict]` | `{repo_path, port, status, file_count, symbol_count}` |
| Dependency map | `Dict[module → Set[deps]]` | Cross-module dependency graph from `WorkspaceConnector` |
| Health report | `Dict` | Per-module health with sync status |
| Architecture digest | `Dict` | Aggregated role/risk summary across all modules |
