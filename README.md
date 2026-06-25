# SRT-1 CORE

**SRT-1 is a repo-continuity and alignment partner for AI coding assistants.** It helps an assistant understand the project, avoid hallucination, prevent context bleed, preserve architectural coherence, follow the approved seed/build plan, and operate inside the correct local workcell.

SRT-1 CORE is local-first. Its public boundary is repo understanding, continuity, reflection, recall, reinjection, context isolation, verification, human co-creation, constellation awareness, and trust awareness. Private signing, private memory/security implementations, and Enterprise runtime systems are optional integrations outside public Core.

---

## What Core Does

SRT-1 CORE keeps an AI coding session anchored to the repository it is actually working in.

| Authority | Core responsibility |
| --- | --- |
| Repo Understanding | Index files, parse supported source, hash files, build symbol/dependency maps, and produce manifests. |
| Continuity | Track seeds as continuity objects with active, pending, completed, terminated, and partial states. |
| Reflection | Detect drift, doctrine conflicts, coherence risks, and architectural inconsistency. |
| Recall | Serve relevant prior state without flooding the assistant with stale walkthroughs. |
| Reinjection | Reinsert approved context through AGENTS.md, CLAUDE.md, Cursor context, MCP, or local APIs. |
| Context Isolation | Keep work inside the correct local workcell through manifest-derived read/write boundaries and forbidden paths. |
| Verification | Prepare and check proposed changes, diffs, post-execution evidence, and re-index events. |
| Human Co-Creation | Provide dashboard/PWA surfaces for observation, review, approval, rejection, and status awareness. |
| Constellation Awareness | Recognize independent SRT-1 engines across folders without merging their context by default. |
| Trust Awareness | Understand signed/unsigned, verified/unverified, and lineage present/missing states. |

Core does not autonomously control code execution. It prepares context, boundaries, proposals, and verification evidence for a human and an assistant to use deliberately.

---

## Trust Boundary

Core may understand trust states such as:

- signed or unsigned
- verified or unverified
- lineage present or missing
- approval present or missing
- execution history present or missing

Core does **not** ship private Seed Signature authority, private keys, SCIA memory implementation, SCIA security implementation, SION internals, private audit chain, or Enterprise backend. Public hooks and contracts must fail closed when a private or Enterprise backend is unavailable.

---

## Local Workcell Model

SRT-1 is designed around the local workcell: one repo, one engine, one local state boundary.

- Each repo can maintain its own `.srt1` state, manifest, and dashboard/API surface.
- FileCell is a local containment concept, not Enterprise-only.
- Manifest-derived boundaries define allowed reads, allowed writes, forbidden paths, and re-index checkpoints.
- Cross-project context is not shared unless explicitly approved through constellation coordination.

---

## Human Surface

The dashboard and mobile PWA are human observability/review surfaces. They may display repo state, seeds, proposed blueprints, trust status, verification status, and continuity warnings. They are not direct controllers for autonomous code execution.

A typical Core flow is:

1. Index the repo and generate/update the manifest.
2. Plant or receive a seed.
3. Build an aligned plan from current repo facts.
4. Present the plan for human review.
5. Serve bounded context to the assistant.
6. Verify proposed or completed changes.
7. Re-index accepted changes and update continuity state.

---

## Assistant Interface

SRT-1 can serve context through local files and local tools:

- `AGENTS.md`
- `CLAUDE.md`
- Cursor context files
- MCP tools
- local dashboard/API endpoints

The assistant interface should reinforce the recovered authority model: observe before changing, prefer existing capability, avoid duplicate systems, and preserve continuity.

---

## Installation

```bash
pip install srt1-core
```

## Quick Start

Start a local SRT-1 engine over a project folder:

```bash
srt1-index --repo_path ./my_project
```

The engine should index the repo, maintain local manifest/context state, and expose local observability surfaces. The exact port may be assigned by the local engine.

Example local endpoints:

| Surface | Example URL | Purpose |
| --- | --- | --- |
| Dashboard | `http://localhost:{port}/dashboard` | Human observability and review surface |
| Mobile PWA | `http://localhost:{port}/mobile` | Mobile review/status companion |
| Status API | `http://localhost:{port}/status` | JSON engine telemetry |

Seed planting can be exposed through the local API when enabled:

```bash
curl -X POST http://localhost:{port}/task -H "Content-Type: application/json" -d "{\"task\":\"Add user logout endpoint\"}"
```

Seed planting records intent and continuity state. It does not grant autonomous execution authority.

## MCP Setup Examples

Claude Desktop:

```json
{
  "mcpServers": {
    "srt1": {
      "command": "srt1-mcp",
      "env": {
        "SRT1_REPO_PATH": "/path/to/your/project"
      }
    }
  }
}
```

Cursor:

```json
{
  "mcpServers": {
    "srt1": {
      "command": "srt1-mcp",
      "env": {
        "SRT1_REPO_PATH": "."
      }
    }
  }
}
```

MCP tools should serve bounded repo context, continuity state, and verification evidence. Core may understand signed/unsigned, verified/unverified, and lineage present/missing trust states; private signing authority is optional/external and is not shipped in Core.

---

## Core / Pro / Enterprise Boundary

| Layer | Belongs here |
| --- | --- |
| Core | Local repo understanding, continuity, reflection, recall, reinjection, context isolation concepts, verification concepts, human observability shell, trust vocabulary. |
| Pro | Workspace connector, constellation coordination, richer context bundling, local multi-folder awareness, public contracts that remain decoupled from private systems. |
| Enterprise / Private | SCIA memory implementation, SCIA security implementation, private Seed Signature authority, private keys, SION internals, private audit/signing authority, team/cloud/SSO/Slack backend, Enterprise dashboards/processes that expose private flow. |

Enterprise/private systems are optional integrations. Core must remain useful without them and must fail closed when they are unavailable.

---

## Repository Map

```text
SRT1-CORE/
├── srt1_code_indexer/       repo understanding, AST/parser, hashing, manifest support
├── srt1_platform/           local platform authorities, MCP/context tools, seed queue, tracing
├── srt1_pro/                workspace connector, context bundling, constellation candidates
├── developer-pwa/           dashboard/PWA shell pending canonical source approval
├── srt1_platform/pwa/       platform-served PWA shell pending canonical source approval
├── srt1-contracts/          public contracts and skill surfaces for review
├── srt1-skills/             public skill definitions for review
└── docs/recovery/           architecture recovery and boundary planning
```

PWA sources are not moved until the canonical source is approved.

---

## Requirements

- Python 3.9+
- Core indexing uses the Python standard library where possible.
- SQLite may be used for local persistence.
- No private signing keys or private Enterprise services are required for public Core operation.

## License

Business Source License 1.1 (BSL 1.1)

The source code is available for reading, auditing, and permitted use under the project license. Production, team, and Enterprise use may require a commercial license.

## Author

William Darnell Jernigan IV - THE ORIGINAL SEED

Architecture: Seed-Class Intelligence Architecture (SCIA)
