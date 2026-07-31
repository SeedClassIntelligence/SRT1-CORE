import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from srt1_code_indexer import engine as engine_module
from srt1_platform.recall_packet import RecallPacket
from srt1_pro.context_bundler import SCIAContextBundler
from srt1_pro.reinjector import SCIAReinjector


class RecordingSeedQueue(engine_module.SCIASeedQueue):
    def __init__(self, queue_dir, events):
        self.events = events
        super().__init__(queue_dir=queue_dir)

    def plant(self, *args, **kwargs):
        self.events.append("queue")
        return super().plant(*args, **kwargs)


class TaskResponseIdentityTests(unittest.TestCase):
    def test_project_conversation_uses_srt1_context_without_creating_execution(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.repo_path = "C:/project"
        engine.synopsis = "Canonical project synopsis"
        engine.manifest = {
            "metadata": {"total_files_scanned": 2, "total_symbols_indexed": 4},
            "integrity": {"manifest_hash": "manifest-123"},
            "file_manifest": [{"file_path": "app.py"}, {"file_path": "tests/test_app.py"}],
        }
        engine.symbol_table = {}
        engine.signing_client = None
        engine._trust_integrity = None
        engine._trust_chain = None
        engine._get_workcell_status = lambda: {"executions": []}
        engine._get_active_seed_identity = lambda: None
        captured = {}

        class FakeRegistry:
            def __init__(self, configs): captured["configs"] = configs
            def dispatch_all(self, request):
                captured["request"] = request
                return {"openai_compatible": {
                    "status": "dispatched",
                    "response": {
                        "provider": "together", "model": "test-model",
                        "result": {"choices": [{"message": {"content": '{"message":"Grounded response"}'}}]},
                    },
                }}

        with patch.object(engine_module, "AssistantAdapterRegistry", FakeRegistry):
            result = engine._project_conversation({
                "message": "Explain the architecture",
                "assistant_adapter": {
                    "type": "openai_compatible", "provider": "together",
                    "endpoint": "https://api.together.xyz/v1/chat/completions", "model": "test-model",
                },
                "assistant_credentials": {
                    "mode": "session", "provider": "together",
                    "provider_keys": {"together": "session-secret"},
                },
            })

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["message"], "Grounded response")
        self.assertFalse(result["execution_created"])
        self.assertFalse(result["write_scope_granted"])
        self.assertFalse(result["secret_persisted"])
        self.assertTrue(captured["request"].metadata["conversation_only"])
        self.assertIn("Canonical project synopsis", captured["request"].blueprint)

    def test_task_response_uses_queue_seed_id_as_primary_seed_id(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = None
            engine.task_seed_id = None
            engine.operations = []
            engine.injections = []
            engine.llm = None
            engine.analytics = None
            engine.manifest = {}
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            engine.bridge = None

            with patch.object(engine_module, "get_template_registry", None):
                queue_seed_id = engine._plant_seed(
                    "Add continuity identity compatibility",
                    source="api",
                    priority=5,
                    auto_dispatch=False,
                )

            response = engine._build_task_response(
                task="Add continuity identity compatibility",
                queue_seed_id=queue_seed_id,
                auto_dispatch=False,
            )

        self.assertEqual(response["seed_id"], queue_seed_id)
        self.assertEqual(response["queue_seed_id"], queue_seed_id)
        self.assertEqual(response["srt_anchor_id"], engine.task_seed_id)
        self.assertNotEqual(response["seed_id"], response["srt_anchor_id"])

    def test_plant_seed_creates_queue_seed_before_srt_anchor(self):
        events = []

        class FakeSRT:
            def __init__(self, reflection_interval):
                self._active_seed_id = None

            def plant_seed(self, *args, **kwargs):
                events.append("srt")
                self._active_seed_id = "srt_anchor_001"

        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = None
            engine.task_seed_id = None
            engine.operations = []
            engine.injections = []
            engine.llm = None
            engine.analytics = None
            engine.manifest = {}
            engine.seed_queue = RecordingSeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds"),
                events=events,
            )
            engine.bridge = None

            with patch.object(engine_module, "get_template_registry", None), \
                    patch.object(engine_module, "SRT", FakeSRT):
                queue_seed_id = engine._plant_seed(
                    "Create queue first",
                    source="api",
                    priority=5,
                    auto_dispatch=False,
                )

            queue_seed = engine.seed_queue.get_seed(queue_seed_id)

        self.assertEqual(events, ["queue", "srt"])
        self.assertEqual(queue_seed["srt_anchor_id"], "srt_anchor_001")

    def test_engine_task_seed_id_does_not_override_queue_seed_id_in_response(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.task_seed_id = "srt_anchor_should_not_win"
        engine.bridge = None
        engine.manifest = {}
        engine.seed_queue = None

        response = engine._build_task_response(
            task="Prefer queue id",
            queue_seed_id="seed_0001_queue",
            auto_dispatch=False,
        )

        self.assertEqual(response["seed_id"], "seed_0001_queue")
        self.assertEqual(response["queue_seed_id"], "seed_0001_queue")
        self.assertEqual(response["srt_anchor_id"], "srt_anchor_should_not_win")

    def test_active_seed_identity_prefers_queue_state(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.task = "Queue canonical status"
            engine.task_seed_id = "srt_anchor_legacy"
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            seed = engine.seed_queue.plant(
                "Queue canonical status",
                source="api",
                priority=5,
            )
            engine.seed_queue.set_srt_anchor(seed.seed_id, "srt_anchor_queue")

            identity = engine._get_active_seed_identity()

        self.assertEqual(identity["seed_id"], seed.seed_id)
        self.assertEqual(identity["queue_seed_id"], seed.seed_id)
        self.assertEqual(identity["srt_anchor_id"], "srt_anchor_queue")
        self.assertEqual(identity["lifecycle_state"], "planted")
        self.assertEqual(identity["stage"], "planted")
        self.assertEqual(identity["trust_state"]["signature"], "unsigned")
        self.assertIsNone(identity["manifest_hash"])

    def test_active_seed_identity_falls_back_when_queue_unavailable(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.task = "Legacy active seed"
        engine.task_seed_id = "srt_anchor_legacy"
        engine.seed_queue = None

        identity = engine._get_active_seed_identity()

        self.assertEqual(identity["seed_id"], "srt_anchor_legacy")
        self.assertIsNone(identity["queue_seed_id"])
        self.assertEqual(identity["srt_anchor_id"], "srt_anchor_legacy")
        self.assertIsNone(identity["lifecycle_state"])
        self.assertEqual(identity["intent"], "Legacy active seed")

    def test_recall_hydration_uses_canonical_queue_seed_id(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.task = "Recall canonical seed"
            engine.task_seed_id = "srt_anchor_recall"
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            seed = engine.seed_queue.plant("Recall canonical seed")
            engine.seed_queue.set_srt_anchor(seed.seed_id, "srt_anchor_recall")

            recall_seed_id = engine._get_recall_seed_id()
            recall_url = engine._build_recall_url(recall_seed_id, limit=3)

        self.assertEqual(recall_seed_id, seed.seed_id)
        self.assertIn(f"/memory/recall/{seed.seed_id}?limit=3", recall_url)
        self.assertNotIn("{self.task_seed_id}", recall_url)
        self.assertNotIn("srt_anchor_recall", recall_url)

    def test_recall_packet_uses_queue_seed_id_with_srt_anchor_metadata(self):
        packet = RecallPacket.create(
            queue_seed_id="seed_0001_queue",
            srt_anchor_id="srt_anchor_001",
            source_type="manifest",
            source_id="symbol:Example",
            content="Example is relevant.",
            relevance_score=0.8,
            freshness_state="fresh",
            manifest_hash="abc123",
        )
        data = packet.to_dict()

        self.assertEqual(data["queue_seed_id"], "seed_0001_queue")
        self.assertEqual(data["srt_anchor_id"], "srt_anchor_001")
        self.assertNotEqual(data["queue_seed_id"], data["srt_anchor_id"])
        self.assertEqual(data["trust_state"]["signature"], "unsigned")

    def test_external_memory_reflection_becomes_recall_packet(self):
        packet = RecallPacket.from_external_reflection(
            {
                "id": "lesson_1",
                "content": "Use the existing queue seed identity.",
                "relevance_score": 0.75,
                "ttl": 2,
            },
            queue_seed_id="seed_0001_queue",
            srt_anchor_id="srt_anchor_001",
            manifest_hash="manifest_hash",
        )
        reinjection = packet.to_reinjection_dict()

        self.assertEqual(reinjection["queue_seed_id"], "seed_0001_queue")
        self.assertEqual(reinjection["srt_anchor_id"], "srt_anchor_001")
        self.assertEqual(reinjection["mode"], "recall")
        self.assertEqual(reinjection["source_type"], "external_private")
        self.assertEqual(reinjection["content"], "Use the existing queue seed identity.")

    def test_recall_hydration_fails_closed_for_placeholder_seed_id(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.task_seed_id = "{self.task_seed_id}"
        engine.seed_queue = None

        self.assertEqual(engine._fetch_recall_reflections(), [])

    def test_private_memory_unavailable_fails_closed_with_queue_identity(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.task = "Recall unavailable"
            engine.task_seed_id = "srt_anchor_unavailable"
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            seed = engine.seed_queue.plant("Recall unavailable")
            engine.seed_queue.set_srt_anchor(seed.seed_id, "srt_anchor_unavailable")

            recalls = engine._fetch_recall_reflections(limit=1)

        self.assertEqual(recalls, [])

    def test_reinjector_consumes_recall_packet_metadata(self):
        with tempfile.TemporaryDirectory() as repo:
            agents_path = Path(repo) / "AGENTS.md"
            agents_path.write_text(
                "## ⚠️ ACTIVE ENFORCEMENT (BLOCKING)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🎯 ACTIVE ALIGNMENT (GUIDANCE)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🧠 RELEVANT MEMORY (RECALL)\n"
                "*(runtime)*\n"
                "- old\n",
                encoding="utf-8",
            )
            packet = RecallPacket.create(
                queue_seed_id="seed_0001_queue",
                srt_anchor_id="srt_anchor_001",
                source_type="manifest",
                source_id="symbol:Queue",
                content="Use queue seed identity.",
                relevance_score=0.9,
                freshness_state="fresh",
            )

            reinjector = SCIAReinjector(repo)
            success = reinjector.inject_packets(
                active_task="Align recall",
                warnings=[],
                reflections=[packet],
            )
            state = json.loads((Path(repo) / ".srt1" / "reinjector_state.json").read_text(encoding="utf-8"))
            content = agents_path.read_text(encoding="utf-8")

        self.assertTrue(success)
        recall_state = [p for p in state if p["mode"] == "recall"][0]
        self.assertEqual(recall_state["queue_seed_id"], "seed_0001_queue")
        self.assertEqual(recall_state["srt_anchor_id"], "srt_anchor_001")
        self.assertEqual(recall_state["source_type"], "manifest")
        self.assertEqual(recall_state["freshness_state"], "fresh")
        self.assertIn("queue_seed_id=seed_0001_queue", content)
        self.assertIn("source_type=manifest", content)

    def test_reinjector_marks_degraded_recall_packet_warning(self):
        with tempfile.TemporaryDirectory() as repo:
            agents_path = Path(repo) / "AGENTS.md"
            agents_path.write_text(
                "## ⚠️ ACTIVE ENFORCEMENT (BLOCKING)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🎯 ACTIVE ALIGNMENT (GUIDANCE)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🧠 RELEVANT MEMORY (RECALL)\n"
                "*(runtime)*\n"
                "- old\n",
                encoding="utf-8",
            )
            packet = RecallPacket.degraded(
                queue_seed_id="seed_0001_queue",
                srt_anchor_id="srt_anchor_001",
                reason="private memory unavailable",
            )

            reinjector = SCIAReinjector(repo)
            success = reinjector.inject_packets(
                active_task="Align degraded recall",
                warnings=[],
                reflections=[packet.to_reinjection_dict()],
            )
            state = json.loads((Path(repo) / ".srt1" / "reinjector_state.json").read_text(encoding="utf-8"))
            content = agents_path.read_text(encoding="utf-8")

        self.assertTrue(success)
        recall_state = [p for p in state if p["mode"] == "recall"][0]
        self.assertEqual(recall_state["freshness_state"], "degraded")
        self.assertEqual(recall_state["degradation_reason"], "private memory unavailable")
        self.assertEqual(recall_state["warning"], "private memory unavailable")
        self.assertIn("freshness=degraded", content)
        self.assertIn("warning=private memory unavailable", content)

    def test_reinjector_still_accepts_legacy_raw_reflection(self):
        with tempfile.TemporaryDirectory() as repo:
            Path(repo, "AGENTS.md").write_text(
                "## ⚠️ ACTIVE ENFORCEMENT (BLOCKING)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🎯 ACTIVE ALIGNMENT (GUIDANCE)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🧠 RELEVANT MEMORY (RECALL)\n"
                "*(runtime)*\n"
                "- old\n",
                encoding="utf-8",
            )

            reinjector = SCIAReinjector(repo)
            success = reinjector.inject_packets(
                active_task="Legacy reflection",
                warnings=[],
                reflections=[{"content": "Legacy lesson", "priority": 30}],
            )
            state = json.loads((Path(repo) / ".srt1" / "reinjector_state.json").read_text(encoding="utf-8"))

        self.assertTrue(success)
        recall_state = [p for p in state if p["mode"] == "recall"][0]
        self.assertEqual(recall_state["content"], "Legacy lesson")
        self.assertIsNone(recall_state["queue_seed_id"])

    def test_context_bundler_emits_recall_packet_manifest_candidates(self):
        with tempfile.TemporaryDirectory() as repo:
            manifest_path = Path(repo) / "srt1_code_manifest.json"
            manifest_path.write_text(
                json.dumps({
                    "metadata": {"repo_path": repo},
                    "integrity": {"manifest_hash": "manifest_123"},
                    "symbol_table": {
                        "srt1_platform/seed_queue.py": [
                            {
                                "name": "SCIASeedQueue",
                                "type": "class",
                                "line": 10,
                                "dependencies": [],
                                "docstring_first_line": "Manages canonical seed lifecycle queue",
                            }
                        ]
                    },
                    "reflections": [
                        {
                            "metadata": {
                                "file": "srt1_platform/seed_queue.py",
                                "symbol": "SCIASeedQueue",
                            },
                            "content": json.dumps({
                                "architectural_role": "CONTINUITY",
                                "risk_profile": ["LOW_RISK"],
                                "purpose": "Owns canonical queue seed lifecycle state.",
                            }),
                        }
                    ],
                }),
                encoding="utf-8",
            )

            bundler = SCIAContextBundler(str(manifest_path))
            candidates = bundler.build_recall_candidates(
                task="fix seed queue identity",
                queue_seed_id="seed_0001_queue",
                srt_anchor_id="srt_anchor_001",
            )

        self.assertGreaterEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate["queue_seed_id"], "seed_0001_queue")
        self.assertEqual(candidate["srt_anchor_id"], "srt_anchor_001")
        self.assertEqual(candidate["source_type"], "manifest")
        self.assertEqual(candidate["manifest_hash"], "manifest_123")
        self.assertEqual(candidate["freshness_state"], "fresh")
        self.assertEqual(candidate["trust_state"]["signature"], "unsigned")
        self.assertIn("queue", candidate["content"].lower())

    def test_context_bundler_recall_candidates_do_not_write_assistant_files(self):
        with tempfile.TemporaryDirectory() as repo:
            manifest_path = Path(repo) / "srt1_code_manifest.json"
            manifest_path.write_text(
                json.dumps({
                    "metadata": {"repo_path": repo},
                    "integrity": {"manifest_hash": "manifest_123"},
                    "symbol_table": {
                        "module.py": [
                            {
                                "name": "build_context",
                                "type": "function",
                                "line": 1,
                                "dependencies": [],
                                "docstring_first_line": "Build context candidates",
                            }
                        ]
                    },
                    "reflections": [],
                }),
                encoding="utf-8",
            )

            bundler = SCIAContextBundler(str(manifest_path))
            bundler.build_recall_candidates(
                task="build context candidates",
                queue_seed_id="seed_0001_queue",
            )

            forbidden = ["AGENTS.md", "CLAUDE.md", ".cursorrules", "copilot-instructions.md"]
            written = [name for name in forbidden if (Path(repo) / name).exists()]

        self.assertEqual(written, [])

    def test_engine_builds_packet_shaped_recall_handoff(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = "Recall handoff"
            engine.task_seed_id = "srt_anchor_handoff"
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            seed = engine.seed_queue.plant("Recall handoff")
            engine.seed_queue.set_srt_anchor(seed.seed_id, "srt_anchor_handoff")

            with patch.object(engine, "_fetch_recall_reflections", return_value=[
                RecallPacket.create(
                    queue_seed_id=seed.seed_id,
                    srt_anchor_id="srt_anchor_handoff",
                    source_type="external_private",
                    source_id="lesson_1",
                    content="External lesson",
                    relevance_score=0.9,
                ).to_reinjection_dict()
            ]), patch.object(engine, "_build_manifest_recall_candidates", return_value=[]):
                packets = engine._build_recall_packets(limit=3)

        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]["queue_seed_id"], seed.seed_id)
        self.assertEqual(packets[0]["srt_anchor_id"], "srt_anchor_handoff")
        self.assertEqual(packets[0]["source_type"], "external_private")

    def test_engine_includes_context_bundler_candidates_in_recall_handoff(self):
        with tempfile.TemporaryDirectory() as repo:
            manifest_path = Path(repo) / "srt1_code_manifest.json"
            manifest_path.write_text(
                json.dumps({
                    "metadata": {"repo_path": repo},
                    "integrity": {"manifest_hash": "manifest_123"},
                    "symbol_table": {
                        "module.py": [
                            {
                                "name": "RecallHandoff",
                                "type": "class",
                                "line": 1,
                                "dependencies": [],
                                "docstring_first_line": "Recall handoff candidate",
                            }
                        ]
                    },
                    "reflections": [],
                }),
                encoding="utf-8",
            )
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = "recall handoff candidate"
            engine.task_seed_id = "srt_anchor_handoff"
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            seed = engine.seed_queue.plant("recall handoff candidate")
            engine.seed_queue.set_srt_anchor(seed.seed_id, "srt_anchor_handoff")

            with patch.object(engine, "_fetch_recall_reflections", return_value=[]):
                packets = engine._build_recall_packets(limit=3)

        self.assertGreaterEqual(len(packets), 1)
        self.assertEqual(packets[0]["queue_seed_id"], seed.seed_id)
        self.assertEqual(packets[0]["srt_anchor_id"], "srt_anchor_handoff")
        self.assertEqual(packets[0]["source_type"], "manifest")

    def test_engine_generate_context_files_hands_packet_data_to_reinjector(self):
        with tempfile.TemporaryDirectory() as repo:
            Path(repo, "AGENTS.md").write_text(
                "## ⚠️ ACTIVE ENFORCEMENT (BLOCKING)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🎯 ACTIVE ALIGNMENT (GUIDANCE)\n"
                "*(runtime)*\n"
                "- old\n\n"
                "## 🧠 RELEVANT MEMORY (RECALL)\n"
                "*(runtime)*\n"
                "- old\n",
                encoding="utf-8",
            )
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = "handoff to reinjector"
            engine.port = 7483
            engine.signing_client = None
            engine.symbol_table = {}
            engine.synopsis = "Runtime map synopsis"
            engine._collect_warnings = lambda: []
            packet = RecallPacket.create(
                queue_seed_id="seed_0001_queue",
                srt_anchor_id="srt_anchor_handoff",
                source_type="manifest",
                source_id="symbol:handoff",
                content="Manifest candidate handoff",
                relevance_score=0.7,
            ).to_reinjection_dict()

            with patch.object(engine, "_build_recall_packets", return_value=[packet]):
                result = engine._generate_context_files()

            state = json.loads((Path(repo) / ".srt1" / "reinjector_state.json").read_text(encoding="utf-8"))
            agents_text = (Path(repo) / "AGENTS.md").read_text(encoding="utf-8")
            reinjection = Path(repo) / ".srt1" / "context" / "reinjection.md"
            runtime_map = Path(repo) / ".srt1" / "context" / "runtime_codebase_map.md"
            runtime_map_exists = runtime_map.exists()
            runtime_map_text = runtime_map.read_text(encoding="utf-8") if runtime_map_exists else ""

        recall_state = [p for p in state if p["mode"] == "recall"][0]
        self.assertEqual(recall_state["queue_seed_id"], "seed_0001_queue")
        self.assertEqual(recall_state["source_type"], "manifest")
        self.assertEqual(result["status"], "updated")
        self.assertIn(os.path.join(".srt1", "context", "reinjection.md"), result["files_written"])
        self.assertIn(os.path.join(".srt1", "context", "runtime_codebase_map.md"), result["files_written"])
        self.assertNotIn("Runtime Codebase Map", agents_text)
        self.assertTrue(runtime_map_exists)
        self.assertIn("Runtime map synopsis", runtime_map_text)

    def test_engine_generate_context_files_reports_runtime_reinjection_unavailable(self):
        with tempfile.TemporaryDirectory() as repo:
            Path(repo, "AGENTS.md").write_text("plain instructions only\n", encoding="utf-8")
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = "truthful context result"
            engine.port = 7483
            engine.signing_client = None
            engine.symbol_table = {}
            engine.synopsis = ""
            engine._collect_warnings = lambda: []

            with patch.object(engine, "_build_recall_packets", return_value=[]), \
                    patch("srt1_pro.reinjector.SCIAReinjector.inject_packets", return_value=False):
                result = engine._generate_context_files()

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["files_written"], [])
        self.assertEqual(result["reason"], "runtime reinjection unavailable")

    def test_recall_response_returns_packet_shape_with_queue_identity(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.task = "Recall API response"
            engine.task_seed_id = "srt_anchor_api"
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            seed = engine.seed_queue.plant("Recall API response")
            engine.seed_queue.set_srt_anchor(seed.seed_id, "srt_anchor_api")
            packet = RecallPacket.create(
                queue_seed_id=seed.seed_id,
                srt_anchor_id="srt_anchor_api",
                source_type="manifest",
                source_id="symbol:Recall",
                content="Recall API packet",
                relevance_score=0.8,
                freshness_state="fresh",
            ).to_dict()

            with patch.object(engine, "_build_manifest_recall_candidates", return_value=[packet]):
                response = engine._build_recall_response("legacy_seed", limit=1)

        self.assertEqual(response["seed_id"], seed.seed_id)
        self.assertEqual(response["queue_seed_id"], seed.seed_id)
        self.assertEqual(response["srt_anchor_id"], "srt_anchor_api")
        self.assertEqual(response["count"], 1)
        self.assertEqual(response["recalls"][0]["source_type"], "manifest")
        self.assertEqual(response["freshness_state"], "fresh")

    def test_recall_response_fails_closed_with_degraded_packet(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.task = None
        engine.task_seed_id = None
        engine.seed_queue = None

        with patch.object(engine, "_build_recall_packets", return_value=[]):
            response = engine._build_recall_response("seed_missing", limit=3)

        self.assertEqual(response["seed_id"], "seed_missing")
        self.assertEqual(response["queue_seed_id"], "seed_missing")
        self.assertEqual(response["freshness_state"], "degraded")
        self.assertEqual(response["recalls"][0]["source_type"], "recall_unavailable")
        self.assertEqual(response["recalls"][0]["trust_state"]["signature"], "unsigned")

    def test_recall_response_does_not_call_external_memory_by_default(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.task = None
        engine.task_seed_id = "queue_public_api"
        engine.seed_queue = None

        with patch.object(engine, "_fetch_recall_reflections", side_effect=AssertionError), \
                patch.object(engine, "_build_manifest_recall_candidates", return_value=[]):
            response = engine._build_recall_response("queue_public_api", limit=1)

        self.assertEqual(response["seed_id"], "queue_public_api")
        self.assertEqual(response["freshness_state"], "degraded")

    def test_recall_response_honors_requested_queue_seed(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.task = "Recall requested seed"
            engine.task_seed_id = "srt_anchor_latest"
            engine.repo_path = repo
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            first = engine.seed_queue.plant("Original active seed")
            engine.seed_queue.set_srt_anchor(first.seed_id, "srt_anchor_first")
            requested = engine.seed_queue.plant("Requested seed")
            engine.seed_queue.set_srt_anchor(requested.seed_id, "srt_anchor_requested")

            with patch.object(engine, "_build_manifest_recall_candidates", return_value=[]):
                response = engine._build_recall_response(requested.seed_id, limit=1)

        self.assertEqual(response["seed_id"], requested.seed_id)
        self.assertEqual(response["queue_seed_id"], requested.seed_id)
        self.assertEqual(response["srt_anchor_id"], "srt_anchor_requested")
        self.assertEqual(response["recalls"][0]["queue_seed_id"], requested.seed_id)

    def test_completion_by_srt_anchor_updates_canonical_queue_seed(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            engine.validator = None
            seed = engine.seed_queue.plant("Complete canonical queue seed")
            engine.seed_queue.set_srt_anchor(seed.seed_id, "srt_anchor_completion")

            engine._on_seed_completed(
                "srt_anchor_completion",
                files_modified=["example.py"],
                summary="Done",
            )
            queue_seed = engine.seed_queue.get_seed(seed.seed_id)

        self.assertEqual(queue_seed["stage"], "bloomed")
        self.assertEqual(queue_seed["completion_state"], "human_accepted")
        self.assertEqual(queue_seed["srt_anchor_id"], "srt_anchor_completion")
        self.assertIn("example.py", queue_seed["files_modified"])

    def test_completion_rejection_records_returned_for_revision(self):
        class Report:
            is_complete = False
            empty_harnesses = []

        class Validator:
            def verify_tree(self, files_to_check=None):
                return Report()

        class SRTTool:
            def __init__(self):
                self.reflections = []

            def add_reflection(self, reflection_type, content, metadata):
                self.reflections.append((reflection_type, content, metadata))

        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.seed_queue = engine_module.SCIASeedQueue(
                queue_dir=str(Path(repo) / ".srt1" / "seeds")
            )
            engine.validator = Validator()
            engine.srt_tool = SRTTool()
            seed = engine.seed_queue.plant("Rejected completion")

            engine._on_seed_completed(
                seed.seed_id,
                files_modified=[],
                summary="Done",
            )
            queue_seed = engine.seed_queue.get_seed(seed.seed_id)

        self.assertEqual(queue_seed["stage"], "planted")
        self.assertEqual(queue_seed["completion_state"], "returned_for_revision")

    def test_task_response_allows_missing_srt_anchor_id(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.task_seed_id = None
        engine.bridge = None
        engine.manifest = {}
        engine.seed_queue = None

        response = engine._build_task_response(
            task="Queue-only seed response",
            queue_seed_id="seed_0001_queue",
            auto_dispatch=False,
        )

        self.assertEqual(response["seed_id"], "seed_0001_queue")
        self.assertEqual(response["queue_seed_id"], "seed_0001_queue")
        self.assertIsNone(response["srt_anchor_id"])

    def test_legacy_fallback_when_queue_is_unavailable(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.task = None
            engine.task_seed_id = None
            engine.operations = []
            engine.injections = []
            engine.llm = None
            engine.analytics = None
            engine.manifest = {}
            engine.seed_queue = None
            engine.bridge = None

            with patch.object(engine_module, "get_template_registry", None):
                queue_seed_id = engine._plant_seed(
                    "Queue unavailable fallback",
                    source="api",
                    priority=5,
                    auto_dispatch=False,
                )

            response = engine._build_task_response(
                task="Queue unavailable fallback",
                queue_seed_id=queue_seed_id,
                auto_dispatch=False,
            )

        self.assertIsNone(queue_seed_id)
        self.assertEqual(response["seed_id"], engine.task_seed_id)
        self.assertIsNone(response["queue_seed_id"])
        self.assertEqual(response["srt_anchor_id"], engine.task_seed_id)


if __name__ == "__main__":
    unittest.main()
