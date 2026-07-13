# SRT-1 Standard Experience Redesign Plan

## 1. Current Screen Critique

The current Standard Experience is closer, but it still behaves like a visual mirror of backend architecture. It exposes project navigation, current work, project conversation, project intelligence, status cards, and action buttons as separate permanent regions.

The main issue is not styling. The issue is product structure. The user is still asked to choose between interface areas that should be operated by SRT-1 itself through conversation.

The Standard Experience should not feel like a dashboard with chat inside it. It should feel like a conversational workspace that can operate the dashboard, backend services, WorkCells, seeds, verification, files, and review state when needed.

## 1A. Product Organizing Question

Do not start with the UI.

Start with:

```text
What can the owner ask SRT-1 to do?
```

The Standard Experience should be organized around owner intention, not backend features. SRT-1 may still use seeds, WorkCells, FileCells, verification, recall, assistant routing, and Control Room views internally, but those should be orchestration details unless the owner explicitly asks to inspect them.

The product grammar:

- Create: ideas, projects, roadmaps, architecture, databases, apps, websites, documentation, brainstorming.
- Connect: folders, GitHub, current workspace, VS Code, Slack, Google Drive, last project.
- Understand: project explanation, architecture, modules, files, functions, dependencies, broken areas, changed work.
- Plan: features, tasks, estimates, priorities, milestones, WorkCells, merged ideas.
- Execute: continue, build, implement, fix, refactor, document, test, clean, finish.
- Observe: active work, assistant activity, progress, blocked work, waiting reviews, completed work.
- Review: changed work, implementation explanation, before/after comparison, reasoning, tests, safety, approve, reject, return.
- Inspect: Control Room, WorkCell, verification, manifest, repository intelligence, Constellation, logs.
- Collaborate: assign Codex, assign Claude, ask Gemini to review, switch assistants, bring another engineer in, share with the team.
- Learn: lessons, recurring mistakes, patterns, remembered decisions, reusable methodology.
- Manage: pause, resume, archive, duplicate, rename, delete, move, merge, reopen.
- Search: conversations, authentication, seeds, documentation, code, decisions, reviews.

The core operating line is:

```text
What do you want to accomplish?
```

The only permanent Standard Experience concepts should be:

- Projects: where the owner is working.
- Conversation: how the owner directs the work.
- Activity: what is happening now.
- Reviews: what needs the owner's decision.
- Advanced: explicit access to the machinery.

## 1B. Living Mission Workspace

The Standard Experience must not feel like an AI project manager waiting for instructions. It should feel like an AI project operating system that is already awake, already synchronized, and already aware of what happened while the owner was away.

Every session should begin with a mission brief:

```text
Welcome back.

Here's what happened while you were away.
- Authentication completed.
- Mobile build paused.
- One review is waiting.
- Codex has no active assignments.

Today's recommendation:
Finish Authentication before starting Mobile.

Continue?
```

The hierarchy is:

```text
Projects contain missions.
Missions contain work.
Work creates focused execution threads.
Execution returns reviewable outcomes.
```

The primary surface should always show:

- Current Mission.
- Mission objective.
- Mission progress.
- What happened while the owner was away.
- What needs the owner's decision.
- What SRT-1 recommends next.
- A conversation with the intelligence responsible for the mission.

SRT-1 concepts should surface as outcomes, not premature internal labels:

- Recall becomes "Last time we worked on this..."
- Verification becomes "Everything checks out" or "One issue needs attention."
- Continuity becomes "I've restored exactly where we left off."
- Constellation becomes "Everything is synchronized."
- WorkCells become specific pieces of active work, such as "Authentication" or "Mobile Build."
- Seeds become mission requests or ideas SRT-1 carries forward.

Product rule:

```text
Do not design an interface where users operate SRT-1.
Design an interface where SRT-1 operates the platform and the user collaborates with SRT-1.
```

The conversation must not sit on top of the workspace as an instruction layer. The conversation is the workspace. Mission state, ambient briefings, active work, review cards, suggestions, approvals, returns, and inspection links should appear as conversational turns inside the same thread where the owner is collaborating with SRT-1.

## 2. Exact Duplicated Components

- Separate project onboarding view and Project Controller entry flow.
- Project selection in the left rail plus separate "Open Existing Project" flow.
- "Current Project" and "Previous Work" controls duplicating what project selection and conversation history should provide.
- Project Conversation panel plus Project Intelligence panel, even though intelligence should appear inside the conversation.
- Top status cards duplicating information that should be contextual or Advanced-only.
- Permanent action buttons such as Plant Seed, Check File, Pause, Resume, and Control Room, even though these should be natural-language actions or contextual response buttons.

## 3. Components To Preserve

- SRT-1 branding.
- Advanced / Control Room access.
- Ability to connect a project from folder, current folder, or GitHub.
- Project-aware conversation foundation.
- Ability to start new work.
- Ability to continue work.
- Ability to pause, resume, review, approve, return, inspect files, and request technical detail.
- Existing backend routes and state ownership.
- Existing Control Room and dashboard pages.
- Existing homepage messaging: "Bring the idea once" and continuity-focused assistant direction.

## 4. Components To Remove From The Primary Layout

- Permanent Project Intelligence sidebar.
- Permanent lineage, important files, suggested next action cards.
- Permanent top status-card row.
- Permanent backend action buttons.
- Permanent Current Work block when no project or relevant work is selected.
- Duplicate Previous Work block.
- Any backend-module-like navigation in Standard Experience.
- Technical status text before a project is connected.

## 5. Components To Move Into Conversation Cards

- Work status.
- Ready-for-review summaries.
- File inspection results.
- Suggested next action.
- Project lineage.
- Verification status.
- Important files.
- Pause/resume state.
- Approval/return decisions.
- Technical-detail links.

These should appear only when relevant to a conversational turn.

## 6. Components To Move Into Advanced Mode

- WorkCell lists.
- FileCell lists.
- Seed queue internals.
- Verification logs.
- Repository intelligence details.
- Manifest state.
- Runtime ports.
- Symbol counts.
- Constellation graphs.
- Assistant adapter state.
- Trust and authority state.
- Raw technical activity.

## 7. New Left-Sidebar Structure

The left sidebar should represent where the user is working, not which backend system they are operating.

Recommended structure:

```text
Home

Projects
  SCI
  SRT-1
  SoulSonus
  Housing
  Atmosphere

+ Add Project

Recent
Reviews
Activity

Advanced
```

Clicking a project opens that project's conversation. SRT-1 handles the project identity, active seed, WorkCell, recall, verification, and assistant context behind the scenes.

## 8. New Center Conversation Structure

The center conversation becomes the workspace.

Example:

```text
SRT-1

SCI

Welcome back.

Since your last session:
- Authentication work is ready for review.
- Documentation work is still active.
- No verification failures were found.

What would you like to do?
```

The message input remains persistent at the bottom.

## 9. Project Onboarding Flow

Project onboarding is separate from an active workspace.

Step 1:

```text
Welcome to SRT-1

Connect your first project.

[Choose Folder]
[Connect GitHub]
[Upload Project]
[Use Current Folder]
```

Step 2:

```text
SRT-1 is preparing your project.

Reading project files
Understanding project structure
Preparing project memory
Creating focused workspaces
Getting everything ready
```

Step 3:

```text
Your project is ready.

What would you like to accomplish first?
```

Then enter the project conversation.

## 10. Existing-Project Flow

If projects exist, the user lands in the Standard Experience with project navigation on the left and the selected project's conversation in the center.

Previous work is represented through:

- project selection
- conversation history
- contextual "while you were away" summary
- review cards
- active work cards

There should not be a large separate "Continue Previous Work" section by default.

## 11. Conversation Action Model

The user expresses intent naturally.

Examples:

```text
Continue the authentication cleanup.
Explain what Codex changed.
Check the affected files.
Start a new mobile implementation.
Pause documentation work.
Review what is ready.
Return the latest change for revision.
Show me the technical details.
```

SRT-1 maps these intents to existing backend capabilities:

- project selection
- seed creation
- seed continuation
- WorkCell activation
- file inspection
- verification
- assistant routing
- review decisions
- Control Room deep links

## 12. Contextual-Card System

Conversation cards should appear only when needed.

Work status card:

```text
Authentication

Status: Working
Assistant: Codex
3 files changed
18 tests passing

[Continue]
[Pause]
[Open Files]
```

Review card:

```text
Ready for Review

What changed:
- token refresh logic improved
- regression tests added
- public login behavior preserved

Checks:
- 18 tests passed
- no scope violations

[Approve]
[Return for Changes]
[Explain]
[Technical Details]
```

File card:

```text
Important File

auth/token_refresh.py

SRT-1 found the retry logic here.

[Open]
[Explain]
[Compare Changes]
```

Project preparation card:

```text
Preparing Your Project

Reading files
Understanding project structure
Preparing project memory
Creating focused workspaces

Ready.
```

## 13. Control Room Deep-Link Model

Advanced access should remain available, but contextual.

Examples:

- "Show verification" opens the relevant verification view.
- "Show affected files" opens the relevant FileCell or file view.
- "Open workspace" opens the relevant WorkCell.
- "Show repository health" opens Repository Intelligence.
- "Show all active work" opens Constellation or Active Work.

The Standard Experience should avoid sending users to a generic Control Room page when the technical object is already known.

## 14. Existing Backend Routes To Reuse

Reuse existing routes where possible:

- `/dashboard-summary`
- `/api/v1/repositories/register-path`
- `/api/v1/repositories/browse-folder`
- `/api/v1/repositories/register-current`
- `/api/v1/workcells`
- `/api/v1/workcells/{queue_seed_id}/messages?limit=20`
- `/api/v1/workcells/{queue_seed_id}/chat`

Potentially reuse existing dashboard anchors:

- `dashboard.html#workcells`
- `dashboard.html#verification`
- `dashboard.html#repositories`
- `dashboard.html#constellation`

Exact anchors should be verified against the current dashboard implementation during implementation.

## 15. Existing Frontend Components To Reuse

- Dark SRT-1 visual identity.
- Existing header branding.
- Existing project registration controls.
- Existing message rendering style.
- Existing WorkCell message fetch.
- Existing WorkCell chat post.
- Existing Advanced / dashboard links.
- Existing public homepage continuity messaging.

## 16. New Components Required

- `ProjectSidebar`
- `MissionWorkspace`
- `ConversationMessage`
- `ConversationCard`
- `ActionMenu`
- `ProjectOnboarding`
- `ProjectPreparationCard`
- `ReviewCard`
- `WorkStatusCard`
- `FileCard`
- `TechnicalLinkCard`

These can be implemented inside `experience.html` first, then extracted later if the frontend becomes modular.

## 17. State Model

Suggested client-side state:

```json
{
  "selected_project_id": "srt1-core",
  "selected_project_name": "SRT-1",
  "project_connected": true,
  "conversation_id": "project-srt1",
  "active_queue_seed_id": "seed-id-or-null",
  "active_work": [],
  "recent_projects": [],
  "messages": [],
  "runtime_available": true,
  "pending_review_count": 0,
  "last_check": "just now"
}
```

The frontend should not create a second source of truth. It should derive this from existing SRT-1 runtime responses and local UI selection.

## 18. Screen Wireframe

Target Standard Experience:

```text
SRT-1                                      [Advanced] [Account]
----------------------------------------------------------------
Projects              SCI

Home                  Welcome back.

SCI                   Since your last session:
SRT-1                 - Authentication work is ready for review.
SoulSonus             - Documentation is still active.
Housing               - No verification failures were found.
Atmosphere

+ Add Project         What would you like to do?

Recent                [Review Card appears when relevant]
Reviews               [File Card appears when relevant]
Activity              [Work Status Card appears when relevant]

                      Tell SRT-1 what you want to plan, build,
                      inspect, continue, or review...
```

No permanent right-side intelligence panel.
No permanent top backend status cards.
No permanent system-action button row.

## 19. Mobile Behavior

On mobile:

- Project sidebar collapses into a project switcher.
- Conversation takes the full screen.
- Message input remains sticky at the bottom.
- Contextual cards stack inside the conversation.
- Advanced access remains in the header menu.
- Add Project appears as a prominent onboarding action when no project exists.

## 20. Test Plan

Update frontend messaging tests to verify:

- Standard Experience does not contain permanent Project Intelligence sidebar.
- Standard Experience does not contain permanent backend stat card row.
- Standard Experience does not expose backend module names in primary navigation.
- Standard Experience keeps continuity messaging.
- Standard Experience includes project navigation.
- Standard Experience includes a single active conversation workspace.
- Standard Experience includes project onboarding copy.
- Standard Experience includes contextual card strings.
- Advanced / Control Room link remains available.
- Existing backend route strings remain present where used.

Run:

```text
python -m unittest tests.test_public_website_messaging tests.test_workcell_runtime tests.test_seed_queue_compatibility tests.test_task_response_identity
```

## 21. Minimum Implementation Batches

Batch 1:

- Remove permanent right-side intelligence panel.
- Remove permanent top status cards.
- Rename center surface to Mission or Workspace.
- Convert current intelligence content into seeded conversation messages/cards.
- Keep backend route integration unchanged.

Batch 2:

- Replace system-action button row with compact action menu.
- Add contextual cards for review, work status, file, project preparation.
- Update tests.

Batch 3:

- Restructure left sidebar into project navigation.
- Add project onboarding state.
- Remove bulky Previous Work view from the default path.

Batch 4:

- Add contextual Control Room deep-link helpers.
- Refine mobile behavior.
- Verify route anchors against dashboard implementation.

## 22. Files That May Be Modified

- `srt1_platform/pwa/experience.html`
- `tests/test_public_website_messaging.py`
- `srt1_platform/pwa/dashboard.html` only if a deep-link anchor must be added without changing dashboard behavior
- Documentation files related to Standard Experience design, if needed

## 23. Files That Must Not Be Modified

- `srt1_code_indexer/engine.py`
- Backend WorkCell runtime modules unless a missing route is explicitly required later
- Seed queue core logic
- Verification core logic
- Recall / Reflection / Reinjection core logic
- Constellation backend logic
- Existing Control Room behavior except for safe anchor/link support

## Final Rule

The Standard Experience is not a simplified dashboard.

It is an intelligent conversational workspace that operates the full SRT-1 platform on the user's behalf.

The Control Room shows the machinery.

The Standard Experience lets the user direct the machinery through conversation.
