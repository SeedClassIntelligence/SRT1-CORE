# SRT-1 — Cognitive Operating System for Software Repositories

**Brain Over the Repo** — Anti-hallucination and architectural-coherence guardrails for AI-assisted software work.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://seedreflection.com)
[![PyPI version](https://badge.fury.io/py/srt1-core.svg)](https://pypi.org/project/srt1-core/)

---

## What Is SRT-1?

SRT-1 scans your codebase, builds a structured manifest of files, symbols, purpose, risk, and architectural role, and uses that context to reduce hallucination, duplication, and drift in AI-assisted development workflows.

### The SCIA Pipeline

```text
Phase 1: Code Indexer    → scans, parses, curates → code manifest
Phase 2: Context Bundler → task analysis + symbol search → context bundle
Phase 3: Execution Layer → governed task routing → result
```

## Installation

```bash
pip install srt1-core
```

## Quick Start

### Index a Repository

```bash
srt1-index --repo_path /path/to/your/repo
```

This generates `srt1_code_manifest.json` with an integrity hash.

### Use as a Library

```python
from srt1_code_indexer import SRT1CodeIndexer

indexer = SRT1CodeIndexer("/path/to/repo")
manifest = indexer.index_repository()
```

### Build a Context Bundle (Pro)

```bash
srt1-bundle --manifest srt1_code_manifest.json --task "Add user authentication"
```

### Start the Live Middleware (Platform)

```bash
srt1-middleware --repo_path ./my_project --port 7483
```

Then integrate with any AI assistant via HTTP:

```bash
curl -X POST http://localhost:7483/task -d '{"task": "Add refund emails"}'
curl http://localhost:7483/context
```

## The Unified Ecosystem

You no longer have to download multiple packages. `pip install srt1-core` gives you the complete Seed-Class Intelligence Ecosystem in a single installation:

| Component | Description | CLI Tools |
|------|----------|-----------|
| **Core Intelligence** | Code Indexer, SRT Engine, AST mapping | `srt1-index` |
| **Pro Execution** | Context Bundler, Execution Engine, Self-Healing | `srt1-bundle`, `srt1-execute`, `srt1-heal` |
| **Platform & PWA** | Live Middleware, Seed Queue, Execution Bridge, Thread Recovery, Mobile PWA | `srt1-middleware` |

## What the Code Manifest Contains

- **File manifest** with SHA-256 content hashes
- **Symbol table** with AST-extracted metadata (classes, functions, parameters)
- **Curation report** (duplicate files, overlapping functions)
- **SRT-1 reflections** (purpose, architectural role, risk profile for every symbol)
- **Execution trace chain** and coherence history
- **Integrity hash** for tamper detection

## CTO-Grade Security & Governance (Enterprise Use)

While the open-source `srt1-core` package provides the complete platform capabilities offline, the **SRT-1 Governance License** activates remote execution and team fleet management features built for CTOs to securely govern AI development:

- **Cryptographic Trust Signatures & Manifests**: Every file and symbol is hashed (SHA-256) into an immutable code manifest, creating an indisputable execution roadmap.
- **Enterprise Enforcement Guardrails**: SRT-1 dynamically triggers `HARD_STOP` locks when it detects functional overlaps or duplicate files, forcing AI developers to strictly align with the existing architecture.
- **Zero-IP-Leak Physical Isolation**: The core engine operates locally offline and is physically decoupled from any proprietary SaaS backend, securing your perimeter.
- **Strict Network Loopback Telemetry**: Built-in `SCIARemoteAuth` cryptographic middleware instantly locks down external API fetches, while transparently permitting 127.0.0.1 bypasses to seamlessly drive isolated local Developer Dashboards.

## Architecture

SRT-1 is deployed as a single unified wheel containing all subsystems:

```text
srt1_code_indexer/          → Code reflection and indexing engine
srt1_pro/                   → Bundling, execution, self-heal
srt1_platform/              → Middleware, queueing, bridge, thread recovery
```

## Requirements

- Python 3.9+
- Core indexing uses the Python standard library only

## License

Apache License 2.0
Author: William Darnell Jernigan IV
