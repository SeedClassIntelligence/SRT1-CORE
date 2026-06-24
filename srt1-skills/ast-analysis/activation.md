# AST Analysis — Activation

## Trigger Conditions

| Trigger | Source | Frequency |
|---------|--------|-----------|
| Indexer pipeline | `SRT1CodeIndexer.index_repository()` calls `_build_ast()` for each `.py` file | During indexing / re-indexing |
| Non-Python dispatch | `dispatch_parser(source, filepath, ext)` in `language_parsers.py` | During indexing / re-indexing |
| LLM enrichment | `IntelligenceAdapter.deep_analyze_source()` | On-demand semantic reflection |

## Pre-conditions

- Target source file is readable.
- File path extension is supported (dispatches to Python AST parser or regex structural parser).
- Codebase index is initialized or actively indexing.

## Post-conditions

- Symbol extraction data populated (classes, functions, parameters, docstrings).
- Dependencies and imports mapped.
- Symbol table updated with parsed structures.
