# SRT1 Private Archive Candidates

This note preserves valuable doctrine removed from public Core-facing docs during Batch 2 documentation authority alignment. It is an archive candidate list, not public Core implementation guidance.

Do not stage private implementation, private keys, signing services, SCIA memory/security code, SION internals, private audit chain code, or Enterprise backend code into public Core.

## Preserve Outside Public Core Staging

| Topic | Why preserve | Recommended location |
| --- | --- | --- |
| SION-specific doctrine | Captures prior decisions around bounded runtime execution, scope derivation limits, sponsored intent, and runtime separation. | Private/Enterprise archive |
| Ledger/private audit doctrine | Captures audit-chain separation, ledger/store boundary thinking, backpressure concerns, and integrity posture. | Private audit/signing archive |
| Docker/destructive reliability notes | Captures mocked/live reliability evidence and test-honesty outcomes without making public Core depend on Docker runtime execution. | Private reliability archive |
| Enterprise governance/backlog notes | Captures IntentCompiler, SponsorshipVerifier, SIONBridge separation, team/cloud/SSO/Slack, and Enterprise dashboard process backlog. | Enterprise planning archive |
| Long-horizon private governance notes | Captures future governance directions that require strict human-in-the-loop checkpoints and should not imply public Core autonomy. | Private roadmap archive |

## Public Core Boundary

Public Core may retain contracts, vocabulary, and fail-closed hooks when they are decoupled from private systems. Public Core must not ship the private implementation behind those hooks.

Core may understand trust states such as signed/unsigned, verified/unverified, lineage present/missing, approval present/missing, and execution history present/missing. Private signing authority remains optional and external.
