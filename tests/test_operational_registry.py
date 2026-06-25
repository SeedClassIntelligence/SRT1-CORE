import tempfile
import unittest
from pathlib import Path

from srt1_platform.operational_registry import OperationalRegistry


class OperationalRegistryTests(unittest.TestCase):
    def test_registers_engine_with_deterministic_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            registry_path = str(Path(temp_dir) / "registry.json")
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            registry = OperationalRegistry(registry_path=registry_path)
            engine_id = registry.generate_engine_id(str(workspace), 7483)

            entry = registry.register_engine(
                engine_id=engine_id,
                port=7483,
                workspace_path=str(workspace),
                manifest_hash="manifest_123",
            )

            self.assertEqual(entry["status"], "RUNNING")
            self.assertEqual(entry["manifest_hash"], "manifest_123")
            self.assertEqual(registry.get_all_engines()["engines"][engine_id]["port"], 7483)

    def test_heartbeat_updates_manifest_hash_and_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            registry = OperationalRegistry(registry_path=str(Path(temp_dir) / "registry.json"))
            engine_id = registry.generate_engine_id(str(workspace), 7483)
            registry.register_engine(engine_id, 7483, str(workspace), manifest_hash="old")

            updated = registry.heartbeat(engine_id, manifest_hash="new", status="DEGRADED")

            self.assertTrue(updated)
            entry = registry.get_all_engines()["engines"][engine_id]
            self.assertEqual(entry["manifest_hash"], "new")
            self.assertEqual(entry["status"], "DEGRADED")

    def test_deregister_marks_engine_offline_without_deleting_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            registry = OperationalRegistry(registry_path=str(Path(temp_dir) / "registry.json"))
            engine_id = registry.generate_engine_id(str(workspace), 7483)
            registry.register_engine(engine_id, 7483, str(workspace))

            self.assertTrue(registry.deregister_engine(engine_id))

            data = registry.get_all_engines()
            self.assertIn(engine_id, data["engines"])
            self.assertEqual(data["engines"][engine_id]["status"], "OFFLINE")


if __name__ == "__main__":
    unittest.main()
