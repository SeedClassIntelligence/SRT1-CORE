# Post-Execution Verification Skill

> **Skill ID:** `SRT1-SKILL-007`
> **Module:** NEEDS_SOURCE — Not yet implemented
> **Classification:** VERIFYING
> **Mutates Source:** ❌ Never

---

## Purpose

Compares the intended changes (from `ChangeProposal`) against the actual file mutations after execution actor completes execution. This is the verification half of the doctrine: "SRT-1 sees → external authorization authority permits → execution actor acts → **SRT-1 verifies**."

---

## Current State

**Not yet implemented.** The building blocks exist:

| Component | Exists? | Location |
|-----------|---------|----------|
| File hash snapshotting | ✅ Partial | `execution_bridge.py` — `_snapshot_files()` |
| File watcher re-indexing | ✅ | `engine.py` — 15s poll loop |
| Completion detection | ✅ | `execution_bridge.py` — signal file / quiet period |
| Scope validation (proposal vs actual) | ❌ | NEEDS_IMPLEMENTATION |
| Structural re-validation | ❌ | NEEDS_IMPLEMENTATION |
| Verification events | ❌ | NEEDS_IMPLEMENTATION |

---

## Target Design

### Activation

| Trigger | Source |
|---------|--------|
| Seed completion detected | `ExecutionBridge._check_completion()` → calls `verifier.verify()` |

### Inputs

| Input | Type |
|-------|------|
| `ChangeProposal` | Typed proposal with `files_write`, `files_must_not_change`, `max_lines_changed` |
| Pre-execution file hashes | `Dict[str, str]` from `_snapshot_files()` |
| Post-execution file hashes | `Dict[str, str]` computed after completion |

### Outputs

| Output | Type |
|--------|------|
| Verification verdict | `VERIFIED`, `PARTIAL_PASS`, or `FAILED` |
| Scope violations | List of unauthorized modifications |
| Collateral damage | List of protected files that changed |

### Events

| Event | Severity | Status |
|-------|----------|--------|
| `post_execution_snapshot_taken` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `verification_passed` | CRITICAL | ❌ NEEDS_IMPLEMENTATION |
| `verification_failed` | CRITICAL | ❌ NEEDS_IMPLEMENTATION |
| `verification_scope_violation` | CRITICAL | ❌ NEEDS_IMPLEMENTATION |
| `verification_returned_for_revision` | CRITICAL | ❌ NEEDS_IMPLEMENTATION |

### Implementation Path

1. Create `srt1_platform/verification.py` with `PostExecutionVerifier` class
2. Wire into `ExecutionBridge` completion lifecycle
3. Emit verification events to `public event log`

## Source of Truth

- [execution_bridge.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/execution_bridge.py) — `_snapshot_files()`
- Governed by: [post_execution_verification_contract.md](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1-contracts/post_execution_verification_contract.md)
