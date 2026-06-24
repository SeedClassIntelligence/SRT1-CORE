# Audit Event Emission — Inputs & Outputs

## Inputs (per `event_logger.record()` call)

| Input | Type | Description |
|-------|------|-------------|
| `component` | `str` | Module emitting the event (e.g., `engine`, `verifier`, `lease_manager`) |
| `operation` | `str` | Event name / type (e.g., `repo_index_completed`) |
| `severity` | `str` | `INFO`, `WARN`, `HIGH`, or `CRITICAL` |
| `actor` | `str` | Who triggered: `engine`, `execution_actor`, `user`, `governance_monitor` |
| `input_hash` | `str` (optional) | SHA-256 hash of input data |
| `output_hash` | `str` (optional) | SHA-256 hash of output data |
| `result_status` | `str` (optional) | `SUCCESS`, `FAILURE`, or `BLOCKED` |
| `detail` | `Dict` | Event-specific payload |

## Outputs

| Output | Type | Destination |
|--------|------|-------------|
| Event Log row | event record | `{state_dir}/audit/event_log` |
| Chain hash | `str` | Appended to chain in event log row |
| External signing handoff entry | event record | `external_signing_handoff` table (CRITICAL events only) |
