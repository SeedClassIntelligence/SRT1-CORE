# Audit Event Contract

**Contract ID:** `SRT1-CONTRACT-AUDIT-001`
**Between:** SRT-1 Authorities and Trust Awareness
**Status:** Public Core vocabulary, private signing external

## Purpose

Define the event/trust metadata SRT-1 records for repository understanding,
continuity, WorkCells, verification, human decisions, and Seed Signature
attachment. Events provide traceability and attribution evidence; they do not
embed private signing infrastructure.

## Event Fields

```yaml
event_id: string
component: string
operation: string
severity: info | warning | high | critical
actor: string
queue_seed_id: string | null
srt_anchor_id: string | null
workcell_id: string | null
filecell_id: string | null
manifest_hash: string | null
trust_state: signed | unsigned | verified | unverified | degraded | unknown
signature_id: string | null
certificate_url: string | null
result_status: success | failure | blocked | degraded | unknown
detail: object
created_at: datetime
event_hash: string | null
previous_event_hash: string | null
```

## Guarantees

- Seed-scoped events preserve `queue_seed_id`.
- Reflection-scoped events may preserve `srt_anchor_id`.
- WorkCell/FileCell events preserve boundary identity.
- Trust state is visible and never implied.
- Signature-required artifacts are signed, marked unsigned, or blocked.
- Public Core stores returned Seed Signature metadata only.

## Seed Signature Boundary

SRT-1 may let the user create or attach a Seed Signature from the dashboard.
Seed Signature signs externally and returns public metadata such as
`signature_id` and `certificate_url`. SRT-1 does not ship private keys, private
signing service, private audit chain internals, or Seed Signature platform code.

## Refusal Conditions

- Required attribution metadata is missing and enforcement is required.
- Event would expose secrets, keys, private signing records, or private audit
  internals.
- Execution actor or assistant attempts to mutate trust records directly.

## Events Covered

```text
repo_index_started
repo_index_completed
seed_planted
workcell_created
filecell_updated
context_packet_created
drift_warning_emitted
verification_passed
verification_failed
signature_attachment_requested
signature_attachment_completed
trust_state_updated
```
