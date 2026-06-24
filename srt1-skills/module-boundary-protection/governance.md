# Module Boundary Protection — Governance

## Boundary Rules

| Rule | Enforcement |
|------|-------------|
| Read-Only Component | Never writes or modifies files; only validates paths against manifest. |
| Path Canonicalization | `os.path.realpath()` applied to all inputs — blocks symlink escape attacks. |
| Hardcoded Forbidden Patterns | `ALWAYS_FORBIDDEN_PATTERNS` (`.env`, `.git`, `*.key`, `*secret*`) are non-overridable. |
| `AGENTS.md` Exclusion | `AGENTS.md` never included in `allowed_reads` unless explicitly authorized with logged reason. |
| Semantic Escalation | If resolved files carry `AUTH_SECURITY` or `CRYPTOGRAPHIC` role tags, domain sponsorship is required or derivation is blocked entirely. |

## Who Can Call This Skill

| Caller | Authorized? |
|--------|-------------|
| `FileCellGuard` | ✅ Primary enforcer |
| `LeastPrivilegeManifestDeriver` | ✅ Derivation-time checks |
| execution actor | ❌ execution actor is the subject of enforcement, not the caller |
| External API | ❌ No external exposure |

## execution actor Interaction

execution actor is the entity being constrained. Every file read or write that execution actor attempts is validated through this skill. A violation immediately raises an exception and emits a CRITICAL audit event. execution actor cannot override or disable this protection.
