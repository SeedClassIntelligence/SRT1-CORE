# Audit Event Emission — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Append-Only | Events cannot be deleted or updated — SQLite schema enforces this. |
| Write-Once Per Event | No `UPDATE` queries exist on the events table. |
| execution actor Isolation | Event Log is not in execution actor's FileCell. execution actor cannot read or write the event log directly. |
| External Trust Rotation | Core records metadata and does not manage signing keys. |
| Critical Auto-Signing | `CRITICAL` severity events are immediately queued for external Seed Signature authority. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| All SRT-1 modules | ✅ Any component may emit events to the event log |
| `GovernanceMonitor` | ✅ Emits governance health events |
| execution actor (direct) | ❌ execution actor is never a direct event log caller |
| External API | ❌ Event Log writes are internal-only |
