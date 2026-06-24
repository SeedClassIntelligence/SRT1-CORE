# FileCell Manifest Derivation — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Manifest created | `FileCellManifest` object returned with non-empty `cell_id` |
| Dependencies resolved | `dependencies` list contains all transitive targets up to depth=2 |
| Forbidden excluded | No path in `allowed_reads` or `allowed_writes` matches `ALWAYS_FORBIDDEN_PATTERNS` |
| Escalation enforced | Protected-role targets without domain raise exception during derivation |
| Output dir exists | `sion_output/{seed_id}/` directory created on disk |

## Failure Indicators

| Indicator | Meaning |
|-----------|-------|
| `files_likely` target rejected | File not found in `symbol_table` |
| Exception during derivation | Semantic escalation triggered without domain sponsorship |
| Empty `allowed_reads` | Dependency walk failed or all targets forbidden |
