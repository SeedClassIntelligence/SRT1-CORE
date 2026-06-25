# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)
# Signed by: SeedSignature — Seed Class Intelligence
# Architecture: SCIA v4.0.0 — Patent USPTO #63/827,977

"""
LLM Provider Infrastructure — Shared Transport Layer
======================================================
Pure provider transport. No identity. No doctrine prompts.
No cognition methods. No SRT-1 language. No executor-specific language.

This layer is jurisdiction-neutral infrastructure. It does not know which
authority or product tier is calling it.

Creator: William Darnell Jernigan IV — The Original Seed
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional

logger = logging.getLogger("scia.llm")


# ═══════════════════════════════════════════════════════════════════════════
# COST CONTROL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TokenBudget:
    """Hard daily cap on LLM token usage. Prevents surprise bills.

    When exhausted, the adapter signals callers to fall back to
    deterministic methods. Resets at midnight.
    """
    daily_limit: int = 100_000
    used_today: int = 0
    _reset_date: str = ""

    def _check_reset(self):
        today = date.today().isoformat()
        if self._reset_date != today:
            self.used_today = 0
            self._reset_date = today

    def can_spend(self, estimated_tokens: int) -> bool:
        self._check_reset()
        return (self.used_today + estimated_tokens) <= self.daily_limit

    def spend(self, actual_tokens: int):
        self._check_reset()
        self.used_today += actual_tokens

    def remaining(self) -> int:
        self._check_reset()
        return max(0, self.daily_limit - self.used_today)

    def usage_pct(self) -> float:
        self._check_reset()
        return (self.used_today / self.daily_limit) * 100 if self.daily_limit else 0


@dataclass
class AnalysisCache:
    """Hash-based cache for LLM results. Zero tokens on cache hit."""
    _cache: Dict[str, Any] = field(default_factory=dict)
    _max_entries: int = 50

    def get(self, input_hash: str) -> Optional[Any]:
        entry = self._cache.get(input_hash)
        if entry:
            entry["hits"] = entry.get("hits", 0) + 1
            return entry["result"]
        return None

    def put(self, input_hash: str, result: Any):
        if len(self._cache) >= self._max_entries:
            least = min(self._cache, key=lambda k: self._cache[k].get("hits", 0))
            del self._cache[least]
        self._cache[input_hash] = {"result": result, "hits": 0, "ts": time.time()}

    def invalidate(self, input_hash: str):
        self._cache.pop(input_hash, None)

    def clear(self):
        self._cache.clear()

    @staticmethod
    def hash_input(data: Any) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    provider: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    raw_response: Optional[Dict[str, Any]] = None
    cached: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "cached": self.cached,
        }


@dataclass
class SeedIntent:
    """Classified intent from a natural language seed description."""
    action: str
    title: str
    description: str
    priority: str
    domains: List[str]
    files_likely: List[str]
    steps: List[str]
    confidence: float


# ═══════════════════════════════════════════════════════════════════════════
# PROVIDER IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════

class _BaseProvider:
    """Base class for LLM providers."""
    name: str = "base"
    model: str = "unknown"

    def is_available(self) -> bool:
        return False

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        raise NotImplementedError


class GeminiProvider(_BaseProvider):
    """Google Gemini API provider."""
    name = "gemini"

    def __init__(self, api_key: str = "", model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        import urllib.request

        start = time.time()
        contents = []
        system_instruction = None
        for msg in messages:
            role = msg["role"]
            if role == "system":
                system_instruction = msg["content"]
                continue
            gemini_role = "user" if role == "user" else "model"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": msg["content"]}]
            })

        payload: Dict[str, Any] = {"contents": contents}
        if system_instruction:
            payload["system_instruction"] = {"parts": [{"text": system_instruction}]}
        payload["generationConfig"] = {
            "temperature": kwargs.get("temperature", 0.3),
            "maxOutputTokens": kwargs.get("max_tokens", 4096),
        }

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "User-Agent": "SCIA-Provider/2.0",
        })

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())

        content = ""
        if "candidates" in result and result["candidates"]:
            parts = result["candidates"][0].get("content", {}).get("parts", [])
            content = "".join(p.get("text", "") for p in parts)

        tokens = result.get("usageMetadata", {}).get("totalTokenCount", 0)
        latency = (time.time() - start) * 1000

        return LLMResponse(
            content=content, provider="gemini", model=self.model,
            tokens_used=tokens, latency_ms=latency, raw_response=result,
        )


class OpenAICompatibleProvider(_BaseProvider):
    """Provider for any OpenAI-compatible API (Groq, Together, Ollama, etc.)."""

    def __init__(self, name: str, base_url: str, api_key: str = "",
                 model: str = "llama-3.3-70b-versatile"):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def is_available(self) -> bool:
        if self.name == "ollama":
            try:
                import urllib.request
                urllib.request.urlopen(f"{self.base_url}/v1/models", timeout=2)
                return True
            except Exception:
                return False
        return bool(self.api_key)

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        import urllib.request

        start = time.time()
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        url = f"{self.base_url}/v1/chat/completions"
        data = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SCIA-Provider/2.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())

        content = result["choices"][0]["message"]["content"]
        tokens = result.get("usage", {}).get("total_tokens", 0)
        latency = (time.time() - start) * 1000

        return LLMResponse(
            content=content, provider=self.name,
            model=result.get("model", self.model),
            tokens_used=tokens, latency_ms=latency, raw_response=result,
        )


# ═══════════════════════════════════════════════════════════════════════════
# LLM PROVIDER ROUTER — JURISDICTION-NEUTRAL TRANSPORT
# ═══════════════════════════════════════════════════════════════════════════

class LLMProviderRouter:
    """
    Pure provider routing. No identity. No doctrine.
    Accepts messages, returns LLMResponse. Does not know the caller.
    """

    def __init__(self, consumer_keys: Optional[Dict[str, str]] = None,
                 token_budget: Optional[TokenBudget] = None):
        self._providers: Dict[str, _BaseProvider] = {}
        self._provider_order: List[str] = []
        self._consumer_keys = consumer_keys or {}
        self.budget = token_budget or TokenBudget()
        self.cache = AnalysisCache()
        self._init_providers()

    def _init_providers(self):
        """Initialize all configured providers. Consumer keys override env vars."""
        ck = self._consumer_keys

        # 1. Groq (primary — fast LPU, free tier)
        groq_key = ck.get("groq", "") or os.getenv("GROQ_API_KEY", "")
        if groq_key:
            self._providers["groq"] = OpenAICompatibleProvider(
                name="groq", base_url="https://api.groq.com/openai",
                api_key=groq_key, model="llama-3.3-70b-versatile",
            )
            self._provider_order.append("groq")
            src = "BYOK" if ck.get("groq") else "server"
            logger.info(f"LLM Provider: Groq initialized ({src})")

        # 2. Together.ai (Qwen Coder — best for code generation)
        together_key = ck.get("together", "") or os.getenv("TOGETHER_API_KEY", "")
        if together_key:
            self._providers["together"] = OpenAICompatibleProvider(
                name="together", base_url="https://api.together.xyz",
                api_key=together_key,
                model="Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8",
            )
            self._provider_order.append("together")
            src = "BYOK" if ck.get("together") else "server"
            logger.info(f"LLM Provider: Together.ai initialized ({src})")

        # 3. Gemini (BYOK)
        gemini_key = ck.get("google", "") or os.getenv("GOOGLE_API_KEY", "")
        if gemini_key:
            self._providers["gemini"] = GeminiProvider(api_key=gemini_key)
            self._provider_order.append("gemini")
            src = "BYOK" if ck.get("google") else "server"
            logger.info(f"LLM Provider: Gemini initialized ({src})")

        # 4. OpenAI (BYOK)
        openai_key = ck.get("openai", "") or os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            self._providers["openai"] = OpenAICompatibleProvider(
                name="openai", base_url="https://api.openai.com",
                api_key=openai_key, model="gpt-4o",
            )
            self._provider_order.append("openai")
            src = "BYOK" if ck.get("openai") else "server"
            logger.info(f"LLM Provider: OpenAI initialized ({src})")

        # 5. Anthropic (BYOK)
        anthropic_key = ck.get("anthropic", "") or os.getenv("ANTHROPIC_API_KEY", "")
        if anthropic_key:
            self._providers["anthropic"] = OpenAICompatibleProvider(
                name="anthropic", base_url="https://api.anthropic.com",
                api_key=anthropic_key, model="claude-sonnet-4-20250514",
            )
            self._provider_order.append("anthropic")
            src = "BYOK" if ck.get("anthropic") else "server"
            logger.info(f"LLM Provider: Anthropic initialized ({src})")

        # Last: Ollama (local fallback)
        if not os.getenv("DISABLE_OLLAMA"):
            self._providers["ollama"] = OpenAICompatibleProvider(
                name="ollama", base_url="http://localhost:11434",
                api_key="", model="llama3.1:8b",
            )
            self._provider_order.append("ollama")
            logger.info("LLM Provider: Ollama local fallback registered")
        else:
            logger.info("LLM Provider: Ollama local fallback disabled via DISABLE_OLLAMA env var")

        available = [n for n in self._provider_order if self._providers[n].is_available()]
        logger.info(f"LLM Providers: {len(available)} available: {available}")

    def get_available_providers(self) -> List[str]:
        return [n for n in self._provider_order if self._providers[n].is_available()]

    def is_available(self) -> bool:
        """True if at least one LLM provider is available."""
        return len(self.get_available_providers()) > 0

    def route(self, messages: List[Dict[str, str]], provider: str = "auto",
              preferred: str = "", **kwargs) -> LLMResponse:
        """Route messages to a provider. Pure transport — no identity, no prompts."""
        if provider != "auto":
            p = self._providers.get(provider)
            if p and p.is_available():
                return p.generate(messages, **kwargs)
            raise ValueError(f"Provider '{provider}' not available")

        # Try preferred first
        if preferred and preferred in self._providers:
            p = self._providers[preferred]
            if p.is_available():
                try:
                    response = p.generate(messages, **kwargs)
                    logger.info(
                        f"LLM: {preferred} responded in "
                        f"{response.latency_ms:.0f}ms ({response.tokens_used} tokens)"
                    )
                    return response
                except Exception as e:
                    logger.warning(f"LLM: preferred provider {preferred} failed: {e}")

        # Fallback chain
        errors = []
        for name in self._provider_order:
            p = self._providers[name]
            if not p.is_available():
                continue
            try:
                response = p.generate(messages, **kwargs)
                logger.info(
                    f"LLM: {name} responded in {response.latency_ms:.0f}ms "
                    f"({response.tokens_used} tokens)"
                )
                return response
            except Exception as e:
                errors.append(f"{name}: {e}")
                logger.warning(f"LLM: {name} failed: {e}")

        raise RuntimeError(f"All LLM providers failed. Errors: {'; '.join(errors)}")

    def get_budget_status(self) -> Dict[str, Any]:
        """Return current token budget status."""
        return {
            "daily_limit": self.budget.daily_limit,
            "used_today": self.budget.used_today,
            "remaining": self.budget.remaining(),
            "usage_pct": round(self.budget.usage_pct(), 1),
            "cache_entries": len(self.cache._cache),
        }
