import tempfile
import unittest
from pathlib import Path

from srt1_code_indexer import engine as engine_module
from srt1_platform.repository_activation import RepositoryActivationRegistry
from srt1_platform.workcell import WorkCellRegistry


class RepositoryActivationTests(unittest.TestCase):
    def test_registry_registers_active_repository_with_manifest_counts(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = RepositoryActivationRegistry(
                state_dir=str(Path(repo) / ".srt1" / "repositories")
            )
            record = registry.register_current(
                repo_path=repo,
                runtime_port=7483,
                manifest={
                    "integrity": {"manifest_hash": "manifest_123"},
                    "file_manifest": [
                        {"file_path": "src/auth.py"},
                        {"file_path": "tests/test_auth.py"},
                    ],
                },
                workcell_count=2,
            )
            reloaded = RepositoryActivationRegistry(
                state_dir=str(Path(repo) / ".srt1" / "repositories")
            )
            summary = reloaded.summary()

        self.assertTrue(record.active)
        self.assertEqual(record.status, "ready")
        self.assertEqual(record.file_count, 2)
        self.assertEqual(record.filecell_count, 2)
        self.assertEqual(record.workcell_count, 2)
        self.assertEqual(record.freshness_state, "fresh")
        self.assertEqual(summary["status"], "ready")
        self.assertEqual(summary["active_repository"]["repo_id"], record.repo_id)

    def test_engine_refresh_exposes_repository_activation_status(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.port = 7499
            engine.manifest = {
                "integrity": {"manifest_hash": "manifest_abc"},
                "file_manifest": [
                    {"file_path": "src/auth.py"},
                    {"file_path": "src/session.py"},
                ],
            }
            engine.repository_registry = RepositoryActivationRegistry(
                state_dir=str(Path(repo) / ".srt1" / "repositories")
            )
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.workcell_registry.populate_from_manifest(engine.manifest)

            status = engine._refresh_repository_activation()

        self.assertEqual(status["status"], "ready")
        self.assertEqual(status["count"], 1)
        self.assertEqual(status["active_repository"]["runtime_port"], 7499)
        self.assertEqual(status["active_repository"]["file_count"], 2)
        self.assertEqual(status["active_repository"]["workcell_count"], 2)

    def test_dashboard_contains_repository_manager_wiring(self):
        dashboard = (
            Path(__file__).resolve().parents[1]
            / "srt1_platform"
            / "pwa"
            / "dashboard.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Repository Manager", dashboard)
        self.assertIn("renderRepositoryManager", dashboard)
        self.assertIn("registerCurrentRepository", dashboard)
        self.assertIn("/api/v1/repositories/register-current", dashboard)


if __name__ == "__main__":
    unittest.main()
