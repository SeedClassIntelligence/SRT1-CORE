"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: TRACING_AUDIT
Key Symbols: EmptinessFinding, CompletenessReport, SeedTreeValidator, is_complete, to_dict ... and 4 more

Extracted Purposes:
  - SeedTreeValidator: Seed-to-Tree Completeness Engine.
  - _is_body_empty: Check if a node body is logically empty (no intelligence).
  - verify_tree: Verify an entire tree (or subset of files) for emptiness and missing intelligence.
"""
import ast
import os
import glob
from dataclasses import dataclass, field
from typing import List, Dict, Set, Any, Optional

@dataclass
class EmptinessFinding:
    file_path: str
    node_name: str
    node_type: str  # function, meth, class
    line_number: int
    reason: str

@dataclass
class CompletenessReport:
    total_files_analyzed: int = 0
    total_functions: int = 0
    empty_harnesses: List[EmptinessFinding] = field(default_factory=list)
    uninvoked_declarations: List[str] = field(default_factory=list)
    
    @property
    def is_complete(self) -> bool:
        return len(self.empty_harnesses) == 0
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_complete": self.is_complete,
            "total_files_analyzed": self.total_files_analyzed,
            "total_functions": self.total_functions,
            "empty_harness_count": len(self.empty_harnesses),
            "empty_harnesses": [
                {
                    "file": f.file_path,
                    "name": f.node_name,
                    "type": f.node_type,
                    "line": f.line_number,
                    "reason": f.reason
                } for f in self.empty_harnesses
            ]
        }

class SeedTreeValidator:
    """
    Seed-to-Tree Completeness Engine.
    Analyzes ASTs to detect "empty harnesses" — functional declarations that
    lack business logic (the "intelligence").
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)

    def _is_body_empty(self, body_nodes: List[ast.AST]) -> tuple[bool, str]:
        """Check if a node body is logically empty (no intelligence)."""
        real_stmts = []
        for node in body_nodes:
            # Ignore docstrings (Expr with string literal)
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    continue
                # Python 3.8+ Ellipsis check
                if isinstance(node.value, ast.Constant) and node.value.value is Ellipsis:
                    continue
            real_stmts.append(node)

        if not real_stmts:
            return True, "Only contains docstring or ellipsis"

        # Check for single statement emptiness signs
        if len(real_stmts) == 1:
            stmt = real_stmts[0]
            if isinstance(stmt, ast.Pass):
                return True, "Contains only 'pass'"
            elif isinstance(stmt, ast.Return):
                if stmt.value is None or (isinstance(stmt.value, ast.Constant) and stmt.value.value is None):
                    return True, "Contains only 'return' or 'return None'"
            elif isinstance(stmt, ast.Raise):
                # Check for NotImplementedError
                if isinstance(stmt.exc, ast.Call) and getattr(stmt.exc.func, 'id', '') == 'NotImplementedError':
                    return True, "Raises NotImplementedError"
                if isinstance(stmt.exc, ast.Name) and stmt.exc.id == 'NotImplementedError':
                    return True, "Raises NotImplementedError"

        return False, ""

    def evaluate_file(self, file_path: str, rel_path: str) -> List[EmptinessFinding]:
        findings = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    is_empty, reason = self._is_body_empty(node.body)
                    if is_empty:
                        findings.append(EmptinessFinding(
                            file_path=rel_path,
                            node_name=node.name,
                            node_type="method" if len(node.args.args) > 0 and node.args.args[0].arg == 'self' else "function",
                            line_number=node.lineno,
                            reason=reason
                        ))
                elif isinstance(node, ast.AsyncFunctionDef):
                    is_empty, reason = self._is_body_empty(node.body)
                    if is_empty:
                        findings.append(EmptinessFinding(
                            file_path=rel_path,
                            node_name=node.name,
                            node_type="async_function",
                            line_number=node.lineno,
                            reason=reason
                        ))
                elif isinstance(node, ast.ClassDef):
                    # For classes, if it only has pass/docstring, it might be an empty wrapper or base exception.
                    # We only flag it if there are no inner definitions at all
                    is_empty, reason = self._is_body_empty(node.body)
                    # We might want to allow empty exception classes
                    if is_empty and not any(isinstance(b, ast.Name) and b.id.endswith("Error") for b in node.bases):
                        findings.append(EmptinessFinding(
                            file_path=rel_path,
                            node_name=node.name,
                            node_type="class",
                            line_number=node.lineno,
                            reason=reason
                        ))
                        
        except Exception:
            # SyntaxError or parsing issue, skip
            pass
        return findings

    def verify_tree(self, files_to_check: Optional[List[str]] = None) -> CompletenessReport:
        """
        Verify an entire tree (or subset of files) for emptiness and missing intelligence.
        """
        report = CompletenessReport()
        
        if files_to_check is None:
            # Walk the repo
            files_to_check = []
            for root, dirs, files in os.walk(self.repo_path):
                # Skip common ignore dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "venv", "env", "node_modules")]
                for f in files:
                    if f.endswith(".py"):
                        files_to_check.append(os.path.join(root, f))
        
        for fp in files_to_check:
            if not os.path.isabs(fp):
                fp = os.path.join(self.repo_path, fp)
            if not os.path.exists(fp):
                continue
                
            rel = os.path.relpath(fp, self.repo_path)
            report.total_files_analyzed += 1
            
            # Rough function count via text
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.lstrip().startswith("def ") or line.lstrip().startswith("async def "):
                            report.total_functions += 1
            except Exception:
                pass
                
            findings = self.evaluate_file(fp, rel)
            report.empty_harnesses.extend(findings)
            
        return report
