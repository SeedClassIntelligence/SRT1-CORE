# Context Injection Skill

> **Skill ID:** `SRT1-SKILL-003`
> **Module:** SRT-1 Engine + MCP Server
> **Classification:** UNDERSTANDING → OBSERVING
> **Mutates Source:** ❌ Never (writes only to context/instruction files)

---

## Purpose

Updates AI assistant context files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `copilot-instructions.md`) with live codebase intelligence. Also provides live injection via MCP protocol tools during AI conversations.

---

## Activation

| Trigger | Source | Target |
|---------|--------|--------|
| Engine startup | `_generate_context_docs()` | All 4 target files |
| Manifest regeneration | File watcher → re-index → context docs | All 4 target files |
| Seed dispatch | `ExecutionBridge` | `AGENTS.md` (seed block), `pending_seed.md` |
| MCP tool call | `srt1_get_context`, `srt1_log_interaction` | Direct AI context injection |

## Inputs

| Input | Type |
|-------|------|
| `symbol_table` | In-memory symbol map |
| `curation_report` | Duplicate/overlap warnings |
| `manifest` metadata | File counts, language stats |
| Seed intent (when dispatching) | Task string + blueprint |

## Outputs

| Output | Destination |
|--------|-------------|
| `AGENTS.md` | `{workspace_root}/AGENTS.md` |
| `CLAUDE.md` | `{workspace_root}/CLAUDE.md` |
| `.cursorrules` | `{workspace_root}/.cursorrules` |
| `copilot-instructions.md` | `{workspace_root}/docs/.github/copilot-instructions.md` |
| MCP tool response | stdio (JSON-RPC) |

## Governance

- Content is metadata only — never includes raw source code
- Never includes secret file references (governed by `ALWAYS_FORBIDDEN_PATTERNS`)
- Idempotent: same manifest produces same output
- `AGENTS.md` is NOT readable by execution actor without explicit FileCell authorization
- Seed injection is temporary — removed on seed completion

## Verification

| Check | Condition |
|-------|-----------|
| Files written | At least `AGENTS.md` exists after startup |
| Content matches manifest | Synopsis stats match `symbol_table` |
| Seed block removed | After seed completion, `AGENTS.md` no longer contains seed block |

## Events

| Event | Severity | Status |
|-------|----------|--------|
| `context_injection_updated` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `context_injection_seed_added` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `context_injection_seed_removed` | INFO | ❌ NEEDS_IMPLEMENTATION |

## Source of Truth

- [engine.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_code_indexer/engine.py) — `_generate_context_docs()`
- [execution_bridge.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/execution_bridge.py) — Seed injection
- [mcp_server.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/mcp_server.py) — MCP tools
