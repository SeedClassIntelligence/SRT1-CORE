import json
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
                    "symbol_table": {
                        "src/auth.py": [
                            {
                                "name": "authenticate",
                                "type": "function",
                                "line": 5,
                                "dependencies": ["load_user"],
                                "reflection": {
                                    "architectural_role": "AUTHORITY",
                                    "risk_profile": ["SECURITY_CRITICAL"],
                                },
                            }
                        ]
                    },
                },
            )

            package = Path(execution.package_path)
            workcell_md = package / "workcell.md"
            runtime_state = package / "runtime_state.json"
            filecells_json = package / "filecells.json"
            content = workcell_md.read_text(encoding="utf-8")
            filecells = json.loads(filecells_json.read_text(encoding="utf-8"))
            runtime = json.loads(runtime_state.read_text(encoding="utf-8"))

            self.assertEqual(execution.queue_seed_id, "seed_0001_workcell")
            self.assertEqual(execution.srt_anchor_id, "srt_anchor_001")
            self.assertTrue(workcell_md.exists())
            self.assertTrue(runtime_state.exists())
            self.assertTrue(filecells_json.exists())
            self.assertTrue(execution.package_status["assistant_ready"])
            self.assertTrue(execution.package_status["workcell_md_exists"])
            self.assertTrue(execution.package_status["filecells_json_exists"])
            self.assertTrue(execution.package_status["runtime_state_json_exists"])
            self.assertEqual(execution.package_status["missing_files"], [])
            self.assertIn("Refactor src/auth.py safely", content)
            self.assertIn("queue_seed_id: seed_0001_workcell", content)
            self.assertIn("Do not broaden context because files are nearby.", content)
            self.assertIn("## Attached FileCell", content)
            self.assertIn("src/auth.py", content)
            self.assertEqual(filecells["filecells"][0]["path"], "src/auth.py")
            self.assertEqual(filecells["filecells"][0]["symbol_count"], 1)
            self.assertEqual(filecells["filecells"][0]["symbols"][0]["name"], "authenticate")
            self.assertIn("load_user", filecells["filecells"][0]["dependencies"])
            self.assertEqual(runtime["filecells"][0]["path"], "src/auth.py")
            self.assertTrue(runtime["execution"]["package_status"]["assistant_ready"])

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

    def test_workcell_execution_records_observable_activity(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            execution = registry.activate_execution(
                queue_seed_id="seed_0001_activity",
                objective="Observe bounded assistant work",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )

            result = registry.record_execution_event(
                queue_seed_id="seed_0001_activity",
                event_type="assistant.dispatched",
                status="running",
                actor="codex",
                message="Bounded request handed to assistant.",
                metadata={"allowed_paths": ["app.py"]},
                execution_status="dispatched",
            )
            current = registry.get_execution_for_seed("seed_0001_activity")
            runtime = json.loads(
                (Path(execution.package_path) / "runtime_state.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result["status"], "recorded")
        self.assertEqual(current["activity_events"][0]["event_type"], "execution.created")
        self.assertEqual(current["activity_events"][1]["event_type"], "assistant.dispatched")
        self.assertEqual(current["status"], "dispatched")
        self.assertEqual(current["activity_events"][1]["metadata"]["allowed_paths"], ["app.py"])
        self.assertEqual(runtime["execution"]["activity_events"], current["activity_events"])

    def test_workcell_execution_job_registry_tracks_runtime_ownership(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_job_registry",
                objective="Track assistant job",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )

            started = registry.start_execution_job(
                "seed_job_registry",
                provider="openai",
                adapter="openai_compatible",
                cancellable=True,
                hard_cancellable=False,
                metadata={"api_key": "must-not-persist"},
            )
            job_id = started["job"]["job_id"]
            updated = registry.update_execution_job(
                "seed_job_registry",
                job_id=job_id,
                status="dispatched",
                provider_acknowledged=True,
                result={"secret": "must-not-persist"},
            )
            stopped = registry.control_execution("seed_job_registry", "stop")
            current = registry.get_execution_for_seed("seed_job_registry")
            registry_text = Path(repo, ".srt1", "workcells", "workcell_registry.json").read_text(encoding="utf-8")

        self.assertEqual(started["status"], "registered")
        self.assertEqual(updated["status"], "updated")
        self.assertEqual(stopped["status"], "stop_requested")
        self.assertEqual(current["current_execution_job"]["job_id"], job_id)
        self.assertEqual(current["current_execution_job"]["provider"], "openai")
        self.assertEqual(current["current_execution_job"]["status"], "stop_requested")
        self.assertTrue(current["current_execution_job"]["stop_requested"])
        self.assertFalse(current["current_execution_job"]["hard_cancellable"])
        self.assertNotIn("must-not-persist", registry_text)
        self.assertIn("[REDACTED]", registry_text)

    def test_provider_acknowledgement_updates_current_execution_job(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_ack",
                objective="Acknowledge assistant runtime",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )
            started = registry.start_execution_job(
                "seed_ack",
                provider="openai",
                adapter="openai_compatible",
            )
            job_id = started["job"]["job_id"]
            registry.control_execution("seed_ack", "stop")

            ack = registry.acknowledge_execution_job(
                "seed_ack",
                job_id=job_id,
                acknowledgement="stopping",
                actor="provider_runtime",
                metadata={"authorization": "Bearer must-not-persist"},
            )
            stopped = registry.acknowledge_execution_job(
                "seed_ack",
                job_id=job_id,
                acknowledgement="stopped",
                actor="provider_runtime",
            )
            current = registry.get_execution_for_seed("seed_ack")
            registry_text = Path(repo, ".srt1", "workcells", "workcell_registry.json").read_text(encoding="utf-8")

        self.assertEqual(ack["status"], "acknowledged")
        self.assertEqual(ack["acknowledgement"], "stopping")
        self.assertEqual(stopped["acknowledgement"], "stopped")
        self.assertEqual(current["status"], "terminated")
        self.assertEqual(current["current_execution_job"]["acknowledgement"], "stopped")
        self.assertEqual(current["current_execution_job"]["status"], "stopped")
        self.assertTrue(current["current_execution_job"]["provider_acknowledged"])
        self.assertTrue(
            any(event["event_type"] == "execution_job.acknowledged" for event in current["activity_events"])
        )
        self.assertNotIn("must-not-persist", registry_text)
        self.assertIn("[REDACTED]", registry_text)

    def test_provider_completion_enters_human_review_lane(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_provider_complete",
                objective="Review completed provider work",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )
            started = registry.start_execution_job(
                "seed_provider_complete",
                provider="openai",
                adapter="openai_compatible",
            )

            ack = registry.acknowledge_execution_job(
                "seed_provider_complete",
                job_id=started["job"]["job_id"],
                acknowledgement="completed",
                actor="provider_runtime",
            )
            current = registry.get_execution_for_seed("seed_provider_complete")

        self.assertEqual(ack["status"], "acknowledged")
        self.assertEqual(current["status"], "awaiting_review")
        self.assertEqual(current["verification_state"], "unverified")
        self.assertEqual(current["current_execution_job"]["status"], "completed")
        self.assertTrue(current["current_execution_job"]["review_required"])
        self.assertTrue(current["current_execution_job"]["verification_required"])

    def test_old_workcell_registry_without_activity_events_still_loads(self):
        with tempfile.TemporaryDirectory() as repo:
            registry_dir = Path(repo) / ".srt1" / "workcells"
            registry_dir.mkdir(parents=True)
            registry_data = {
                "repo_path": repo,
                "workcells": [],
                "executions": [{
                    "workcell_execution_id": "wcx_seed-old",
                    "workcell_id": "workcell_repository",
                    "queue_seed_id": "seed-old",
                    "srt_anchor_id": None,
                    "objective": "Legacy execution",
                }],
            }
            (registry_dir / "workcell_registry.json").write_text(
                json.dumps(registry_data),
                encoding="utf-8",
            )

            registry = WorkCellRegistry(repo_path=repo)
            execution = registry.get_execution_for_seed("seed-old")

        self.assertIsNotNone(execution)
        self.assertEqual(execution["activity_events"], [])

    def test_activity_log_preserves_history_beyond_dashboard_window_and_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            execution = registry.activate_execution(
                queue_seed_id="seed_activity_history",
                objective="Preserve secure activity",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )
            for index in range(205):
                registry.record_execution_event(
                    "seed_activity_history",
                    event_type="test.progress",
                    status="running",
                    metadata={
                        "index": index,
                        "api_key": "must-not-persist",
                        "authorization": "Bearer secret-token",
                    },
                )

            current = registry.get_execution_for_seed("seed_activity_history")
            first_page = registry.get_execution_activity("seed_activity_history", limit=200)
            second_page = registry.get_execution_activity(
                "seed_activity_history",
                limit=200,
                offset=200,
            )
            activity_text = (
                Path(execution.package_path) / "activity.jsonl"
            ).read_text(encoding="utf-8")

        self.assertEqual(len(current["activity_events"]), 200)
        self.assertEqual(first_page["total"], 206)
        self.assertEqual(len(first_page["events"]), 200)
        self.assertEqual(len(second_page["events"]), 6)
        self.assertNotIn("must-not-persist", activity_text)
        self.assertNotIn("secret-token", activity_text)
        self.assertIn("[REDACTED]", activity_text)

    def test_workcell_controls_are_isolated_and_approval_fails_closed(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_controls",
                objective="Control one WorkCell",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )

            blocked = registry.control_execution("seed_controls", "approve")
            paused = registry.control_execution("seed_controls", "pause")
            resumed = registry.control_execution("seed_controls", "resume")
            stopped = registry.control_execution("seed_controls", "stop")
            cancelled = registry.control_execution("seed_controls", "cancel")
            current = registry.get_execution_for_seed("seed_controls")

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(paused["status"], "pause_requested")
        self.assertEqual(resumed["status"], "running")
        self.assertEqual(stopped["status"], "stop_requested")
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(current["status"], "cancelled")
        self.assertTrue(
            any(event["event_type"] == "execution.cancel" for event in current["activity_events"])
        )
        self.assertTrue(
            any(
                event["event_type"] == "execution.stop"
                and event["metadata"].get("requires_runtime_ack") is True
                for event in current["activity_events"]
            )
        )

    def test_workcell_write_guard_allows_only_owned_paths(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_write_guard",
                objective="Update src/auth.py",
                manifest={
                    "file_manifest": [
                        {"file_path": "src/auth.py"},
                        {"file_path": "src/billing.py"},
                    ],
                },
            )

            allowed = registry.validate_execution_writes(
                "seed_write_guard",
                ["src/auth.py"],
            )
            blocked = registry.validate_execution_writes(
                "seed_write_guard",
                ["src/billing.py"],
            )
            escaped = registry.validate_execution_writes(
                "seed_write_guard",
                ["../outside.py"],
            )
            current = registry.get_execution_for_seed("seed_write_guard")

        self.assertTrue(allowed["allowed"])
        self.assertEqual(allowed["approved_paths"], ["src/auth.py"])
        self.assertFalse(blocked["allowed"])
        self.assertEqual(blocked["violations"][0]["path"], "src/billing.py")
        self.assertFalse(escaped["allowed"])
        self.assertEqual(escaped["violations"][0]["path"], "../outside.py")
        self.assertEqual(current["status"], "returned")
        self.assertTrue(
            any(event["event_type"] == "boundary.write_blocked" for event in current["activity_events"])
        )

    def test_workcell_package_repair_regenerates_missing_filecells_json(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            execution = registry.activate_execution(
                queue_seed_id="seed_0001_repair",
                objective="Repair package",
                manifest={
                    "integrity": {"manifest_hash": "manifest_123"},
                    "file_manifest": [{"file_path": "src/auth.py"}],
                    "symbol_table": {
                        "src/auth.py": [
                            {
                                "name": "authenticate",
                                "type": "function",
                                "line": 5,
                                "dependencies": [],
                            }
                        ]
                    },
                },
            )
            filecells_json = Path(execution.package_path) / "filecells.json"
            filecells_json.unlink()

            degraded = registry.get_execution_for_seed("seed_0001_repair")
            result = registry.repair_execution_package("seed_0001_repair")

        self.assertFalse(degraded["package_status"]["assistant_ready"])
        self.assertIn("filecells_json", degraded["package_status"]["missing_files"])
        self.assertEqual(result["status"], "repaired")
        self.assertTrue(result["after"]["assistant_ready"])
        self.assertTrue(result["after"]["filecells_json_exists"])

    def test_workcell_md_preview_reads_generated_entry_instructions(self):
        with tempfile.TemporaryDirectory() as repo:
            registry = WorkCellRegistry(repo_path=repo)
            registry.activate_execution(
                queue_seed_id="seed_0001_preview",
                srt_anchor_id="srt_anchor_preview",
                objective="Preview WorkCell instructions",
                manifest={
                    "integrity": {"manifest_hash": "manifest_123"},
                    "file_manifest": [{"file_path": "src/auth.py"}],
                },
            )

            preview = registry.read_workcell_md("seed_0001_preview")

        self.assertEqual(preview["status"], "ok")
        self.assertEqual(preview["queue_seed_id"], "seed_0001_preview")
        self.assertIn("Preview WorkCell instructions", preview["content"])
        self.assertIn("## Operating Rule", preview["content"])
        self.assertIn("queue_seed_id: seed_0001_preview", preview["content"])

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
        self.assertTrue(status["executions"][0]["package_status"]["assistant_ready"])
        self.assertTrue(status["executions"][0]["package_status"]["workcell_md_exists"])
        self.assertTrue(status["executions"][0]["package_status"]["filecells_json_exists"])

    def test_engine_validates_workcell_writes_through_registry(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.workcell_registry.activate_execution(
                queue_seed_id="seed_engine_guard",
                objective="Update app.py",
                manifest={
                    "file_manifest": [
                        {"file_path": "app.py"},
                        {"file_path": "other.py"},
                    ]
                },
            )

            allowed = engine._validate_workcell_writes("seed_engine_guard", ["app.py"])
            blocked = engine._validate_workcell_writes("seed_engine_guard", ["other.py"])

        self.assertTrue(allowed["allowed"])
        self.assertFalse(blocked["allowed"])
        self.assertEqual(blocked["status"], "blocked")


    def test_engine_workcell_dispatch_guard_blocks_cancelled_or_unscoped_runs(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.workcell_registry.activate_execution(
                queue_seed_id="seed_dispatch_guard",
                objective="Update app.py",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )

            allowed = engine._check_workcell_dispatch_guard("seed_dispatch_guard", ["app.py"])
            unscoped = engine._check_workcell_dispatch_guard("seed_dispatch_guard", [])
            engine.workcell_registry.control_execution("seed_dispatch_guard", "cancel")
            cancelled = engine._check_workcell_dispatch_guard("seed_dispatch_guard", ["app.py"])

        self.assertTrue(allowed["allowed"])
        self.assertFalse(unscoped["allowed"])
        self.assertIn("validated WorkCell write scope", unscoped["reason"])
        self.assertFalse(cancelled["allowed"])
        self.assertEqual(cancelled["execution_status"], "cancelled")

    def test_engine_resolves_allowed_paths_from_selected_workcell(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            execution = engine.workcell_registry.activate_execution(
                queue_seed_id="seed_dispatch_scope",
                objective="Update tests/test_assistant_adapter_surfaces.py",
                manifest={
                    "file_manifest": [
                        {"file_path": "tests/test_assistant_adapter_surfaces.py"},
                        {"file_path": "srt1_code_indexer/engine.py"},
                    ]
                },
            ).to_dict()

            allowed_paths = engine._get_workcell_allowed_paths(execution)

        self.assertEqual(allowed_paths, ["tests/test_assistant_adapter_surfaces.py"])

    def test_blueprint_filename_is_safe_when_seed_mentions_path(self):
        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.llm = None
            engine.symbol_table = {}
            engine.curation_report = {}
            engine.manifest = {"file_manifest": []}

            result = engine.generate_blueprint(
                "Resolve tests/test_assistant_adapter_surfaces.py provider smoke"
            )

            blueprint_path = Path(result["saved_to"])
            relative = blueprint_path.relative_to(Path(repo) / ".srt1")

        self.assertEqual(len(relative.parts), 1)
        self.assertTrue(blueprint_path.name.startswith("blueprint_resolve_tests_test_assistant"))

    def test_engine_reviews_change_proposal_and_records_workcell_timeline(self):
        from srt1_platform.change_proposal import ChangeProposalStore

        with tempfile.TemporaryDirectory() as repo:
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.workcell_registry.activate_execution(
                queue_seed_id="seed_proposal_review",
                objective="Review provider proposal",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )
            store = ChangeProposalStore(repo_path=repo)
            record = store.create_from_provider_result(
                queue_seed_id="seed_proposal_review",
                objective="Review provider proposal",
                provider_result={"proposed_changes": [{"file_path": "app.py", "action": "MODIFY"}]},
                allowed_paths=["app.py"],
            )

            result = engine._review_change_proposal(
                record["proposal"]["proposal_id"],
                action="approve",
                actor="test",
            )
            current = engine.workcell_registry.get_execution_for_seed("seed_proposal_review")

        self.assertEqual(result["status"], "approved")
        self.assertFalse(result["applied"])
        self.assertTrue(
            any(event["event_type"] == "change_proposal.approve" for event in current["activity_events"])
        )


    def test_engine_applies_approved_change_proposal_through_workcell_guard(self):
        from srt1_platform.change_proposal import ChangeProposalStore

        with tempfile.TemporaryDirectory() as repo:
            app = Path(repo) / "app.py"
            other = Path(repo) / "other.py"
            app.write_text("old = True\n", encoding="utf-8")
            other.write_text("other = True\n", encoding="utf-8")
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.workcell_registry.activate_execution(
                queue_seed_id="seed_apply_guard",
                objective="Update app.py",
                manifest={"file_manifest": [{"file_path": "app.py"}, {"file_path": "other.py"}]},
            )
            store = ChangeProposalStore(repo_path=repo)
            record = store.create_from_provider_result(
                queue_seed_id="seed_apply_guard",
                objective="Update app.py",
                provider_result={"proposed_changes": [{"file_path": "app.py", "action": "MODIFY", "new_content": "new = True\n"}]},
                allowed_paths=["app.py"],
            )
            proposal_id = record["proposal"]["proposal_id"]
            store.review_proposal(proposal_id, action="approve")

            result = engine._apply_change_proposal(proposal_id, actor="test")
            current = engine.workcell_registry.get_execution_for_seed("seed_apply_guard")

            self.assertEqual(result["status"], "completed")
            self.assertEqual(app.read_text(encoding="utf-8"), "new = True\n")
            self.assertEqual(other.read_text(encoding="utf-8"), "other = True\n")
            self.assertTrue(
            any(event["event_type"] == "change_proposal.apply" for event in current["activity_events"])
            )

    def test_dashboard_contains_workcell_operations_surface(self):
        dashboard = Path(__file__).resolve().parents[1] / "srt1_platform" / "pwa" / "dashboard.html"
        html = dashboard.read_text(encoding="utf-8")

        self.assertIn("WorkCell Operations", html)
        self.assertIn("workcellList", html)
        self.assertIn("/api/v1/workcells", html)
        self.assertIn("renderWorkCells", html)
        self.assertIn("Attached FileCell", html)
        self.assertIn("filecell_summary", html)
        self.assertIn("workcell-filecell-grid", html)
        self.assertIn("workcellDetail", html)
        self.assertIn("selectWorkCellDetail", html)
        self.assertIn("renderWorkCellDetail", html)
        self.assertIn("workcell-detail-grid", html)
        self.assertIn("data-workcell-execution-id", html)
        self.assertIn('role="button"', html)
        self.assertIn("Core Help", html)
        self.assertIn("dismissIntroModal", html)
        self.assertIn("srt1DashboardIntroDismissed", html)
        self.assertIn("getDashboardPreference", html)
        self.assertIn("setDashboardPreference", html)
        self.assertIn("Package Actions", html)
        self.assertIn("assistant_ready", html)
        self.assertIn("copyWorkCellPackagePath", html)
        self.assertIn("Copy package path", html)
        self.assertIn("repairWorkCellPackage", html)
        self.assertIn("Repair package", html)
        self.assertIn("repair-package", html)
        self.assertIn("loadWorkCellMdPreview", html)
        self.assertIn("workcell.md Preview", html)
        self.assertIn("package/workcell-md", html)
        self.assertIn("Execution Timeline", html)
        self.assertIn("Change Proposals", html)
        self.assertIn("loadWorkCellProposals", html)
        self.assertIn("reviewChangeProposal", html)
        self.assertIn("applyChangeProposal", html)
        self.assertIn("/apply", html)
        self.assertIn("/api/v1/change-proposals/", html)
        self.assertIn("loadWorkCellActivity", html)
        self.assertIn("exportWorkCellActivity", html)
        self.assertIn("controlWorkCell", html)
        self.assertIn("/activity?limit=50", html)
        self.assertIn("/action", html)
        self.assertIn("Cancel WorkCell", html)
        self.assertIn("Request stop", html)
        self.assertIn("validate-writes", html)
        self.assertIn("/ack", html)
        self.assertIn("Run with Assistant", html)
        self.assertIn("Execution Control Truth", html)
        self.assertIn("getWorkCellExecutionControlTruth", html)
        self.assertIn("hard cancellable", html)
        self.assertIn("cooperative controls", html)
        self.assertIn("soft stop requested", html)
        self.assertIn("job state", html)
        self.assertIn("current_execution_job", html)
        self.assertIn("provider ack", html)
        self.assertIn("job handle", html)
        self.assertIn("describeWorkCellActivityEvent", html)
        self.assertIn("Stop requested", html)
        self.assertIn("Provider stopping", html)
        self.assertIn("Provider stopped", html)
        self.assertIn("provider stopped", html)
        self.assertIn("Provider Completion Review", html)
        self.assertIn("getProviderCompletionReviewState", html)
        self.assertIn("ready for human decision", html)
        self.assertIn("review required", html)
        self.assertIn("inspect Change Proposals below", html)
        self.assertIn("Provider Execution Readiness", html)
        self.assertIn("getProviderExecutionReadiness", html)
        self.assertIn("workcell-provider-readiness", html)
        self.assertIn("provider adapter", html)
        self.assertIn("session key", html)
        self.assertIn("endpoint/model", html)
        self.assertIn("write scope", html)
        self.assertIn("runtime state", html)
        self.assertIn("runWorkCellWithAssistant", html)
        self.assertIn("dashboard_workcell", html)
        self.assertIn("buildAssistantCredentialPayload", html)


if __name__ == "__main__":
    unittest.main()
