"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: CLI_ENTRY_POINT, TRACING_AUDIT
Key Symbols: SCIAContextBundler, main, __init__, _load_manifest, _build_indices ... and 12 more

Extracted Purposes:
  - SCIAContextBundler: Phase 2 of the SCIA pipeline.
  - _load_manifest: Load the Phase 1 Code Manifest and verify its integrity.
  - _build_indices: Build searchable indices from the manifest for fast lookups.
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 Context Bundler (Phase 2) - Intelligent Context Assembly Engine

FILE: srt1_context_bundler.py
SRT-1 TAG: CONTEXT_BUNDLER :: INTELLIGENT_ROUTER

Purpose:
    Consumes the Code Manifest (Phase 1 output) and a developer task,
    then assembles a surgically precise Context Bundle containing only
    the relevant code, reflections, and architectural context needed
    for an AI code assistant to execute the task correctly.

Architecture:
    Phase 1 (Indexer)  -->  srt1_code_manifest.json
    Phase 2 (Bundler)  -->  reads manifest + task --> Context Bundle
    Phase 3 (Executor) -->  validates and executes via AI assistant

Author : William Darnell Jernigan IV (Architect)
License: Business Source License 1.1
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

# Core SCIA IP imports
try:
    from srt1_code_indexer.srt import SRT
except ImportError:
    try:
        from srt import SRT
    except ImportError:
        sys.exit("[FATAL] Cannot import SRT. Ensure srt.py is available.")




class SCIAContextBundler:
    """
    Phase 2 of the SCIA pipeline.

    Given a developer task and a Code Manifest, assembles an optimized
    Context Bundle that provides an AI code assistant with:
      - The exact source code it needs
      - The architectural context (roles, risks, dependencies)
      - Clear instructions derived from the task analysis
    """

    def __init__(self, manifest_path: str):
        if not os.path.isfile(manifest_path):
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        self.manifest_path = os.path.abspath(manifest_path)
        self.manifest: Dict[str, Any] = {}
        self.repo_path: str = ""

        # Core SCIA tools
        self.srt_tool = SRT()

        # Internal indices built from manifest
        self._symbol_index: Dict[str, Dict[str, Any]] = {}
        self._keyword_index: Dict[str, List[str]] = defaultdict(list)
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_deps: Dict[str, Set[str]] = defaultdict(set)
        self._file_to_symbols: Dict[str, List[str]] = defaultdict(list)

        # Load and index
        self._load_manifest()
        self._build_indices()

    # ==========================================================================
    # INITIALIZATION
    # ==========================================================================

    def _load_manifest(self) -> None:
        """Load the Phase 1 Code Manifest and verify its integrity."""
        with open(self.manifest_path, "r", encoding="utf-8") as fh:
            self.manifest = json.load(fh)

        self.repo_path = self.manifest.get("metadata", {}).get("repo_path", "")

        # Verify integrity hash if present
        integrity = self.manifest.get("integrity")
        if integrity:
            manifest_hash = integrity.get("manifest_hash", "N/A")
            print(f"  [Bundler] Manifest loaded. Integrity: {manifest_hash[:16]}...")
        else:
            print("  [Bundler] Manifest loaded. No integrity hash found.")

    def _build_indices(self) -> None:
        """Build searchable indices from the manifest for fast lookups."""
        symbol_table = self.manifest.get("symbol_table", {})
        reflections = self.manifest.get("reflections", [])

        # Build reflection lookup by (file, symbol_name)
        reflection_lookup: Dict[Tuple[str, str], Dict] = {}
        for ref in reflections:
            meta = ref.get("metadata", {})
            key = (meta.get("file", ""), meta.get("symbol", ""))
            try:
                reflection_lookup[key] = json.loads(ref.get("content", "{}"))
            except json.JSONDecodeError:
                pass

        # Process symbol table
        for file_path, symbols in symbol_table.items():
            for sym in symbols:
                sym_name = sym["name"]
                qualified_name = f"{file_path}::{sym_name}"

                # Master symbol index
                reflection = reflection_lookup.get((file_path, sym_name), {})
                self._symbol_index[qualified_name] = {
                    "name": sym_name,
                    "file": file_path,
                    "type": sym.get("type", "unknown"),
                    "line": sym.get("line"),
                    "end_line": sym.get("end_line"),
                    "parameters": sym.get("parameters", []),
                    "dependencies": sym.get("dependencies", []),
                    "docstring": sym.get("docstring_first_line", ""),
                    "role": reflection.get("architectural_role", "GENERAL"),
                    "risk": reflection.get("risk_profile", []),
                    "purpose": reflection.get("purpose", ""),
                }

                # File-to-symbols mapping
                self._file_to_symbols[file_path].append(qualified_name)

                # Keyword index (name, docstring, role, purpose)
                keywords = set()
                keywords.add(sym_name.lower())
                # Split camelCase and snake_case into words
                for word in re.split(r"[_\s]+|(?<=[a-z])(?=[A-Z])", sym_name):
                    if word:
                        keywords.add(word.lower())
                if sym.get("docstring_first_line"):
                    for word in sym["docstring_first_line"].lower().split():
                        clean = re.sub(r"[^a-z0-9]", "", word)
                        if clean and len(clean) > 2:
                            keywords.add(clean)
                role = reflection.get("architectural_role", "")
                if role:
                    keywords.add(role.lower())
                    for part in role.lower().split("_"):
                        keywords.add(part)

                for kw in keywords:
                    self._keyword_index[kw].append(qualified_name)

                # Dependency graph
                for dep in sym.get("dependencies", []):
                    self._dependency_graph[qualified_name].add(dep)
                    self._reverse_deps[dep].add(qualified_name)

        total_symbols = len(self._symbol_index)
        total_keywords = len(self._keyword_index)
        print(f"  [Bundler] Indices built: {total_symbols} symbols, {total_keywords} keywords indexed.")

    # ==========================================================================
    # CORE PUBLIC METHOD
    # ==========================================================================

    def build_context_bundle(self, task: str, max_files: int = 10, max_depth: int = 3) -> Dict[str, Any]:
        """
        Given a developer task, assemble a complete Context Bundle.

        Args:
            task:      Natural language description of the development task.
            max_files: Maximum number of source files to include in the bundle.
            max_depth: Maximum depth for dependency chain traversal.

        Returns:
            A signed Context Bundle dictionary ready for Phase 3 consumption.
        """
        print()
        print("--- [SRT-1 Context Bundler] Building Context Bundle ---")
        print(f"    Task: {task[:100]}{'...' if len(task) > 100 else ''}")
        print()

        # Step 1: Analyze the task to extract search terms
        task_analysis = self._analyze_task(task)

        # Step 2: Search the manifest for relevant symbols
        relevant_symbols = self._search_symbols(task_analysis)

        # Step 3: Expand via dependency tracing
        expanded_symbols = self._trace_dependencies(relevant_symbols, max_depth)

        # Step 4: Read the actual source code for relevant files
        source_extracts = self._extract_source_code(expanded_symbols, max_files)

        # Step 5: Build architectural context from reflections
        arch_context = self._build_architectural_context(expanded_symbols)

        # Step 6: Generate the task directive
        directive = self._generate_directive(task, task_analysis, arch_context)

        # Step 7: Assemble the Context Bundle
        bundle = self._assemble_bundle(
            task=task,
            task_analysis=task_analysis,
            relevant_symbols=expanded_symbols,
            source_extracts=source_extracts,
            architectural_context=arch_context,
            directive=directive,
        )

        # Step 8: Sign the bundle
        bundle = self._sign_bundle(bundle)

        print()
        print("--- [SRT-1 Context Bundler] Bundle Complete ---")
        return bundle

    # ==========================================================================
    # PIPELINE STAGES
    # ==========================================================================

    def _analyze_task(self, task: str) -> Dict[str, Any]:
        """Extract keywords, intent signals, and domain hints from the task."""
        task_lower = task.lower()

        # Extract meaningful keywords
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "it", "its", "this", "that", "these", "those", "i", "we",
            "you", "he", "she", "they", "my", "our", "your",
            "and", "but", "or", "not", "so", "if", "then", "else",
            "all", "each", "every", "some", "any", "no", "than",
            "just", "also", "very", "too", "as", "up", "about",
        }
        words = re.findall(r"[a-z][a-z0-9_]*", task_lower)
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        # Detect intent signals
        intent_signals = {
            "add": "FEATURE_ADD",
            "create": "FEATURE_ADD",
            "implement": "FEATURE_ADD",
            "build": "FEATURE_ADD",
            "fix": "BUG_FIX",
            "repair": "BUG_FIX",
            "debug": "BUG_FIX",
            "resolve": "BUG_FIX",
            "refactor": "REFACTOR",
            "clean": "REFACTOR",
            "optimize": "OPTIMIZATION",
            "improve": "OPTIMIZATION",
            "speed": "OPTIMIZATION",
            "performance": "OPTIMIZATION",
            "cache": "OPTIMIZATION",
            "test": "TESTING",
            "remove": "REMOVAL",
            "delete": "REMOVAL",
            "deprecate": "REMOVAL",
            "document": "DOCUMENTATION",
            "secure": "SECURITY",
            "auth": "SECURITY",
            "encrypt": "SECURITY",
            "migrate": "MIGRATION",
        }
        detected_intents = []
        for word in words:
            if word in intent_signals:
                intent = intent_signals[word]
                if intent not in detected_intents:
                    detected_intents.append(intent)

        # Detect architectural domain hints
        domain_hints = []
        domain_keywords = {
            "api": "API_CONTROLLER",
            "endpoint": "API_CONTROLLER",
            "route": "API_CONTROLLER",
            "database": "DATABASE_SERVICE",
            "query": "DATABASE_SERVICE",
            "model": "DATA_MODEL",
            "schema": "DATA_MODEL",
            "service": "SERVICE_LAYER",
            "test": "TEST",
            "config": "CONFIGURATION",
            "auth": "AUTH_SECURITY",
            "middleware": "MIDDLEWARE",
        }
        for word in words:
            if word in domain_keywords:
                hint = domain_keywords[word]
                if hint not in domain_hints:
                    domain_hints.append(hint)

        analysis = {
            "original_task": task,
            "keywords": keywords,
            "intents": detected_intents if detected_intents else ["GENERAL"],
            "domain_hints": domain_hints,
            "word_count": len(words),
        }

        print(f"  [1/7] Task Analysis: {len(keywords)} keywords, intents={analysis['intents']}, domains={domain_hints}")
        return analysis

    def _search_symbols(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search the manifest indices for symbols matching the task.

        Scoring: name match (5.0), keyword*IDF (3.0), purpose overlap (2.0),
        substring (1.0), domain boost (5.0), dunder penalty (0.5x).
        """
        import math
        scores: Dict[str, float] = defaultdict(float)
        keywords = task_analysis["keywords"]
        domain_hints = task_analysis["domain_hints"]
        keyword_set = set(keywords)

        # IDF: keywords in fewer symbols score higher
        total_symbols = max(len(self._symbol_index), 1)
        idf: Dict[str, float] = {}
        for kw in keywords:
            doc_freq = len(self._keyword_index.get(kw, []))
            idf[kw] = math.log(total_symbols / max(doc_freq, 1)) + 1.0

        # Keyword matching with IDF weighting
        for kw in keywords:
            weight = idf.get(kw, 1.0)
            if kw in self._keyword_index:
                for qname in self._keyword_index[kw]:
                    scores[qname] += 3.0 * weight
            for indexed_kw, qnames in self._keyword_index.items():
                if indexed_kw == kw:
                    continue
                if kw in indexed_kw or indexed_kw in kw:
                    for qname in qnames:
                        scores[qname] += 1.0

        # Direct name match bonus (strongest signal)
        for qname, sym_info in self._symbol_index.items():
            name_parts = set(re.split(r"[_\s]+", sym_info["name"].lower()))
            overlap = keyword_set & name_parts
            if overlap:
                scores[qname] += 5.0 * len(overlap)

        # Purpose/docstring text matching
        for qname, sym_info in self._symbol_index.items():
            purpose = sym_info.get("purpose", "").lower()
            if purpose:
                purpose_words = set(re.findall(r"[a-z][a-z0-9]+", purpose))
                overlap = keyword_set & purpose_words
                if overlap:
                    scores[qname] += 2.0 * len(overlap)

        # Domain/role boosting
        for qname, sym_info in self._symbol_index.items():
            role = sym_info.get("role", "")
            if role in domain_hints:
                scores[qname] += 5.0

        # Dunder penalty (reduce noise)
        for qname in list(scores.keys()):
            name = self._symbol_index.get(qname, {}).get("name", "")
            if name.startswith("__") and name.endswith("__"):
                scores[qname] *= 0.5

        # Rank and filter
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for qname, score in ranked:
            if score >= 2.0:
                sym = self._symbol_index[qname].copy()
                sym["relevance_score"] = round(score, 2)
                sym["qualified_name"] = qname
                results.append(sym)
        results = results[:30]
        print(f"  [2/7] Symbol Search: Found {len(results)} relevant symbols (from {len(scores)} candidates).")
        return results

    def _trace_dependencies(self, symbols: List[Dict[str, Any]], max_depth: int) -> List[Dict[str, Any]]:
        """Expand the symbol set by tracing dependency chains."""
        known_qnames = {s["qualified_name"] for s in symbols}
        frontier = list(known_qnames)
        visited: Set[str] = set(known_qnames)
        added = []

        for depth in range(max_depth):
            next_frontier = []
            for qname in frontier:
                sym_info = self._symbol_index.get(qname)
                if not sym_info:
                    continue
                # Forward dependencies
                for dep_name in sym_info.get("dependencies", []):
                    # Find the qualified name for this dependency
                    for candidate_qname, candidate_info in self._symbol_index.items():
                        if candidate_info["name"] == dep_name and candidate_qname not in visited:
                            visited.add(candidate_qname)
                            next_frontier.append(candidate_qname)
                            dep_entry = candidate_info.copy()
                            dep_entry["qualified_name"] = candidate_qname
                            dep_entry["relevance_score"] = 1.0 / (depth + 2)
                            dep_entry["trace_reason"] = f"dependency of {qname} (depth {depth + 1})"
                            added.append(dep_entry)

                # Reverse dependencies (who calls this symbol)
                for caller_qname in self._reverse_deps.get(sym_info["name"], set()):
                    if caller_qname not in visited:
                        visited.add(caller_qname)
                        caller_info = self._symbol_index.get(caller_qname)
                        if caller_info:
                            entry = caller_info.copy()
                            entry["qualified_name"] = caller_qname
                            entry["relevance_score"] = 0.5 / (depth + 2)
                            entry["trace_reason"] = f"calls {qname} (depth {depth + 1})"
                            added.append(entry)

            frontier = next_frontier
            if not frontier:
                break

        all_symbols = symbols + added
        print(f"  [3/7] Dependency Trace: Expanded from {len(symbols)} to {len(all_symbols)} symbols (depth {max_depth}).")
        return all_symbols

    def _extract_source_code(self, symbols: List[Dict[str, Any]], max_files: int) -> Dict[str, str]:
        """Read the actual source code for the files containing relevant symbols."""
        # Determine which files to include, ranked by total relevance score
        file_scores: Dict[str, float] = defaultdict(float)
        for sym in symbols:
            file_scores[sym["file"]] += sym.get("relevance_score", 1.0)

        ranked_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)[:max_files]
        selected_files = {f for f, _ in ranked_files}

        source_extracts: Dict[str, str] = {}
        for file_path in selected_files:
            full_path = os.path.join(self.repo_path, file_path)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
                        source_extracts[file_path] = fh.read()
                except OSError as exc:
                    print(f"    [WARN] Could not read {file_path}: {exc}")

        total_lines = sum(s.count(chr(10)) for s in source_extracts.values())
        print(f"  [4/7] Source Extraction: Loaded {len(source_extracts)} files ({total_lines} lines).")
        return source_extracts

    def _build_architectural_context(self, symbols: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a structured architectural summary from the relevant symbols."""
        roles_found: Dict[str, List[str]] = defaultdict(list)
        risks_found: Dict[str, List[str]] = defaultdict(list)
        dep_chains: List[str] = []

        for sym in symbols:
            role = sym.get("role", "GENERAL")
            roles_found[role].append(sym["name"])
            for risk in sym.get("risk", []):
                risks_found[risk].append(sym["name"])

        # Build dependency chain descriptions
        for sym in symbols[:10]:
            deps = sym.get("dependencies", [])
            if deps:
                dep_names = ", ".join(deps[:5])
                dep_chains.append(f"{sym['name']} ({sym.get('role', '?')}) --> depends on: {dep_names}")

        context = {
            "roles_summary": {role: names[:5] for role, names in roles_found.items()},
            "risk_summary": {risk: names[:5] for risk, names in risks_found.items()},
            "dependency_chains": dep_chains[:15],
            "total_relevant_symbols": len(symbols),
            "files_involved": list(set(s["file"] for s in symbols)),
        }

        print(f"  [5/7] Architectural Context: {len(roles_found)} roles, {len(risks_found)} risk categories.")
        return context

    def _generate_directive(self, task: str, analysis: Dict[str, Any], arch_context: Dict[str, Any]) -> str:
        """Generate a clear, structured directive for the AI code assistant."""
        lines = []
        lines.append("=" * 70)
        lines.append("SRT-1 CONTEXT DIRECTIVE")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"TASK: {task}")
        lines.append("")
        lines.append(f"INTENT: {', '.join(analysis['intents'])}")
        lines.append(f"DOMAIN: {', '.join(analysis['domain_hints']) if analysis['domain_hints'] else 'GENERAL'}")
        lines.append("")

        # Architectural guidance
        lines.append("ARCHITECTURAL CONTEXT:")
        for role, names in arch_context.get("roles_summary", {}).items():
            lines.append(f"  [{role}]: {', '.join(names[:3])}")
        lines.append("")

        # Risk warnings
        risk_summary = arch_context.get("risk_summary", {})
        high_risk = [r for r in risk_summary if r in ("WRITES_TO_DB", "AUTH_SENSITIVE", "SYSTEM_SIDE_EFFECT", "EXTERNAL_API_CALL")]
        if high_risk:
            lines.append("RISK WARNINGS:")
            for risk in high_risk:
                affected = ", ".join(risk_summary[risk][:3])
                lines.append(f"  [{risk}]: Affects {affected}")
            lines.append("")

        # Dependency chain guidance
        chains = arch_context.get("dependency_chains", [])
        if chains:
            lines.append("DEPENDENCY CHAINS (modify in this order):")
            for i, chain in enumerate(chains[:8], 1):
                lines.append(f"  {i}. {chain}")
            lines.append("")

        lines.append("INSTRUCTIONS:")
        lines.append("  1. Review the source code provided below.")
        lines.append("  2. Respect the architectural roles and dependency chains above.")
        lines.append("  3. Do NOT modify files or functions outside the relevant scope.")
        lines.append("  4. If the task requires new files, follow existing naming conventions.")
        lines.append("  5. Preserve all existing integrity hashes and SRT-1 reflections.")
        lines.append("=" * 70)

        directive = chr(10).join(lines)
        print(f"  [6/7] Directive Generated: {len(lines)} lines.")
        return directive

    def _assemble_bundle(self, task: str, task_analysis: Dict[str, Any],
                         relevant_symbols: List[Dict[str, Any]],
                         source_extracts: Dict[str, str],
                         architectural_context: Dict[str, Any],
                         directive: str) -> Dict[str, Any]:
        """Assemble all components into the final Context Bundle."""

        # Build the symbol summary (without full source, for the structured section)
        symbol_summaries = []
        for sym in relevant_symbols:
            symbol_summaries.append({
                "name": sym["name"],
                "file": sym["file"],
                "type": sym["type"],
                "line": sym.get("line"),
                "role": sym.get("role", "GENERAL"),
                "risk": sym.get("risk", []),
                "purpose": sym.get("purpose", ""),
                "relevance_score": sym.get("relevance_score", 0),
                "trace_reason": sym.get("trace_reason", "direct match"),
            })

        # Build the super-prompt (human-readable context block)
        super_prompt_parts = [directive, "", ""]
        super_prompt_parts.append("SOURCE CODE:")
        super_prompt_parts.append("" + "=" * 70)
        for file_path, source in source_extracts.items():
            super_prompt_parts.append(f"--- FILE: {file_path} ---")
            super_prompt_parts.append(source)
            super_prompt_parts.append(f"--- END: {file_path} ---")
            super_prompt_parts.append("")

        super_prompt = chr(10).join(super_prompt_parts)

        bundle = {
            "bundle_metadata": {
                "bundle_version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "manifest_source": "<scrubbed_manifest_path>",
                "repo_path": "<scrubbed_repo_root>",
                "task": task,
            },
            "task_analysis": task_analysis,
            "relevant_symbols": symbol_summaries,
            "architectural_context": architectural_context,
            "source_extracts": source_extracts,
            "directive": directive,
            "super_prompt": super_prompt,
            "phase3_ready": True,
        }

        return bundle

    def _finalize_bundle(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Compute integrity hash for the Context Bundle."""
        # Add SRT reflection for this bundle operation
        self.srt_tool.add_reflection(
            reflection_type="context_bundle",
            content=json.dumps({
                "task": bundle["bundle_metadata"]["task"],
                "symbols_included": len(bundle["relevant_symbols"]),
                "files_included": len(bundle["source_extracts"]),
            }),
            metadata={"operation": "CONTEXT_BUNDLING"},
        )

        # Compute integrity hash
        bundle_json = json.dumps(bundle, sort_keys=True, default=str)
        integrity_hash = hashlib.sha256(bundle_json.encode('utf-8')).hexdigest()
        bundle["integrity"] = {
            "hash_algorithm": "sha256",
            "bundle_hash": integrity_hash,
            "timestamp": datetime.now().isoformat(),
        }

        print(f"  [7/7] Bundle Verified: {integrity_hash[:16]}...")
        return bundle

    # ==========================================================================
    # UTILITY: Save and Format
    # ==========================================================================

    def save_bundle(self, bundle: Dict[str, Any], output_path: str) -> str:
        """Save the Context Bundle to a JSON file."""
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(bundle, fh, indent=2, default=str)
        print(f"  [Bundler] Bundle saved to: {output_path}")
        return output_path

    def get_super_prompt(self, bundle: Dict[str, Any]) -> str:
        """Extract the human-readable super-prompt from a bundle."""
        return bundle.get("super_prompt", "")

    def print_bundle_summary(self, bundle: Dict[str, Any]) -> None:
        """Print a concise summary of the bundle."""
        meta = bundle.get("bundle_metadata", {})
        syms = bundle.get("relevant_symbols", [])
        src = bundle.get("source_extracts", {})
        integrity = bundle.get("integrity", {})
        arch = bundle.get("architectural_context", {})

        print("=" * 60)
        print("  SRT-1 CONTEXT BUNDLE SUMMARY")
        print("=" * 60)
        print(f"  Task:     {meta.get('task', 'N/A')[:80]}")
        print(f"  Symbols:  {len(syms)} relevant symbols identified")
        print(f"  Files:    {len(src)} source files loaded")
        print(f"  Roles:    {list(arch.get('roles_summary', {}).keys())}")
        print(f"  Risks:    {list(arch.get('risk_summary', {}).keys())}")
        print(f"  Integrity:{integrity.get('bundle_hash', 'N/A')[:16]}...")
        prompt = bundle.get("super_prompt", "")
        print(f"  Prompt:   {len(prompt)} chars / ~{len(prompt)//4} tokens")
        print("=" * 60)


# ==========================================================================
# CLI
# ==========================================================================

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="SRT-1 Context Bundler (Phase 2) - Assemble AI-ready context from a Code Manifest.",
    )
    parser.add_argument("--manifest", required=True, help="Path to srt1_code_manifest.json")
    parser.add_argument("--task", required=True, help="Developer task (natural language)")
    parser.add_argument("--output", default=None, help="Output path for the context bundle JSON")
    parser.add_argument("--max-files", type=int, default=10, help="Max source files to include")
    parser.add_argument("--max-depth", type=int, default=3, help="Max dependency trace depth")
    parser.add_argument("--print-prompt", action="store_true", help="Print the super-prompt to stdout")
    args = parser.parse_args()

    try:
        bundler = SCIAContextBundler(args.manifest)
        bundle = bundler.build_context_bundle(
            task=args.task,
            max_files=args.max_files,
            max_depth=args.max_depth,
        )

        bundler.print_bundle_summary(bundle)

        if args.output:
            bundler.save_bundle(bundle, args.output)
        else:
            # Default output next to manifest
            default_out = os.path.join(
                os.path.dirname(args.manifest),
                "srt1_context_bundle.json",
            )
            bundler.save_bundle(bundle, default_out)

        if args.print_prompt:
            print(bundler.get_super_prompt(bundle))

    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
