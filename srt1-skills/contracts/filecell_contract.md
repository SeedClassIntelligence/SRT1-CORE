# FileCell Contract

**Contract ID:** `SRT1-CONTRACT-FILECELL-001`
**Between:** Repository Understanding, Context Isolation, and WorkCell Runtime
**Status:** Public Core / Pro Candidate

## Purpose

Define the persistent intelligence object for a repository file or tightly
coupled file set. A FileCell stores what SRT-1 knows about that file. A WorkCell
uses one or more FileCells as its bounded execution package.

## FileCell Fields

```yaml
filecell_id: string
repo_root: path
file_path: path
content_hash: string
language: string
symbols: list[object]
imports: list[string]
exports: list[string]
dependencies: list[path]
contracts: list[string]
authority_metadata: list[string]
architectural_role: string | null
ownership: string | null
verification_status: string
trust_state: string
last_indexed_at: datetime
freshness_state: fresh | stale | degraded | unknown
```

## Guarantees

- FileCell intelligence is derived from registered repository understanding.
- FileCells are persistent repository knowledge objects, not temporary context
  windows.
- File changes update FileCells rather than forcing assistants to rediscover
  the whole repository.
- WorkCells consume selected FileCells; they do not own repository truth.
- Forbidden paths and secrets never become FileCells.

## WorkCell Relationship

```text
Repository Understanding
-> FileCells
-> WorkCell package
-> assistant/developer action
-> Verification
-> updated FileCells
```

By default, one repository file receives one FileCell and one default WorkCell
execution boundary. Additional FileCells are attached only through dependency
evidence or explicit human approval.

## Refusal Conditions

- File path is outside the registered sandbox.
- File path matches forbidden path rules.
- File cannot be parsed and no degraded metadata can be produced.
- WorkCell requests access to a FileCell without scope evidence or approval.

## Events

```text
filecell_created
filecell_updated
filecell_stale
filecell_attached_to_workcell
filecell_boundary_violation
```
