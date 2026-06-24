# SRT-1 CORE Agent Instructions

You are working inside the SRT-1 CORE repository.

SRT-1 is a repo-continuity and alignment partner for AI coding assistants. It helps the assistant understand the project, avoid hallucination, prevent context bleed, preserve architectural coherence, follow the approved seed/build plan, and operate inside the correct local workcell.

## Public Core Authorities

Core includes local repo understanding, continuity, reflection, recall, reinjection, context isolation, verification, human co-creation, constellation awareness, and trust awareness.

- `srt1_code_indexer/`: repo understanding, AST/parser support, file hashing, symbol/dependency mapping, and manifest generation.
- `srt1_platform/`: local platform authorities such as seed lifecycle, trace/reflection surfaces, MCP/context serving, public containment concepts, and verification candidates.
- `srt1_pro/`: workspace connector, context bundling, and constellation-aware public/pro capabilities when decoupled from private systems.
- `developer-pwa/` and `srt1_platform/pwa/`: human observability/review shell. Do not treat the PWA as a direct execution controller.

## Hard Boundaries

Do not add, expose, or rely on private implementations in public Core:

- private Seed Signature authority
- private keys
- SCIA memory implementation
- SCIA security implementation
- SION internals
- private audit chain
- Enterprise backend, team/cloud/SSO/Slack implementation

Core may understand trust states such as signed/unsigned, verified/unverified, and lineage present/missing. The signing authority and private audit implementation remain outside Core.

FileCell is a local containment concept, not Enterprise-only. Public FileCell, manifest derivation, verification, and operational registry work may belong in Core/Pro when decoupled from SION, private signing, and private ledger code.

Enterprise/private integrations are optional and must fail closed when unavailable.

Generated symbol maps and full repo intelligence belong in SRT-1 manifests/context outputs, not in this standing instruction file.

## Operating Rules

1. Observe before changing. Read the relevant files and prefer existing capability.
2. Do not build duplicate systems when a working local authority already exists.
3. Do not move PWA files until the canonical source is approved.
4. Do not stage or publish private implementations.
5. Do not claim SRT-1 autonomously executes, merges, self-heals, or controls code changes.
6. Keep dashboard/PWA language centered on observation, review, approval, rejection, and status.
7. Verification prepares evidence and checkpoints; human approval remains the gate.
