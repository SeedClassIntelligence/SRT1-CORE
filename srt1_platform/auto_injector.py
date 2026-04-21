"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: CLI_ENTRY_POINT, DATA_MODEL
Key Symbols: SCIADocumentGenerator, main, __init__, run, _index ... and 8 more

Extracted Purposes:
  - SCIADocumentGenerator: Generates AI-readable context files from SRT-1's codebase knowledge.
  - run: Full pipeline: index → analyze flow → generate all context files.
  - _index: Run the SRT-1 Code Indexer.
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 Auto-Injector — The Last Mile

FILE: srt1_auto_injector.py
PURPOSE: Bridges SRT-1's knowledge directly into AI coding environments
         by generating files that AI tools automatically read.

HOW IT WORKS:
    Every AI coding tool (Claude Code, Cursor, VS Code Copilot, Antigravity,
    Windsurf, etc.) reads certain files in your project for context:

    - CLAUDE.md          → Claude Code / Antigravity
    - .cursorrules       → Cursor
    - AGENTS.md          → Generic agent instructions
    - .github/copilot-instructions.md → GitHub Copilot
    - .srt1/context.md   → Universal SRT-1 context (any tool can read)

    This script generates ALL of those files, populated with SRT-1's
    codebase knowledge, task tracking, and anti-hallucination directives.

    When the AI coding assistant opens your project, it AUTOMATICALLY reads
    these files and knows:
    - What every function does
    - What's risky
    - What's duplicated
    - What the current task is
    - What NOT to do

    No manual pasting. No API calls. The AI just reads a file.

USAGE:
    python srt1_auto_injector.py --repo_path ./my_project
    python srt1_auto_injector.py --repo_path ./my_project --task "Add logout feature"
    python srt1_auto_injector.py --repo_path ./my_project --watch

Author : William Darnell Jernigan IV (Architect)
License: Apache License 2.0
"""

import os
import sys
import json
import time
import hashlib
import argparse
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

# ---- Import the indexer ----
try:
    from srt1_code_indexer import SRT1CodeIndexer
except ImportError:
    # Fallback: import the standalone script's class
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from srt1_code_indexer import SRT1CodeIndexer
    except ImportError:
        print("[FATAL] Cannot import SRT1CodeIndexer. Ensure srt1_code_indexer.py is available.")
        sys.exit(1)


class SCIADocumentGenerator:
    """
    Generates AI-readable context files from SRT-1's codebase knowledge.
    Drop-in auto-injection for every major AI coding tool.
    """

    # Files to skip when scanning (don't index our own output)
    OWN_FILES = {
        "CLAUDE.md", ".cursorrules", "AGENTS.md",
        "copilot-instructions.md", "context.md",
    }

    def __init__(self, repo_path: str, task: Optional[str] = None):
        self.repo_path = os.path.abspath(repo_path)
        self.task = task
        self.manifest: Dict[str, Any] = {}
        self.symbol_table: Dict[str, List[Dict]] = {}
        self.curation_report: Dict[str, Any] = {}
        self.call_graph: Dict[str, List[str]] = {}  # function -> [functions it calls]
        
        # Drift Audit state
        self.high_drift_files: List[Dict[str, Any]] = []
        self.CANONICAL_SEEDS = {
            "srt1", "seed", "reflection", "coherence", "drift",
            "signature", "client", "api", "auth", "dashboard",
            "engine", "indexer", "jwt", "fastapi", "uvicorn",
            "telemetry", "trust"
        }
        self.DRIFT_INDICATORS = {
            "flask", "django", "sqlite3", "boto3", "aws", "print_exc",
            "ip_secure", "internal_signing", "MemPalace",
            "tmp", "scratch", "TODO", "FIXME", "legacy"
        }
        self.EXCLUDE_DIRS = {".git", ".agent", ".vscode", "node_modules", "storage", "__pycache__", "test_venv", "venv", "env"}

    def run(self) -> None:
        """Full pipeline: index → analyze flow → generate all context files."""
        print("\n  SRT-1 Auto-Injector")
        print("  " + "=" * 50)

        # Step 1: Index the codebase
        print("\n  [1/4] Indexing codebase...")
        self._index()

        # Step 2: Build call graph (flow mapping)
        print("  [2/5] Building call graph...")
        self._build_call_graph()

        # Step 3: Drift Audit
        print("  [3/5] Auditing for structural drift...")
        self._run_drift_audit()

        # Step 4: Generate all context files
        print("  [4/5] Generating AI context files...")
        self._generate_all_context_files()

        # Step 5: Summary
        print("  [5/5] Done.\n")
        self._print_summary()

    def _index(self) -> None:
        """Run the SRT-1 Code Indexer."""
        indexer = SRT1CodeIndexer(self.repo_path)
        self.manifest = indexer.index_repository()
        self.symbol_table = indexer.symbol_table
        self.curation_report = indexer.curation_report

    def _build_call_graph(self) -> None:
        """
        Build a cross-file call graph: for each function, trace what it calls
        and resolve those calls to actual functions in the codebase.
        """
        # First, build a lookup: function_name -> (file, line, type)
        all_symbols: Dict[str, List[Dict]] = {}
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                name = sym["name"]
                if name not in all_symbols:
                    all_symbols[name] = []
                all_symbols[name].append({
                    "file": fpath,
                    "line": sym["line"],
                    "type": sym["type"],
                })

        # Now trace: for each function, which known functions does it call?
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                key = f"{fpath}:{sym['name']}"
                resolved_calls = []

                for dep in sym.get("dependencies", []):
                    if dep in all_symbols:
                        for target in all_symbols[dep]:
                            resolved_calls.append(
                                f"{target['file']}:{dep}:{target['line']}"
                            )

                if resolved_calls:
                    self.call_graph[key] = resolved_calls

        print(f"        Mapped {len(self.call_graph)} call chains across files.")

    def _run_drift_audit(self) -> None:
        """Scan the entire workspace for files missing architectural context."""
        import re
        self.high_drift_files = []
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
            for file in files:
                if not (file.endswith(".py") or file.endswith(".js") or file.endswith(".html")):
                    continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                except Exception:
                    continue

                words = set(re.findall(r'[a-z0-9_]+', content))
                if not words:
                    continue

                coherence_hits = sum(1 for seed in self.CANONICAL_SEEDS if seed in words)
                drift_hits = sum(1 for indicator in self.DRIFT_INDICATORS if indicator in words)

                coherence_score = (coherence_hits / len(self.CANONICAL_SEEDS)) * 100
                drift_score = 100.0 - coherence_score + (drift_hits * 15.0)
                drift_score = min(100.0, max(0.0, drift_score))

                line_count = len(content.splitlines())
                if line_count < 20: 
                    continue

                if drift_score >= 50.0:
                    rel_path = os.path.relpath(filepath, self.repo_path)
                    self.high_drift_files.append({
                        "file": rel_path,
                        "drift": drift_score,
                        "lines": line_count,
                        "flags": [ind for ind in self.DRIFT_INDICATORS if ind in words]
                    })
        
        # Sort worst offenders to the top
        self.high_drift_files.sort(key=lambda x: x['drift'], reverse=True)
        print(f"        Identified {len(self.high_drift_files)} high-drift files.")

    # -----------------------------------------------------------------
    # CONTEXT FILE GENERATION
    # -----------------------------------------------------------------

    def _generate_all_context_files(self) -> None:
        """Generate context files for all supported AI tools."""
        content = self._build_universal_context()

        # 1. CLAUDE.md (Claude Code, Antigravity)
        self._write_file("CLAUDE.md", content)

        # 2. .cursorrules (Cursor)
        self._write_file(".cursorrules", content)

        # 3. AGENTS.md (generic)
        self._write_file("AGENTS.md", content)

        # 4. .github/copilot-instructions.md (GitHub Copilot)
        github_dir = os.path.join(self.repo_path, ".github")
        os.makedirs(github_dir, exist_ok=True)
        self._write_file(os.path.join(".github", "copilot-instructions.md"), content)

        # 5. .srt1/context.md (universal SRT-1 context)
        srt1_dir = os.path.join(self.repo_path, ".srt1")
        os.makedirs(srt1_dir, exist_ok=True)
        self._write_file(os.path.join(".srt1", "context.md"), content)

    def _write_file(self, rel_path: str, content: str) -> None:
        """Write a context file to the repo."""
        full_path = os.path.join(self.repo_path, rel_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"        ✓ {rel_path}")

    def _build_universal_context(self) -> str:
        """
        Build the universal context document that all AI tools will read.
        This is the INJECTION — the brain dump that keeps the AI on task.
        """
        lines: List[str] = []

        # ---- HEADER ----
        lines.append("# SRT-1 Codebase Intelligence")
        lines.append("")
        lines.append("> **AUTO-GENERATED by SRT-1 Code Indexer v2.0**")
        lines.append(f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"> Repository: {os.path.basename(self.repo_path)}")
        lines.append("")
        lines.append("**READ THIS BEFORE EVERY ACTION.** This file contains")
        lines.append("the complete knowledge map of this codebase. Use it to:")
        lines.append("- Know what already exists before building anything new")
        lines.append("- Understand what each file and function does")
        lines.append("- Avoid duplicating existing functionality")
        lines.append("- Identify risky code that needs careful handling")
        lines.append("")

        # ---- ACTIVE TASK ----
        if self.task:
            lines.append("## 🌱 ACTIVE TASK")
            lines.append("")
            lines.append(f"**{self.task}**")
            lines.append("")
            lines.append("Stay focused on this task. Do not drift into unrelated work.")
            lines.append("Every change you make should serve this goal.")
            lines.append("")

        # ---- CRITICAL WARNINGS ----
        warnings = self._collect_warnings()
        if warnings or self.high_drift_files:
            lines.append("## ⚠️ WARNINGS — DO NOT IGNORE")
            lines.append("")
            if self.high_drift_files:
                lines.append("🚨 **CRITICAL ARCHITECTURE DRIFT DETECTED** 🚨")
                lines.append("The following files have lost coherence with the active seed (100% drift).")
                lines.append("They are likely orphaned, hallucinated, or legacy. **QUARANTINE THEM.**")
                lines.append("Do NOT use them as architectural references:")
                for r in self.high_drift_files[:15]:
                    flags = f" (Flags: {', '.join(r['flags'])})" if r['flags'] else ""
                    lines.append(f"- `{r['file']}` [{r['drift']:.1f}% Drift]{flags}")
                lines.append("")

            for w in warnings:
                lines.append(f"- {w}")
            lines.append("")

        # ---- CODEBASE MAP ----
        lines.append("## 📁 Codebase Map")
        lines.append("")

        for fpath, symbols in self.symbol_table.items():
            lines.append(f"### `{fpath}`")
            lines.append("")

            # Group by type
            classes = [s for s in symbols if s["type"] == "class"]
            functions = [s for s in symbols if s["type"] == "function"]

            for cls in classes:
                ref = cls.get("reflection", {})
                risk = ref.get("risk_profile", [])
                risk_str = ", ".join(risk) if risk and risk != ["LOW_RISK"] else ""
                risk_badge = f" ⚠️ `{risk_str}`" if risk_str else ""

                lines.append(f"**`{cls['name']}`** (class, line {cls['line']}){risk_badge}")
                lines.append(f"  - Purpose: {ref.get('purpose', 'No docstring')}")
                lines.append(f"  - Role: {ref.get('architectural_role', 'GENERAL')}")

                # List dependencies
                deps = cls.get("dependencies", [])
                if deps:
                    lines.append(f"  - Calls: `{'`, `'.join(deps[:8])}`")

                lines.append("")

            for func in functions:
                ref = func.get("reflection", {})
                risk = ref.get("risk_profile", [])
                risk_str = ", ".join(risk) if risk and risk != ["LOW_RISK"] else ""
                risk_badge = f" ⚠️ `{risk_str}`" if risk_str else ""

                # Skip __init__ clutter
                if func["name"] == "__init__":
                    continue

                params = func.get("parameters", [])
                params_clean = [p for p in params if p != "self"]
                param_str = f"({', '.join(params_clean)})" if params_clean else "()"

                lines.append(f"- `{func['name']}{param_str}` (line {func['line']}){risk_badge}")
                lines.append(f"  - {ref.get('purpose', 'No docstring')}")

                # Show call chain if mapped
                key = f"{fpath}:{func['name']}"
                if key in self.call_graph:
                    targets = self.call_graph[key]
                    chain_parts = [t.split(":")[1] for t in targets[:5]]
                    lines.append(f"  - Calls → `{'` → `'.join(chain_parts)}`")

                lines.append("")

        # ---- CALL FLOW MAP ----
        if self.call_graph:
            lines.append("## 🔗 Call Flow Map")
            lines.append("")
            lines.append("How functions connect across files:")
            lines.append("")

            for source, targets in self.call_graph.items():
                src_file, src_func = source.split(":", 1)
                for target in targets[:3]:
                    parts = target.split(":")
                    tgt_file, tgt_func = parts[0], parts[1]
                    if src_file != tgt_file:
                        lines.append(
                            f"- `{src_func}` ({src_file}) → `{tgt_func}` ({tgt_file})"
                        )

            lines.append("")

        # ---- RULES ----
        lines.append("## 📋 SCIA Working Logic & Core Directives")
        lines.append("")
        lines.append("**PROTOCOL BINDING:** You are operating under the Seed-Class Intelligence Architecture (SCIA).")
        lines.append("You are not a standard code generator. You are a Coherence Engine.")
        lines.append("")
        lines.append("**1. The Seed (Canonical Intent):**")
        lines.append("   Before you execute any code, you must anchor to the active Seed (Task).")
        lines.append("   Every N operations, you must reflect: 'Does this change serve the Seed?'")
        lines.append("")
        lines.append("**2. Trace Logging (Cryptographic Provenance):**")
        lines.append("   Assume every function, class, and architectural decision you make is being")
        lines.append("   hashed and traced. Do not create 'black box' modifications.")
        lines.append("")
        lines.append("**3. Drift Prevention (The Immune System):**")
        lines.append("   If you encounter a file listed in the 'CRITICAL ARCHITECTURE DRIFT' section above,")
        lines.append("   you are FORBIDDEN from using its logic as an architectural reference.")
        lines.append("   Those files have >50% semantic drift and are infected with legacy architecture.")
        lines.append("")
        lines.append("**4. Zero-Duplication Directive:**")
        lines.append("   Check the Codebase Map before creating a new function. If a utility or")
        lines.append("   concept exists, wire into it. Empty harnesses and orphaned logic trigger SCIA alarms.")
        lines.append("")
        lines.append("**5. Risk-Aware Execution:**")
        lines.append("   Respect risk tags. Functions tagged `AUTH_SENSITIVE`, `WRITES_TO_DB`, ")
        lines.append("   or `DYNAMIC_EXECUTION` require explicit structural reverence.")
        lines.append("")

        # ---- FOOTER ----
        lines.append("---")
        lines.append(f"*Generated by SRT-1 Code Indexer v2.0 — {datetime.now().isoformat()}*")
        lines.append(f"*Seed-Class Intelligence Architecture (SCIA) — Apache 2.0*")

        return "\n".join(lines)

    def _collect_warnings(self) -> List[str]:
        """Collect all curation warnings."""
        warnings = []

        for overlap in self.curation_report.get("functional_overlaps", []):
            func = overlap["instances"][0]["function"]
            canon = overlap.get("canonical", "")
            instances = [f"`{i['file']}:{i['line']}`" for i in overlap["instances"]]
            warnings.append(
                f"**`{func}()`** exists in {', '.join(instances)}. "
                f"Use `{canon}` as the canonical version. Do NOT create another."
            )

        for dup in self.curation_report.get("duplicate_files", []):
            canon = dup.get("canonical", "")
            warnings.append(f"Duplicate files detected. Use `{canon}` as canonical.")

        # High-risk functions
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                risk = sym.get("reflection", {}).get("risk_profile", [])
                if "DYNAMIC_EXECUTION" in risk:
                    warnings.append(
                        f"**`{sym['name']}`** in `{fpath}` uses dynamic execution "
                        f"(eval/exec). Handle with extreme care."
                    )

        return warnings

    # -----------------------------------------------------------------
    # WATCH MODE
    # -----------------------------------------------------------------

    def watch(self, interval: int = 30) -> None:
        """Continuously watch for changes and regenerate context files."""
        print(f"\n  SRT-1 Auto-Injector — Watch Mode")
        print(f"  Checking every {interval}s for changes...")
        print(f"  Press Ctrl+C to stop.\n")

        last_hashes: Dict[str, str] = {}

        while True:
            # Check if files changed
            changed = False
            for entry in self.manifest.get("file_manifest", []):
                fp = os.path.join(self.repo_path, entry.get("file_path", ""))
                if os.path.exists(fp):
                    try:
                        with open(fp, "rb") as f:
                            h = hashlib.sha256(f.read()).hexdigest()
                        if last_hashes.get(entry["file_path"]) != h:
                            changed = True
                            last_hashes[entry["file_path"]] = h
                    except OSError:
                        pass

            if changed:
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] Changes detected — regenerating...")
                self.run()
            else:
                pass  # Silent when no changes

            time.sleep(interval)

    def _print_summary(self) -> None:
        """Print what was generated."""
        total_files = len(self.manifest.get("file_manifest", []))
        total_syms = sum(len(s) for s in self.symbol_table.values())
        total_chains = len(self.call_graph)
        total_warnings = len(self._collect_warnings())

        print(f"  Summary:")
        print(f"    Files indexed:    {total_files}")
        print(f"    Symbols mapped:   {total_syms}")
        print(f"    Call chains:      {total_chains}")
        print(f"    Warnings:         {total_warnings}")
        print(f"    Task:             {self.task or '(none set)'}")
        print()
        print(f"  Generated files:")
        print(f"    ✓ CLAUDE.md              → Claude Code / Antigravity")
        print(f"    ✓ .cursorrules           → Cursor")
        print(f"    ✓ AGENTS.md              → Generic AI agents")
        print(f"    ✓ .github/copilot-instructions.md → GitHub Copilot")
        print(f"    ✓ .srt1/context.md       → Universal SRT-1 context")
        print()
        print(f"  Your AI assistant will now automatically read these files")
        print(f"  and know your entire codebase. No pasting required.")
        print()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SRT-1 Auto-Injector — Bridge SRT-1 knowledge into AI coding tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python srt1_auto_injector.py --repo_path ./my_project\n"
            "  python srt1_auto_injector.py --repo_path . --task 'Add user logout'\n"
            "  python srt1_auto_injector.py --repo_path . --task 'Fix payment bug' --watch\n"
        ),
    )
    parser.add_argument("--repo_path", required=True, help="Path to the repository")
    parser.add_argument("--task", help="Current task (planted as the active seed)")
    parser.add_argument("--watch", action="store_true", help="Watch mode — regenerate on changes")
    args = parser.parse_args()

    injector = SCIADocumentGenerator(repo_path=args.repo_path, task=args.task)
    injector.run()

    if args.watch:
        try:
            injector.watch()
        except KeyboardInterrupt:
            print("\n  SRT-1 Auto-Injector stopped.")


if __name__ == "__main__":
    main()
