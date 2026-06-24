# Execution Lease Contract
**Contract ID:** `SRT1-CONTRACT-EXECLEASE-001`
**Between:** external authorization authority ↔ execution actor
**Version:** 1.0.0
**Status:** CANONICAL

---

## Doctrine
external authorization authority permits. The Execution Lease is the permission token.
execution actor has no authority to act without an active, non-expired Execution Lease.
The Lease defines exactly what execution actor may do, for how long, and within what boundary.

---

## Purpose
Grant execution actor temporary, bounded execution authority for a single ChangeProposal.
The Lease is not a credential — it is a time-boxed task authorization that expires
regardless of whether execution completes. No Lease extension. No Lease transfer.

---

## Parties

| Party | Role |
|-------|------|
| **external authorization authority** | Issues the Lease. Only authority that can do so. |
| **execution actor** | Operates under the Lease. Authority is fully bounded by Lease terms. |
| **SRT-1** | Observes Lease status. Reports violations. Does not issue or revoke. |

---

## Execution Lease Schema

```yaml
lease_id: string                # Format: EL-{proposal_id}-{timestamp}
proposal_id: string             # The ChangeProposal this Lease authorizes
filecell_id: string             # The FileCell this Lease activates
sandbox_id: string              # Sandbox this Lease operates within
seed_id: string                 # Originating seed (traceability)

# Authority definition
granted_to: string              # execution actor instance identifier
granted_by: string              # external authorization token
granted_at: datetime
expires_at: datetime            # Hard expiry — execution actor halts regardless of state

# Scope
authorized_operations: list[enum]  # Exact operations execution actor may perform
authorized_file_count: integer     # Max files execution actor may touch
scope_override: boolean            # Whether this Lease overrides any prior scope (default: false)

# Time
ttl_seconds: integer            # Time-to-live from grant. external authorization authority sets this.
  # LOW risk:      60-120s
  # MEDIUM risk:   300s
  # HIGH risk:     600s
  # CRITICAL risk: 3600s (operator-set only)

# State
status: enum                    # PENDING | ACTIVE | CONSUMED | EXPIRED | REVOKED | VIOLATED
activated_at: datetime | null   # When execution actor began execution
consumed_at: datetime | null    # When execution actor reported completion
revocation_reason: string | null

# Audit
events: list[AuditEvent]        # All lifecycle events for this Lease
```

---

## Lease Lifecycle

```
PENDING → ACTIVE → CONSUMED (success)
        ↘ EXPIRED (TTL elapsed before execution actor completed)
ACTIVE  ↘ REVOKED (external authorization authority revokes mid-execution)
        ↘ VIOLATED (execution actor exceeded scope)
```

### State Transitions

| From | To | Trigger | Actor |
|------|----|---------|-------|
| PENDING | ACTIVE | execution actor begins execution | execution actor |
| ACTIVE | CONSUMED | execution actor reports completion | execution actor |
| ACTIVE | EXPIRED | TTL elapses | external authorization authority timer |
| ACTIVE | REVOKED | external authorization authority revokes | external authorization authority |
| ACTIVE | VIOLATED | Scope violation detected | SRT-1 / external authorization authority |
| EXPIRED | — | Terminal. No recovery. | — |
| VIOLATED | — | Terminal. Operator review required. | — |

---

## Lease Rules

### external authorization authority SHALL:
- Issue at most one active Lease per ChangeProposal
- Set `expires_at` based on ChangeProposal `risk_level`
- Revoke the Lease immediately if FileCell is violated
- Revoke the Lease immediately if the associated ChangeProposal is suspended
- Log all Lease issuances, activations, and terminations

### execution actor SHALL:
- Activate the Lease before beginning any file operation
- Check Lease status before each file operation (not just at start)
- Halt immediately if Lease transitions to EXPIRED, REVOKED, or VIOLATED
- Report Lease consumed upon successful completion of all authorized operations
- Never cache or reuse a Lease for a different ChangeProposal

### execution actor SHALL NOT:
- Begin execution without an ACTIVE Lease
- Continue execution after Lease expiry, even mid-file
- Transfer Lease authority to any other component
- Operate on files outside FileCell boundaries regardless of Lease status
- Issue its own Leases

### SRT-1 SHALL:
- Monitor Lease status throughout execution
- Trigger post-execution verification when Lease is CONSUMED
- Alert external authorization authority if Lease expires without CONSUMED status
- Emit `execution_lease_expired_without_completion` if TTL elapses mid-execution
- Never issue or revoke a Lease (observer only)

---

## Revocation Triggers

| Trigger | Initiated By | Effect |
|---------|-------------|--------|
| FileCell boundary violated | SRT-1 / external authorization authority | Immediate halt. execution actor stops mid-operation. |
| ChangeProposal suspended | external authorization authority / Operator | Lease revoked. Revision requested. |
| execution actor process crash | external authorization authority (timeout) | Lease expires. Revision requested. |
| Operator override | Operator | Lease revoked. State preserved for audit. |
| Constellation conflict detected | SRT-1 | Lease suspended pending resolution. |

---

## Events Emitted

```
execution_lease_granted
execution_lease_activated
execution_requested
execution_authorized
execution_lease_consumed
execution_lease_expired
execution_lease_revoked
execution_lease_violated
execution_lease_expired_without_completion
```

---

## Relationship to Other Contracts

```
ChangeProposal Contract → [authorized]
  → FileCell Contract → [derived + authorized]
    → Execution Lease Contract → [granted]
      → execution actor executes
        → Lease consumed
          → Verification Contract triggers
            → Audit Contract records
```

---

## NEEDS_SOURCE
- [ ] How external authorization authority timer is implemented (cron job? async task? event loop?)
- [ ] Whether execution actor receives Lease as a signed token or looks it up from external authorization authority API
- [ ] How mid-execution halt is implemented — does execution actor checkpoint state?
- [ ] Whether partial writes are rolled back atomically or file-by-file
- [ ] Maximum number of concurrent active Leases
- [ ] Whether Lease violations trigger execution actor lock globally or per-sandbox
