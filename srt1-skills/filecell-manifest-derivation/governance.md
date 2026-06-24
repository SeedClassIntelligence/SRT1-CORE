# FileCell Manifest Derivation — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Source of Read-Only | Derivation uses the `symbol_table` and `call_graph` to compute boundaries. Never modifies source files. |
| H.1 Enforcement | Files in `files_likely` must exist in `symbol_table` or be valid new creation targets — unknown files are REJECTED. |
| Depth Cap | BFS dependency walk is capped at depth=2 to prevent scope explosion. |
| Escalation Block | Files with `AUTH_SECURITY` or `CRYPTOGRAPHIC` roles require domain sponsorship or derivation raises an exception. |
| ALWAYS_FORBIDDEN_PATTERNS | Hardcoded forbidden paths are always computed and always excluded from any read/write set. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| `ExecutionBridge` | ✅ Orchestrates derivation before dispatch |
| external authorization authority (optional external platform) | ✅ Pre-authorization gate |
| execution actor | ❌ execution actor is the subject of the derived cell, not the caller |

## execution actor Interaction

execution actor receives the derived manifest as a read-only constraint. It does not participate in derivation, cannot modify the manifest, and cannot expand its own boundaries. The manifest is signed before execution actor executes.
