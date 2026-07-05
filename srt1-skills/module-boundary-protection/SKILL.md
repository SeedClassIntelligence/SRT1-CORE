# Module Boundary Protection Skill

> **Skill ID:** `SRT1-SKILL-005`
> **Module:** FileCellGuard + ManifestDeriver
> **Authority:** Context Isolation
> **Classification:** Public Core / Pro Candidate
> **Mutates Source:** Never

## Purpose

Module Boundary Protection prevents context bleed and unauthorized file access
inside SRT-1. It ensures reads, writes, context expansion, and WorkCell package
assembly stay inside the allowed FileCell/WorkCell boundary.

FileCells carry persistent repository intelligence. WorkCells define bounded
execution environments. This skill enforces the boundary between what an
assistant may know, inspect, or change and what remains outside scope.

## Activation

| Trigger | Source | Frequency |
|---|---|---|
| WorkCell creation | Manifest derivation / Repository Understanding | Once per WorkCell package |
| Read validation | `FileCellGuard.validate_read(path, manifest)` | Before governed reads |
| Write validation | `FileCellGuard.validate_write(path, manifest)` | Before governed writes |
| Context expansion | Reinjection / WorkCell package generation | Before attaching more files |
| Semantic escalation check | Role/domain detection | During derivation or expansion |

## Preconditions

- A FileCell or WorkCell boundary has been derived.
- Incoming paths are canonicalized before validation.
- Allowed reads, allowed writes, and forbidden paths are known.
- Protected architectural roles have explicit sponsorship when required.

## Inputs

| Input | Type | Source |
|---|---|---|
| Target path | String | Requested read/write/context expansion |
| FileCell/WorkCell manifest | Dataclass/dict | Manifest Deriver / WorkCell runtime |
| `symbol_table` | Dict | Repo Understanding |
| Dependency map | Dict | Repo Understanding |
| Domain tags | List | Change proposal / WorkCell scope |
| Forbidden path rules | List | Context Isolation policy |

## Outputs

| Output | Type | Meaning |
|---|---|---|
| Validation result | Boolean or exception | Allowed or blocked |
| Boundary violation | Exception/event metadata | Access rejected |
| Derived manifest | Dataclass/dict | Allowed reads/writes and reasoning |
| Escalation warning | Dict/event metadata | Protected role requires sponsorship |

## Runtime Responsibilities

1. Canonicalize paths before evaluation.
2. Block access outside allowed reads/writes.
3. Block forbidden paths regardless of requested scope.
4. Prevent symlink/path traversal escapes.
5. Require explicit sponsorship for protected domains such as authentication,
   security, cryptographic, or signing-adjacent code.
6. Keep assistant context bounded to approved FileCells/WorkCells.
7. Emit or expose violations as evidence for Verification and Trust Awareness.

## Boundary Rules

| Rule | Enforcement |
|---|---|
| Read-only enforcer | This skill validates; it does not mutate source files |
| Path canonicalization | Resolve real paths before validation |
| Non-overridable forbidden patterns | `.env`, `.git`, keys, secrets, runtime caches |
| Assistant instruction protection | `AGENTS.md` is excluded unless explicitly authorized with reason |
| No execution actor bypass | Execution actor is constrained by this skill, not allowed to call/disable it |
| Semantic escalation | Protected architectural roles require matching approval/sponsorship |
| No cross-project bleed | WorkCell expansion cannot cross repository boundary without explicit approval |

## Verification

| Check | Success condition |
|---|---|
| Boundary holds | Out-of-scope write raises a boundary violation |
| Forbidden paths blocked | `.env`, `.git`, key/secret paths never enter allowed lists |
| Symlinks resolved | Real path validation prevents escapes |
| Protected roles enforced | Sensitive role access requires explicit sponsorship |
| Violations visible | Blocked attempts produce evidence for status/audit/verification |

Failure indicators include forbidden paths in allowed lists, uncanonicalized
paths, unauthorized `AGENTS.md` access, silent violation handling, or WorkCell
scope expansion without evidence.

## Events

| Event | Severity | Status |
|---|---|---|
| `filecell_boundary_violation` | critical | exists/planned depending on runtime path |
| `filecell_manifest_derived` | info | exists/planned depending on runtime path |
| `filecell_semantic_escalation_blocked` | critical | planned |
| `filecell_agents_md_included` | warning | planned |

## Source of Truth

- `srt1_platform/filecell.py`
- `srt1_platform/manifest_deriver.py`
- WorkCell package metadata
- FileCell/WorkCell boundary contracts
