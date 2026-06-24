# Context Injection — Inputs & Outputs

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| `symbol_table` | `Dict` | In-memory Engine state | Current index mapping filepaths to symbol arrays |
| `curation_report` | `Dict` | In-memory Engine state | Detected function duplicates and overlaps |
| `manifest` metadata | `Dict` | In-memory Engine state | File counts, language coverage statistics |
| Seed Intent | `str` | `ExecutionBridge` / Seed Queue | The active task description and keywords to plant |

## Outputs

| Output | Destination | Description |
|--------|-------------|-------------|
| `AGENTS.md` | `{workspace_root}/AGENTS.md` | Complete codebase architecture map |
| `CLAUDE.md` | `{workspace_root}/CLAUDE.md` | Condensed summary for Claude Code |
| `.cursorrules` | `{workspace_root}/.cursorrules` | Codebase formatting and architectural instructions |
| `copilot-instructions.md` | `{workspace_root}/docs/.github/copilot-instructions.md` | GitHub Copilot instruction manifest |
| MCP tool response | JSON-RPC | Direct context payload injected into AI assistant |
