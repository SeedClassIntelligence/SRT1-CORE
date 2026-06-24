# SRT-1 Canonical Build Guide

This document maps the public SRT-1 Core build boundary. It is an authority map, not permission to move files or merge duplicate surfaces.

SRT-1 is a repo-continuity and alignment partner for AI coding assistants. Core includes local repo understanding, continuity, reflection, recall, reinjection, context isolation, verification, human co-creation, constellation awareness, and trust awareness.

## Public Directory Map

```text
SRT1 CODING/
├── srt1_code_indexer/       Repo understanding authority
│   ├── indexer.py           File traversal, hashing, manifest and symbol-map support
│   ├── engine.py            Local engine/API surface for index and status serving
│   ├── language_parsers.py  Parser expansion candidate
│   └── srt.py               Reflection/trace models and enforcement vocabulary
├── srt1_platform/           Local platform authorities
│   ├── seed_queue.py        Seed lifecycle and continuity candidate
│   ├── tracing_system.py    Trace/reflection support
│   ├── mcp_server.py        Assistant interface/context serving candidate
│   ├── filecell.py          Local containment concept candidate
│   ├── manifest_deriver.py  Manifest-derived boundary candidate
│   ├── verification.py      Verification/stitch preparation candidate
│   └── operational_registry.py  Local runtime/constellation registry candidate
├── srt1_pro/                Public/Pro extensions
│   ├── workspace_connector.py  Constellation/workspace connector candidate
│   └── context_bundler.py      Reinjection/context bundling candidate
├── developer-pwa/           Human observability/review shell candidate
├── srt1_platform/pwa/       Platform-served PWA shell candidate
├── srt1-contracts/          Public contracts pending review
├── srt1-skills/             Public skills pending review
└── docs/recovery/           Recovery inventory, authority maps, and boundary plans
```

## Canonical Source Caution

There are currently multiple dashboard/PWA surfaces. Do not move, delete, or consolidate them until the canonical source is approved. The PWA is a human observability/review surface, not a direct execution controller.

## Trust and Private Boundary

Core may understand trust states such as signed/unsigned, verified/unverified, and lineage present/missing. Core does not ship private Seed Signature authority, private keys, SCIA memory implementation, SCIA security implementation, SION internals, private audit chain, or Enterprise backend.

Public hooks and contracts must fail closed if private/Enterprise services are unavailable.

## Build Guidance

Before packaging or publishing:

1. Confirm no private implementation paths are staged.
2. Confirm `memory/`, `scia_memory/`, `scia_security/`, private audit/signing files, generated runtime state, logs, caches, and scratch files are ignored or intentionally excluded.
3. Confirm PWA changes are staged only after the canonical PWA source is approved.
4. Confirm FileCell, manifest derivation, verification, and operational registry code is staged only after private dependencies have been removed or abstracted.
5. Confirm docs describe Core as local continuity/alignment infrastructure, not as autonomous execution or private signing authority.

## Build / Test / Package Commands

Install standard build tooling:

```bash
pip install build wheel
```

Build the source distribution and wheel:

```bash
python -m build
```

Run the local engine against the current repo when the package or local scripts expose the engine command:

```bash
srt1-engine --repo_path ./
```

If working directly from source, use the repo's current local engine entrypoint only after confirming it belongs to public Core and does not import private signing, SCIA memory/security, SION, or private audit implementation.

## Core-Only Validation Checks

Before staging or publishing public Core artifacts:

1. Run the repo's available test suite without downloading new dependencies unless explicitly approved.
2. Confirm generated files, runtime state, caches, logs, local DBs, and scratch outputs are not staged.
3. Confirm private paths remain excluded: `memory/`, `scia_memory/`, `scia_security/`, private audit/signing files, SION internals, and Enterprise backend files.
4. Confirm public hooks fail closed when optional private/Enterprise integrations are unavailable.
5. Confirm README, AGENTS, CLAUDE, BUILD, and canonical state docs describe trust awareness as metadata/vocabulary, not bundled private signing authority.

## Package Boundary

The first safe public package should preserve working Core behavior and documentation while excluding private implementations. Package contents should favor existing local capabilities over new systems, and every public Enterprise integration point must degrade safely when the private backend is absent.
