# Post-Execution Verification Contract
**Contract ID:** `SRT1-CONTRACT-VERIFY-001`
**Between:** execution actor ↔ SRT-1 Engine
**Version:** 1.0.0
**Status:** CANONICAL

---

## Doctrine
execution actor acts. SRT-1 verifies. These roles do not overlap.
SRT-1 is not a rubber stamp — it compares what was declared to what was done.
A mismatch is a failure. Failure stops the chain. Nothing is signed until verification passes.

---

## Purpose
After execution actor reports execution complete, SRT-1 re-indexes the affected files and
compares the actual post-execution state against the ChangeProposal's declared intent.
This is the system's truth-telling moment.

---

## Parties

| Party | Role |
|-------|------|
| **execution actor** | Reports execution complete. Provides actual operations log. |
| **SRT-1 Engine** | Re-indexes affected files. Compares actual vs declared. Issues verdict. |
| **external authorization authority** | Receives verdict. Takes action if verification fails. |
| **Seed Signature** | Receives verification pass signal. Signs lineage proof. |

---

## Verification Schema

```yaml
verification_id: string             # Format: VRF-{proposal_id}-{timestamp}
proposal_id: string                 # The ChangeProposal being verified
execution_lease_id: string          # The Execution Lease that authorized execution
sandbox_id: string                  # Sandbox where execution occurred
verified_by: string                 # Always SRT-1 Engine instance ID

# Timing
verification_triggered_at: datetime # When execution actor reported complete
reindex_started_at: datetime
reindex_completed_at: datetime
verdict_issued_at: datetime

# Declared vs Actual
declared_files: list[DeclaredFile]  # From ChangeProposal.target_files
actual_files: list[ActualFile]      # From SRT-1 post-execution re-index

# Verdict
verdict: enum                       # PASSED | FAILED | PARTIAL | SCOPE_EXCEEDED
verdict_reason: string
drift_detected: boolean
drift_description: string | null

# Coherence scoring
coherence_score: float              # 0.0 to 1.0. 1.0 = perfect match.
coherence_threshold: float          # Minimum score to pass. Default: 0.95.
  # CRITICAL proposals may require: 1.0

# Signature
external_signature_requested: boolean
signature_id: string | null
```

---

## DeclaredFile Schema (from ChangeProposal)

```yaml
file_path: path
operation: enum                 # CREATE | MODIFY | DELETE | RENAME | MOVE
proposed_content_hash: string   # SHA256 of what execution actor was supposed to write
diff_summary: string
line_count_delta: integer
```

---

## ActualFile Schema (from SRT-1 re-index)

```yaml
file_path: path
operation_detected: enum        # What SRT-1 observed actually happened
actual_content_hash: string     # SHA256 of what's actually in the file now
actual_line_count_delta: integer
file_exists: boolean
modification_timestamp: datetime
```

---

## Verification Process

```
1. execution actor emits execution_complete
   ↓
2. SRT-1 receives signal — triggers post_execution_reindex_started
   ↓
3. SRT-1 re-indexes every file in ChangeProposal.target_files
   ↓
4. For each file: compare DeclaredFile vs ActualFile
   ↓
5. Compute coherence_score
   ↓
6. Issue verdict
   ↓
7. Emit verification event
   ↓
8. If PASSED → mark for external Seed Signature → update ExecutionGraph
   If FAILED → emit failure event → notify external authorization authority → request human or external revision review if reversible
   If PARTIAL → notify external authorization authority → operator review required
   If SCOPE_EXCEEDED → CRITICAL → halt further execution from this seed
```

---

## Verdict Rules

### PASSED
- All `declared_files` match `actual_files` (hash comparison)
- No files mutated outside `target_files`
- `coherence_score >= coherence_threshold`
- No drift detected

### FAILED
- One or more declared files do not match actual state
- OR files were mutated outside declared scope
- OR `coherence_score < coherence_threshold`

### PARTIAL
- Some declared files match, some do not
- Requires human review — SRT-1 does not auto-decide remediation

### SCOPE_EXCEEDED
- Files were mutated that were NOT in `declared_files`
- This is a CRITICAL security violation — not just a verification failure
- Triggers execution actor lock and operator alert

---

## Coherence Score Calculation

```
coherence_score = matched_files / total_declared_files

where matched_files = files where:
  - file_exists == true (or operation was DELETE and file_exists == false)
  - actual_content_hash == proposed_content_hash (for CREATE and MODIFY)
  - operation_detected == declared operation
```

Additional deductions:
- `-0.1` per undeclared file mutation detected
- `-0.2` if any forbidden path was touched (even if content unchanged)
- Score floor: 0.0 (never negative)

---

## Failure Response Protocol

| Verdict | SRT-1 Action | external authorization authority Action | execution actor Action |
|---------|-------------|-------------------|-------------|
| PASSED | Queue signature. Update ExecutionGraph. | Record pass. | No action required. |
| FAILED | Emit failure event. Flag to operator. | Request human or external revision review if `reversible: true`. | Apply approved revision action on external authorization authority signal. |
| PARTIAL | Emit partial event. Flag for review. | Hold further proposals from this seed. | Await operator decision. |
| SCOPE_EXCEEDED | Emit critical event. Lock this seed. | Lock execution actor. Alert operator. | Halt. Report to external authorization authority. |

---

## Drift Detection

SRT-1 compares the post-execution codebase state against its pre-execution index
to detect unintended changes beyond the FileCell:

**Drift indicators:**
- Symbol map changes outside target files
- Import graph changes outside target files
- New files created outside target files
- Deleted files not in target files
- Modified timestamps on untouched files

If drift is detected: `drift_detected: true`, `drift_description` populated, verdict
automatically escalates to FAILED or SCOPE_EXCEEDED.

---

## Events Emitted

```
post_execution_reindex_started
post_execution_reindex_completed
verification_passed
verification_failed
verification_partial
verification_scope_exceeded     # Critical
drift_detected
external_signature_requested
```

---

## NEEDS_SOURCE
- [ ] How SRT-1 compares content hashes — does it read files directly or use a hash store?
- [ ] Whether `coherence_threshold` is global config or per-sandbox or per-proposal
- [ ] How revision is triggered — SRT-1 signals execution actor? Or external authorization authority directly?
- [ ] Whether SCOPE_EXCEEDED triggers a system-wide execution actor lock or sandbox-scoped lock
- [ ] How ExecutionGraph is updated — does SRT-1 write directly or emit to a broker?
- [ ] Whether verification runs synchronously or asynchronously after execution actor reports complete
