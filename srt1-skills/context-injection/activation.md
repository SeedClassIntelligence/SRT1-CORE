# Context Injection — Activation

## Trigger Conditions

| Trigger | Source | Frequency / Target |
|---------|--------|--------------------|
| Engine startup | `_generate_context_docs()` | Once at startup, target files rewritten |
| Manifest regeneration | File watcher detects changes → re-index pipeline | When file watcher detects changes |
| Seed dispatch | `ExecutionBridge` | On dispatch: appends seed block to `AGENTS.md` & writes `pending_seed.md` |
| MCP tool call | AI Assistant invokes `srt1_get_context` or `srt1_log_interaction` | On assistant tool call |

## Pre-conditions

- `symbol_table` and `curation_report` are fully populated.
- File system permissions allow writing to workspace root and document paths.
- For MCP, an active communication socket / session is open.

## Post-conditions

- `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, and `copilot-instructions.md` are rewritten/created.
- Active seeds are reflected in context docs.
- Context injection is successfully cleaned up on seed completion.
