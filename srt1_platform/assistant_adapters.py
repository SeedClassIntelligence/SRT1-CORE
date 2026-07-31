"""Model-agnostic assistant dispatch adapters for SRT-1 Core.

Adapters receive bounded WorkCell execution requests. They do not own seed
lifecycle, repository truth, WorkCell scope, verification, or trust state.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now().isoformat()


def _safe_slug(value: str) -> str:
    allowed = []
    for char in value:
        if char.isalnum() or char in {"-", "_"}:
            allowed.append(char)
        else:
            allowed.append("_")
    return "".join(allowed).strip("_") or "request"


@dataclass
class WorkCellExecutionRequest:
    """Bounded request handed from SRT-1 to an assistant adapter."""

    seed_id: str
    intent: str
    blueprint: str = ""
    repo_path: str = ""
    srt1_dir: str = ""
    workcell_package_path: Optional[str] = None
    allowed_paths: List[str] = field(default_factory=list)
    restricted_paths: List[str] = field(default_factory=list)
    completion_signal_path: Optional[str] = None
    trust_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    transient_credentials: Dict[str, str] = field(default_factory=dict, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_id": self.seed_id,
            "intent": self.intent,
            "blueprint": self.blueprint,
            "repo_path": self.repo_path,
            "srt1_dir": self.srt1_dir,
            "workcell_package_path": self.workcell_package_path,
            "allowed_paths": list(self.allowed_paths),
            "restricted_paths": list(self.restricted_paths),
            "completion_signal_path": self.completion_signal_path,
            "trust_state": dict(self.trust_state),
            "metadata": dict(self.metadata),
        }


@dataclass
class AssistantDispatchResult:
    """Result returned by an assistant adapter."""

    adapter: str
    status: str
    message: str = ""
    request_path: Optional[str] = None
    instruction_path: Optional[str] = None
    response: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adapter": self.adapter,
            "status": self.status,
            "message": self.message,
            "request_path": self.request_path,
            "instruction_path": self.instruction_path,
            "response": dict(self.response),
        }


class BaseAssistantAdapter:
    """Base adapter. Subclasses must fail closed on missing configuration."""

    name = "base"

    def dispatch(self, request: WorkCellExecutionRequest) -> AssistantDispatchResult:
        raise NotImplementedError


class FileHandoffAssistantAdapter(BaseAssistantAdapter):
    """Writes a bounded assistant request into `.srt1/adapters/<name>/`."""

    name = "file_context"
    instruction_title = "SRT-1 Assistant Handoff"

    def __init__(self, adapter_name: Optional[str] = None):
        if adapter_name:
            self.name = adapter_name

    def dispatch(self, request: WorkCellExecutionRequest) -> AssistantDispatchResult:
        if not request.srt1_dir:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message="srt1_dir is required for file handoff",
            )

        out_dir = os.path.join(request.srt1_dir, "adapters", self.name)
        os.makedirs(out_dir, exist_ok=True)
        seed_slug = _safe_slug(request.seed_id)
        request_path = os.path.join(out_dir, f"{seed_slug}.json")
        instruction_path = os.path.join(out_dir, f"{seed_slug}.md")

        payload = request.to_dict()
        payload["adapter"] = self.name
        payload["created_at"] = _now()
        payload["contract"] = {
            "scope": "WorkCell-bound assistant execution request",
            "must_stay_inside_allowed_paths": True,
            "must_create_completion_signal": True,
            "does_not_grant_repo_wide_access": True,
        }

        with open(request_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)

        with open(instruction_path, "w", encoding="utf-8") as f:
            f.write(self._build_instruction_markdown(request))

        return AssistantDispatchResult(
            adapter=self.name,
            status="dispatched",
            message="Bounded assistant request written",
            request_path=request_path,
            instruction_path=instruction_path,
        )

    def _build_instruction_markdown(self, request: WorkCellExecutionRequest) -> str:
        allowed = request.allowed_paths or ["Use workcell.md and manifest evidence before expanding scope."]
        restricted = request.restricted_paths or [".git/", ".srt1/seeds/", ".srt1/runtime/"]
        signal = request.completion_signal_path or os.path.join(
            request.srt1_dir or ".srt1", "signals", f"{request.seed_id}_done.json"
        )
        lines = [
            f"# {self.instruction_title}",
            "",
            "## Objective",
            request.intent,
            "",
            "## WorkCell Package",
            request.workcell_package_path or "Not available",
            "",
            "## Operating Rules",
            "- Begin with `workcell.md` when a WorkCell package is available.",
            "- Stay inside allowed paths unless the human expands scope.",
            "- Do not use neighboring files as permission to broaden context.",
            "- Return completion through the SRT-1 completion signal.",
            "- Report runtime acknowledgement through the SRT-1 acknowledgement endpoint when available.",
            "",
            "## Runtime Acknowledgement",
            request.metadata.get("runtime_ack_endpoint") or "Not available",
            "",
            "## Allowed Paths",
            *[f"- {path}" for path in allowed],
            "",
            "## Restricted Paths",
            *[f"- {path}" for path in restricted],
            "",
            "## Completion Signal",
            f"Write `{signal}` when complete with:",
            "",
            "```json",
            json.dumps(
                {
                    "seed_id": request.seed_id,
                    "status": "complete",
                    "files_modified": ["list files here"],
                    "summary": "what changed",
                },
                indent=2,
            ),
            "```",
            "",
            "## Blueprint",
            request.blueprint or "No blueprint supplied. Use the WorkCell package and objective.",
            "",
        ]
        return "\n".join(lines)


class CodexAssistantAdapter(FileHandoffAssistantAdapter):
    """A first-party handoff slot for Codex inside SRT-1 WorkCells."""

    name = "codex"
    instruction_title = "SRT-1 Codex WorkCell Handoff"


class CustomHTTPAssistantAdapter(BaseAssistantAdapter):
    """POST a bounded WorkCell request to a developer-provided endpoint."""

    name = "custom_http"

    def __init__(
        self,
        endpoint: str = "",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 20.0,
    ):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout

    def dispatch(self, request: WorkCellExecutionRequest) -> AssistantDispatchResult:
        if not self.endpoint:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message="custom_http endpoint is not configured",
            )

        payload = request.to_dict()
        payload["adapter"] = self.name
        payload["created_at"] = _now()
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json", **self.headers}
        provider = str(
            request.metadata.get("credential_provider")
            or request.metadata.get("assistant_provider")
            or ""
        ).strip().lower()
        credential = request.transient_credentials.get(provider)
        if not credential and len(request.transient_credentials) == 1:
            provider, credential = next(iter(request.transient_credentials.items()))
        if credential:
            headers.setdefault("Authorization", f"Bearer {credential}")
            headers.setdefault("X-SRT1-Credential-Mode", "session")
            if provider:
                headers.setdefault("X-SRT1-Credential-Provider", provider)
        req = urllib.request.Request(self.endpoint, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = response.read().decode("utf-8")
        response_payload = json.loads(body) if body else {}
        return AssistantDispatchResult(
            adapter=self.name,
            status="dispatched",
            message="Bounded request posted to custom HTTP adapter",
            response=response_payload,
        )


class OpenAICompatibleAssistantAdapter(BaseAssistantAdapter):
    """Call any OpenAI-compatible chat completions endpoint with a bounded WorkCell request."""

    name = "openai_compatible"

    def __init__(
        self,
        provider: str = "openai",
        endpoint: str = "https://api.openai.com/v1/chat/completions",
        model: str = "gpt-4o-mini",
        timeout: float = 60.0,
    ):
        self.provider = (provider or "openai").strip().lower()
        self.endpoint = endpoint or "https://api.openai.com/v1/chat/completions"
        self.model = model or "gpt-4o-mini"
        self.timeout = timeout

    def dispatch(self, request: WorkCellExecutionRequest) -> AssistantDispatchResult:
        credential = request.transient_credentials.get(self.provider)
        if not credential and len(request.transient_credentials) == 1:
            credential = next(iter(request.transient_credentials.values()))
        if not credential:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message=f"{self.provider} session credential is required",
            )
        if not request.allowed_paths:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message="validated WorkCell allowed paths are required",
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        _bounded_provider_prompt(request)
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(self._build_model_payload(request), indent=2, sort_keys=True),
                },
            ],
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credential}",
            "X-SRT1-Credential-Mode": "session",
            "X-SRT1-Credential-Provider": self.provider,
        }
        req = urllib.request.Request(self.endpoint, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = response.read().decode("utf-8")
        response_payload = json.loads(body) if body else {}
        return AssistantDispatchResult(
            adapter=self.name,
            status="dispatched",
            message="Bounded WorkCell request completed by OpenAI-compatible provider",
            response={
                "provider": self.provider,
                "model": self.model,
                "endpoint": self.endpoint,
                "result": response_payload,
                "secret_persisted": False,
            },
        )

    def _build_model_payload(self, request: WorkCellExecutionRequest) -> Dict[str, Any]:
        if request.metadata.get("conversation_only"):
            return {
                "mode": "project_conversation",
                "user_message": request.intent,
                "repository_context": request.blueprint,
                "conversation_history": request.metadata.get("conversation_history", []),
                "trust_state": dict(request.trust_state),
                "response_contract": {
                    "discussion_only": True,
                    "must_not_write_files": True,
                    "must_not_claim_execution": True,
                    "must_ground_repository_claims_in_supplied_context": True,
                    "json_schema": {"message": "grounded conversational response"},
                },
            }
        return {
            "seed_id": request.seed_id,
            "intent": request.intent,
            "blueprint": request.blueprint,
            "workcell_package_path": request.workcell_package_path,
            "allowed_paths": list(request.allowed_paths),
            "restricted_paths": list(request.restricted_paths),
            "completion_signal_path": request.completion_signal_path,
            "trust_state": dict(request.trust_state),
            "runtime_controls": request.metadata.get("runtime_control_endpoints", {}),
            "runtime_ack_endpoint": request.metadata.get("runtime_ack_endpoint"),
            "write_validation_endpoint": request.metadata.get("write_validation_endpoint"),
            "required_response_contract": {
                "return_proposed_changes_only": True,
                "do_not_write_files_directly": True,
                "must_stay_inside_allowed_paths": True,
                "must_respect_pause_stop_cancel": True,
                "json_schema": {
                    "proposed_changes": [
                        {
                            "file_path": "relative/path/inside/workcell",
                            "action": "MODIFY|CREATE",
                            "new_content": "complete replacement or new file content",
                            "rationale": "why this change satisfies the WorkCell objective",
                        }
                    ]
                },
            },
        }


def _bounded_provider_prompt(request: Optional[WorkCellExecutionRequest] = None) -> str:
    if request and request.metadata.get("conversation_only"):
        return (
            "You are the conversational reasoning layer inside SRT-1. "
            "Discuss the user's code project using only the repository evidence supplied by SRT-1. "
            "Do not write files, propose file mutations, claim work was executed, or broaden repository access. "
            "Clearly distinguish known repository facts from recommendations. "
            "Return only a JSON object with one string field named message."
        )
    return (
        "You are operating inside SRT-1. Return only a JSON object. "
        "Do not write files directly and do not claim files were changed. "
        "All file edits must be returned as proposed_changes for human review. "
        "Each proposed change must include file_path, action, new_content, and rationale. "
        "Use only MODIFY or CREATE actions. Stay inside allowed paths and obey pause, stop, and cancel controls. "
        'If no safe change is available, return {"proposed_changes": []}.'
    )


def _bounded_provider_payload(request: WorkCellExecutionRequest) -> Dict[str, Any]:
    return OpenAICompatibleAssistantAdapter()._build_model_payload(request)


def _normalized_chat_result(content: str) -> Dict[str, Any]:
    """Normalize native provider text for the shared proposal and chat paths."""
    return {"choices": [{"message": {"content": str(content or "")}}]}


class AnthropicAssistantAdapter(BaseAssistantAdapter):
    """Call Anthropic Messages with a bounded WorkCell request."""

    name = "anthropic"

    def __init__(
        self,
        endpoint: str = "https://api.anthropic.com/v1/messages",
        model: str = "claude-sonnet-4-5",
        timeout: float = 60.0,
        max_tokens: int = 8192,
    ):
        self.endpoint = endpoint or "https://api.anthropic.com/v1/messages"
        self.model = model or "claude-sonnet-4-5"
        self.timeout = timeout
        self.max_tokens = max_tokens

    def dispatch(self, request: WorkCellExecutionRequest) -> AssistantDispatchResult:
        credential = request.transient_credentials.get("anthropic")
        if not credential and len(request.transient_credentials) == 1:
            credential = next(iter(request.transient_credentials.values()))
        if not credential:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message="anthropic session credential is required",
            )
        if not request.allowed_paths:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message="validated WorkCell allowed paths are required",
            )

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": 0.2,
            "system": _bounded_provider_prompt(request),
            "messages": [{
                "role": "user",
                "content": json.dumps(_bounded_provider_payload(request), indent=2, sort_keys=True),
            }],
        }
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": credential,
                "anthropic-version": "2023-06-01",
                "X-SRT1-Credential-Mode": "session",
                "X-SRT1-Credential-Provider": "anthropic",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = response.read().decode("utf-8")
        native_result = json.loads(body) if body else {}
        content = "".join(
            str(block.get("text") or "")
            for block in (native_result.get("content") or [])
            if isinstance(block, dict) and block.get("type") == "text"
        )
        return AssistantDispatchResult(
            adapter=self.name,
            status="dispatched",
            message="Bounded WorkCell request completed by Anthropic",
            response={
                "provider": "anthropic",
                "model": self.model,
                "endpoint": self.endpoint,
                "result": _normalized_chat_result(content),
                "native_result": native_result,
                "secret_persisted": False,
            },
        )


class GeminiAssistantAdapter(BaseAssistantAdapter):
    """Call Gemini generateContent with a bounded WorkCell request."""

    name = "gemini"

    def __init__(
        self,
        endpoint: str = "",
        model: str = "gemini-2.5-flash",
        timeout: float = 60.0,
    ):
        self.model = model or "gemini-2.5-flash"
        self.endpoint = endpoint or (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )
        self.timeout = timeout

    def dispatch(self, request: WorkCellExecutionRequest) -> AssistantDispatchResult:
        credential = request.transient_credentials.get("gemini")
        if not credential and len(request.transient_credentials) == 1:
            credential = next(iter(request.transient_credentials.values()))
        if not credential:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message="gemini session credential is required",
            )
        if not request.allowed_paths:
            return AssistantDispatchResult(
                adapter=self.name,
                status="degraded",
                message="validated WorkCell allowed paths are required",
            )

        payload = {
            "systemInstruction": {"parts": [{"text": _bounded_provider_prompt(request)}]},
            "contents": [{
                "role": "user",
                "parts": [{
                    "text": json.dumps(_bounded_provider_payload(request), indent=2, sort_keys=True),
                }],
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": credential,
                "X-SRT1-Credential-Mode": "session",
                "X-SRT1-Credential-Provider": "gemini",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = response.read().decode("utf-8")
        native_result = json.loads(body) if body else {}
        candidates = native_result.get("candidates") or []
        parts = ((candidates[0].get("content") or {}).get("parts") or []) if candidates else []
        content = "".join(
            str(part.get("text") or "") for part in parts if isinstance(part, dict)
        )
        return AssistantDispatchResult(
            adapter=self.name,
            status="dispatched",
            message="Bounded WorkCell request completed by Gemini",
            response={
                "provider": "gemini",
                "model": self.model,
                "endpoint": self.endpoint,
                "result": _normalized_chat_result(content),
                "native_result": native_result,
                "secret_persisted": False,
            },
        )


class AssistantAdapterRegistry:
    """Build adapters from Core-safe configuration dictionaries."""

    def __init__(self, configs: Optional[List[Dict[str, Any]]] = None):
        self.configs = configs or []

    def dispatch_all(self, request: WorkCellExecutionRequest) -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        for config in self.configs:
            adapter = self._build_adapter(config)
            if adapter is None:
                name = str(config.get("type") or "unknown")
                results[name] = AssistantDispatchResult(
                    adapter=name,
                    status="degraded",
                    message="Unknown assistant adapter type",
                ).to_dict()
                continue
            try:
                results[adapter.name] = adapter.dispatch(request).to_dict()
            except urllib.error.HTTPError as exc:
                results[adapter.name] = AssistantDispatchResult(
                    adapter=adapter.name,
                    status="degraded",
                    message=f"Provider request failed with HTTP {exc.code}",
                ).to_dict()
            except (urllib.error.URLError, TimeoutError):
                results[adapter.name] = AssistantDispatchResult(
                    adapter=adapter.name,
                    status="degraded",
                    message="Provider request could not reach the configured endpoint",
                ).to_dict()
            except Exception:
                results[adapter.name] = AssistantDispatchResult(
                    adapter=adapter.name,
                    status="degraded",
                    message="Provider request failed before a usable response was returned",
                ).to_dict()
        return results

    def _build_adapter(self, config: Dict[str, Any]) -> Optional[BaseAssistantAdapter]:
        adapter_type = str(config.get("type") or "").strip().lower()
        if adapter_type in {"file", "file_context", "file_handoff"}:
            return FileHandoffAssistantAdapter(adapter_name=config.get("name") or "file_context")
        if adapter_type == "codex":
            return CodexAssistantAdapter()
        if adapter_type in {"custom_http", "http", "webhook"}:
            return CustomHTTPAssistantAdapter(
                endpoint=str(config.get("endpoint") or ""),
                headers=dict(config.get("headers") or {}),
                timeout=float(config.get("timeout") or 20.0),
            )
        if adapter_type in {"openai_compatible", "provider_runtime", "llm_provider"}:
            return OpenAICompatibleAssistantAdapter(
                provider=str(config.get("provider") or "openai"),
                endpoint=str(config.get("endpoint") or "https://api.openai.com/v1/chat/completions"),
                model=str(config.get("model") or "gpt-4o-mini"),
                timeout=float(config.get("timeout") or 60.0),
            )
        if adapter_type in {"anthropic", "claude"}:
            return AnthropicAssistantAdapter(
                endpoint=str(config.get("endpoint") or "https://api.anthropic.com/v1/messages"),
                model=str(config.get("model") or "claude-sonnet-4-5"),
                timeout=float(config.get("timeout") or 60.0),
                max_tokens=int(config.get("max_tokens") or 8192),
            )
        if adapter_type in {"gemini", "google"}:
            return GeminiAssistantAdapter(
                endpoint=str(config.get("endpoint") or ""),
                model=str(config.get("model") or "gemini-2.5-flash"),
                timeout=float(config.get("timeout") or 60.0),
            )
        return None
