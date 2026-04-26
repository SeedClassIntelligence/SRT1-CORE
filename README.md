# SRT-1 CORE

**Brain Over the Repo** — Anti-hallucination, architectural coherence, and cryptographic guardrails for AI-assisted software work.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: BSL 1.1](https://img.shields.io/badge/license-BSL_1.1-green.svg)](https://srt1.io)
[![PyPI version](https://badge.fury.io/py/srt1-core.svg)](https://pypi.org/project/srt1-core/)

---

## What Is SRT-1?

SRT-1 solves the problem of AI code assistants hallucinating architecture or breaking dependencies. It locally scans your codebase, builds a deep Abstract Syntax Tree (AST) manifest, and uses that context to forcefully guide the AI. 

The `srt1-core` package provides the **Memory Minimum Architecture**—a completely decoupled, local-first engine that runs entirely on your machine via SQLite, without pinging a cloud API.

### The "Drop-In" Sandbox (Zero Global State)

Unlike massive IDE extensions or global CLI tools that muddy your entire system, SRT-1 is hermetically sealed. You drop SRT-1 into any folder, and it spins up its own engine on its own port. 

- **One Folder, One Engine, One Port:** Each project folder gets its own SRT-1 engine running on a dedicated port, derived from the folder path. Drop SRT-1 into 5 different projects — you get 5 independent engines on 5 different ports, with zero collisions and zero configuration.
- **Local Context Only:** The engine builds its `.srt1` memory cache purely inside the project boundary. Zero cross-contamination across your machine.
- **The AI Handcuffs:** You aren't replacing your AI; you are dropping a constraint engine into your folder. Tell Cursor to use SRT-1, and the AI is instantly handcuffed to your deterministic, architectural rules.

```
── Your machine ────────────────────────────────────
● auth-module/    → Engine on port 7483  · 12 files, 47 functions
● payments/       → Engine on port 8192  · 8 files, 31 functions
● frontend/       → Engine on port 9104  · 24 files, 89 functions
● api-gateway/    → Engine on port 7821  · 6 files, 22 functions
● admin-panel/    → Engine on port 8640  · 15 files, 53 functions

Each engine: independent process, independent manifest, independent dashboard.
```

### The Workspace Connector (Pro)

Modules don't exist in a vacuum. Auth calls payments. The gateway routes to both. The **Workspace Connector** acts as a parent orchestrator — it queries each running Sandbox engine on its port, collects their live manifests, and builds a unified cross-module dependency map. Zero re-indexing. It reads what's already running.

### The Cryptographic Trust Layer

Every action in the SRT-1 pipeline is cryptographically tied to the codebase using **Seed Signature**. From the moment the AST generates the code manifest, to the exact moment you approve a task dispatch, the engine signs and verifies the payload. This ensures an indisputable, immutable execution roadmap.

---

## The Local Developer Experience

SRT-1 ships with a fully-featured **Developer Homepage**, a live **Developer Dashboard**, and a **Mobile PWA** — all served locally from the engine.

| Surface | URL | Purpose |
|---------|-----|---------|
| Developer Homepage | `http://localhost:{port}/` | Product overview, interactive demo, pricing |
| Developer Dashboard | `http://localhost:{port}/dashboard` | Live metrics, trust chain, repo explorer, audit trail |
| Mobile PWA | `http://localhost:{port}/mobile` | Seed planting, task review, mobile companion |
| API Status | `http://localhost:{port}/status` | JSON engine telemetry |

### The Human-in-the-Loop Pipeline

SRT-1 acts as a strict proxy between you and your code assistant (like Claude Code, Cursor, or Aider). 

1. **Plant a Seed:** You submit a task via the terminal, the dashboard, or the PWA.
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

---

## Installation

```bash
pip install srt1-core
```

## Quick Start

### 1. Start the Engine

```bash
srt1-engine --repo_path ./my_project
```

The engine automatically:
- Indexes your codebase (AST + file hashing)
- Generates AI context files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`)
- Starts the developer dashboard and API on a dynamically assigned port
- Begins file watching — auto re-indexes on every change

The terminal will print the exact port:
```
  ╔══════════════════════════════════════════════════════╗
  ║               INDEXER IMMUNE SYSTEM IS LIVE         ║
  ╚══════════════════════════════════════════════════════╝

  Developer:  http://127.0.0.1:8368/dashboard
  Consumer:   http://127.0.0.1:8368/consumer
  Mobile:     http://127.0.0.1:8368/mobile
  API:        http://127.0.0.1:8368/status
```

### 2. Connect Your AI

Point your AI assistant at the generated `AGENTS.md` or connect via MCP for real-time injection.

### 3. Plant Seeds

Submit tasks via the dashboard, mobile PWA, or API:
```bash
curl -X POST http://localhost:8368/task -d '{"task": "Add user logout endpoint"}'
```

---

## Pricing

SRT-1 is **source-available** under the Business Source License 1.1. The full single-folder engine is free forever.

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | Full single-folder Sandbox engine. AST indexing, dashboard, trust chain, file watcher, seed tracking. 100% local. |
| **Pro** | $9/month | Everything in Free + Workspace Connector (link up to 15 modules), Mobile PWA, MCP Server, Blueprint generation, Execution Bridge. |
| **Enterprise** | $49/seat/month | Everything in Pro + Team sync, CTO admin dashboard, Knowledge Graph, SCIA Memory Orchestrator, SSO/SAML, audit exports, SLA support. Volume discounts available. |

---

## The Two Products

SRT-1 CORE contains two distinct products served from the same engine:

### For Developers (Root Path `/`)
The developer-facing platform — codebase indexing, trust chain, AI governance, blueprint generation. This is the engineering tool.

### For Everyone — Seed Reflection (Path `/consumer/`)
A consumer-facing conversation recovery product. Upload a ChatGPT JSON export or paste a Claude conversation, and get every abandoned idea back — prioritized and ready to pick up.

**Live:** [seeds.srt1.io](https://seeds.srt1.io)

---

## The Unified Ecosystem

`pip install srt1-core` provides the complete ecosystem:

| Component | Description | CLI Tools |
|-----------|-------------|-----------|
| **Core Intelligence** | Local AST mapping, file hashing, curation, enforcement | `srt1-index` |
| **Pro Execution** | Context Bundler, Execution Engine, Self-Healing | `srt1-bundle`, `srt1-execute`, `srt1-heal` |
| **Platform & UI** | Live engine, Developer Dashboard, Mobile PWA | `srt1-engine`, `srt1-middleware` |
| **MCP Server** | Real-time AI injection via Model Context Protocol | `srt1-mcp` |
| **Workspace Connector** | Multi-folder orchestration (Pro) | `srt1-workspace` |

## Architecture

```text
SRT1-CORE/
├── srt1_code_indexer/       → Code reflection, indexing engine, HTTP server
│   └── engine.py            → The unified engine (index → analyze → serve → watch)
├── srt1_pro/                → Bundling, execution, self-heal, reinjection
├── srt1_platform/           → Middleware, Seed Queue, MCP server, execution bridge
├── developer-pwa/           → Developer Homepage, Dashboard, Documentation
│   ├── index.html           → Developer landing page
│   ├── dashboard.html       → Live engine monitoring dashboard
│   ├── workspace-demo.html  → Sandbox & Connector architecture page
│   ├── contact.html         → Enterprise contact & volume pricing
│   └── documentation.html   → API reference & integration guides
├── packages/
│   ├── scia_memory/         → Memory Orchestrator, frame persistence, Redis integration
│   └── scia_security/       → Audit logging, execution graph tracking
└── seed-reflection/         → Consumer product — conversation recovery
    ├── index.html           → Consumer landing page
    └── dashboard.html       → Consumer seed dashboard
```

## Requirements
- Python 3.9+
- Core indexing uses the Python standard library only.
- SQLite (bundled with Python) for local persistence.

## License

Business Source License 1.1 (BSL 1.1)

The source code is available for reading, auditing, and non-production use. Production use requires a commercial license for teams and enterprises. Individual developer use on personal and open-source projects is permitted.

**Author:** William Darnell Jernigan IV — THE ORIGINAL SEED

**Architecture:** Seed-Class Intelligence Architecture (SCIA)

© 2026 SRT-1 — [srt1.io](https://srt1.io)
