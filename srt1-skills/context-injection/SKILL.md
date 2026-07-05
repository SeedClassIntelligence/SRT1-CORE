# Context Injection Skill

> **Skill ID:** `SRT1-SKILL-003`
> **Module:** SRT-1 Engine + MCP Server + Reinjection
> **Authority:** Reinjection
> **Classification:** Public Core
> **Mutates Source:** Never

## Purpose

Context Injection delivers bounded SRT-1 context to AI assistant surfaces. It
turns already-retrieved RecallPacket-shaped data, manifest summaries, WorkCell
scope, and reflection warnings into compact context packets, assistant
instruction updates, and MCP responses.

It does not own recall retrieval and it does not perform repository
understanding. It consumes prepared context and delivers it through approved
surfaces.

## Activation

| Trigger | Source | Target |
|---|---|---|
| Engine startup | Context generation path | Assistant files / dashboard state |
| Manifest regeneration | Re-index pipeline | Context candidates and summaries |
| Seed planting | Continuity / seed queue | WorkCell context packet |
| WorkCell package creation | WorkCell runtime | `workcell.md` and package metadata |
| MCP tool call | `srt1_get_context` / related tools | Direct assistant context response |
| Manual refresh | Dashboard/API | Rebuilt context packet |

## Preconditions

- Repo Understanding has produced current or degraded manifest data.
- Continuity has identified the canonical `queue_seed_id` when seed-scoped.
- Recall has returned packet-shaped context when recall is available.
- Context Isolation has defined allowed scope when a WorkCell is active.
- Target assistant/file output path is allowed by policy.

## Inputs

| Input | Type | Source |
|---|---|---|
| Recall packets | List/dict | Recall authority |
| Manifest summary | Dict | Repo Understanding |
| WorkCell/FileCell scope | Dict | Context Isolation |
| Reflection warnings | Dict/list | Reflection |
| Seed identity | Dict | Continuity |
| Trust metadata | Dict | Trust Awareness / Seed Signature attachment metadata |

## Outputs

| Output | Destination |
|---|---|
| Context packet | Reinjection/API/MCP |
| Assistant instruction update | `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or configured target |
| WorkCell instructions | `workcell.md` inside WorkCell package |
| MCP response | JSON-RPC response |
| Pending seed/context state | `.srt1` runtime state, when configured |

Assistant files are delivery targets, not source authority. Generated symbol
maps and full repo intelligence belong in SRT-1 manifests/context outputs, not
standing instruction files.

## Runtime Responsibilities

1. Normalize recall/context inputs into bounded context packets.
2. Preserve identity metadata such as `queue_seed_id` and `srt_anchor_id`.
3. Preserve trust/freshness/degradation metadata.
4. Keep output compact and task-scoped.
5. Deliver context through approved assistant files, MCP, dashboard, or WorkCell
   package surfaces.
6. Avoid raw source dumps unless explicitly allowed by WorkCell scope.
7. Fail closed or mark degraded when recall, manifest, or signing metadata is
   unavailable.

## Boundary Rules

| Rule | Enforcement |
|---|---|
| No source mutation | Writes only generated context/instruction/runtime files |
| No recall ownership | Consumes RecallPackets; does not retrieve private memory itself |
| No raw repo dump | Emits summaries and scoped packets, not whole-repo contents |
| Secret exclusion | Filters forbidden paths and credential patterns |
| Scope respect | Uses WorkCell/FileCell boundary when active |
| Execution actor isolation | Execution actor cannot directly call or control context injection |

## Verification

| Check | Success condition |
|---|---|
| Packet metadata preserved | `queue_seed_id`, `srt_anchor_id`, freshness, trust metadata survive output |
| Context is bounded | Output only references allowed scope |
| No forbidden leakage | Output contains no secret paths/credentials |
| Target files valid | Generated assistant files exist when requested and are non-empty |
| Degraded state visible | Missing recall/manifest/signature metadata is labeled, not hidden |

Failure indicators include stale manifest counts, missing packet identity,
forbidden path leakage, raw source over-injection, or context output that
contradicts WorkCell scope.

## Events

Context Injection may emit public Core observability events:

| Event | Severity | Status |
|---|---|---|
| `context_injection_updated` | info | planned |
| `context_injection_seed_added` | info | planned |
| `context_injection_seed_removed` | info | planned |
| `context_injection_failed` | warning | planned |

## Source of Truth

- `srt1_pro/reinjector.py`
- `srt1_pro/context_bundler.py`
- `srt1_platform/mcp_server.py`
- `srt1_code_indexer/engine.py` orchestration paths
