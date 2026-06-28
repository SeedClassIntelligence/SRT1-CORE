import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from srt1_code_indexer import engine as engine_module
from srt1_platform.workcell import WorkCellRegistry


class WorkCellRuntimeTests(unittest.TestCase):
    def test_repository_understanding_populates_one_workcell_per_file(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            workcells = registry.populate_from_manifest({
                "integrity": {"manifest_hash": "manifest_123"},
                "file_manifest": [
                    {"file_path": "src/auth.py"},
                    {"file_path": "src/oauth.py"},
                    {"file_path": "src/billing.py"},
                ],
            })
            summary = registry.summary()

        self.assertEqual(len(workcells), 3)
        self.assertEqual(summary["workcell_count"], 3)
        self.assertEqual(
            sorted(wc["owned_paths"][0] for wc in summary["workcells"]),
            ["src/auth.py", "src/billing.py", "src/oauth.py"],
        )

    def test_seed_execution_selects_matching_file_workcell(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            execution = registry.activate_execution(
                queue_seed_id="seed_0001_auth",
                objective="Fix auth token validation",
                manifest={
                    "integrity": {"manifest_hash": "manifest_123"},
                    "file_manifest": [
                        {"file_path": "src/auth.py"},
                        {"file_path": "src/billing.py"},
                    ],
                },
            )
            summary = registry.summary()
            selected = [
                wc for wc in summary["workcells"]
                if wc["workcell_id"] == execution.workcell_id
            ][0]

        self.assertEqual(selected["owned_paths"], ["src/auth.py"])

    def test_seed_execution_prefers_exact_path_over_loose_stem_match(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            execution = registry.activate_execution(
                queue_seed_id="seed_0001_workcell_path",
                objective="Review srt1_platform/workcell.py boundary",
                manifest={
                    "integrity": {"manifest_hash": "manifest_123"},
                    "file_manifest": [
                        {"file_path": "srt1_code_indexer/srt.py"},
                        {"file_path": "srt1_platform/workcell.py"},
                    ],
                },
            )
            summary = registry.summary()
            selected = [
                wc for wc in summary["workcells"]
                if wc["workcell_id"] == execution.workcell_id
            ][0]

        self.assertEqual(selected["owned_paths"], ["srt1_platform/workcell.py"])

    def test_workcell_registry_creates_execution_package_with_workcell_md(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            execution = registry.activate_execution(
                queue_seed_id="seed_0001_workcell",
                srt_anchor_id="srt_anchor_001",
                objective="Refactor src/auth.py safely",
                runtime_port=4102,
                manifest={
                    "integrity": {"manifest_hash": "manifest_123"},
                    "file_manifest": [
                        {"file_path": "src/auth.py"},
                        {"file_path": "tests/test_auth.py"},
                    ],
                },
            )

            package = Path(execution.package_path)
            workcell_md = package / "workcell.md"
            runtime_state = package / "runtime_state.json"
            content = workcell_md.read_text(encoding="utf-8")

            self.assertEqual(execution.queue_seed_id, "seed_0001_workcell")
            self.assertEqual(execution.srt_anchor_id, "srt_anchor_001")
            self.assertTrue(workcell_md.exists())
            self.assertTrue(runtime_state.exists())
            self.assertIn("Refactor src/auth.py safely", content)
            self.assertIn("queue_seed_id: seed_0001_workcell", content)
            self.assertIn("Do not broaden context because files are nearby.", content)
            self.assertIn("src/auth.py", content)

    def test_workcell_candidate_generation_does_not_write_assistant_files(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_0001_no_assistant_writes",
                objective="Prepare bounded context",
                manifest={"file_manifest": [{"file_path": "module.py"}]},
            )

            forbidden = [
                "AGENTS.md",
                "CLAUDE.md",
                ".cursorrules",
                "copilot-instructions.md",
            ]
            written = [name for name in forbidden if (Path(repo) / name).exists()]

        self.assertEqual(written, [])

    def test_task_response_exposes_workcell_execution_for_queue_seed(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = None
            engine.task_seed_id = None
            engine.operations = []
            engine.injections = []
            engine.llm = None
            engine.analytics = None
            engine.manifest = {
                "integrity": {"manifest_hash": "manifest_abc"},
                "file_manifest": [{"file_path": "srt1_platform/seed_queue.py"}],
            }
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.bridge = None
            engine.port = 7484

            with patch.object(engine_module, "get_template_registry", None):
                queue_seed_id = engine._plant_seed(
                    "Create WorkCell execution",
                    source="api",
                    priority=5,
                    auto_dispatch=False,
                )

            response = engine._build_task_response(
                task="Create WorkCell execution",
                queue_seed_id=queue_seed_id,
                auto_dispatch=False,
            )
            workcell_md = Path(repo) / ".srt1" / "workcells" / queue_seed_id / "workcell.md"
            workcell_exists = workcell_md.exists()

        self.assertEqual(response["seed_id"], queue_seed_id)
        self.assertEqual(response["workcell"]["queue_seed_id"], queue_seed_id)
        self.assertEqual(response["workcell"]["runtime_port"], 7484)
        self.assertTrue(workcell_exists)

    def test_workcell_status_summary_is_available_without_active_seed(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.workcell_registry.activate_execution(
                queue_seed_id="seed_0001_status",
                objective="Expose WorkCell status",
                manifest={},
            )

            status = engine._get_workcell_status()

        self.assertEqual(status["workcell_count"], 1)
        self.assertEqual(status["execution_count"], 1)
        self.assertEqual(status["executions"][0]["queue_seed_id"], "seed_0001_status")

    def test_dashboard_contains_workcell_operations_surface(self):
        dashboard = Path(__file__).resolve().parents[1] / "srt1_platform" / "pwa" / "dashboard.html"
        html = dashboard.read_text(encoding="utf-8")

        self.assertIn("WorkCell Operations", html)
        self.assertIn("workcellList", html)
        self.assertIn("/api/v1/workcells", html)
        self.assertIn("renderWorkCells", html)


if __name__ == "__main__":
    unittest.main()
