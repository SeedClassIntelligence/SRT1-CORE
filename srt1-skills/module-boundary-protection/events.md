# Module Boundary Protection — Events

## Emitted Events

| Event | Severity | Emitter | Status |
|-------|----------|---------|--------|
| `filecell_boundary_violation` | CRITICAL | `FileCellGuard` | ✅ Exists |
| `filecell_manifest_derived` | INFO | `ManifestDeriver` | ✅ Exists |
| `filecell_semantic_escalation_blocked` | CRITICAL | `ManifestDeriver` | ❌ Needs implementation |
| `filecell_agents_md_included` | WARNING | `ManifestDeriver` | ❌ Needs implementation |

## Expected Detail Payload

For `filecell_boundary_violation`:
```json
{
  "cell_id": "cell_abc123...",
  "blocked_path": "/absolute/path/to/blocked/file.py",
  "operation": "write",
  "seed_id": "seed_0001_abc12345"
}
```
