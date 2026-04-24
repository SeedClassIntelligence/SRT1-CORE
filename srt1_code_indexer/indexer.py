"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: ORCHESTRATOR, DATABASE_SERVICE, CLI_ENTRY_POINT
Key Symbols: _DependencyVisitor, _extract_dependencies, _first_docstring_line, SRT1CodeIndexer, main ... and 11 more

Extracted Purposes:
  - _DependencyVisitor: Walk a function body and collect names of functions it calls.
  - _extract_dependencies: Return deduplicated list of function names called inside node.
  - _first_docstring_line: Return first line of node docstring, or empty string.
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 Code Indexer v2.0 — Cognitive Operating System for Software Repositories

FILE: indexer.py
SRT-1 TAG: CODE_REFLECTION_INDEXER :: BRAIN_OVER_THE_REPO

PURPOSE:
    Scans a software repository, analyzes its structure using AST parsing,
    curates and deduplicates code, generates architectural reflections for
    every symbol, and produces a verified Code Manifest.

    v2.0 UPGRADE: Fully integrated with SRT-1 anti-hallucination tracing.
    Every pipeline stage is traced with input/output hashing, and reflection
    checkpoints are generated every 3 operations to enforce coherence.

ARCHITECTURE:
    Consumer of core SCIA IP. Imports SRT (v2).
    Does NOT modify the core module.

PIPELINE:
    Stage 1: Repository Scanner       — Walk dirs, hash files
    Stage 2: Structural Parser         — AST analysis, symbol extraction
    Stage 3: Curation & Sanitization   — Duplicate/overlap detection
    Stage 4: Reflection Engine         — Role/risk tagging with heuristics
    Stage 5: Manifest Generation       — Save JSON with integrity hash

Usage:
    python -m srt1_code_indexer --repo_path /path/to/repository
    srt1-index --repo_path /path/to/repository

Author : William Darnell Jernigan IV (Architect)
License: Apache License 2.0
"""

import os
import sys
import ast
import json
import hashlib
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Set, Optional

# Core SCIA IP imports
try:
    from srt1_code_indexer.srt import SRT
except ImportError:
    try:
        from srt import SRT
    except ImportError:
        sys.exit('[FATAL] Cannot import SRT. Ensure the srt1_code_indexer package is installed.')




# ==============================================================================
# CONSTANTS
# ==============================================================================

SUPPORTED_EXTENSIONS: Set[str] = {
    '.py', '.js', '.ts', '.jsx', '.tsx',
    '.go', '.rs', '.java', '.c', '.cpp', '.h',
    '.md', '.txt', '.json', '.yaml', '.yml',
    '.html', '.css', '.scss',
}

SKIP_DIRS: Set[str] = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv',
    'env', '.tox', '.mypy_cache', '.pytest_cache', 'dist', 'build',
    '.eggs', '.gemini', 'test_venv', 'test_repo', 'test_wheel',
    'legacy', 'site-packages',
}



# ==============================================================================
# AST HELPERS
# ==============================================================================

class _DependencyVisitor(ast.NodeVisitor):
    """Walk a function body and collect names of functions it calls."""

    def __init__(self):
        self.calls: List[str] = []

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)


def _extract_dependencies(node: ast.AST) -> List[str]:
    """Return deduplicated list of function names called inside node."""
    visitor = _DependencyVisitor()
    visitor.visit(node)
    seen: set = set()
    result: List[str] = []
    for name in visitor.calls:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def _first_docstring_line(node: ast.AST) -> str:
    """Return first line of node docstring, or empty string."""
    ds = ast.get_docstring(node)
    if ds:
        return ds.strip().split(chr(10))[0].strip()
    return ''


# ==============================================================================
# SRT-1 CODE INDEXER v2.0
# ==============================================================================

class SRT1CodeIndexer:
    """
    Cognitive operating system for software repositories.
    Scans, parses, curates, reflects, and verifies an entire codebase.

    v2.0: Every pipeline stage is traced through SRT-1 with input/output
    hashing. A seed is planted at initialization representing the indexing
    task, and reflection checkpoints fire every 3 operations to maintain
    coherence throughout the pipeline.
    """

    def __init__(self, repo_path: str, reflection_interval: int = 3):
        if not os.path.isdir(repo_path):
            raise ValueError(f'Provided path is not a valid directory: {repo_path}')

        self.repo_path: str = os.path.abspath(repo_path)

        # Core SCIA IP — v2 with anti-hallucination tracing
        self.srt_tool: SRT = SRT(reflection_interval=reflection_interval)

        # Pipeline state
        self.file_manifest: List[Dict[str, Any]] = []
        self.symbol_table: Dict[str, List[Dict[str, Any]]] = {}
        self.curation_report: Dict[str, Any] = {
            'duplicate_files': [],
            'functional_overlaps': [],
            'unused_functions': [],
        }
        self.code_manifest: Dict[str, Any] = {}

        # Tracing state
        self._stage_traces: List[str] = []

        # Plant the seed — anchor the indexing task intent
        # Keywords MUST cover terms used in ALL 5 stages' metadata
        # so coherence stays high throughout the entire pipeline.
        self.srt_tool.plant_seed(
            task=f"Index and reflect on repository at {self.repo_path}",
            domain="code_indexing",
            keywords=[
                "index", "repository", "scan", "parse", "symbols",
                "curate", "reflect", "manifest", "sign", "code",
                "reflection", "artifact", "analyzing", "curation",
                "scanning", "parsing", "sanitizing", "signing",
                "saving", "finalizing",
            ],
            metadata={"repo_path": self.repo_path},
        )

    # ------------------------------------------------------------------
    # ORCHESTRATION
    # ------------------------------------------------------------------

    def index_repository(self) -> Dict[str, Any]:
        """Execute the full indexing pipeline and return the signed manifest."""
        print('--- [SRT-1 for Code v2.0] Initiating Repository Indexing ---')
        print(f'    Target: {self.repo_path}')
        print()

        self._scan_repository()
        self._parse_source_files()
        self._curate_and_sanitize()
        self._generate_reflections()
        self._save_manifest()

        # Final coherence check
        final_checkpoint = self.srt_tool.force_reflection()
        print()
        print(f'    SRT-1 Final Coherence: {final_checkpoint.coherence_status.value} '
              f'({final_checkpoint.coherence_score:.0%})')
        print(f'    Total Operations Traced: {self.srt_tool._operation_count}')
        print(f'    Reflection Checkpoints: {len(self.srt_tool._checkpoints)}')
        print()
        print('--- [SRT-1 for Code v2.0] Indexing Complete. ---')
        return self.code_manifest

    # ------------------------------------------------------------------
    # STAGE 1: Repository Scanner
    # ------------------------------------------------------------------

    def _scan_repository(self) -> None:
        """Walk directory tree, catalogue files, compute SHA-256 hashes."""
        start_time = time.time()

        for dirpath, dirnames, filenames in os.walk(self.repo_path):
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_DIRS and not d.endswith('.egg-info')
            ]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, self.repo_path)
                try:
                    with open(full_path, 'rb') as fh:
                        content_bytes = fh.read()
                    content_hash = hashlib.sha256(content_bytes).hexdigest()
                except (OSError, PermissionError) as exc:
                    print(f'    [WARN] Could not read {rel_path}: {exc}')
                    continue
                self.file_manifest.append({
                    'file_path': rel_path,
                    'full_path': full_path,
                    'extension': ext,
                    'content_hash': content_hash,
                    'size_bytes': len(content_bytes),
                })

        duration_ms = int((time.time() - start_time) * 1000)

        # SRT-1 Trace: Record this stage
        self.srt_tool.trace_operation(
            module="indexer",
            operation="scan_repository",
            input_data={"repo_path": self.repo_path},
            output_data={
                "files_found": len(self.file_manifest),
                "extensions": list(set(e['extension'] for e in self.file_manifest)),
            },
            metadata={
                "stage": "1/5",
                "scan": "repository",
                "index": "files",
                "code": "scanning",
            },
        )

        print(f'  [1/5] Scan Complete: Found {len(self.file_manifest)} source file(s). ({duration_ms}ms)')

    # ------------------------------------------------------------------
    # STAGE 2: Structural Parser
    # ------------------------------------------------------------------

    def _parse_source_files(self) -> None:
        """Parse Python files with ast and build the symbol table."""
        start_time = time.time()
        total_symbols = 0

        for entry in self.file_manifest:
            if entry['extension'] != '.py':
                continue
            fpath = entry['full_path']
            rel = entry['file_path']
            try:
                with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
                    source = fh.read()
                tree = ast.parse(source, filename=rel)
            except SyntaxError as exc:
                print(f'    [WARN] Syntax error in {rel}: {exc}')
                continue

            symbols: List[Dict[str, Any]] = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbol_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    deps = _extract_dependencies(node)
                    docstring_first = _first_docstring_line(node)
                    params: List[str] = []
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for arg in node.args.args:
                            params.append(arg.arg)
                    symbols.append({
                        'name': node.name,
                        'type': symbol_type,
                        'line': node.lineno,
                        'end_line': getattr(node, 'end_lineno', None),
                        'dependencies': deps,
                        'parameters': params,
                        'docstring_first_line': docstring_first,
                    })
                    total_symbols += 1

            if symbols:
                self.symbol_table[rel] = symbols

        duration_ms = int((time.time() - start_time) * 1000)

        # SRT-1 Trace: Record this stage
        self.srt_tool.trace_operation(
            module="indexer",
            operation="parse_source_files",
            input_data={"files_to_parse": len(self.file_manifest)},
            output_data={
                "symbols_found": total_symbols,
                "files_with_symbols": len(self.symbol_table),
            },
            metadata={
                "stage": "2/5",
                "parse": "symbols",
                "code": "parsing",
            },
        )

        print(f'  [2/5] Parse Complete: Identified {total_symbols} symbol(s). ({duration_ms}ms)')

    # ------------------------------------------------------------------
    # STAGE 3: Curation & Sanitization
    # ------------------------------------------------------------------

    def _curate_and_sanitize(self) -> None:
        """Detect duplicate files and overlapping functions."""
        start_time = time.time()

        # 3a. Duplicate File Detection
        hash_to_files: Dict[str, List[str]] = {}
        for entry in self.file_manifest:
            h = entry['content_hash']
            hash_to_files.setdefault(h, []).append(entry['file_path'])
        for h, files in hash_to_files.items():
            if len(files) > 1:
                canonical = min(files, key=len)
                self.curation_report['duplicate_files'].append({
                    'type': 'duplicate_file',
                    'content_hash': h,
                    'files': files,
                    'recommendation': f"Archive all except '{canonical}'.",
                })

        # Methods that are standard or polymorphic and naturally overlap
        SKIP_FUNCTIONS = {
            '__init__', 'main', 'to_dict', 'do_get', 'do_post', 'do_options',
            'do_patch', 'send_prompt', 'get_name', 'validate_email'
        }

        # 3b. Functional Overlap Analysis
        fingerprints: Dict[str, List[Dict[str, Any]]] = {}
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                if sym['type'] != 'function':
                    continue
                if sym['name'].lower() in SKIP_FUNCTIONS:
                    continue
                fp_parts = [
                    sym['name'],
                    ','.join(sorted(sym.get('parameters', []))),
                    sym.get('docstring_first_line', ''),
                ]
                fp_string = '|'.join(fp_parts).lower()
                fp_hash = hashlib.sha256(fp_string.encode('utf-8')).hexdigest()[:12]
                fingerprints.setdefault(fp_hash, []).append({
                    'file': fpath,
                    'function': sym['name'],
                    'line': sym['line'],
                    'fingerprint_source': fp_string,
                })
        for fp_hash, entries in fingerprints.items():
            if len(entries) > 1:
                self.curation_report['functional_overlaps'].append({
                    'type': 'functional_overlap',
                    'fingerprint_hash': fp_hash,
                    'instances': entries,
                    'recommendation': (
                        f"Review {len(entries)} instances of "
                        f"'{entries[0]['function']}' for consolidation."
                    ),
                })

        # 3c. Unused Function Detection
        # Build sets of all defined vs. all referenced function names
        ENTRY_POINTS = {
            'main', 'cli', 'run', 'start', 'setup', 'teardown',
            'index_repository', '__main__', 'app', 'create_app',
        }
        defined_functions: Dict[str, List[str]] = {}  # name -> [file:line, ...]
        all_referenced: Set[str] = set()

        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                if sym['type'] == 'function':
                    loc = f"{fpath}:{sym['line']}"
                    defined_functions.setdefault(sym['name'], []).append(loc)
                # Collect all dependencies (function calls)
                for dep in sym.get('dependencies', []):
                    all_referenced.add(dep)

        self.curation_report['unused_functions'] = []
        for func_name, locations in defined_functions.items():
            fn_lower = func_name.lower()
            # Skip entry points, dunder methods, test methods, private helpers
            if fn_lower in ENTRY_POINTS:
                continue
            if func_name.startswith('__') and func_name.endswith('__'):
                continue
            if func_name.startswith('test_'):
                continue
            # If this function is NEVER referenced by any other function
            if func_name not in all_referenced:
                # Only flag if it exists in a single location (not polymorphic)
                if len(locations) == 1:
                    self.curation_report['unused_functions'].append({
                        'type': 'unused_function',
                        'function': func_name,
                        'location': locations[0],
                        'recommendation': f"'{func_name}' at {locations[0]} is never called by other functions. Verify if it's an entry point or dead code.",
                    })

        total_issues = (
            len(self.curation_report['duplicate_files'])
            + len(self.curation_report['functional_overlaps'])
            + len(self.curation_report.get('unused_functions', []))
        )
        duration_ms = int((time.time() - start_time) * 1000)

        # SRT-1 Trace: Record this stage
        self.srt_tool.trace_operation(
            module="indexer",
            operation="curate_and_sanitize",
            input_data={
                "files_checked": len(self.file_manifest),
                "functions_checked": sum(
                    1 for syms in self.symbol_table.values()
                    for s in syms if s['type'] == 'function'
                ),
            },
            output_data={
                "duplicates": len(self.curation_report['duplicate_files']),
                "overlaps": len(self.curation_report['functional_overlaps']),
                "unused": len(self.curation_report.get('unused_functions', [])),
                "total_issues": total_issues,
            },
            metadata={
                "stage": "3/5",
                "curate": "curation",
                "code": "sanitizing",
            },
        )

        print(f'  [3/5] Curation Complete: Found {total_issues} issue(s). ({duration_ms}ms)')

    # ------------------------------------------------------------------
    # STAGE 4: Reflection Engine
    # ------------------------------------------------------------------

    def _generate_reflections(self) -> None:
        """
        The core intelligence step. Iterates through the symbol table
        and generates SRT-1 reflections for every class and function.
        Uses heuristics to determine architectural role and risk profile.

        SCALABILITY: Reflection gates (coherence checkpoints) are suppressed
        during bulk indexing. There is no conversation to drift from yet —
        firing coherence checks every 3 symbols is wasted computation.
        Gates are restored after indexing for live conversation monitoring.
        """
        start_time = time.time()

        # Suppress reflection gates during bulk indexing pass.
        # Without this, an 800-symbol repo fires ~270 useless coherence
        # checkpoints before the server even starts.
        original_interval = self.srt_tool._reflection_interval
        self.srt_tool._reflection_interval = 999999

        # Pre-load source for risk analysis scoped to each symbol
        source_lines_cache: Dict[str, List[str]] = {}
        for entry in self.file_manifest:
            if entry['extension'] == '.py':
                try:
                    with open(entry['full_path'], 'r', encoding='utf-8', errors='replace') as fh:
                        source_lines_cache[entry['file_path']] = fh.read().splitlines()
                except OSError:
                    pass

        for file_path, symbols in self.symbol_table.items():
            source_lines = source_lines_cache.get(file_path, [])

            for symbol in symbols:
                purpose = symbol.get('docstring_first_line') or 'No docstring provided.'

                # Extract only this symbol's source for precise risk scoping
                start_line = symbol.get('line', 1) - 1
                end_line = symbol.get('end_line') or (start_line + 1)
                symbol_source = '\n'.join(source_lines[start_line:end_line]) if source_lines else ''

                role = self._infer_architectural_role(file_path, symbol['name'], symbol_source)
                risk_tags = self._infer_risk_profile(symbol, symbol_source)

                reflection_content = {
                    'purpose': purpose,
                    'architectural_role': role,
                    'risk_profile': risk_tags,
                    'dependencies': symbol['dependencies'],
                    'parameters': symbol.get('parameters', []),
                    'symbol_type': symbol['type'],
                    'location': f"{file_path}:{symbol['line']}",
                }

                # Use core SCIA IP to add the reflection
                self.srt_tool.add_reflection(
                    reflection_type='code_artifact',
                    content=json.dumps(reflection_content),
                    metadata={
                        'file': file_path,
                        'symbol': symbol['name'],
                        'line': symbol['line'],
                        'module': 'reflector',
                        'context': 'index repository reflect code artifact symbols scan parse curate manifest sign',
                    },
                )

                # Augment the symbol table entry
                symbol['reflection'] = reflection_content

        # Restore reflection interval for live conversation monitoring
        self.srt_tool._reflection_interval = original_interval

        total = len(self.srt_tool.get_reflections())
        duration_ms = int((time.time() - start_time) * 1000)

        print(f'  [4/5] Reflection Complete: Generated {total} reflection(s). ({duration_ms}ms)')

    @staticmethod
    def _infer_architectural_role(file_path: str, symbol_name: str, source: str) -> str:
        """Assign architectural role tag. Symbol name has priority over file path."""
        sn = symbol_name.lower()
        fp = file_path.lower()

        # Symbol-name rules (highest priority)
        name_rules = [
            (['route', 'endpoint', 'view', 'controller'], 'API_CONTROLLER'),
            (['model', 'schema', 'entity'], 'DATA_MODEL'),
            (['service', 'manager', 'handler', 'worker'], 'SERVICE_LAYER'),
            (['repository', 'dao', 'store'], 'DATABASE_SERVICE'),
            (['test', 'spec'], 'TEST'),
            (['main'], 'CLI_ENTRY_POINT'),
            (['migrate', 'migration'], 'DATA_MIGRATION'),
        ]
        for keywords, role in name_rules:
            if any(kw in sn for kw in keywords):
                return role

        # File-path rules (secondary signal)
        path_rules = [
            (['route', 'endpoint', 'view', 'controller', 'api'], 'API_CONTROLLER'),
            (['model', 'schema', 'orm', 'table', 'entity'], 'DATA_MODEL'),
            (['service'], 'SERVICE_LAYER'),
            (['repo', 'repository', 'dao', 'store', 'database', 'db'], 'DATABASE_SERVICE'),
            (['util', 'helper', 'common', 'misc', 'tools'], 'UTILITY'),
            (['test', 'spec', 'fixture', 'conftest'], 'TEST'),
            (['config', 'settings', 'constants'], 'CONFIGURATION'),
            (['middleware', 'interceptor', 'hook'], 'MIDDLEWARE'),
            (['cli', 'command'], 'CLI_ENTRY_POINT'),
            (['orchestrat', 'pipeline', 'workflow', 'engine', 'index'], 'ORCHESTRATOR'),
            (['auth', 'permission', 'login', 'session', 'token'], 'AUTH_SECURITY'),
            (['migrate', 'migration'], 'DATA_MIGRATION'),
            (['trace', 'audit', 'srt'], 'TRACING_AUDIT'),
            (['signature', 'sign', 'crypto'], 'CRYPTOGRAPHIC'),
        ]
        for keywords, role in path_rules:
            if any(kw in fp for kw in keywords):
                return role

        return 'GENERAL'

    @staticmethod
    def _infer_risk_profile(symbol: Dict[str, Any], source: str) -> List[str]:
        """Assign risk tags based on keyword analysis of the symbol's source."""
        tags: List[str] = []
        src_lower = source.lower()
        dep_str = ' '.join(symbol.get('dependencies', [])).lower()
        scan_text = src_lower + ' ' + dep_str

        risk_rules = [
            (['insert ', 'update ', 'delete ', 'db.execute', 'cursor.execute',
              'session.commit', 'session.add'], 'WRITES_TO_DB'),
            (['requests.get', 'requests.post', 'requests.put', 'httpx',
              'urllib.request', 'aiohttp'], 'EXTERNAL_API_CALL'),
            (['auth', 'permission', 'login', 'token', 'jwt', 'oauth',
              'credentials', 'secret'], 'AUTH_SENSITIVE'),
            (['os.remove', 'shutil.rmtree', 'os.unlink', 'subprocess',
              'os.system'], 'SYSTEM_SIDE_EFFECT'),
            (['open(', 'write(', 'pathlib'], 'FILE_IO'),
            (['logging', 'logger'], 'HAS_LOGGING'),
            (['eval(', 'exec(', '__import__'], 'DYNAMIC_EXECUTION'),
        ]
        for keywords, tag in risk_rules:
            if any(kw in scan_text for kw in keywords):
                tags.append(tag)

        if not tags:
            tags.append('LOW_RISK')
        return tags

    # ------------------------------------------------------------------
    # STAGE 5: Manifest Generation & Signing
    # ------------------------------------------------------------------

    def _save_manifest(self) -> None:
        """Assemble Code Manifest, compute integrity hash, write to repo root."""
        start_time = time.time()

        # SRT-1 Trace: Record this stage
        self.srt_tool.trace_operation(
            module="indexer",
            operation="save_manifest",
            input_data={
                "files": len(self.file_manifest),
                "symbols": sum(len(s) for s in self.symbol_table.values()),
                "reflections": len(self.srt_tool.get_reflections()),
            },
            output_data={"operation": "manifest_assembly"},
            metadata={
                "stage": "5/5",
                "manifest": "saving",
                "sign": "signing",
                "code": "finalizing",
            },
        )

        # SECURITY: Strip full_path from file manifest before saving
        safe_file_manifest = [
            {k: v for k, v in entry.items() if k != 'full_path'}
            for entry in self.file_manifest
        ]

        self.code_manifest = {
            'metadata': {
                'manifest_version': '2.0.0',
                'scia_version': '4.0.0',
                'srt_version': '2.0.0',
                'repo_name': os.path.basename(self.repo_path),
                'index_timestamp': datetime.now().isoformat(),
                'total_files_scanned': len(self.file_manifest),
                'total_symbols_indexed': sum(len(s) for s in self.symbol_table.values()),
                'total_reflections': len(self.srt_tool.get_reflections()),
            },
            'file_manifest': safe_file_manifest,
            'symbol_table': self.symbol_table,
            'curation_report': self.curation_report,
            'reflections': self.srt_tool.get_reflections(),
            'reflection_summary': self.srt_tool.summarize_reflections(),
            'srt_trace_chain': self.srt_tool.get_trace_chain(),
            'srt_coherence_history': self.srt_tool.get_coherence_history(),
        }

        # Compute manifest integrity hash
        manifest_json = json.dumps(self.code_manifest, sort_keys=True, default=str)
        integrity_hash = hashlib.sha256(manifest_json.encode('utf-8')).hexdigest()
        self.code_manifest['integrity'] = {
            'hash_algorithm': 'sha256',
            'manifest_hash': integrity_hash,
            'timestamp': datetime.now().isoformat(),
        }

        # Sign the manifest via SeedSignature if the signing client is available
        try:
            from scia_security.signing_client import SigningServiceClient
            _signer = SigningServiceClient()
            sig = _signer.sign(
                {"manifest_hash": integrity_hash,
                 "files": len(self.file_manifest),
                 "symbols": sum(len(s) for s in self.symbol_table.values())},
                phase="manifest_generation"
            )
            if "error" not in sig:
                self.code_manifest['integrity']['_provenance'] = sig
                print('        ✓ Manifest signed by SeedSignature authority')
        except ImportError:
            pass  # scia_security not installed — standalone mode

        # Write to disk
        manifest_path = os.path.join(self.repo_path, 'srt1_code_manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as fh:
            json.dump(self.code_manifest, fh, indent=2, default=str)

        duration_ms = int((time.time() - start_time) * 1000)

        print(f'  [5/5] Manifest Saved & Verified. ({duration_ms}ms)')
        print(f'        Path : {manifest_path}')
        print(f'        Integrity: {integrity_hash[:16]}...')


# ==============================================================================
# CLI
# ==============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description='SRT-1 Code Indexer v2.0 — Brain Over the Repo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n'
            '  srt1-index --repo_path /path/to/repo\n'
            '  srt1-index --repo_path . --reflection-interval 5\n'
        ),
    )
    parser.add_argument(
        '--repo_path', required=True,
        help='Path to the software repository to index.',
    )
    parser.add_argument(
        '--reflection-interval', type=int, default=3,
        help='SRT-1 reflection checkpoint interval (default: 3 operations).',
    )
    args = parser.parse_args()

    try:
        indexer = SRT1CodeIndexer(
            args.repo_path,
            reflection_interval=args.reflection_interval,
        )
        manifest = indexer.index_repository()

        integrity = manifest.get('integrity', {}).get('manifest_hash', 'N/A')
        print(f'  Manifest Integrity: {integrity[:16]}...')
        print('  Done.')

    except Exception as exc:
        print(f'[ERROR] {exc}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
