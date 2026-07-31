# SRT1 Canonical Development Folder

## Canonical Folder

The canonical SRT-1 Core development folder is:

```text
C:\Users\SEEDN\Downloads\SRT1 CODING
```

This folder is the only folder that should be treated as the active SRT-1 Core
working repository for release cleanup, testing, commit preparation, and GitHub
pushes.

Git remote:

```text
https://github.com/SeedClassIntelligence/SRT1-CORE.git
```

Branch:

```text
main
```

## Non-Canonical Folders

Nearby folders such as `SRT1-main`, `SRT1 CODE`, `SRT1`, `SRT1-ENTERPRISE`,
`seed-reflection-isolated`, `seedsignature-main`, `scia-studio`, and other
SCIA/Seed folders may be useful as history, reference, or separate products.
They are not the active SRT-1 Core development source unless explicitly
promoted by founder decision.

Do not mix files from those folders into Core without a boundary review.

## Product Separation

SRT-1 Core, SRT-1 Enterprise, Seed Signature, Seed Reflections, and LegalTrigger
are separate product surfaces.

Core may reference external products by integration boundary, but Core must not
absorb their private implementation.

Core must not ship:

- private Seed Signature authority implementation
- private keys
- SCIA memory implementation
- SCIA security implementation
- SION internals
- private audit chain
- Enterprise backend implementation
- unrelated LegalTrigger implementation
- Seed Reflections application source

## Dirty File Meaning

Dirty files inside the canonical folder are not automatically bad. They mean the
worktree contains changes that have not yet been split, reviewed, staged, and
committed.

Dirty files must be separated by release batch before staging:

| Bucket | Purpose | Examples |
| --- | --- | --- |
| Release gate docs | Release blueprint, known limitations, canonical folder rule | `docs/recovery/SRT1_RELEASE_BLUEPRINT.md`, `docs/recovery/SRT1_RELEASE_NOTES_DRAFT.md`, this file |
| Boundary protection | Ignore local/generated/scratch paths | `.gitignore`, `MANIFEST.in` |
| Trust / release hygiene | Fail-closed trust and no shipped secrets | `srt1_code_indexer/authority_client.py`, narrow `engine.py` hunks |
| WorkCell execution | Bounded assistant execution and native runtime | `srt1_platform/native_execution_runtime.py`, `srt1_platform/workcell.py`, `srt1_platform/execution_bridge.py` |
| Provider adapters | Assistant adapter handoff and session-only credentials | `srt1_platform/assistant_adapters.py`, adapter tests |
| Experience/dashboard | Consumer workstation and technical cockpit UI | `srt1_platform/pwa/experience.html`, `dashboard.html`, website copy |
| Tests | Evidence that boundaries and runtime behavior work | `tests/test_*` files |
| Review/prototype | Not staged until explicitly promoted | `srt1_platform/pwa/preview2.html`, draft/native docs if not release-approved |

## Separation Rule

Do not stage the whole dirty tree.

Every commit must have one purpose, one boundary, and one test story.

Recommended order:

1. Canonical release docs and boundary ignores.
2. Trust and enforcement hygiene.
3. WorkCell/native execution boundary.
4. Assistant provider adapter handoff.
5. Consumer experience/dashboard route and UX fixes.
6. Package/build/install verification.
7. Final boundary scan and GitHub push.

## Current Release Gate Status

Completed:

- Runtime Gate
- User Journey Gate
- WorkCell Boundary Gate
- Trust Gate
- Documentation Gate
- Test Gate
- Boundary Scan Gate

Open:

- Git Gate

The Git Gate remains open because the worktree contains multiple streams of
work. It should be closed only after clean commit splitting and a final staged
boundary scan.
