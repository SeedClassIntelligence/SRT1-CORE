# SRT-1 CORE — Open Source Edition

**Brain Over the Repo** — Anti-hallucination, architectural coherence, and cryptographic guardrails for AI-assisted software work.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://seed-reflection.srt1.io)
[![PyPI version](https://badge.fury.io/py/srt1-core.svg)](https://pypi.org/project/srt1-core/)

---

## What Is SRT-1?

SRT-1 solves the problem of AI code assistants hallucinating architecture or breaking dependencies. It locally scans your codebase, builds a deep Abstract Syntax Tree (AST) manifest, and uses that context to forcefully guide the AI. 

The `srt1-core` package provides the **Memory Minimum Architecture**—a completely decoupled, local-first engine that runs entirely on your machine via SQLite, without pinging a cloud API.

### The "Drop-In" Sandbox (Zero Global State)
Unlike massive IDE extensions or global CLI tools that muddy your entire system, SRT-1 is hermetically sealed. You simply drop the `SRT1-CORE-OSS` folder into any codebase, and tell your existing AI assistant (Cursor, Copilot, etc.) to run it. 
- **Auto-Isolated Ports:** The engine dynamically finds available network ports, meaning you can drop SRT-1 into 5 different projects simultaneously without a single collision.
- **Local Context Only:** The engine builds its `.srt1` memory cache purely inside the project boundary. Zero cross-contamination across your machine.
- **The AI Handcuffs:** You aren't replacing your AI; you are dropping a constraint engine into your folder. Tell Cursor to use SRT-1, and the AI is instantly handcuffed to your deterministic, architectural rules.

### The Cryptographic Trust Layer
Every action in the SRT-1 pipeline is cryptographically tied to the codebase using **Seed Signature**. From the moment the AST generates the code manifest, to the exact moment you approve a task dispatch, the engine signs and verifies the payload. This ensures an indisputable, immutable execution roadmap.

## The Local Developer Experience

SRT-1 ships with a fully-featured local Developer Dashboard and a Mobile-reflective PWA. 

### The Human-in-the-Loop Pipeline
SRT-1 acts as a strict proxy between you and your code assistant (like Claude Code, Cursor, or Aider). 

1. **Plant a Seed:** You submit a task via the terminal or the PWA.
2. **Review Blueprint:** The system generates a blueprint of the intended changes.
3. **Approve via Seed Signature:** You review the blueprint in the PWA. Once you click Approve, the payload is signed via **Seed Signature** and dispatched to your code assistant to execute.
4. **Self-Heal:** If the AI makes a mistake, the AST detects the architectural drift and injects correction warnings into the AI's context files. The next time the AI reads its instructions, it sees the error.

### Real-Time Delivery: The MCP Server

Writing corrections to a file is useless if the AI never re-reads it. That's why SRT-1 ships with a **Model Context Protocol (MCP) server** — a live, bidirectional pipe between SRT-1 and your AI agent.

When connected via MCP, SRT-1 doesn't wait for the AI to check a file. It **pushes** codebase intelligence directly into the AI's context on every interaction:

- **`srt1_get_context`** — AI calls this before making changes. Gets the full code map, risk tags, and warnings.
- **`srt1_log_interaction`** — AI calls this after every action. Every 3 calls, SRT-1 fires a reflection checkpoint and pushes a coherence score + correction directives back into the conversation.
- **`srt1_check_function`** — AI calls this before creating a function. SRT-1 tells it if the function already exists.
- **`srt1_set_task`** — Plants the seed. Everything after this is measured for drift.

#### Setup for Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "srt1": {
      "command": "srt1-mcp",
      "env": { "SRT1_REPO_PATH": "/path/to/your/project" }
    }
  }
}
```

#### Setup for Cursor
Add to `.cursor/mcp.json` in your project:
```json
{
  "mcpServers": {
    "srt1": {
      "command": "srt1-mcp",
      "env": { "SRT1_REPO_PATH": "." }
    }
  }
}
```

Once connected, the AI is **forced** to call SRT-1 tools — and SRT-1 injects corrections directly into the conversation in real time. No file polling. No hoping the AI re-reads.

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
Navigate to `http://localhost:7483/mobile` to start planting seeds and governing your AI's execution pipeline.

## The Unified Ecosystem

`pip install srt1-core` provides the complete Open Source ecosystem:

| Component | Description | CLI Tools |
|------|----------|-----------|
| **Core Intelligence** | Local AST mapping, File hashing, Curation | `srt1-index` |
| **Pro Execution** | Context Bundler, Execution Engine, Self-Healing | `srt1-bundle`, `srt1-execute`, `srt1-heal` |
| **Platform & UI** | Live Middleware, Developer Dashboard, PWA | `srt1-middleware` |
| **MCP Server** | Real-time AI injection via Model Context Protocol | `srt1-mcp` |

## Architecture

SRT-1 is deployed as a single unified wheel containing all subsystems:

```text
srt1_code_indexer/          → Code reflection and indexing engine
srt1_pro/                   → Bundling, execution, self-heal
srt1_platform/              → Middleware, Seed Queue, MCP server, bridge
srt1_platform/pwa/          → Local Developer UI & Human-in-the-Loop PWA
```

## Requirements
- Python 3.9+
- Core indexing uses the Python standard library only.

## License
Apache License 2.0
Author: William Darnell Jernigan IV AKA THE ORIGINAL SEED
