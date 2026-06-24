# SRT1 Authority Runtime Classification

## Overview

Phase 2C recovered governing authorities. Phase 2D recovered authority contracts. Phase 2E classifies how the SRT-1 organism lives at runtime.

This document does not add new authorities by default. It separates:

- Governing Authorities: own decision domains.
- Metabolic Processes: transform experience into reusable knowledge.
- Runtime Services: perform bounded operations when invoked.
- Persistence Systems: store continuity, recall, lineage, trust, and graph state.
- Interfaces: expose state and receive human or assistant input.

The key distinction:

```text
Authorities govern.
Processes transform.
Services act.
Stores remember.
Interfaces mediate.
```

Learning and Knowledge Structuring are therefore treated as candidate non-authority systems unless future evidence shows that they own decision domains.

## Runtime Category Definitions

| Category | Definition | Owns decisions? | Examples |
| --- | --- | --- | --- |
| Governing Authority | Owns a decision domain, refusal rules, acceptance criteria, and state responsibility | Yes | Continuity, Verification, Trust Awareness |
| Metabolic Process | Converts experience, evidence, or state into improved future knowledge | No, unless delegated by an authority | Learning, lesson promotion, cognitive reconstitution |
| Runtime Service | Performs bounded work when invoked by an authority or interface | No | Indexing, context serving, packet generation |
| Persistence System | Stores durable state, graph relationships, lineage, or metadata | No | Continuity store, recall store, knowledge graph |
| Interface | Presents state and receives input from humans or assistants | No, but may submit decisions to authorities | PWA, MCP, local API |

## Authority Runtime Table

| Authority | Runtime posture | State posture | Owns decisions | Reads state | Emits state | Primary triggers | Must not own |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Repo Understanding | Invoked, optionally watched | Persists manifest outputs | Repo truth, freshness, parser coverage | Files, ignore rules, prior manifest | Manifest, symbols, hashes, dependencies | manual re-index, file change, accepted change, assistant startup | seed lifecycle, approval, private signing |
| Continuity | Always available, event-driven transitions | Persistent canonical state | seed/build state progression | manifest freshness, human decisions, verification | seed state, build state, checkpoints | seed planted, approval, verification, return/revise | AST parsing, code mutation |
| Reflection | Event-driven, periodic, human-requested | Mostly computed, findings may persist | coherence/drift assessment | continuity, repo facts, doctrine, traces | findings, confidence, warnings | drift signal, checkpoint, human request, verification failure | remediation, lifecycle mutation |
| Recall | Invoked | Reads persistent state, emits packets | retrieval eligibility and relevance | continuity, prior packets, state docs, reflection | recall packet, relevance/freshness label | seed activation, context generation, verification, reinjection | lesson creation, private memory implementation |
| Reinjection | Event-driven/invoked | Mostly ephemeral packets, optional cached outputs | context delivery boundaries | recall packet, manifest summary, drift warnings | context packet, MCP response, compact instructions | assistant startup, drift, context refresh, seed activation | source mutation, full repo dumps in standing docs |
| Context Isolation | Invoked per seed/proposal/action | Boundary output may persist for task | allowed/forbidden boundary | manifest, seed scope, dependency map | workcell/FileCell boundary | proposal, assistant action, verification setup | private execution authority, global repo access |
| Verification | Invoked after proposed or completed change | Evidence persists | evidence verdict | proposal, workcell, pre/post hashes, manifest | verdict, evidence, re-index request | change proposal, post-change event, human request | merge authority, private rollback executor |
| Human Co-Creation | Human-invoked/event-notified | Decisions persist | approve/reject/revise/accept decisions | verification, continuity, warnings, trust state | decision record, scope change | review, alert, status check, approval gate | autonomous control, direct source mutation |
| Constellation | Invoked/periodic health polling | Registry persists, peer status partly ephemeral | federation awareness and sharing eligibility | engine registry, peer health, approved summaries | peer map, health report, stale/degraded flags | workspace scan, health poll, human-approved sharing | shared context by default, cross-engine execution |
| Trust Awareness | Always available, computed plus persisted metadata | Partly persistent | trust state vocabulary and fail-closed posture | artifact metadata, verification, lineage, decisions | signed/unsigned, verified/unverified, lineage labels | artifact creation, verification, approval, state transition | private signing service, private keys, audit chain implementation |

## Always-On / Invoked / Persisted Map

| Authority | Always available | Always running | Invoked | Event-driven | Periodic | Persistent state |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Repo Understanding | Yes | No | Yes | Optional | Optional | Manifest outputs |
| Continuity | Yes | Yes as state authority | No for access, yes for transitions | Yes | No | Yes |
| Reflection | Yes | No | Yes | Yes | Optional | Findings optional |
| Recall | Yes | No | Yes | Yes | No | Packets optional, source stores yes |
| Reinjection | Yes | No | Yes | Yes | No | Packets optional |
| Context Isolation | Yes | No | Yes | Yes | No | Per-task boundary optional |
| Verification | Yes | No | Yes | Yes | No | Evidence yes |
| Human Co-Creation | Yes | No | Yes | Yes | No | Decisions yes |
| Constellation | Yes | No | Yes | Yes | Optional | Registry yes |
| Trust Awareness | Yes | Yes as computed posture | Yes | Yes | No | Metadata yes |

## State Ownership Map

| State | Owner | Readers | Persistence |
| --- | --- | --- | --- |
| Source files | Repo / human workspace | Repo Understanding, Context Isolation, Verification | Filesystem |
| Manifest | Repo Understanding | All authorities | Persistent generated output |
| Symbol map | Repo Understanding | Reflection, Context Isolation, Reinjection, Verification | Manifest/context output |
| Dependency map | Repo Understanding | Context Isolation, Constellation, Verification | Manifest/context output |
| Seed state | Continuity | Reflection, Recall, Human Co-Creation, Verification | Persistent |
| Build plan state | Continuity | Reflection, Reinjection, Human Co-Creation | Persistent |
| Drift findings | Reflection | Recall, Reinjection, Human Co-Creation | Persistent or ephemeral by severity |
| Recall packet | Recall | Reinjection, Human Co-Creation | Ephemeral/cacheable |
| Context packet | Reinjection | Assistant Interface, Context Isolation | Ephemeral/cacheable |
| Workcell/FileCell boundary | Context Isolation | Verification, Human Co-Creation | Per-task persistent or ephemeral |
| Verification evidence | Verification | Human Co-Creation, Continuity, Trust Awareness | Persistent |
| Human decisions | Human Co-Creation | Continuity, Trust Awareness, Constellation | Persistent |
| Peer registry | Constellation | Human Co-Creation, Reinjection by approval | Persistent |
| Peer health | Constellation | Human Co-Creation | Ephemeral with freshness |
| Trust metadata | Trust Awareness | All authorities | Persistent where tied to artifacts |
| Lesson records | Metabolic process, governed by Verification/Human/Trust | Recall, Knowledge Structuring | Persistent if accepted |
| Knowledge graph | Persistence/structuring layer | Recall, Reflection, Constellation summaries | Persistent |

## Candidate Non-Authority Systems

These systems are architecturally important, but they do not currently appear to own governing decision domains.

| System | Likely category | Governed by | Purpose | Reason not authority yet |
| --- | --- | --- | --- | --- |
| Learning | Metabolic process | Verification, Human Co-Creation, Trust Awareness | Converts verified experience into candidate lessons | Transforms experience; does not decide acceptance alone |
| Lesson Extraction | Metabolic process | Reflection, Verification | Extracts reusable pattern from experience | Produces candidates, not authority decisions |
| Lesson Promotion | Metabolic process | Human Co-Creation, Trust Awareness | Promotes candidate lessons into accepted recall material | Promotion requires approval/trust |
| Lesson Retirement | Metabolic process | Reflection, Human Co-Creation, Trust Awareness | Retires stale or contradicted lessons | Retirement is governed by evidence and approval |
| Cognitive Reconstitution | Metabolic/recovery process | Continuity, Recall, Reflection | Rebuilds context after drift, loss, or interruption | Recovery transform, not standalone decision owner |
| DataCraft | Metabolic/structuring process | Repo Understanding, Recall, Trust Awareness | Shapes raw state into usable structured knowledge | Organizes and transforms |
| Knowledge Structuring | Topology/structuring layer | Recall, Reflection, Trust Awareness | Builds relationships, clusters, lineage, lesson networks | Organizes idea-to-idea topology, does not govern by itself |
| Knowledge Graph | Persistence system | Trust Awareness, Recall | Stores relationships, clusters, lineage | Store, not authority |
| Graph Traversal | Runtime service | Recall, Knowledge Structuring | Retrieves connected context | Service, not authority |
| Context Serving | Runtime service | Reinjection | Serves bounded context to assistants | Service under Reinjection |
| Packet Generation | Runtime service | Reinjection, Recall | Builds recall/context packets | Service under authority rules |
| Workcell Derivation | Runtime service | Context Isolation | Computes allowed/forbidden boundaries | Service under Context Isolation |
| Indexing | Runtime service | Repo Understanding | Runs scan/parse/hash pipeline | Service under Repo Understanding |

## Metabolic Process Lifecycle

### Experience to Lesson Flow

```text
Experience occurs
-> Verification determines evidence result
-> Human Co-Creation accepts, rejects, or returns outcome
-> Trust Awareness labels evidence and lineage
-> Learning extracts candidate lesson
-> Knowledge Structuring links lesson to seeds, files, decisions, failures, and domains
-> Human/Trust gates promote or reject lesson
-> Recall may retrieve promoted lesson later
-> Reflection may flag lesson as stale or contradicted
-> Human/Trust gates retire or revise lesson
```

### Lesson States

| State | Meaning | Governing checks |
| --- | --- | --- |
| candidate | Extracted but not accepted | Verification evidence present |
| promoted | Accepted for future recall | Human approval and trust state sufficient |
| degraded | Still useful but stale, partial, or contradicted | Reflection finding or freshness issue |
| retired | No longer eligible for default recall | Human decision or trust/reflection failure |
| unknown | Missing lineage or source | Trust Awareness blocks default promotion |

### Lesson Metadata

- `lesson_id`
- `source_seed_id`
- `source_verification_id`
- `source_decision_id`
- `confidence`
- `freshness_state`
- `trust_state`
- `lineage`
- `related_symbols`
- `related_decisions`
- `promotion_state`
- `retirement_reason`

## Knowledge Structuring Layer

Knowledge Structuring is topology, not governance. It organizes idea-to-idea relationships so Recall and Reflection can operate with better context.

### Owns

- Relationship maps.
- Clusters.
- Lineage chains.
- Lesson networks.
- Semantic adjacency.
- Cross-seed conceptual links.

### Does Not Own

- Whether a lesson is accepted.
- Whether a fact is verified.
- Whether context should be injected.
- Whether cross-engine sharing is allowed.
- Whether source files may be read or written.

### Relationship to Constellation

| Constellation | Knowledge Structuring |
| --- | --- |
| Engine-to-engine awareness | Idea-to-idea awareness |
| Per-engine registry | Concept graph |
| Port/health/status map | Relationship/cluster/lineage map |
| Prevents workspace contamination | Prevents conceptual/context contamination |
| Federated runtime view | Structured knowledge topology |

## Interface Classification

| Interface | Authority served | Runtime role | Persistent output |
| --- | --- | --- | --- |
| PWA/dashboard | Human Co-Creation | Cockpit, review, approval, observation | Human decisions, status notes |
| MCP | Reinjection, Repo Understanding, Recall | Assistant context serving | Usually ephemeral packets |
| Local API | Multiple authorities | Status, seed operations, context serving | Depends on endpoint |
| AGENTS.md / CLAUDE.md | Reinjection | Compact standing instruction surface | Persistent but not full repo intelligence |
| Manifest/context outputs | Repo Understanding, Reinjection | Machine-readable intelligence | Persistent generated outputs |

## Operational Lifecycle Model

### Startup

1. Trust Awareness initializes fail-closed vocabulary.
2. Continuity loads seed/build state if present.
3. Repo Understanding checks manifest freshness.
4. Constellation may load local engine registry.
5. Human interfaces expose current state as fresh/stale/degraded/unknown.

### Seed Activation

1. Continuity creates or resumes seed state.
2. Repo Understanding confirms manifest freshness.
3. Reflection checks seed/repo coherence.
4. Recall retrieves relevant prior state.
5. Reinjection generates bounded context packet.
6. Human Co-Creation may review direction.

### Proposed Work

1. Context Isolation derives workcell boundary.
2. Reinjection updates assistant context with boundaries.
3. Verification prepares expected evidence criteria.
4. Human Co-Creation approves, revises, or rejects scope where required.

### Accepted Change

1. Verification compares intended vs observed state.
2. Repo Understanding re-indexes affected scope.
3. Continuity records completion, partial completion, return, or termination.
4. Trust Awareness updates verified/unverified and lineage labels.
5. Learning may extract candidate lessons.
6. Knowledge Structuring may link new lessons, decisions, files, and seeds.

### Drift or Failure

1. Reflection emits drift/coherence finding.
2. Recall retrieves relevant prior state.
3. Reinjection emits boundary or correction context.
4. Human Co-Creation chooses revise, return, terminate, or accept risk.
5. Trust Awareness labels degraded/unknown states.

### Constellation Awareness

1. Constellation reads engine registry.
2. Peer health and manifest summaries are checked.
3. Human-approved sharing rules are applied.
4. Reinjection may consume approved summaries only.
5. No shared context is created by default.

## Runtime Conflict Warnings

1. Do not turn metabolic processes into authorities unless they own decisions.
2. Do not let Knowledge Structuring become Constellation; one maps ideas, the other maps engines.
3. Do not let Recall create lessons silently; Recall retrieves.
4. Do not let Reinjection become source mutation.
5. Do not let PWA become an autonomous controller.
6. Do not let Trust Awareness become private signing implementation.
7. Do not let Repo Understanding treat generated manifests as source authority.
8. Do not let Verification become private rollback or merge authority.
9. Do not let Constellation create shared context without explicit approval.

## Phase 2E Findings

1. The current authority list remains valid as governing architecture.
2. Learning is real but currently fits better as a metabolic process.
3. Knowledge Structuring is real but currently fits better as topology/structuring.
4. Runtime services should be audited under their governing authorities, not promoted into authorities.
5. Persistence systems need their own map before implementation recovery.
6. Batch 4 should audit Repo Understanding first, but should record which parts are authority, service, store, or metabolic behavior.

## Batch 4 Implications

Batch 4 should not ask only "what file implements Repo Understanding?"

It should ask:

- Which parts of Repo Understanding are governing authority?
- Which parts are runtime services?
- Which outputs are persistent generated state?
- Which behaviors are metabolic or downstream authority leakage?
- Which private hooks are optional and fail-closed?
- Which generated files are source evidence and which are outputs?

The first code-side audit should classify each implementation candidate by runtime category before proposing any code changes.
