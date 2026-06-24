# SRT1 Legacy Docs Review

Date: 2026-06-24

## Purpose

This review explains why several tracked root-level documents were removed from
public Core source truth during cleanup.

The goal is not to erase knowledge. The goal is to keep public SRT1 Core focused
on the recovered product boundary:

- repo continuity
- assistant alignment
- local repo intelligence
- seed lifecycle
- recall/reinjection
- workcell/context isolation
- verification
- human cockpit
- constellation awareness
- trust-state awareness

## Reviewed Deleted Documents

| Document | Decision | Reason |
| --- | --- | --- |
| `CTO_HANDOVER_TO_CLAUDE.md` | Remove from public Core root. | Stale handoff document tied to a prior PWA/payment-gating phase. It points to `developer-pwa/` as source after Core selected `srt1_platform/pwa/` as canonical. |
| `PRODUCT_ARCHITECTURE.md` | Remove from public Core root. | Broader SCIA/SION/product-stack doctrine, not current public SRT1 Core source truth. Valuable concepts should live in private or recovery context, not as public Core architecture authority. |
| `SRT1_ENFORCEMENT_MODE.md` | Remove from public Core root. | Contains useful enforcement doctrine but is SION/SCIA-heavy and stronger than the current Core boundary. Public Core keeps Context Isolation and Verification; autonomous enforcement/SION doctrine remains private/review. |

## Preserved Recovery Docs

The following Core-safe recovery documents were moved under `docs/recovery/`:

- `SRT1_AUTHORITY_CONTRACTS.md`
- `SRT1_AUTHORITY_RUNTIME_CLASSIFICATION.md`
- `SRT1_STATE_OWNERSHIP.md`

## Local Review-Only Docs

The following local files are intentionally ignored until explicitly reviewed:

- `PHASE_*_WALKTHROUGH.md`
- `SRT1_CONSTITUTION.md`
- `docs/SRT1_Code_Indexer_Complete_Reference.docx`

These may contain valuable private, Enterprise, SION, or broader ecosystem
doctrine. They should not be promoted into public Core without boundary review.

## Follow-Up

If any deleted root document contains reusable public Core material, restore only
the relevant section into `docs/recovery/` or a public Core guide after removing
private implementation claims and Enterprise/SION authority language.
