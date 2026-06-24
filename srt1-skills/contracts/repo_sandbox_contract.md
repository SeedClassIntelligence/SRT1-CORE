# Repo Sandbox Contract
**Contract ID:** `SRT1-CONTRACT-SANDBOX-001`
**Between:** Repo Folder ↔ SRT-1 Engine
**Version:** 1.0.0
**Status:** CANONICAL

---

## Doctrine
SRT-1 sees. SRT-1 does not mutate source.
This contract defines exactly what SRT-1 is allowed to observe about a repo sandbox,
and what identity it assigns that sandbox in the registry.

---

## Purpose
Establish a bounded, observable sandbox around a repository or module.
Every repo SRT-1 tracks must have one active Repo Sandbox Contract.
No indexing, scanning, or context injection may occur outside a registered sandbox.

---

## Parties

| Party | Role |
|-------|------|
| **Repo Folder** | The filesystem root being observed. Read-only to SRT-1. |
| **SRT-1 Engine** | The observer. Reads, indexes, injects context, detects drift. Never mutates. |

---

## Contract Fields

```yaml
sandbox_id: string              # Unique ID for this sandbox. Format: SBX-{repo_slug}-{timestamp}
repo_root: path                 # Absolute path to repo root. SRT-1 reads from here only.
repo_slug: string               # Human-readable repo identifier (e.g., "seedlink-engine")
registry_entry: string          # Key under which this sandbox is registered in SRT-1 state
port: integer | null            # Dev server port if applicable. Null if not a running service.
state: enum                     # ACTIVE | SUSPENDED | ARCHIVED | ERROR
index_depth: integer            # How many directory levels deep SRT-1 indexes (default: 5)
excluded_paths: list[path]      # Paths SRT-1 will never read (node_modules, .env, secrets)
scan_triggers: list[enum]       # MANUAL | FILE_CHANGE | SEED_INTAKE | SCHEDULED
created_at: datetime
last_indexed_at: datetime | null
constellation_member: boolean   # Whether this sandbox is part of a multi-repo Constellation
constellation_id: string | null # Parent Constellation ID if applicable
```

---

## Obligations

### SRT-1 Engine SHALL:
- Register the sandbox in its internal registry before any indexing begins
- Respect `excluded_paths` absolutely — no reads, no scans, no references
- Emit `repo_sandbox_registered` event on creation
- Emit `repo_index_started` and `repo_index_completed` on each scan
- Set state to `ERROR` and halt if repo root is inaccessible
- Re-validate the contract on each `scan_trigger` before proceeding

### SRT-1 Engine SHALL NOT:
- Write to any file within `repo_root`
- Delete any file within `repo_root`
- Execute code within `repo_root`
- Pass repo root write access to any other component (execution actor receives FileCell boundaries, not raw paths)

### Repo Folder SHALL:
- Remain accessible at `repo_root` while contract is ACTIVE
- Provide consistent filesystem structure between scans
- Not remove `excluded_paths` entries without contract amendment

---

## Failure Modes

| Condition | Response |
|-----------|----------|
| `repo_root` not found | Set state → ERROR. Emit `sandbox_error`. Block all downstream. |
| `excluded_paths` violated | CRITICAL. Halt engine. Log violation. Require manual reset. |
| Scan exceeds `index_depth` | Truncate. Log warning. Complete partial index. |
| Registry collision | Reject new sandbox. Require explicit deregistration of existing. |

---

## Events Emitted

```
repo_sandbox_registered
repo_sandbox_deregistered
repo_index_started
repo_index_completed
sandbox_state_changed
sandbox_error
```

---

## Governance
- This contract may only be amended by the system operator or execution actor with external authorization
- SRT-1 may not self-amend this contract
- Constellation membership requires separate Constellation Contract

---

## NEEDS_SOURCE
- [ ] Registry storage backend (in-memory? file-based? Redis?)
- [ ] Maximum number of concurrent active sandboxes
- [ ] How `state: SUSPENDED` differs from `state: ARCHIVED` in practice
- [ ] Whether `scan_triggers: FILE_CHANGE` uses inotify, polling, or webhook
