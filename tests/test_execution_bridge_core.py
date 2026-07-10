import json
import tempfile
import unittest
from pathlib import Path

from unittest.mock import Mock, patch

from srt1_platform.assistant_adapters import (
    CustomHTTPAssistantAdapter,
    FileHandoffAssistantAdapter,
    WorkCellExecutionRequest,
)
from srt1_platform.execution_bridge import DispatchMethod, SCIADispatchBridge


class ExecutionBridgeCoreTests(unittest.TestCase):
    def test_dispatch_seed_file_based_records_active_dispatch(self):
        with tempfile.TemporaryDirectory() as repo:
            bridge = SCIADispatchBridge(repo_path=repo)
            bridge.configure(dispatch_methods=[DispatchMethod.FILE_BASED])
            bridge.set_callbacks(get_file_hashes=lambda: [("app.py", "hash1")])

            result = bridge.dispatch_seed("seed_1", "Improve app", blueprint="Do it safely")

            self.assertTrue(result["dispatched"])
            self.assertIn(DispatchMethod.FILE_BASED, result["methods"])
            self.assertIn("seed_1", bridge._active_dispatches)
            self.assertEqual(bridge._file_snapshots["seed_1"], {"app.py": "hash1"})

            pending = Path(repo) / ".srt1" / "pending_seed.md"
            self.assertTrue(pending.exists())
            self.assertIn("Improve app", pending.read_text(encoding="utf-8"))

    def test_handle_completion_preserves_dispatch_info_without_verification_owner(self):
        with tempfile.TemporaryDirectory() as repo:
            bridge = SCIADispatchBridge(repo_path=repo)
            bridge._active_dispatches["seed_1"] = {
                "intent": "Improve app",
                "methods": [DispatchMethod.FILE_BASED],
            }

            bridge._handle_completion(
                seed_id="seed_1",
                method="manual",
                files_modified=["app.py"],
                summary="Done",
            )

            completion_path = Path(repo) / ".srt1" / "completed_seeds" / "seed_1_completed.json"
            completion = json.loads(completion_path.read_text(encoding="utf-8"))

            self.assertEqual(completion["seed_id"], "seed_1")
            self.assertEqual(completion["dispatch_info"]["intent"], "Improve app")
            self.assertNotIn("verification", completion)

    def test_codex_assistant_adapter_writes_bounded_workcell_handoff(self):
        with tempfile.TemporaryDirectory() as repo:
            workcell_package = Path(repo) / ".srt1" / "workcells" / "seed_1"
            workcell_package.mkdir(parents=True)
            bridge = SCIADispatchBridge(repo_path=repo)
            bridge.configure(
                dispatch_methods=[DispatchMethod.ASSISTANT_ADAPTER],
                assistant_adapters=[{"type": "codex"}],
            )

            result = bridge.dispatch_seed(
                "seed_1",
                "Improve app.py only",
                blueprint="Change app.py safely",
                blueprint_meta={
                    "workcell_package_path": str(workcell_package),
                    "allowed_paths": ["app.py"],
                    "restricted_paths": [".git/", "private/"],
                },
            )

            adapter_result = result["methods"][DispatchMethod.ASSISTANT_ADAPTER]
            self.assertTrue(adapter_result["success"])
            codex = adapter_result["adapters"]["codex"]
            self.assertEqual(codex["status"], "dispatched")

            request_path = Path(codex["request_path"])
            instruction_path = Path(codex["instruction_path"])
            self.assertTrue(request_path.exists())
            self.assertTrue(instruction_path.exists())

            payload = json.loads(request_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["seed_id"], "seed_1")
            self.assertEqual(payload["workcell_package_path"], str(workcell_package))
            self.assertEqual(payload["allowed_paths"], ["app.py"])
            self.assertTrue(payload["contract"]["must_stay_inside_allowed_paths"])

            instructions = instruction_path.read_text(encoding="utf-8")
            self.assertIn("SRT-1 Codex WorkCell Handoff", instructions)
            self.assertIn("Improve app.py only", instructions)
            self.assertIn("app.py", instructions)

    def test_unknown_assistant_adapter_fails_closed(self):
        with tempfile.TemporaryDirectory() as repo:
            bridge = SCIADispatchBridge(repo_path=repo)
            bridge.configure(
                dispatch_methods=[DispatchMethod.ASSISTANT_ADAPTER],
                assistant_adapters=[{"type": "mystery_model"}],
            )

            result = bridge.dispatch_seed("seed_1", "Improve app", blueprint_meta={"allowed_paths": ["app.py"]})

            adapter_result = result["methods"][DispatchMethod.ASSISTANT_ADAPTER]
            self.assertFalse(adapter_result["success"])
            self.assertEqual(adapter_result["adapters"]["mystery_model"]["status"], "degraded")


    def test_assistant_adapter_dispatch_without_allowed_paths_fails_closed(self):
        with tempfile.TemporaryDirectory() as repo:
            bridge = SCIADispatchBridge(repo_path=repo)
            bridge.configure(
                dispatch_methods=[DispatchMethod.ASSISTANT_ADAPTER],
                assistant_adapters=[{"type": "codex"}],
            )

            result = bridge.dispatch_seed("seed_no_scope", "Improve app")

        adapter_result = result["methods"][DispatchMethod.ASSISTANT_ADAPTER]
        self.assertFalse(adapter_result["success"])
        self.assertIn("allowed paths", adapter_result["error"])
    def test_file_handoff_does_not_persist_transient_credentials(self):
        with tempfile.TemporaryDirectory() as repo:
            request = WorkCellExecutionRequest(
                seed_id="seed_secure",
                intent="Use assistant safely",
                srt1_dir=str(Path(repo) / ".srt1"),
                transient_credentials={"openai": "sk-test-secret"},
            )

            result = FileHandoffAssistantAdapter().dispatch(request)

            self.assertEqual(result.status, "dispatched")
            payload = Path(result.request_path).read_text(encoding="utf-8")
            instructions = Path(result.instruction_path).read_text(encoding="utf-8")
            self.assertNotIn("sk-test-secret", payload)
            self.assertNotIn("transient_credentials", payload)
            self.assertNotIn("sk-test-secret", instructions)

    def test_custom_http_uses_transient_credential_without_serializing_it(self):
        captured = {}

        class FakeResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"ok": true}'

        def fake_urlopen(request, timeout=0):
            captured["authorization"] = request.get_header("Authorization")
            captured["credential_mode"] = request.get_header("X-srt1-credential-mode")
            captured["credential_provider"] = request.get_header("X-srt1-credential-provider")
            captured["body"] = request.data.decode("utf-8")
            return FakeResponse()

        request = WorkCellExecutionRequest(
            seed_id="seed_http",
            intent="Dispatch through local adapter",
            metadata={"credential_provider": "openai"},
            transient_credentials={"openai": "sk-test-secret"},
        )

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = CustomHTTPAssistantAdapter(
                endpoint="http://127.0.0.1:9999/workcell"
            ).dispatch(request)

        self.assertEqual(result.status, "dispatched")
        self.assertEqual(captured["authorization"], "Bearer sk-test-secret")
        self.assertEqual(captured["credential_mode"], "session")
        self.assertEqual(captured["credential_provider"], "openai")
        self.assertNotIn("sk-test-secret", captured["body"])
        self.assertNotIn("transient_credentials", captured["body"])


if __name__ == "__main__":
    unittest.main()
