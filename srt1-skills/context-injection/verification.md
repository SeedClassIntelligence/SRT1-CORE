# Context Injection — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Documents Written | Target files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`) exist and have size > 0. |
| Stats Match Live State | File count and symbol statistics in synopsis match the live in-memory indices. |
| Seed Block Present | Active seeds show up inside `AGENTS.md` and `.srt1/pending_seed.md` during execution. |
| Seed Block Reverted | Seed injection blocks are cleanly removed from files after task completion or wilting. |

## Failure Indicators

| Indicator | Meaning |
|-----------|---------|
| Missing files | Write permissions blocked, or engine crashed before generation. |
| Stale synopsis data | Statistics inside files do not match the live manifest count. |
| Cryptographic secret leakage | Forbidden patterns found in target context files. |
