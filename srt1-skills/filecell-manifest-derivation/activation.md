# FileCell Manifest Derivation — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Seed execution request | `ExecutionBridge` or external authorization authority pre-execution actor step | Once per seed execution |
| `LeastPrivilegeManifestDeriver.derive()` call | Execution pipeline with `seed_id`, `task`, `files_likely`, `domains` | On demand |

## Pre-conditions

- `symbol_table` and `call_graph` are populated (index is current).
- `ChangeProposal` has been validated by `ProposalValidator`.
- `files_likely` targets have been declared in the proposal.
- `ExecutionLease` has not yet been granted (manifest comes first).

## Post-conditions

- `FileCellManifest` is created with `allowed_reads`, `allowed_writes`, `forbidden_paths`, and `dependency_reasoning`.
- Output directory `{workspace_root}/sion_output/{seed_id}/` created.
- `filecell_manifest_derived` event emitted to event log.
