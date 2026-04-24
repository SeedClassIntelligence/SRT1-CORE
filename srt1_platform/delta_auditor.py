"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: DATA_MODEL
Key Symbols: SCIADeltaAuditor, compute_delta

Extracted Purposes:
  - SCIADeltaAuditor: Enterprise Delta Auditor for computing architectural drift.
  - compute_delta: Compare two states of the srt1_code_manifest.json to detect architecture drift.
"""
import json
import os
import hashlib
from typing import Dict, Any, List

class SCIADeltaAuditor:
    """Enterprise Delta Auditor for computing architectural drift."""

    @staticmethod
    def compute_delta(repo_path: str, state_t1: Dict[str, Any], state_t2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two states of the srt1_code_manifest.json to detect architecture drift.
        Returns the delta signature.
        """
        report = {
            "drift_score": 0,
            "protected_symbols": [],
            "recovery_path": "",
            "file_state_velocity": {
                "added": [],
                "removed": [],
                "modified": []
            }
        }

        # Handle purely empty states
        t1_files = {f["file_path"]: f for f in state_t1.get("file_manifest", [])}
        t2_files = {f["file_path"]: f for f in state_t2.get("file_manifest", [])}

        # 1. File Velocity
        for path in t1_files:
            if path not in t2_files:
                report["file_state_velocity"]["removed"].append(path)
                report["drift_score"] += 2
            elif t1_files[path].get("content_hash") != t2_files[path].get("content_hash"):
                report["file_state_velocity"]["modified"].append(path)
                report["drift_score"] += 1

        for path in t2_files:
            if path not in t1_files:
                report["file_state_velocity"]["added"].append(path)
                report["drift_score"] += 2

        # 2. Protected Symbols
        # Reflections in the manifest are a list of dicts from srt_tool.get_reflections()
        # Each entry has: {'type': ..., 'content': ..., 'metadata': {'file': ..., 'symbol': ..., ...}}
        # We need to extract symbols with AUTH_SENSITIVE or SECURITY risk profiles.
        t1_symbols = {}
        t1_reflections = state_t1.get("reflections", [])
        if isinstance(t1_reflections, list):
            for ref in t1_reflections:
                meta = ref.get("metadata", {})
                content_str = ref.get("content", "{}")
                try:
                    content = json.loads(content_str) if isinstance(content_str, str) else content_str
                except (json.JSONDecodeError, TypeError):
                    content = {}
                risk = content.get("risk_profile", [])
                fp = meta.get("file", "")
                symbol = meta.get("symbol", "")
                if fp and symbol and any(r in risk for r in ["SECURITY", "AUTH_SENSITIVE"]):
                    t1_symbols[fp + ":" + symbol] = {
                        "line": meta.get("line"),
                        "risk_profile": risk,
                    }
        elif isinstance(t1_reflections, dict):
            # Legacy dict-of-dicts format (backwards compat)
            for fp, sym_list in t1_reflections.items():
                if isinstance(sym_list, dict):
                    for symbol, details in sym_list.items():
                        if any(r in details.get("risk_profile", []) for r in ["SECURITY", "AUTH_SENSITIVE"]):
                            t1_symbols[fp + ":" + symbol] = details

        has_critical = False
        has_high = False

        # Build a lookup of T2 symbols for comparison
        t2_symbol_lookup = {}
        t2_reflections = state_t2.get("reflections", [])
        if isinstance(t2_reflections, list):
            for ref in t2_reflections:
                meta = ref.get("metadata", {})
                fp = meta.get("file", "")
                symbol = meta.get("symbol", "")
                if fp and symbol:
                    t2_symbol_lookup[fp + ":" + symbol] = {"line": meta.get("line")}
        elif isinstance(t2_reflections, dict):
            for fp, sym_list in t2_reflections.items():
                if isinstance(sym_list, dict):
                    for symbol, details in sym_list.items():
                        t2_symbol_lookup[fp + ":" + symbol] = details

        for sym_id, details in t1_symbols.items():
            fp, symbol = sym_id.split(":", 1)
            
            if sym_id not in t2_symbol_lookup:
                report["protected_symbols"].append({
                    "symbol": symbol,
                    "file": fp,
                    "violation": "REMOVED_OR_RENAMED",
                    "who_changed": "unknown",
                    "severity": "CRITICAL"
                })
                has_critical = True
                report["drift_score"] += 40
            elif t2_symbol_lookup[sym_id].get("line") != details.get("line") and fp in report["file_state_velocity"]["modified"]:
                report["protected_symbols"].append({
                    "symbol": symbol,
                    "file": fp,
                    "violation": "MODIFIED_UNAUTHORIZED",
                    "who_changed": "unknown",
                    "severity": "HIGH"
                })
                has_high = True
                report["drift_score"] += 20

        # Apply Governance Floors
        if has_critical and report["drift_score"] < 60:
            report["drift_score"] = 60
        elif has_high and report["drift_score"] < 40:
            report["drift_score"] = 40

        # 3. Recovery Path
        num_mod = len(report["file_state_velocity"]["modified"])
        num_rem = len(report["file_state_velocity"]["removed"])
        if report["drift_score"] > 0 and os.path.exists(os.path.join(repo_path, ".git")):
            files_to_restore = report["file_state_velocity"]["modified"] + report["file_state_velocity"]["removed"]
            if files_to_restore:
                file_str = " ".join([f'"{f}"' for f in files_to_restore])
                report["recovery_path"] = f"git checkout HEAD -- {file_str}"
            else:
                report["recovery_path"] = "git status"

        # Cap drift score
        report["drift_score"] = min(report["drift_score"], 100)
        return report
