# SRT-1 Native Execution Runtime

## Purpose

SRT-1 will incorporate Codex-derived local code-agent capability as a native execution runtime inside the platform.

This is not a Codex adapter, plugin, or user-facing integration. The product promise is:

> SRT-1 executes work through bounded WorkCells.

Codex-derived capability supplies local coding-agent mechanics: reading scoped context, editing files, generating patches, running commands, executing tests, and reporting results. SRT-1 supplies the mission, continuity, WorkCell boundary, FileCell scope, verification, review, conversation, and owner authority.

## Product Position

The owner should not think:

```text
I am using Codex inside SRT-1.
```

The owner should think:

```text
SRT-1 can build, inspect, test, and review work inside my projects.
```

Any Codex-derived implementation is internal platform machinery. In the Standard Experience, SRT-1 speaks in owner-facing language:

```text
SRT-1 is working on authentication.
SRT-1 updated three files.
SRT-1 ran the test suite.
One issue is ready for review.
```

The Control Room may expose deeper execution details when explicitly requested, but the default product surface remains conversational.

## Authority Model

SRT-1 remains the authority over:

- owner intent
- project and mission state
- continuity and recall
- Seed creation
- WorkCell creation and lifecycle
- FileCell boundaries
- allowed and forbidden paths
- execution state
- verification evidence
- review decisions
- audit events
- owner-facing conversation

The native execution runtime is allowed to:

- read the WorkCell package it was given
- inspect allowed files
- propose edits inside allowed paths
- run approved commands
- run configured tests
- summarize work performed
- return structured execution evidence

The native execution runtime is forbidden to:

- create work outside a WorkCell
- broaden file scope because nearby files look useful
- mutate files outside allowed FileCell paths
- silently apply changes without SRT-1 recording them
- mark work complete without verification evidence
- bypass human review when review is required
- persist provider secrets
- change SRT-1 mission, memory, or authority state directly
- expose backend machinery as Standard Experience UI

## Core Execution Flow

```text
Owner says what they want
  -> SRT-1 classifies the intention
  -> SRT-1 creates or selects a Mission
  -> SRT-1 creates or selects a WorkCell
  -> SRT-1 generates a bounded execution package
  -> Native Execution Runtime performs scoped work
  -> Runtime returns proposed changes and evidence
  -> SRT-1 validates write boundaries
  -> SRT-1 runs or records verification
  -> SRT-1 creates review state when needed
  -> SRT-1 explains outcome conversationally
```

No execution begins without a WorkCell.

No completion is trusted without evidence.

No user-facing state is updated without SRT-1 recording the event.

## WorkCell Execution Package

Every native execution job receives a structured package:

```text
workcell.md
workspace.json
filecells.json
runtime_state.json
conversation.json
acceptance_criteria.json
verification_contract.json
forbidden_paths.json
```

The package must answer:

- what the owner asked for
- why this WorkCell exists
- which files are allowed
- which files are forbidden
- what context matters
- what has already happened
- what tests or checks prove success
- how to report completion
- how to report a blocker

The package must not include secrets, unrelated repository sprawl, or raw backend clutter that is not needed to execute the objective.

## Native Runtime Interface

The SRT-1 native execution layer should expose an internal interface shaped like this:

```text
create_execution(workcell_package) -> execution_id
start(execution_id) -> accepted | blocked
status(execution_id) -> queued | running | blocked | completed | failed | cancelled
cancel(execution_id) -> cancellation_record
collect_result(execution_id) -> execution_result
```

The interface is native to SRT-1. It should not be named or presented as an adapter in product surfaces.

Possible internal names:

```text
SRT1NativeExecutionRuntime
WorkCellExecutionRuntime
SRT1BuildRuntime
SRT1LocalExecutionCore
```

Avoid product-facing names such as:

```text
Codex Adapter
Codex Plugin
Connect Codex
Run Codex
```

## Execution Result Contract

The runtime returns structured evidence:

```json
{
  "execution_id": "exec_...",
  "queue_seed_id": "seed_...",
  "status": "completed",
  "summary": "Implemented the requested upload flow fix.",
  "files_read": [],
  "files_changed": [],
  "commands_run": [],
  "tests_run": [],
  "verification_evidence": [],
  "proposed_changes": [],
  "blockers": [],
  "risks": [],
  "next_recommendation": ""
}
```

SRT-1 validates this result before it enters review or completion state.

## Change Application Rule

The native runtime may produce patches, but SRT-1 decides whether those patches become repository truth.

The required order is:

```text
runtime proposes change
  -> SRT-1 validates path scope
  -> SRT-1 records proposal
  -> SRT-1 runs verification
  -> SRT-1 asks for review when required
  -> approved change becomes accepted work
```

The runtime must not directly bypass `ChangeProposal`, `WorkCellRegistry`, or verification surfaces.

## Model Layer

The runtime should support multiple model sources:

- OpenAI API models
- open-weight models such as `gpt-oss`
- local runtimes
- OpenAI-compatible providers
- future SRT-1-owned model providers

The model is not the product authority.

The model is a reasoning and code-generation component under SRT-1 governance.

Secrets and provider keys must remain transient, environment-backed, or vault-backed. They must not be committed, persisted in public Core state, or written into WorkCell packages.

## Standard Experience Behavior

The Standard Experience must never expose this runtime as backend machinery by default.

The owner says:

```text
Fix this bug.
Continue authentication.
Explain this module.
Run the tests.
Review what changed.
```

SRT-1 responds:

```text
I created a bounded work unit for that.
I am working inside the authentication files.
The implementation is complete.
The tests passed.
One review is waiting.
```

If the owner asks to inspect:

```text
Show the WorkCell.
Show verification.
Show the logs.
Open Control Room.
```

Then SRT-1 may reveal runtime details through Advanced or Control Room surfaces.

## Control Room Behavior

Control Room may show:

- execution id
- WorkCell id
- active state
- files in scope
- commands run
- tests run
- proposals
- verification evidence
- runtime logs
- cancellation or pause state

Control Room should make machinery inspectable, not mandatory.

## Incorporation Strategy

The correct implementation strategy is:

1. Study the open-source Codex CLI execution loop.
2. Identify reusable concepts:
   - local repo inspection
   - patch planning
   - command execution
   - approval modes
   - sandboxing
   - diff review
   - structured task loop
3. Rebuild or vendor only what SRT-1 needs.
4. Wrap every capability in WorkCell authority.
5. Rename the product surface to SRT-1 native execution language.
6. Keep license notices and attribution where required.
7. Add tests proving execution cannot escape WorkCell scope.

Do not copy the Codex product identity into SRT-1.

Do not let external execution assumptions weaken SRT-1 boundaries.

## Implementation Phases

### Phase 1: Specification And Boundary

- define native runtime interface
- define execution result schema
- define WorkCell package contract
- define forbidden operations
- write tests for scope enforcement

### Phase 2: Local Handoff Runtime

- generate execution packages
- create execution folders
- write request and result files
- support manual/local runner execution
- record result into WorkCell activity

### Phase 3: Subprocess Runtime

- invoke a local code-agent binary or SRT-1-owned runner
- pass only WorkCell package path and approved settings
- capture stdout, stderr, exit code, diff, and test evidence
- fail closed on timeout, path escape, or missing result contract

### Phase 4: Native Embedded Runtime

- incorporate selected Codex-derived execution-loop components
- use SRT-1's own WorkCell/FileCell APIs as the execution boundary
- support open-weight or OpenAI-compatible models
- keep review and verification under SRT-1

### Phase 5: Conversation-First Product Surface

- surface execution state inside the Standard Experience thread
- show only owner-relevant summaries
- route inspection to Control Room on request
- preserve SRT-1 continuity messaging:

```text
Bring the idea once. SRT-1 keeps the assistant on task and carries the work to completion.
```

## Acceptance Criteria

The native execution runtime is acceptable only when:

- SRT-1 can execute a WorkCell without exposing Codex as a product surface.
- No execution can begin outside a WorkCell.
- No write can escape FileCell scope.
- Every change is recorded.
- Every completion has verification evidence or an explicit missing-evidence state.
- The Standard Experience remains conversational.
- Control Room remains available for inspection.
- Secrets are not persisted.
- Open-source license obligations are preserved.
- The owner can ask SRT-1 to build, test, inspect, review, pause, resume, or explain work without knowing the underlying runtime.

## CTO Decision

The strategic decision is:

```text
Codex-derived capability becomes part of SRT-1's native execution core.
SRT-1 remains the mission operating system.
WorkCells remain the authority boundary.
The user collaborates with SRT-1, not with the execution machinery.
```
