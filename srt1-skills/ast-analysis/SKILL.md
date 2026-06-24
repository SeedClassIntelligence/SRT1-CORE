# AST Analysis Skill

> **Skill ID:** `SRT1-SKILL-002`
> **Module:** SRT-1 Code Indexer
> **Classification:** UNDERSTANDING
> **Mutates Source:** ❌ Never

---

## Purpose

Extracts classes, functions, imports, and dependencies from Python source files using the `ast` module. For non-Python files, falls back to regex-based structural extraction via `language_parsers.py`.

---

## Activation

| Trigger | Source |
|---------|--------|
| Indexer pipeline | `SRT1CodeIndexer.index_repository()` calls `_build_ast()` per `.py` file |
| Non-Python dispatch | `dispatch_parser(source, filepath, ext)` in `language_parsers.py` |
| LLM enrichment | `IntelligenceAdapter.deep_analyze_source()` for semantic depth |

## Inputs

| Input | Type |
|-------|------|
| Source file content | `str` |
| File path | `str` (for context) |
| File extension | `str` (for parser dispatch) |

## Outputs

| Output | Type |
|--------|------|
| Symbol list | `List[Dict]` — `{name, type, line, end_line, parameters, dependencies, docstring_first_line}` |
| Architectural reflection | `Dict` — `{architectural_role, risk_profile, purpose}` (via LLM enrichment) |

## Governance

- Read-only: never modifies source files
- AST parse failures are logged as warnings, not errors — the skill degrades gracefully
- LLM enrichment is optional — if no API key or provider fails, regex output is used

## Verification

| Check | Condition |
|-------|-----------|
| Parse succeeds | Returns list (even if empty) |
| No false positives | Only real structural elements extracted |
| Dependency resolution | `dependencies` list maps to real symbols in other files |

## Events

| Event | Status |
|-------|--------|
| *(No dedicated events — runs within repo_index lifecycle)* | Covered by `repo_index_*` events |

## Source of Truth

- [indexer.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_code_indexer/indexer.py) — Python AST extraction
- [language_parsers.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_code_indexer/language_parsers.py) — Regex parsers for JS, TS, HTML, CSS, C#, etc.
- [intelligence_adapter.py](file:///c:/Users/SEEDN/Downloads/SRT1%20CODING/srt1_platform/intelligence_adapter.py) — LLM enrichment
