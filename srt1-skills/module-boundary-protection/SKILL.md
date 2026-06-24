# Module Boundary Protection Skill

> **Skill ID:** `SRT1-SKILL-005`
> **Module:** FileCellGuard + ManifestDeriver
> **Classification:** VERIFYING
> **Mutates Source:** ❌ Never

---

## Purpose

Prevents file/folder knowledge bleed across module and sandbox boundaries. Ensures that every read and write operation is scoped to the authorized FileCell. Blocks symlink escapes, forbidden pattern access, and semantic escalation.

---

## Activation

| Trigger | Source |
|---------|--------|
| Write validation | `FileCellGuard.validate_write(path, manifest)` |
| Read validation | `FileCellGuard.validate_read(path, manifest)` |
| Manifest derivation | `LeastPrivilegeManifestDeriver.derive()` |
| Semantic escalation check | During derivation — `AUTH_SECURITY` / `CRYPTOGRAPHIC` role detection |

## Inputs

| Input | Type |
|-------|------|
| Target path | `str` (absolute or relative) |
| `FileCellManifest` | Dataclass with `allowed_reads`, `allowed_writes`, `forbidden_paths` |
| `symbol_table` | For dependency walking during derivation |
| `domains` | List of authorized domain tags |

## Outputs

| Output | Type |
|--------|------|
| Validation result | `True` or `FileCellBoundaryViolation` exception |
| `FileCellManifest` | From derivation — includes reasoning log |

## Governance

- Stateless: no persistent state, no memory between calls
- Path canonicalization with `os.path.realpath()` — blocks symlink escapes
- `ALWAYS_FORBIDDEN_PATTERNS` are hardcoded and non-overridable
- `AGENTS.md` excluded from reads by default
- Semantic Escalation: files with `AUTH_SECURITY` or `CRYPTOGRAPHIC` roles require matching domain sponsorship or the derivation raises an exception

## Verification

| Check | Condition |
|-------|-----------|
| Boundary holds | Write outside `allowed_writes` raises `FileCellBoundaryViolation` |
| Forbidden blocked | `.env`, `.git`, `*.key` paths are never in `allowed_reads` or `allowed_writes` |
| Symlink resolved | `os.path.realpath()` applied before validation |
| Escalation enforced | Protected role without domain sponsorship raises `Exception` |

## Events

| Event | Severity | Status |
|-------|----------|--------|
| `filecell_boundary_violation` | CRITICAL | ✅ EXISTS |
| `filecell_manifest_derived` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `filecell_semantic_escalation_blocked` | CRITICAL | ❌ NEEDS_IMPLEMENTATION |

## Source of Truth

- [filecell.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/filecell.py) — Guard + Manifest
- [manifest_deriver.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/manifest_deriver.py) — Derivation + escalation
