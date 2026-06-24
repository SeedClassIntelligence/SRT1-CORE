# Constellation Mapping — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Engine startup | Engine registers self in `OperationalRegistry` at startup | Once |
| `/api/constellation` request | HTTP GET query to local engine endpoint | On demand |
| `WorkspaceConnector` scan | CLI-driven cross-module dependency mapping | On demand |
| `/api/status` response | Includes consolidated constellation peer data | On status query |

## Pre-conditions

- `OperationalRegistry` file (`~/.srt1/registry.json`) is accessible.
- Target peer engines are running and reachable on localhost.
- Current engine has a valid `workspace_root` and `port` assigned.

## Post-conditions

- Peer list hydrated and marked `live` or `stale`.
- Architecture digest computed across all reachable engines.
- Health report available per module.
