# Constellation Mapping — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Read-Only Queries | All peer HTTP calls are GET-only — no mutations triggered via constellation. |
| No Shared Memory | Engines run as separate OS processes with no shared Python globals or imports. |
| Localhost-Only Communication | Peer discovery only contacts `http://127.0.0.1:{port}/api/status`. No external network. |
| No Cross-Engine Triggers | One engine can never trigger re-indexing, seeding, or execution in another engine. |
| Stale Tolerance | Dead or unreachable peers return last-known status, marked `stale`. No blocking behavior. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| `SRT1Engine` (self) | ✅ Registers in registry at startup |
| `WorkspaceConnector` CLI | ✅ Cross-module scanning |
| execution actor | ❌ Forbidden — execution actor cannot query peer engines |
| External network callers | ❌ Localhost-only |
