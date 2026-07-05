# Drift Detection Skill

> **Skill ID:** `SRT1-SKILL-004`
> **Module:** SRT Core (`srt.py`) + Reflection
> **Authority:** Reflection
> **Classification:** Public Core
> **Mutates Source:** Never

## Purpose

Drift Detection identifies when assistant activity, WorkCell execution, or
context progression is moving away from the planted seed, approved scope, or
current continuity state.

It is a detective/reflection skill. It produces coherence findings, warnings,
and reinjection cues. Public Core does not autonomously rewrite code or repair
the project because drift was detected.

## Activation

| Trigger | Source | Frequency |
|---|---|---|
| Reflection interval | `SRT.trace_operation()` / tracing loop | Every configured N operations |
| Forced reflection | `SRT.force_reflection()` or dashboard/API request | On demand |
| MCP interaction logging | Assistant tool interaction | Periodic / configured |
| Completion review | Continuity / Verification handoff | Before acceptance |
| Context refresh | Reinjection path | When drift warning should be included |

## Preconditions

- A canonical `queue_seed_id` exists when work is seed-scoped.
- `srt_anchor_id` may exist as reflection/coherence metadata.
- Seed intent, keywords, or objective text are available.
- Recent operations, trace metadata, or WorkCell activity are available.

## Inputs

| Input | Type | Source |
|---|---|---|
| Canonical seed identity | Dict/string | Continuity / seed queue |
| SRT anchor metadata | Dict/string | SRT reflection anchor |
| Seed objective / intent | String/list | Continuity / SRT anchor |
| Recent operations | List | Tracing / WorkCell runtime |
| Recent trace metadata | List/dict | Tracing system |
| WorkCell scope | Dict | Context Isolation |

## Outputs

| Output | Type | Meaning |
|---|---|---|
| `coherence_score` | Float | Bounded score from 0.0 to 1.0 |
| `coherence_status` | Enum/string | `ON_TASK`, `MINOR_DRIFT`, `MAJOR_DRIFT`, `SEED_LOST` |
| `drift_indicators` | List | Evidence explaining the finding |
| `ReflectionCheckpoint` | Dataclass/dict | Full checkpoint record |
| Reinjection cue | String/dict | Context warning for Reinjection to deliver |

## Coherence Model

The current implementation compares seed intent keywords with recent operation
language and metadata. That model is intentionally simple and must label
confidence honestly.

```text
ON_TASK:     score >= 0.8
MINOR_DRIFT: score >= 0.5
MAJOR_DRIFT: score >= 0.2
SEED_LOST:   score < 0.2
```

Future implementations may use richer manifest, WorkCell, verification, and
recall evidence, but Reflection still owns findings rather than remediation.

## Runtime Responsibilities

1. Compare recent activity against the seed objective and WorkCell scope.
2. Produce bounded coherence scores.
3. Preserve `queue_seed_id` as canonical lifecycle identity.
4. Preserve `srt_anchor_id` as reflection metadata when available.
5. Emit drift findings with evidence and confidence.
6. Provide Reinjection with warning metadata.
7. Avoid autonomous remediation in public Core.

## Boundary Rules

| Rule | Enforcement |
|---|---|
| Read-only observer | Does not mutate source files |
| Detective-only Core behavior | Findings do not automatically rewrite code |
| Continuity identity | Uses `queue_seed_id` as canonical seed identity |
| SRT anchor separation | SRT seed/anchor remains reflection metadata |
| Execution actor isolation | Execution actor cannot clear or bypass drift findings |
| Scope awareness | Findings should consider WorkCell/FileCell boundary when available |

## Verification

| Check | Success condition |
|---|---|
| Checkpoint generation | Reflection checkpoint is created at interval or on demand |
| Score boundedness | Score remains between 0.0 and 1.0 |
| Drift sensitivity | Unrelated operations lower coherence and change status |
| Identity preservation | Findings include `queue_seed_id` and optional `srt_anchor_id` |
| Reinjection metadata | Drift warning can be delivered without source mutation |

Failure indicators include missing checkpoints, impossible scores, erased
identity metadata, status/score mismatch, or drift findings that attempt to
execute remediation.

## Events

| Event | Severity | Status |
|---|---|---|
| `trace_start` | info | exists/planned depending on runtime path |
| `trace_complete` | info | exists/planned depending on runtime path |
| `coherence_checkpoint_fired` | info | planned |
| `drift_warning_emitted` | warning | planned |

## Source of Truth

- `srt1_code_indexer/srt.py`
- `srt1_platform/tracing_system.py`
- Continuity seed queue state
- WorkCell runtime state when available
