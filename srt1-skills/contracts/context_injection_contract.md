# Context Injection Contract
**Contract ID:** `SRT1-CONTRACT-CTXINJECT-001`
**Between:** SRT-1 Engine ↔ AI Assistant Files
**Version:** 1.0.0
**Status:** CANONICAL

---

## Doctrine
SRT-1 illuminates. This contract governs how SRT-1 makes its knowledge available
to AI coding assistants (Claude, Cursor, Copilot, etc.) through structured context files.
SRT-1 writes to designated context files only. It does not write to source files.

---

## Purpose
Define what context SRT-1 injects, into which files, at what trigger points,
and with what boundaries. Context injection is how SRT-1 keeps AI assistants
aligned to repo architecture, boundaries, and current task scope.

---

## Parties

| Party | Role |
|-------|------|
| **SRT-1 Engine** | The injector. Writes structured context to designated files only. |
| **AI Assistant Files** | The targets. AGENTS.md, CLAUDE.md, .cursorrules, .github/copilot-instructions.md |
| **execution actor / operator** | May request context bundle generation via Seed Intake Contract. |

---

## Injection Target Files

| File | Assistant | Purpose |
|------|-----------|---------|
| `AGENTS.md` | General / Claude Code | Primary task context, module map, constraints |
| `CLAUDE.md` | Claude (all) | Claude-specific cognitive context and boundaries |
| `.cursorrules` | Cursor | Cursor editor rules derived from repo architecture |
| `.github/copilot-instructions.md` | GitHub Copilot | Copilot-specific constraints |
| `srt1-context/current_bundle.json` | SRT-1 / execution actor internal | Machine-readable context bundle |
| `srt1-context/module_map.json` | SRT-1 / execution actor internal | Symbol and dependency map |

---

## Context Injection Schema

```yaml
injection_id: string            # Format: CTX-{sandbox_id}-{timestamp}
sandbox_id: string              # Source sandbox
seed_id: string | null          # Seed that triggered this injection (if applicable)
proposal_id: string | null      # ChangeProposal context is being injected for (if applicable)
injected_by: string             # SRT-1 Engine instance
injected_at: datetime
trigger: enum                   # See Injection Triggers below

# Content blocks
context_bundle:
  repo_summary: string          # 200-word max overview of repo purpose and architecture
  current_task: string          # What this seed/task is trying to accomplish
  module_map: object            # Symbol map, file structure, key dependencies
  active_filecell: object | null    # Current FileCell boundaries (read/write limits for AI)
  boundary_rules: list[string]      # Explicit rules AI must follow for this session
  forbidden_patterns: list[string]  # Code patterns AI must never generate
  architecture_principles: list[string]  # Core architectural rules from repo doctrine
  drift_warnings: list[string]  # Active drift alerts from SRT-1 drift detection
  coherence_score: float | null # Last verification coherence score

# Targets
injected_into: list[string]     # Which files were updated
injection_mode: enum            # FULL_REPLACE | APPEND | MERGE | SECTION_UPDATE

# Validation
injection_validated: boolean    # Whether SRT-1 confirmed inject succeeded
previous_injection_id: string | null  # For diffing and continuity
```

---

## Injection Triggers

| Trigger | When | Context Scope |
|---------|------|--------------|
| `SEED_INTAKE` | New seed received | Full context bundle |
| `REPO_INDEXED` | After repo index completes | Module map + architecture |
| `TASK_SCOPED` | When ChangeProposal is created | Task + FileCell boundaries |
| `EXECUTION_STARTED` | When execution actor begins | FileCell + forbidden patterns |
| `VERIFICATION_COMPLETE` | After verification | Coherence score + drift warnings |
| `DRIFT_DETECTED` | When drift is flagged | Drift warnings + boundary reinforcement |
| `MANUAL` | Operator request | Full context bundle |
| `SCHEDULED` | Periodic refresh | Module map refresh |

---

## Context Bundle Rules

### SRT-1 SHALL:
- Write context to designated injection targets ONLY (listed above)
- Never write to source files — not even comments
- Generate context from its own index — never from AI assistant output
- Redact `forbidden_paths` and `excluded_paths` from all context bundles
- Include `boundary_rules` in every injection regardless of trigger
- Emit `context_bundle_generated` event on every injection
- Preserve `previous_injection_id` for continuity tracking

### Content Constraints:
- `repo_summary`: 200 words max. No implementation detail. Purpose + architecture only.
- `current_task`: 100 words max. What, not how.
- `boundary_rules`: Plain language. Numbered. AI must be able to follow literally.
- `forbidden_patterns`: Specific, not vague. "Never use eval()" not "avoid unsafe code."
- `drift_warnings`: Only active, unresolved drift. Remove on verification pass.
- `module_map`: Machine-readable. Do not embed implementation in context files.

### SRT-1 SHALL NOT:
- Inject source code into context files
- Include file contents from `excluded_paths` in any bundle
- Expose FileCell internal authorization tokens to AI context
- Inject context that contradicts external authorization
- Generate context for files outside the active sandbox

---

## Injection Modes

| Mode | Behavior | When to Use |
|------|---------|-------------|
| `FULL_REPLACE` | Overwrites entire target file | New sandbox, new seed |
| `APPEND` | Adds to end of target file | Incremental updates |
| `MERGE` | Updates specific keys in structured files | JSON context files |
| `SECTION_UPDATE` | Updates named section within a markdown file | AGENTS.md, CLAUDE.md section refresh |

**Default for AGENTS.md and CLAUDE.md:** `SECTION_UPDATE` with SRT-1-managed sections.
**Default for JSON context files:** `MERGE`.
**Default for new sandboxes:** `FULL_REPLACE`.

---

## SRT-1 Section Markers

SRT-1 manages specific sections in AGENTS.md and CLAUDE.md using markers:

```markdown
<!-- SRT1:START context_bundle -->
[SRT-1 managed content here]
<!-- SRT1:END context_bundle -->
```

Content outside SRT-1 markers is not modified by SRT-1 injection.
Content inside SRT-1 markers is fully managed by SRT-1 and will be overwritten on update.

---

## Events Emitted

```
context_bundle_generated
context_injection_started
context_injection_completed
context_injection_failed
context_drift_warning_injected
context_cleared              # When sandbox is archived or reset
```

---

## NEEDS_SOURCE
- [ ] Whether SRT-1 writes context files directly or through a file broker
- [ ] Whether Cursor rules file has a specific schema SRT-1 must conform to
- [ ] How SRT-1 handles merge conflicts if a human has manually edited AGENTS.md
- [ ] Whether `srt1-context/` directory is gitignored or committed
- [ ] Whether AI assistants have a mechanism to signal that context is stale
- [ ] Maximum size of `module_map.json` before it needs to be chunked
