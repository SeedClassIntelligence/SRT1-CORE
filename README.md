# SRT-1 CORE — Open Source Edition

**Brain Over the Repo** — Anti-hallucination, architectural coherence, and cryptographic guardrails for AI-assisted software work.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://seedreflection.com)
[![PyPI version](https://badge.fury.io/py/srt1-core.svg)](https://pypi.org/project/srt1-core/)

---

## What Is SRT-1?

SRT-1 solves the problem of AI code assistants hallucinating architecture or breaking dependencies. It locally scans your codebase, builds a deep Abstract Syntax Tree (AST) manifest, and uses that context to forcefully guide the AI. 

The `srt1-core` package provides the **Memory Minimum Architecture**—a completely decoupled, local-first engine that runs entirely on your machine via SQLite, without pinging a cloud API.

### The Cryptographic Trust Layer
Every action in the SRT-1 pipeline is cryptographically tied to the codebase using **Seed Signature**. From the moment the AST generates the code manifest, to the exact moment you approve a task dispatch, the engine signs and verifies the payload. This ensures an indisputable, immutable execution roadmap.

## The Local Developer Experience

SRT-1 ships with a fully-featured local Developer Dashboard and a Mobile-reflective PWA. 

### The Human-in-the-Loop Pipeline
SRT-1 acts as a strict proxy between you and your code assistant (like Claude Code, Cursor, or Aider). 

1. **Plant a Seed:** You submit a task via the terminal or the PWA.
2. **Review Blueprint:** The system generates a blueprint of the intended changes and pauses execution (`auto_dispatch: false`).
3. **Approve via Seed Signature:** You review the blueprint in the PWA. Once you click Approve, the payload is signed via **Seed Signature** and dispatched to your code assistant to execute.
4. **Self-Heal:** If the AI makes a mistake, the AST detects the drift, bundles the error, and automatically sends it back to the AI for self-healing.

## Installation

```bash
pip install srt1-core
```

## Quick Start

### 1. Index a Repository

```bash
srt1-index --repo_path /path/to/your/repo
```
*This generates `srt1_code_manifest.json`—the foundational map of your codebase, verified by Seed Signature.*

### 2. Start the Live Middleware & Dashboard

```bash
srt1-middleware --repo_path ./my_project --port 7483
```
*This spins up the local execution engine and the Developer Dashboard/PWA.*

### 3. Open the PWA
Navigate to `http://localhost:7483/mobile.html` to start planting seeds and governing your AI's execution pipeline.

## The Unified Ecosystem

`pip install srt1-core` provides the complete Open Source ecosystem:

| Component | Description | CLI Tools |
|------|----------|-----------|
| **Core Intelligence** | Local AST mapping, File hashing, Curation | `srt1-index` |
| **Pro Execution** | Context Bundler, Execution Engine, Self-Healing | `srt1-bundle`, `srt1-execute`, `srt1-heal` |
| **Platform & UI** | Live Middleware, Developer Dashboard, PWA | `srt1-middleware` |

## Architecture

SRT-1 is deployed as a single unified wheel containing all subsystems:

```text
srt1_code_indexer/          → Code reflection and indexing engine
srt1_pro/                   → Bundling, execution, self-heal
srt1_platform/              → Middleware, Seed Queue, bridge
developer-pwa/              → Local Developer UI & Human-in-the-Loop PWA
```

## Requirements
- Python 3.9+
- Core indexing uses the Python standard library only.

## License
Apache License 2.0
Author: William Darnell Jernigan IV AKA THE ORIGINAL SEED
