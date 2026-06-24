# Repo Indexing Skill

> **Skill ID:** `SRT1-SKILL-001`
> **Module:** SRT-1 Engine
> **Classification:** UNDERSTANDING
> **Mutates Source:** ❌ Never

---

## Purpose

Reads a repository or module and builds the complete symbol/context map — the `srt1_code_manifest.json`. This is the foundational skill. Everything else depends on this.

---

## What It Does

1. Walks the directory tree (respecting `.gitignore` and `EXCLUDED_DIRS`)
2. Dispatches each file to the appropriate parser (AST for Python, regex for others)
3. Builds `symbol_table`: `{filepath → [{name, type, line, parameters, dependencies, docstring}]}`
4. Builds `call_graph`: `{function_name → [called_function_names]}`
5. Computes file hashes (SHA-256) for integrity tracking
6. Detects file duplicates and functional overlaps
7. Writes `srt1_code_manifest.json`

## Activation Trigger

- Engine startup (`SRT1Engine.__init__()`)
- File watcher detects changes (15-second poll loop)
- Manual re-index via `/api/reindex` endpoint
- MCP `srt1_get_context` tool call (if stale)
