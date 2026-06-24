# SRT1 Dirty Repo Cleanup Inventory

Date: 2026-06-24

This document captures the current dirty state of the SRT1 working tree after the
Continuity, Recall/Reinjection, and Workcell recovery checkpoints.

No files were moved, deleted, staged, or committed as part of this inventory.

## Cleanup Objective

SRT1 Core should become a clean public product repository centered on:

- local repo intelligence
- manifest generation
- continuity and seed lifecycle
- recall and reinjection
- workcell/context isolation
- verification
- MCP/API/context serving
- human dashboard/PWA shell
- constellation awareness
- public trust-state awareness

SRT1 Core should not contain:

- private Seed Signature authority implementation
- private keys
- private audit chain implementation
- SCIA memory implementation
- SCIA security implementation
- SION internals
- Enterprise backend implementation
- generated runtime state
- scratch probes
- duplicated dashboard authority

## Current Dirty Summary

The current working tree contains:

- 53 tracked changed/deleted files
- 212 dirty/untracked status entries reported by `git status --short -uall`
- no staged files at inventory time
- one local permission warning reading `.pytest_cache/`

Recent clean checkpoints:

| Commit | Purpose |
| --- | --- |
| `fd47bec` | Workcell boundary primitives and tests |
| `a55d55a` | Continuity identity and Recall/Reinjection handoff |
| `462bc86` | Authority dependency architecture |
| `4d63029` | Core authority docs and public boundary |
| `e7d07d1` | Recovery inventory and boundary plan |

## Cleanup Buckets

### KEEP / CORE

These are likely public Core product assets, but must still be staged in focused
commits.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `srt1_code_indexer/indexer.py` | modified | Repo Understanding implementation. | Review and commit only Core-safe hunks. |
| `srt1_code_indexer/language_parsers.py` | untracked | Parser/AST support for Repo Understanding. | Review, test, then commit if Core-safe. |
| `srt1_platform/tracing_system.py` | modified | Reflection/coherence candidate. | Review for private coupling before commit. |
| `srt1_platform/execution_bridge.py` | modified | Assistant/work execution boundary candidate. | Review for autonomous execution and private coupling. |
| `srt1_platform/consistency_auditor.py` | untracked | Reflection/consistency candidate. | Review and test before commit. |
| `srt1_platform/doctrine_scanner.py` | untracked | Reflection/doctrine candidate. | Review and test before commit. |
| `srt1_platform/governance_monitor.py` | untracked | Reflection/governance candidate. | Review for Core-safe vocabulary. |
| `srt1_platform/taxonomy_validator.py` | untracked | Validation/typing candidate. | Review before commit. |
| `srt1_platform/llm_adapter.py` | untracked | Optional adapter candidate. | Keep only if local, optional, and fail-closed. |
| `srt1_platform/llm_providers.py` | untracked | Optional local/provider abstraction candidate. | Review for dependency and secret exposure. |
| `srt1_platform/intelligence_adapter.py` | untracked | Repo intelligence/semantic enrichment candidate. | Review for external/private coupling. |
| `srt1_pro/workspace_connector.py` | modified | Constellation/workspace awareness candidate. | Review and isolate as Constellation batch. |
| `srt1_platform/operational_registry.py` | untracked | Constellation registry candidate. | Review and test before commit. |
| `srt1.bat` | untracked | Local launcher candidate. | Review path assumptions before commit. |
| `Install-SRT1.ps1` | untracked | Public installer candidate. | Review for local paths/private refs before commit. |

### KEEP / REVIEW

These may belong in Core, but need founder/product decision before staging.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `srt1_code_indexer/engine.py` | modified | Large mixed orchestration file with Core, Constellation, PWA, auth/cloud, SION/audit/private-adjacent changes. | Never stage whole. Split by hunk after audit. |
| `srt1_platform/__init__.py` | modified | Public package exports may expose new modules. | Review after module decisions. |
| `srt1_pro/__init__.py` | modified | Public package exports may expose Pro/Core boundary. | Review after module decisions. |
| `.cursorrules` | modified | Assistant context policy. | Review after docs/context boundary decision. |
| `START_SRT1.bat` | modified | Local launcher behavior. | Review with installer/launch batch. |
| `SRT1_AUTHORITY_CONTRACTS.md` | untracked | Valuable architecture doctrine. | Move or commit under `docs/recovery/` if Core-safe. |
| `SRT1_AUTHORITY_RUNTIME_CLASSIFICATION.md` | untracked | Valuable architecture doctrine. | Move or commit under `docs/recovery/` if Core-safe. |
| `SRT1_STATE_OWNERSHIP.md` | untracked | Valuable architecture doctrine. | Move or commit under `docs/recovery/` if Core-safe. |
| `SRT1_CONSTITUTION.md` | untracked | Potential product doctrine. | Review for public language/private claims. |
| `PHASE_*_WALKTHROUGH.md` | untracked | Recovery/build narrative. | Archive, docs, or omit from Core. |
| `docs/SRT1_Code_Indexer_Complete_Reference.docx` | untracked | Large reference artifact. | Review whether source docs should be Markdown instead. |
| `scia_ui_system_skill_v_1.md` | untracked | UI/system skill candidate. | Review for Core relevance. |

### PWA / DASHBOARD DUPLICATION

There are two dashboard/PWA surfaces. This is a real product cleanup issue.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `developer-pwa/*` | modified/untracked | Existing standalone PWA/dashboard surface. | Decide if canonical, archive, or source template. |
| `srt1_platform/pwa/*` | modified/untracked | Packaged PWA/dashboard surface. | Decide if canonical public Core PWA. |
| `developer-pwa/constellation.html` | untracked | Constellation UI candidate. | Review during Constellation/PWA batch. |
| `developer-pwa/health.html` | untracked | Health/status UI candidate. | Review during PWA batch. |
| `developer-pwa/observatory.html` | untracked | Human observability candidate. | Review during PWA batch. |
| `developer-pwa/srt1-core.html` | untracked | Product page or app shell candidate. | Review for public Core fit. |
| `srt1_platform/pwa/constellation.html` | untracked | Packaged duplicate/candidate. | Review only after canonical source decision. |
| `srt1_platform/pwa/health.html` | untracked | Packaged duplicate/candidate. | Review only after canonical source decision. |
| `srt1_platform/pwa/observatory.html` | untracked | Packaged duplicate/candidate. | Review only after canonical source decision. |
| `srt1_platform/pwa/templates/*` | untracked | PWA template expansion. | Keep only in canonical PWA source. |
| `developer-pwa/sw.js`, `srt1_platform/pwa/sw.js` | modified | Service worker changed in both surfaces. | Do not stage until canonical PWA chosen. |

### PRIVATE / REMOVE FROM PUBLIC CORE

These are private/Enterprise implementation areas and should not be pushed into
public SRT1 Core.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `packages/scia_memory/*` | deleted tracked | Private memory implementation should not ship in public Core. | Confirm deletion strategy, then commit removal or move to private repo. |
| `packages/scia_security/*` | deleted tracked | Private security/signing/integrity implementation should not ship in public Core. | Confirm deletion strategy, then commit removal or move to private repo. |
| `memory/` | local directory | Private/local memory area already ignored. | Keep local/private; do not stage. |
| `scia_memory/` | local directory | Private memory implementation already ignored. | Keep local/private; do not stage. |
| `scia_security/` | local directory | Private security implementation already ignored. | Keep local/private; do not stage. |
| `seed-reflection/` | local ignored directory | Proprietary/private-adjacent area. | Keep outside public Core. |
| `SRT1-CORE/` | local ignored nested checkout/copy | Nested repo/checkouts should not be tracked here. | Keep ignored or remove locally later. |
| `sion_output/` | local runtime/private-adjacent output | Generated output with SION naming. | Ignore/archive locally; do not stage. |

### GENERATED / LOCAL IGNORE

These should not be part of public Core product source.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `.srt1/` | local directory | Runtime state. | Keep ignored. |
| `.pytest_cache/` | local directory | Test cache; currently permission warning. | Ignore and optionally clean locally later. |
| `debug.log` | local file | Runtime log. | Keep ignored. |
| `pytest_output.txt` | local file | Test output. | Keep ignored. |
| `srt1_audit_delta.json` | local file | Generated audit output. | Keep ignored. |
| `srt1_cloud.db` | local file | Local database; `*.db` ignored. | Keep ignored. |
| `srt1_code_manifest.json` | local generated manifest. | Generated repo intelligence output. | Keep ignored via manifest pattern. |
| `scratch.html` | local scratch. | Temporary output. | Keep ignored. |
| `unknown_to_ast.py` | local scratch. | Temporary analysis artifact. | Keep ignored. |
| `scratch/*` | untracked | Probe scripts, live experiments, dashboard patches. | Do not commit; archive selectively if valuable. |
| `scratch_ledger_test/` | local directory | Local test output/probe. | Ignore/archive locally. |

### MARKETING / PRODUCT POSITIONING REVIEW

These are not runtime source. Some may be valuable, but they should not be mixed
with implementation recovery commits.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `docs/marketing/*` | untracked | Marketing copy and production briefs. | Review as product/marketing batch. |
| `docs/marketing/screenshots/*` | untracked | Generated screenshots/assets. | Keep only if docs site needs them. |
| `SRT1_Marketing_DevExperience.webp` | untracked | Marketing image. | Move under docs/marketing or omit. |
| `docs/marketing/SRT1_Dashboard_Promo.webp` | untracked | Marketing image. | Review size/source before commit. |

### SKILLS / CONTRACTS REVIEW

The skills directory is valuable but should become a disciplined public Core
capability map, not a random doctrine dump.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `srt1-skills/SRT1_OPERATING_MAP.md` | untracked | Skills operating map. | Review for Core-safe authority alignment. |
| `srt1-skills/repo-indexing/*` | untracked | Repo Understanding skill. | Preserve after boundary scan. |
| `srt1-skills/ast-analysis/*` | untracked | Repo Understanding skill. | Preserve after boundary scan. |
| `srt1-skills/context-injection/*` | untracked | Reinjection skill. | Preserve after boundary scan. |
| `srt1-skills/drift-detection/*` | untracked | Reflection skill. | Preserve after boundary scan. |
| `srt1-skills/filecell-manifest-derivation/*` | untracked | Context Isolation skill. | Preserve after boundary scan. |
| `srt1-skills/module-boundary-protection/*` | untracked | Context Isolation/Verification skill. | Preserve after boundary scan. |
| `srt1-skills/post-execution-verification/*` | untracked | Verification skill. | Preserve after boundary scan. |
| `srt1-skills/constellation-mapping/*` | untracked | Constellation skill. | Preserve after boundary scan. |
| `srt1-skills/audit-event-emission/*` | untracked | Trust/audit-adjacent skill. | Review carefully for private audit leakage. |
| `srt1-skills/contracts/*` | untracked | Public contract candidates. | Review terms; preserve only Core-safe contracts. |

### DELETED DOCS REVIEW

These tracked files are deleted in the working tree. Deletion may be correct, but
should not be committed blindly.

| Path | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `CTO_HANDOVER_TO_CLAUDE.md` | deleted | May contain stale handoff/private context. | Review from HEAD before confirming deletion. |
| `PRODUCT_ARCHITECTURE.md` | deleted | May contain stale or valuable product architecture. | Review from HEAD; archive valuable sections if needed. |
| `SRT1_ENFORCEMENT_MODE.md` | deleted | May contain enforcement doctrine. | Review for private/SION language before deletion/archive. |

## Engine Cleanup Warning

`srt1_code_indexer/engine.py` is the main high-risk dirty file.

Current diff size is large and mixed. It appears to include multiple concerns:

- Core orchestration
- seed/continuity support
- recall/reinjection support
- PWA/API routes
- constellation/operational registry hooks
- audit ledger hooks
- private or SION-adjacent references
- auth/session/cloud routes
- Enterprise proxy-adjacent routes

Rule: do not stage `engine.py` as a whole.

Required cleanup method:

1. split by authority/function
2. extract only Core-safe hunks
3. test each hunk set
4. boundary scan staged diff
5. commit small checkpoints

## Proposed Cleanup Batches

### Batch B: Ignore and Local Artifact Cleanup

Purpose: reduce noise without touching product logic.

Actions:

- verify `.gitignore` covers all local/generated artifacts
- add `scratch/`, `scratch_ledger_test/`, `sion_output/`, and marketing drafts if decided
- do not delete yet unless explicitly approved

Candidate commit:

```text
chore: tighten local artifact ignores
```

### Batch C: Private Boundary Cleanup

Purpose: make public Core stop tracking private implementation.

Actions:

- decide whether deleted `packages/scia_memory/*` and `packages/scia_security/*` should be committed as removals
- preserve any valuable doctrine in private archive notes, not public implementation
- confirm no public Core imports break

Candidate commit:

```text
chore: remove private implementation packages from public core
```

### Batch D: PWA Canonical Source Decision

Purpose: eliminate duplicated dashboard authority.

Actions:

- compare `developer-pwa/` vs `srt1_platform/pwa/`
- choose canonical public Core PWA source
- archive/ignore the non-canonical copy
- do not redesign UI in this batch

Candidate commit:

```text
recover: choose canonical public core pwa shell
```

### Batch E: Engine Split

Purpose: separate engine work into safe public Core slices.

Actions:

- inspect `engine.py` diff by hunk
- stage only Core-safe orchestration changes
- reject or park private/SION/auth/cloud/Enterprise hunks
- keep engine as orchestrator, not authority owner

Candidate commits:

```text
recover: isolate core engine orchestration
recover: add constellation status orchestration
recover: align pwa api surface
```

### Batch F: Skills and Contracts Cleanup

Purpose: make skills a public Core capability map.

Actions:

- boundary scan all `srt1-skills/`
- keep Core-safe skills/contracts
- rewrite/archive private-heavy audit/signing language
- add missing Repo Read Discipline skill only after approval

Candidate commit:

```text
docs: add public core skills and contracts map
```

### Batch G: Product Source Consolidation

Purpose: commit final clean source structure for build-out.

Actions:

- verify package exports
- verify launcher/install scripts
- verify PWA source
- verify tests
- run boundary scan and smoke tests

Candidate commit:

```text
recover: consolidate srt1 core product structure
```

## Immediate Founder Decisions Needed

1. Should `packages/scia_memory/*` and `packages/scia_security/*` be removed from public Core in the next cleanup commit?
2. Which PWA source is canonical: `developer-pwa/` or `srt1_platform/pwa/`?
3. Should marketing assets live in this repo, or stay outside until product packaging?
4. Should recovery docs at repo root be moved under `docs/recovery/` before commit?
5. Should `scratch/` be ignored entirely, or should selected scripts be promoted into tests/tools?

## Founder Decisions Recorded

1. `packages/scia_memory/*` and `packages/scia_security/*` should be removed from public Core.
2. Seed Signature applies conceptually across developer, Pro, and Enterprise tiers, but the signing authority implementation, keys, signing service, and private audit chain remain outside public Core.
3. Marketing assets may stay outside Core until product packaging.
4. Recovery docs should live under `docs/recovery/` before commit when they are preserved.
5. Scratch should be ignored by default. Selected scripts may be promoted later into tests/tools only after review.
6. PWA canonical source remains undecided. Current working assumption for review: `srt1_platform/pwa/` is the likely packaged public Core PWA, while `developer-pwa/` is likely a development/prototype surface.

## Recommended Next Action

Proceed with Batch B:

```text
Ignore and Local Artifact Cleanup
```

Do not delete files yet. First tighten ignore rules and produce a reduced
`git status` view. Then move to private boundary cleanup.
