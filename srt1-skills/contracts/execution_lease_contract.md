# Execution Lease Contract

**Contract ID:** `SRT1-CONTRACT-EXECLEASE-001`
**Between:** WorkCell Runtime and Assistant/Developer Execution
**Status:** Public Core / Pro Candidate

## Purpose

Define a temporary, bounded permission window for a governed assistant or
developer action inside a WorkCell. The lease is a scope/time contract, not a
private credential and not a signing authority.

## Contract Fields

```yaml
lease_id: string
proposal_id: string | null
queue_seed_id: string
workcell_id: string
repo_root: path
granted_to: string
granted_at: datetime
expires_at: datetime
authorized_operations: list[read | create | modify | delete | rename | test]
allowed_reads: list[path]
allowed_writes: list[path]
forbidden_paths: list[path]
status: pending | active | consumed | expired | revoked | violated
trust_required: boolean
signature_id: string | null
```

## Guarantees

- Lease scope cannot exceed the WorkCell/FileCell boundary.
- Lease expiry is visible and enforced by the orchestrating runtime.
- A lease cannot authorize forbidden paths.
- A lease does not grant cross-repository or cross-runtime authority.
- A lease does not replace verification or human acceptance.
- Missing required Seed Signature metadata causes fail-closed or unsigned state.

## Public Core Boundary

Public Core may model and display execution leases, and may enforce lease
boundaries where it controls the workflow. Private execution backends, private
agent runtimes, SION internals, and private rollback executors are not shipped
in Core.

## Refusal Conditions

- No active WorkCell exists.
- Lease scope exceeds allowed WorkCell/FileCell paths.
- Lease requests forbidden/private paths.
- Lease requires attribution but no Seed Signature metadata is available.
- Lease is expired, revoked, or violated.

## Events

```text
execution_lease_created
execution_lease_activated
execution_lease_consumed
execution_lease_expired
execution_lease_revoked
execution_lease_violated
```
