# SRT1 Skill Registry

This registry is the compact always-available map of SRT1 skills. Full skill documents and contracts should be loaded only when a seed, WorkCell, runtime event, or user action triggers them.

| Skill ID | Skill | Authority | Load when | Primary inputs | Primary outputs | Boundary | Full doc |
|---|---|---|---|---|---|---|---|
| SRT1-SKILL-001 | Repo Indexing | Repo Understanding | Repository activation, engine startup, file change re-index | Repo root, ignore rules, supported extensions | Manifest, file list, hashes, module map | Public Core | repo-indexing/SKILL.md |
| SRT1-SKILL-002 | AST Analysis | Repo Understanding | Indexing/parsing supported source files | Source file, parser rules | Symbols, imports, functions/classes, parse warnings | Public Core | ast-analysis/SKILL.md |
| SRT1-SKILL-003 | Context Injection | Reinjection | Assistant context refresh, MCP context request, WorkCell package generation | Recall/context packets, manifest summary, WorkCell scope | Assistant context packet/files/MCP response | Public Core | context-injection/SKILL.md |
| SRT1-SKILL-004 | Drift Detection | Reflection | Seed checkpoint, coherence scan, completion review | Seed intent, continuity state, recent actions | Drift/coherence findings and warnings | Public Core detective-only | drift-detection/SKILL.md |
| SRT1-SKILL-005 | Module Boundary Protection | Context Isolation | Before allowed reads/writes, WorkCell expansion, context expansion | FileCell/WorkCell scope, forbidden paths, requested path | Allow/deny boundary decision | Public Core/Pro candidate | module-boundary-protection/SKILL.md |
| SRT1-SKILL-006 | FileCell Manifest Derivation | Context Isolation / Repo Understanding | WorkCell creation, seed scoping, manifest refresh | Symbol table, dependency map, seed scope | FileCell/WorkCell manifest and allowed paths | Public Core/Pro candidate | filecell-manifest-derivation/SKILL.md |
| SRT1-SKILL-007 | Post-Execution Verification | Verification | After proposed code/file changes, completion request | Change proposal, pre/post hashes, manifest, tests | Verification result, mismatch evidence, re-index request | Public Core/Pro candidate | post-execution-verification/SKILL.md |
| SRT1-SKILL-008 | Constellation Mapping | Constellation | Multi-repo/multi-runtime dashboard, engine federation status | Runtime registry, engine health, port map | Read-only constellation map | Public Core/Pro awareness, no shared context by default | constellation-mapping/SKILL.md |
| SRT1-SKILL-009 | Audit Event Emission | Trust Awareness / Continuity | Lifecycle events, verification evidence, trust metadata updates, Seed Signature create/attach request | Event metadata, queue seed id, artifact lineage | Public event record, trust metadata, optional external Seed Signature attachment | Public Core vocabulary; Seed Signature platform external | audit-event-emission/SKILL.md |

## Empty / Scaffold Skill Folders

| Folder | Possible authority | Decision needed |
|---|---|---|
| consistency-auditing | Reflection | Fold into drift-detection or document as separate skill only if implementation exists. |
| doctrine-scanning | Reflection | Fold into drift-detection/reflection or document as separate skill only if implementation exists. |

## Loader Rule

The registry is always safe to load. Full SKILL.md files are loaded only when their `Load when` trigger matches the active seed, WorkCell, dashboard request, verification event, or context request.

## Public Core Boundary

SRT-1 may let a developer create or attach a Seed Signature from inside the
platform. Public Core brokers that request and records returned trust metadata.
The standalone Seed Signature platform owns signature creation, signing
authority, keys, and private signing records. Public Core does not ship private
signing authority, private keys, private audit chain, SION internals, or
Enterprise backend implementation.

The Core-safe integration is a server-side session-token route plus the
frontend Seed Signature widget SDK. SRT-1 uses its backend API key only on the
server, opens the external signing modal in the dashboard, and stores returned
metadata such as `signatureId` and `certificateUrl`.
