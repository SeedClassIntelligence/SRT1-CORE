# AST Analysis — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Read-Only | Never modifies source files under any circumstances. |
| Parse Failure Grace | AST syntax failures are logged as warnings rather than crashing the indexer pipeline, allowing graceful degradation. |
| Optional Enrichment | LLM enrichment is optional. If provider endpoints are offline or API keys are missing, the skill falls back to pure AST/Regex structural metadata. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| `SRT1CodeIndexer` | ✅ Primary Caller |
| `IntelligenceAdapter` | ✅ For semantic enrichment queries |
| execution actor | ❌ execution actor must never call or control AST analysis |

## execution actor Interaction

execution actor has no direct interaction with AST Analysis. execution actor operates based on derived FileCells, while SRT-1 uses AST Analysis to construct symbol and call graphs independently.
