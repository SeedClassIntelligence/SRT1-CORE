# SRT1 Recovery Summary

This document preserves the current recovered SRT-1 Core decisions without
keeping every historical recovery/audit artifact as active public Core context.

## Product Separation

SRT-1 Core is one product in a three-product ecosystem:

1. Seed Reflection: consumer-grade reflection/recovery product.
2. SRT-1 Core: public local repo-continuity and assistant-alignment platform.
3. SRT-1 Enterprise: separate private/team/cloud governance product.

Public Core must not ship Enterprise backend implementation, private signing
authority, private keys, private audit chain, SCIA memory/security
implementation, SION internals, or private execution backends.

## Core Position

SRT-1 Core is a repo-continuity and alignment partner for AI coding assistants.
It helps an assistant understand the project, avoid hallucination, prevent
context bleed, preserve architectural coherence, follow the approved seed/build
plan, operate inside the correct local WorkCell, and keep the human in control.

## Recovered Authorities

| Authority | Owns |
|---|---|
| Repo Understanding | repo facts, manifests, hashes, symbols, dependency maps |
| Continuity | seed/build lifecycle, queue seed identity, checkpoints |
| Reflection | drift/coherence/doctrine findings |
| Recall | relevant prior state and RecallPackets |
| Reinjection | bounded assistant context delivery |
| Context Isolation | WorkCell/FileCell boundaries and forbidden paths |
| Verification | evidence, verdicts, scope comparison, re-index requests |
| Human Co-Creation | approve, reject, revise, return, accept |
| Constellation | independent runtime/repository awareness |
| Trust Awareness | signed/unsigned, verified/unverified, lineage/freshness metadata |

## Runtime Spine

```text
Repository Activation
-> Repo Understanding
-> FileCells
-> WorkCells
-> Seed planting
-> Recall
-> Reinjection
-> WorkCell execution or assistant handoff
-> Verification
-> Human review
-> Re-index and update FileCells
```

## Identity Rules

```text
queue_seed_id = canonical lifecycle identity
srt_anchor_id = reflection/coherence metadata
engine fields = orchestration compatibility only
```

## WorkCell / FileCell Rules

- Repository Understanding creates persistent FileCells.
- Each repository file should receive a default WorkCell boundary.
- FileCells own persistent repository intelligence.
- WorkCells define bounded execution environments.
- WorkCell packages contain `workcell.md`, selected FileCells, recall packets,
  dependency evidence, allowed paths, forbidden paths, verification rules, and
  trust metadata.
- WorkCells may expand only through dependency evidence or human approval.

## Seed Signature Boundary

SRT-1 may let a developer create or attach a Seed Signature from the dashboard.
The safe integration is:

```text
SRT-1 backend requests short-lived Seed Signature session token
-> dashboard opens Seed Signature widget
-> Seed Signature signs externally
-> SRT-1 stores returned signatureId/certificateUrl/trust metadata
```

SRT-1 may enforce attribution by failing closed or marking governed outputs as
unsigned/unverified when required Seed Signature metadata is missing. Public
Core does not ship the Seed Signature platform, private keys, private signing
service, or private audit chain.

## Markdown Cleanup Decision

The SRT-1 skill system was consolidated from one parent file plus five support
files per skill into one `SKILL.md` per skill plus a compact skill registry.
Contracts were condensed into public Core-safe reference contracts.

Active Core standing docs remain:

```text
README.md
BUILD.md
AGENTS.md
CLAUDE.md
SRT1_CURRENT_STATE.md
SRT1_CONTEXT_INDEX.md
SRT1_DECISIONS.md
SRT1_FRONTIER.md
```

Historical recovery reports should not be treated as runtime context.

## Living Recovery References

- `SRT1_REPOSITORY_ACTIVATION.md`
- `SRT1_WORKCELL_RUNTIME_CONTRACT.md`
- `SRT1_SEED_SIGNATURE_WIDGET_INTEGRATION.md`
- `SRT1_SKILL_DYNAMIC_LOADING_PLAN.md`

These are reference documents, not always-loaded assistant context.
