# Constellation Mapping Skill

> **Skill ID:** `SRT1-SKILL-008`
> **Module:** WorkspaceConnector + OperationalRegistry + Engine
> **Authority:** Constellation
> **Classification:** Public Core / Pro Awareness
> **Mutates Source:** Never

## Purpose

Constellation Mapping gives SRT-1 read-only awareness of multiple independent
SRT-1 runtimes, repositories, ports, and WorkCell environments. It lets the user
see how registered engines relate without merging their context or allowing one
engine to control another.

Each SRT-1 runtime remains sovereign over its own repository. Constellation
Mapping provides visibility, not shared memory and not cross-engine execution.

## Activation

| Trigger | Source | Frequency |
|---|---|---|
| Engine startup | Runtime registers itself | Once per runtime start |
| Repository launch/switch | Repository Manager | On demand |
| Dashboard constellation view | `/api/constellation` or equivalent | On demand |
| Status query | `/api/status` | On demand |
| Workspace scan | WorkspaceConnector | On demand |

## Preconditions

- Current runtime has a repository root and port.
- Registry or runtime map is accessible.
- Peer runtimes are contacted only through approved local/status endpoints.
- Missing peers can be represented as stale/unavailable without blocking the
  current runtime.

## Inputs

| Input | Type | Source |
|---|---|---|
| Runtime registry | File/dict | Operational registry / Repository Manager |
| Peer status endpoint | HTTP GET | `http://127.0.0.1:{port}/api/status` |
| Repository roots | List | Registered repositories |
| Port map | Dict | Runtime manager |
| WorkCell status summaries | Dict/list | Each owning runtime |

## Outputs

| Output | Type | Meaning |
|---|---|---|
| Peer list | List | Repo path, port, status, file/symbol counts |
| Runtime map | Dict | Which repository/workcell owns which port |
| Health report | Dict | live, stale, unavailable, degraded |
| Dependency awareness | Dict | Cross-repo/module awareness when explicitly scanned |
| Dashboard topology | Dict | User-facing constellation view |

## Runtime Responsibilities

1. Register the local SRT-1 runtime.
2. Report current runtime status.
3. Discover registered peers through read-only status calls.
4. Mark unreachable peers as stale/unavailable.
5. Preserve per-engine independence.
6. Expose topology to the dashboard without cross-context contamination.
7. Avoid automatic re-indexing or execution in peer runtimes.

## Boundary Rules

| Rule | Enforcement |
|---|---|
| Read-only peer queries | Constellation calls use status/GET-style endpoints only |
| No shared memory | Engines do not share Python globals, process state, or context stores |
| No cross-engine triggers | One runtime cannot seed, execute, re-index, or stop another by default |
| No shared context by default | Peer summaries do not inject peer source/context into local WorkCells |
| Local-first communication | Runtime awareness is local/registered unless explicitly configured |
| Stale tolerance | Dead peers are labeled, not treated as fatal |

## Verification

| Check | Success condition |
|---|---|
| Self-registration | Current runtime appears in registry/status map |
| Peer discovery safe | Peer calls are read-only |
| Stale peer handling | Unreachable peers are labeled stale/unavailable |
| No contamination | Peer context is not injected into local WorkCells by default |
| Port ownership clear | Dashboard can show which runtime owns each port |

Failure indicators include missing runtime identity, cross-engine mutation,
automatic peer re-indexing, shared context without approval, or unreachable
peers blocking the current repository.

## Events

| Event | Severity | Status |
|---|---|---|
| `constellation_peer_discovered` | info | planned |
| `constellation_peer_lost` | warning | planned |
| `repo_runtime_registered` | info | planned |
| `repo_runtime_heartbeat` | debug | planned |
| `workspace_scan_completed` | info | planned |

## Source of Truth

- `srt1_platform/operational_registry.py`
- `srt1_pro/workspace_connector.py`
- `srt1_code_indexer/engine.py` status/constellation routes
- Repository activation/runtime manager state
