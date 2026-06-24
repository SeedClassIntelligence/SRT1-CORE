# Module Boundary Protection — Inputs & Outputs

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Target path | `str` (absolute) | execution actor operation | File path being accessed |
| `FileCellManifest` | Dataclass | `ManifestDeriver` | Contains `allowed_reads`, `allowed_writes`, `forbidden_paths` |
| `symbol_table` | `Dict` | SRT-1 Engine | Used during derivation for dependency walking |
| `domains` | `List[str]` | ChangeProposal | Authorized domain tags for semantic escalation checks |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| Validation result | `True` or exception | `True` if path is permitted; `FileCellBoundaryViolation` if blocked |
| `FileCellManifest` | Dataclass | Output of derivation — includes dependency reasoning log |
