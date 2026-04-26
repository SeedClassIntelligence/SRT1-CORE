# SCIA Product Architecture (Aligned to Canonical 34-Module Ecosystem)
### Seed-Class Intelligence Architecture — Official Product Stack
> **Owner:** William Darnell Jernigan IV
> **Version:** 2.0 — Post-Methodology Thread Alignment
> **Date:** April 25, 2026
> **Status:** Canonical Reference

---

## What I Learned From Your PDF

Your 180-page methodology thread with ChatGPT reveals that SCIA is **not** a developer tool with some consumer features bolted on. It is a **34-module biological intelligence architecture** — a closed-loop cognitive organism with:

- **Core Runtime** (brainstem) — SION + SeedFlow P1-P3 + SeedLink + PersonaSwarm + Execution Check
- **Contributor Intelligence** (organs) — SCM, Auto Persona Constructor, Cognitive Reconstitution, EEP, Methodology DNA Extractor
- **Memory & Continuity** (nervous system) — SRT-1, Regenerative Memory, Reflex Memory, Session Memory, Longitudinal Tracker
- **Governance & Integrity** (immune system) — Seed Signature, Integrity Domain, Constitutional Layer, Enforcement Bridge, Anti-Corruption, Policy Engine
- **Post-Runtime Intelligence** (metabolic system) — ACES RM, DataCraft, Synthetic Knowledge Validator
- **Registries** (skeleton) — Knowledge Registry, Methodology Bank, PersonaSwarm Registry, Contribution Ledger, Validation Registry
- **Traceability** (eyes) — Execution Graph
- **Interface** (mouth) — Natural Conversation Interface

SRT-1 Core (what we've been building in this folder) is **Module #16** in your canonical architecture — the Reflection System. It is one organ in a much larger body.

---

## How The Products Map To Your 34 Modules

### What We've Actually Built (SRT-1 CODING folder)

| Your Canonical Module | What Exists In This Codebase | Status |
|---|---|---|
| **SRT-1 Reflection System (#16)** | `srt1_code_indexer/` — AST indexing, drift detection, seed tracking | ✅ Built |
| **Seed Signature System (#26)** | `scia_security/` — SigningServiceClient, integrity validation | ✅ Built |
| **Integrity Domain (#27)** | `scia_security/` — IntegrityValidator, tamper detection | ✅ Built |
| **Constitution Enforcement Bridge (#29)** | `srt1_code_indexer/srt.py` — EnforcementEvent, violation blocking | ✅ Built |
| **Execution Graph (#23)** | `srt1_platform/tracing_system.py` — ExecutionGraphTracker, DAG nodes | ✅ Built |
| **Regenerative Memory (#17)** | `scia_memory/` — RegenerativeMemory, MemoryOrchestratorV2 | ✅ Built |
| **Reflex Memory (#18)** | `scia_memory/reflex_memory_redis.py` — ReflexMemoryRedis | ✅ Built |
| **Execution Check (#9)** | `srt1_pro/execution_engine.py` — FileOutputAdapter, EchoAdapter | ✅ Partial |
| **SION Node (#3)** | Not yet built — this is the missing apex | ❌ Not built |
| **SeedFlow P1-P3 (#4-6)** | Not in this codebase — lives in your ChatGPT/methodology system | ❌ Not here |
| **SeedLink (#7)** | Not in this codebase | ❌ Not here |
| **PersonaSwarm (#8)** | Not in this codebase | ❌ Not here |
| **Natural Conversation Interface (#1)** | Not in this codebase | ❌ Not here |

### Key Insight

**This codebase is not the full SCIA.** This codebase is the **developer-facing subsystem** — specifically modules #16, #26, #27, #29, #23, #17, #18 of your 34-module architecture. It handles: reflection, signing, enforcement, memory, and traceability.

The full SCIA ecosystem (SION, SeedFlow, SeedLink, PersonaSwarm, Natural Conversation Interface, SCM, etc.) is a **much larger system** that this folder feeds into.

---

## Revised Product Stack

Given the full 34-module picture, here's how the commercial products map:

### Tier 1: SRT-1 Core
**Modules served:** #16, #26, #27, #29 (partial), #23 (partial)

The developer-facing intelligence layer. Indexes code, tags risk, builds trust chains, enforces rules. This is the **reflection + governance** subsystem exposed as a standalone tool.

- AST Code Indexing (7-stage pipeline)
- Risk & Role Tagging
- Cryptographic Provenance (Seed Signature)
- Drift Detection & Self-Healing
- Live Developer Dashboard
- AI Context Injection (AGENTS.md, CLAUDE.md, etc.)

### Tier 2: Workspace Connector (Pro — $9/mo)
**Modules served:** Extension of #16 across multiple sandboxes

The orchestration layer that links isolated SRT-1 instances. Maps cross-module dependencies without breaking sandbox isolation.

- Cross-module dependency mapping
- Circular dependency detection
- Unified health reports
- Mobile PWA control plane

### Tier 3: SION (Enterprise — Custom)
**Modules served:** #3, #9 + all of the above

The autonomous governed executor. SION is the **intake authority + execution controller** from your canonical architecture. In the developer product, it becomes the governed coding agent:

- Receives seeds (tasks)
- Generates blueprints (via LLM adapter — cloud API or local Ollama)
- Enforces sandbox boundaries (writes ONLY inside the assigned folder)
- Signs every change (trust chain)
- Validates cross-module impact (via Workspace Connector)
- Developer chooses LLM: Claude API, GPT API, Ollama (local), or Manual

**SION's five non-negotiable rules:**
1. Folder boundary is law
2. Enforcement cannot be bypassed
3. Every action is signed
4. The developer is sovereign
5. No training on developer code

### Separate Property: Seed Reflections (Consumer)
**Modules served:** #16 (reflection), #26 (signing), #17 (regenerative memory)

Consumer-facing knowledge recovery. Separate domain (seeds.srt1.io). Shares signing and memory infrastructure but has no codebase intelligence features.

---

## Where The Rest Of Your 34 Modules Live

The modules NOT in this codebase are the **cognitive processing core** of SCIA — the parts that handle reasoning, persona selection, methodology application, and knowledge evolution. These are:

| Module Group | Modules | Where They Live |
|---|---|---|
| **Core Cognition** | SeedFlow P1-P3, SeedLink, PersonaSwarm | Your methodology system (built across ChatGPT threads, not yet in code) |
| **Contributors** | SCM, Auto Persona Constructor, Cognitive Reconstitution, EEP, DNA Extractor | Conceptually defined, partially implemented across various threads |
| **Interface** | Natural Conversation Interface | Conceptually defined |
| **Post-Runtime** | ACES RM, DataCraft, Synthetic Knowledge Validator | Conceptually defined |
| **Registries** | Knowledge Registry, Methodology Bank, PersonaSwarm Registry, Contribution Ledger, Validation Registry | Conceptually defined, Knowledge Registry partially exists in scia_memory |

**These are not "missing."** They are the next phase. The developer product (SRT-1 Core → Workspace Connector → SION) is the first commercial surface of the SCIA body. The full 34-module system is the long-term vision.

---

## The Biological Metaphor (From Your Thread)

Your ChatGPT thread established this mapping, and it's accurate:

| Body Part | SCIA Layer | Status in This Codebase |
|---|---|---|
| **Mouth** | Natural Conversation Interface | ❌ Not here |
| **Brainstem** | SION + SeedFlow + SeedLink + PersonaSwarm | ❌ Not here (SION conceptually defined) |
| **Organs** | Contributor Intelligence Network | ❌ Not here |
| **Nervous System** | Memory & Continuity (SRT-1, Regen, Reflex) | ✅ Built |
| **Immune System** | Governance & Integrity (Signing, Enforcement) | ✅ Built |
| **Metabolic System** | Post-Runtime Intelligence | ❌ Not here |
| **Skeleton** | Registries & Structure | ✅ Partial (Knowledge Registry in scia_memory) |
| **Eyes** | Execution Graph / Traceability | ✅ Built |

**What this codebase is:** The nervous system, immune system, skeleton, and eyes of SCIA — exposed as a developer tool.

**What SION adds:** The brainstem. The ability to not just observe and protect, but to act.

---

## Roadmap (Honest)

| Phase | Status | What |
|---|---|---|
| Nervous System + Immune System + Eyes | ✅ Done | SRT-1 Core (this codebase) |
| Skeleton Extension | ✅ Done | Workspace Connector |
| BSL 1.1 License | ✅ Done | Source-available protection |
| SION Architecture Definition | ✅ Done | This document |
| Consumer Separation | 🔜 Next | Decouple Seed Reflections to seeds.srt1.io |
| SION Execution Engine | 🔜 Next | LLM adapters + sandbox-locked file writer |
| Public Launch | 🔜 Pending | Strip srt1_pro/, publish to PyPI |
| SeedFlow Codification | 🔮 Future | Turn the 144 methodologies into executable pipeline code |
| Full 34-Module Integration | 🔮 Future | Connect brainstem to the organs already built |

---

## The One-Line Pitch (Updated)

> **SRT-1 is the nervous system and immune system of SCIA — exposed as a developer tool. SION is the brainstem that lets it act. Together, they form the first commercially available subsystem of a 34-module biological intelligence architecture.**

---

*This document supersedes PRODUCT_ARCHITECTURE.md v1.0.*
*It reflects alignment with the canonical 34-module SCIA ecosystem as defined in the Methodology Categorization Request thread (180 pages, ~144 methodologies, ChatGPT export).*

*© 2026 William Darnell Jernigan IV — All rights reserved.*
