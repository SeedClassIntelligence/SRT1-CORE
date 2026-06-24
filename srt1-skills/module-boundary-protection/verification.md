# Module Boundary Protection — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Boundary holds | Write outside `allowed_writes` raises `FileCellBoundaryViolation` |
| Forbidden blocked | `.env`, `.git`, `*.key` paths are never in `allowed_reads` or `allowed_writes` |
| Symlink resolved | `os.path.realpath()` applied before validation |
| Escalation enforced | Protected role without domain sponsorship raises `Exception` |
| Audit emitted | Every violation triggers a event log record |

## Failure Indicators

| Indicator | Meaning |
|-----------|-------|
| No exception raised on forbidden path | Guard check bypassed or path not canonicalized |
| `AGENTS.md` in allowed reads without reason | Authorization logic failure |
| Symlinked path bypassing restrictions | `realpath()` not applied |
