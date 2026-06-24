# Post-Execution Verification — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Read-Only Verifier | Only reads file hashes (SHA-256). Never writes, edits, or deletes. |
| Snapshot Integrity | Pre-execution hashes are stored in memory under `proposal_id` key. Not modifiable between capture and verify. |
| Independent Observer | SRT-1 acts as the independent post-execution auditor. execution actor has no ability to modify verification results. |
| Scope Boundary | Any file modified outside `files_write ∪ files_create` is flagged as a scope violation. |
| Collateral Detection | Files in `files_must_not_change` are verified byte-identical before and after. |
| Structural Integrity | Modified `.py` files are compiled with `compile()` to detect syntax corruption. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| `ExecutionBridge` | ✅ Orchestrates snapshot and verify calls |
| SRT-1 Engine (direct) | ✅ If wired into completion detection |
| execution actor | ❌ execution actor cannot call or influence verification |
| Human operator | ❌ No direct API — only via execution pipeline |

## execution actor Interaction

execution actor completes mutation, then stops. SRT-1 takes over and runs verification independently. execution actor cannot alter, delay, or bypass this check. Verification verdict determines whether the seed advances to BLOOMED or reverts.
