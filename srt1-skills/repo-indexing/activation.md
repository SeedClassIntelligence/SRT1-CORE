# Repo Indexing — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Engine startup | `SRT1Engine.__init__()` → `self._run_index_pipeline()` | Once |
| File change detected | `_file_watcher_loop()` polls every 15s, checks mtimes | On change |
| Manual re-index | `POST /api/reindex` | On demand |
| Constellation peer request | `GET /api/status` triggers status report (index assumed current) | On demand |

## Pre-conditions

- `workspace_root` exists and is readable
- Python interpreter has file system access
- No active `LOCKOUT` enforcement event

## Post-conditions

- `symbol_table` populated in memory
- `call_graph` populated in memory
- `srt1_code_manifest.json` written to `workspace_root`
- Context docs regenerated (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `copilot-instructions.md`)
