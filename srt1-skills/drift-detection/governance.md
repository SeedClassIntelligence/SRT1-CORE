# Drift Detection — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Read-Only Observer | Never writes files or modifies codebase source code; only generates transient checkpoints in memory. |
| Advisory Mode vs Enforcement Mode | In `advisory` mode (default), drift does not halt operations. In `enforcement` mode, any `check_enforcement()` check that encounters a `HARD_STOP` or `LOCKOUT` status returns a blocking event that prevents further steps. |
| Coherence Scopes | Checks keyword intersections exclusively on recent operation names and metadata; doesn't index codebase files directly. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| `SRT` (self) | ✅ Primary caller during tracing loop |
| `McpServer` | ✅ Via `srt1_log_interaction` |
| execution actor | ❌ execution actor cannot clear or bypass drift status |

## execution actor Interaction

execution actor has no ability to alter the drift detection state. If execution actor's operations deviate from the planted seed, drift will be flagged by SRT-1. execution actor is the actor; SRT-1 remains the independent observer.
