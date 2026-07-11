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

Repository Activation is now a working product bootstrapping layer. SRT-1 can register or select the local repository it manages, run Repository Understanding, and expose FileCells and WorkCells through the dashboard cockpit.

## 2. Public Core Authority State

- Repository Activation: ACTIVE. Repository Manager, repository registry, active repository selection, launch/stop runtime controls, and repository readiness loading exist as public Core product surfaces.
- Repo Understanding: ACTIVE. Supports local indexing, AST/parser work, file hashing, symbol/dependency mapping, and manifest generation.
- Continuity: ACTIVE / ADVANCING. Queue seed identity is canonical lifecycle truth; SRT anchors remain reflection/coherence metadata. WorkCell execution jobs, review states, completion metadata, and human decisions are recorded.
- Reflection: ACTIVE / OBSERVATIONAL ONLY. Drift detection, doctrine scanning, consistency auditing, and coherence checkpoints may report divergence but must not self-correct.
- Recall: ACTIVE / ADVANCING. RecallPacket-shaped context and manifest candidates are used as the normal handoff shape into Reinjection; private memory remains optional and fail-closed.
- Reinjection: ACTIVE / ADVANCING. AGENTS.md, CLAUDE.md, Cursor context, MCP, local APIs, and packet-shaped context delivery are valid reinjection surfaces.
- Context Isolation: ACTIVE / ADVANCING. FileCell is a local containment concept, not a private-runtime-only concept. WorkCell registry, package readiness, FileCell summaries, workcell.md preview, allowed paths, and write guards exist.
- Verification: ACTIVE / ADVANCING. ChangeProposal review/apply, WorkCell write validation, verification trigger, and post-apply verification evidence exist as public Core surfaces.
- Human Co-Creation: ACTIVE / ADVANCING. Dashboard/PWA surfaces observe, dispatch bounded WorkCell requests, review proposals, run verification, approve completion, return work for revision, and stop/pause/cancel WorkCell jobs. They do not grant raw autonomous repository mutation outside WorkCell guards.
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

SRT-1 Core remains guardrail-first during Plateau 1. It may observe, classify, warn, propose, dispatch bounded WorkCell requests, apply approved ChangeProposals through WorkCell guards, and verify. It must not autonomously merge, self-heal, remediate, or mutate code outside approved WorkCell proposal paths.
