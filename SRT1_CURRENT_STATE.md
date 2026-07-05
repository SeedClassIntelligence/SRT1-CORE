# SRT1 Current State (Canonical)

## Current Stabilization State

- Organism Stabilization Plateau 1: ACTIVE
- Constitutional Freeze: ACTIVE
- Continuity Cognition: ACTIVE
- Merge Authority: DISABLED
- Reflection Authority: OBSERVATIONAL ONLY
- Detective Constitutional Systems: ACTIVE
- Workspace Mutation Authority: DISABLED
- Autonomous Remediation: FORBIDDEN

## 1. Core Positioning

SRT-1 is a repo-continuity and alignment partner for AI coding assistants. It helps the assistant understand the project, avoid hallucination, prevent context bleed, preserve architectural coherence, follow the approved seed/build plan, and operate inside the correct local workcell.

Core includes local repo understanding, continuity, reflection, recall, reinjection, context isolation, verification, human co-creation, constellation awareness, and trust awareness.

Repository Activation is now recognized as the missing product bootstrapping layer. SRT-1 must first register or select the local repository it manages, then run Repository Understanding, then expose FileCells and WorkCells. Without this layer, the product starts in the middle of the lifecycle.

## 2. Public Core Authority State

- Repository Activation: MISSING / NEXT. First-run Repository Manager, repository registry, active repository selection, and repository freshness loading are not yet complete product surfaces.
- Repo Understanding: ACTIVE. Supports local indexing, AST/parser work, file hashing, symbol/dependency mapping, and manifest generation.
- Continuity: PARTIAL. Seed lifecycle and build-plan state exist as public candidates and must be stabilized around active/pending/completed/terminated and partial-completion states.
- Reflection: ACTIVE / OBSERVATIONAL ONLY. Drift detection, doctrine scanning, consistency auditing, and coherence checkpoints may report divergence but must not self-correct.
- Recall: PARTIAL. Canonical continuity docs exist; historical walkthroughs remain archival evidence and are not injected by default.
- Reinjection: PARTIAL. AGENTS.md, CLAUDE.md, Cursor context, MCP, and local APIs are valid reinjection surfaces.
- Context Isolation: PARTIAL / ADVANCING. FileCell is a local containment concept, not a private-runtime-only concept. WorkCell registry, package readiness, FileCell summaries, and workcell.md preview now exist; Repository Activation must precede them in the first-run user flow.
- Verification: PARTIAL. Verification and stitch preparation are public Core/Pro candidates when decoupled from private signing, SION, and private ledger implementation.
- Human Co-Creation: PARTIAL / ADVANCING. Dashboard/PWA surfaces exist as observability/review surfaces, not direct controllers. The PWA now needs a Repository Manager before the WorkCell cockpit for first-time users.
- Constellation: PARTIAL. Workspace connector and registry work should federate independent engines without shared context by default.
- Trust Awareness: VOCABULARY ONLY IN CORE. Core may understand signed/unsigned, verified/unverified, and lineage present/missing states.

## 3. Private / External Boundary

The following do not belong in public Core:

- private Seed Signature authority
- private keys
- SCIA memory implementation
- SCIA security implementation
- SION internals
- private audit chain
- proprietary team/cloud/SSO/Slack backend implementation

Private/external systems are optional integrations and must fail closed when unavailable.

## 4. Continuity Freshness Definitions

| State | Meaning |
| --- | --- |
| FRESH | Canonical docs align with runtime state and manifest evidence within threshold. |
| STALE | Canonical docs lag physical reality beyond acceptable threshold. Context may be incorrect. |
| DEGRADED | Continuity cannot be verified. Insufficient evidence to confirm or deny alignment. |
| UNKNOWN | No freshness data available. Session must treat compressed memory as unverified. |

## 5. Active Constraint

SRT-1 Core remains detective-first during Plateau 1. It may observe, classify, warn, propose, and verify. It must not autonomously merge, self-heal, remediate, or execute code changes.
