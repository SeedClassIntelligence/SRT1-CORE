# ChangeProposal Contract
**Contract ID:** `SRT1-CONTRACT-CHANGEPROP-001`
**Between:** SRT-1 / AI Assistant ↔ external authorization authority / execution actor
**Version:** 1.0.0
**Status:** CANONICAL
**Priority:** CRITICAL — This is the biggest missing piece.

---

## Doctrine
execution actor acts. external authorization authority permits. SRT-1 sees and verifies.
No file mutation reaches execution actor without passing through a ChangeProposal Contract.
ChangeProposals are the single chokepoint between intent and action.

---

## Purpose
Define the structure, validation rules, and lifecycle of every proposed file change
before it reaches execution actor for execution. A ChangeProposal is not a request — it is a
formal, bounded declaration that must be authorized before any mutation occurs.

**No ChangeProposal = No Mutation. This is absolute.**

---

## Parties

| Party | Role |
|-------|------|
| **Proposer** | SRT-1 Engine or AI Assistant generating the change. |
| **external authorization authority** | Authorization authority. Approves, rejects, or suspends proposals. |
| **execution actor** | The only executor. Receives authorized proposals and mutates source. |
| **SRT-1** | Post-execution verifier. Does not approve — only confirms or flags. |

---

## ChangeProposal Schema

```yaml
proposal_id: string             # Unique ID. Format: CP-{sandbox_id}-{timestamp}-{hash}
sandbox_id: string              # Must match an ACTIVE Repo Sandbox Contract
seed_id: string                 # Seed that originated this change (links to Seed Intake Contract)
proposer: enum                  # SRT1_ENGINE | AI_ASSISTANT | EXECUTION_ACTOR_SELF | OPERATOR
proposed_at: datetime

# What is changing
target_files: list[FileChange]  # See FileChange schema below
scope: enum                     # SINGLE_FILE | MULTI_FILE | MODULE | CROSS_MODULE

# Risk profile
risk_level: enum                # LOW | MEDIUM | HIGH | CRITICAL
risk_reason: string             # Why this risk level was assigned
revision_plan: string           # How to undo this change if verification fails
reversible: boolean             # Whether revision is feasible

# Authorization
authorization_required: enum   # AUTO | RUNTIME_LAW | OPERATOR
authorization_status: enum     # PENDING | AUTHORIZED | REJECTED | SUSPENDED | EXPIRED
authorized_by: string | null
authorized_at: datetime | null
authorization_ttl: integer      # Seconds before authorization expires. Default: 300.

# Execution
execution_lease_id: string | null   # Set when Execution Lease is granted
execution_status: enum              # NOT_STARTED | IN_PROGRESS | COMPLETED | FAILED | ROLLED_BACK
sion_executed_at: datetime | null

# Verification
verification_status: enum      # PENDING | PASSED | FAILED | PARTIAL
verified_by: string            # Always SRT-1 Engine
verified_at: datetime | null
verification_notes: string

# Audit
audit_trail: list[AuditEvent]  # All lifecycle events for this proposal
signature_status: enum         # UNSIGNED | QUEUED | SIGNED
signature_id: string | null
```

---

## FileChange Schema

```yaml
file_path: path                 # Absolute path within sandbox
operation: enum                 # CREATE | MODIFY | DELETE | RENAME | MOVE
current_hash: string | null     # SHA256 of current file content (null for CREATE)
proposed_content_hash: string   # SHA256 of proposed content
diff_summary: string            # Human-readable summary of what changes
line_count_delta: integer       # Net line change (+ adds, - removes)
filecell_authorized: boolean    # Must be true before execution actor executes
forbidden_path_check: boolean   # Must be true (passed) before execution actor executes
```

---

## ChangeProposal Lifecycle

```
DRAFT → VALIDATION → PENDING_AUTHORIZATION → AUTHORIZED → IN_EXECUTION → COMPLETED
                                           ↘ REJECTED
                                           ↘ SUSPENDED
                          COMPLETED → VERIFICATION → PASSED → SIGNED
                                                   ↘ FAILED → ROLLBACK
```

### State Transitions

| From | To | Trigger | Actor |
|------|----|---------|-------|
| DRAFT | VALIDATION | Proposal submitted | SRT-1 / AI |
| VALIDATION | PENDING_AUTHORIZATION | All fields valid | SRT-1 |
| VALIDATION | REJECTED | Validation failure | SRT-1 |
| PENDING_AUTHORIZATION | AUTHORIZED | external authorization authority approval | external authorization authority |
| PENDING_AUTHORIZATION | REJECTED | external authorization authority denial | external authorization authority |
| PENDING_AUTHORIZATION | SUSPENDED | Operator hold | Operator |
| AUTHORIZED | IN_EXECUTION | Execution Lease granted | external authorization authority |
| IN_EXECUTION | COMPLETED | execution actor reports success | execution actor |
| IN_EXECUTION | FAILED | execution actor reports failure | execution actor |
| COMPLETED | VERIFICATION | SRT-1 re-indexes | SRT-1 |
| VERIFICATION | PASSED | Diff matches intent | SRT-1 |
| VERIFICATION | FAILED | Diff mismatch | SRT-1 |
| FAILED | ROLLBACK | Auto or manual trigger | execution actor / operator |

---

## Validation Rules (SRT-1 enforces before forwarding)

1. `sandbox_id` must match an ACTIVE Repo Sandbox Contract
2. `seed_id` must reference a valid Seed Intake Contract
3. All `target_files` must be within sandbox `repo_root`
4. No `target_file` may be in `excluded_paths`
5. `filecell_authorized` must be confirmed against FileCell Contract
6. `forbidden_path_check` must pass for every target file
7. `risk_level: CRITICAL` requires `authorization_required: OPERATOR`
8. `reversible: false` requires explicit operator acknowledgment
9. `authorization_ttl` may not exceed 3600 seconds
10. `scope: CROSS_MODULE` requires Constellation Contract to be active

---

## Authorization Rules (external authorization authority enforces)

| Risk Level | Required Authorization | TTL |
|------------|----------------------|-----|
| LOW | AUTO | 60s |
| MEDIUM | RUNTIME_LAW | 300s |
| HIGH | RUNTIME_LAW + review | 600s |
| CRITICAL | OPERATOR explicit | 3600s |

---

## What SRT-1 Does With a ChangeProposal

SRT-1 is **not** the authorizer. SRT-1:
1. **Generates** the proposal from AI output or seed intent
2. **Validates** all fields before forwarding to external authorization authority
3. **Monitors** execution status (observer only)
4. **Verifies** post-execution diff against proposed diff
5. **Emits** audit events at each lifecycle stage
6. **Flags** verification failures to execution actor and external authorization authority
7. **Signs** or queues for Seed Signature if verification passes

---

## Events Emitted

```
change_proposal_created
change_proposal_validated
change_proposal_rejected          # From validation failure
change_proposal_submitted         # Sent to external authorization authority
change_proposal_authorized
change_proposal_rejected          # From external authorization authority denial
change_proposal_suspended
execution_requested
execution_authorized
execution_action_started
execution_action_completed
post_execution_reindex_started
post_execution_reindex_completed
verification_passed
verification_failed
revision_triggered
signature_applied
```

---

## Failure Modes

| Condition | Response |
|-----------|----------|
| Proposal targets path outside sandbox | REJECT. Emit security violation event. |
| Proposal targets excluded path | REJECT. CRITICAL security violation. |
| FileCell not authorized | REJECT. Forward to external authorization authority with explanation. |
| Authorization TTL expires before execution | REJECT. Require resubmission. |
| execution actor reports failure | Request human or external revision review plan. Emit `verification_failed`. |
| Verification diff mismatch | Flag to operator. Halt further proposals from same seed. |
| execution actor mutates beyond proposal scope | CRITICAL violation. Halt execution actor. Require operator review. |

---

## Governance
- No proposal may be self-authorized by SRT-1 or the AI assistant
- external authorization authority is the sole authorization authority
- execution actor may not execute without an active Execution Lease linked to an authorized proposal
- All proposals are immutable after authorization — amendment requires a new proposal

---

## NEEDS_SOURCE
- [ ] ChangeProposal storage format (JSON file? DB record? In-memory queue?)
- [ ] Whether AI Assistant proposals are pre-validated by SRT-1 before external authorization authority sees them
- [ ] Revision mechanism — does execution actor restore from hash, git revert, or snapshot?
- [ ] Whether `scope: CROSS_MODULE` requires proposals to be split per module
- [ ] Maximum number of concurrent PENDING_AUTHORIZATION proposals
- [ ] Whether proposals expire if not executed within `authorization_ttl`
