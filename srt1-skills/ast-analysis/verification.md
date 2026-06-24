# AST Analysis — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| AST Parses Successfully | Returns non-empty list of symbols for syntactically correct source files. |
| Structural Completeness | Extracted line and end-line spans match exact code boundaries. |
| Zero Side Effects | File content is identical pre/post parsing (no mutations). |
| Cross-Reference Consistency | Extracted dependencies mapped to valid targets where possible. |

## Failure Indicators

| Indicator | Meaning |
|-----------|---------|
| Blank Symbol List | Parser failed or file was empty. |
| Crash / Pipeline Interruption | SyntaxError or parsing library exceptions unhandled (should degrade to warnings). |
| Mapped Span Mismatch | Line number indices do not match actual symbol spans in source. |
