# SRT-1 Core Developer Instructions

## 🌱 ACTIVE SEED — seed_0018_e7711dfd

**TASK:** Verification Seed

**STATUS:** Dispatched, awaiting execution

**PRIORITY:** Execute this task NOW. This was planted remotely.

When complete, create a file at `.srt1/signals/seed_0018_e7711dfd_done.json` with:
```json
{"seed_id": "seed_0018_e7711dfd", "status": "complete", "files_modified": ["list", "of", "files"], "summary": "what was done"}
```

---



You are working inside the SRT-1 CORE repository.

SRT-1 is a repo-continuity and alignment partner for AI coding assistants. Its job is to preserve architectural coherence, reduce hallucination, prevent context bleed, maintain continuity, reflect on drift, recall relevant state, reinject alignment, verify changes, and keep the human in the loop.

## Architecture

- `srt1_code_indexer`: repo understanding authority. Scans files, parses supported source, hashes files, builds symbol/dependency maps, and generates manifests.
- `srt1_platform`: local platform authority. Contains continuity, tracing/reflection, MCP/context serving, containment concepts, verification candidates, and human-loop support.
- `srt1_pro`: Pro/public extension authority. Contains workspace connector, context bundling, and constellation-aware coordination when decoupled from private systems.
- `developer-pwa` and `srt1_platform/pwa`: human observability/review surfaces. They are not direct controllers for autonomous execution.

Generated symbol maps and full repo intelligence belong in SRT-1 manifests/context outputs, not in this standing instruction file.

## Strict Operational Rules

1. Do not introduce private implementation into Core.
2. Do not import, expose, or recreate private Seed Signature authority, private keys, SCIA memory implementation, SCIA security implementation, SION internals, private audit chain, or proprietary team/cloud backend.
3. Core may understand trust states: signed/unsigned, verified/unverified, lineage present/missing. It must not contain the private signing service.
4. FileCell is a local containment concept, not a private-runtime-only concept. Treat FileCell, manifest derivation, verification, and operational registry as Core/Pro candidates only when decoupled from SION, private signing, and private ledger implementation.
5. SRT-1 Core observes, prepares, constrains, and verifies. It does not autonomously merge, remediate, or execute code changes.
6. Private/external integrations must fail closed when unavailable.
7. Follow PONYTAIL: Prefer Existing Capability, Observe Before Changing, No Duplicate Systems, Yield To Existing Working Code, Trim Before Building, Align To Original Intent, Inject Continuity, Leave Simpler Than Found.
