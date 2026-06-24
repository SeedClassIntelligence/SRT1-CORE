# Repo Indexing — Inputs & Outputs

## Inputs

| Input | Type | Source |
|-------|------|--------|
| `workspace_root` | `str` (absolute path) | CLI argument or Engine constructor |
| Source files | File system | Directory walk with extension filter |
| `.gitignore` patterns | Text file | Parsed for exclusion rules |
| `SUPPORTED_EXTENSIONS` | Set | `.py, .js, .ts, .html, .css, .json, .md, .yaml, .yml, .toml, .cfg, .ini, .xml, .sql, .sh, .bat, .ps1, .cs, .java, .go, .rs, .rb, .php, .swift, .kt` |

## Outputs

| Output | Type | Destination |
|--------|------|-------------|
| `symbol_table` | `Dict[str, List[Dict]]` | In-memory (Engine attribute) |
| `call_graph` | `Dict[str, List[str]]` | In-memory (Engine attribute) |
| `curation_report` | `Dict` containing `file_duplicates`, `functional_overlaps` | In-memory |
| `srt1_code_manifest.json` | JSON file | `{workspace_root}/srt1_code_manifest.json` |
| `file_tree` | `Dict[str, Any]` | Nested directory structure for dashboard |
| `language_coverage` | `Dict[str, int]` | File count by extension |
| Context docs | Markdown files | `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `copilot-instructions.md` |
