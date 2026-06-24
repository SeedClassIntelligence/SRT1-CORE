# SRT1 Context Loading Map

When an AI session begins a task, inject only the slices needed for that authority. SRT-1 is a repo-continuity and alignment partner for AI coding assistants, so context must be relevant, bounded, and current.

| Task Type | Required Context Slices |
| --- | --- |
| Repo Understanding / AST | Constitution + `SRT1_DECISIONS.md` + indexer/parser/manifest context |
| Continuity / Seed Lifecycle | Constitution + `SRT1_CURRENT_STATE.md` + seed/build-plan state context |
| Reflection / Drift | Constitution + `SRT1_DECISIONS.md` + doctrine scanner, consistency auditor, trace context |
| Recall | `SRT1_CURRENT_STATE.md` + `SRT1_DECISIONS.md` + approved summaries only |
| Reinjection / MCP | Constitution + assistant interface docs + AGENTS/CLAUDE/Cursor context rules |
| Context Isolation / FileCell | Constitution + FileCell/manifest-deriver contracts + allowed/forbidden path policy |
| Verification / Stitch Prep | Constitution + verification contracts + change proposal and post-execution verification context |
| Human Co-Creation / PWA | Constitution + dashboard/PWA doctrine + approval/review/status context |
| Constellation | Constitution + workspace connector/operational registry context + no-contamination rules |
| Trust Awareness | `SRT1_DECISIONS.md` + trust metadata vocabulary; never private signing implementation |
| Private / Enterprise Review | Boundary inventory + private exclusion list only; do not inject private implementation |

## Tiered Context Serving

The future `srt1_get_context` implementation should serve:

- minimal context: only current constraints and the active authority target
- task-specific context: targeted slices resolved from this context index
- constitutional context: human sovereignty and non-autonomous operation rules
- verification context: change proposal, manifest, diff, and post-execution evidence
- historical evidence on demand: legacy walkthroughs or prior phase records only when explicitly requested

## Walkthrough Archival Policy

- Walkthroughs remain immutable evidence, not primary runtime context.
- Completed phase walkthroughs should be summarized into `SRT1_CURRENT_STATE.md`, `SRT1_DECISIONS.md`, `SRT1_FRONTIER.md`, and this context index when they change active architecture.
- After summarization, historical walkthroughs should be removed from active context to prevent context suffocation and stale authority bleed.

## Trust Context Rule

Core may load trust metadata states such as signed/unsigned, verified/unverified, and lineage present/missing. Core must not load private Seed Signature authority, private keys, SCIA memory implementation, SCIA security implementation, SION internals, private audit chain, or Enterprise backend code into public context.