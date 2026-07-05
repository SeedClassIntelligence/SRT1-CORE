# SRT1 Skill Dynamic Loading Plan

Purpose: slim the SRT1 skill system without removing capability. The current skill set is relevant, but its Markdown layout is too heavy for active runtime context.

## Current Skill Shape

SRT1 currently has nine documented public skill capabilities:

| Skill | Primary authority | Runtime loading | Keep? | Reason |
|---|---|---|---|---|
| repo-indexing | Repo Understanding | Startup, repo activation, re-index | Yes | Foundational repository truth. |
| ast-analysis | Repo Understanding | During indexing/parsing | Yes | Symbol/dependency extraction. |
| filecell-manifest-derivation | Context Isolation / Repo Understanding | Seed/workcell scope derivation | Yes | Converts repo intelligence into bounded FileCell/WorkCell scope. |
| module-boundary-protection | Context Isolation | Before reads/writes/context expansion | Yes | Prevents context bleed and unauthorized path access. |
| context-injection | Reinjection | Assistant startup, context refresh, MCP request | Yes | Delivers bounded context to assistant surfaces. |
| drift-detection | Reflection | Seed checkpoints, completion review, manual scan | Yes | Detects coherence drift without autonomous remediation. |
| post-execution-verification | Verification | After proposed execution/change | Yes, but partial | Needed for completion truth; current docs mark implementation gaps. |
| constellation-mapping | Constellation | Multi-engine/repo view, dashboard topology | Yes | Supports federated independent SRT1 runtimes. |
| audit-event-emission | Trust Awareness / Continuity | Lifecycle and evidence events | Yes, boundary-reviewed | Keep Core event vocabulary; Seed Signature creation/attachment may be initiated in SRT-1, but signing authority remains external. |

Two additional skill folders exist without Markdown payloads:

| Folder | Status | Recommendation |
|---|---|---|
| consistency-auditing | Empty/scaffold | Either document as Reflection subskill or remove folder later if unused. |
| doctrine-scanning | Empty/scaffold | Either document as Reflection subskill or remove folder later if unused. |

## Problem

Each documented skill repeats the same support-file structure:

- activation.md
- events.md
- governance.md
- inputs_outputs.md
- verification.md
- SKILL.md

That creates 45 support docs beyond the parent SKILL.md files. The content is useful, but the structure makes SRT1 treat many small Markdown files as separate truth sources.

## Dynamic Loading Model

SRT1 should not load every skill document for every task.

Always available:

- Compact skill registry.
- Skill ID and name.
- Authority supported.
- Trigger conditions.
- Inputs/outputs summary.
- Boundary classification.
- Source-of-truth implementation file.

Loaded only when triggered:

- Full parent SKILL.md.
- Related contract docs.
- Verification details.
- Governance details.
- Event schema details.

Never loaded as active runtime truth by default:

- Historical recovery notes.
- Marketing docs.
- Enterprise/private implementation docs.
- Consumer Seed Reflection docs.
- Private signing implementation docs.

## Selection Rules

| Trigger | Skills selected |
|---|---|
| Register/open repository | repo-indexing, ast-analysis |
| Generate or refresh manifest | repo-indexing, ast-analysis, filecell-manifest-derivation |
| Create WorkCell/FileCell package | filecell-manifest-derivation, module-boundary-protection, context-injection |
| Plant seed | module-boundary-protection, context-injection, drift-detection |
| Assistant context refresh | context-injection, drift-detection as needed |
| Change proposed/executed | module-boundary-protection, post-execution-verification, audit-event-emission |
| Completion review | post-execution-verification, drift-detection, audit-event-emission |
| Multi-repo/multi-runtime dashboard | constellation-mapping |
| Trust lineage display | audit-event-emission plus Trust Awareness vocabulary only |

## Consolidation Rule

For each skill folder, preserve the parent SKILL.md and merge only the strongest points from support docs:

- Activation triggers.
- Required inputs.
- Expected outputs.
- Boundary rules.
- Verification success/failure criteria.
- Emitted events, if public Core-safe.

After merge, support docs can be removed from Core tracking or archived after approval.

## Boundary Corrections Needed

Public Core skill docs may mention Seed Signature and may describe an in-product
flow where a developer creates or attaches a Seed Signature from SRT-1. The
boundary is that SRT-1 brokers the request and stores returned trust metadata;
the standalone Seed Signature platform owns signature creation, signing
authority, keys, and private signing records.

The approved integration shape is a widget/session-token flow:

- SRT-1 backend calls the Seed Signature session endpoint server-to-server.
- The platform API key is used only on the backend.
- SRT-1 frontend loads the Seed Signature SDK.
- Dashboard triggers call `SeedSignature.openSignModal(...)` with the returned
  session token.
- `onComplete` returns public metadata such as `signatureId` and
  `certificateUrl`.
- SRT-1 stores returned metadata only.
- If Seed Signature is unavailable, SRT-1 fails closed.

Public Core must not imply it ships:

- private Seed Signature authority
- private keys
- private signing service
- private audit chain
- signing queues as implementation
- SION internals
- Enterprise backend

Audit/event docs should use language like:

> Core can mark signature-eligible events and let a developer initiate Seed
> Signature creation/attachment from SRT-1. The standalone Seed Signature
> platform performs signing and returns trust metadata. Public Core fails closed
> when no external signing authority is configured.

## Target Shape

Current tracked skill Markdown shape:

```text
9 parent SKILL.md files
45 support docs
7 contracts
1 operating map
```

Recommended public Core shape:

```text
srt1-skills/SRT1_SKILL_REGISTRY.md
srt1-skills/<skill>/SKILL.md          # one per active skill
srt1-skills/contracts/*.md            # reference only, later condensed
```

Estimated reduction:

```text
~62 skill Markdown files
↓
~17-20 skill/contract Markdown files
```

## Implementation Sequence

1. Create compact registry.
2. Boundary-sanitize parent SKILL.md files.
3. Merge support docs into parent SKILL.md files.
4. Remove support docs from Core tracking only after verifying content is preserved.
5. Mark contracts as reference docs, not always-on runtime context.
6. Add skill-selection logic later so SRT1 retrieves skill docs by trigger/authority.

## Stop Point

This is a cleanup and loading plan. No support docs should be deleted until their strongest points are merged into the parent SKILL.md files and approved.
