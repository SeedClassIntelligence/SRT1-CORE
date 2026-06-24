# SRT1 Workcell Boundary Contract

## Overview

This document defines the public Core contract for Context Isolation.

SRT-1 uses a workcell boundary to keep assistant context, proposed changes, file access, and verification inside the correct local repository scope. A workcell is local containment. It is not Enterprise-only, not a private signing service, and not an autonomous execution controller.

Public Core may understand boundary, trust, and verification states. Public Core must not ship private Seed Signature authority, private keys, private audit chain, SCIA memory implementation, SCIA security implementation, SION internals, or Enterprise backend implementation.

## Canonical Terms

| Term | Public Core meaning | Must not mean |
| --- | --- | --- |
| Workcell | Local containment boundary for a seed/build task. | Enterprise runtime, shared context, or autonomous executor. |
| FileCell | Implementation candidate for a workcell manifest and guard. | SION-only execution cell. |
| Manifest Deriver | Authority helper that derives least-privilege reads, writes, dependencies, and forbidden paths from repo evidence. | Private policy engine or signing authority. |
| FileCell Guard | Boundary enforcement helper for read/write path checks. | Private audit ledger or autonomous mutation controller. |
| Change Proposal | Typed intended-change contract used before mutation or verification. | Permission to bypass human approval. |
| Execution Lease | Optional, time-bounded permission record for an approved local operation. | Private execution authority, SION mandate, or Core autonomy. |
| Post-Execution Verification | Evidence comparison between intended and actual changes. | Private rollback executor or final human acceptance. |

## Authority Ownership

| Responsibility | Owner | Current implementation candidates | Placement |
| --- | --- | --- | --- |
| Derive allowed reads | Context Isolation | `srt1_platform/manifest_deriver.py` | Core/Pro candidate |
| Derive allowed writes | Context Isolation | `srt1_platform/manifest_deriver.py` | Core/Pro candidate |
| Derive forbidden paths | Context Isolation | `srt1_platform/manifest_deriver.py` | Core candidate |
| Enforce read boundary | Context Isolation | `srt1_platform/filecell.py` | Core candidate |
| Enforce write boundary | Context Isolation | `srt1_platform/filecell.py` | Core candidate |
| Declare intended changes | Verification / Context Isolation handoff | `srt1_platform/change_proposal.py` | Core/Pro candidate |
| Bound temporary execution | Context Isolation / Verification handoff | `srt1_platform/execution_lease.py` | Pro/private until decoupled |
| Compare intended vs actual change | Verification | `srt1_platform/verification.py` | Core/Pro candidate |
| Orchestrate boundary use | Engine | `srt1_code_indexer/engine.py` | Orchestrator only |

## Required Guarantees

1. Allowed reads and allowed writes are separate.
2. Read permission never implies write permission.
3. Forbidden paths override allowed reads and writes.
4. Paths are canonicalized before comparison.
5. Workcell derivation must use repo evidence: manifest, symbol table, dependency map, seed intent, and explicit human-approved scope.
6. Generated manifests are outputs, not source authority.
7. Private paths, secrets, keys, local runtime state, and private implementations must fail closed.
8. Engine may orchestrate workcell creation and verification, but must not own boundary truth.
9. PWA may request, review, approve, reject, or return scope, but must not bypass workcell boundaries.
10. Verification must receive the workcell boundary before judging scope safety.

## Inputs

Context Isolation may consume:

- canonical `queue_seed_id`
- optional `srt_anchor_id` metadata
- seed intent
- build plan state
- repo manifest
- symbol table
- dependency map
- explicit human-approved read/write scope
- recall/reinjection metadata when relevant to scope
- forbidden path policy
- trust metadata such as signed/unsigned, verified/unverified, lineage present/missing

Context Isolation must not require:

- private signing service
- private audit ledger
- SCIA memory implementation
- SCIA security implementation
- SION runtime
- Enterprise backend

## Outputs

Context Isolation may produce:

- workcell manifest
- allowed reads
- allowed writes
- forbidden paths
- dependency reasoning
- scope warnings
- boundary violation records
- degraded/fail-closed status
- verification-ready boundary evidence

Context Isolation must not produce:

- direct source mutation
- autonomous execution verdict
- human acceptance
- private signature
- private audit-chain event

## Runtime Flow

```text
Continuity provides canonical queue_seed_id
Repo Understanding provides manifest, symbol map, dependency map
Recall/Reinjection provide packet-shaped context
Human Co-Creation may approve or adjust scope
Context Isolation derives workcell boundary
Change Proposal declares intended mutation
Optional Execution Lease bounds an approved local operation
Verification compares actual change against proposal and workcell
Continuity records final lifecycle outcome
Trust Awareness labels lineage, verification, and signature state
```

## Public Core Boundary Rules

Public Core may include:

- `FileCellManifest`
- read/write/forbidden path validation
- least-privilege manifest derivation
- proposal schemas
- post-change verification schemas and local comparison
- trust-state vocabulary
- fail-closed optional hooks for private integrations

Public Core must exclude:

- private Seed Signature authority implementation
- private keys
- private signing queues
- private audit chain
- SCIA memory implementation
- SCIA security implementation
- SION internals
- Enterprise backend implementation
- autonomous controller behavior

## Current Decoupling Targets

| File | Preserve | Decouple later |
| --- | --- | --- |
| `srt1_platform/filecell.py` | Path canonicalization, read/write enforcement, forbidden-first checks. | SION docstring, `sion_node` actor, direct audit/signing assumptions. |
| `srt1_platform/manifest_deriver.py` | Least-privilege derivation, AST-backed target validation, forbidden filtering. | `sion_output` default, audit ledger wording, private doctrine headers. |
| `srt1_platform/change_proposal.py` | Typed proposal, file scope, rollback plan, expected verification, risk assessment. | Runtime Law/SION/Seed Signature doctrine language. |
| `srt1_platform/execution_lease.py` | TTL, revocation, one active lease per seed, scope counters. | SION-only mutation authority language and private audit assumptions. |
| `srt1_platform/verification.py` | Snapshot, scope violation detection, collateral damage detection, syntax check. | SION-specific lifecycle wording and private audit assumptions. |
| `srt1_code_indexer/engine.py` | Orchestration handoff. | Direct workcell derivation/signing inside blueprint generation. |

## Refusal Conditions

Context Isolation should fail closed when:

- no canonical seed identity is available
- repo manifest or symbol evidence is stale or missing
- requested scope includes forbidden paths
- requested write scope is broader than approved
- private integration is unavailable but required for the requested operation
- workcell boundary cannot be derived from repo evidence
- PWA or API attempts to bypass verification or continuity state

## Future Recovery Sequence

1. Rename public-facing doctrine from SION-specific language to neutral workcell language.
2. Keep private signing and audit as optional hooks that fail closed.
3. Move engine-side FileCell derivation toward `manifest_deriver.py`.
4. Add tests for read/write separation, forbidden path precedence, and private-hook absence.
5. Align `change_proposal.py` and `verification.py` with canonical `queue_seed_id`.
6. Decide whether `execution_lease.py` is Core, Pro, or private after decoupling review.

## Open Questions

- Should public Core expose `FileCell` as the canonical term, or should `Workcell` be the public term and `FileCell` remain the implementation?
- Should the default output location be `.srt1/workcells/<queue_seed_id>` instead of `sion_output/<seed_id>`?
- Should execution leases exist in public Core as passive records, or only in Pro/private execution integrations?
- Which human approval event expands workcell scope after initial derivation?
