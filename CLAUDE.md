# SRT-1 Core Developer Instructions

You are working inside the SRT-1 Core repository.

SRT-1 preserves project understanding and continuity while constraining AI coding assistants to approved WorkCells. Runtime context is generated under `.srt1/context/` and must not overwrite this standing file.

## Architecture

- `srt1_code_indexer`: repository scanning, AST parsing, hashing, symbols, dependencies, and manifests.
- `srt1_platform`: continuity, WorkCells, bounded assistant execution, verification, trust metadata, and human-loop runtime surfaces.
- `srt1_pro`: context bundling, reinjection, and constellation-aware public/Pro capabilities.
- `srt1_platform/pwa`: consumer workspace and technical control room.

Generated symbol maps and full repo intelligence belong in SRT-1 manifests/context outputs, not in this standing instruction file.

## Strict Operational Rules

1. Do not introduce private implementation into Core.
2. Do not expose private Seed Signature authority, keys, SCIA memory/security, SION internals, private audit chains, or Enterprise backend implementation.
3. Core understands trust states; configured private signing remains external and must fail closed.
4. FileCell intelligence is persistent. WorkCell execution is temporary and bounded by allowed paths.
5. Assistant proposals require scoped execution, authority signing when configured, backend verification, and human acceptance.
6. Keep runtime seed/context state under `.srt1/`; never inject it into this file.
7. Follow PONYTAIL: Prefer Existing Capability, Observe Before Changing, No Duplicate Systems, Yield To Existing Working Code, Trim Before Building, Align To Original Intent, Inject Continuity, Leave Simpler Than Found.
