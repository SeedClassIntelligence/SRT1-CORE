# SRT1 Release Blueprint

This blueprint is the release discipline SRT-1 Core must follow going forward.
It exists to keep release work focused, public-safe, and product-real.

## Release Principle

SRT-1 Core is released only when it is usable as a local repo-continuity and
assistant-alignment platform without exposing private or Enterprise
implementation.

Release work must strengthen the actual product, not only the description of
the product.

## SRT-1 Must Use SRT-1

SRT-1 is designed to prevent repeated full-repo rereads by producing durable
repo intelligence:

- runtime codebase map
- reinjection context
- manifest-derived summaries
- FileCell and WorkCell packages
- recovery decisions
- authority and boundary records

Release work must use these generated context outputs first. A full repo scan
is allowed only when:

- the generated context is missing;
- the generated context is stale;
- the requested change touches a file not covered by the context;
- verification requires source inspection;
- SRT-1 itself reports uncertainty, drift, or violation findings.

If SRT-1 context is available, it is the first source of repo orientation. Code
files are then read only as bounded evidence for the current task.

## Release-Clean Definition

SRT-1 Core is release-clean when all of these are true:

1. Runtime starts reliably from the documented command.
2. Experience page is the primary user entry point.
3. Dashboard/control room remains advanced visibility and administration.
4. Repository intake works for local folder, pasted path, and GitHub URL.
5. Repository Understanding produces a usable synopsis, manifest, FileCells,
   WorkCells, and dependency/authority evidence.
6. The user can move from onboarding to project conversation without falling
   back to raw backend screens.
7. WorkCell execution is bounded by allowed paths and visible to the user.
8. Assistant/provider selection is explicit and session-safe.
9. Seed Signature is represented as external trust/signing integration, not as
   private Core implementation.
10. No Enterprise/private files or implementation are shipped in public Core.
11. Tests pass for the release-critical paths.
12. Git status contains only intentional Core changes before commit and push.

## Public Core Boundary

Public Core may include:

- repo understanding
- manifest generation
- AST/symbol/dependency extraction
- continuity and seed queue lifecycle
- reflection and drift findings
- recall packets
- reinjection/context delivery
- WorkCell and FileCell boundaries
- verification evidence
- human approval/revision gates
- constellation awareness
- trust-state vocabulary
- external assistant/provider adapter contracts
- external Seed Signature integration hooks

Public Core must not include:

- private Seed Signature service implementation
- private keys
- private audit chain
- SCIA memory implementation
- SCIA security implementation
- SION internals
- Enterprise backend implementation
- proprietary governance loops
- private execution infrastructure
- unrelated LegalTrigger implementation

Seed Signature may be mentioned as the external signing and attribution
platform. Core may request or store public metadata such as signature status,
signature id, certificate URL, lineage, and verification state. Core must not
ship the private signing platform.

## Product Separation

SRT-1 Core, SRT-1 Enterprise, and Seed Reflection are separate products.

SRT-1 Core release work must not blur these lines:

- Seed Reflection is the consumer reflection product.
- SRT-1 Core is the local coding continuity and assistant-alignment product.
- SRT-1 Enterprise is a separate private/team/cloud product with its own
  dashboard and backend.

Core may link to Seed Reflection or Seed Signature as external products, but
their implementations must not be absorbed into Core.

## Required Release Gates

### Gate 1: Runtime Gate

Verify:

- SRT-1 starts.
- `/status` responds.
- `/experience.html?start=1` shows onboarding.
- `/dashboard` loads.
- stop/restart behavior is known.

### Gate 2: User Journey Gate

Verify the real user path:

```text
Open Experience
-> choose folder / paste path / GitHub URL
-> register repository
-> run Repository Understanding
-> read project synopsis
-> discuss direction
-> plant seed
-> create/select WorkCell
-> select assistant/provider
-> execute or hand off
-> review changes
-> verify
-> approve, return, or pause
```

The user must not be trapped in the control room to perform normal work.

### Gate 3: WorkCell Boundary Gate

Verify:

- execution receives allowed paths;
- forbidden paths are enforced;
- assistant actions are attached to a WorkCell;
- visible timeline records dispatch, pause, stop, verification, and approval;
- no assistant can write outside the assigned WorkCell boundary.

### Gate 4: Trust Gate

Verify:

- unsigned work is labeled unsigned;
- unverified work is labeled unverified;
- missing lineage is visible;
- Seed Signature integration fails closed when unavailable;
- no private signing code or keys are present.

### Gate 5: Documentation Gate

Verify:

- README install/start path is accurate;
- website copy matches product reality;
- pricing/payment copy is not misleading;
- Core/Pro/Enterprise boundaries are explicit;
- release notes name known limitations honestly.

### Gate 6: Test Gate

Minimum release-critical checks:

```text
python -m unittest discover -s tests
python -m py_compile <changed python files>
```

Focused checks must include:

- repository activation
- WorkCell runtime/boundary
- seed queue compatibility
- task response identity
- assistant adapter/provider surfaces
- execution bridge fail-closed behavior
- public website messaging

### Gate 7: Boundary Scan Gate

Before commit or push, scan staged diff for:

- private keys
- raw API secrets
- private Seed Signature implementation
- SCIA memory/security implementation
- SION internals
- private audit ledger/chain implementation
- Enterprise backend implementation
- LegalTrigger bleed
- generated runtime state
- scratch/demo artifacts

### Gate 8: Git Gate

Before push:

- inspect `git status --short -uall`;
- stage only intentional files;
- confirm staged file list;
- run tests;
- run boundary scan;
- commit with clean message;
- push only after explicit approval.

## Current Release Posture

Current state from SRT-1 generated context:

- SRT-1 has generated repo intelligence.
- It reports 195 source files, 5871 symbols, and 980 cross-file call chains.
- It reports duplicate and drift findings that must be reviewed before release.
- It has current runtime context files under `.srt1/context`.
- The worktree contains many uncommitted changes.

Therefore, SRT-1 is runtime-capable but not release-clean until the gates above
are satisfied.

## Operating Rule For Future Work

Every future release task must start with:

1. Check SRT-1 runtime/context availability.
2. Read generated SRT-1 context before source files.
3. Define the smallest affected WorkCell/FileCell set.
4. Make the narrowest change that satisfies the release gate.
5. Verify with tests and browser checks when UI is affected.
6. Report exact evidence, remaining risk, and next step.

This is the release blueprint I will follow until it is superseded by an
approved release blueprint version.
