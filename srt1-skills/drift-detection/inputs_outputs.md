# Drift Detection — Inputs & Outputs

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Active Seed | `Seed` | In-memory `SRT` state | representation containing `original_task`, `intent_keywords`, `domain_context` |
| Recent Operations | `List[str]` | In-memory `SRT` state | List of operations since the last reflection check |
| Recent Trace Metadata | `List[Dict]` | In-memory `SRT` state | Metadata dictionaries from the last N `ExecutionTrace` records |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `coherence_score` | `float` | Score bounded between `0.0` and `1.0` |
| `coherence_status` | `CoherenceStatus` | Classification: `ON_TASK`, `MINOR_DRIFT`, `MAJOR_DRIFT`, or `SEED_LOST` |
| `drift_indicators` | `List[str]` | Diagnoses of drift (e.g. `MISSING_KEYWORDS: ...`) |
| `injection_directive` | `str` | Text instructions to be injected back into AI system context |
| `ReflectionCheckpoint` | Dataclass | Holds the full snapshot of this check's values |
