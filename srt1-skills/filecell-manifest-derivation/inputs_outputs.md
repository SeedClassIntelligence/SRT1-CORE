# FileCell Manifest Derivation — Inputs & Outputs

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| `seed_id` | `str` | Seed Queue | Unique identifier for this execution |
| `task` | `str` | `ChangeProposal` | Human-readable task description |
| `files_likely` | `List[str]` | `ChangeProposal` / LLM intent classifier | Files likely touched by the task |
| `domains` | `List[str]` | `ChangeProposal` | Authorized domain tags |
| `symbol_table` | `Dict` | SRT-1 Engine | Maps filepaths to symbol arrays |
| `call_graph` | `Dict` | SRT-1 Engine | Maps function names to called function names |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `FileCellManifest` | Dataclass | `cell_id`, `allowed_reads`, `allowed_writes`, `forbidden_paths`, `dependencies`, `dependency_reasoning` |
| Output Directory | `Path` | `{workspace_root}/sion_output/{seed_id}/` created on filesystem |
