# SRT-1 Canonical Directory Tree & Build Guide

This document maintains the canonical file mappings and build architecture for the SRT-1 Unified Engine.

## Canonical Directory Tree

Below is the authoritative map of the SRT-1 platform. Use this map to prevent duplication and ensure you are working on the correct production files.

```text
SRT1_CODING/
├── srt1_code_indexer_engine.py      (1) The Primary Core Engine & API Server (Port 7483)
├── srt1_dashboard.html              (2) The Production Developer Dashboard (Command Center) 
├── srt1_mobile.html                 (3) Mobile PWA interface
├── README_PYPI.md                   (4) Package description and documentation
├── pyproject.toml                   (5) Build Configuration
├── srt1_code_indexer/               (6) Core Package - Open Source Features
│   ├── indexer.py                   - Tree traversal and file mapping
│   ├── srt.py                       - Intent anchoring models
│   └── srt1_signature_client_community.py (Safe community stub for open source)
├── external_api/                       (7) Proprietary V2 Core (PROTECTED - Excluded from Git)
│   └── srt1_signature_client.py     - True cryptographic signing engine
├── srt1_platform/                   (8) Internal Tracing, Networking & Queueing
│   ├── mcp_server.py                - Multi-agent control plane
│   ├── tracing_system.py            - Graph-based deterministic pipeline tracer
│   └── seed_queue.py                - Lifecycle execution & task tracking
├── srt1_pro/                        (9) Enterprise Features & Context Injectors
│   ├── execution_engine.py          - Bridge executing and writing final tasks
│   └── self_heal.py                 - Autonomous redundancy repair tools
└── seed-reflection/                 (10) Public Marketing & Sales Funnel (Static)
    ├── home.html                    - Public Root / Landing Page
    ├── developer-landing.html       - Developer Pitch
    ├── comparison.html              - Competitive Comparison Matrix
    └── auth.html                    - Registration / Login Gateway
```

---

## The "Two Dashboards" Rule
There are currently multiple versions of the dashboard inside the repository. To avoid overlap, obey these strict resolutions:

* **Production Live Dashboard:** `srt1_dashboard.html` at the root directory. This contains live API fetching (e.g. `GET /seeds/active`), the real Repository Explorer, and Command Center Chat.
* **Legacy Mock Dashboard:** `seed-reflection/dashboard.html` is **DEPRECATED** and serves purely as a mockup. 

*Note: The engine explicitly routes requests for `/dashboard.html` to `srt1_dashboard.html`.*

---

## Build Instructions (PyPI Package)

We package SRT-1 as an installable background-running daemon.

### 1. Build the Wheel
```bash
# Ensure standard build tools are present
pip install build wheel

# Create the packaged .tar.gz and .whl in /dist
python -m build
```

### 2. Output Validation
Before deploying, confirm that `.gitignore` correctly filtered out `external_api/srt1_signature_client.py` to prevent IP leakage, and that `srt1_code_indexer/srt1_signature_client_community.py` is bundled in its place.

### 3. Local Execution Run
To start the engine locally over an existing codebase:
```bash
python srt1_code_indexer_engine.py --repo_path ./
```
*The engine will start on Port 7483 and index the current working directory.*
