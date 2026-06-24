# Post-Execution Verification — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Pre-execution snapshot | `PostExecutionVerifier.capture_snapshot(proposal_id, files_to_watch)` | Called by `ExecutionBridge` BEFORE execution actor dispatch |
| Post-execution verification | `PostExecutionVerifier.verify(proposal_id, files_write, ...)` | Called by `ExecutionBridge` AFTER completion detected |

## Pre-conditions

- `ChangeProposal` is validated and has `expected_verification` block populated.
- Pre-execution snapshot (`capture_snapshot`) has been stored for the `proposal_id`.
- execution actor has completed (or failed) execution — signal file or quiet period detected.

## Post-conditions

- `VerificationResult` is returned with verdict: `VERIFIED`, `PARTIAL_PASS`, or `FAILED`.
- Audit events emitted: `verification_passed` or `verification_failed` to event log.
- On `FAILED`: revision may be triggered (per ChangeProposal revision strategy).
