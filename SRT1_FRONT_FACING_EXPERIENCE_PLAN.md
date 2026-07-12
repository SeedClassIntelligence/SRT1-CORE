# SRT1 Front-Facing Experience Plan

## 1. Current Frontend Inventory

Current public and PWA surfaces:

- `srt1_platform/pwa/srt1-core.html` - public product overview page.
- `srt1_platform/pwa/index.html` - lightweight redirect/entry page.
- `srt1_platform/pwa/auth.html` - sign up/login surface.
- `srt1_platform/pwa/dashboard.html` - existing technical Operations Console. This must remain intact.
- `srt1_platform/pwa/mobile.html` - mobile/PWA companion surface.
- `srt1_platform/pwa/constellation.html` - constellation/project activity surface.
- `srt1_platform/pwa/observatory.html` - deeper observability surface.
- `srt1_platform/pwa/documentation.html` - docs/quickstart.
- `srt1_platform/pwa/comparison.html` - product boundary comparison, including separate Seed Reflections links.
- `srt1_platform/pwa/workspace-demo.html` - workspace demonstration page.
- `srt1_platform/pwa/health.html` - system/health page.
- `srt1_platform/pwa/contact.html` - contact/sales page.

Reusable templates:

- `templates/home-hero.html`
- `templates/home-pricing.html`
- `templates/home-stats.html`
- `templates/dashboard-sidebar.html`
- `templates/dashboard-architecture.html`
- `templates/dashboard-enforcement.html`
- `templates/dashboard-telemetry.html`
- `templates/doc-content.html`
- `templates/doc-sidebar.html`
- `templates/compare-table.html`
- `templates/sandbox-concept-grid.html`
- `templates/sandbox-terminal.html`

Important current state:

- The current `dashboard.html` is the technical Operations Console, even if some visible copy now says "Active Work."
- It exposes repository registration, WorkCells, seeds, assistant adapters, verification, file maps, reflection, settings, runtime controls, and technical state.
- It should become Advanced/Developer Mode, not the default standard experience.

## 2. Existing Reusable Backend Routes

Repository and project preparation:

- `GET /api/v1/repositories`
- `POST /api/v1/repositories/register-current`
- `POST /api/v1/repositories/register-path`
- `POST /api/v1/repositories/browse-folder`
- `POST /api/v1/repositories/activate`
- `POST /api/v1/repositories/launch`
- `POST /api/v1/repositories/stop-runtime`
- `GET /dashboard-summary`
- `GET /manifest`
- `GET /synopsis`
- `GET /status`
- `GET /health`

Seeds and active work:

- `GET /seeds`
- `GET /seeds/active`
- `GET /seeds/pending`
- `GET /seeds/stats`
- `POST /seeds`
- `POST /task`
- `POST /api/v1/task`
- `PATCH /seeds/<id>`
- `POST /seeds/<id>/complete`
- `POST /seeds/<id>/fail`
- `POST /api/v1/slack/seed`
- `POST /api/v1/slack/command`

Work and conversation:

- `GET /api/v1/workcells`
- `GET /api/v1/workcells/{queue_seed_id}/messages`
- `POST /api/v1/workcells/{queue_seed_id}/chat`
- `GET /api/v1/workcells/{queue_seed_id}/stream`
- `GET /api/v1/workcells/{queue_seed_id}/activity`
- `GET /api/v1/workcells/{queue_seed_id}/workspace`
- `POST /api/v1/workcells/{queue_seed_id}/workspace/open`
- `POST /api/v1/workcells/{queue_seed_id}/dispatch`
- `POST /api/v1/workcells/{queue_seed_id}/action`
- `POST /api/v1/workcells/{queue_seed_id}/pause`
- `POST /api/v1/workcells/{queue_seed_id}/stop`
- `POST /api/v1/workcells/{queue_seed_id}/cancel`
- `POST /api/v1/workcells/{queue_seed_id}/verify`
- `POST /api/v1/workcells/{queue_seed_id}/ack`
- `POST /api/v1/workcells/{queue_seed_id}/validate-writes`

Review and approval:

- `GET /api/v1/change-proposals`
- `GET /api/v1/change-proposals/{proposal_id}`
- `GET /api/v1/workcells/{queue_seed_id}/proposals`
- `POST /api/v1/change-proposals/{proposal_id}/review`
- `POST /api/v1/change-proposals/{proposal_id}/apply`
- `POST /api/v1/workcells/{queue_seed_id}/verify`
- `POST /api/v1/workcells/{queue_seed_id}/action` with `approve` or `reject`.

Auth and external surfaces:

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `GET /auth/tokens`
- `POST /auth/generate`
- `POST /auth/revoke`
- `POST /auth/rotate`
- `GET /api/v1/assistant-adapters`
- `POST /api/v1/assistant-adapters`

## 3. Existing Reusable PWA Components

From `dashboard.html`:

- Repository preparation functions:
  - `renderRepositoryManager`
  - `registerCurrentRepository`
  - `registerRepositoryPath`
  - `browseRepositoryFolder`
  - `activateRepository`
  - `launchRepositoryRuntime`
  - `stopRepositoryRuntime`
  - `shutdownCurrentRuntime`

- Seed functions:
  - `submitTask`
  - `loadSeedQueue`
  - `renderFixQueue`
  - `updateBlueprintPreview`
  - `approveBlueprint`
  - `rejectBlueprint`
  - `createFindingFixSeed`

- Work/WorkCell functions:
  - `loadWorkCells`
  - `renderWorkCells`
  - `selectWorkCellDetail`
  - `renderWorkCellDetail`
  - `loadWorkCellMessages`
  - `sendWorkCellChat`
  - `loadWorkCellActivity`
  - `loadWorkCellProposals`
  - `reviewChangeProposal`
  - `applyChangeProposal`
  - `verifyWorkCell`
  - `controlWorkCell`
  - `openWorkCellInDesktopIDE`
  - `openWorkCellWorkspace`

- Assistant/adapter functions:
  - `loadAssistantAdapters`
  - `saveAssistantAdapters`
  - `runWorkCellWithAssistant`
  - `buildAssistantCredentialPayload`
  - `getProviderCompletionReviewState`
  - `getProviderResultSummary`

- General UI helpers:
  - `escapeHtml`
  - `formatTime`
  - `openDashboardPanel`
  - `switchDashTab`
  - `describeDashboardActionError`
  - theme and intro-modal helpers.

These components can be reused, but the Standard Experience should wrap them in simpler language and avoid direct exposure of internal terms by default.

## 4. Required New User-Facing Routes

Minimum proposed routes:

- `experience.html` - default post-login/front-facing SRT-1 home.
- `onboarding.html` - first-run choice screen.
- `idea.html` - start-with-an-idea conversational intake.
- `project.html` - project/work conversation view.
- `review.html` - plain-language review and approval surface.

Alternative implementation:

- Build all of the above as sections inside one `experience.html` shell, using query params or hash routes:
  - `experience.html#start`
  - `experience.html#project`
  - `experience.html#idea`
  - `experience.html#work`
  - `experience.html#review`

Recommended MVP:

- Use one new `experience.html` shell first.
- Link `dashboard.html` as "Advanced" or "Operations Console."
- Keep `dashboard.html` unchanged except for a deliberate link back to the Standard Experience later.

## 5. Complete Onboarding Flow

First-launch screen:

```text
Welcome to SRT-1

What would you like to do?

[ Add a project ]
[ Open an existing project ]
[ Connect a GitHub repository ]
[ Continue previous work ]
[ Capture an idea for later ]
[ Advanced / Operations Console ]
```

Behavior:

- `Add a project` is the primary first action. It opens folder/path/repository registration.
- `Open an existing project` calls existing repository activation routes.
- `Connect a GitHub repository` is presented as planned/optional if no route is available yet.
- `Continue previous work` reads `/dashboard-summary`, `/seeds`, and `/api/v1/workcells`.
- `Capture an idea for later` opens idea intake, but does not imply executable work until a project is attached.
- `Advanced / Operations Console` opens `dashboard.html`.

Project-first rule:

- Because SRT-1 runs from the user's computer and understands local work, the normal first step is adding a folder, repository, or project.
- Ideas become actionable after SRT-1 has a project context to understand, scope, verify, and protect.
- If the user only has an idea, SRT-1 may capture and clarify it as a draft, then guide the user to add or create the supporting project before planting executable work.

Standard language:

- "Project" instead of repository.
- "Work" instead of seed queue.
- "Workspace" or "work environment" instead of WorkCell.
- "Review/checks" instead of verification internals.
- "Advanced" instead of Operations Console in primary navigation.

## 6. Add-Project-First Flow

Goal:

Let a user attach the local folder, repository, or project SRT-1 should understand before any idea becomes executable work.

Entry choices:

```text
[ Choose Folder ]
[ Paste Project Path ]
[ Connect GitHub ]
```

Reusable backend:

- `POST /api/v1/repositories/browse-folder`
- `POST /api/v1/repositories/register-path`
- `POST /api/v1/repositories/register-current`
- `POST /api/v1/repositories/activate`
- `POST /api/v1/repositories/launch`

Preparation screen:

```text
SRT-1 is learning your project.

Reading project files
Understanding the project structure
Finding important relationships
Preparing project memory
Creating focused workspaces

Your project is ready.
```

Internal mapping:

- Reading project files = indexing and file scan.
- Understanding structure = manifest, symbols, dependencies.
- Finding relationships = dependency map and semantic graph.
- Preparing memory = continuity/recall setup.
- Creating focused workspaces = FileCells and WorkCells.

Do not show internal names unless the user clicks "Show technical details."

After project preparation:

```text
Your project is ready.

What would you like to accomplish first?

[ Plant an idea ]
[ Continue existing work ]
[ Open project conversation ]
[ Advanced details ]
```

## 7. Idea Capture Flow

Goal:

Let a user capture and clarify an idea, while making clear that executable SRT-1 work needs a project/folder/repository context.

Screen when a project is already active:

```text
Tell me what you want to create.
```

Screen when no project is active:

```text
Tell me the idea.

I can help shape it now. To turn it into active work, add the folder or repository SRT-1 should use.
```

Conversation tasks:

- Clarify the idea.
- Identify the intended outcome.
- Ask necessary questions.
- Determine if supporting files already exist.
- Suggest next step: attach folder, open existing project, connect repository, or plant the idea inside the active project.

Primary actions:

```text
[ Add Project ]
[ Plant This Idea In Current Project ]
[ Save Idea Draft ]
```

Backend mapping:

- MVP can call existing seed routes with `source: front_facing_idea`.
- If no repository/project is active, do not create an executable WorkCell. Save or display the idea as project-pending and guide the user to add a folder/repository.
- If a project is active, planting the idea may create the canonical seed, queue record, WorkCell, conversation, continuity state, assistant assignment, and verification requirements.
- Later, add a first-class idea/project draft record if needed. Do not add duplicate backend systems in the first pass.

Internal results may include:

- canonical seed
- seed queue record
- conversation identity
- WorkCell after project context exists
- continuity state
- assigned assistant adapter
- verification requirements

The user only sees:

- idea name
- status
- next question/action
- "ready to plant" or "project needed."

## 7A. Existing-Project Shortcut

This is the shortcut path for users who already registered or recently used a project.

Entry choices remain:

```text
[ Choose Folder ]
[ Paste Project Path ]
[ Connect GitHub ]
[ Recent Projects ]
```

Reusable backend:

- `POST /api/v1/repositories/browse-folder`
- `POST /api/v1/repositories/register-path`
- `POST /api/v1/repositories/register-current`
- `POST /api/v1/repositories/activate`
- `POST /api/v1/repositories/launch`

Preparation screen:

```text
SRT-1 is learning your project.

Reading project files
Understanding the project structure
Finding important relationships
Preparing project memory
Creating focused workspaces

Your project is ready.
```

Internal mapping:

- Reading project files = indexing and file scan.
- Understanding structure = manifest, symbols, dependencies.
- Finding relationships = dependency map and semantic graph.
- Preparing memory = continuity/recall setup.
- Creating focused workspaces = FileCells and WorkCells.

The UI should prefer recent/local projects first, because SRT-1 is local-first and normally works from the user's machine.

## 8. Front-Facing Home

Screen:

```text
Good afternoon, Darnell.

What would you like to accomplish today?

[ Add project ]
[ Plant an idea in current project ]
[ Continue previous work ]

Active Work

SCI Runtime
Working

SRT-1 Interface
Waiting for review

SoulSonus
Ready to continue
```

Data sources:

- `/dashboard-summary`
- `/api/v1/repositories`
- `/seeds`
- `/api/v1/workcells`
- `/api/v1/workcells/{queue_seed_id}/activity`

Plain-language status mapping:

- `ready`, `running`, `dispatched` = Working
- `awaiting_review` = Waiting for review
- `verified` = Checks passed
- `completed` = Completed
- `returned` = Needs changes
- no active execution = Ready to continue
- engine unavailable = Needs project runtime

## 9. Project Conversation Experience

Project page layout:

```text
SCI Runtime

Welcome back.

Since your last session:
- Authentication work was completed.
- Documentation is waiting for your review.
- No review problems were found.

What would you like to do?

[ conversation input ]
```

User can ask:

- Continue cleaning SRT-1.
- Show me what changed.
- Explain what is waiting for review.
- Start working on the mobile interface.
- Open files.
- Show technical details.

Backend mapping:

- Determine active seed from `/seeds/active` and `/api/v1/workcells`.
- Use WorkCell conversation endpoints:
  - `GET /api/v1/workcells/{id}/messages`
  - `POST /api/v1/workcells/{id}/chat`
  - `GET /api/v1/workcells/{id}/stream`
- Use activity/proposals routes for status summaries.

MVP limitation:

- The current chat endpoint records messages but does not yet perform live assistant execution. The page should say "message recorded" or "assistant adapter pending" unless an adapter is actually connected.

## 10. Review And Approval Experience

Plain-language review screen:

```text
Ready for your review

What was completed:
- Token refresh logic was improved.
- Regression tests were added.
- Existing login behavior was preserved.

Checks:
- 18 tests passed.
- No files outside the assigned workspace were changed.

[ Approve ]
[ Return for changes ]
[ Show technical details ]
```

Reusable backend:

- `GET /api/v1/workcells/{id}/proposals`
- `POST /api/v1/change-proposals/{proposal_id}/review`
- `POST /api/v1/change-proposals/{proposal_id}/apply`
- `POST /api/v1/workcells/{id}/verify`
- `POST /api/v1/workcells/{id}/action` with approve/reject
- `GET /api/v1/workcells/{id}/activity`

Translation rule:

- Show summaries first.
- Put file paths, proposal IDs, WorkCell IDs, test logs, and boundary checks behind "Show technical details."

## 11. Standard Versus Advanced Mode

Standard Experience:

- add/open project
- plant an idea in the active project
- capture an idea draft only when no project is ready
- active work list
- conversation-first project screen
- plain review
- approve/return
- optional file/IDE open

Advanced Experience:

- existing `dashboard.html`
- repository manager
- manifest and symbols
- FileCells and WorkCells
- reflection
- seed queue internals
- verification internals
- Constellation and Observatory
- runtime ports
- assistant adapter configuration
- technical logs and package files

Both modes use the same backend. They are not separate systems.

## 12. How The Current Operations Console Remains Accessible

The current `dashboard.html` remains the Operations Console.

Access points:

- Standard header link: `Advanced`
- Project menu: `Show technical details`
- Review screen: `Open Operations Console`
- Error/debug path: `Developer Mode`
- Direct URL: `/dashboard`

Do not remove:

- current dashboard tabs
- WorkCell Operations
- repository manager
- assistant adapter settings
- reflection panels
- file maps
- Constellation/Observatory links
- seed queue internals
- verification internals

## 13. Minimum Viable Implementation Sequence

Phase 1 - Planning and copy guardrails:

- Add this plan.
- Keep current dashboard intact.
- Add tests to distinguish Standard Experience from Operations Console.

Phase 2 - Front-facing shell:

- Add `experience.html`.
- Add welcome/onboarding choice screen.
- Link `Advanced` to `dashboard.html`.
- Do not move backend logic.

Phase 3 - Project-first onboarding:

- Reuse repository registration functions/routes.
- Present preparation checklist in plain language.
- Route to front-facing home after ready.
- Treat idea capture as secondary until a project/folder/repository exists.

Phase 4 - Active Work home:

- Fetch `/dashboard-summary`, `/seeds`, `/api/v1/workcells`.
- Render project/work cards with plain-language statuses.
- Hide technical metrics from the primary home.

Phase 5 - Project conversation:

- Add conversation-first project view.
- Reuse WorkCell message/chat/stream endpoints.
- Add "Show technical details" link to the matching WorkCell in `dashboard.html`.

Phase 6 - Review and approval:

- Create owner-facing review panel.
- Reuse change proposal, verification, and action endpoints.
- Translate verification results into plain language.

Phase 7 - Assistant adapter execution:

- Route conversation messages into the chosen assistant adapter when configured.
- Stream assistant/tool/test/file-change events into the same conversation.
- Keep SRT-1 as owner of state, permissions, recall, verification, and lineage.

## 14. Files That Would Be Changed

Likely new files:

- `SRT1_FRONT_FACING_EXPERIENCE_PLAN.md`
- `srt1_platform/pwa/experience.html`
- `srt1_platform/pwa/experience.css` or inline styles inside `experience.html` for MVP
- `srt1_platform/pwa/experience.js` or inline script inside `experience.html` for MVP
- `tests/test_front_facing_experience.py`

Likely modified files:

- `srt1_platform/pwa/auth.html` - route post-login users to `experience.html` instead of technical dashboard.
- `srt1_platform/pwa/srt1-core.html` - make primary CTA point to front-facing experience/onboarding.
- `srt1_platform/pwa/mobile.html` - optionally align mobile entry to the same Standard Experience.
- `srt1_platform/pwa/dashboard.html` - add a clear "Standard Experience" return link and ensure it is labeled Advanced/Operations Console.
- `srt_code_indexer/engine.py` only if static serving needs an explicit `/experience` route. Avoid broad changes.

## 15. Files That Must Not Be Changed

For the first implementation pass:

- Do not change WorkCell backend semantics in `srt1_platform/workcell.py`.
- Do not rename `Seed`, `WorkCell`, `FileCell`, `Manifest`, `Verification`, or `Constellation` internally.
- Do not remove or rewrite `srt1_platform/pwa/dashboard.html`.
- Do not remove `srt1_platform/pwa/constellation.html`.
- Do not remove `srt1_platform/pwa/observatory.html`.
- Do not remove existing seed queue behavior.
- Do not remove assistant adapter settings.
- Do not remove existing `/api/v1/workcells/*` routes.
- Do not remove existing `/seeds` routes.
- Do not broadly restructure `srt1_code_indexer/engine.py`.

## 16. Test Plan

Static tests:

- Confirm `experience.html` exists.
- Confirm front-facing home includes:
  - Add a project
  - Open existing project
  - Plant an idea in current project
  - Capture an idea for later
  - Continue previous work
  - Advanced / Operations Console
- Confirm Standard Experience does not expose primary internal labels:
  - Manifest
  - FileCell
  - RecallPacket
  - runtime port
  - dependency graph
- Confirm `dashboard.html` still contains Operations Console capabilities.
- Confirm `dashboard.html` remains reachable from Standard Experience.

Route tests:

- Existing tests for WorkCells and seed queue continue passing.
- Add tests for any new `/experience` static route if `engine.py` is touched.

Behavior tests:

- Mock `/dashboard-summary`, `/seeds`, `/api/v1/workcells` responses and verify plain-language status mapping.
- Mock WorkCell messages and verify conversation renders without technical IDs by default.
- Mock review/proposals response and verify owner-facing review summary renders.

Regression tests:

- Run:
  - `python -m unittest tests.test_public_website_messaging`
  - `python -m unittest tests.test_workcell_runtime`
  - `python -m unittest tests.test_seed_queue_compatibility tests.test_task_response_identity`

Manual verification:

- Open `experience.html`.
- Walk through:
  - add a project
  - open existing project
  - plant an idea in the active project
  - capture an idea without a project and confirm it remains pending
  - continue previous work
  - open Operations Console
- Confirm current `dashboard.html` still works.

## 17. Risks And Unresolved Questions

Risks:

- The Standard Experience could accidentally hide important review/verification evidence. Mitigation: always provide "Show technical details."
- The system may appear to promise full assistant execution before adapters are connected. Mitigation: label MVP chat state accurately.
- Existing `dashboard.html` is large and contains reusable logic embedded inline. Reusing it without duplication may require extracting shared API helpers later.
- GitHub connection may not yet have a complete local backend route. Treat it as planned or connector-dependent until verified.
- "Capture an idea" without a repository needs a clear pending state. It should not pretend a WorkCell exists before project context exists.
- The front-facing layer must not create a second seed/work/conversation system.

Unresolved questions:

- Should `experience.html` become the post-login default immediately, or should this be guarded behind a feature flag first?
- Should first-run setup store a local preference such as `srt1_standard_experience_seen`?
- What should the canonical user display name source be for greetings?
- Should "project" map to repository activation immediately, or should SRT-1 support non-code project folders first?
- Should GitHub connection be built through existing repository path handling, GitHub app integration, or a future import service?
- Should WorkCell conversation messages trigger assistant execution immediately, or should the first MVP record messages only until adapter execution is explicitly enabled?

## Final Principle

Do not simplify SRT-1.

Build a simplified front-facing experience over the system that already exists.

The ordinary user should experience:

```text
Add or open a project from the computer
-> let SRT-1 prepare it
-> plant or continue an idea inside that project
-> talk to the work
-> watch understandable progress
-> review the result
-> approve or return it
-> open technical details only when desired
```

The existing technical platform remains the machine room. The new layer becomes the front door.
