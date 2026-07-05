# Repo Sandbox Contract

**Contract ID:** `SRT1-CONTRACT-SANDBOX-001`
**Between:** Registered Repository and SRT-1 Runtime
**Status:** Public Core

## Purpose

Define the local repository boundary SRT-1 may understand. No indexing,
WorkCell creation, FileCell creation, context serving, or verification may occur
outside a registered repository sandbox.

## Contract Fields

```yaml
sandbox_id: string
repo_root: path
repo_slug: string
runtime_port: integer | null
state: ACTIVE | SUSPENDED | ARCHIVED | ERROR
excluded_paths: list[path]
scan_triggers: list[MANUAL | FILE_CHANGE | SEED_INTAKE | SCHEDULED]
created_at: datetime
last_indexed_at: datetime | null
manifest_hash: string | null
constellation_member: boolean
```

## Guarantees

- SRT-1 reads only inside `repo_root`.
- Excluded paths are never read, indexed, summarized, or injected.
- Runtime/generated folders are skipped unless explicitly approved.
- Repository identity, manifest hash, and freshness state are visible.
- A sandbox may be part of a Constellation without sharing context by default.

## Refusal Conditions

- `repo_root` is missing, unreadable, or outside the approved local path.
- Requested scan crosses repository boundary.
- Requested scan targets forbidden paths such as `.git`, secrets, keys, runtime
  state, caches, or private implementation folders.
- Registry collision cannot be resolved safely.

## Events

```text
repo_sandbox_registered
repo_sandbox_state_changed
repo_index_started
repo_index_completed
repo_index_failed
sandbox_error
```

## Boundary

Public Core owns local repository registration and observation. It does not
grant broad write access to assistants. Governed writes must pass through
WorkCell/FileCell scope, verification, and human/assistant execution policy.
