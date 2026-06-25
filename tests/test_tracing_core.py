import unittest

from srt1_platform.tracing_system import SRT1TracingSystem, ExecutionGraphTracker


class TracingCoreTests(unittest.TestCase):
    def test_trace_lifecycle_stays_local_without_audit_ledger(self):
        tracing = SRT1TracingSystem()

        trace_id = tracing.create_universal_trace(
            component="indexer",
            operation="scan",
            input_data={"path": "app.py"},
            context={"llm_provider": "local"},
        )
        tracing.complete_trace(trace_id, output_data={"symbols": 1}, duration_ms=12)

        trace = tracing.get_trace(trace_id)

        self.assertEqual(trace["component"], "indexer")
        self.assertEqual(trace["operation"], "scan")
        self.assertEqual(trace["status"], "COMPLETED")
        self.assertFalse(hasattr(tracing, "audit_ledger"))

    def test_execution_graph_cell_id_is_optional_metadata(self):
        tracker = ExecutionGraphTracker()
        graph_id = tracker.start_validation_graph(
            content_hash="abc123",
            context={"queue_seed_id": "seed_1"},
            llm_provider="local",
        )

        legacy_step = tracker.add_validation_step(
            graph_id=graph_id,
            criterion_name="legacy",
            llm_provider="local",
        )
        cell_step = tracker.add_validation_step(
            graph_id=graph_id,
            criterion_name="bounded",
            llm_provider="local",
            cell_id="cell_auth",
        )

        graph = tracker.get_graph(graph_id)
        steps = {step["step_id"]: step for step in graph["steps"]}

        self.assertIsNone(steps[legacy_step]["cell_id"])
        self.assertEqual(steps[cell_step]["cell_id"], "cell_auth")


if __name__ == "__main__":
    unittest.main()
