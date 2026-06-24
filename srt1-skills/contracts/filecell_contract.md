# FileCell Contract
**Contract ID:** `SRT1-CONTRACT-FILECELL-001`
**Between:** external authorization authority ↔ execution actor
**Version:** 1.0.0
**Status:** CANONICAL

---

## Doctrine
external authorization authority permits. execution actor acts within exactly the boundary external authorization authority defines.
A FileCell is the minimum executable surface — the exact set of files execution actor may
touch for a single authorized task. Nothing outside the FileCell may be read or
written by execution actor during execution.

---

## Purpose
Define the precise read and write permissions granted to execution actor for a single
execution. FileCells are derived from ChangeProposals by SRT-1 and authorized
by external authorization authority. They do not persist beyond the Execution Lease TTL.

**One FileCell per Execution Lease. One Execution Lease per ChangeProposal.**

---

## Parties

| Party | Role |
|-------|------|
| **external authorization authority** | Derives and authorizes the FileCell from the ChangeProposal |
| **execution actor** | Executes within the FileCell boundary. No access outside. |
| **SRT-1** | Derives the FileCell manifest from repo index. Does not authorize. |

---

## FileCell Schema

```yaml
filecell_id: string             # Format: FC-{proposal_id}-{timestamp}
proposal_id: string             # Parent ChangeProposal this cell was derived from
execution_lease_id: string      # Parent Execution Lease
sandbox_id: string              # Sandbox this FileCell operates within
derived_by: string              # SRT-1 Engine instance that derived the manifest
authorized_by: string           # external authorization token
created_at: datetime
expires_at: datetime            # Must match Execution Lease expiry

# Read permissions
readable_paths: list[path]      # Absolute paths execution actor may read during execution
readable_extensions: list[str]  # File types execution actor may read (e.g., [".py", ".js", ".md"])
readable_depth: integer         # Max directory depth for reads (default: 3)

# Write permissions
writable_paths: list[path]      # Absolute paths execution actor may write or mutate
writable_operations: list[enum] # Subset of [CREATE, MODIFY, DELETE, RENAME, MOVE]

# Absolute boundaries
forbidden_paths: list[path]     # Paths that can NEVER be accessed regardless of above
forbidden_extensions: list[str] # File types that can NEVER be accessed (e.g., [".env", ".key"])
forbidden_operations: list[enum]# Operations never permitted (e.g., [DELETE] on protected files)

# Validation
content_hash_required: boolean  # Whether execution actor must verify file hash before writing (default: true)
max_files_writable: integer     # Hard cap on how many files can be written (default: 10)
max_lines_per_file: integer     # Hard cap on lines written per file (default: 500)

# State
status: enum                    # ACTIVE | CONSUMED | EXPIRED | VIOLATED | REVOKED
violation_count: integer        # Number of boundary violations detected
```

---

## Derivation Process (SRT-1's Role)

SRT-1 derives the FileCell manifest from the approved ChangeProposal:

```
ChangeProposal.target_files
  → Cross-reference with Repo Sandbox Contract (excluded_paths)
  → Cross-reference with module boundary map (Module Boundary Skill)
  → Derive minimum readable_paths required for the write operations
  → Derive writable_paths from target_files only
  → Set forbidden_paths = sandbox.excluded_paths + any paths not in target_files
  → Output FileCell manifest
  → Forward to external authorization authority for authorization
```

SRT-1 derives. external authorization authority authorizes. execution actor executes. This sequence is non-negotiable.

---

## Boundary Rules

### execution actor SHALL:
- Check FileCell status is ACTIVE before any operation
- Verify file content hash before modifying (if `content_hash_required: true`)
- Stay within `writable_paths` absolutely
- Stay within `readable_paths` for any reads during execution
- Report each file operation to SRT-1 in real time
- Report FileCell consumed when execution is complete
- Halt and report `filecell_violated` if any boundary check fails

### execution actor SHALL NOT:
- Read from paths not in `readable_paths`
- Write to paths not in `writable_paths`
- Perform operations not in `writable_operations`
- Touch `forbidden_paths` under any circumstance
- Access `forbidden_extensions` under any circumstance
- Exceed `max_files_writable` or `max_lines_per_file`
- Carry FileCell state from one Execution Lease to another

### external authorization authority SHALL:
- Authorize FileCells only from validated ChangeProposals
- Set `expires_at` to match Execution Lease TTL
- Revoke FileCell immediately if Execution Lease is revoked
- Log all FileCell authorizations in the event log

---

## Violation Handling

| Violation | Response |
|-----------|----------|
| execution actor reads outside `readable_paths` | HALT. Set status → VIOLATED. Emit `filecell_violated`. |
| execution actor writes outside `writable_paths` | HALT. Set status → VIOLATED. Return/revision. Operator alert. |
| execution actor touches `forbidden_paths` | CRITICAL. HALT. Lock execution actor. Require operator review. |
| FileCell expired before execution complete | HALT. execution actor may not continue. Return/revision. |
| `max_files_writable` exceeded | HALT. Partial execution logged. Require new proposal. |

---

## FileCell Derivation Rules

1. `readable_paths` must include all paths needed to understand context for the write
2. `writable_paths` must be the minimal surface — exactly what the ChangeProposal specifies
3. `forbidden_paths` must include ALL paths in sandbox `excluded_paths`
4. Parent directories of `writable_paths` are NOT automatically readable unless explicitly added
5. `forbidden_extensions` always includes: `.env`, `.key`, `.pem`, `.secret`, `.credentials`
6. No FileCell may grant DELETE permission without `risk_level: HIGH` or above in parent proposal

---

## Relationship to Other Contracts

```
Seed Intake Contract
  → triggers ChangeProposal Contract
    → validated by SRT-1
      → FileCell derived (SRT-1)
        → FileCell authorized (external authorization authority)
          → Execution Lease granted (external authorization authority)
            → execution actor executes within FileCell
              → FileCell consumed
                → Verification Contract triggered (SRT-1)
                  → Audit Contract records
                    → Signature Contract signs
```

---

## Events Emitted

```
filecell_manifest_derived
filecell_authorized
filecell_activated
filecell_consumed
filecell_expired
filecell_revoked
filecell_violated           # Security critical
```

---

## NEEDS_SOURCE
- [ ] Whether FileCells are stored in memory or persisted to disk
- [ ] Whether execution actor receives the FileCell directly or through a broker
- [ ] How `content_hash_required` verification is implemented in execution actor
- [ ] Whether `forbidden_extensions` list is global config or per-sandbox
- [ ] Revision mechanism when execution actor halts mid-execution
- [ ] Whether partial FileCell consumption is logged separately from full consumption
