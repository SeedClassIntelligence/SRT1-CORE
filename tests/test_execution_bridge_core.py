import json
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
