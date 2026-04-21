"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: ORCHESTRATOR, CLI_ENTRY_POINT
Key Symbols: AssistantAdapter, EchoAdapter, FileOutputAdapter, PlanValidator, SCIAExecutionEngine ... and 20 more

Extracted Purposes:
  - AssistantAdapter: Abstract base class for AI code assistant adapters.
  - EchoAdapter: Test adapter that echoes the prompt back. Used for validation testing.
  - FileOutputAdapter: Adapter that writes the super-prompt to a file for manual use with any AI.
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 Execution Engine (Phase 3) - AI-Governed Code Execution

FILE: srt1_execution_engine.py
SRT-1 TAG: EXECUTION_ENGINE :: GOVERNED_ASSISTANT

Purpose:
    Consumes a Context Bundle (Phase 2 output), validates it,
    dispatches it to an AI code assistant, validates the response
    against architectural constraints, and signs the result.

Architecture:
    Phase 1 (Indexer)   -->  srt1_code_manifest.json
    Phase 2 (Bundler)   -->  srt1_context_bundle.json
    Phase 3 (Executor)  -->  validates + dispatches + governs

Author : William Darnell Jernigan IV (Architect)
License: Apache License 2.0
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod

try:
    from srt1_code_indexer.srt import SRT
except ImportError:
    try:
        from srt import SRT
    except ImportError:
        sys.exit("[FATAL] Cannot import SRT.")




# ==============================================================================
# ASSISTANT ADAPTERS (Pluggable - AI-Agnostic)
# ==============================================================================

class AssistantAdapter(ABC):
    """Abstract base class for AI code assistant adapters."""

    @abstractmethod
    def send_prompt(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send the super-prompt to the AI assistant and return its response."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the adapter name."""
        pass


class EchoAdapter(AssistantAdapter):
    """Test adapter that echoes the prompt back. Used for validation testing."""

    def send_prompt(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        symbols = context.get("relevant_symbols", [])
        return {
            "assistant": "echo",
            "response": (
                f"[ECHO] Received prompt of {len(prompt)} chars "
                f"with {len(symbols)} symbols."
            ),
            "plan": {
                "files_to_modify": [s["file"] for s in symbols[:5]],
                "approach": "Echo adapter - no actual code generation.",
                "estimated_changes": 0,
            },
            "code_blocks": [],
            "raw_response": prompt[:500],
        }

    def get_name(self) -> str:
        return "EchoAdapter (Test)"


class FileOutputAdapter(AssistantAdapter):
    """Adapter that writes the super-prompt to a file for manual use with any AI."""

    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir

    def send_prompt(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"srt1_prompt_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(prompt)
        return {
            "assistant": "file_output",
            "response": f"Super-prompt written to {filepath}",
            "plan": {
                "files_to_modify": [],
                "approach": "Manual - prompt saved to file for external assistant use.",
                "estimated_changes": 0,
                "prompt_file": filepath,
            },
            "code_blocks": [],
            "raw_response": "",
        }

    def get_name(self) -> str:
        return "FileOutputAdapter"


# ==============================================================================
# PLAN VALIDATOR
# ==============================================================================

class PlanValidator:
    """Validates an AI assistant plan against the Code Manifest constraints."""

    def __init__(self, manifest: Dict[str, Any]):
        self.manifest = manifest
        self.known_files = set()
        for entry in manifest.get("file_manifest", []):
            self.known_files.add(entry["file_path"])

    def validate_plan(self, plan: Dict[str, Any], bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the proposed plan against architectural constraints."""
        issues = []
        warnings = []
        approved = True

        files_to_modify = plan.get("files_to_modify", [])
        bundle_files = set(bundle.get("source_extracts", {}).keys())

        # Check 1: Are modified files within the bundle scope?
        for f in files_to_modify:
            if f not in bundle_files and f in self.known_files:
                warnings.append(
                    f"File '{f}' is in the repo but was not included in the "
                    f"context bundle. The assistant may lack full context."
                )

        # Check 2: Are modified files actually in the repo?
        for f in files_to_modify:
            if f not in self.known_files and not f.startswith("NEW:"):
                issues.append(
                    f"File '{f}' does not exist in the indexed repository."
                )

        # Check 3: Risk assessment
        arch = bundle.get("architectural_context", {})
        risk_summary = arch.get("risk_summary", {})
        high_risks = [
            r for r in risk_summary
            if r in ("WRITES_TO_DB", "AUTH_SENSITIVE", "SYSTEM_SIDE_EFFECT")
        ]
        if high_risks:
            warnings.append(
                f"High-risk operations in scope: {', '.join(high_risks)}. "
                f"Review changes carefully before applying."
            )

        if issues:
            approved = False

        return {
            "approved": approved,
            "issues": issues,
            "warnings": warnings,
            "files_validated": len(files_to_modify),
            "validation_timestamp": datetime.now().isoformat(),
        }


# ==============================================================================
# EXECUTION ENGINE
# ==============================================================================

class SCIAExecutionEngine:
    """
    Phase 3 of the SCIA pipeline.

    Governs the interaction between the Context Bundle and an AI code assistant.
    Validates inputs, dispatches prompts, validates outputs, signs results.
    """

    def __init__(self, manifest_path: str, adapter: Optional[AssistantAdapter] = None):
        if not os.path.isfile(manifest_path):
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as fh:
            self.manifest = json.load(fh)

        self.manifest_path = os.path.abspath(manifest_path)
        self.adapter = adapter or FileOutputAdapter()
        self.srt_tool = SRT()
        self.validator = PlanValidator(self.manifest)

        print(f"  [Executor] Loaded manifest. Adapter: {self.adapter.get_name()}")

    def execute(self, bundle_path: str) -> Dict[str, Any]:
        """
        Execute the full Phase 3 pipeline.

        Args:
            bundle_path: Path to the srt1_context_bundle.json from Phase 2.

        Returns:
            A verified Execution Result dictionary.
        """
        print()
        print("--- [SRT-1 Execution Engine] Starting Governed Execution ---")

        # Step 1: Load and verify the bundle
        bundle = self._load_bundle(bundle_path)

        # Step 2: Verify bundle integrity
        self._verify_bundle_integrity(bundle)

        # Step 3: Dispatch to AI assistant
        assistant_response = self._dispatch_to_assistant(bundle)

        # Step 4: Validate the plan
        validation = self._validate_response(assistant_response, bundle)

        # Step 5: Assemble execution result
        result = self._assemble_result(bundle, assistant_response, validation)

        # Step 6: Finalize the result
        result = self._finalize_result(result)

        print()
        print("--- [SRT-1 Execution Engine] Execution Complete ---")
        return result

    def _load_bundle(self, bundle_path: str) -> Dict[str, Any]:
        """Load the Context Bundle from Phase 2."""
        if not os.path.isfile(bundle_path):
            raise FileNotFoundError(f"Bundle not found: {bundle_path}")
        with open(bundle_path, "r", encoding="utf-8") as fh:
            bundle = json.load(fh)
        task = bundle.get("bundle_metadata", {}).get("task", "N/A")
        syms = len(bundle.get("relevant_symbols", []))
        files = len(bundle.get("source_extracts", {}))
        print(f"  [1/6] Bundle Loaded: {syms} symbols, {files} files.")
        print(f"         Task: {task[:80]}")
        return bundle

    def _verify_bundle_integrity(self, bundle: Dict[str, Any]) -> None:
        """Verify the Phase 2 bundle integrity."""
        integrity = bundle.get("integrity")
        if integrity:
            bundle_hash = integrity.get("manifest_hash", "N/A")
            print(f"  [2/6] Bundle Integrity: {bundle_hash[:16]}...")
        else:
            print("  [2/6] Bundle Integrity: no hash present")

    def _dispatch_to_assistant(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Send the super-prompt to the AI assistant via the adapter."""
        super_prompt = bundle.get("super_prompt", "")
        adapter_name = self.adapter.get_name()
        token_est = len(super_prompt) // 4
        print(f"  [3/6] Dispatching to {adapter_name}...")
        print(f"         Prompt: {len(super_prompt)} chars (~{token_est} tokens)")

        response = self.adapter.send_prompt(super_prompt, bundle)

        self.srt_tool.add_reflection(
            reflection_type="assistant_dispatch",
            content=json.dumps({
                "adapter": adapter_name,
                "prompt_size": len(super_prompt),
                "response_received": bool(response),
            }),
            metadata={"operation": "DISPATCH"},
        )

        assistant = response.get("assistant", "unknown")
        print(f"  [3/6] Response received from {assistant}.")
        return response

    def _validate_response(
        self, response: Dict[str, Any], bundle: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the assistant response against manifest constraints."""
        plan = response.get("plan", {})
        validation = self.validator.validate_plan(plan, bundle)

        status = "APPROVED" if validation["approved"] else "REJECTED"
        print(f"  [4/6] Plan Validation: {status}")

        for issue in validation.get("issues", []):
            print(f"    [ISSUE] {issue}")
        for warning in validation.get("warnings", []):
            print(f"    [WARN]  {warning}")

        self.srt_tool.add_reflection(
            reflection_type="plan_validation",
            content=json.dumps(validation),
            metadata={"operation": "VALIDATION"},
        )

        return validation

    def _assemble_result(
        self,
        bundle: Dict[str, Any],
        response: Dict[str, Any],
        validation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assemble the final execution result."""
        result = {
            "execution_metadata": {
                "engine_version": "1.0.0",
                "executed_at": datetime.now().isoformat(),
                "manifest_source": self.manifest_path,
                "adapter": self.adapter.get_name(),
                "task": bundle.get("bundle_metadata", {}).get("task", ""),
            },
            "assistant_response": {
                "assistant": response.get("assistant", "unknown"),
                "response_text": response.get("response", ""),
                "plan": response.get("plan", {}),
                "code_blocks": response.get("code_blocks", []),
            },
            "validation": validation,
            "bundle_summary": {
                "symbols_in_scope": len(bundle.get("relevant_symbols", [])),
                "files_in_scope": list(bundle.get("source_extracts", {}).keys()),
                "architectural_roles": list(
                    bundle.get("architectural_context", {})
                    .get("roles_summary", {})
                    .keys()
                ),
            },
            "reflections": self.srt_tool.get_reflections(),
            "reflection_summary": self.srt_tool.summarize_reflections(),
        }

        print("  [5/6] Execution Result assembled.")
        return result

    def _finalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Compute integrity hash for the execution result."""
        result_json = json.dumps(result, sort_keys=True, default=str)
        integrity_hash = hashlib.sha256(result_json.encode('utf-8')).hexdigest()
        result["integrity"] = {
            "hash_algorithm": "sha256",
            "result_hash": integrity_hash,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"  [6/6] Execution Result Verified: {integrity_hash[:16]}...")
        return result

    def save_result(self, result: Dict[str, Any], output_path: str) -> str:
        """Save execution result to JSON."""
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, default=str)
        print(f"  [Executor] Result saved to: {output_path}")
        return output_path

    def print_result_summary(self, result: Dict[str, Any]) -> None:
        """Print a summary of the execution result."""
        meta = result.get("execution_metadata", {})
        val = result.get("validation", {})
        integrity = result.get("integrity", {})

        print()
        print("=" * 60)
        print("  SRT-1 EXECUTION RESULT SUMMARY")
        print("=" * 60)
        print(f"  Task:       {meta.get('task', 'N/A')[:70]}")
        print(f"  Adapter:    {meta.get('adapter', 'N/A')}")
        print(f"  Approved:   {val.get('approved', 'N/A')}")
        print(f"  Issues:     {len(val.get('issues', []))}")
        print(f"  Warnings:   {len(val.get('warnings', []))}")
        print(f"  Integrity:  {integrity.get('result_hash', 'N/A')[:16]}...")
        print("=" * 60)


# ==============================================================================
# CLI
# ==============================================================================

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="SRT-1 Execution Engine (Phase 3) - Governed AI code execution.",
    )
    parser.add_argument(
        "--manifest", required=True, help="Path to srt1_code_manifest.json"
    )
    parser.add_argument(
        "--bundle", required=True, help="Path to srt1_context_bundle.json"
    )
    parser.add_argument(
        "--output", default=None, help="Output path for execution result"
    )
    parser.add_argument(
        "--adapter",
        default="file",
        choices=["echo", "file"],
        help="Assistant adapter to use (default: file)",
    )
    args = parser.parse_args()

    try:
        if args.adapter == "echo":
            adapter = EchoAdapter()
        else:
            adapter = FileOutputAdapter(os.path.dirname(args.manifest))

        engine = SCIAExecutionEngine(args.manifest, adapter=adapter)
        result = engine.execute(args.bundle)
        engine.print_result_summary(result)

        output = args.output or os.path.join(
            os.path.dirname(args.manifest),
            "srt1_execution_result.json",
        )
        engine.save_result(result, output)

    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
