"""
SRT-1 Workspace Connector (Pro Feature)
========================================
Connects isolated module sandboxes into a unified cross-module view.

Each module runs in its own folder with its own SRT-1 engine.
The workspace connector collects summaries from each module and
builds a cross-module dependency map — all locally, zero network calls.

Usage:
    python -m srt1_pro.workspace_connector --root .
    srt1-code-indexer --workspace

Copyright 2026 Seed Class Intelligence. All rights reserved.
BSL 1.1 — Source Available. See LICENSE for terms.
"""

import os
import re
import ast
import json
import glob
import time
import argparse
from datetime import datetime
from collections import defaultdict

try:
    from srt1_code_indexer.language_parsers import dispatch_parser
except ImportError:
    try:
        from language_parsers import dispatch_parser
    except ImportError:
        dispatch_parser = lambda source, file_path, extension: []

# ─── MODULE SCANNER ───────────────────────────────────────────────

class ModuleScanner:
    """Scans a single module folder and produces a summary manifest."""

    # File extensions to scan
    PY_EXTENSIONS = {".py"}
    WEB_EXTENSIONS = {".html", ".js", ".jsx", ".css", ".scss", ".ts", ".tsx"}
    ALL_EXTENSIONS = PY_EXTENSIONS | WEB_EXTENSIONS | {".go", ".rs", ".java", ".c", ".cpp", ".h", ".md", ".json", ".yaml", ".yml"}

    def __init__(self, module_path: str, module_name: str):
        self.path = os.path.abspath(module_path)
        self.name = module_name
        self.files = []
        self.classes = []
        self.functions = []
        self.imports = []          # raw import statements
        self.exports = []          # public functions/classes this module exposes
        self.external_deps = []    # imports from OTHER modules

    def scan(self) -> dict:
        """Scan the module and return a structured summary."""
        self._collect_files()
        self._analyze_source_files()
        return self._build_summary()

    def _collect_files(self):
        """Walk the directory and collect all source files."""
        for root, dirs, files in os.walk(self.path):
            # Skip hidden dirs, __pycache__, node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'node_modules']
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in self.ALL_EXTENSIONS:
                    self.files.append({
                        "path": os.path.relpath(os.path.join(root, f), self.path),
                        "type": ext,
                        "size": os.path.getsize(os.path.join(root, f))
                    })

    def _analyze_source_files(self):
        """Parse all source files to extract classes, functions, and imports."""
        for file_info in self.files:
            ext = file_info["type"]
            full_path = os.path.join(self.path, file_info["path"])
            
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
            except OSError:
                continue

            if ext == ".py":
                self._analyze_python_file(source, file_info["path"])
            elif ext in {".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".c", ".cpp", ".h"}:
                self._analyze_with_regex(source, file_info["path"], ext)

    def _analyze_python_file(self, source: str, filepath: str):
        try:
            tree = ast.parse(source, filename=filepath)
            self._extract_from_ast(tree, filepath)
        except (SyntaxError, UnicodeDecodeError):
            pass

    def _analyze_with_regex(self, source: str, filepath: str, ext: str):
        symbols = dispatch_parser(source, filepath, ext)
        for sym in symbols:
            if sym["type"] == "class":
                self.classes.append({
                    "name": sym["name"],
                    "file": filepath,
                    "line": sym["line"],
                    "methods": []
                })
                self.exports.append(sym["name"])
            elif sym["type"] == "function":
                self.functions.append({
                    "name": sym["name"],
                    "file": filepath,
                    "line": sym["line"]
                })
                if not sym["name"].startswith("_"):
                    self.exports.append(sym["name"])
            elif sym["type"] in {"interface", "type", "enum", "struct", "trait"}:
                if not sym["name"].startswith("_"):
                    self.exports.append(sym["name"])
            # Note: For workspace connector we keep the existing import logic simple.
            # Regex parsers don't currently extract 'imports' robustly into a separate list.

    def _extract_from_ast(self, tree: ast.AST, filepath: str):
        """Extract classes, functions, and imports from an AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.classes.append({
                    "name": node.name,
                    "file": filepath,
                    "line": node.lineno,
                    "methods": [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                })
                self.exports.append(node.name)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Only top-level functions (not methods inside classes)
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                    pass
                self.functions.append({
                    "name": node.name,
                    "file": filepath,
                    "line": node.lineno
                })
                if not node.name.startswith("_"):
                    self.exports.append(node.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append({
                        "module": alias.name,
                        "alias": alias.asname,
                        "file": filepath
                    })

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.append({
                        "module": node.module,
                        "names": [a.name for a in node.names],
                        "file": filepath
                    })

    def _build_summary(self) -> dict:
        """Build the module summary."""
        py_files = [f for f in self.files if f["type"] == ".py"]
        web_files = [f for f in self.files if f["type"] in self.WEB_EXTENSIONS]
        total_size = sum(f["size"] for f in self.files)

        return {
            "name": self.name,
            "path": self.path,
            "total_files": len(self.files),
            "python_files": len(py_files),
            "web_files": len(web_files),
            "total_size_kb": round(total_size / 1024, 1),
            "classes": len(self.classes),
            "functions": len(self.functions),
            "class_names": [c["name"] for c in self.classes],
            "public_exports": list(set(self.exports)),
            "imports": self.imports,
            "file_list": [f["path"] for f in self.files]
        }


# ─── WORKSPACE CONNECTOR ─────────────────────────────────────────

class WorkspaceConnector:
    """
    Connects multiple isolated SRT-1 module sandboxes into a unified view.
    
    This is the Pro feature that turns individual module intelligence
    into cross-module architectural understanding.
    """

    def __init__(self, root_path: str):
        self.root = os.path.abspath(root_path)
        self.workspace_config = {}
        self.module_summaries = {}
        self.dependency_map = {}
        self.cross_module_calls = []

    def load_workspace(self) -> bool:
        """Load workspace.json configuration."""
        config_path = os.path.join(self.root, ".srt1", "workspace.json")
        if not os.path.exists(config_path):
            print(f"  ✗ No workspace.json found at {config_path}")
            print(f"    Create .srt1/workspace.json to define your modules.")
            return False

        with open(config_path, "r", encoding="utf-8") as f:
            self.workspace_config = json.load(f)

        print(f"  ✓ Workspace loaded: {self.workspace_config.get('workspace', 'Unnamed')}")
        print(f"    {len(self.workspace_config.get('modules', []))} modules defined")
        return True

    def scan_all_modules(self):
        """Scan every module defined in workspace.json."""
        modules = self.workspace_config.get("modules", [])
        print()
        for i, mod in enumerate(modules, 1):
            name = mod["name"]
            path = os.path.join(self.root, mod["path"])

            if not os.path.isdir(path):
                print(f"  [{i}/{len(modules)}] ✗ {name} — path not found: {mod['path']}")
                continue

            print(f"  [{i}/{len(modules)}] Scanning {name}...", end="", flush=True)
            scanner = ModuleScanner(path, name)
            summary = scanner.scan()
            self.module_summaries[name] = summary
            print(f" {summary['total_files']} files, {summary['classes']} classes, {summary['functions']} functions")

    def build_dependency_map(self):
        """Analyze imports across modules to find cross-module dependencies."""
        # Build a lookup: which module owns which symbol?
        symbol_owners = {}  # symbol_name -> module_name
        module_packages = {}  # package_prefix -> module_name

        # Map known package prefixes to modules
        for name, summary in self.module_summaries.items():
            # Infer package name from directory name
            dir_name = os.path.basename(summary["path"])
            module_packages[dir_name] = name

            # Map all exported symbols
            for export in summary.get("public_exports", []):
                symbol_owners[export] = name

        # Now check every import in every module
        for mod_name, summary in self.module_summaries.items():
            deps = set()
            for imp in summary.get("imports", []):
                imp_module = imp.get("module", "")

                # Check if this import references another module's package
                for pkg_prefix, owner_name in module_packages.items():
                    if owner_name != mod_name and (
                        imp_module == pkg_prefix or
                        imp_module.startswith(pkg_prefix + ".") or
                        imp_module.startswith(pkg_prefix.replace("-", "_") + ".")
                    ):
                        deps.add(owner_name)
                        imported_names = imp.get("names", [imp_module])
                        self.cross_module_calls.append({
                            "from_module": mod_name,
                            "to_module": owner_name,
                            "import": imp_module,
                            "names": imported_names if isinstance(imported_names, list) else [imported_names],
                            "file": imp.get("file", "")
                        })

            self.dependency_map[mod_name] = sorted(deps)

    def generate_report(self) -> str:
        """Generate a human-readable cross-module report."""
        lines = []
        ws_name = self.workspace_config.get("workspace", "Unnamed Workspace")

        lines.append("")
        lines.append("  ╔══════════════════════════════════════════════════════════════╗")
        lines.append(f"  ║  SRT-1 Workspace Connector — {ws_name:<30}║")
        lines.append("  ╚══════════════════════════════════════════════════════════════╝")
        lines.append("")

        # ── Module Summary Table ──
        lines.append("  ┌─ Module Summary ────────────────────────────────────────────┐")
        lines.append("  │                                                             │")
        lines.append(f"  │  {'Module':<14} {'Files':>6} {'Classes':>9} {'Functions':>11} {'Size':>8}  │")
        lines.append(f"  │  {'─'*14} {'─'*6} {'─'*9} {'─'*11} {'─'*8}  │")

        totals = {"files": 0, "classes": 0, "functions": 0, "size": 0}
        for name, summary in self.module_summaries.items():
            f = summary["total_files"]
            c = summary["classes"]
            fn = summary["functions"]
            sz = summary["total_size_kb"]
            totals["files"] += f
            totals["classes"] += c
            totals["functions"] += fn
            totals["size"] += sz
            lines.append(f"  │  {name:<14} {f:>6} {c:>9} {fn:>11} {sz:>6.0f}KB  │")

        lines.append(f"  │  {'─'*14} {'─'*6} {'─'*9} {'─'*11} {'─'*8}  │")
        lines.append(f"  │  {'TOTAL':<14} {totals['files']:>6} {totals['classes']:>9} {totals['functions']:>11} {totals['size']:>6.0f}KB  │")
        lines.append("  │                                                             │")
        lines.append("  └─────────────────────────────────────────────────────────────┘")
        lines.append("")

        # ── Dependency Map ──
        lines.append("  ┌─ Cross-Module Dependencies ─────────────────────────────────┐")
        lines.append("  │                                                             │")

        for mod_name, deps in self.dependency_map.items():
            if deps:
                dep_str = ", ".join(deps)
                lines.append(f"  │  {mod_name:<14} → {dep_str:<43}│")
            else:
                lines.append(f"  │  {mod_name:<14}   (standalone — no cross-module deps)     │")

        lines.append("  │                                                             │")
        lines.append("  └─────────────────────────────────────────────────────────────┘")
        lines.append("")

        # ── Cross-Module Calls Detail ──
        if self.cross_module_calls:
            lines.append("  ┌─ Cross-Module Import Details ────────────────────────────────┐")
            lines.append("  │                                                              │")
            for call in self.cross_module_calls:
                names_str = ", ".join(call["names"][:3])
                if len(call["names"]) > 3:
                    names_str += f" +{len(call['names'])-3} more"
                line = f"  │  {call['from_module']:<10} → {call['to_module']:<10} : {names_str:<30}│"
                lines.append(line)
            lines.append("  │                                                              │")
            lines.append("  └──────────────────────────────────────────────────────────────┘")
            lines.append("")

        # ── Health Assessment ──
        lines.append("  ┌─ Architecture Health ───────────────────────────────────────┐")
        lines.append("  │                                                             │")

        standalone = [n for n, d in self.dependency_map.items() if not d]
        connected = [n for n, d in self.dependency_map.items() if d]

        if standalone:
            lines.append(f"  │  🟢 Standalone modules: {', '.join(standalone):<37}│")
        if connected:
            lines.append(f"  │  🔗 Connected modules:  {', '.join(connected):<37}│")

        # Check for circular dependencies
        circular = []
        for mod_a, deps_a in self.dependency_map.items():
            for dep in deps_a:
                if mod_a in self.dependency_map.get(dep, []):
                    pair = tuple(sorted([mod_a, dep]))
                    if pair not in circular:
                        circular.append(pair)

        if circular:
            lines.append("  │                                                             │")
            lines.append("  │  ⚠️  Circular dependencies detected:                        │")
            for a, b in circular:
                lines.append(f"  │     {a} ↔ {b:<50}│")
        else:
            lines.append("  │  ✅ No circular dependencies                                │")

        lines.append("  │                                                             │")
        lines.append("  └─────────────────────────────────────────────────────────────┘")
        lines.append("")

        return "\n".join(lines)

    def save_report(self, output_path: str = None):
        """Save the workspace report as JSON."""
        if not output_path:
            output_path = os.path.join(self.root, ".srt1", "workspace_report.json")

        report = {
            "workspace": self.workspace_config.get("workspace", ""),
            "generated_at": datetime.now().isoformat(),
            "modules": self.module_summaries,
            "dependencies": self.dependency_map,
            "cross_module_calls": self.cross_module_calls,
            "summary": {
                "total_modules": len(self.module_summaries),
                "total_files": sum(s["total_files"] for s in self.module_summaries.values()),
                "total_classes": sum(s["classes"] for s in self.module_summaries.values()),
                "total_functions": sum(s["functions"] for s in self.module_summaries.values()),
            }
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"  ✓ Report saved to {os.path.relpath(output_path, self.root)}")

    def run(self):
        """Full workspace connector pipeline."""
        print()
        print("  ╔══════════════════════════════════════════════════════════════╗")
        print("  ║           SRT-1 Workspace Connector (Pro)                   ║")
        print("  ╚══════════════════════════════════════════════════════════════╝")
        print()

        if not self.load_workspace():
            return

        print()
        print("  Scanning modules...")
        self.scan_all_modules()

        print()
        print("  Analyzing cross-module dependencies...")
        self.build_dependency_map()
        print(f"  ✓ Found {len(self.cross_module_calls)} cross-module imports")

        report = self.generate_report()
        print(report)

        self.save_report()
        print()


# ─── CLI ENTRY POINT ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SRT-1 Workspace Connector — Link isolated module sandboxes",
    )
    parser.add_argument(
        "--root", default=".",
        help="Root directory containing .srt1/workspace.json"
    )
    args = parser.parse_args()

    connector = WorkspaceConnector(args.root)
    connector.run()


if __name__ == "__main__":
    main()
