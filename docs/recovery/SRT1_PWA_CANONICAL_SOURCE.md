# SRT1 PWA Canonical Source Decision

Date: 2026-06-24

## Decision

The canonical public Core PWA source is:

```text
srt1_platform/pwa/
```

The local development/prototype copy is:

```text
developer-pwa/
```

`developer-pwa/` should remain available locally for visual experiments and
prototype review, but it should not be tracked as a second shipping PWA source in
public Core.

## Evidence

At decision time, every comparable file in `developer-pwa/` and
`srt1_platform/pwa/` had identical content, excluding
`srt1_platform/pwa/__init__.py`.

That means no product capability is lost by making `srt1_platform/pwa/`
canonical. The change removes duplicated dashboard authority rather than
discarding functionality.

## Product Boundary

The public Core PWA is a human cockpit for:

- observing engine status
- planting seeds
- reviewing blueprints
- approving or rejecting direction
- observing continuity, health, constellation, and workcell state

The public Core PWA must not:

- directly mutate source files
- bypass Workcell boundaries
- bypass verification
- bypass continuity tracking
- imply that public Core ships private memory/security implementations
- imply that public Core ships private Seed Signature keys, signing service, or
  private audit chain

## Trust Position

Seed Signature is a cross-tier trust authority concept. It may sign developer,
Pro, and Enterprise artifacts when the external authority is configured.

Public Core may expose:

- signed / unsigned
- verified / unverified
- lineage present / missing
- fresh / stale / degraded / unknown

Public Core must not ship:

- private Seed Signature authority implementation
- private keys
- private audit chain implementation
- SCIA memory implementation
- SCIA security implementation
- SION internals
- Enterprise backend implementation

## Follow-Up

The next PWA pass should review UI copy and API calls for:

- Core-safe local engine behavior
- optional external trust integrations
- no hard dependency on Enterprise backend
- no private implementation examples
- no autonomous execution-controller posture
