# FileCell Manifest Derivation — Events

## Emitted Events

| Event | Severity | Emitter | Status |
|-------|----------|---------|--------|
| `filecell_manifest_derived` | INFO | `ManifestDeriver` | ✅ Exists |
| `filecell_semantic_escalation_blocked` | CRITICAL | `ManifestDeriver` | ❌ Needs implementation |

## Expected Detail Payload

For `filecell_manifest_derived`:
```json
{
  "seed_id": "seed_0001_abc12345",
  "cell_id": "cell_abc123...",
  "allowed_reads_count": 8,
  "allowed_writes_count": 3,
  "forbidden_count": 12,
  "dependency_count": 5
}
```
