# SRT1 WorkCell Runtime Contract

## Overview

This document defines the recovered WorkCell runtime direction for SRT-1 Core.

The existing workcell boundary contract defines containment: allowed reads, allowed writes, forbidden paths, and verification scope. This runtime contract extends that model. A WorkCell is not only a sandbox. A WorkCell is a persistent bounded architectural environment that can be activated by a seed into a concrete execution instance with repository intelligence, recall, verification rules, and human-approved scope.

The governing principle is:

```text
FileCells own persistent repository intelligence.
WorkCells own bounded architectural environments.
Seeds activate execution inside WorkCells.
```

SRT-1 should not require every assistant session to reread and reinterpret the whole repository. Repo Understanding should maintain persistent FileCells and create a persistent WorkCell for every repository file. Continuity should use seeds to activate work inside the most relevant file WorkCell. The active WorkCell execution should attach additional FileCells only when dependency evidence, contracts, verification requirements, or human approval require expansion.

## Canonical Terms

| Term | Meaning | Must not mean |
| --- | --- | --- |
| Repository Runtime | The local SRT-1 engine for one repository. | A shared cross-project context pool. |
| FileCell | Persistent intelligence object for one file or tightly coupled file set. | Temporary prompt context or an execution sandbox. |
| WorkCell | Persistent bounded execution environment associated with one repository file by default. | A raw folder copy, repo-wide assistant session, feature bucket, or direct autonomous controller. |
| WorkCell Execution | Active seed-driven runtime instance inside a WorkCell. | The permanent WorkCell identity or the whole repository. |
| workcell.md | Agent entry document describing objective, scope, boundaries, verification, and completion rules. | Replacement for source files or standing global assistant instructions. |
| WorkCell Package | Runtime bundle containing local instructions, selected FileCells, recall packets, dependency evidence, allowed paths, and verification rules. | Private memory dump, private signing chain, or Enterprise backend state. |
| Local Knowledge Index | Curated WorkCell-local retrieval set derived from public/Core repository intelligence and approved recall. | Unbounded repository search or private memory dependency. |
| Runtime Port | Optional endpoint identifying an active WorkCell runtime. | Permission to bypass boundaries, verification, or human approval. |

## Architecture Principle

Repository intelligence is persistent.

FileCells are persistent.

WorkCells are persistent bounded file environments assembled from persistent knowledge.

WorkCell executions are temporary runtime instances activated by seeds.

The PWA exists to manage WorkCells rather than to browse repository files as the primary experience. Source code remains available as a view inside the WorkCell, but the core product surface should show operating environments, state, scope, verification, and readiness.

## Authority Ownership

| Responsibility | Owner authority | Notes |
| --- | --- | --- |
| Create canonical seed identity | Continuity | Uses `queue_seed_id` as lifecycle identity. |
| Produce manifest, symbols, dependencies, and file hashes | Repo Understanding | Source of FileCell intelligence. |
| Maintain FileCell intelligence | Repo Understanding + Recall + Verification | Repo facts, historical recall, and verification evidence attach to FileCells. |
| Create persistent WorkCells | Repo Understanding + Context Isolation | Every repository file receives a default WorkCell after repository understanding. |
| Activate WorkCell execution from seed | Continuity + Context Isolation | Continuity owns seed lifecycle; Context Isolation owns boundary. |
| Select FileCells for WorkCell execution | Context Isolation + Recall | Selection must be evidence-based and bounded. |
| Generate `workcell.md` | Reinjection | Reinjection delivers instructions; it does not own retrieval. |
| Run WorkCell execution runtime | Engine / runtime service | Orchestrator only; not owner of seed truth, WorkCell identity, or repo intelligence. |
| Verify WorkCell output | Verification | Checks scope, evidence, tests, and post-change state. |
| Approve, reject, return, or expand scope | Human Co-Creation | PWA is cockpit, not autonomous mutator. |
| Label trust and lineage | Trust Awareness | Core understands labels; private signing remains external. |
| Track multiple WorkCells and ports | Constellation | Federation and status awareness without context contamination. |

## FileCell Contract

A FileCell is the canonical representation of a file inside SRT-1's repository intelligence layer.

### FileCell Identity

Minimum identity fields:

- `filecell_id`
- `repo_id` or repo root identity
- `path`
- `path_hash`
- `content_hash`
- `manifest_hash`
- `language`
- `parser`
- `created_at`
- `updated_at`
- `freshness_state`
- `trust_state`

### FileCell Knowledge

A FileCell may contain:

- AST/parser output
- symbols
- imports
- exports
- dependencies
- dependents
- contracts
- authority metadata
- architectural role
- ownership metadata
- verification status
- historical recall
- related decisions
- risk tags
- allowed operation hints

### FileCell Guarantees

- FileCells are derived from repository evidence, not generated manifests alone.
- FileCells persist across WorkCells.
- FileCells update when the source file changes.
- FileCells may degrade when parser coverage or trust metadata is missing.
- FileCells do not execute work.
- FileCells do not own seed lifecycle.
- FileCells do not bypass allowed/forbidden path policy.

## WorkCell Contract

A WorkCell is the defined operating boundary for one repository file by default. It is the smallest safe execution environment SRT-1 can give an AI assistant.

A seed does not create the file WorkCell itself. Repository Understanding creates the WorkCell after indexing the file. A seed activates work inside the relevant WorkCell when one is known, or causes SRT-1 to propose a degraded fallback when no file evidence exists.

The practical distinction is:

```text
WorkCell = the place
Seed = the purpose
Agent = the worker
FileCells = the knowledge objects
WorkCell Execution = the active runtime package
```

The default relationship is one-to-one:

```text
repository file
-> FileCell
-> WorkCell
```

The FileCell stores what SRT-1 knows. The WorkCell defines where the assistant is allowed to work.

### WorkCell Identity

Minimum identity fields:

- `workcell_id`
- `name`
- `purpose`
- `repo_id` or repo root identity
- `owned_paths`
- `related_paths`
- `restricted_paths`
- `authority_scope`
- `default_verification_rules`
- `default_runtime_port`
- `created_at`
- `updated_at`
- `freshness_state`
- `trust_state`

For a file WorkCell, `owned_paths` should contain exactly one repository file path unless a later, human-approved expansion explicitly attaches related WorkCells.

### WorkCell Execution Identity

Minimum identity fields:

- `workcell_execution_id`
- `workcell_id`
- `queue_seed_id`
- `srt_anchor_id`
- `objective`
- `status`
- `runtime_port`
- `assigned_agent`
- `created_at`
- `updated_at`
- `manifest_hash`
- `trust_state`
- `verification_state`

### WorkCell Execution Runtime State

Recommended state vocabulary:

- `queued`
- `preparing`
- `ready`
- `running`
- `blocked`
- `awaiting_review`
- `returned`
- `completed`
- `terminated`
- `degraded`

Compatibility with older lifecycle vocabulary may remain, but the active WorkCell execution should expose clear operational states.

### WorkCell Package

Every active WorkCell execution should eventually have a package under a deterministic local path such as:

```text
.srt1/workcells/<queue_seed_id>/
```

The package may contain:

```text
workcell.md
runtime_state.json
manifest_snapshot.json
filecells.json
dependency_graph.json
authority_graph.json
verification_rules.json
recall_packets.json
allowed_paths.json
execution_log.json
test_plan.json
handoff.json
```

Not every file needs to exist in the first implementation slice. Missing package sections must be marked `unknown`, `degraded`, or `not_available`, not silently invented.

## Persistent WorkCell Registry

SRT-1 should maintain a persistent WorkCell registry for the repository.

The registry answers:

- which file WorkCells exist
- which repository file belongs to each WorkCell
- which dependencies are allowed or expected
- which contracts govern the environment
- which tests usually verify it
- which active seeds are currently running inside each WorkCell
- which runtime port, if any, is assigned to the active execution

The registry prevents context contamination by making SRT-1 choose a file WorkCell before an agent starts reading.

## workcell.md Contract

`workcell.md` is the entry document for any agent entering an active WorkCell execution.

It should include:

- objective
- seed identity
- current lifecycle state
- assigned agent
- runtime port if active
- scope summary
- success criteria
- authority boundaries
- allowed directories
- restricted directories
- attached FileCells
- related contracts
- recall packet summary
- verification requirements
- testing expectations
- completion requirements
- known blockers
- human approval gates
- trust and freshness labels

The agent should begin with `workcell.md` instead of rediscovering its responsibilities from the full repository.

## Context Contamination Rule

The primary risk WorkCells address is not only out-of-scope file mutation. It is context contamination.

SRT-1 should prevent agents from forming unnecessary relationships across unrelated files simply because they were visible. The agent should not begin by reading the broad repository, a whole feature folder, or neighboring files. The agent should enter through the active file WorkCell package and read only the FileCell, dependencies, contracts, and recall packets selected for the mission.

The default posture is:

```text
Do not broaden context because it is nearby.
Broaden context only when dependency evidence, contract evidence, verification needs, or human-approved scope requires it.
```

## Controlled Expansion

The default execution boundary is one file.

Additional WorkCells may be attached only when:

- Repository Understanding detects an import/dependency relationship
- a contract requires another file
- Verification requires a test/support file
- Recall identifies directly relevant prior work
- a human explicitly approves scope expansion

Expansion should attach additional WorkCells intentionally. It should not happen because files are adjacent in a folder.

## Local Knowledge Index Contract

Each active WorkCell execution should receive a curated local knowledge index. The index should be derived from persistent FileCells, manifest evidence, recall packets, dependency summaries, prior WorkCell outcomes, and human-approved scope.

The local index may include:

- affected symbols
- related contracts
- relevant architectural decisions
- recall packets
- dependency summaries
- verification history
- documentation excerpts
- previous WorkCell outcomes
- known risks

The local knowledge index must not become a hidden global memory dump. It should remain bounded by the WorkCell purpose, active seed objective, dependency evidence, and approved scope.

## Runtime Port Contract

An active WorkCell may receive its own runtime endpoint.

Example:

| Port | Runtime |
| --- | --- |
| 4101 | Repository Runtime |
| 4102 | Authentication WorkCell |
| 4103 | Billing WorkCell |
| 4104 | Documentation WorkCell |
| 4105 | API WorkCell |
| 4106 | Manifest Recovery WorkCell |
| 4107 | Testing WorkCell |
| 4108 | PWA WorkCell |

The port identifies an active runtime environment. It does not grant authority to mutate files, bypass verification, or bypass human approval.

Constellation should know:

- which WorkCell owns each active port
- which repository runtime owns each WorkCell
- which agent is assigned
- whether the WorkCell is healthy, degraded, blocked, or complete
- whether the WorkCell has merge-ready output

## PWA Contract

The PWA should evolve into the operational control center for WorkCells.

The repository dashboard should prioritize:

- repository runtime status
- active WorkCells
- queued WorkCells
- blocked WorkCells
- runtime ports
- assigned agents
- verification state
- trust/lineage state
- merge readiness
- dependency warnings

A WorkCell detail view should expose:

- objective
- current state
- assigned agent
- runtime port
- affected FileCells
- allowed paths
- restricted paths
- recall history
- dependency graph
- execution logs
- pending actions
- test status
- verification progress
- completion requirements
- merge readiness

Source browsing should be a WorkCell view, not the primary product model.

## Runtime Flow

```text
Repository
-> Repo Understanding
-> Persistent FileCells
-> Persistent file WorkCell registry
-> Seed
-> Continuity activates file WorkCell execution
-> Context Isolation derives execution boundary
-> Recall selects relevant prior state
-> Reinjection generates workcell.md and context package
-> WorkCell execution runtime starts or becomes ready
-> Agent operates inside WorkCell execution
-> Verification checks output against scope and evidence
-> Human accepts, returns, rejects, or expands scope
-> FileCells update after accepted changes
-> WorkCell registry updates if boundaries or relationships changed
-> Continuity records final lifecycle state
-> Constellation updates runtime map
```

## State Ownership

| State | Owner | Consumers |
| --- | --- | --- |
| Repository manifest | Repo Understanding | FileCells, WorkCells, Recall, Verification |
| FileCell | Repo Understanding | WorkCells, Recall, Verification, PWA |
| Persistent file WorkCell registry | Context Isolation + Repo Understanding | Continuity, PWA, Constellation, Reinjection |
| Seed lifecycle | Continuity | WorkCell runtime, PWA, Verification |
| WorkCell execution lifecycle | Continuity | PWA, Constellation, Verification |
| WorkCell execution boundary | Context Isolation | Agent, Verification, PWA |
| Recall packets | Recall | Reinjection, WorkCell, PWA |
| `workcell.md` | Reinjection | Agent, PWA |
| Verification result | Verification | Continuity, PWA, FileCells |
| Runtime port map | Constellation | PWA, engine, operators |
| Trust metadata | Trust Awareness | Every authority |

## Public Core Boundary

Public Core may include:

- WorkCell vocabulary
- persistent per-file WorkCell registry schema
- WorkCell package schema
- WorkCell execution schema
- `workcell.md` generation contract
- FileCell identity and summary schema
- manifest-derived FileCell evidence
- local WorkCell registry
- runtime status vocabulary
- port ownership metadata
- bounded local knowledge index
- verification and merge-readiness metadata
- trust labels such as signed/unsigned, verified/unverified, lineage present/missing, fresh/stale/degraded/unknown

Public Core must exclude:

- private Seed Signature authority implementation
- private keys
- private signing queues
- private audit chain
- SCIA memory implementation
- SCIA security implementation
- SION internals
- Enterprise backend implementation
- autonomous source mutation without WorkCell boundary, verification, and human-approved authority

SION may later become a first-party assistant/executor that operates inside approved WorkCells, but SION is not required for the current SRT-1 Core WorkCell runtime contract.

## First Implementation Slice

The easiest safe implementation path is:

1. Keep current repository runtime as the only active server.
2. Add a read-only persistent WorkCell registry that creates one WorkCell per manifest file.
3. Add a read-only WorkCell execution record linked to `queue_seed_id`.
4. Generate a minimal `.srt1/workcells/<queue_seed_id>/workcell.md`.
5. Attach existing manifest summary and boundary evidence.
6. Expose WorkCell registry/status through API.
7. Update the PWA to show WorkCells first.
8. Add FileCell summaries after the per-file WorkCell registry is stable.
9. Add multi-port runtime support only after single-runtime WorkCell executions are reliable.

This preserves working code while moving the product toward autonomous bounded runtime environments without pretending the active seed is the same thing as the persistent WorkCell.

## Refusal Conditions

WorkCell execution should fail closed when:

- no canonical `queue_seed_id` exists
- no WorkCell can be selected or safely proposed
- repository manifest is missing or stale beyond allowed policy
- requested scope includes forbidden paths
- FileCell evidence cannot be derived for required files
- private integration is required but unavailable
- a runtime port is already owned by another active WorkCell execution
- the PWA or API attempts to bypass approval or verification gates

## Open Questions

- Should a WorkCell always have a local package directory, or only once it reaches `ready`?
- Should `runtime_port` be optional until multi-runtime support exists?
- Should FileCells be stored as separate persistent objects or generated from manifest plus verification history in the first Core release?
- Should `workcell.md` be regenerated on every scope change or versioned as immutable snapshots?
- Which WorkCell state should trigger dashboard merge readiness?
- What is the minimum FileCell schema needed before PWA WorkCell views become accurate?
