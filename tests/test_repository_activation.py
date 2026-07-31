import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

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

    def test_engine_normalizes_github_repository_urls(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)

        https_repo = engine._parse_github_repository_url("https://github.com/SeedClassIntelligence/SRT1-CORE")
        ssh_repo = engine._parse_github_repository_url("git@github.com:SeedClassIntelligence/SRT1-CORE.git")

        self.assertEqual(https_repo["owner"], "SeedClassIntelligence")
        self.assertEqual(https_repo["repo"], "SRT1-CORE")
        self.assertEqual(https_repo["clone_url"], "https://github.com/SeedClassIntelligence/SRT1-CORE.git")
        self.assertEqual(https_repo["safe_name"], "SeedClassIntelligence__SRT1-CORE")
        self.assertEqual(ssh_repo["clone_url"], "git@github.com:SeedClassIntelligence/SRT1-CORE.git")
        with self.assertRaises(ValueError):
            engine._parse_github_repository_url("https://gitlab.com/owner/repo")

    def test_engine_register_github_fails_closed_when_git_is_unavailable(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.repository_registry = RepositoryActivationRegistry(
                state_dir=str(Path(repo) / ".srt1" / "repositories")
            )
            with patch.object(engine, "_git_executable", return_value=None):
                result = engine._register_github_repository("https://github.com/owner/repo")

        self.assertEqual(result["status"], "error")
        self.assertIn("Git is required", result["error"])
        self.assertEqual(result["repositories"], [])

    def test_engine_registers_external_path_without_switching_runtime(self):
        with tempfile.TemporaryDirectory() as active_repo, tempfile.TemporaryDirectory() as other_repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = active_repo
            engine.port = 7499
            engine.manifest = {
                "integrity": {"manifest_hash": "manifest_active"},
                "file_manifest": [{"file_path": "src/app.py"}],
            }
            engine.repository_registry = RepositoryActivationRegistry(
                state_dir=str(Path(active_repo) / ".srt1" / "repositories")
            )
            engine.workcell_registry = WorkCellRegistry(repo_path=active_repo)
            engine.workcell_registry.populate_from_manifest(engine.manifest)
            active_status = engine._refresh_repository_activation()

            registered = engine._register_repository_path(other_repo)
            rejected_activation = engine._activate_repository(
                registered["registered_repository"]["repo_id"]
            )

        self.assertEqual(active_status["status"], "ready")
        self.assertEqual(registered["status"], "registered")
        self.assertEqual(len(registered["repositories"]), 2)
        self.assertEqual(registered["active_repository"]["path"], str(Path(active_repo).resolve()))
        self.assertEqual(rejected_activation["status"], "registered")
        self.assertIn("different local path", rejected_activation["error"])

    def test_engine_launches_registered_repository_as_separate_runtime(self):
        with tempfile.TemporaryDirectory() as active_repo, tempfile.TemporaryDirectory() as other_repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = active_repo
            engine.port = 7499
            engine.manifest = {
                "integrity": {"manifest_hash": "manifest_active"},
                "file_manifest": [{"file_path": "src/app.py"}],
            }
            engine.repository_registry = RepositoryActivationRegistry(
                state_dir=str(Path(active_repo) / ".srt1" / "repositories")
            )
            engine.workcell_registry = WorkCellRegistry(repo_path=active_repo)
            engine.workcell_registry.populate_from_manifest(engine.manifest)
            engine._refresh_repository_activation()
            registered = engine._register_repository_path(other_repo)
            repo_id = registered["registered_repository"]["repo_id"]

            with patch.object(engine_module, "OperationalRegistry", None), \
                 patch.object(engine_module, "_find_free_port", return_value=7555), \
                 patch.object(engine_module.subprocess, "Popen", return_value=Mock(pid=12345)) as popen:
                launched = engine._launch_repository_runtime(repo_id)

        self.assertEqual(launched["status"], "launching", launched)
        self.assertEqual(launched["runtime_port"], 7555)
        self.assertEqual(launched["pid"], 12345)
        self.assertEqual(launched["active_repository"]["path"], str(Path(active_repo).resolve()))
        self.assertIn("http://127.0.0.1:7555/experience.html", launched["experience_url"])
        self.assertIn("http://127.0.0.1:7555/dashboard", launched["dashboard_url"])
        args = popen.call_args.args[0]
        self.assertIn("--repo_path", args)
        self.assertIn(str(Path(other_repo).resolve()), args)
        self.assertEqual(popen.call_args.kwargs["env"]["SRT1_NO_BROWSER"], "1")

    def test_engine_clears_stale_external_runtime_ports_from_status(self):
        with tempfile.TemporaryDirectory() as active_repo, tempfile.TemporaryDirectory() as other_repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = active_repo
            engine.port = 7499
            engine.manifest = {
                "integrity": {"manifest_hash": "manifest_active"},
                "file_manifest": [{"file_path": "src/app.py"}],
            }
            engine.repository_registry = RepositoryActivationRegistry(
                state_dir=str(Path(active_repo) / ".srt1" / "repositories")
            )
            engine.workcell_registry = WorkCellRegistry(repo_path=active_repo)
            engine.workcell_registry.populate_from_manifest(engine.manifest)
            engine._refresh_repository_activation()
            stale = engine.repository_registry.register_path(other_repo, runtime_port=7555)

            with patch.object(engine_module, "_is_local_port_open", return_value=False):
                status = engine._get_repository_activation_status()

        other = next(repo for repo in status["repositories"] if repo["repo_id"] == stale.repo_id)
        self.assertIsNone(other["runtime_port"])
        self.assertEqual(status["active_repository"]["runtime_port"], 7499)

    def test_engine_stops_external_repository_runtime(self):
        with tempfile.TemporaryDirectory() as active_repo, tempfile.TemporaryDirectory() as other_repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = active_repo
            engine.port = 7499
            engine.manifest = {
                "integrity": {"manifest_hash": "manifest_active"},
                "file_manifest": [{"file_path": "src/app.py"}],
            }
            engine.repository_registry = RepositoryActivationRegistry(
                state_dir=str(Path(active_repo) / ".srt1" / "repositories")
            )
            engine.workcell_registry = WorkCellRegistry(repo_path=active_repo)
            engine.workcell_registry.populate_from_manifest(engine.manifest)
            engine._refresh_repository_activation()
            registered = engine._register_repository_path(other_repo)
            repo_id = registered["registered_repository"]["repo_id"]
            engine.repository_registry.register_path(other_repo, runtime_port=7555)

            class FakeOperationalRegistry:
                def __init__(self):
                    self.deregistered = None

                def get_all_engines(self):
                    return {
                        "engines": {
                            "engine_other": {
                                "workspace_path": str(Path(other_repo).resolve()),
                                "status": "RUNNING",
                                "pid": 12345,
                                "port": 7555,
                            }
                        }
                    }

                def deregister_engine(self, engine_id):
                    self.deregistered = engine_id
                    return True

            fake_registry = FakeOperationalRegistry()
            with patch.object(engine_module, "OperationalRegistry", return_value=fake_registry), \
                 patch.object(engine_module.os, "kill") as kill:
                stopped = engine._stop_repository_runtime(repo_id)

        self.assertEqual(stopped["status"], "stopped")
        self.assertEqual(stopped["stopped_pid"], 12345)
        kill.assert_called_once()
        self.assertEqual(stopped["registered_repository"]["runtime_port"], None)
        self.assertEqual(stopped["active_repository"]["path"], str(Path(active_repo).resolve()))

    def test_dashboard_contains_repository_manager_wiring(self):
        dashboard = (
            Path(__file__).resolve().parents[1]
            / "srt1_platform"
            / "pwa"
            / "dashboard.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Repository Manager", dashboard)
        self.assertIn("repo-activation-flow", dashboard)
        self.assertIn("Repository Readiness", dashboard)
        self.assertIn("repoReadinessStrip", dashboard)
        self.assertIn("repoReadyRepository", dashboard)
        self.assertIn("repoReadyUnderstanding", dashboard)
        self.assertIn("repoReadyWorkCells", dashboard)
        self.assertIn("repoReadyRuntime", dashboard)
        self.assertIn("Known Repositories", dashboard)
        self.assertIn("renderRepositoryManager", dashboard)
        self.assertIn("setRepositoryReadiness", dashboard)
        self.assertIn("Reflection Findings", dashboard)
        self.assertIn("Reflection Guardrails", dashboard)
        self.assertIn("themeToggle", dashboard)
        self.assertIn("toggleDashboardTheme", dashboard)
        self.assertIn("srt1_dashboard_theme", dashboard)
        self.assertIn("theme-light", dashboard)
        self.assertIn("file-intel-trigger", dashboard)
        self.assertIn("file-intel-popover", dashboard)
        self.assertIn("FileCell", dashboard)
        self.assertIn("activateRepository", dashboard)
        self.assertIn("registerRepositoryPath", dashboard)
        self.assertIn("browseRepositoryFolder", dashboard)
        self.assertIn("Browse folder", dashboard)
        self.assertIn("launchRepositoryRuntime", dashboard)
        self.assertIn("Launch runtime", dashboard)
        self.assertIn("stopRepositoryRuntime", dashboard)
        self.assertIn("Stop runtime", dashboard)
        self.assertIn("shutdownCurrentRuntime", dashboard)
        self.assertIn("Stop SRT-1", dashboard)
        self.assertIn("openRepositoryRuntime", dashboard)
        self.assertIn("result.experience_url", dashboard)
        self.assertIn("/experience.html", dashboard)
        self.assertNotIn("window.location.href = result.dashboard_url", dashboard)
        self.assertIn("registerCurrentRepository", dashboard)
        self.assertIn("/api/v1/repositories/launch", dashboard)
        self.assertIn("/api/v1/repositories/stop-runtime", dashboard)
        self.assertIn("/api/v1/runtime/shutdown", dashboard)
        self.assertIn("/api/v1/repositories/browse-folder", dashboard)
        self.assertIn("/api/v1/repositories/register-path", dashboard)
        self.assertIn("/api/v1/repositories/register-current", dashboard)
        self.assertIn("/api/v1/repositories/activate", dashboard)


if __name__ == "__main__":
    unittest.main()
