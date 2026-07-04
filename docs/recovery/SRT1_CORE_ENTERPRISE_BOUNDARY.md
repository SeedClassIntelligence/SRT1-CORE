# SRT1 Core / Enterprise Boundary

This document records the current public/private product boundary after the
SRT-1 Core recovery work through the assistant adapter and Slack seed-intake
slice.

SRT-1 Core and SRT-1 Enterprise are related products, but they are not the same
runtime, dashboard, or packaging target. Core must remain a local-first,
public-safe repo-continuity and alignment partner for AI coding assistants.
Enterprise must remain a separate private/team/cloud product line with its own
dashboard, backend, policy controls, and private integrations.

## Current Core Product

SRT-1 Core is the local developer product. It manages one local repository
runtime at a time and gives the developer a cockpit for repository
understanding, seed continuity, WorkCells, FileCells, assistant handoff, recall,
reinjection, verification, and trust-state awareness.

Core currently includes or may publicly expose:

- Repository activation and local runtime registration.
- Repo Understanding through indexing, manifest generation, file hashing,
  parser coverage, symbol extraction, dependency awareness, and project
  synopsis.
- Persistent FileCell direction for per-file repository intelligence.
- WorkCell runtime packages with `workcell.md`, package status, FileCell
  summaries, allowed/restricted path metadata, and assistant handoff context.
- Canonical seed continuity through `SCIASeedQueue`.
- SRT reflection/coherence anchors as metadata, not lifecycle identity.
- RecallPacket-shaped context.
- Reinjection that consumes RecallPacket-shaped data.
- Dashboard/PWA cockpit for human observability, review, adapter selection,
  WorkCell inspection, seed planting, runtime start/stop, and local status.
- Model-agnostic assistant adapters:
  - Codex WorkCell file handoff.
  - Generic file handoff.
  - Custom HTTP model adapter.
- Local Slack-style seed intake endpoints that plant seeds into the same
  queue-first WorkCell execution path.
- Trust Awareness vocabulary:
  - signed / unsigned
  - verified / unverified
  - lineage present / missing
  - fresh / stale / degraded / unknown
- Fail-closed hooks for optional external systems.

Core must remain useful when every private or Enterprise service is unavailable.

## Current Enterprise Product Direction

Enterprise is a separate product line. It should not be treated as a hidden
folder inside Core or as a set of extra buttons on the Core dashboard.

Enterprise needs its own recovery and build track:

- Separate Enterprise dashboard.
- Separate setup and onboarding.
- Organization/team/workspace management.
- Team/cloud/SSO backend.
- Slack/team communication backend.
- Role-based approval and review.
- Policy controls and governance configuration.
- Private audit chain integration.
- Private Seed Signature authority integration.
- SCIA memory implementation.
- SCIA security implementation.
- Enterprise-specific observability, reporting, and compliance views.
- Multi-user WorkCell assignment.
- Cross-repository/team Constellation controls.
- Cloud or managed runtime orchestration.
- Optional future SION runtime integration.

Enterprise must be built and enhanced, but its private implementation must not
bleed into public Core.

## Seed Signature Boundary

Seed Signature is cross-tier trust authority. It can sign Developer, Pro, and
Enterprise artifacts when the private signing authority is configured.

Public Core may preserve Seed Signature as trust vocabulary and external
provenance metadata. Public Core must not ship:

- private Seed Signature authority implementation
- private keys
- private signing queue
- private audit chain
- private signing service backend

The correct boundary is:

```text
Core understands trust states.
Private Seed Signature authority produces signatures.
Enterprise may integrate private authority at scale.
```

## Slack Boundary

Core now supports local Slack-style seed intake. This means Core can accept a
Slack-shaped payload and plant a seed into the normal queue-first WorkCell path.

Core Slack-style intake is not the Enterprise Slack backend.

| Surface | Core | Enterprise |
| --- | --- | --- |
| Slack-shaped seed payload | Yes | Yes |
| Local seed intake endpoint | Yes | Yes |
| Slack signing secret verification | Later / optional local config | Required |
| Workspace/team mapping | No | Required |
| Channel/user permissions | No | Required |
| Organization policy | No | Required |
| Completion notifications | Later local hook | Required |
| Admin controls | No | Required |

Core route:

```text
Slack-style payload
-> /api/v1/slack/seed
-> SCIASeedQueue canonical seed
-> WorkCell execution package
-> assistant adapter handoff
```

Enterprise route:

```text
Slack workspace
-> Enterprise auth/policy backend
-> repository/workspace mapping
-> approved seed intake
-> team-visible WorkCell execution
-> notification/reporting/audit
```

## Assistant Adapter Boundary

Core assistant adapters are model-agnostic dispatch surfaces. They receive
bounded WorkCell execution requests. They do not own repository truth, seed
lifecycle, verification, trust authority, or policy.

Core adapter types:

- `codex`
- `file_context`
- `custom_http`

Future adapters may support Claude Code, Cursor, local open-source models,
OpenAI-compatible endpoints, Anthropic-compatible endpoints, or SION.

Enterprise may add:

- managed provider credentials
- team-level model routing
- billing/rate policy
- approved model registry
- audit-backed dispatch records
- organization-level assistant assignment

Core must not store or expose Enterprise credential backends.

## SION Boundary

SION is spelled `SION`.

SION is not active in current Core. SION is a planned first-party assistant or
runtime that may eventually operate inside WorkCells, modify code inside bounded
scope, or delegate to other assistants.

Current rule:

```text
Do not make SION a Core dependency.
Do not wire SION as current lifecycle authority.
Do not expose SION internals in public Core.
```

Future rule:

```text
SION may become an assistant adapter or Enterprise/private runtime after its
own boundary, dashboard, policy, and verification contracts are recovered.
```

## What Must Stay Out Of Public Core

Do not publish private implementation for:

- SCIA memory implementation
- SCIA security implementation
- private Seed Signature authority
- private keys
- private signing queues
- private audit chain
- SION internals
- Enterprise backend
- team/cloud/SSO backend
- private Slack workspace backend
- proprietary governance loops

Public Core may include contracts, vocabulary, placeholders, hooks, or fail-closed
adapters only when they do not expose private implementation.

## Current Public Core Release Position

Core is now positioned as:

```text
SRT-1 Core is a local-first repo-continuity, WorkCell, recall, verification,
and assistant-handoff platform for AI coding assistants.
```

Enterprise is positioned as:

```text
SRT-1 Enterprise is the private/team/cloud governance product with its own
dashboard, backend, policy, Slack/team workflows, Seed Signature integration,
private memory/security systems, and managed execution controls.
```

These two product lines should evolve together, but they must not be mixed in
one public Core package.

