# Constellation Mapping Skill

> **Skill ID:** `SRT1-SKILL-008`
> **Module:** WorkspaceConnector + OperationalRegistry + Engine
> **Classification:** UNDERSTANDING
> **Mutates Source:** ❌ Never

---

## Purpose

Maps multiple isolated repo/module sandboxes into a unified architectural view without cross-module state bleed. Each engine is sovereign in its sandbox; this skill provides read-only visibility across the constellation.

---

## Activation

| Trigger | Source |
|---------|--------|
| Engine startup | Registers self in `OperationalRegistry` |
| `/api/constellation` request | Engine queries registered peers via HTTP |
| `WorkspaceConnector` scan | CLI-driven cross-module dependency mapping |
| `/api/status` response | Includes constellation peer data |

## Inputs

| Input | Type | Source |
|-------|------|--------|
| `OperationalRegistry` | Global `~/.srt1/registry.json` | All engines read/write |
| Peer engine HTTP endpoints | `http://127.0.0.1:{port}/api/status` | Localhost only |
| Workspace root directories | `List[str]` | From registry or CLI |

## Outputs

| Output | Type |
|--------|------|
| Peer list | `List[Dict]` — `{repo_path, port, status, file_count, symbol_count}` |
| Dependency map | `Dict[module → Set[dependency_modules]]` | WorkspaceConnector |
| Health report | `Dict` — per-module health with sync status |
| Architecture digest | Cross-module role/risk aggregation |

## Isolation Guarantees

| Rule | Enforcement |
|------|-------------|
| No shared memory | Engines run as separate processes |
| No cross-import | No `sys.path` injection between engines |
| Communication via HTTP only | `requests.get(f"http://127.0.0.1:{port}/api/status")` |
| Read-only queries | Constellation API is GET-only — no mutations |
| Stale peers tolerated | Dead peers return last-known status, marked as `stale` |

## Governance

- Each engine only serves its own data
- No engine can trigger actions in another engine
- Registry is append/update only — no engine can delete another's entry
- `WorkspaceConnector` performs directory scans, never modifies source

## Events

| Event | Severity | Status |
|-------|----------|--------|
| `constellation_peer_discovered` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `constellation_peer_lost` | WARNING | ❌ NEEDS_IMPLEMENTATION |
| `workspace_scan_completed` | INFO | ❌ NEEDS_IMPLEMENTATION |

## Source of Truth

- [engine.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_code_indexer/engine.py) — `/api/constellation` endpoint
- [operational_registry.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/operational_registry.py) — Global registry
- [workspace_connector.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_pro/workspace_connector.py) — Cross-module scanning
