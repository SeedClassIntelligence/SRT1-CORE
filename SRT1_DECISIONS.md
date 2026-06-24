# SRT1 Architectural Decisions & Constraints

## Core Doctrine

1. SRT-1 Core is a repo-continuity and alignment partner for AI coding assistants.
2. Core includes local repo understanding, continuity, reflection, recall, reinjection, context isolation, verification, human co-creation, constellation awareness, and trust awareness.
3. Seed is a continuity object, not merely a task. Seed state must preserve active, pending, completed, terminated, and partial-completion continuity.
4. Reflection is a governing principle, not merely a scanner. Reflections and coherence scores are interpretive continuity metrics, not ground truth.
5. Recall is first-class. Historical evidence may be retrieved deliberately, but stale walkthroughs must not override canonical state.
6. Reinjection is first-class. AGENTS.md, CLAUDE.md, Cursor context, MCP, and local APIs are alignment surfaces.
7. FileCell is a local containment concept, not Enterprise-only.
8. Verification prepares evidence and checkpoints. It does not create merge authority.
9. PWA and dashboard surfaces are human observability/review surfaces, not direct execution controllers.
10. Constellation federates independent SRT-1 engines. It must not contaminate context across repos unless explicitly allowed.
11. Trust Awareness is metadata/vocabulary in Core. Core may understand signed/unsigned, verified/unverified, and lineage present/missing states.
12. Core does not ship private Seed Signature authority, private keys, SCIA memory implementation, SCIA security implementation, SION internals, private audit chain, or Enterprise backend.
13. Enterprise/private integrations are optional and must fail closed when unavailable.
14. Merge authority does not exist in Core. SRT-1 cannot self-heal, auto-remediate, or autonomously merge code.
15. Test honesty is mandatory. Unavailable dependencies must return INCONCLUSIVE, not fake a PASS.

## Public Boundary Decisions

- Public contracts and placeholders may remain public when they expose vocabulary or interfaces without private implementation.
- A file is not private merely because it mentions Enterprise.
- A file is not public merely because it lives under `srt1_platform` or `srt1_pro`.
- FileCell, manifest derivation, verification, and operational registry are Core/Pro candidates only after private dependencies are removed or abstracted.
- PWA sources must not be moved until the canonical source is approved.

## Archival Override Protection

No historical walkthrough should override this file unless `SRT1_CURRENT_STATE.md` and `SRT1_DECISIONS.md` are explicitly amended. Legacy walkthrough text is stale narrative unless promoted into canonical state.