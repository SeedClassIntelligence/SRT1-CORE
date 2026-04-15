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
pip install SRT1-CORE
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

## Tiers

| Tier | Includes | CLI Tools |
|------|----------|-----------|
| **Core** | Code Indexer, SRT Engine | `srt1-index` |
| **Pro** | + Context Bundler, Execution Engine, Self-Heal | `srt1-bundle`, `srt1-execute`, `srt1-heal` |
| **Platform** | + Live Middleware, Seed Queue, Execution Bridge, Thread Recovery | `srt1-middleware` |

## What the Code Manifest Contains

- **File manifest** with SHA-256 content hashes
- **Symbol table** with AST-extracted metadata (classes, functions, parameters)
- **Curation report** (duplicate files, overlapping functions)
- **SRT-1 reflections** (purpose, architectural role, risk profile for every symbol)
- **Execution trace chain** and coherence history
- **Integrity hash** for tamper detection

## Security

- **Local-first indexing and analysis**
- **Read-only repository scanning**
- **Path-safe output** with no absolute local paths
- **Integrity verification** via SHA-256 manifest hashing

## Architecture

```text
srt.py                      → Seed Reflection Tool (anti-hallucination guardrail)
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
