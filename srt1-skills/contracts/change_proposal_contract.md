# Change Proposal Contract

**Contract ID:** `SRT1-CONTRACT-CHANGEPROP-001`
**Between:** Assistant/Developer Action and SRT-1 Verification
**Status:** Public Core / Pro Candidate

## Purpose

Define the evidence required before a governed change is treated as ready for
execution, review, verification, or completion. A Change Proposal describes
what should change, where it may change, why it is in scope, and how it will be
verified.

## Contract Fields

```yaml
proposal_id: string
queue_seed_id: string
srt_anchor_id: string | null
workcell_id: string | null
repo_root: path
created_by: assistant | developer | srt1
created_at: datetime
objective: string
target_files: list[path]
allowed_reads: list[path]
allowed_writes: list[path]
forbidden_paths: list[path]
risk_level: low | medium | high | critical
risk_reason: string
expected_verification: object
trust_required: boolean
signature_id: string | null
status: draft | proposed | awaiting_review | approved | rejected | returned | completed
```

## Guarantees

- No governed mutation is accepted as complete without known scope.
- Target files must live inside the registered repo sandbox.
- WorkCell/FileCell boundaries define allowed reads and writes.
- Protected/private paths are never included.
- Human review can approve, reject, return, or request scope changes.
- Seed Signature metadata can be required as attribution/trust metadata.

## Public Core Boundary

SRT-1 Core may prepare, validate, display, and verify Change Proposals. It may
hand a proposal to a configured assistant adapter or developer workflow. It does
not ship private execution backends, private rollback executors, or private
signing infrastructure.

## Refusal Conditions

- Proposal targets paths outside the sandbox.
- Proposal touches forbidden/private paths.
- Proposal lacks canonical `queue_seed_id` for seed-scoped work.
- Proposal requires trust attribution but has no attached/available Seed
  Signature metadata.
- Proposal expands WorkCell scope without dependency evidence or approval.

## Events

```text
change_proposal_created
change_proposal_validated
change_proposal_rejected
change_proposal_approved
change_proposal_returned
change_proposal_scope_changed
verification_requested
```
