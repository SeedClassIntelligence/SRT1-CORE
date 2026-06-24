# SRT-1 Operating Map
**Version:** 1.0.0
**Patent ref:** USPTO #63/827,977
**Status:** CANONICAL

---

## Core Doctrine

```
SRT-1 illuminates.
external authorization authority permits.
execution actor acts.
SRT-1 verifies.
ExecutionGraph records.
Seed Signature signs.
Constellation observes.
```

SRT-1 is the **continuity and repo-intelligence child of SCIA**.
- It does NOT execute
- It does NOT mutate source
- It does NOT govern like external authorization authority
- It **sees, remembers, indexes, reflects, detects drift, preserves boundaries**,
  and feeds structured understanding to coding agents and execution actor

---

## Component Map

### Skills (SRT-1 Capabilities)
| Skill | ID | Purpose |
|-------|----|---------|
| Repo Indexing | SRT1-SKILL-REPO-INDEX | Reads repo and builds symbol/context map |
| AST Analysis | SRT1-SKILL-AST | Extracts classes, functions, imports, dependencies |
| Context Injection | SRT1-SKILL-CTX-INJECT | Updates AGENTS.md, CLAUDE.md, Cursor rules, Copilot instructions |
| Module Boundary Protection | SRT1-SKILL-MODULE-BOUNDARY | Prevents file/folder knowledge bleed |
| FileCell Manifest Derivation | SRT1-SKILL-FILECELL-DERIVE | Defines allowed reads/writes for execution |
| Drift Detection | SRT1-SKILL-DRIFT | Detects when AI/code deviates from intent |
| Post-Execution Verification | SRT1-SKILL-VERIFY | Compares intended change vs actual result |
| Constellation Mapping | SRT1-SKILL-CONSTELLATION | Maps multiple isolated repo/module sandboxes |
| Audit Event Emission | SRT1-SKILL-AUDIT | Emits traceable events for lifecycle visibility |

### Contracts
| Contract | ID | Between |
|----------|----|---------|
| Repo Sandbox | SRT1-CONTRACT-SANDBOX-001 | Repo Folder ↔ SRT-1 Engine |
| ChangeProposal | SRT1-CONTRACT-CHANGEPROP-001 | SRT-1/AI ↔ external authorization authority/execution actor |
| FileCell | SRT1-CONTRACT-FILECELL-001 | external authorization authority ↔ execution actor |
| Execution Lease | SRT1-CONTRACT-EXECLEASE-001 | external authorization authority ↔ execution actor |
| Post-Execution Verification | SRT1-CONTRACT-VERIFY-001 | execution actor ↔ SRT-1 Engine |
| Context Injection | SRT1-CONTRACT-CTXINJECT-001 | SRT-1 ↔ AI Assistant Files |
| Audit Event | SRT1-CONTRACT-AUDIT-001 | Runtime System ↔ Event Metadata |

---

## Full Execution Flow

```
1. SEED INTAKE
   operator / execution actor → SRT-1 (seed_dispatched)
   SRT-1: Trigger repo index → Build context bundle → Inject into AGENTS.md/CLAUDE.md

2. CHANGE PROPOSAL
   AI Assistant / SRT-1 → ChangeProposal created
   SRT-1: Validate proposal → Derive FileCell manifest → Forward to external authorization authority

3. AUTHORIZATION
   external authorization authority: Authorizes proposal → Authorizes FileCell → Issues Execution Lease

4. EXECUTION
   execution actor: Activates Lease → Executes within FileCell boundaries → Reports complete

5. VERIFICATION
   SRT-1: Re-indexes affected files → Compares hashes → Issues verdict
   PASSED → Mark for external signature → Update ExecutionGraph
   FAILED → Signal external authorization authority → Request human or external revision review

6. SIGNATURE
   Seed Signature: Signs lineage proof → Chain complete
```

---

## Event Lineage Chain (Signature-Eligible Sequence)

For a seed to be signature-eligible, this sequence must be present in the event log:

```
seed_dispatched
→ change_proposal_created → change_proposal_validated → change_proposal_authorized
→ filecell_manifest_derived → filecell_authorized
→ execution_lease_granted → execution_authorized
→ execution_action_started → execution_action_completed
→ post_execution_reindex_completed → verification_passed
→ external_signature_requested → signature_applied
```

Any break = no signature issued.

---

## Boundary Rules (Absolute)

1. SRT-1 never writes to source files
2. SRT-1 never executes code in the repo
3. SRT-1 never self-authorizes ChangeProposals
4. SRT-1 never issues Execution Leases
5. SRT-1 never triggers execution actor directly
6. SRT-1 always respects excluded_paths
7. SRT-1 always emits events — no silent operations
8. FileCell permissions are derived by SRT-1 but authorized by external authorization authority only
9. Constellation visibility does not expand FileCell permissions

---

## NEEDS_SOURCE Registry

All open NEEDS_SOURCE items across contracts and skills:

### Architecture
- [ ] external authorization authority implementation (service? library? in-process?)
- [ ] execution actor implementation (subprocess? API? in-process?)
- [ ] Event Metadata storage backend
- [ ] ExecutionGraph — separate service or embedded?
- [ ] How operator alerts are delivered
- [ ] Whether events are synchronous or async

### Storage
- [ ] Whether SRT-1 index is stored in memory or on disk between runs
- [ ] Whether FileCell manifests are stored or passed directly
- [ ] Whether srt1-context/ is gitignored or committed
- [ ] Event retention policy

### Execution
- [ ] How mid-execution execution actor halt is implemented
- [ ] Whether partial writes are rolled back atomically or file-by-file
- [ ] How revision is triggered — SRT-1 signals execution actor? Or external authorization authority directly?
- [ ] Maximum concurrent active Leases
- [ ] Whether SCOPE_EXCEEDED triggers global or sandbox-scoped execution actor lock

### Detection
- [ ] How drift detection frequency is configured
- [ ] Whether drift from intentional refactoring is distinguishable from unintended
- [ ] How module boundaries are defined (package.json? directory convention? config?)

---

## File Structure

```
srt1/
  SRT1_OPERATING_MAP.md           ← This file
  contracts/
    repo_sandbox_contract.md
    change_proposal_contract.md
    filecell_contract.md
    execution_lease_contract.md
    post_execution_verification_contract.md
    context_injection_contract.md
    audit_event_contract.md
  srt1-skills/
    repo-indexing/
      SKILL.md
      activation.md
      verification.md
      events.md
    ast-analysis/
    context-injection/
    drift-detection/
    module-boundary-protection/
    filecell-manifest-derivation/
    post-execution-verification/
    constellation-mapping/
    audit-event-emission/
  events/
    event_taxonomy.md
```
