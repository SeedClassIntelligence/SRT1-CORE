import os
import unittest
from unittest.mock import patch

from srt1_platform.intelligence_adapter import IntelligenceAdapter
from srt1_platform.llm_providers import AnalysisCache, LLMResponse, TokenBudget


class IntelligenceAdapterTests(unittest.TestCase):
    def test_adapter_fails_closed_when_no_provider_is_configured(self):
        clean_env = {
            key: value for key, value in os.environ.items()
            if key not in {
                "GROQ_API_KEY",
                "TOGETHER_API_KEY",
                "GOOGLE_API_KEY",
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
            }
        }
        clean_env["DISABLE_OLLAMA"] = "1"

        with patch.dict(os.environ, clean_env, clear=True):
            adapter = IntelligenceAdapter()

        self.assertFalse(adapter.is_available())
        self.assertEqual(adapter.get_available_providers(), [])
        self.assertEqual(adapter.get_budget_status()["used_today"], 0)

    def test_budget_exhaustion_returns_empty_response_without_provider_call(self):
        budget = TokenBudget(daily_limit=1, used_today=1)
        with patch.dict(os.environ, {"DISABLE_OLLAMA": "1"}, clear=True):
            adapter = IntelligenceAdapter(token_budget=budget)

        response = adapter.analyze("Explain this module")

        self.assertIsInstance(response, LLMResponse)
        self.assertEqual(response.provider, "budget_exhausted")
        self.assertEqual(response.content, "")

    def test_cached_analysis_does_not_require_provider(self):
        with patch.dict(os.environ, {"DISABLE_OLLAMA": "1"}, clear=True):
            adapter = IntelligenceAdapter()

        cache_key = AnalysisCache.hash_input({"p": "Explain this module", "c": ""})
        adapter.cache.put(cache_key, "cached understanding")

        response = adapter.analyze("Explain this module")

        self.assertTrue(response.cached)
        self.assertEqual(response.provider, "cache")
        self.assertEqual(response.content, "cached understanding")

    def test_adapter_does_not_expose_transformation_methods(self):
        with patch.dict(os.environ, {"DISABLE_OLLAMA": "1"}, clear=True):
            adapter = IntelligenceAdapter()

        for method_name in ("generate_code", "plan_steps", "execute", "transform"):
            self.assertFalse(hasattr(adapter, method_name), method_name)


if __name__ == "__main__":
    unittest.main()
