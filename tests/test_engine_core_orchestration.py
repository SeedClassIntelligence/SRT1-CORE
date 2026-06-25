import unittest

from srt1_code_indexer import engine as engine_module


class FakeSigningClient:
    def sign(self, payload, phase=None, **kwargs):
        return {"signed": True, "phase": phase, "payload": payload}


class FakeLLM:
    def __init__(self):
        self.calls = []

    def enrich_roles(self, symbols):
        self.calls.append(("enrich_roles", symbols))
        return [{"name": "run", "role": "service", "risk": "LOW_RISK"}]

    def detect_semantic_overlaps(self, functions):
        self.calls.append(("detect_semantic_overlaps", functions))
        return []

    def assess_coherence(self, summary):
        self.calls.append(("assess_coherence", summary))
        return {"coherence_score": 91, "strengths": ["clear"], "risks": []}

    def summarize_module(self, source, module_name=""):
        self.calls.append(("summarize_module", module_name))
        return ""

    def build_context_insight(self, symbols, task):
        self.calls.append(("build_context_insight", task))
        return "run is relevant"

    def deep_analyze_source(self, source, file_path, ext, symbols):
        self.calls.append(("deep_analyze_source", file_path))
        return {}

    def get_budget_status(self):
        return {"used_today": 0, "remaining": 100}


class EngineCoreOrchestrationTests(unittest.TestCase):
    def test_log_event_uses_memory_cache_without_audit_ledger(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.signing_client = None
        engine._event_log = []

        engine._log_event("test", "message", {"ok": True})

        self.assertEqual(len(engine._event_log), 1)
        self.assertEqual(engine._event_log[0]["category"], "test")
        self.assertNotIn("_provenance", engine._event_log[0])

    def test_log_event_attaches_optional_signature_metadata(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.signing_client = FakeSigningClient()
        engine._event_log = []

        engine._log_event("test", "message")

        self.assertTrue(engine._event_log[0]["_provenance"]["signed"])
        self.assertEqual(engine._event_log[0]["_provenance"]["phase"], "event_log")

    def test_semantic_enrichment_is_additive_metadata(self):
        engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
        engine.llm = FakeLLM()
        engine.task = "Improve run flow"
        engine.repo_path = "."
        engine.manifest = {"metadata": {"repo_name": "demo"}}
        engine.symbol_table = {
            "app.py": [
                {
                    "name": "run",
                    "type": "function",
                    "line": 1,
                    "docstring_first_line": "Run app",
                    "dependencies": [],
                    "reflection": {"architectural_role": "GENERAL"},
                }
            ]
        }
        engine.curation_report = {"duplicate_files": [], "functional_overlaps": [], "unused_functions": []}

        engine._apply_semantic_enrichment()

        self.assertIn("semantic_enrichment", engine.manifest)
        self.assertEqual(engine.manifest["semantic_enrichment"]["_meta"]["authority"], "semantic_enrichment")
        self.assertEqual(engine.symbol_table["app.py"][0]["reflection"]["architectural_role"], "GENERAL")
        self.assertEqual(
            engine.symbol_table["app.py"][0]["semantic_enrichment"]["semantic_role"],
            "service",
        )


if __name__ == "__main__":
    unittest.main()
