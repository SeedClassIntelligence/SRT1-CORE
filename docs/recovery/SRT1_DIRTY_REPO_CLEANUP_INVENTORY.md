# SRT1 Dirty Repo Cleanup Inventory

Date: 2026-06-24

This document captures the dirty-repo cleanup path that brought SRT1 Core back to
a clean public working tree after the Continuity, Recall/Reinjection, Workcell,
Repo Understanding, Constellation, Reflection, engine orchestration, execution
bridge, tracing, launcher, and governance-draft quarantine checkpoints.

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

## Current Clean Summary

The current public Core working tree contains:

- 0 tracked changed files
- 0 staged files
- 0 untracked public Core files
- ignored local/deferred drafts preserved on disk
- one local permission warning may still appear when reading `.pytest_cache/`

Recent clean checkpoints:

| Commit | Purpose |
| --- | --- |
| `924d7bb` | Deferred private/SION governance drafts quarantined |
| `3df755c` | Core local setup simplified |
| `93f2f0f` | Pro remediation wording normalized |
| `8c9aee1` | Tracing kept Core-safe |
| `f658bf6` | Dirty repo cleanup map updated |
| `a39699d` | Execution bridge kept Core-safe, without private governance ownership |
| `e1b239b` | Core engine orchestration isolated |
| `9f62c7d` | Detective doctrine and taxonomy scanners |
| `f56988f` | Local operational registry |
| `d11d8f8` | Core understanding intelligence adapter |
| `307f08b` | Workspace connector parser coverage |
| `dac5028` | Repo understanding parser coverage |
| `60df130` | Packaged Core PWA source selected |

## Completed Cleanup Queue

| Cleanup area | Result | Commit |
| --- | --- | --- |
| Local/generated ignores | Runtime, scratch, local copies, generated manifests, DBs, and marketing drafts ignored. | `91c1da8` |
| Private package removal | `packages/scia_memory/*` and `packages/scia_security/*` removed from public Core. | `4c325d9` |
| PWA canonical source | `srt1_platform/pwa/` selected as packaged Core PWA source; `developer-pwa/` treated as local prototype copy. | `60df130` |
| Recovery docs | Root recovery doctrine consolidated under `docs/recovery/`. | `3664555` |
| Skills/contracts | Public Core skills/contracts map added. | `29dceb9` |
| Repo Understanding | Parser/indexer coverage recovered and tested. | `dac5028`, `307f08b`, `d11d8f8` |
| Constellation/registry | Local operational registry added. | `f56988f` |
| Reflection/detective scans | Doctrine/taxonomy scanners added. | `9f62c7d` |
| Engine orchestration | Core-safe orchestration isolated without staging private/SION paths. | `e1b239b` |
| Execution bridge | Bridge kept Core-safe and decoupled from private governance ownership. | `a39699d` |
| Tracing | Trace metadata preserved without private audit-ledger wiring. | `8c9aee1` |
| Pro wording | “Self-healing” language normalized to governed remediation. | `93f2f0f` |
| Setup | Root installer, launcher, and `srt1.bat` made Core-only and easy to run. | `3df755c` |
| Deferred drafts | Private/SION audit/governance drafts ignored and preserved locally. | `924d7bb` |

## Historical Cleanup Buckets

The following buckets are preserved as the original cleanup evidence. They do
not describe the current working tree; the current clean state and ignored
residue are summarized above and below.

### KEEP / CORE

These are likely public Core product assets, but must still be staged in focused
commits.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `srt1_platform/tracing_system.py` | modified | Reflection/coherence candidate. | Review for private coupling before commit. |
| `srt1_platform/consistency_auditor.py` | untracked | Reflection/consistency candidate. | Review and test before commit. |
| `srt1_platform/governance_monitor.py` | untracked | Reflection/governance candidate. | Review for Core-safe vocabulary. |
| `srt1.bat` | untracked | Local launcher candidate. | Review path assumptions before commit. |
| `Install-SRT1.ps1` | untracked | Public installer candidate. | Review for local paths/private refs before commit. |

### KEEP / REVIEW

These may belong in Core, but need founder/product decision before staging.

| Path or group | Status | Reason | Recommended action |
| --- | --- | --- | --- |
| `srt1_pro/__init__.py` | modified | Public package exports may expose Pro/Core boundary. | Review after module decisions. |
| `.cursorrules` | modified | Assistant context policy. | Review after docs/context boundary decision. |
| `START_SRT1.bat` | modified | Local launcher behavior. | Review with installer/launch batch. |
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
| `srt1_platform/audit_ledger.py` | untracked | Private audit/signing implementation candidate. | Keep out of public Core unless reduced to public trust metadata only. |

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

## Historical Engine Cleanup Warning

This warning is preserved from the dirty-state audit. The broad engine split was
completed in `e1b239b` by staging only Core-safe orchestration and leaving
private/SION/auth/cloud/Enterprise-adjacent paths out of the public checkpoint.

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
6. PWA canonical source is `srt1_platform/pwa/`. `developer-pwa/` remains a local/prototype copy outside public Core commits.
7. SION is spelled `SION`.
8. SION is a deferred first-party assistant/executor integration. It may later work inside approved sandboxes/workcells or delegate to other agents, but it is not active current SRT1 Core runtime.
9. Current public Core cleanup should focus on SRT1 process/product and should not wire SION as an execution or governance owner.

## Current Ignored / Deferred Residue

As of the latest cleanup checkpoint, the public Core working tree is clean. The
following ignored local/deferred files remain preserved on disk:

| Path | Status | Current read |
| --- | --- | --- |
| `srt1_platform/audit_ledger.py` | ignored | Private audit/signing implementation candidate. Preserve locally or move to private repo; do not publish as public Core implementation. |
| `srt1_platform/governance_monitor.py` | ignored | Private/SION/audit-ledger governance monitor candidate. Preserve for later private/SION work. |
| `srt1_platform/consistency_auditor.py` | ignored | Valuable detective Reflection idea, but current draft imports private audit ledger and mentions SION. Rewrite Core-safe before promotion. |
| `scia_ui_system_skill_v_1.md` | ignored | Product/UI doctrine with Enterprise/SION surface guidance. Preserve as product doctrine or private archive candidate. |
| `scratch/` | ignored | Local probes and experiment scripts. Promote selected scripts only after review. |
| `scratch_ledger_test/` | ignored | Local ledger test output. Keep local/generated. |
| `.pytest_cache/` | ignored | Local test cache; may show permission warning on this machine. |

## Recommended Next Action

Proceed from cleanup into product verification:

```text
1. Run full targeted Core smoke tests.
2. Verify package metadata and entry points.
3. Verify `Install-SRT1.ps1`, `START_SRT1.bat`, and `srt1.bat` on a clean path.
4. Boundary scan tracked public Core files for private/SION implementation leakage.
5. If clean, prepare push/PR plan for public Core.
```

Do not delete ignored drafts yet. They are preserved local material, not public
Core source.
