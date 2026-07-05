# Context Injection Contract

**Contract ID:** `SRT1-CONTRACT-CTXINJECT-001`
**Between:** SRT-1 Reinjection and Assistant Surfaces
**Status:** Public Core

## Purpose

Define how SRT-1 delivers bounded context to assistants through MCP responses,
assistant files, dashboard views, and WorkCell packages. Context Injection
consumes prepared RecallPacket-shaped data, manifest summaries, WorkCell scope,
reflection warnings, and trust metadata. It does not own recall retrieval.

## Allowed Targets

```text
AGENTS.md
CLAUDE.md
.cursorrules
.github/copilot-instructions.md
workcell.md
.srt1 runtime/context state
MCP/API context responses
```

Assistant files are delivery targets, not source authority. Generated symbol
maps and full repo intelligence belong in manifests/context outputs, not in
standing instruction files.

## Context Packet Fields

```yaml
injection_id: string
queue_seed_id: string | null
srt_anchor_id: string | null
workcell_id: string | null
manifest_hash: string | null
freshness_state: fresh | stale | degraded | unknown
trust_state: signed | unsigned | verified | unverified | degraded | unknown
source_packets: list[RecallPacket]
boundary_rules: list[string]
forbidden_paths: list[path]
drift_warnings: list[string]
degradation_reason: string | null
targets: list[string]
```

## Guarantees

- Context is bounded to the active repository, seed, and WorkCell scope.
- `queue_seed_id` remains canonical when seed-scoped.
- `srt_anchor_id` is preserved as reflection metadata only.
- Trust and freshness metadata survive delivery.
- Forbidden paths, secrets, keys, and private implementation details are
  excluded.
- Raw source dumps are not injected unless explicitly allowed by WorkCell scope.

## Refusal Conditions

- No registered repository sandbox exists.
- WorkCell/FileCell scope is required but unavailable.
- Context would include forbidden paths or secrets.
- Context would cross project boundaries without explicit approval.
- Required Seed Signature attribution is missing and enforcement mode is
  required.

## Events

```text
context_packet_created
context_injection_started
context_injection_completed
context_injection_failed
context_drift_warning_injected
context_degraded
```
