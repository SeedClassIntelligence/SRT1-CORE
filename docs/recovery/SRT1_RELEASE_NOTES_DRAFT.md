# SRT1 Release Notes Draft

## Current Release Position

SRT-1 Core is a local repo-continuity and alignment partner for AI coding assistants. It can register a repository, build repo intelligence, create FileCells and WorkCells, plant seeds, prepare bounded assistant handoff packages, expose dashboard/experience surfaces, track continuity state, and verify WorkCell boundaries.

## Release-Clean Claims

- Core is local-first by default.
- Core understands signed/unsigned, verified/unverified, and lineage present/missing trust states.
- Seed Signature is an external signing platform. Core can prepare signing evidence and fail closed when the external authority is unavailable.
- Assistant execution is bounded by WorkCell allowed paths, restricted paths, verification, and human review.
- Provider API keys are session-scoped unless the developer explicitly opts into their own local storage later.

## Known Limitations Before Public Tag

- SRT-1 Core does not ship private Seed Signature authority, private keys, SCIA memory/security implementation, SION internals, private audit chain, or Enterprise backend.
- WorkCell execution handoff is available, but fully autonomous multi-agent orchestration remains a future hardening area.
- Slack and additional communication surfaces should plant seeds into the same WorkCell path, but production install flows require a separate release gate.
- Website pricing/payment copy must remain PayPal-first and should be reviewed before paid launch.
- Some dashboard/website visual assets still need polish for final product packaging.

## Required Verification Before Tag

- Focused WorkCell boundary tests pass.
- Seed identity and task response tests pass.
- Public website messaging tests pass.
- Package build and install smoke pass from a clean environment.
- Boundary scan confirms private/Enterprise implementation is excluded from public Core.
