# SRT1 Enterprise Pickup Instructions

These instructions are for the next thread or recovery pass that works on SRT-1
Enterprise. They intentionally do not move Enterprise implementation into public
Core.

## Starting Point

SRT-1 Core has recently been recovered and pushed through:

- boundary cleanup
- authority recovery
- runtime classification
- state ownership
- continuity identity alignment
- recall/reinjection alignment
- WorkCell/FileCell direction
- repository activation
- dashboard cockpit improvements
- assistant adapter layer
- dashboard adapter controls
- local Slack-style seed intake

Latest known Core checkpoint when this document was written:

```text
c1da15591d5395220b5043f7c0764b13f23a171c
feat: wire dashboard assistant adapters and slack seeds
```

Enterprise must now be recovered as its own product line.

## Enterprise Mission

SRT-1 Enterprise is the private/team/cloud governance and orchestration product
for organizations using SRT-1 across teams, repositories, assistants, WorkCells,
and trust authorities.

Enterprise is not public Core. Enterprise has its own setup, dashboard, backend,
policy layer, authentication model, and private integrations.

## Non-Negotiable Boundary

Do not place Enterprise private implementation into public Core.

Do not expose:

- private Seed Signature authority implementation
- private keys
- private signing service
- private audit chain
- SCIA memory implementation
- SCIA security implementation
- SION internals
- Enterprise backend implementation
- team/cloud/SSO backend
- private Slack workspace backend

Core may retain public hooks/contracts/placeholders that fail closed.

Enterprise may implement the private systems behind those hooks in a separate
private product surface.

## Enterprise Dashboard Requirement

Enterprise must have a separate dashboard and setup.

The Enterprise dashboard should not simply be the Core dashboard with more
cards. It should be designed around organization, team, policy, and managed
execution workflows.

Enterprise dashboard should eventually expose:

- organization/workspace selector
- team and role management
- repository fleet view
- WorkCell assignment by team/member/assistant
- Slack/team channel routing
- model/provider routing policy
- Seed Signature status
- private audit chain status
- policy violations
- approval queues
- managed assistant execution status
- SION readiness/status if enabled
- cross-repo Constellation view
- compliance/reporting exports
- billing/license/admin controls

Core dashboard remains the local developer cockpit.

## Enterprise Backend Requirement

Enterprise backend should own:

- organization identity
- users and roles
- SSO/session policy
- workspace/repository registry
- team Slack integration
- provider credential vault
- model-routing policy
- private audit ledger
- Seed Signature authority integration
- SCIA memory/security integration
- managed WorkCell assignment
- managed runtime orchestration
- Enterprise notifications
- reporting/compliance surfaces

Enterprise backend should consume Core concepts, not rewrite them.

Preserve Core concepts:

- Repository
- FileCell
- WorkCell
- Seed
- RecallPacket
- Reinjection packet
- Verification result
- Trust metadata
- Assistant adapter dispatch

Enterprise adds policy, team, cloud, private trust, and governance around those
objects.

## Enterprise Recovery Phase 1

Inventory only. Do not build.

Output:

```text
docs/recovery/SRT1_ENTERPRISE_INVENTORY.md
```

Classify all Enterprise/private-related files into:

1. Enterprise dashboard candidate
2. Enterprise backend candidate
3. Seed Signature/private trust candidate
4. SCIA memory/security candidate
5. SION candidate
6. Slack/team/cloud candidate
7. Public Core hook/contract candidate
8. Generated/local/private ignore
9. Needs founder decision

For each file:

- exact path
- current git status
- capability
- risk
- keep private / public hook / archive / ignore / review
- reason

## Enterprise Recovery Phase 2

Architecture only. Do not build.

Output:

```text
docs/recovery/SRT1_ENTERPRISE_ARCHITECTURE_V1.md
```

Define:

- Enterprise product mission
- Enterprise authorities
- Enterprise dashboard architecture
- Enterprise backend architecture
- private trust architecture
- Slack/team architecture
- SION future integration boundary
- Core integration points
- private exclusions from Core

## Enterprise Recovery Phase 3

Dashboard plan only. Do not build until approved.

Output:

```text
docs/recovery/SRT1_ENTERPRISE_DASHBOARD_PLAN.md
```

Define screens:

- Enterprise home
- Organizations
- Teams
- Repositories
- WorkCells
- Assistant assignments
- Slack/team channels
- Seed approvals
- Verification queue
- Trust/audit status
- Policy violations
- Reports
- Settings

## Enterprise Recovery Phase 4

Backend plan only. Do not build until approved.

Output:

```text
docs/recovery/SRT1_ENTERPRISE_BACKEND_PLAN.md
```

Define:

- data model
- auth/session model
- organization/workspace model
- repository registry
- WorkCell assignment model
- Slack app model
- provider credentials model
- Seed Signature integration model
- audit ledger model
- policy engine boundaries
- fail-closed behavior

## How Enterprise Should Integrate With Core

Enterprise should call or package Core capabilities through explicit boundaries:

```text
Core Repository Runtime
-> Enterprise Registry
-> Enterprise Dashboard
-> Enterprise Policy
-> Core WorkCell/Seed APIs
-> Assistant Adapter / Managed Runtime
-> Verification
-> Enterprise Audit / Trust / Reporting
```

Enterprise should not mutate Core internals directly.

Enterprise should not replace `SCIASeedQueue` as canonical seed lifecycle owner.

Enterprise should not bypass WorkCells.

Enterprise should not bypass verification.

Enterprise should not inject private memory/security/audit data into public Core
context packets.

## Immediate Next Enterprise Instruction

Use this exact instruction when ready to continue Enterprise recovery:

```text
Proceed with SRT1 Enterprise Recovery Phase 1: Enterprise Inventory.

Documentation-only.
Do not modify code.
Do not move files.
Do not stage private implementation into public Core.

Read the current SRT1 repo and identify all Enterprise/private-related files,
including Enterprise dashboard candidates, backend candidates, Seed Signature,
SCIA memory/security, SION, Slack/team/cloud, private audit, auth/session, and
public Core hooks/contracts.

Create:
docs/recovery/SRT1_ENTERPRISE_INVENTORY.md

For each file, include:
- exact path
- git status if known
- capability
- classification
- risk
- recommended action
- reason

Preserve Enterprise as a separate product line with a separate dashboard and
setup. Do not expose private implementation in public Core.
```

