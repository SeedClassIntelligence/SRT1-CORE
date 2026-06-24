# Context Injection — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Read-Only for Source | Writes ONLY to context files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `copilot-instructions.md`, and `.srt1/pending_seed.md`). Never modifies codebase source files. |
| Exclusion of Secrets | Strictly filters file listings against `ALWAYS_FORBIDDEN_PATTERNS` to prevent database or API credential leakage. |
| Metadata-Only Synopsis | Synopsis files contain counts, roles, risk profiles, and structural summaries. Raw source code snippets are not exported. |
| FileCell Protection of AGENTS.md | `AGENTS.md` is hidden from execution actor's read boundary by default, preventing execution engines from dynamically parsing and bypassing security instructions. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| `SRT1Engine` | ✅ Primary Caller |
| `ExecutionBridge` | ✅ For seed tracking injection |
| `McpServer` | ✅ For live tools integration |
| execution actor | ❌ Forbidden |

## execution actor Interaction

execution actor has no access to this skill. After execution actor completes mutations, the engine's file watcher will trigger the indexer, which in turn invokes `_generate_context_docs()`, keeping the context updated passively.
