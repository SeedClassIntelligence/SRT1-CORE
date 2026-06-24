# Repo Indexing — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Symbol table populated | `len(symbol_table) > 0` |
| Manifest written | `srt1_code_manifest.json` exists and is valid JSON |
| No HARD_STOP violations | `curation_report` has no critical violations |
| Context docs generated | At least `AGENTS.md` written |
| Manifest hash computed | `integrity.manifest_hash` present |

## Failure Indicators

| Indicator | Meaning |
|-----------|---------|
| `symbol_table` is empty | No parseable files found or all excluded |
| Manifest write fails | Disk full, permissions, or path error |
| AST parse errors on Python files | Syntax errors in source — logged as warnings |
| Index takes > 60s | Possible recursive inclusion or very large repo |
