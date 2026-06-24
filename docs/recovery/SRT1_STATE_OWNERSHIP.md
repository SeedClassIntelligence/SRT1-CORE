# SRT1 State Ownership

## Overview

This document defines canonical ownership for SRT-1 state before implementation recovery begins.

The purpose is to prevent authorities, runtime services, interfaces, stores, and private integrations from claiming the same truth. One state may have many readers, many generated views, and many persistence locations, but it has exactly one canonical owner.

Core rule:

```text
Authority owns meaning.
Service performs work.
Store persists records.
Interface presents and receives input.
Generated output is not source authority.
```

## Ownership Rules

1. Every state has exactly one canonical owner.
2. Many readers are allowed.
3. Writers must be the owner or an owner-approved transition service.
4. Stores do not own the meaning of stored data.
5. Interfaces do not own displayed state.
6. Runtime services do not own authority state unless explicitly delegated.
7. Metabolic processes may create candidate knowledge, but promotion requires governing authority.
8. Generated manifests, packets, reports, and dashboards are outputs, not source authority.
9. Private/Enterprise state must remain outside public Core.
10. Engine orchestration may coordinate state transitions but must not become permanent state owner.

## 1. Canonical State Inventory

| State | Canonical owner | Primary writers | Readers | Persistence class | Current locations | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Source files | Human/workspace | Human, approved developer tooling | Repo Understanding, Verification, Context Isolation | Project | repository filesystem | Source files outrank generated manifests. |
| Repo sandbox identity | Repo Understanding | sandbox registration service | all authorities | Project/session | repo path, registry entries | Defines the valid read boundary. |
| Ignore/exclusion rules | Repo Understanding | config/docs/user | Repo Understanding, Context Isolation, Reinjection | Project | `.gitignore`, engine skip lists, contracts | Exclusions must be obeyed by all downstream outputs. |
| Repository manifest | Repo Understanding | indexer | all downstream authorities | Project generated output | `srt1_code_manifest.json`, `self.manifest` | Generated output, not source authority. |
| Manifest freshness state | Repo Understanding | indexer/watch service | Continuity, Reflection, Recall, Reinjection, Verification | Session/project | manifest metadata, status routes | Must be explicit: fresh/stale/degraded/unknown. |
| File hash map | Repo Understanding | indexer | Verification, Trust Awareness | Project/session | manifest, `self.file_hashes` | Current hash truth belongs to Repo Understanding. |
| Pre/post verification hash snapshots | Verification | verifier | Human Co-Creation, Trust Awareness, Continuity | Session/project evidence | `verification.py` snapshots | Verification owns comparison evidence, not current repo truth. |
| Symbol map | Repo Understanding | indexer/parser | Reflection, Recall, Reinjection, Context Isolation, Verification | Project generated output | manifest, `self.symbol_table` | Downstream authorities consume but do not redefine. |
| Dependency/call graph | Repo Understanding | indexer/call graph builder | Context Isolation, Verification, Constellation, Knowledge Structuring | Project generated output | `self.call_graph`, manifest | If semantic/topological, Knowledge Structuring may own derived relationships. |
| Parser coverage | Repo Understanding | parser/indexer | Trust Awareness, Human Co-Creation | Project generated output | manifest language coverage | Completeness must be labeled by fidelity. |
| Curation findings | Repo Understanding | indexer curation pass | Reflection, Human Co-Creation | Project generated output | `curation_report` | Duplicate/overlap detection is repo fact; governance response belongs to Reflection. |
| Active seed | Continuity | seed lifecycle service | Reflection, Recall, Reinjection, Human Co-Creation | Session/project | `srt.py`, `seed_queue.py`, engine fields | One canonical active seed source is needed. |
| Seed queue | Continuity | seed queue service | Human Co-Creation, Reflection, Verification | Project | `.srt1/seeds`, `SCIASeedQueue` | Engine may route but should not own lifecycle. |
| Seed lifecycle transition | Continuity | Continuity service via human/verification input | Trust Awareness, Human Co-Creation | Permanent/project history | seed logs, event stream | Transition provenance matters. |
| Build plan | Continuity | build-plan service | Reflection, Reinjection, Human Co-Creation | Project/session | `self.build_plan` | Should reference manifest freshness. |
| Partial completion state | Continuity | Verification + Human Co-Creation through Continuity | Reflection, Recall, Reinjection | Project | seed queue, completion callbacks | Must not collapse into pass/fail only. |
| Reflection checkpoint | Reflection | SRT/reflection service | Recall, Reinjection, Human Co-Creation | Session/project by severity | `srt.py`, `tracing_system.py` | Detective state, not lifecycle owner. |
| Drift finding | Reflection | drift/coherence service | Recall, Reinjection, Human Co-Creation | Session/project | SRT checkpoints, auditors | Should cite evidence/confidence. |
| Doctrine mismatch finding | Reflection | doctrine scanner/consistency auditor | Human Co-Creation, Reinjection | Project | `doctrine_scanner.py`, `consistency_auditor.py` | Doctrine source required. |
| Recall packet | Recall | Recall service | Reinjection, Human Co-Creation | Ephemeral/session cache | `context_bundler.py`, memory call sites | Recall retrieves; it does not create lessons. |
| Recall source eligibility | Recall | Recall service | Reinjection, Trust Awareness | Project/session | not cleanly implemented | Determines whether prior state can be used. |
| Lesson candidate | Learning / Metabolic Process | lesson extraction process | Human Co-Creation, Trust Awareness, Knowledge Structuring | Session/project | not cleanly implemented | Candidate only until promoted. |
| Promoted lesson | Learning / Metabolic Process governed by Human Co-Creation + Trust Awareness | promotion process after approval | Recall, Knowledge Structuring, Reflection | Long-term/project | not cleanly implemented | Promotion requires verification/trust/human approval. |
| Retired lesson | Learning / Metabolic Process governed by Reflection + Human Co-Creation + Trust Awareness | retirement process | Recall, Knowledge Structuring | Long-term/project | not cleanly implemented | Retired lessons are not default recall material. |
| Knowledge graph relationship | Knowledge Structuring / Topology Layer | graph structuring service | Recall, Reflection, Constellation summaries | Long-term/project | not cleanly implemented | Topology, not governance. |
| Context packet | Reinjection | Reinjection service | Assistant Interface, Context Isolation | Ephemeral/session cache | `reinjector.py`, MCP responses | Bounded assistant context. |
| Standing instruction files | Reinjection for generated sections; human owns rest | Reinjection only inside approved managed sections | assistants, humans | Project | `AGENTS.md`, `CLAUDE.md`, `.cursorrules` | Must not become full repo intelligence dump. |
| Workcell/FileCell boundary | Context Isolation | boundary derivation service | Verification, Human Co-Creation, Reinjection | Session/project per task | `filecell.py`, `manifest_deriver.py`, blueprint metadata | Public concept only if decoupled from private execution. |
| Allowed read/write paths | Context Isolation | boundary derivation service | Verification, assistant context | Session/project per task | FileCell/workcell outputs | Forbidden paths override. |
| Change proposal | Verification | proposal service | Context Isolation, Human Co-Creation, Trust Awareness | Session/project evidence | `change_proposal.py`, blueprint data | Public schema must decouple private executor. |
| Verification result | Verification | verifier | Continuity, Human Co-Creation, Trust Awareness | Project evidence | `verification.py`, completion callbacks | Verification owns verdict. |
| Verification evidence bundle | Verification | verifier | Human Co-Creation, Trust Awareness | Project/permanent evidence | snapshots, result objects | Evidence persists beyond UI. |
| Human approval decision | Human Co-Creation | PWA/API/human decision service | Continuity, Trust Awareness | Permanent/project | seed routes, future decision logs | Interfaces capture; Human Co-Creation owns meaning. |
| Human rejection/revision decision | Human Co-Creation | PWA/API/human decision service | Continuity, Reflection, Reinjection | Permanent/project | seed fail/return routes | Must be distinct from technical failure. |
| Dashboard read model | Human Co-Creation | read-model service | humans | Ephemeral/session | `/status`, `/events`, PWA | Derived view, not authority truth. |
| Engine registry | Constellation | registry service | Human Co-Creation, Constellation API | Project/session global | `~/.srt1/registry.json` | Engine may register via adapter. |
| Peer health state | Constellation | health polling service | Human Co-Creation | Ephemeral/session | `/api/constellation` | Stale by default after threshold. |
| Workspace report | Constellation | workspace connector | Human Co-Creation, Reinjection by approval | Project generated output | `.srt1/workspace_report.json` | Summary only; no shared context by default. |
| Trust metadata | Trust Awareness | Trust service/adapters | all authorities | Project/permanent where artifact-bound | `_trust_chain`, provenance fields | Core vocabulary, not private signing. |
| Signature/provenance result | Private / Enterprise | private signing authority | Trust Awareness | Permanent/private | `authority_client.py`, signing hooks | Public Core may reference external state only. |
| Audit ledger entry | Private / Enterprise for private ledger; Trust Awareness for public event metadata | event service/private adapter | dashboard, governance | Permanent/private or project metadata | `audit_ledger.py`, `ledger.db`, `_event_log` | Split public event metadata from private ledger implementation. |
| Auth/session/user files | Private / Enterprise | auth service | interface | Session/project private | `srt1_cloud.db`, auth routes | Not public Core state. |
| Telemetry consent/payload | Human Co-Creation / Trust Awareness | telemetry service after consent | dashboard/human | Project/session | consent file, event log | Optional and explicit. |

## 2. State Dependency Graph

```text
Source files
-> Repo sandbox identity + exclusions
-> Repository manifest
-> Symbol map + dependency map + parser coverage
-> Manifest freshness
-> Continuity seed/build state
-> Reflection findings
-> Recall packet
-> Reinjection context packet
-> Context Isolation workcell boundary
-> Verification evidence/result
-> Human decision
-> Continuity transition
-> Re-index request
-> Repository manifest
```

Cross-cutting graph:

```text
Trust metadata reads:
manifest hash
seed transition
reflection evidence
recall source freshness
context packet source lineage
workcell derivation
verification result
human decision
constellation peer identity
```

Metabolic graph:

```text
Verified experience
-> human accepted outcome
-> trust-labeled evidence
-> lesson candidate
-> promoted lesson
-> knowledge graph relationship
-> future recall packet
```

Constellation graph:

```text
Engine registry
-> peer health
-> manifest summary
-> approved workspace summary
-> optional reinjection input
```

## 3. Writer / Reader Matrix

| State | Canonical writer | Approved transition writers | Readers |
| --- | --- | --- | --- |
| Repository manifest | Repo Understanding indexer | none | all authorities |
| Manifest freshness | Repo Understanding | file watcher/re-index service | Continuity, Reflection, Recall, Reinjection, Verification |
| Symbol map | Repo Understanding parser/indexer | none | Reflection, Recall, Reinjection, Context Isolation, Verification |
| Dependency map | Repo Understanding | Knowledge Structuring may write derived topology | Context Isolation, Verification, Constellation |
| Seed state | Continuity | Human Co-Creation and Verification through Continuity | Reflection, Recall, Reinjection |
| Build state | Continuity | Human Co-Creation through Continuity | Reflection, Reinjection |
| Reflection finding | Reflection | none | Recall, Reinjection, Human Co-Creation |
| Recall packet | Recall | none | Reinjection, Human Co-Creation |
| Context packet | Reinjection | none | Assistant Interface, Context Isolation |
| Workcell boundary | Context Isolation | Human scope approval through Context Isolation | Verification, Reinjection, Human Co-Creation |
| Change proposal | Verification | Human Co-Creation may revise through proposal service | Context Isolation, Verification |
| Verification result | Verification | none | Continuity, Human Co-Creation, Trust Awareness |
| Human decision | Human Co-Creation | none | Continuity, Trust Awareness, Constellation |
| Engine registry | Constellation | engine registration adapter | Human Co-Creation, Constellation |
| Peer health | Constellation | health poller | Human Co-Creation |
| Trust metadata | Trust Awareness | external signing adapter may append external signature reference | all authorities |
| Lesson candidate | Learning process | Verification may supply evidence | Human Co-Creation, Trust Awareness |
| Promoted lesson | Learning process after approval | Human Co-Creation + Trust Awareness gates | Recall, Knowledge Structuring |
| Graph relationship | Knowledge Structuring | lesson/decision/link processors | Recall, Reflection |
| Audit ledger row | Private ledger adapter | private governance components | dashboard/governance views |
| Auth/session state | Private auth service | auth routes | private interfaces |

## 4. Persistence Ownership Matrix

| Persistence class | Definition | Examples | Owner rule |
| --- | --- | --- | --- |
| Ephemeral | Valid only during current operation/request | HTTP response, current peer health, transient context packet | Owned by authority that defines eligibility/verdict |
| Session | Valid for current engine run or assistant session | `self._event_log`, context packet cache, active warnings | Must expire or tie to manifest/session |
| Project | Valid across sessions for one repository | manifest, seed queue, continuity state, workcell evidence | Owned by project authority, not engine |
| Long-term | Reusable across project history | promoted lessons, knowledge graph, decisions | Requires trust/freshness metadata |
| Permanent | Audit/evidence/history that should not be mutated | human decisions, verification evidence, private ledger rows | Append-only or explicitly superseded |
| Private | Not public Core state | private signing records, private audit chain, auth sessions | Excluded or fail-closed hook only |

| State | Persistence class | Canonical owner | Expiration / supersession |
| --- | --- | --- | --- |
| Manifest | Project | Repo Understanding | Superseded by newer scan |
| Manifest freshness | Session/project | Repo Understanding | Expires on file change or unknown scan |
| Seed state | Project | Continuity | Terminal state or explicit reopen |
| Reflection finding | Session/project | Reflection | Superseded by later finding or resolution |
| Recall packet | Ephemeral/session | Recall | Expires on seed/manifest/context change |
| Context packet | Ephemeral/session | Reinjection | Expires on token TTL, seed change, or stale source |
| Workcell boundary | Session/project | Context Isolation | Expires on scope, proposal, or manifest change |
| Verification result | Project/permanent evidence | Verification | Superseded only by new verification event |
| Human decision | Permanent/project | Human Co-Creation | Superseded only by explicit later decision |
| Engine registry | Session/project | Constellation | Expires on heartbeat timeout |
| Trust metadata | Project/permanent where artifact-bound | Trust Awareness | Superseded by artifact change |
| Lesson | Long-term/project | Learning process governed by Human/Trust/Verification | Retired or revised |
| Graph relationship | Long-term/project | Knowledge Structuring | Reweighted, superseded, or retired |
| Audit ledger entry | Private/permanent | Private / Enterprise | Append-only |
| Auth session | Private/session | Private / Enterprise | TTL/revocation |

## 5. Freshness & Expiration Rules

### Global Freshness Vocabulary

| State | Meaning |
| --- | --- |
| fresh | Source basis is current and lineage is present. |
| stale | Source basis was once valid but a newer change exists. |
| degraded | State is partially useful but incomplete, conflicting, or low confidence. |
| unknown | Source basis, timestamp, lineage, or owner is missing. |

### Rules

1. A manifest becomes stale when any indexed source file changes after scan time.
2. A symbol map inherits the manifest freshness state.
3. A seed state becomes degraded when its manifest basis becomes stale.
4. A reflection finding becomes stale when its source manifest or seed state changes.
5. A recall packet expires when seed state, manifest hash, or recall source freshness changes.
6. A context packet expires when its recall packet expires or when token/scope limits are exceeded.
7. A workcell boundary expires when proposal scope, manifest hash, or forbidden-path rules change.
8. A verification result is fresh only for the artifact state it verified.
9. A human decision remains valid until explicitly superseded, but may become contextually degraded if underlying evidence is stale.
10. Constellation peer health expires on heartbeat timeout.
11. Trust metadata becomes stale when the artifact hash changes.
12. Lessons become degraded when Reflection detects contradiction or Trust Awareness loses lineage.

## 6. State Leakage Report

| Leakage | Current pattern | Correct owner | Severity | Recommended boundary |
| --- | --- | --- | --- | --- |
| Engine owns manifest | `engine.py` stores and mutates `self.manifest` | Repo Understanding | HIGH | Engine holds read cache only. |
| Engine owns symbol map | `engine.py` stores `self.symbol_table` | Repo Understanding | HIGH | Use manifest/symbol accessor. |
| Engine owns file hashes | `engine.py` stores `self.file_hashes` | Repo Understanding | MEDIUM | Verification owns snapshots, Repo Understanding owns current hashes. |
| Engine owns seed ID | `engine.py` stores `task_seed_id` while seed queue also stores seeds | Continuity | HIGH | Single seed lifecycle store. |
| Engine owns build plan | `engine.py` stores `self.build_plan` | Continuity | MEDIUM | Build plan state belongs to Continuity. |
| Engine owns context injection output | `engine.py` writes AGENTS.md and appends runtime map | Reinjection | HIGH | Engine triggers Reinjection only. |
| Engine owns recall hydration | `engine.py` calls private memory recall URL | Recall | CRITICAL | Recall service owns fail-closed private integration. |
| Engine owns trust chain | `engine.py` stores `_trust_chain` and `_trust_integrity` | Trust Awareness | HIGH | Trust metadata service owns labels. |
| Engine owns event truth | `_log_event` writes ledger and in-memory cache | Trust Awareness / Private ledger | CRITICAL | Public event metadata separate from private ledger. |
| Engine owns auth sessions | `init_db`, auth routes, `srt1_cloud.db` | Private / Enterprise | CRITICAL | Not public Core. |
| Engine owns registry lifecycle | `engine.py` creates registry and heartbeat | Constellation | MEDIUM | Constellation registry adapter. |
| Engine owns verification completion verdict | `_on_seed_completed` rejects completion | Verification | MEDIUM | Verification returns verdict to Continuity. |
| Engine owns FileCell generation | `generate_blueprint` creates FileCell | Context Isolation | HIGH | Boundary derivation service. |

## 7. Engine State Violations Report

`engine.py` is currently an orchestration shell, interface server, state cache, state writer, private integration host, and authority router. That makes it the highest-risk state ownership violation in the codebase.

| Engine state | Correct owner | Violation | Risk |
| --- | --- | --- | --- |
| `self.manifest` | Repo Understanding | Engine mutates canonical generated repo facts | HIGH |
| `self.symbol_table` | Repo Understanding | Engine serves and consumes symbol truth directly | HIGH |
| `self.curation_report` | Repo Understanding / Reflection consumer | Engine turns repo findings into enforcement | MEDIUM |
| `self.file_hashes` | Repo Understanding | Engine keeps current hash truth | MEDIUM |
| `self.call_graph` | Repo Understanding / Knowledge Structuring | Engine derives and stores dependency graph | MEDIUM |
| `self.task_seed_id` | Continuity | Engine owns active seed pointer | HIGH |
| `self.build_plan` | Continuity | Engine owns build-plan state | MEDIUM |
| `self.operations` | Reflection / Runtime session | Engine owns operation trace-like state | MEDIUM |
| `self.injections` | Reinjection | Engine owns injection history-like state | MEDIUM |
| `self._trust_chain` | Trust Awareness | Engine owns trust chain | HIGH |
| `self._trust_integrity` | Trust Awareness | Engine owns trust verdict | HIGH |
| `self._event_log` | Trust Awareness read cache | Engine owns dashboard cache and ledger write path | HIGH |
| `self.auth` / `dev_token` | Private / Enterprise or local auth adapter | Engine owns auth state | CRITICAL |
| `self.audit_ledger` | Private / Enterprise ledger adapter | Engine owns private ledger dependency | CRITICAL |
| `self.signing_client` | Private signing adapter | Engine owns private signing client | CRITICAL |
| `self._registry` / `_engine_id` | Constellation | Engine owns registry lifecycle | MEDIUM |

## 8. Proposed Ownership Transfers

| Current state / responsibility | Current location | Future owner | Engine role after transfer | Priority |
| --- | --- | --- | --- | --- |
| Manifest state | `engine.py` | Repo Understanding | request scan/read snapshot | HIGH |
| Symbol map | `engine.py` | Repo Understanding | read snapshot | HIGH |
| File hash map | `engine.py` | Repo Understanding | read current hashes | MEDIUM |
| Verification hash snapshots | future verifier | Verification | request verification | MEDIUM |
| Call graph | `engine.py` | Repo Understanding or Knowledge Structuring | read generated graph | MEDIUM |
| Seed lifecycle | `engine.py`, `srt.py`, `seed_queue.py` | Continuity | submit transition request | HIGH |
| Build plan | `engine.py` | Continuity | request generated plan | MEDIUM |
| Reflection warnings | `engine.py`, `srt.py` | Reflection | display/forward findings | MEDIUM |
| Recall hydration | `engine.py` | Recall | request recall packet | CRITICAL |
| Context packets | `engine.py`, `reinjector.py` | Reinjection | trigger packet generation | HIGH |
| Standing instruction generated sections | `engine.py`, `reinjector.py`, `auto_injector.py` | Reinjection | no direct writes | HIGH |
| Workcell/FileCell boundary | `engine.py`, `filecell.py`, `manifest_deriver.py` | Context Isolation | request boundary | HIGH |
| Proposal state | `engine.py`, `change_proposal.py` | Verification | route proposal request | HIGH |
| Verification result | engine completion callbacks | Verification | consume verdict | MEDIUM |
| Human decisions | seed routes/PWA | Human Co-Creation + Continuity | receive decision and delegate transition | HIGH |
| Registry state | `engine.py`, `operational_registry.py` | Constellation | register heartbeat via adapter | MEDIUM |
| Trust metadata | `engine.py`, `authority_client.py` | Trust Awareness | request labels | HIGH |
| Private signatures | engine signing hooks | Private / Enterprise | optional fail-closed external reference | CRITICAL |
| Audit ledger | engine `_log_event` | Private / Enterprise ledger; public metadata by Trust Awareness | emit public event, optional private adapter | CRITICAL |
| Auth/session/user DB | engine auth routes | Private / Enterprise | none in public Core | CRITICAL |

## 9. Refactor Preconditions

No refactor should begin until these are true:

1. Repo Understanding exposes a clear manifest/symbol/hash read boundary.
2. Continuity has one canonical seed/build state owner.
3. Reinjection has a context packet schema distinct from standing instruction files.
4. Recall has a public fail-closed packet boundary and does not depend on private memory.
5. Context Isolation has a public workcell/FileCell schema decoupled from private execution authority.
6. Verification has a public evidence/result schema decoupled from private rollback/signing.
7. Trust Awareness has public metadata vocabulary separated from private signing and private ledger.
8. Human Co-Creation has explicit decision state semantics.
9. Constellation owns registry and peer health state outside engine internals.
10. Engine is documented as an orchestrator/interface shell, not an authority state owner.

## Batch 4B Gate

Batch 4B may proceed to Repo Understanding Implementation Audit only after this state ownership model is accepted as the working boundary.

The Batch 4B audit should ask:

- Does `indexer.py` own manifest truth cleanly?
- Does `engine.py` merely request/read repo state or does it mutate ownership?
- Are generated manifests clearly outputs, not source authority?
- Are parser coverage and freshness explicit?
- Are private signing and delta audit hooks optional and fail-closed?

Until those questions are answered, implementation changes should remain blocked.
