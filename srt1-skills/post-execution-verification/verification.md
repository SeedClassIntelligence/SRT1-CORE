# Post-Execution Verification — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Snapshot taken | Pre-execution hashes stored before execution actor runs |
| Only authorized files changed | `files_actually_changed` is a subset of `files_write ∪ files_create` |
| Protected files unchanged | All files in `files_must_not_change` have identical hashes pre/post |
| No syntax corruption | All modified `.py` files compile without `SyntaxError` |
| Events emitted | `verification_passed` or `verification_failed` recorded in event log |

## Failure Indicators

| Indicator | Meaning |
|-----------|-------|
| Scope violation detected | execution actor modified files outside its FileCell |
| Collateral damage | Protected file unexpectedly changed |
| Structural warning | Modified Python file has syntax errors |
| No pre-snapshot found | `capture_snapshot()` was not called before dispatch |
