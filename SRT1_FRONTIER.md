# SRT1 Active Frontier

## Current Stabilization Phase

- Organism Stabilization Plateau 1: ACTIVE
- Posture: Product verification and release hardening
- Capability escalation: CONTROLLED
- Code movement: PAUSED except narrow release fixes
- PWA canonicalization: CANONICAL PUBLIC CORE PWA IS `srt1_platform/pwa/`
- Private/Enterprise exposure: FORBIDDEN

## Primary Frontier: Public Core Release Readiness

Status: ACTIVE

The immediate frontier is validating that public Core can be installed, launched, opened in the dashboard, register repositories, create WorkCells/FileCells, dispatch bounded WorkCell requests, review provider proposals, apply approved changes through guards, verify results, and keep private/Enterprise implementations excluded.

SRT-1 is a repo-continuity and alignment partner for AI coding assistants. Public Core must describe local repo understanding, continuity, reflection, recall, reinjection, context isolation, verification, human co-creation, constellation awareness, and trust awareness without implying that private Enterprise systems ship in Core.

## Product Frontier: Repository Activation

Status: ACTIVE

SRT-1 currently has a working single-repository runtime, Repository Manager, Repo Understanding, WorkCell registry, FileCell summaries, WorkCell cockpit, package readiness, workcell.md preview, provider execution readiness, selected-WorkCell dispatch, provider result visibility, ChangeProposal review/apply, verification trigger, and review decision timeline.

Expected first-run flow:

```text
Install SRT-1
-> Launch SRT-1
-> Add Repository
-> Repository Understanding
-> Repository Ready
-> Select WorkCell
-> Plant Seed
```

Expected daily flow:

```text
Launch SRT-1
-> Select Repository
-> Load existing understanding
-> Refresh stale evidence if needed
-> Select WorkCell
-> Plant Seed
```

## Secondary Frontier: Release Hardening

Status: NEXT

The product loop now needs hardening around broader smoke tests, docs truth, package install re-test, dashboard UX pass, and GitHub push/tag preparation. This frontier must preserve the Core/private boundary and must not reintroduce private signing, private memory/security, SION internals, or Enterprise backend code.

| Check | Release concern |
| --- | --- |
| Full test suite | `python -m unittest discover -s tests` must pass |
| Package build | `python -m build` must produce wheel/sdist without private modules |
| Package install | Wheel install smoke must verify CLI entrypoints and dashboard assets |
| Runtime smoke | Dashboard must open and show Repository Manager, WorkCells, provider result controls |
| Boundary scan | Staged/public package must exclude private audit/signing, SCIA memory/security, SION internals, and Enterprise backend |

## Boundary Backlog

- Re-test package install from built wheel in a clean environment.
- Run dashboard smoke after package install.
- Verify README/website copy reflects bounded WorkCell execution and provider proposal review.
- Decide whether local CAS collaboration doctrine remains user-local only or becomes a public SRT-1 doctrine later.
- Push signed/attributed Core commits when boundary scan is clean.
- Stabilize recall as approved summaries and targeted historical evidence retrieval.
- Decouple FileCell, manifest derivation, verification, and operational registry candidates from private signing, SION, and private ledger assumptions before staging.
- Decide canonical PWA source before moving or consolidating dashboard files.
- Clarify constellation as federation of independent engines, not shared context by default.
- Keep trust awareness as Core metadata/vocabulary while private signing remains outside Core.

## Prohibited Frontiers

- Autonomous remediation or orchestration
- Auto-healing syntax/code
- Merge or rollback authority
- Self-correcting continuity
- Public exposure of private Seed Signature authority, private keys, SCIA memory implementation, SCIA security implementation, SION internals, private audit chain, or Enterprise backend
- Architecture expansion during Plateau 1 stabilization
