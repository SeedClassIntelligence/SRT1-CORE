# Audit Event Contract
**Contract ID:** `SRT1-CONTRACT-AUDIT-001`
**Between:** Runtime System ↔ Event Metadata
**Version:** 1.0.0
**Status:** CANONICAL

---

## Doctrine
ExecutionGraph records. Every significant system action emits a traceable event.
No event = no tuning. No event = no proof. No event = no signature.
This contract defines the canonical event schema and the full event taxonomy.

---

## Purpose
Define what events the system must emit, their required fields, and the routing
rules that determine which events go to the event log, which trigger downstream actions,
and which are required for Seed Signature eligibility.

---

## Parties

| Party | Role |
|-------|------|
| **All SRT-1 components** | Emit events according to this contract |
| **Event Metadata** | Receives, stores, and indexes all events |
| **ExecutionGraph** | Subscribes to execution-phase events for lineage recording |
| **Seed Signature** | Subscribes to signature-eligible events for signing |
| **external authorization authority** | Subscribes to authorization and violation events |

---

## Canonical Event Schema

Every event MUST conform to this schema:

```yaml
event_id: string            # Format: EVT-{type}-{timestamp}-{hash6}
event_type: string          # From the Event Taxonomy below
emitted_by: string          # Component that emitted the event
emitted_at: datetime        # ISO 8601 with milliseconds
severity: enum              # INFO | WARN | ERROR | CRITICAL

# Context (all optional but fill as many as applicable)
sandbox_id: string | null
seed_id: string | null
proposal_id: string | null
filecell_id: string | null
lease_id: string | null
verification_id: string | null
injection_id: string | null
constellation_id: string | null

# Payload
payload: object             # Event-specific data. See per-event payload specs below.

# Routing
event_log_required: boolean    # Must reach event log. Failure = system alert.
execution_graph: boolean    # Whether ExecutionGraph should record this event
signature_eligible: boolean # Whether this event is part of signature lineage chain
triggers_action: list[string]  # Downstream actions this event triggers (if any)
```

---

## Event Taxonomy

### 1. Sandbox Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `repo_sandbox_registered` | INFO | ✅ | ❌ | ❌ |
| `repo_sandbox_deregistered` | INFO | ✅ | ❌ | ❌ |
| `repo_index_started` | INFO | ✅ | ✅ | ❌ |
| `repo_index_completed` | INFO | ✅ | ✅ | ❌ |
| `sandbox_state_changed` | INFO | ✅ | ❌ | ❌ |
| `sandbox_error` | ERROR | ✅ | ❌ | ❌ |

### 2. Context Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `context_bundle_generated` | INFO | ✅ | ✅ | ❌ |
| `context_injection_started` | INFO | ✅ | ✅ | ❌ |
| `context_injection_completed` | INFO | ✅ | ✅ | ❌ |
| `context_injection_failed` | ERROR | ✅ | ✅ | ❌ |
| `context_drift_warning_injected` | WARN | ✅ | ✅ | ❌ |
| `context_cleared` | INFO | ✅ | ❌ | ❌ |

### 3. Seed Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `seed_dispatched` | INFO | ✅ | ✅ | ✅ |
| `seed_scoped` | INFO | ✅ | ✅ | ✅ |
| `seed_halted` | WARN | ✅ | ✅ | ❌ |
| `seed_locked` | ERROR | ✅ | ✅ | ❌ |

### 4. ChangeProposal Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `change_proposal_created` | INFO | ✅ | ✅ | ✅ |
| `change_proposal_validated` | INFO | ✅ | ✅ | ✅ |
| `change_proposal_rejected` | WARN | ✅ | ✅ | ❌ |
| `change_proposal_submitted` | INFO | ✅ | ✅ | ✅ |
| `change_proposal_authorized` | INFO | ✅ | ✅ | ✅ |
| `change_proposal_suspended` | WARN | ✅ | ✅ | ❌ |

### 5. FileCell Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `filecell_manifest_derived` | INFO | ✅ | ✅ | ✅ |
| `filecell_authorized` | INFO | ✅ | ✅ | ✅ |
| `filecell_activated` | INFO | ✅ | ✅ | ✅ |
| `filecell_consumed` | INFO | ✅ | ✅ | ✅ |
| `filecell_expired` | WARN | ✅ | ✅ | ❌ |
| `filecell_revoked` | WARN | ✅ | ✅ | ❌ |
| `filecell_violated` | CRITICAL | ✅ | ✅ | ❌ |

### 6. Execution Lease Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `execution_lease_granted` | INFO | ✅ | ✅ | ✅ |
| `execution_lease_activated` | INFO | ✅ | ✅ | ✅ |
| `execution_requested` | INFO | ✅ | ✅ | ✅ |
| `execution_authorized` | INFO | ✅ | ✅ | ✅ |
| `execution_lease_consumed` | INFO | ✅ | ✅ | ✅ |
| `execution_lease_expired` | WARN | ✅ | ✅ | ❌ |
| `execution_lease_revoked` | WARN | ✅ | ✅ | ❌ |
| `execution_lease_violated` | CRITICAL | ✅ | ✅ | ❌ |
| `execution_lease_expired_without_completion` | ERROR | ✅ | ✅ | ❌ |

### 7. execution actor Mutation Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `execution_action_started` | INFO | ✅ | ✅ | ✅ |
| `execution_action_completed` | INFO | ✅ | ✅ | ✅ |
| `execution_action_failed` | ERROR | ✅ | ✅ | ❌ |
| `execution_action_returned_for_revision` | WARN | ✅ | ✅ | ❌ |
| `execution_scope_exceeded` | CRITICAL | ✅ | ✅ | ❌ |

### 8. Verification Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `post_execution_reindex_started` | INFO | ✅ | ✅ | ✅ |
| `post_execution_reindex_completed` | INFO | ✅ | ✅ | ✅ |
| `verification_passed` | INFO | ✅ | ✅ | ✅ |
| `verification_failed` | ERROR | ✅ | ✅ | ❌ |
| `verification_partial` | WARN | ✅ | ✅ | ❌ |
| `verification_scope_exceeded` | CRITICAL | ✅ | ✅ | ❌ |
| `drift_detected` | WARN | ✅ | ✅ | ❌ |

### 9. Signature Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `external_signature_requested` | INFO | ✅ | ✅ | ✅ |
| `signature_applied` | INFO | ✅ | ✅ | ✅ |
| `signature_failed` | ERROR | ✅ | ✅ | ❌ |

### 10. Constellation Events
| Event | Severity | Event Log | ExecGraph | Sig-Eligible |
|-------|----------|--------|-----------|-------------|
| `constellation_member_added` | INFO | ✅ | ❌ | ❌ |
| `constellation_member_removed` | INFO | ✅ | ❌ | ❌ |
| `constellation_boundary_enforced` | INFO | ✅ | ✅ | ❌ |
| `constellation_bleed_detected` | CRITICAL | ✅ | ✅ | ❌ |

---

## Signature Lineage Chain

For a seed's work to be eligible for Seed Signature, this exact event sequence
must be present and traceable in the event log for the same `seed_id`:

```
seed_dispatched
→ change_proposal_created
→ change_proposal_validated
→ change_proposal_authorized
→ filecell_manifest_derived
→ filecell_authorized
→ execution_lease_granted
→ execution_authorized
→ execution_action_started
→ execution_action_completed
→ post_execution_reindex_completed
→ verification_passed
→ external_signature_requested
→ signature_applied
```

**Any break in this chain = signature not issued.**
Missing events are as significant as failed events.

---

## Routing Rules

- `severity: CRITICAL` → Immediate operator alert + event log write + downstream halt
- `severity: ERROR` → Event Log write + downstream notification
- `severity: WARN` → Event Log write + log
- `severity: INFO` → Event Log write
- `event_log_required: true` → Failed event log write must retry 3x before system alert
- `execution_graph: true` → ExecutionGraph receives async copy

---

## Events Emitted By This Contract
This contract does not emit events — it defines them. All events are emitted by the
component indicated in `emitted_by`.

---

## NEEDS_SOURCE
- [ ] Event Metadata storage backend (append-only file? time-series DB? blockchain?)
- [ ] Whether events are synchronous (blocking) or async (fire-and-forget)
- [ ] Whether ExecutionGraph is a separate service or embedded in SRT-1
- [ ] How operator alerts are delivered (email? Slack? webhook?)
- [ ] Event retention policy (how long are events kept?)
- [ ] Whether events are encrypted at rest
- [ ] How event replay works for debugging failed lineage chains
