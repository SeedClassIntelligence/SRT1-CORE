# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)
# Signed by: SeedSignature — Seed Class Intelligence
# Architecture: SCIA v4.0.0 — Patent USPTO #63/827,977

"""
Intelligence Adapter — CORE Understanding Cognition
=====================================================
Asks: 'What does this mean?'
Never asks: 'What should be done?'

This adapter provides model-assisted intelligence extraction for SRT-1 CORE.
It analyzes, classifies, enriches, and assesses — it never generates code,
plans execution steps, or proposes transformations.

Allowed operations:
  - analyze()                  — semantic analysis, synopsis, drift
  - classify_intent()          — structured intent classification
  - enrich_roles()             — infer architectural roles
  - detect_semantic_overlaps() — find semantic duplicates
  - assess_coherence()         — architectural health assessment
  - summarize_module()         — module cognitive summary
  - build_context_insight()    — semantic context ranking

Forbidden:
  - No transformation or execution methods
  - No execution identity or execution language
  - No file writes, command execution, or state mutation

Creator: William Darnell Jernigan IV — The Original Seed
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from srt1_platform.llm_providers import (
    LLMProviderRouter,
    LLMResponse,
    SeedIntent,
    TokenBudget,
    AnalysisCache,
)

logger = logging.getLogger("scia.intelligence")


class IntelligenceAdapter:
    """
    CORE understanding cognition.

    Asks: 'What does this mean?'
    Produces: intelligence enrichment, classifications, assessments.
    Cannot: generate code, plan execution steps, propose transformations.
    """

    # Understanding cognition prompt — analysis and mapping only
    UNDERSTANDING_PROMPT = """You are SRT-1 (Seed Reflection Tracing), the structural
intelligence layer of the SCIA platform built by Seed Class Intelligence.

Your role:
- ANALYZE codebases — understand architecture, detect patterns, explain drift
- CLASSIFY developer intent from natural language
- SUMMARIZE modules and components semantically
- ASSESS architectural coherence and health
- EXTRACT methodology, patterns, and structural wisdom
- You produce UNDERSTANDING — never code, execution plans, or patches
- Outputs may carry trust metadata or external signatures when configured

When analyzing:
- Focus on architectural patterns, purpose, and relationships
- Identify risks, dependencies, and design decisions
- Be concise and precise — never fabricate

Creator: William Darnell Jernigan IV — The Original Seed
Architecture: SCIA v4.0.0 — Patent USPTO #63/827,977"""

    def __init__(self, consumer_keys: Optional[Dict[str, str]] = None,
                 token_budget: Optional[TokenBudget] = None):
        self._router = LLMProviderRouter(
            consumer_keys=consumer_keys,
            token_budget=token_budget,
        )
        self.budget = self._router.budget
        self.cache = self._router.cache

    def get_available_providers(self) -> List[str]:
        return self._router.get_available_providers()

    def is_available(self) -> bool:
        return self._router.is_available()

    def get_budget_status(self) -> Dict[str, Any]:
        return self._router.get_budget_status()

    # ── Understanding Cognition Methods ────────────────────────────────

    def analyze(self, prompt: str, context: str = "",
                provider: str = "auto", **kwargs) -> LLMResponse:
        """Semantic analysis — synopsis, drift, understanding.
        Cached by input hash — repeated calls with same data cost zero tokens."""
        cache_key = AnalysisCache.hash_input({"p": prompt, "c": context[:500]})
        cached = self.cache.get(cache_key)
        if cached:
            return LLMResponse(
                content=cached, provider="cache", model="cache",
                tokens_used=0, latency_ms=0, cached=True,
            )

        if not self.budget.can_spend(3000):
            return LLMResponse(
                content="", provider="budget_exhausted", model="none",
                tokens_used=0, latency_ms=0,
            )

        messages = [{"role": "system", "content": self.UNDERSTANDING_PROMPT}]
        if context:
            messages.append({"role": "user", "content": f"Context:\n{context}"})
            messages.append({"role": "assistant", "content": "Understood. I have the context."})
        messages.append({"role": "user", "content": prompt})

        response = self._router.route(messages, provider, preferred="groq", **kwargs)
        self.budget.spend(response.tokens_used)
        self.cache.put(cache_key, response.content)
        return response

    def classify_intent(self, text: str, provider: str = "auto") -> SeedIntent:
        """Classify natural language into a structured SeedIntent."""
        cache_key = AnalysisCache.hash_input({"classify": text})
        cached = self.cache.get(cache_key)
        if cached and isinstance(cached, dict):
            return SeedIntent(**cached)

        prompt = f"""Classify this developer request into a structured intent.

Request: "{text}"

Respond in JSON format ONLY (no markdown, no explanation):
{{
    "action": "plant_seed|fix_bug|add_feature|generate_docs|refactor|analyze|ask_question",
    "title": "short title (max 80 chars)",
    "description": "what needs to be done",
    "priority": "low|medium|high|critical",
    "domains": ["backend", "frontend", "database", "api", "testing", "devops"],
    "files_likely": ["path/to/file.py"],
    "steps": ["step 1", "step 2", "step 3"],
    "confidence": 0.85
}}"""

        messages = [
            {"role": "system", "content": self.UNDERSTANDING_PROMPT},
            {"role": "user", "content": prompt},
        ]
        response = self._router.route(messages, provider, preferred="groq",
                                      temperature=0.1, max_tokens=1024)
        self.budget.spend(response.tokens_used)

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            data = json.loads(content)
            intent = SeedIntent(
                action=data.get("action", "plant_seed"),
                title=data.get("title", text[:80]),
                description=data.get("description", text),
                priority=data.get("priority", "medium"),
                domains=data.get("domains", []),
                files_likely=data.get("files_likely", []),
                steps=data.get("steps", []),
                confidence=data.get("confidence", 0.5),
            )
            self.cache.put(cache_key, data)
            return intent
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse intent classification: {e}")
            return SeedIntent(
                action="plant_seed", title=text[:80], description=text,
                priority="medium", domains=[], files_likely=[],
                steps=[], confidence=0.3,
            )

    def enrich_roles(self, symbol_data: List[Dict], provider: str = "auto") -> List[Dict]:
        """Infer architectural roles from function/class signatures and bodies.
        Returns enrichment proposals — caller decides whether to apply."""
        if not symbol_data:
            return []
        summaries = []
        for s in symbol_data[:20]:
            summaries.append(f"{s.get('type','?')} {s.get('name','?')}: {s.get('docstring','')[:100]}")
        prompt = (
            "For each symbol below, infer its architectural role "
            "(controller, model, utility, service, test, config, middleware) "
            "and risk profile (auth, exec, file-io, network, none).\n\n"
            + "\n".join(summaries) +
            "\n\nRespond in JSON: [{\"name\": ..., \"role\": ..., \"risk\": ...}]"
        )
        response = self.analyze(prompt, provider=provider, max_tokens=1024)
        if response.cached or response.provider == "budget_exhausted":
            return []
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(content)
        except (json.JSONDecodeError, KeyError):
            return []

    def detect_semantic_overlaps(self, functions: List[Dict],
                                  provider: str = "auto") -> List[Dict]:
        """Detect semantic duplicates beyond pattern matching.
        Returns overlap proposals — caller validates."""
        if len(functions) < 2:
            return []
        descs = [f"{f.get('name','?')}: {f.get('docstring','')[:80]}" for f in functions[:30]]
        prompt = (
            "Identify semantically overlapping functions (same purpose, different names).\n\n"
            + "\n".join(descs) +
            '\n\nRespond in JSON: [{"group": [...names], "reason": "..."}]'
        )
        response = self.analyze(prompt, provider=provider, max_tokens=1024)
        if response.cached or response.provider == "budget_exhausted":
            return []
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(content)
        except (json.JSONDecodeError, KeyError):
            return []

    def assess_coherence(self, manifest_summary: str,
                          provider: str = "auto") -> Dict[str, Any]:
        """Assess architectural health and detect drift.
        Returns assessment — caller decides what to act on."""
        prompt = (
            "Assess the architectural coherence of this codebase.\n\n"
            f"{manifest_summary}\n\n"
            "Respond in JSON: {\"coherence_score\": 0-100, \"strengths\": [...], "
            "\"risks\": [...], \"drift_indicators\": [...], \"recommendations\": [...]}"
        )
        response = self.analyze(prompt, provider=provider, max_tokens=1024)
        if response.cached or response.provider == "budget_exhausted":
            return {"coherence_score": 0, "error": "unavailable"}
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(content)
        except (json.JSONDecodeError, KeyError):
            return {"coherence_score": 0, "error": "parse_failed"}

    def summarize_module(self, module_source: str, module_name: str = "",
                          provider: str = "auto") -> str:
        """Produce cognitive summary of a module's purpose and structure."""
        prompt = (
            f"Summarize the purpose, architecture, and key components of "
            f"{'module ' + module_name if module_name else 'this module'}. "
            f"Be concise (3-5 sentences). Focus on what it does and why it exists."
        )
        response = self.analyze(prompt, context=module_source[:3000],
                                provider=provider, max_tokens=512)
        return response.content if response.content else ""

    def build_context_insight(self, symbols: List[Dict], task: str,
                               provider: str = "auto") -> str:
        """Rank symbol relevance semantically for context bundling.
        Returns ranked assessment — caller uses for context selection."""
        names = [s.get("name", "?") for s in symbols[:30]]
        prompt = (
            f"Task: {task}\n\n"
            f"Available symbols: {', '.join(names)}\n\n"
            "Rank the top 10 most relevant symbols for this task and explain why. "
            "Focus on architectural relevance, not keyword matching."
        )
        response = self.analyze(prompt, provider=provider, max_tokens=1024)
        return response.content if response.content else ""

    # ================================================================
    # DEEP SOURCE ANALYSIS — LLM-Enhanced Parsing for Non-Python
    # ================================================================
    # Added: Phase D — Language Coverage Expansion
    # This method sends non-Python source code to the LLM for real
    # semantic understanding that regex pattern matching cannot provide.
    # It respects TokenBudget and AnalysisCache for cost control.
    # Falls back to empty dict if LLM unavailable — caller keeps regex.
    # ================================================================

    # Language-specific extraction prompts
    _LANG_NAMES = {
        ".js": "JavaScript", ".jsx": "JavaScript (JSX)",
        ".ts": "TypeScript", ".tsx": "TypeScript (TSX)",
        ".go": "Go", ".rs": "Rust", ".java": "Java",
        ".cs": "C#", ".c": "C", ".cpp": "C++", ".h": "C/C++ Header",
        ".html": "HTML", ".css": "CSS",
    }

    def deep_analyze_source(self, source: str, file_path: str,
                             extension: str, regex_symbols: List[Dict],
                             provider: str = "auto") -> Dict[str, Any]:
        """
        LLM-enhanced deep analysis of non-Python source code.

        Takes regex-extracted symbols as a starting point, then asks
        the LLM to:
        1. Identify missed functions/classes/exports the regex missed
        2. Map real dependency chains between symbols
        3. Infer architectural purpose for each symbol
        4. Classify risk profile from actual code patterns
        5. Detect patterns regex can't catch (closures, generics, macros)

        Returns enriched symbol list — caller merges with regex results.
        Falls back to empty dict if LLM unavailable or budget exhausted.

        This is UNDERSTANDING cognition only — no code generation,
        no execution planning, no transformation proposals.
        """
        if not source or not source.strip():
            return {}

        lang_name = self._LANG_NAMES.get(extension, extension)

        # Build the known symbols summary from regex extraction
        known_names = [s.get("name", "?") for s in regex_symbols[:30]]
        known_summary = ", ".join(known_names) if known_names else "(none detected)"

        # Truncate source to avoid token explosion
        source_excerpt = source[:4000]

        prompt = (
            f"Analyze this {lang_name} source file: {file_path}\n\n"
            f"Regex already found these symbols: {known_summary}\n\n"
            f"Source code:\n```\n{source_excerpt}\n```\n\n"
            "Respond in JSON with this structure:\n"
            "{\n"
            '  "missed_symbols": [{"name": "...", "type": "function|class|export|const", "line": N}],\n'
            '  "dependency_chains": [{"from": "funcA", "calls": ["funcB", "funcC"]}],\n'
            '  "architectural_purpose": "one-sentence summary of this file\'s role",\n'
            '  "risk_tags": ["FILE_IO", "AUTH_SENSITIVE", ...],\n'
            '  "enriched_symbols": [\n'
            '    {"name": "...", "type": "function|class", "purpose": "brief description", '
            '"dependencies": ["..."], "risk": ["LOW_RISK"]}\n'
            '  ]\n'
            "}\n\n"
            "Rules:\n"
            "- Only include symbols actually in the source code\n"
            "- Risk tags: LOW_RISK, FILE_IO, AUTH_SENSITIVE, EXTERNAL_API_CALL, "
            "WRITES_TO_DB, DYNAMIC_EXECUTION, SYSTEM_SIDE_EFFECT, HAS_LOGGING\n"
            "- Be precise — no hallucinated symbols\n"
            "- Return valid JSON only, no markdown"
        )

        try:
            response = self.analyze(
                prompt, provider=provider, max_tokens=2048
            )
            if not response.content:
                return {}

            # Parse JSON from LLM response
            content = response.content.strip()
            # Strip markdown code fence if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            result = json.loads(content)
            logger.info(
                "Deep analysis of %s (%s): found %d enriched symbols, %d missed",
                file_path, lang_name,
                len(result.get("enriched_symbols", [])),
                len(result.get("missed_symbols", []))
            )
            return result

        except json.JSONDecodeError as e:
            logger.warning("Deep analysis JSON parse error for %s: %s", file_path, e)
            return {}
        except Exception as e:
            logger.warning("Deep analysis failed for %s: %s", file_path, e)
            return {}
