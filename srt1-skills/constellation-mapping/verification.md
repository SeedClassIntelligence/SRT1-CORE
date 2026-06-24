# Constellation Mapping — Verification

## Success Criteria

| Check | Condition |
|-------|-----------|
| Self-registration | Engine entry exists in `~/.srt1/registry.json` after startup |
| Peer discovery | At least one peer reported in `/api/constellation` response |
| Read-only confirmed | No state-changing calls to peer endpoints |
| Stale peers tolerated | Dead peers return last-known data, not errors |

## Failure Indicators

| Indicator | Meaning |
|-----------|-------|
| Registry missing | `~/.srt1/registry.json` not created at startup |
| All peers stale | No peer engines reachable on expected ports |
| Cross-engine mutation attempted | Constellation API issues POST/PATCH to a peer |
