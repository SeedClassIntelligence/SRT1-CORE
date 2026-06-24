# Module Boundary Protection — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Write validation | `FileCellGuard.validate_write(path, manifest)` | Before every execution actor write operation |
| Read validation | `FileCellGuard.validate_read(path, manifest)` | Before every execution actor read operation |
| Manifest derivation | `LeastPrivilegeManifestDeriver.derive()` | Once per seed, before execution begins |
| Semantic escalation check | During derivation — `AUTH_SECURITY` / `CRYPTOGRAPHIC` role detection | During derivation |

## Pre-conditions

- A `FileCellManifest` has been derived for the current seed.
- The `ExecutionLease` is active and unexpired.
- `os.path.realpath()` is applied to all incoming path arguments.

## Post-conditions

- Path validated: returns `True` (permitted) or raises `FileCellBoundaryViolation` (blocked).
- Any violation immediately emits `filecell_boundary_violation` event to event log.
