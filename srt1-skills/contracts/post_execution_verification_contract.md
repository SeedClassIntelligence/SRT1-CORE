# Post-Execution Verification Contract

**Contract ID:** `SRT1-CONTRACT-VERIFY-001`
**Between:** WorkCell Output and SRT-1 Verification
**Status:** Public Core / Pro Candidate

## Purpose

Verify actual repository changes against intended scope after a proposed
assistant/developer action. Verification owns evidence and verdicts. Continuity
owns lifecycle state. Human Co-Creation owns accept, reject, or return decisions.

## Contract Fields

```yaml
verification_id: string
proposal_id: string | null
queue_seed_id: string
srt_anchor_id: string | null
workcell_id: string | null
repo_root: path
manifest_hash_before: string | null
manifest_hash_after: string | null
declared_files: list[path]
actual_changed_files: list[path]
scope_violations: list[object]
collateral_damage: list[object]
structural_warnings: list[string]
verdict: verified | partial | failed | returned | unknown
trust_state: signed | unsigned | verified | unverified | degraded | unknown
signature_id: string | null
verified_at: datetime
```

## Guarantees

- Verification compares intended scope to actual changes.
- Unauthorized modifications are flagged as scope violations.
- Protected files are checked for collateral damage.
- Supported files may receive structural/syntax checks.
- Verification result does not directly overwrite seed lifecycle truth.
- Accepted changes should trigger Repo Understanding re-index.

## Trust And Attribution

If Seed Signature enforcement is required, verification must expose whether a
valid `signature_id` or returned trust metadata is present. Public Core may
label work unsigned/unverified or fail closed. The standalone Seed Signature
platform performs signing.

## Refusal Conditions

- No canonical `queue_seed_id` exists for seed-scoped verification.
- Intended scope is unknown.
- Actual changed files cannot be determined and no degraded reason is recorded.
- Required signature attribution is unavailable.
- Verification would require private rollback or private signing code.

## Events

```text
post_execution_verification_started
post_execution_reindex_requested
verification_passed
verification_failed
verification_partial
verification_scope_violation
verification_returned_for_revision
```
