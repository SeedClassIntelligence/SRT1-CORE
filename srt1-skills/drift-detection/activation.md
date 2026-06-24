# Drift Detection — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Reflection Interval | `SRT.trace_operation()` detects `operation_count % reflection_interval == 0` | Every N (default 3) operations |
| Forced reflection | Manual call to `SRT.force_reflection()` | On demand |
| Interaction Logging | MCP tool `srt1_log_interaction` invoked by Assistant | Every 3 agent interactions |

## Pre-conditions

- An active `Seed` must be planted and marked as active (`_active_seed_id` is set).
- Intent keywords must be populated in the active Seed structure.
- Tracking history list `_ops_since_last_reflection` is not empty.

## Post-conditions

- Coherence score calculated.
- `ReflectionCheckpoint` generated and stored in memory.
- `injection_directive` text generated and ready for assistant context update.
