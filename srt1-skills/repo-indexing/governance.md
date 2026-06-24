# Repo Indexing — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Only reads files within `workspace_root` | Path canonicalization + `commonpath` check |
| Never writes to source files | Writes only to `srt1_code_manifest.json` and context docs |
| Respects `.gitignore` | Patterns parsed and applied during directory walk |
| Skips `EXCLUDED_DIRS` | `__pycache__`, `.git`, `node_modules`, `venv`, `.srt1`, etc. |
| Skips binary/large files | Extension filter + size guard |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| Engine (self) | ✅ Primary caller |
| Dashboard API (`/api/reindex`) | ✅ Manual trigger |
| Workspace Connector | ✅ For cross-module scanning |
| execution actor | ❌ execution actor must not trigger re-indexing directly |
| External API | ❌ No public re-index endpoint |

## execution actor Interaction

execution actor never calls this skill. After execution actor mutates files, the file watcher detects changes and triggers re-indexing automatically. This preserves the separation: **execution actor acts, SRT-1 observes**.
