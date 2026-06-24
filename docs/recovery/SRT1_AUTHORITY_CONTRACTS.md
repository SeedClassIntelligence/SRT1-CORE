# SRT1 Authority Contracts

## Overview

SRT-1 Core is a local repo-continuity and alignment partner for AI coding assistants. This document converts the Phase 2C authority graph into explicit authority contracts before any code-side recovery begins.

These contracts define what each authority may consume, emit, guarantee, refuse, degrade into, and exclude from public Core. Current files are evidence and implementation candidates, not the source of architectural authority.

Canonical dependency model:

```text
Repo Understanding
-> Continuity
-> Reflection
-> Recall
-> Reinjection
-> Context Isolation
-> Verification
-> Human Co-Creation
-> Constellation

Trust Awareness cross-cuts every authority.
```

Core may understand trust states: signed/unsigned, verified/unverified, lineage present/missing, official/unofficial, fresh/stale/degraded/unknown.

Core must not ship private Seed Signature authority, private keys, private signing service, private audit chain, SCIA memory implementation, SCIA security implementation, SION internals, Runtime Law, signing queues, or Enterprise backend implementation.

## Authority Contract Table

| Authority | Contract focus | Inputs | Outputs | Placement | Evidence sources | Recovery action |
| --- | --- | --- | --- | --- | --- | --- |
| Repo Understanding | Manifest freshness, symbol ownership, dependency completeness, parser coverage | Source files, repo sandbox, parser rules, ignore rules | Manifest, file hashes, symbol map, dependency map, parser coverage, freshness state | Core | `srt1_code_indexer/indexer.py`, `language_parsers.py`, `repo-indexing`, `ast-analysis`, `repo_sandbox_contract.md` | Preserve; separate from reinjection/private signing |
| Continuity | Seed/build lifecycle, state transition ownership, partial completion tracking | Manifest state, seed intent, build state, user decisions | Seed state, build state, checkpoints, lifecycle history | Core | `srt.py`, `seed_queue.py`, state docs | Preserve; define lifecycle contract |
| Reflection | Coherence, drift confidence, doctrine mismatch, detective-only behavior | Continuity state, repo facts, trace observations, doctrine sources | Findings, confidence, warnings, recommendations | Core | `srt.py`, `tracing_system.py`, `doctrine_scanner.py`, `consistency_auditor.py`, `drift-detection` | Preserve as detective authority |
| Recall | Relevance, freshness, degradation, public/Core state only | Seed state, prior checkpoints, public state docs, manifest metadata | Recall packet, relevance notes, freshness label | Core/Pro | `thread_recovery.py`, `context_bundler.py`, state docs | Promote to first-class authority |
| Reinjection | Bounded context, token discipline, contamination prevention | Recall packet, reflection warnings, manifest summary, workcell scope | Context packet, MCP response, compact guidance | Core | `reinjector.py`, `context_bundler.py`, `mcp_server.py`, `context_injection_contract.md` | Rewrite around packets and compact standing docs |
| Context Isolation | Allowed/forbidden paths, FileCell/workcell derivation, no cross-project bleed | Manifest, seed/build scope, repo sandbox, dependency map | Workcell boundary, readable/writable paths, forbidden paths | Core/Pro | `filecell.py`, `manifest_deriver.py`, `module-boundary-protection`, `filecell_contract.md` | Rewrite without private execution authority |
| Verification | Proposal/diff evidence, verified/unverified, re-index triggers | Change proposal, workcell, hashes, post-change manifest | Verification result, evidence, re-index request | Core/Pro | `verification.py`, `change_proposal.py`, `post_execution_verification_contract.md` | Rewrite without private rollback executor |
| Human Co-Creation | Approval gates, reject/revise/accept, cockpit-only posture | Context packet, verification evidence, seed/build state | Approval, rejection, revision, acceptance, scope decision | Core | PWA/dashboard/API surfaces | Preserve cockpit; remove autonomous controller claims |
| Constellation | Independent engine federation, per-engine registry, per-port map | Engine registry, health endpoints, approved summaries | Peer map, health/status, dependency awareness | Pro/Core-aware | `workspace_connector.py`, `operational_registry.py`, `constellation-mapping`, `repo_sandbox_contract.md` | Preserve; no shared context by default |
| Trust Awareness | Trust vocabulary and fail-closed metadata | Artifact metadata, transitions, verification evidence | Trust labels, lineage state, official/unofficial state | Core vocabulary, private implementation excluded | `authority_client.py`, audit/signing docs, `audit_event_contract.md` | Keep vocabulary; archive/private implementation doctrine |

## 1. Repo Understanding Contract

### Purpose

Repo Understanding owns the factual map of the local repository. It scans files, computes hashes, parses supported languages, extracts symbols, infers dependencies, detects duplicates/overlaps, and produces a manifest with freshness and parser coverage metadata.

### Inputs

- Registered repo sandbox root.
- Source files inside allowed read boundaries.
- Ignore and exclusion rules.
- Parser dispatch rules.
- Supported extension list.
- Prior manifest metadata for freshness comparison.

### Outputs

- File manifest with hashes and sizes.
- Symbol map.
- Dependency map or call graph.
- Parser coverage report.
- Duplicate, overlap, and risk-tag findings.
- Manifest integrity hash.
- Freshness state: fresh, stale, degraded, or unknown.

### Required Guarantees

- Generated manifests are outputs, not source authority.
- Source files and explicit repo configuration outrank generated manifests.
- Every manifest must identify scan root, timestamp, supported parser coverage, exclusions, and integrity hash.
- Symbol ownership belongs here. Downstream authorities may consume symbols but must not redefine symbol truth.
- Dependency completeness must be labeled by parser fidelity, not overclaimed.
- Excluded paths must not be read, indexed, summarized, or injected.

### Refusal Conditions

- Refuse to scan outside the registered repo sandbox.
- Refuse to treat generated manifests as source files.
- Refuse to mark a manifest fresh when source hashes, parser coverage, or scan completion are unknown.
- Refuse to include private implementation directories marked excluded.
- Refuse to claim full AST certainty for regex or structural-anchor parsers.

### Freshness Rules

- Fresh: source hash set matches current repo state and scan completed without critical parser/read errors.
- Stale: known file changes occurred after manifest generation.
- Degraded: scan completed with unreadable files, parser failures, or partial coverage.
- Unknown: no manifest, missing timestamp, missing hash basis, or unsupported source of truth.

### Trust Metadata

- `manifest_hash`
- `generated_at`
- `source_root`
- `parser_coverage`
- `excluded_paths`
- `freshness_state`
- `signed/unsigned` if an external signing authority is present

### Failure / Degraded Modes

- Partial manifest with degraded state.
- Parser coverage warnings.
- Read-error report.
- Downstream block if sandbox root is missing or excluded-path violation is detected.

### Upstream Dependencies

- Repo sandbox registration.
- Local filesystem access.
- Ignore/exclusion policy.

### Downstream Consumers

- Continuity
- Reflection
- Recall
- Reinjection
- Context Isolation
- Verification
- Constellation
- Trust Awareness

### Public/Core Boundary

Repo scanning, hashing, parser coverage, manifest generation, symbol ownership, and dependency mapping belong in Core.

### Private/Enterprise Exclusions

Core Repo Understanding must not require Seed Signature implementation, SCIA security implementation, private audit chain, private memory, SION, Runtime Law, signing queues, or Enterprise backend services.

## 2. Continuity Contract

### Purpose

Continuity owns seed and build lifecycle state. A seed is a continuity object, not merely a task. Continuity records what is active, pending, completed, terminated, wilted, returned, partially complete, or awaiting human decision.

### Inputs

- Seed intent.
- Build plan state.
- Manifest freshness and version.
- Human decisions.
- Verification results.
- Reflection warnings.
- Partial completion evidence.

### Outputs

- Seed lifecycle record.
- Build lifecycle record.
- Active seed state.
- Pending/completed/terminated/wilted/returned state.
- Partial completion notes.
- Checkpoint history.
- State transition provenance.

### Required Guarantees

- Continuity owns state transitions.
- Each seed must reference the repo facts or manifest freshness state it was planted against.
- State transitions must be explicit and explainable.
- Partial completion must be tracked instead of collapsed into success/failure.
- Human decisions must be recorded as state transition inputs.

### Refusal Conditions

- Refuse to mark a seed complete without verification or explicit human acceptance.
- Refuse to advance a seed from stale or unknown repo facts without warning.
- Refuse to let Reflection mutate lifecycle state directly.
- Refuse to treat a generated context packet as lifecycle truth.

### Freshness Rules

- Fresh when state references a current manifest and no newer accepted change is pending re-index.
- Stale when repo facts changed after the seed/build state was created.
- Degraded when partial completion, failed verification, or missing human decision blocks certainty.
- Unknown when lineage to seed intent or manifest basis is absent.

### Trust Metadata

- `seed_id`
- `build_id`
- `state`
- `previous_state`
- `transition_reason`
- `transition_actor`
- `manifest_hash` or freshness basis
- lineage present/missing
- verified/unverified completion state

### Failure / Degraded Modes

- Seed returned for revision.
- Seed wilted due to age, contradiction, or abandonment.
- Seed terminated by human decision.
- Build plan degraded due to stale manifest.
- Partial completion pending review.

### Upstream Dependencies

- Repo Understanding.
- Human Co-Creation for approval transitions.
- Verification for completion evidence.

### Downstream Consumers

- Reflection
- Recall
- Reinjection
- Context Isolation
- Verification
- Human Co-Creation

### Public/Core Boundary

Seed lifecycle, build state, partial completion, and local continuity checkpoints belong in Core.

### Private/Enterprise Exclusions

Core Continuity must not depend on private memory systems, private audit ledger, signing queues, SION execution state, Runtime Law authorization, or Enterprise backend state.

## 3. Reflection Contract

### Purpose

Reflection detects coherence loss, architectural drift, doctrine mismatch, and consistency problems. Reflection is a governing principle and detective authority. It does not autonomously remediate, execute, merge, roll back, or mutate source in Core.

### Inputs

- Continuity state.
- Repo Understanding outputs.
- Trace observations.
- Doctrine and boundary docs.
- Recent assistant/runtime events.
- Verification outcomes.

### Outputs

- Coherence finding.
- Drift finding.
- Doctrine mismatch finding.
- Consistency warning.
- Confidence level.
- Reinjection recommendation.
- Human review recommendation.

### Required Guarantees

- Findings must distinguish evidence from inference.
- Confidence must be labeled.
- Reflection must not overwrite Continuity state.
- Reflection must not mutate code or trigger autonomous remediation in Core.
- Doctrine findings must cite the source document or state basis where available.

### Refusal Conditions

- Refuse to produce a high-confidence finding without source evidence.
- Refuse to treat stale generated context as doctrine.
- Refuse to auto-fix drift in Core.
- Refuse to escalate to execution authority.

### Freshness Rules

- Fresh when based on current manifest and current continuity state.
- Stale when manifest or seed state changed after the finding.
- Degraded when evidence is partial or doctrine sources conflict.
- Unknown when no seed/build state exists.

### Trust Metadata

- `finding_id`
- `finding_type`
- `evidence_refs`
- `confidence`
- `freshness_state`
- `doctrine_source`
- verified/unverified evidence state

### Failure / Degraded Modes

- Low-confidence warning.
- Conflicting doctrine warning.
- Missing source warning.
- Human review required.

### Upstream Dependencies

- Repo Understanding.
- Continuity.

### Downstream Consumers

- Recall
- Reinjection
- Verification
- Human Co-Creation

### Public/Core Boundary

Coherence findings, drift detection, doctrine scanning, and consistency auditing belong in Core.

### Private/Enterprise Exclusions

Core Reflection must not include autonomous remediation, private governance loops, SION control, Runtime Law authorization, private audit enforcement, or Enterprise policy execution.

## 4. Recall Contract

### Purpose

Recall selects relevant prior state for the current seed/build context. Recall is first-class and distinct from private memory implementation. Core Recall works from known public/Core state only.

### Inputs

- Seed or build state.
- Current manifest metadata.
- Reflection findings.
- Public/Core state docs.
- Prior verified context packets.
- Prior accepted decisions.

### Outputs

- Recall packet.
- Relevance explanation.
- Freshness label.
- Degraded/unknown warning.
- Excluded material list.

### Required Guarantees

- Recall packets must be relevant to the active seed/build state.
- Recall must label freshness and confidence.
- Recall must not require SCIA memory implementation.
- Recall must not inject private memory content into public Core context.
- Recall must distinguish official state from historical notes.

### Refusal Conditions

- Refuse to recall from private memory implementation in public Core.
- Refuse stale or contradictory state unless labeled degraded.
- Refuse to include private/Enterprise internals.
- Refuse to treat unverified historical doctrine as current authority.

### Freshness Rules

- Fresh when derived from current docs, current manifest, or verified recent state.
- Stale when superseded by newer decisions or manifest changes.
- Degraded when state conflicts but still contains useful context.
- Unknown when lineage or decision status is missing.

### Trust Metadata

- `recall_packet_id`
- `source_refs`
- `relevance_score`
- `freshness_state`
- official/unofficial
- lineage present/missing

### Failure / Degraded Modes

- Empty recall packet.
- Degraded recall packet with warning.
- Human decision required.
- Reinjection blocked if contamination risk is high.

### Upstream Dependencies

- Continuity.
- Reflection.
- Repo Understanding.

### Downstream Consumers

- Reinjection.
- Human Co-Creation.

### Public/Core Boundary

Core Recall may use public/Core state docs, current manifests, verified context outputs, and local continuity records.

### Private/Enterprise Exclusions

Core Recall must not include SCIA memory implementation, private vector stores, private long-term memory services, Enterprise team memory, private audit chain content, or SION internals.

## 5. Reinjection Contract

### Purpose

Reinjection transforms approved recall, reflection, continuity, and repo-understanding outputs into bounded assistant-facing context. Reinjection prevents hallucination and context bleed without flooding standing instruction files.

### Inputs

- Recall packet.
- Manifest summary.
- Reflection warnings.
- Continuity state.
- Workcell scope.
- Token budget or context budget.
- Assistant target type.

### Outputs

- Context packet.
- MCP response.
- Compact standing instruction update only when approved.
- Drift warning injection.
- Boundary reminder.

### Required Guarantees

- Generated symbol maps and full repo intelligence belong in manifests/context outputs, not standing instruction files.
- Standing instructions must remain compact.
- Reinjection must obey token discipline.
- Reinjection must not mutate source files.
- Reinjection must not include excluded paths, secrets, private implementation, or unrelated project context.
- Context packets must identify source freshness.

### Refusal Conditions

- Refuse to inject context from unknown or stale state without warning.
- Refuse to inject private/Enterprise implementation into Core context.
- Refuse to overwrite human-authored standing instruction content outside approved managed sections.
- Refuse repo-wide context when a bounded packet is sufficient.

### Freshness Rules

- Fresh when generated from current manifest, current seed/build state, and current recall packet.
- Stale when manifest or continuity state changed.
- Degraded when token budget forces omission of relevant material.
- Unknown when source lineage is missing.

### Trust Metadata

- `context_packet_id`
- `generated_at`
- `source_manifest_hash`
- `recall_packet_id`
- `token_budget`
- `omitted_sections`
- `freshness_state`
- `contamination_check`

### Failure / Degraded Modes

- Context packet withheld.
- Minimal boundary-only packet.
- Token-trimmed degraded packet.
- Human review required.

### Upstream Dependencies

- Recall.
- Reflection.
- Continuity.
- Repo Understanding.

### Downstream Consumers

- Assistant Interface.
- Context Isolation.
- Human Co-Creation.

### Public/Core Boundary

MCP context serving, compact assistant guidance, context packets, and bounded reinjection belong in Core.

### Private/Enterprise Exclusions

Core Reinjection must not expose private memory, private security, private signing implementation, SION internals, Runtime Law, private audit ledger, or Enterprise backend context.

## 6. Context Isolation Contract

### Purpose

Context Isolation defines the local workcell boundary for a seed/build task. It determines allowed reads, allowed writes, forbidden paths, and contamination rules. FileCell is a local containment concept, not Enterprise-only.

### Inputs

- Repo sandbox contract.
- Manifest and dependency map.
- Seed/build scope.
- Reinjection context packet.
- Proposed target files.
- Exclusion rules.

### Outputs

- Workcell or FileCell boundary.
- Allowed read paths.
- Allowed write paths.
- Forbidden paths.
- Boundary derivation explanation.
- Scope degradation warning.

### Required Guarantees

- No cross-project bleed.
- No raw repo-wide access beyond the sandbox contract.
- Allowed writes must be minimal and task-specific.
- Forbidden paths must override all other permissions.
- Workcell boundaries must fail closed if derivation is uncertain.
- Context Isolation must not be treated as private execution authority.

### Refusal Conditions

- Refuse access outside the registered repo sandbox.
- Refuse writes to forbidden paths.
- Refuse ambiguous cross-project scope.
- Refuse to derive a write boundary from stale manifest facts without warning.
- Refuse private execution lease authority in public Core.

### Freshness Rules

- Fresh when derived from current manifest and current seed/build scope.
- Stale when repo structure changed after derivation.
- Degraded when dependencies are incomplete or parser coverage is partial.
- Unknown when no valid sandbox or manifest exists.

### Trust Metadata

- `workcell_id`
- `sandbox_id`
- `source_manifest_hash`
- `allowed_reads`
- `allowed_writes`
- `forbidden_paths`
- `derivation_confidence`
- `freshness_state`

### Failure / Degraded Modes

- Read-only workcell.
- Boundary derivation blocked.
- Human review required.
- Verification blocked until boundary is resolved.

### Upstream Dependencies

- Repo Understanding.
- Continuity.
- Reinjection.

### Downstream Consumers

- Verification.
- Human Co-Creation.
- Constellation.

### Public/Core Boundary

Repo sandboxing, FileCell/workcell derivation, allowed/forbidden path metadata, and fail-closed containment belong in Core/Pro candidates.

### Private/Enterprise Exclusions

Core Context Isolation must not include SION authority, Runtime Law, execution leases, private audit ledger enforcement, signing queues, private rollback authority, or Enterprise runtime controls.

## 7. Verification Contract

### Purpose

Verification compares intended change evidence against observed repo state. It distinguishes verified from unverified, identifies scope violations, triggers re-index events, and prepares human review evidence. Verification does not own merge authority or private rollback execution in Core.

### Inputs

- Change proposal or intended change description.
- Workcell boundary.
- Pre-change hashes.
- Post-change hashes.
- Manifest before and after change.
- Diff summary.
- Continuity state.

### Outputs

- Verification result: passed, failed, partial, scope-exceeded, or unknown.
- Evidence bundle.
- Re-index trigger.
- Human review signal.
- Trust metadata update.

### Required Guarantees

- Verification must compare declared scope against observed changes.
- Verification must label verified/unverified explicitly.
- Verification must detect changes outside the workcell when evidence is available.
- Verification must trigger or request re-index after accepted changes.
- Verification must preserve evidence for human review.

### Refusal Conditions

- Refuse to verify without a known workcell boundary.
- Refuse to pass verification if hashes, diff, or manifest basis are missing.
- Refuse to mark scope-exceeded work as acceptable.
- Refuse to trigger private rollback executor in Core.
- Refuse to sign or claim signature authority.

### Freshness Rules

- Fresh when post-change manifest is newer than the change and compared against pre-change basis.
- Stale when repo changed after verification.
- Degraded when only partial diff/hash evidence exists.
- Unknown when pre-change baseline is missing.

### Trust Metadata

- `verification_id`
- `proposal_id` or `change_id`
- `pre_manifest_hash`
- `post_manifest_hash`
- `workcell_id`
- `verdict`
- `evidence_refs`
- verified/unverified
- lineage present/missing

### Failure / Degraded Modes

- Failed verification.
- Partial verification.
- Scope exceeded.
- Unknown due to missing baseline.
- Human review required.

### Upstream Dependencies

- Repo Understanding.
- Continuity.
- Context Isolation.

### Downstream Consumers

- Human Co-Creation.
- Continuity.
- Trust Awareness.
- Constellation when cross-engine awareness is approved.

### Public/Core Boundary

Proposal checking, diff evidence, hash comparison, post-change comparison, and re-index triggers belong in Core/Pro candidates.

### Private/Enterprise Exclusions

Core Verification must not include private rollback executor, SION control, Runtime Law authorization, private audit chain, Seed Signature implementation, private keys, signing queues, or Enterprise execution backend.

## 8. Human Co-Creation Contract

### Purpose

Human Co-Creation owns human review, approval, rejection, revision, acceptance, and scope decisions. The PWA/dashboard is a human-operated cockpit for observability and review, not an autonomous controller.

### Inputs

- Seed/build state.
- Context packet.
- Reflection warnings.
- Workcell boundary.
- Verification evidence.
- Constellation status.
- Trust metadata.

### Outputs

- Approve.
- Reject.
- Revise.
- Return for revision.
- Accept completed work.
- Scope change request.
- Human note or decision record.

### Required Guarantees

- Approval gates must be explicit.
- Human decisions must feed Continuity as state transition evidence.
- PWA must not bypass workcell boundaries.
- PWA must not bypass verification.
- PWA must not directly mutate source in Core.
- Rejection/revision/acceptance semantics must be distinct.

### Refusal Conditions

- Refuse direct source mutation from cockpit controls.
- Refuse approval flow when verification evidence is missing for code-changing work.
- Refuse cross-workspace sharing without explicit human scope decision.
- Refuse to present private signing/audit implementation as Core capability.

### Freshness Rules

- Fresh when displayed state is tied to current manifest, continuity state, and verification evidence.
- Stale when local engine status or manifest has changed since display.
- Degraded when some live endpoints are unavailable.
- Unknown when engine identity or state lineage is missing.

### Trust Metadata

- `decision_id`
- `actor`
- `decision_type`
- `decided_at`
- `evidence_refs`
- `manifest_hash`
- verified/unverified
- approval present/missing

### Failure / Degraded Modes

- Read-only cockpit.
- Awaiting verification.
- Awaiting re-index.
- Awaiting human decision.
- Engine unavailable.

### Upstream Dependencies

- Reinjection.
- Context Isolation.
- Verification.
- Continuity.
- Trust Awareness.

### Downstream Consumers

- Continuity.
- Constellation.
- Repo Understanding through re-index requests.

### Public/Core Boundary

Dashboard/PWA observability, seed planting, blueprint review, edit direction, approve/reject, scope change request, drift warning response, status observation, accept/return semantics belong in Core.

### Private/Enterprise Exclusions

Core Human Co-Creation must not include autonomous execution controller posture, Enterprise backend implementation, team/cloud/SSO/Slack backend, private approval authorities, SION control, Runtime Law, or private signing actions.

## 9. Constellation Contract

### Purpose

Constellation coordinates awareness across independent SRT-1 engines without merging contexts by default. It maps engines, ports, health, and approved summaries while preventing contamination between workspaces.

### Inputs

- Per-engine registry.
- Per-port map.
- Engine health/status endpoint.
- Manifest summary or approved architecture digest.
- Human-approved sharing rules.
- Workcell/context isolation status.

### Outputs

- Peer map.
- Engine health report.
- Dependency awareness.
- Stale/degraded peer warnings.
- Approved cross-module summary.

### Required Guarantees

- Engines remain independent.
- No shared context by default.
- No cross-project read/write authority.
- Per-engine identity and port must be explicit.
- Stale peers must not silently feed context.
- Cross-module awareness must be summary-first unless explicitly approved.

### Refusal Conditions

- Refuse to ingest raw source from peer engines by default.
- Refuse to share context without human-approved boundary.
- Refuse to merge manifests into one global context by default.
- Refuse to coordinate writes across workspaces in Core.

### Freshness Rules

- Fresh when peer health and manifest summary are current.
- Stale when peer heartbeat or manifest timestamp exceeds threshold.
- Degraded when peer is reachable but lacks verified summary.
- Unknown when peer identity cannot be verified.

### Trust Metadata

- `constellation_id`
- `engine_id`
- `port`
- `health_state`
- `manifest_hash`
- `sharing_permission`
- official/unofficial
- freshness_state

### Failure / Degraded Modes

- Peer omitted.
- Peer marked stale.
- Summary-only mode.
- Human approval required.
- Constellation read-only mode.

### Upstream Dependencies

- Repo Understanding.
- Context Isolation.
- Human Co-Creation.
- Trust Awareness.

### Downstream Consumers

- Human Co-Creation.
- Reinjection when explicitly approved.
- Reflection for cross-module drift warnings.

### Public/Core Boundary

Local engine awareness, per-port map, health/status visibility, independent federation, and approved summary coordination belong in Pro/Core-aware surfaces.

### Private/Enterprise Exclusions

Core/Pro Constellation must not include shared private memory, Enterprise team backend, cloud orchestration, unapproved raw source sharing, SION cross-engine execution, or private audit/signing implementation.

## 10. Trust Awareness Contract

### Purpose

Trust Awareness provides public Core vocabulary and metadata for artifact integrity and lineage. It tracks whether artifacts are signed or unsigned, verified or unverified, lineage present or missing, official or unofficial. It does not implement private signing authority in Core.

### Inputs

- Manifest metadata.
- Continuity transitions.
- Reflection findings.
- Recall/context packet metadata.
- Workcell boundaries.
- Verification evidence.
- Human decisions.
- Constellation peer identity.

### Outputs

- Trust labels.
- Lineage state.
- Freshness state.
- Official/unofficial marker.
- Fail-closed warning.

### Required Guarantees

- Core must operate without private signing service.
- Unsigned is a valid state, not a crash condition.
- Missing lineage must be explicit.
- Verified/unverified must not be conflated with signed/unsigned.
- Trust Awareness must fail closed when private authority is unavailable.
- Seed Signature is preserved as trust vocabulary only in public Core.

### Refusal Conditions

- Refuse to claim an artifact is signed without external proof.
- Refuse to expose private keys, signing queues, private audit chain, or signing service implementation.
- Refuse to treat private audit ledger as required Core infrastructure.
- Refuse to promote unsigned/unverified artifacts to official verified state.

### Freshness Rules

- Fresh when trust metadata references current artifact hashes and current state transitions.
- Stale when artifact changed after trust metadata was produced.
- Degraded when only partial lineage is available.
- Unknown when artifact origin is missing.

### Trust Metadata

- signed/unsigned
- verified/unverified
- lineage present/missing
- official/unofficial
- fresh/stale/degraded/unknown
- authority unavailable/available
- external signature reference if present

### Failure / Degraded Modes

- Unsigned but usable.
- Unverified and blocked from acceptance.
- Lineage missing and human review required.
- External authority unavailable and fail-closed.
- Trust state unknown.

### Upstream Dependencies

- All authorities emit trust-relevant metadata.

### Downstream Consumers

- All authorities consume trust state where artifact integrity, approval, verification, lineage, or execution history matters.

### Public/Core Boundary

Trust states, integrity metadata, lineage vocabulary, freshness labels, and fail-closed behavior belong in Core.

### Private/Enterprise Exclusions

Seed Signature implementation, private keys, signing service, private audit chain, SCIA security implementation, signing queues, private ledger, and Enterprise trust backend stay outside public Core.

## Public/Core Boundary Doctrine

Public Core includes:

- Local repo understanding.
- File hashing.
- Parser coverage.
- Symbol and dependency maps.
- Manifest generation as output.
- Seed/build continuity.
- Reflection and drift detection.
- Recall from public/Core state.
- Bounded reinjection and MCP context serving.
- FileCell/workcell as local containment concept.
- Proposal/diff verification and re-index triggers.
- Human cockpit for review and approval.
- Local constellation awareness without shared context by default.
- Trust state vocabulary and fail-closed metadata.

Public Core must remain useful without private services. Optional integrations may exist as hooks or contracts only when they fail closed and do not expose private implementation.

## Private/Enterprise Exclusion Doctrine

The following are not public Core:

- Private Seed Signature authority implementation.
- Private keys.
- Signing service implementation.
- Signing queues.
- Private audit chain or private ledger implementation.
- SCIA memory implementation.
- SCIA security implementation.
- SION internals.
- Runtime Law.
- Execution lease authority implementation.
- Private rollback executor.
- Enterprise backend.
- Team/cloud/SSO/Slack backend.
- Enterprise dashboards or processes exposing private flow.

Concepts allowed in public Core only as abstract vocabulary or fail-closed hooks:

- signed/unsigned
- verified/unverified
- lineage present/missing
- official/unofficial
- external signing authority unavailable
- private backend unavailable

## Open Questions / NEEDS_SOURCE

- What is the canonical storage location for public Core manifests and generated context packets?
- What is the canonical schema for manifest freshness?
- What is the minimal public seed lifecycle schema?
- Which current seed states are canonical: active, pending, completed, terminated, wilted, returned, or others?
- What is the exact public distinction between build plan state and seed state?
- What confidence labels should Reflection use?
- What public sources are eligible for Recall?
- What token budget defaults should Reinjection enforce?
- Should `AGENTS.md` and `CLAUDE.md` ever contain managed SRT-1 sections, or only pointers to generated context outputs?
- What is the public workcell/FileCell schema after removing private execution authority?
- What is the public proposal/diff schema after removing SION/Runtime Law?
- What event vocabulary should Core keep without implying private audit ledger implementation?
- What is the canonical Constellation registry format?
- What trust metadata fields should be required on every artifact?
- Which PWA controls are purely observational versus state-transition controls?

## Batch 4 Code-Audit Criteria

Batch 4 code audits should measure implementation against these contracts, not against folder names.

### Repo Understanding Audit Criteria

- Does the code distinguish source authority from generated manifest output?
- Does it label parser coverage and dependency fidelity?
- Does it exclude private/local/generated paths consistently?
- Does it own symbol and dependency truth without leaking into Reinjection?
- Does manifest signing remain optional/fail-closed and external?

### Continuity Audit Criteria

- Are seed/build lifecycle states explicit?
- Are partial completion and returned/wilted states represented?
- Are transitions owned by Continuity rather than Reflection or PWA?
- Is state tied to manifest freshness?

### Reflection Audit Criteria

- Does Reflection stay detective-only?
- Are confidence and evidence represented?
- Are doctrine mismatches source-linked?
- Is autonomous remediation absent from Core behavior?

### Recall Audit Criteria

- Is Recall first-class rather than incidental context bundling?
- Are public/Core sources separated from private memory?
- Are stale/degraded/unknown states represented?

### Reinjection Audit Criteria

- Are generated repo maps kept out of standing instruction bloat?
- Are context packets bounded and token-aware?
- Are excluded/private paths prevented from injection?
- Does MCP/context serving report freshness?

### Context Isolation Audit Criteria

- Are allowed/forbidden paths explicit?
- Does FileCell/workcell derivation fail closed?
- Is it decoupled from SION, Runtime Law, private ledger, private signing, and Enterprise runtime?

### Verification Audit Criteria

- Does verification compare intended vs actual evidence?
- Does it distinguish verified, unverified, partial, failed, and scope-exceeded?
- Does it trigger or require re-index after accepted changes?
- Is private rollback/signing excluded from Core?

### Human Co-Creation Audit Criteria

- Does PWA act as cockpit rather than autonomous controller?
- Are approve/reject/revise/accept states explicit?
- Are verification and workcell gates preserved?

### Constellation Audit Criteria

- Are engines independent?
- Is registry/port/health state explicit?
- Is shared context disabled by default?
- Is human approval required for cross-workspace context?

### Trust Awareness Audit Criteria

- Are signed/unsigned, verified/unverified, lineage present/missing, official/unofficial represented?
- Does Core fail closed when private authority is unavailable?
- Are private signing/audit implementations excluded?
