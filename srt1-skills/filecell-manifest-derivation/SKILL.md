# FileCell Manifest Derivation Skill

> **Skill ID:** `SRT1-SKILL-006`
> **Module:** LeastPrivilegeManifestDeriver
> **Authority:** Context Isolation / Repo Understanding
> **Classification:** Public Core / Pro Candidate
> **Mutates Source:** Never

## Purpose

FileCell Manifest Derivation computes the smallest safe FileCell/WorkCell scope
for a seed, task, or assistant action. It uses repository intelligence,
symbols, dependencies, declared target files, and boundary rules to determine
what may be read, what may be written, and what must remain forbidden.

This skill replaces broad workspace access with evidence-backed WorkCell scope.
It derives the execution boundary; it does not execute code and it does not
grant private signing or runtime authority.

## Activation

| Trigger | Source | Frequency |
|---|---|---|
| Seed planted | Continuity / seed queue | Once per scoped seed |
| WorkCell creation | Repository Understanding + Context Isolation | Once per WorkCell package |
| Scope expansion request | Dashboard/human approval or dependency evidence | On demand |
| Manifest derivation call | `LeastPrivilegeManifestDeriver.derive()` | On demand |
| Protected-domain check | Role/domain detection | During derivation |

## Preconditions

- Repository index, symbol table, and dependency map are current or explicitly
  marked degraded.
- Target files or likely files are declared by the seed, proposal, dependency
  analysis, or human approval.
- Unknown paths are rejected unless they are valid new-file creation targets.
- Forbidden path rules are loaded.
- WorkCell output/package location is configured if generated artifacts are
  required.

## Inputs

| Input | Type | Source |
|---|---|---|
| `queue_seed_id` / `seed_id` | String | Continuity |
| Task/objective | String | Seed / WorkCell |
| `files_likely` | List | Proposal, intent classifier, or human selection |
| Domain tags | List | Proposal / WorkCell scope |
| `symbol_table` | Dict | Repo Understanding |
| Dependency map / call graph | Dict | Repo Understanding |
| Forbidden path rules | List | Context Isolation policy |

## Outputs

| Output | Type | Meaning |
|---|---|---|
| FileCell/WorkCell manifest | Dataclass/dict | Allowed reads, writes, forbidden paths, dependencies |
| Dependency reasoning | List/dict | Why each attached file is included |
| Scope status | String | fresh, degraded, blocked, or needs approval |
| WorkCell package path | Path/string | Where generated WorkCell instructions/state may live |

## Derivation Algorithm

1. Resolve declared targets against the repository index.
2. Reject unknown files unless they are approved new-file targets.
3. Walk dependency evidence with a bounded depth cap.
4. Add required dependency FileCells only when evidence supports inclusion.
5. Check protected architectural roles such as auth, security, cryptographic, or
   signing-adjacent code.
6. Require explicit sponsorship/approval for protected-domain expansion.
7. Compute allowed reads, allowed writes, and forbidden paths.
8. Remove forbidden paths from all allowed sets.
9. Emit a manifest with reasoning and freshness/degradation metadata.

## Boundary Rules

| Rule | Enforcement |
|---|---|
| Source read-only | Derivation reads repository intelligence; it does not mutate source |
| Evidence-backed scope | Files must be indexed, approved, or valid new targets |
| Depth cap | Dependency walk is bounded to avoid scope explosion |
| Forbidden paths | Secrets, `.git`, runtime state, keys, and private paths are never allowed |
| Protected role escalation | Sensitive domains require explicit sponsorship/approval |
| No self-expansion | Execution actors cannot expand their own manifest |
| Public Core boundary | No SION/private signing/private ledger dependency required |

## Verification

| Check | Success condition |
|---|---|
| Manifest created | Manifest has a stable cell/workcell id and reasoning |
| Dependencies resolved | Included dependencies have evidence and bounded depth |
| Forbidden excluded | No forbidden path appears in allowed reads/writes |
| Protected domains enforced | Sensitive targets require sponsorship/approval |
| Degraded state visible | Stale or incomplete repo intelligence is labeled |

Failure indicators include unknown target acceptance, empty allowed reads without
reason, forbidden path inclusion, unexplained dependency expansion, or hidden
degraded repository intelligence.

## Events

| Event | Severity | Status |
|---|---|---|
| `filecell_manifest_derived` | info | exists/planned depending on runtime path |
| `filecell_scope_degraded` | warning | planned |
| `filecell_semantic_escalation_blocked` | critical | planned |
| `workcell_scope_expansion_requested` | warning | planned |

## Source of Truth

- `srt1_platform/manifest_deriver.py`
- `srt1_platform/filecell.py`
- repository manifest and symbol/dependency maps
- WorkCell package metadata
