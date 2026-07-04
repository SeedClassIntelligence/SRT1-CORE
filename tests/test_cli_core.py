import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from srt1_platform import cli


class CLIPolishTests(unittest.TestCase):
    def test_parser_exposes_public_commands(self):
        parser = cli.build_parser()
        help_text = parser.format_help()

        for command in ["start", "stop", "dashboard", "register", "status"]:
            with self.subTest(command=command):
                self.assertIn(command, help_text)

    def test_dashboard_prints_active_runtime_url_without_opening(self):
        with patch.object(cli, "_select_engine", return_value={"port": 7484}), \
             patch.object(cli.webbrowser, "open") as browser_open:
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.main(["dashboard", "--no-open"])

        self.assertEqual(code, 0)
        self.assertIn("http://127.0.0.1:7484/dashboard", out.getvalue())
        browser_open.assert_not_called()

    def test_select_engine_with_missing_port_does_not_fallback(self):
        engines = [{"port": 7484, "workspace_path": "C:\\repo\\main"}]

        with patch.object(cli, "_active_engines", return_value=engines):
            self.assertIsNone(cli._select_engine(port=7591))

    def test_select_engine_with_missing_repo_does_not_fallback(self):
        engines = [{"port": 7484, "workspace_path": "C:\\repo\\main"}]

        with patch.object(cli, "_active_engines", return_value=engines):
            self.assertIsNone(cli._select_engine(repo_path="C:\\repo\\other"))

    def test_status_reports_stopped_when_no_runtime_exists(self):
        with patch.object(cli, "_active_engines", return_value=[]):
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.main(["status"])

        self.assertEqual(code, 0)
        self.assertIn("No active SRT-1 runtime found.", out.getvalue())

    def test_status_json_reports_stopped_when_no_runtime_exists(self):
        with patch.object(cli, "_active_engines", return_value=[]):
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.main(["status", "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["status"], "stopped")
        self.assertEqual(payload["active_engines"], [])

    def test_status_defaults_to_concise_runtime_summary(self):
        engine = {
            "port": 7484,
            "pid": 12345,
            "workspace_name": "SRT1 CODING",
            "workspace_path": "C:\\repo\\SRT1 CODING",
        }
        status = {
            "status": "ready",
            "codebase_files": 227,
            "codebase_symbols": 5275,
            "active_seed": {
                "queue_seed_id": "seed_queue_1",
                "lifecycle_state": "planted",
            },
            "file_tree": [{"path": f"file_{index}.py"} for index in range(100)],
        }
        with patch.object(cli, "_select_engine", return_value=engine), \
             patch.object(cli, "_request_json", return_value=status):
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.main(["status"])

        text = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("SRT-1: running", text)
        self.assertIn("Dashboard: http://127.0.0.1:7484/dashboard", text)
        self.assertIn("Files: 227", text)
        self.assertIn("Active seed: seed_queue_1 (planted)", text)
        self.assertNotIn("file_99.py", text)

    def test_stop_calls_runtime_shutdown_endpoint(self):
        with patch.object(cli, "_select_engine", return_value={"port": 7484}), \
             patch.object(cli, "_request_json", return_value={"status": "stopping"}) as request_json:
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.main(["stop"])

        self.assertEqual(code, 0)
        request_json.assert_called_once_with(
            "POST",
            "http://127.0.0.1:7484/api/v1/runtime/shutdown",
            payload={},
        )
        self.assertIn("stopping", out.getvalue())

    def test_register_posts_path_to_active_runtime(self):
        with tempfile.TemporaryDirectory() as repo:
            response = {"status": "registered", "registered_repository": {"path": str(Path(repo).resolve())}}
            with patch.object(cli, "_select_engine", return_value={"port": 7484}), \
                 patch.object(cli, "_request_json", return_value=response) as request_json:
                out = io.StringIO()
                with redirect_stdout(out):
                    code = cli.main(["register", repo])

        self.assertEqual(code, 0)
        method, url = request_json.call_args.args
        payload = request_json.call_args.kwargs["payload"]
        self.assertEqual(method, "POST")
        self.assertEqual(url, "http://127.0.0.1:7484/api/v1/repositories/register-path")
        self.assertEqual(payload["path"], str(Path(repo).resolve()))
        self.assertIn("registered", out.getvalue())

    def test_start_uses_existing_engine(self):
        fake_engine = Mock()
        with tempfile.TemporaryDirectory() as repo, \
             patch("srt1_code_indexer.engine.init_db") as init_db, \
             patch("srt1_code_indexer.engine.SRT1Engine", return_value=fake_engine) as engine_cls:
            code = cli.main(["start", "--repo", repo, "--port", "7555", "--task", "Review CLI"])

        self.assertEqual(code, 0)
        init_db.assert_called_once()
        engine_cls.assert_called_once()
        self.assertEqual(engine_cls.call_args.kwargs["repo_path"], str(Path(repo).resolve()))
        self.assertEqual(engine_cls.call_args.kwargs["port"], 7555)
        self.assertEqual(engine_cls.call_args.kwargs["task"], "Review CLI")
        fake_engine.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
