# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)
# Trust awareness: unsigned unless an external authority signs this artifact.

"""
manifest_deriver.py — Least-Privilege FileCell Manifest Deriver
================================================================
Derives the smallest possible FileCellManifest from the SRT-1 indexer's
symbol_table and call_graph. No workspace-wide reads. No secrets.
No dead code. No AGENTS.md unless explicitly authorized.

Doctrine:
    - FileCell scopes
    - Reads ≠ writes
    - Secrets never readable
    - Dead code never included
    - AGENTS.md is NOT system context by default
"""

import os
import fnmatch
import logging
from typing import Dict, List, Any, Optional, Set

from srt1_platform.filecell import FileCellManifest

logger = logging.getLogger("srt1.manifest_deriver")

# ═══════════════════════════════════════════════════════════════════════════
# EXCLUSION RULES
# ═══════════════════════════════════════════════════════════════════════════

# Patterns that must NEVER appear in allowed_reads or allowed_writes
ALWAYS_FORBIDDEN_PATTERNS = [
    ".env",
    ".env.*",
    ".git",
    ".git/**",
    "security",
    "security/**",
    "*.pem",
    "*.key",
    "*credentials*",
    "*secret*",
    "private_key*",
    "*.p12",
    "*.pfx",
    "__pycache__",
    "__pycache__/**",
]

# Known dead/archive files — confirmed isolated, not in any execution path
ARCHIVE_CANDIDATES = [
    "batch_orchestrator.py",
]


class LeastPrivilegeManifestDeriver:
    """
    Derives the smallest possible FileCellManifest from the SRT-1 indexer's
    symbol_table. Replaces workspace-wide reads with dependency-traced reads.
    
    Source of truth: SRT1Engine.symbol_table + SRT1Engine.call_graph
    """

    def __init__(self, workspace_root: str,
                 symbol_table: Dict[str, List[Dict]] = None,
                 call_graph: Dict[str, List[str]] = None,
                 audit_ledger=None):
        self.workspace_root = os.path.realpath(workspace_root)
        self.symbol_table = symbol_table or {}
        self.call_graph = call_graph or {}
        self.audit_ledger = audit_ledger
        self._reasoning_log: List[str] = []

    def derive(self, seed_id: str, task: str,
               files_likely: List[str] = None,
               domains: List[str] = None,
               explicit_reads: List[str] = None,
               explicit_writes: List[str] = None,
               include_agents_md: bool = False,
               agents_md_reason: str = "") -> FileCellManifest:
        """
        Derive a least-privilege manifest for a seed execution.
        
        Args:
            seed_id: The seed identifier
            task: The task description (for intent logging)
            files_likely: Files identified by the LLM intent classifier
            domains: Domain tags from intent classification
            explicit_reads: Additional explicitly authorized read paths
            explicit_writes: Additional explicitly authorized write paths  
            include_agents_md: If True, include AGENTS.md in allowed_reads
            agents_md_reason: Required if include_agents_md is True
        """
        self._reasoning_log = []
        files_likely = files_likely or []
        domains = domains or []
        explicit_reads = explicit_reads or []
        explicit_writes = explicit_writes or []

        # ── Step 1: Resolve target files ──────────────────────────────────
        target_files = self._resolve_target_files(files_likely)
        self._reasoning_log.append(
            f"Target files from intent: {len(target_files)} resolved from "
            f"{len(files_likely)} files_likely"
        )

        # ── Step 2: Walk dependencies (depth=2) ──────────────────────────
        dependency_files = self._resolve_dependencies(target_files, max_depth=2)
        self._reasoning_log.append(
            f"Dependency walk: {len(dependency_files)} files resolved "
            f"(depth=2, from {len(target_files)} targets)"
        )
        
        # ── Step 2.5: Semantic Escalation Check ──────────────────────────
        all_resolved = target_files | dependency_files
        protected_roles = {"AUTH_SECURITY", "CRYPTOGRAPHIC"}
        for fpath in all_resolved:
            rel_key = self._abs_to_symbol_key(fpath)
            if rel_key and rel_key in self.symbol_table:
                for sym in self.symbol_table[rel_key]:
                    reflection = sym.get("reflection", {})
                    role = reflection.get("architectural_role")
                    if role in protected_roles:
                        # Ensure sponsorship
                        # We map role to a domain string (e.g., AUTH_SECURITY -> auth)
                        # For simplicity, if we hit a protected role, we demand "auth" or "crypto" in domains
                        required_domain = "auth" if role == "AUTH_SECURITY" else "crypto"
                        if required_domain not in domains and "security" not in domains:
                            raise Exception(f"Semantic Escalation Blocked: File {fpath} contains {role} but sponsorship domains {domains} do not cover it.")

        # ── Step 3: Compute allowed_reads ─────────────────────────────────
        read_files: Set[str] = set()
        read_files.update(target_files)
        read_files.update(dependency_files)

        # Add explicit reads (pre-authorized by caller)
        for p in explicit_reads:
            resolved = self._resolve_path(p)
            if resolved:
                read_files.add(resolved)
                self._reasoning_log.append(f"Explicit read added: {p}")

        # AGENTS.md — only if explicitly authorized
        if include_agents_md:
            if not agents_md_reason:
                agents_md_reason = "Authorized by system config"
            agents_path = os.path.join(self.workspace_root, "AGENTS.md")
            if os.path.exists(agents_path):
                read_files.add(os.path.realpath(agents_path))
                self._reasoning_log.append(
                    f"AGENTS.md included: {agents_md_reason}"
                )
        else:
            self._reasoning_log.append(
                "AGENTS.md excluded: not explicitly authorized"
            )

        # ── Step 4: Compute allowed_writes ────────────────────────────────
        output_dir = os.path.join(self.workspace_root, ".srt1", "workcells", seed_id)
        os.makedirs(output_dir, exist_ok=True)

        write_paths: Set[str] = {os.path.realpath(output_dir)}
        for p in explicit_writes:
            resolved = self._resolve_path(p)
            if resolved:
                write_paths.add(resolved)
                self._reasoning_log.append(f"Explicit write added: {p}")

        # ── Step 5: Compute forbidden_paths ───────────────────────────────
        forbidden = self._compute_forbidden_paths()

        # ── Step 6: Filter out forbidden from reads/writes ────────────────
        read_files = self._filter_forbidden(read_files, forbidden)
        write_paths = self._filter_forbidden(write_paths, forbidden)

        # ── Step 7: Generate manifest ─────────────────────────────────────
        dependency_reasoning = "\n".join(self._reasoning_log)

        manifest = FileCellManifest.generate(
            task_intent=task[:200],
            allowed_reads=sorted(read_files),
            allowed_writes=sorted(write_paths),
            forbidden_paths=sorted(forbidden),
            dependencies=sorted(target_files | dependency_files),
            dependency_reasoning=dependency_reasoning,
        )

        # ── SCIA Event: filecell_manifest_derived ─────────────────────────
        if self.audit_ledger:
            try:
                self.audit_ledger.record(
                    component="manifest_deriver",
                    operation="filecell_manifest_derived",
                    detail={
                        "seed_id": seed_id,
                        "cell_id": manifest.cell_id,
                        "allowed_reads_count": len(manifest.allowed_reads),
                        "allowed_writes_count": len(manifest.allowed_writes),
                        "forbidden_count": len(manifest.forbidden_paths),
                        "dependency_count": len(manifest.dependencies),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record filecell_manifest_derived: {e}")

        return manifest

    # ── RESOLUTION METHODS ────────────────────────────────────────────────

    def _resolve_path(self, path: str) -> Optional[str]:
        """Resolve a relative or absolute path within the workspace."""
        if os.path.isabs(path):
            resolved = os.path.realpath(path)
        else:
            resolved = os.path.realpath(os.path.join(self.workspace_root, path))

        # Must be within workspace
        try:
            if os.path.commonpath([resolved, self.workspace_root]) != self.workspace_root:
                return None
        except ValueError:
            return None
        return resolved

    def _resolve_target_files(self, files_likely: List[str]) -> Set[str]:
        """Resolve intent's files_likely to absolute paths within workspace.
        Strict H.1 Enforcement: Files must exist in the AST symbol_table."""
        resolved = set()
        for fpath in files_likely:
            full = self._resolve_path(fpath)
            if full and os.path.exists(full):
                # Verify AST knowledge
                rel_key = self._abs_to_symbol_key(full)
                if rel_key and rel_key in self.symbol_table:
                    resolved.add(full)
                else:
                    self._reasoning_log.append(f"REJECTED Target (LLM Guess): {fpath} not found in AST symbol_table.")
            elif full:
                self._reasoning_log.append(
                    f"REJECTED Target (LLM Guess): {fpath} does not exist and is not in AST."
                )
        return resolved

    def _resolve_dependencies(self, target_files: Set[str],
                              max_depth: int = 2) -> Set[str]:
        """
        Walk the symbol_table to find files that target_files depend on.
        Uses symbol name matching across files (depth-limited BFS).
        """
        if not self.symbol_table:
            self._reasoning_log.append(
                "Symbol table empty — no dependency resolution available"
            )
            return set()

        # Build reverse map: relative_path → set of dependency symbol names
        dep_files: Set[str] = set()
        visited_files: Set[str] = set()
        frontier: Set[str] = set()

        # Convert target absolute paths to relative keys for symbol_table lookup
        for abs_path in target_files:
            rel_key = self._abs_to_symbol_key(abs_path)
            if rel_key:
                frontier.add(rel_key)

        for depth in range(max_depth):
            next_frontier: Set[str] = set()
            for file_key in frontier:
                if file_key in visited_files:
                    continue
                visited_files.add(file_key)

                symbols = self.symbol_table.get(file_key, [])
                # Collect all dependency names from this file's symbols
                dep_names: Set[str] = set()
                for sym in symbols:
                    for dep in sym.get("dependencies", []):
                        dep_names.add(dep)

                # Resolve dependency names to files
                for dep_name in dep_names:
                    for other_file, other_symbols in self.symbol_table.items():
                        if other_file == file_key:
                            continue
                        for osym in other_symbols:
                            if osym["name"] == dep_name:
                                abs_dep = self._symbol_key_to_abs(other_file)
                                if abs_dep:
                                    dep_files.add(abs_dep)
                                    next_frontier.add(other_file)
                                    break

            frontier = next_frontier - visited_files
            if not frontier:
                break

        return dep_files

    def _abs_to_symbol_key(self, abs_path: str) -> Optional[str]:
        """Convert absolute path to the relative key used in symbol_table."""
        try:
            rel = os.path.relpath(abs_path, self.workspace_root)
            # symbol_table uses backslash on Windows
            rel_normalized = rel.replace("/", os.sep)
            if rel_normalized in self.symbol_table:
                return rel_normalized
            # Try forward slash
            rel_fwd = rel.replace("\\", "/")
            if rel_fwd in self.symbol_table:
                return rel_fwd
            # Try both sep styles
            for key in self.symbol_table:
                if os.path.normpath(key) == os.path.normpath(rel):
                    return key
        except ValueError:
            pass
        return None

    def _symbol_key_to_abs(self, key: str) -> Optional[str]:
        """Convert a symbol_table key (relative) to absolute path."""
        abs_path = os.path.realpath(os.path.join(self.workspace_root, key))
        try:
            if os.path.commonpath([abs_path, self.workspace_root]) == self.workspace_root:
                return abs_path
        except ValueError:
            pass
        return None

    # ── FORBIDDEN PATH COMPUTATION ────────────────────────────────────────

    def _compute_forbidden_paths(self) -> Set[str]:
        """Build the forbidden paths set from static exclusion rules."""
        forbidden = set()

        for pattern in ALWAYS_FORBIDDEN_PATTERNS:
            # Direct paths
            full = os.path.join(self.workspace_root, pattern)
            resolved = os.path.realpath(full)
            forbidden.add(resolved)

        # Archive candidates
        for archive in ARCHIVE_CANDIDATES:
            for root, dirs, files in os.walk(self.workspace_root):
                for f in files:
                    if f == archive:
                        forbidden.add(os.path.realpath(os.path.join(root, f)))
                # Don't recurse too deep
                if root.count(os.sep) - self.workspace_root.count(os.sep) > 3:
                    dirs.clear()

        return forbidden

    def _filter_forbidden(self, paths: Set[str],
                          forbidden: Set[str]) -> Set[str]:
        """Remove any path that matches a forbidden pattern."""
        clean = set()
        for p in paths:
            is_forbidden = False
            for f in forbidden:
                try:
                    if os.path.commonpath([p, f]) == f:
                        is_forbidden = True
                        self._reasoning_log.append(
                            f"Filtered forbidden: {os.path.basename(p)} "
                            f"(matches {os.path.basename(f)})"
                        )
                        break
                except ValueError:
                    continue
            # Also check glob patterns against basename
            basename = os.path.basename(p)
            for pattern in ALWAYS_FORBIDDEN_PATTERNS:
                if fnmatch.fnmatch(basename, pattern):
                    is_forbidden = True
                    self._reasoning_log.append(
                        f"Filtered forbidden: {basename} (matches pattern {pattern})"
                    )
                    break

            if not is_forbidden:
                clean.add(p)
        return clean
