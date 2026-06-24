# Post-Execution Verification — Inputs & Outputs

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| `proposal_id` | `str` | `ChangeProposal` | The proposal being verified |
| `files_write` | `List[str]` | `ChangeProposal.files_write` | Files authorized for modification |
| `files_create` | `List[str]` | `ChangeProposal.files_create` | Files authorized for creation |
| `files_delete` | `List[str]` | `ChangeProposal.files_delete` | Files authorized for deletion |
| `files_must_not_change` | `List[str]` | `ChangeProposal.expected_verification` | Protected files that must remain identical |
| Pre-execution snapshots | `Dict[str, str]` | Stored by `capture_snapshot()` | SHA-256 hashes before execution actor executed |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `VerificationResult` | Object | Verdict: `VERIFIED`, `PARTIAL_PASS`, or `FAILED` |
| `scope_violations` | `List[Dict]` | Unauthorized modifications detected |
| `collateral_damage` | `List[Dict]` | Protected files that changed |
| `structural_warnings` | `List[str]` | Non-fatal syntax issues in modified `.py` files |
| `stats` | `Dict` | Numerical summary of all checks |
