# SRT1 Repository Activation

## Overview

Repository Activation is the missing first-run layer for SRT-1 Core.

Before SRT-1 can create FileCells, WorkCells, recall packets, verification state, or a useful dashboard, it must know which local repository it is responsible for managing. The first user action after install and launch should not be planting a seed. It should be registering or selecting a repository.

The product lifecycle becomes:

```text
Install SRT-1
-> Launch SRT-1
-> Register Repository
-> Repository Understanding
-> Persistent FileCells
-> Persistent WorkCells
-> Select WorkCell
-> Plant Seed
-> WorkCell Execution
-> Verification
-> Human Review
```

## Purpose

Repository Activation answers:

- which local folder or Git repository SRT-1 manages
- where persistent repository intelligence is stored
- whether existing repository understanding can be reused
- whether a manifest, FileCells, and WorkCells are fresh, stale, degraded, or unknown
- which repository runtime should serve the PWA, MCP, API, and WorkCell cockpit

This prevents SRT-1 from opening into an empty middle state where the user is asked for a task before the system knows the project.

## User Experience Contract

On first launch, if no repositories are registered, the PWA should show a Repository Manager.

Primary actions:

- Add Repository
- Open Repository
- Register Project

The user selects a local project folder. That folder becomes the repository root for one SRT-1 repository runtime.

After registration, SRT-1 performs Repository Understanding:

```text
selected repository
-> file scan
-> hashing
-> parser/AST pass
-> manifest generation
-> FileCell creation
-> WorkCell creation
-> dependency graph
-> authority graph
-> verification index
-> repository ready
```

After the repository is ready, the user should navigate through SRT-1's understanding of the repository rather than repeatedly returning to the operating system file picker.

## Daily Use Contract

After first registration, the normal daily flow should be:

```text
Launch SRT-1
-> Select Repository
-> Load existing repository understanding
-> Refresh stale evidence if needed
-> Select WorkCell
-> Plant Seed
-> Run assistant inside WorkCell
```

The repository should not be rescanned from scratch unless:

- the user requests a full rebuild
- the manifest is missing
- freshness checks fail
- file changes exceed the rebuild threshold
- parser/index schema changes require regeneration

## Repository Manager

The Repository Manager is the first product surface before the WorkCell cockpit.

It should show:

- registered repositories
- repository path
- repository status
- manifest freshness
- FileCell count
- WorkCell count
- last indexed time
- active runtime port
- trust/lineage state
- available actions

Example:

```text
Repositories

SRT-1 Core
Ready
221 files
221 FileCells
221 WorkCells
Port 7484

Veteran Housing
Stale
412 files
Needs refresh

Mobile App
Not indexed
Registering
```

## State Ownership

| State | Owner | Notes |
| --- | --- | --- |
| Registered repository list | Repository Activation | Local registry of known project roots. |
| Repository root path | Repository Activation | Must be explicit and local. |
| Repository runtime identity | Repository Activation + Constellation | Maps a repository to a runtime/port. |
| Repository manifest | Repo Understanding | Created after activation. |
| FileCells | Repo Understanding | Persist after repository understanding. |
| WorkCells | Repo Understanding + Context Isolation | Created per file after repository understanding. |
| Active seed | Continuity | Must attach to an activated repository and selected WorkCell. |
| Runtime port map | Constellation | Knows repository and WorkCell runtime ownership. |
| Trust/freshness labels | Trust Awareness | Labels registered repository state and derived artifacts. |

## Authority Placement

Repository Activation is not a replacement for Repo Understanding.

It is the product bootstrapping layer that runs before Repo Understanding.

| Responsibility | Authority |
| --- | --- |
| Selecting/registering a repository | Repository Activation |
| Scanning/parsing/indexing files | Repo Understanding |
| Creating FileCells | Repo Understanding |
| Creating WorkCells | Repo Understanding + Context Isolation |
| Selecting an active WorkCell | Human Co-Creation + Context Isolation |
| Planting a seed into a WorkCell | Continuity |
| Tracking multiple repository runtimes | Constellation |

## Core Boundary

Public Core may include:

- local repository registration
- local repository list
- repository path validation
- repository freshness metadata
- repository activation status
- first-run PWA Repository Manager
- fail-closed handling for missing or inaccessible paths

Public Core must not include:

- cloud/team repository sync
- Enterprise workspace policy backend
- private memory implementation
- private signing implementation
- private audit chain
- autonomous code mutation during activation

## Refusal Conditions

Repository Activation should fail closed when:

- no repository path is selected
- the selected path does not exist
- the selected path is outside allowed local policy
- the selected path appears to be a private implementation area excluded from Core
- the selected path is another nested SRT-1 checkout unless explicitly approved
- manifest generation cannot complete and no previous understanding exists
- the PWA tries to plant a seed before any repository is active

## Build Plan Placement

Repository Activation belongs before the current WorkCell runtime path:

```text
Repository Activation
-> Repo Understanding
-> FileCells
-> WorkCells
-> Continuity
-> Recall
-> Reinjection
-> Verification
-> Human Co-Creation
-> Constellation
```

The current implementation has repository runtime assumptions, manifest generation, WorkCells, and a dashboard cockpit. It does not yet have the first-run Repository Manager as a complete product surface.

## First Implementation Slice

The easiest safe path is:

1. Keep current single-repository runtime working.
2. Add a local repository registry file under SRT-1 runtime state.
3. Add API endpoints to list, register, activate, and refresh repositories.
4. Add a PWA Repository Manager screen shown before the WorkCell dashboard when no active repository exists.
5. When a repository is activated, reuse existing Repo Understanding to create manifest, FileCells, and WorkCells.
6. Store freshness metadata so the next launch can load existing understanding before rescanning.
7. Only after single-repository activation is stable, connect Constellation to multiple repositories and ports.

Do not implement cloud repository management or Enterprise team workspace policy in this slice.
