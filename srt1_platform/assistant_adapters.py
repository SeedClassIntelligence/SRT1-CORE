"""Model-agnostic assistant dispatch adapters for SRT-1 Core.

Adapters receive bounded WorkCell execution requests. They do not own seed
lifecycle, repository truth, WorkCell scope, verification, or trust state.
"""

from __future__ import annotations

import json
import os
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
            results[adapter.name] = adapter.dispatch(request).to_dict()
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
        return None
