# SRT-1 Core Agent Instructions

You are working inside the SRT-1 Core repository.

SRT-1 is a repo-continuity and alignment partner for AI coding assistants. It helps an assistant understand the project, prevent context bleed, preserve architectural coherence, follow the approved seed/build plan, and operate inside the assigned WorkCell.

## Public Core Authorities

Core includes repo understanding, continuity, reflection, recall, reinjection, context isolation, verification, human co-creation, constellation awareness, and trust awareness.

- `srt1_code_indexer/` owns scanning, parsing, hashing, symbol/dependency maps, and manifests.
- `srt1_platform/` owns local continuity, WorkCells, assistant adapters, verification, and human-loop runtime surfaces.
- `srt1_pro/` contains public/Pro context and constellation capabilities when decoupled from private systems.
- `srt1_platform/pwa/` provides the consumer workspace and technical control room.

## Hard Boundaries

Do not add, expose, or recreate private Seed Signature authority, private keys, SCIA memory/security implementations, SION internals, private audit chains, or Enterprise backend implementation in public Core.

Core may understand signed/unsigned, verified/unverified, and lineage present/missing. External private integrations are optional and fail closed when unavailable. A configured authority signature is required before an assistant proposal may mutate source.

FileCell is persistent file intelligence. WorkCell is the bounded execution environment. Assistant execution must stay inside the WorkCell allowlist and must pass verification and human approval gates.

Generated symbol maps and full repo intelligence belong in SRT-1 manifests and runtime context outputs, not in this standing instruction file.

## Operating Rules

1. Observe before changing and prefer existing capability.
2. Do not duplicate working authorities.
3. Keep runtime seed/context state under `.srt1/`; never inject it into standing instruction files.
4. Do not stage or publish private implementations or generated runtime state.
5. Never bypass WorkCell scope, verification, trust, or human approval.
6. Keep SION deferred unless the user explicitly starts a separate SION effort.
7. Run focused tests and boundary scans before commits.
