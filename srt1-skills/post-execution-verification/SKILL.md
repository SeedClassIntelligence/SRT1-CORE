# Post-Execution Verification Skill

> **Skill ID:** `SRT1-SKILL-007`
> **Module:** Verification
> **Authority:** Verification
> **Classification:** Public Core / Pro Candidate
> **Mutates Source:** Never

## Purpose

Post-Execution Verification compares intended changes against actual repository
changes after an assistant, execution actor, or developer action completes. It
owns evidence and verdicts, not lifecycle truth.

Continuity owns final seed lifecycle state. Verification provides the result
that lets Continuity and Human Co-Creation decide whether work is awaiting
review, completed, returned, partial, or failed.

## Current State

This capability is partially implemented. The building blocks include file
hashing, re-indexing, completion metadata, and tests around continuity identity.
Some verifier paths may still require implementation or cleanup.

| Capability | Status |
|---|---|
| Pre/post hash comparison | partial |
| Scope validation | partial / needs audit |
| Re-index after change | partial |
| Human review handoff | partial |
| Returned/revision metadata | partial |
| Trust metadata handoff | planned |

## Activation

| Trigger | Source | Frequency |
|---|---|---|
| Pre-change snapshot | WorkCell/proposal preparation | Before governed change |
| Completion proposed | Assistant/developer/WorkCell completion signal | On completion request |
| Post-change verification | Verification route/service | After proposed completion |
| Human review | Dashboard / Human Co-Creation | Before final acceptance when required |
| Re-index event | Repo Understanding | After accepted or detected changes |

## Preconditions

- Canonical `queue_seed_id` is resolved when seed-scoped.
- Intended change scope is known through proposal, WorkCell, or allowed paths.
- Pre-change hashes/snapshots are available when the flow requires them.
- Repo root and WorkCell boundary are known.
- Private signing/Seed Signature service is not required for verification to run;
  missing signing metadata is represented as trust metadata.

## Inputs

| Input | Type | Source |
|---|---|---|
| `queue_seed_id` | String | Continuity |
| `srt_anchor_id` | String/null | Reflection metadata |
| Change proposal / intended scope | Dict | WorkCell / Human Co-Creation |
| Allowed reads/writes | List/dict | Context Isolation |
| Pre-change hashes | Dict | Snapshot |
| Post-change hashes | Dict | Snapshot |
| Manifest hash | String | Repo Understanding |
| Trust metadata | Dict | Trust Awareness / Seed Signature attachment metadata |

## Outputs

| Output | Type | Meaning |
|---|---|---|
| Verification result | Dict/object | Verdict and evidence |
| Verdict | String | verified, partial, failed, returned, or unknown |
| Scope violations | List | Unauthorized modifications |
| Collateral damage | List | Protected files unexpectedly changed |
| Structural warnings | List | Syntax/build/test concerns |
| Re-index request | Dict/event | Repo Understanding should refresh |
| Continuity recommendation | Dict | Suggested lifecycle transition, not lifecycle authority |

## Runtime Responsibilities

1. Compare intended scope with actual changed files.
2. Detect unauthorized file modifications.
3. Detect protected-file collateral damage.
4. Check structural validity where supported.
5. Preserve canonical identity metadata.
6. Separate verification verdict from lifecycle transition.
7. Trigger or request re-index after accepted changes.
8. Surface evidence for human review and trust metadata.

## Boundary Rules

| Rule | Enforcement |
|---|---|
| Read-only verifier | Does not write, edit, delete, or rollback source files |
| Verdict only | Does not own final lifecycle state |
| Continuity separation | Completion state is recorded by seed queue/Continuity |
| Human review separation | Human Co-Creation accepts, rejects, or returns work |
| No private rollback executor | Public Core does not perform private rollback automation |
| Trust metadata only | Seed Signature attachment is metadata unless external signer is configured |

## Verification

| Check | Success condition |
|---|---|
| Snapshot available | Pre-change evidence exists or degraded reason is explicit |
| Scope holds | Actual changes stay within approved WorkCell/proposal scope |
| Protected files unchanged | Must-not-change files remain identical |
| Structural checks pass | Supported modified files remain parseable/buildable where tested |
| Identity preserved | Result includes `queue_seed_id` and optional `srt_anchor_id` |
| Lifecycle not collapsed | Verification result does not directly overwrite lifecycle truth |

Failure indicators include no pre-snapshot when required, changed files outside
scope, protected file mutation, missing identity metadata, hidden degraded
state, or direct completion without review/verification evidence.

## Events

| Event | Severity | Status |
|---|---|---|
| `post_execution_snapshot_taken` | info | exists/planned depending on runtime path |
| `post_execution_verification_started` | info | planned |
| `verification_passed` | critical/info by policy | exists/planned depending on runtime path |
| `verification_failed` | critical | exists/planned depending on runtime path |
| `verification_scope_violation` | critical | planned |
| `verification_returned_for_revision` | warning | planned |
| `post_execution_reindex_requested` | info | planned |

## Source of Truth

- `srt1_platform/verification.py`, if present
- `srt1_platform/change_proposal.py`, if present
- `srt1_platform/seed_queue.py` for lifecycle handoff
- `srt1_code_indexer/engine.py` completion orchestration paths
- `srt1-skills/contracts/post_execution_verification_contract.md`
