# SRT1 WorkCell Runtime Contract

## Purpose

Define the public Core WorkCell runtime model.

SRT-1 should not ask assistants to rediscover the whole repository every time
work begins. Repository Understanding creates persistent FileCells. WorkCells
use those FileCells to create bounded execution environments for seeds,
assistant handoffs, verification, and human review.

## Canonical Model

```text
Repository Activation
-> Repo Understanding
-> Persistent FileCells
-> Default WorkCells
-> Seed activates WorkCell execution
-> Recall/Reinjection build context package
-> Assistant/developer operates inside boundary
-> Verification checks result
-> Human accepts, returns, rejects, or expands scope
-> Repo Understanding re-indexes accepted changes
```

## Terms

| Term | Meaning |
|---|---|
| Repository Activation | Register/select the local repo SRT-1 manages. |
| Repository Runtime | Local SRT-1 engine serving one repository. |
| FileCell | Persistent intelligence object for one file or tightly coupled file set. |
| WorkCell | Persistent bounded execution environment associated with a file by default. |
| WorkCell Execution | Temporary seed-driven activity inside a WorkCell. |
| WorkCell Package | Instructions, FileCells, recall packets, allowed paths, verification rules, and trust metadata. |
| `workcell.md` | Agent entry instructions for the active WorkCell. |

## Core Principles

- Every repository file should receive a persistent FileCell.
- Every repository file should receive a default WorkCell boundary.
- FileCells own repository intelligence.
- WorkCells own execution boundaries.
- Seeds activate WorkCell execution; they do not redefine repository truth.
- WorkCells expand only through dependency evidence or human approval.
- PWA is a human cockpit, not an autonomous mutation controller.
- Constellation shows independent runtimes without shared context by default.

## WorkCell Package Fields

```yaml
workcell_id: string
repo_root: path
primary_filecell_id: string
queue_seed_id: string | null
srt_anchor_id: string | null
objective: string
allowed_reads: list[path]
allowed_writes: list[path]
forbidden_paths: list[path]
related_filecells: list[string]
recall_packets: list[object]
verification_rules: list[string]
manifest_hash: string | null
freshness_state: fresh | stale | degraded | unknown
trust_state: signed | unsigned | verified | unverified | degraded | unknown
signature_id: string | null
runtime_port: integer | null
status: ready | active | blocked | returned | completed | degraded
```

## `workcell.md` Requirements

Each active WorkCell package should include concise agent instructions:

- objective
- scope
- allowed files
- forbidden files
- related FileCells
- relevant recall packets
- verification requirements
- completion requirements
- trust/signature state
- escalation rules

The file is an operating instruction package, not a full repository dump.

## Authority Ownership

| Responsibility | Owner |
|---|---|
| Manifest, hashes, symbols, dependencies | Repo Understanding |
| Seed lifecycle and queue identity | Continuity |
| Drift and coherence findings | Reflection |
| Recall packets | Recall |
| Context/workcell instruction delivery | Reinjection |
| Allowed/forbidden paths | Context Isolation |
| Evidence and verdicts | Verification |
| Approval, return, rejection, acceptance | Human Co-Creation |
| Runtime/port federation | Constellation |
| Signed/unsigned and lineage metadata | Trust Awareness |

## Runtime States

```text
created
-> ready
-> active
-> awaiting_review
-> completed
```

Alternative paths:

```text
ready -> blocked
active -> returned
active -> partial
active -> degraded
awaiting_review -> returned
awaiting_review -> completed
```

## Seed Signature Boundary

WorkCells may require Seed Signature attribution. SRT-1 may let the user create
or attach that signature from the dashboard. The standalone Seed Signature
platform performs signing and returns public metadata. Public Core stores and
enforces trust metadata; it does not ship private signing code.

## Refusal Conditions

A WorkCell package should fail closed or mark degraded when:

- repository is not registered
- manifest freshness is unknown and scope requires fresh data
- requested path crosses repository boundary
- forbidden/private path would be included
- required FileCell evidence is missing
- required Seed Signature attribution is missing
- verification evidence is unavailable for completion

## Dashboard Contract

The dashboard should show repositories first, then WorkCells. For each WorkCell,
the cockpit should expose:

- objective
- runtime status
- assigned assistant/adapter
- package readiness
- `workcell.md` preview
- FileCells attached
- allowed and forbidden paths
- recall/degradation state
- verification progress
- trust/signature status
- stop/cleanup controls for launched runtimes

## Public Core Boundary

Public Core includes WorkCell/FileCell concepts, package generation, local
runtime state, dashboard visibility, verification metadata, and external Seed
Signature attachment metadata.

Public Core does not ship Enterprise backend implementation, private signing
authority, private keys, private audit chain, SION internals, SCIA memory or
security implementation, or private execution backends.
