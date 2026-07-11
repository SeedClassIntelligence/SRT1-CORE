import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from srt1_code_indexer import engine as engine_module
from srt1_platform.execution_bridge import DispatchMethod, SCIADispatchBridge


class AssistantAdapterSurfaceTests(unittest.TestCase):
    def test_engine_configures_core_safe_assistant_adapters(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.bridge = SCIADispatchBridge(repo_path=repo)

            result = engine._configure_assistant_adapters([
                {"type": "codex"},
                {"type": "file_context", "name": "local_handoff"},
                {"type": "custom_http", "endpoint": "http://127.0.0.1:9000/workcell"},
                {"type": "openai_compatible", "provider": "openai", "endpoint": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o-mini"},
                {"type": "custom_http", "endpoint": ""},
                {"type": "openai_compatible", "provider": "openai", "endpoint": "", "model": "gpt-4o-mini"},
                {"type": "unknown_model"},
            ])

            self.assertEqual(result["status"], "configured")
            self.assertIn(DispatchMethod.ASSISTANT_ADAPTER, result["dispatch_methods"])
            self.assertEqual(
                result["assistant_adapters"],
                [
                    {"type": "codex", "name": "codex"},
                    {"type": "file_context", "name": "local_handoff"},
                    {
                        "type": "custom_http",
                        "endpoint": "http://127.0.0.1:9000/workcell",
                        "timeout": 20.0,
                    },
                    {
                        "type": "openai_compatible",
                        "provider": "openai",
                        "endpoint": "https://api.openai.com/v1/chat/completions",
                        "model": "gpt-4o-mini",
                        "timeout": 60.0,
                    },
                ],
            )

            reloaded = SCIADispatchBridge(repo_path=repo)
            self.assertEqual(reloaded.assistant_adapters, result["assistant_adapters"])

    def test_clearing_assistant_adapters_removes_dispatch_method(self):
        with tempfile.TemporaryDirectory() as repo:
            bridge = SCIADispatchBridge(repo_path=repo)
            bridge.configure(
                dispatch_methods=[DispatchMethod.FILE_BASED],
                assistant_adapters=[{"type": "codex"}],
            )
            self.assertIn(DispatchMethod.ASSISTANT_ADAPTER, bridge.dispatch_methods)

            bridge.configure(assistant_adapters=[])

            self.assertEqual(bridge.assistant_adapters, [])
            self.assertNotIn(DispatchMethod.ASSISTANT_ADAPTER, bridge.dispatch_methods)

    def test_slack_seed_intake_uses_canonical_plant_seed_flow(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.task = None
        engine._plant_seed = Mock(return_value="seed_queue_1")
        engine._build_task_response = Mock(return_value={
            "seed_id": "seed_queue_1",
            "queue_seed_id": "seed_queue_1",
            "srt_anchor_id": "srt_anchor_1",
        })
        engine._generate_context_files = Mock()

        result = engine._plant_slack_seed({
            "text": "/srt1 improve dashboard adapter selector",
            "user_name": "darnell",
            "user_id": "U123",
            "channel_id": "C123",
        })

        self.assertEqual(result["status"], "seed_planted")
        self.assertEqual(result["queue_seed_id"], "seed_queue_1")
        self.assertEqual(result["source"], "slack")
        self.assertEqual(result["slack"]["user_name"], "darnell")
        engine._plant_seed.assert_called_once_with(
            "improve dashboard adapter selector",
            source="slack",
            priority=5,
            auto_dispatch=True,
            template_id=None,
            assistant_credentials=None,
        )
        engine._build_task_response.assert_called_once_with(
            task="improve dashboard adapter selector",
            queue_seed_id="seed_queue_1",
            auto_dispatch=True,
        )

    def test_dashboard_contains_assistant_adapter_and_slack_wiring(self):
        dashboard = (
            Path(__file__).resolve().parents[1]
            / "srt1_platform"
            / "pwa"
            / "dashboard.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Assistant Adapters", dashboard)
        self.assertIn("adapterCodex", dashboard)
        self.assertIn("adapterFile", dashboard)
        self.assertIn("adapterHttpEndpoint", dashboard)
        self.assertIn("adapterProvider", dashboard)
        self.assertIn("adapterProviderEndpoint", dashboard)
        self.assertIn("adapterProviderModel", dashboard)
        self.assertIn("openai_compatible", dashboard)
        self.assertIn("https://api.openai.com/v1/chat/completions", dashboard)
        self.assertIn("gpt-4o-mini", dashboard)
        self.assertIn("loadAssistantAdapters", dashboard)
        self.assertIn("saveAssistantAdapters", dashboard)
        self.assertIn("/api/v1/assistant-adapters", dashboard)
        self.assertIn("Slack Seed Intake", dashboard)
        self.assertIn("submitSlackSeed", dashboard)
        self.assertIn("/api/v1/slack/seed", dashboard)

    def test_dashboard_does_not_persist_provider_keys(self):
        dashboard = (
            Path(__file__).resolve().parents[1]
            / "srt1_platform"
            / "pwa"
            / "dashboard.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Session keys stay in this browser tab only", dashboard)
        self.assertIn("Credential Mode", dashboard)
        self.assertIn("Session-only", dashboard)
        self.assertIn("External environment / OS vault", dashboard)
        self.assertIn("setCredentialMode", dashboard)
        self.assertIn("buildAssistantCredentialPayload", dashboard)
        self.assertIn("assistant_credentials", dashboard)
        self.assertIn("SRT-1 Core will not persist provider API keys", dashboard)
        self.assertIn("purgePersistedProviderKeys", dashboard)
        self.assertNotIn("localStorage.setItem('srt1_apikey_", dashboard)
        self.assertNotIn('localStorage.setItem("srt1_apikey_', dashboard)
        self.assertNotIn("localStorage.getItem('srt1_apikey_", dashboard)
        self.assertNotIn('localStorage.getItem("srt1_apikey_', dashboard)

    def test_dashboard_workcell_run_sends_session_credentials_to_task(self):
        dashboard = (
            Path(__file__).resolve().parents[1]
            / "srt1_platform"
            / "pwa"
            / "dashboard.html"
        ).read_text(encoding="utf-8")

        self.assertIn("runWorkCellWithAssistant", dashboard)
        self.assertIn("auto_dispatch: true", dashboard)
        self.assertIn("dashboard_workcell", dashboard)
        self.assertIn("assistant_credentials = buildAssistantCredentialPayload()", dashboard)
        self.assertIn("workcell_execution_id", dashboard)
        self.assertIn("allowed_paths", dashboard)
        self.assertIn("loadWorkCellProposals", dashboard)
        self.assertIn("applyChangeProposal", dashboard)

    def test_api_task_route_preserves_credentials_and_serializes_seed(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "srt1_code_indexer"
            / "engine.py"
        ).read_text(encoding="utf-8")

        self.assertIn('path in ("/seeds", "/task", "/api/v1/task")', source)
        self.assertIn('assistant_credentials=body.get("assistant_credentials")', source)
        self.assertIn('if hasattr(seed_data, "to_dict"):', source)
        self.assertIn("seed_data = seed_data.to_dict()", source)
        self.assertIn('"secret_persisted": False', source)


if __name__ == "__main__":
    unittest.main()
