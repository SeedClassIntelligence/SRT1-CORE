# Audit Event Emission Skill

> **Skill ID:** `SRT1-SKILL-009`
> **Module:** Event Log + Tracing
> **Authority:** Trust Awareness / Continuity
> **Classification:** Public Core vocabulary, private signing external
> **Mutates Source:** Never

## Purpose

Audit Event Emission records traceable lifecycle, verification, boundary, and
trust metadata events for SRT-1. It gives the platform an evidence trail for
what happened, when it happened, which seed or WorkCell it belonged to, and
whether attribution/trust metadata was present.

Public Core may keep local event records and hash/integrity metadata. Seed
Signature creation, certificate issuance, private keys, and private signing
records remain owned by the standalone Seed Signature platform.

## Activation

| Trigger | Source | Frequency |
|---|---|---|
| Lifecycle transition | Continuity / seed queue | Per state transition |
| Repository index event | Repo Understanding | Per index/re-index milestone |
| Boundary violation | Context Isolation | Per blocked attempt |
| Verification result | Verification | Per verification verdict |
| Seed Signature request | Dashboard/backend widget session flow | On create/attach request |
| Trust metadata update | Seed Signature callback / external result | On completion |

## Preconditions

- Local event/tracing store is initialized or degradation is explicit.
- Event includes component, operation, actor, result status, and timestamp.
- Seed-scoped events include `queue_seed_id` when available.
- WorkCell-scoped events include WorkCell/FileCell identifiers when available.
- Signature-required events know whether Seed Signature metadata is present,
  missing, unavailable, or not required.

## Inputs

| Input | Type | Meaning |
|---|---|---|
| `component` | String | System component emitting event |
| `operation` | String | Event/action name |
| `severity` | String | info, warning, high, critical |
| `actor` | String | user, engine, assistant, verifier, etc. |
| `queue_seed_id` | String/null | Canonical continuity identity |
| `srt_anchor_id` | String/null | Reflection/coherence metadata |
| `workcell_id` | String/null | WorkCell identity |
| `manifest_hash` | String/null | Repo Understanding freshness/integrity |
| `trust_state` | String | signed, unsigned, verified, unverified, degraded, unknown |
| `detail` | Dict | Event-specific payload |

## Outputs

| Output | Type | Destination |
|---|---|---|
| Local event record | Dict/row | SRT-1 local state |
| Event hash/integrity metadata | String | Event record |
| Signature eligibility metadata | Dict | Trust metadata |
| Seed Signature request metadata | Dict | External widget/session flow |
| Dashboard trust state | Dict | Human observability surface |

## Runtime Responsibilities

1. Record lifecycle, verification, boundary, and trust events.
2. Preserve canonical identity metadata across events.
3. Mark events/artifacts as signed, unsigned, verified, unverified, degraded, or
   unknown.
4. Identify signature-required or signature-eligible events.
5. Support Seed Signature create/attach flow by storing returned public metadata.
6. Fail closed or label unsigned/unverified when required attribution is missing.
7. Keep private signing authority outside public Core.

## Seed Signature Boundary

SRT-1 may let a developer create or attach a Seed Signature from the dashboard.
The safe integration path is:

```text
SRT-1 backend requests short-lived session token
-> dashboard opens Seed Signature widget
-> Seed Signature signs externally
-> SRT-1 stores signatureId/certificateUrl/trust metadata
```

SRT-1 Core must not ship:

- private Seed Signature authority
- private keys
- private signing service
- private signing records
- private audit chain internals
- Seed Signature platform implementation code

## Boundary Rules

| Rule | Enforcement |
|---|---|
| Append-only intent | Events represent history and should not be silently rewritten |
| Execution actor isolation | Execution actors cannot directly mutate event/trust records |
| Public metadata only | Core stores returned trust metadata, not private signing records |
| Attribution enforcement | Required signature metadata must be present or visibly missing |
| No auto-signing claim | Core may request/attach signatures; Seed Signature signs externally |

## Verification

| Check | Success condition |
|---|---|
| Event persisted | Event record exists or degraded reason is explicit |
| Identity preserved | Seed/WorkCell/manifest metadata survives |
| Trust state clear | signed/unsigned/verified/unverified/degraded/unknown is visible |
| Required signature enforced | Missing required attribution fails closed or labels unsigned |
| Private data absent | No private keys, secrets, or signing implementation records stored |

Failure indicators include silent event loss, missing `queue_seed_id` on
seed-scoped events, private signing data in Core, unsigned governed output
presented as signed, or execution actor control over trust records.

## Events

| Event | Severity | Status |
|---|---|---|
| `audit_export_generation` | warning | exists/planned depending on runtime path |
| `signature_attachment_requested` | warning/info | planned |
| `signature_attachment_completed` | info | planned |
| `signature_attachment_unavailable` | warning | planned |
| `trust_state_updated` | info | planned |
| `event_chain_verification_failed` | critical | planned |

## Source of Truth

- `srt1_platform/tracing_system.py`
- local SRT-1 event/tracing state
- Seed Signature widget integration contract
- returned Seed Signature public metadata
