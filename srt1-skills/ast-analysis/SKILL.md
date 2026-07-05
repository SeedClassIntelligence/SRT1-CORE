# AST Analysis Skill

> **Skill ID:** `SRT1-SKILL-002`
> **Module:** SRT-1 Code Indexer
> **Authority:** Repo Understanding
> **Classification:** Public Core
> **Mutates Source:** Never

## Purpose

AST Analysis extracts structural intelligence from repository files: classes,
functions, imports, dependencies, parameters, docstrings, and parser coverage.
Python files use the standard `ast` module. Non-Python files use structural
parsers from `language_parsers.py` where available.

This skill supplies symbol and dependency evidence to Repo Indexing, FileCell
creation, WorkCell scoping, and verification. It does not own repository
truth by itself; it is a parser service under Repo Understanding.

## Activation

| Trigger | Source | Frequency |
|---|---|---|
| Indexing pipeline | `SRT1CodeIndexer.index_repository()` | During indexing/re-indexing |
| Python source parsing | AST parser | Per supported Python file |
| Non-Python dispatch | `dispatch_parser(source, filepath, ext)` | Per supported non-Python file |
| Optional semantic enrichment | Intelligence adapter, when configured | On demand/degraded-safe |

## Preconditions

- Target source file is readable.
- File extension is supported or safely classified as unsupported.
- File content is text, not binary/oversized excluded input.
- Repo indexing has authorized the file path inside the repository boundary.

## Inputs

| Input | Type | Source |
|---|---|---|
| Source file content | String | File system via indexer |
| File path | String | Indexer |
| File extension | String | Parser dispatch |
| Parser rules | Configuration | `language_parsers.py` / indexer |

## Outputs

| Output | Type | Destination |
|---|---|---|
| Symbol list | List of dictionaries | `symbol_table` / manifest |
| Import/dependency evidence | List/dict | dependency map |
| Line and span metadata | Integers/ranges | symbol records |
| Parse warnings | List | indexing diagnostics |
| Optional semantic reflection | Dict | degraded-safe enrichment metadata |

Expected symbol records include fields such as `name`, `type`, `line`,
`end_line`, `parameters`, `dependencies`, and docstring summary when available.

## Runtime Responsibilities

1. Parse supported source files without mutating them.
2. Extract structural symbols and dependency evidence.
3. Preserve file-to-symbol ownership.
4. Return warnings instead of crashing on syntax/parser failures.
5. Label degraded parser coverage when structural extraction is partial.
6. Fall back safely when optional enrichment is unavailable.

## Boundary Rules

| Rule | Enforcement |
|---|---|
| Read-only | Never modifies source files |
| Graceful degradation | Parser failures become warnings, not pipeline crashes |
| Optional enrichment | Missing model/API/provider must not block structural parsing |
| No execution actor control | Execution actors consume derived FileCells, not parser control |
| No private dependency | Public Core parsing must work without private memory/security/signing services |

## Verification

| Check | Success condition |
|---|---|
| Parser returns safely | Returns a symbol list or degraded warning |
| Structural spans are coherent | Line/end-line data match source boundaries where available |
| Zero side effects | File content is identical before and after parsing |
| Dependencies are evidence-backed | Imports/calls map to observed source where possible |
| Pipeline remains alive | Syntax errors do not interrupt repository indexing |

Failure indicators include repeated parser crashes, blank symbol output without a
degraded reason, incorrect line spans, or enrichment failure blocking structural
results.

## Events

AST Analysis does not emit per-file events by default because that would create
event noise. It reports parse warnings and counts through the broader
`repo_index_started`, `repo_index_completed`, and `repo_index_failed` lifecycle.

## Source of Truth

- `srt1_code_indexer/indexer.py`
- `srt1_code_indexer/language_parsers.py`
- optional semantic enrichment adapters, when configured
