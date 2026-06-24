# AST Analysis — Inputs & Outputs

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Source File Content | `str` | File System | Raw code text read from target file path |
| File Path | `str` | File System / Indexer | Absolute path used to map symbols back to files |
| File Extension | `str` | File System / Indexer | File extension (e.g. `.py`, `.js`) determining parser dispatch |

## Outputs

| Output | Type | Destination | Description |
|--------|------|-------------|-------------|
| Symbol List | `List[Dict]` | In-memory / `symbol_table` | List of dictionaries: `{name, type, line, end_line, parameters, dependencies, docstring}` |
| Architectural Reflection | `Dict` | In-memory / `symbol_table` | Dict containing `{architectural_role, risk_profile, purpose}` from semantic analysis |
