# FileCell Manifest Derivation Skill

> **Skill ID:** `SRT1-SKILL-006`
> **Module:** LeastPrivilegeManifestDeriver
> **Classification:** DECIDING
> **Mutates Source:** ❌ (creates output directory only)

---

## Purpose

Computes the smallest possible `FileCellManifest` from the `symbol_table` and `call_graph`. Determines exactly which files execution actor can read and write for a specific seed execution. Replaces workspace-wide reads with dependency-traced reads.

---

## Activation

| Trigger | Source |
|---------|--------|
| Seed execution request | Pre-execution actor authorization step |
| `derive()` called | By execution pipeline with `seed_id`, `task`, `files_likely`, `domains` |

## Inputs

| Input | Type | Source |
|-------|------|--------|
| `seed_id` | `str` | Seed queue |
| `task` | `str` | User intent |
| `files_likely` | `List[str]` | LLM intent classifier or ChangeProposal |
| `domains` | `List[str]` | Intent classification domains |
| `symbol_table` | `Dict` | SRT-1 Engine |
| `call_graph` | `Dict` | SRT-1 Engine |

## Outputs

| Output | Type |
|--------|------|
| `FileCellManifest` | Dataclass: `cell_id`, `allowed_reads`, `allowed_writes`, `forbidden_paths`, `dependencies`, `dependency_reasoning` |
| Output directory | `{workspace_root}/sion_output/{seed_id}/` created |

## Derivation Algorithm

1. **Resolve targets** — `files_likely` → absolute paths, verified against `symbol_table` (H.1 enforcement: files must exist in AST)
2. **Walk dependencies** — BFS depth=2 through `symbol_table` dependency names
3. **Semantic escalation check** — If resolved files contain `AUTH_SECURITY`/`CRYPTOGRAPHIC` roles, require matching domain
4. **Compute reads** — `targets ∪ dependencies ∪ explicit_reads`
5. **Compute writes** — `sion_output/{seed_id}/ ∪ explicit_writes`
6. **Compute forbidden** — `ALWAYS_FORBIDDEN_PATTERNS` + `ARCHIVE_CANDIDATES`
7. **Filter** — Remove forbidden from reads/writes
8. **Generate manifest** — With full reasoning log

## Governance

- `files_likely` that are not in `symbol_table` are REJECTED (logged in reasoning)
- Dependency walk is capped at depth=2 to prevent scope explosion
- `AGENTS.md` only included if explicitly authorized with reason
- Semantic Escalation blocks derivation entirely if domain sponsorship is missing

## Events

| Event | Severity | Status |
|-------|----------|--------|
| `filecell_manifest_derived` | INFO | ❌ NEEDS_IMPLEMENTATION |
| `filecell_semantic_escalation_blocked` | CRITICAL | ❌ NEEDS_IMPLEMENTATION |

## Source of Truth

- [manifest_deriver.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/manifest_deriver.py) — Full derivation logic
