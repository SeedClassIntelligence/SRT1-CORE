# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)
# Signed by: SeedSignature — Seed Class Intelligence

"""
DEPRECATED — Backward Compatibility Shim
==========================================
This file is deprecated. Use the jurisdictionally correct imports:

    CORE (understanding cognition):
        from srt1_platform.intelligence_adapter import IntelligenceAdapter

    Shared transport:
        from srt1_platform.llm_providers import LLMProviderRouter, LLMResponse, TokenBudget

    Private/Enterprise (transformation proposals):
        use an external TransformationAdapter integration

This shim aliases IntelligenceAdapter as SCIALLMAdapter for backward
compatibility ONLY. It does NOT expose code generation, step planning,
free-form thinking, or any transformation/execution methods. Those belong
outside public Core.

Creator: William Darnell Jernigan IV — The Original Seed
Architecture: SCIA v4.0.0 — Patent USPTO #63/827,977
"""

import warnings

warnings.warn(
    "srt1_platform.llm_adapter is deprecated. "
    "Use 'from srt1_platform.intelligence_adapter import IntelligenceAdapter' (CORE) "
    "Use an external private/Enterprise TransformationAdapter for transformation proposals.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export shared infrastructure
from srt1_platform.llm_providers import (
    LLMResponse,
    SeedIntent,
    TokenBudget,
    AnalysisCache,
    GeminiProvider,
    OpenAICompatibleProvider,
    LLMProviderRouter,
)

# CORE-only alias — IntelligenceAdapter only, no execution methods
from srt1_platform.intelligence_adapter import IntelligenceAdapter as SCIALLMAdapter

__all__ = [
    "SCIALLMAdapter",  # DEPRECATED — use IntelligenceAdapter
    "LLMResponse",
    "SeedIntent",
    "TokenBudget",
    "AnalysisCache",
    "GeminiProvider",
    "OpenAICompatibleProvider",
    "LLMProviderRouter",
]
