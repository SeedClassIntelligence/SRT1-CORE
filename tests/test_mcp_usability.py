import tempfile
import unittest
from pathlib import Path

from srt1_platform.mcp_server import MCPServer, SCIAMCPEngine
from srt1_platform.workcell import WorkCellRegistry


class MCPUsabilityTests(unittest.TestCase):
    def _engine(self, repo: str) -> SCIAMCPEngine:
        engine = SCIAMCPEngine.__new__(SCIAMCPEngine)
        engine.repo_path = str(Path(repo).resolve())
        engine.manifest = {
            "integrity": {"manifest_hash": "manifest_mcp"},
            "file_manifest": [{"file_path": "src/auth.py", "extension": ".py"}],
            "symbol_table": {
                "src/auth.py": [
                    {
                        "name": "authenticate",
                        "type": "function",
                        "line": 3,
                        "dependencies": ["load_user"],
                        "reflection": {
                            "purpose": "Validate credentials for a local user.",
                            "architectural_role": "AUTH_SERVICE",
                            "risk_profile": ["AUTH_SENSITIVE"],
                        },
                    }
                ]
            },
        }
        engine.symbol_table = engine.manifest["symbol_table"]
        engine.curation_report = {}
        engine.call_graph = {}
        engine.synopsis = "MCP test repo."
        engine.current_task = None
        engine.interactions = []
        engine.injections = []
        engine.interaction_count = 0
        return engine

    def test_mcp_lists_repository_and_workcell_context_tools(self):
        with tempfile.TemporaryDirectory() as repo:
            server = MCPServer(self._engine(repo))

            response = server._handle_request({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            })
            names = [tool["name"] for tool in response["result"]["tools"]]

        self.assertIn("srt1_get_repository_status", names)
        self.assertIn("srt1_get_workcell_context", names)
        self.assertIn("srt1_get_context", names)

    def test_repository_status_exposes_workcell_and_trust_state(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            engine = self._engine(repo)
            registry.populate_from_manifest(engine.manifest)

            status = engine.get_repository_status()

        self.assertEqual(status["manifest_hash"], "manifest_mcp")
        self.assertEqual(status["freshness_state"], "fresh")
        self.assertEqual(status["trust_state"]["signature"], "unsigned")
        self.assertEqual(status["trust_state"]["verification"], "verified")
        self.assertEqual(status["workcell_count"], 1)
        self.assertIn("WorkCell context first", status["context_rule"])

    def test_workcell_context_is_bounded_to_filecell(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = self._engine(repo)
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_0001_auth",
                objective="Refactor src/auth.py",
                manifest=engine.manifest,
                srt_anchor_id="srt_anchor_auth",
                runtime_port=7484,
            )

            context = engine.get_workcell_context(queue_seed_id="seed_0001_auth")

        self.assertEqual(context["status"], "ready")
        self.assertEqual(context["queue_seed_id"], "seed_0001_auth")
        self.assertEqual(context["owned_paths"], ["src/auth.py"])
        self.assertEqual(context["filecell"]["path"], "src/auth.py")
        self.assertEqual(context["filecell"]["symbol_count"], 1)
        self.assertIn("bounded WorkCell context", context["context_rule"])
        self.assertIn("queue_seed_id: seed_0001_auth", context["workcell_md"])

    def test_default_context_is_compact_orientation_not_repo_dump(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = self._engine(repo)
            text = engine.get_context()

        self.assertIn("SRT-1 Repository Context", text)
        self.assertIn("WorkCells:", text)
        self.assertIn("srt1_get_workcell_context", text)
        self.assertNotIn("Full SRT-1 Context", text)


if __name__ == "__main__":
    unittest.main()
