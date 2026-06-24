# Drift Detection Skill

> **Skill ID:** `SRT1-SKILL-004`
> **Module:** SRT Core (`srt.py`)
> **Classification:** VERIFYING
> **Mutates Source:** ❌ Never

---

## Purpose

Detects when an AI assistant or execution workflow deviates from the original user intent (the planted seed). Compares recent operations against seed keywords and computes a coherence score. Fires a reflection checkpoint every N interactions with an injection directive.

---

## Activation

| Trigger | Source |
|---------|--------|
| Every `reflection_interval` operations | `SRT.trace_operation()` auto-fires `_generate_reflection_checkpoint()` |
| Forced reflection | `SRT.force_reflection()` — manual trigger |
| MCP interaction logging | `srt1_log_interaction` tool (every 3 interactions) |

## Inputs

| Input | Type |
|-------|------|
| Active seed | `Seed` — `original_task`, `intent_keywords`, `domain_context` |
| Recent operations | `_ops_since_last_reflection` list |
| Recent trace metadata | Last N `ExecutionTrace` metadata fields |

## Outputs

| Output | Type |
|--------|------|
| `coherence_score` | `float` — 0.0 to 1.0 |
| `coherence_status` | `CoherenceStatus` — `ON_TASK`, `MINOR_DRIFT`, `MAJOR_DRIFT`, `SEED_LOST` |
| `drift_indicators` | `List[str]` — missing keywords, etc. |
| `injection_directive` | `str` — text block injected back into AI context |
| `ReflectionCheckpoint` | Dataclass with full checkpoint data |

## Coherence Scoring

```
score = len(seed_keywords ∩ recent_words) / len(seed_keywords)

ON_TASK:     score >= 0.8
MINOR_DRIFT: score >= 0.5
MAJOR_DRIFT: score >= 0.2
SEED_LOST:   score < 0.2
```

## Governance

- Read-only: never modifies files or state (only produces checkpoints)
- Does NOT block execution — advisory only in `advisory` mode
- In `enforcement` mode, `check_enforcement()` can return blocking events
- Injection directive is text that gets pushed into AI context — it does not execute

## Verification

| Check | Condition |
|-------|-----------|
| Checkpoint fires | `len(checkpoints)` increases after `reflection_interval` operations |
| Score is bounded | `0.0 <= coherence_score <= 1.0` |
| Drift detected | `MAJOR_DRIFT` or `SEED_LOST` when unrelated operations dominate |

## Events

| Event | Status |
|-------|--------|
| `trace_start` / `trace_complete` | ✅ EXISTS (via TracingSystem → Event Log) |
| *(Checkpoint events are internal to SRT — no dedicated event log event)* | ⚠️ Consider adding `coherence_checkpoint_fired` |

## Source of Truth

- [srt.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_code_indexer/srt.py) — `_generate_reflection_checkpoint()`, `_compute_coherence()`
