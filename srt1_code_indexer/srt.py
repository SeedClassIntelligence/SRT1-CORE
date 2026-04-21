"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: ORCHESTRATOR, TEST
Key Symbols: CoherenceStatus, TraceLevel, EnforcementLevel, ExecutionTrace, Seed ... and 32 more

Extracted Purposes:
  - EnforcementLevel: SRT-1 Enforcement Mode severity levels.
  - ExecutionTrace: SRT-1 execution tracing — full production audit and traceability.
  - Seed: A Seed is the anchored representation of the user's original intent.
  ...
"""
#!/usr/bin/env python3
"""
Seed Reflection Tool v2.0 (SRT-1)

PURPOSE:
    Anti-hallucination guardrail system. Tracks every 2-3 interactions,
    timestamps them, and injects "seed reflections" back into the AI/LLM
    context to enforce coherence between user intent and AI output.

    Originally designed for conversational AI coherence.
    Now extended to code indexing and autonomous code execution.

CORE MECHANISM:
    1. SEED CAPTURE    - Records the user's original intent and task context
    2. TRACE LOGGING   - Timestamps every operation with input/output hashes
    3. REFLECTION GATE - Every N interactions, generates a coherence checkpoint
    4. SEED INJECTION  - Pushes the checkpoint back into the AI's working context
    5. DRIFT DETECTION - Compares current trajectory against original seeds

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import json
import hashlib
import logging
import re
import time
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==============================================================================
# ENUMS
# ==============================================================================

class CoherenceStatus(Enum):
    ON_TASK = "ON_TASK"
    MINOR_DRIFT = "MINOR_DRIFT"
    MAJOR_DRIFT = "MAJOR_DRIFT"
    SEED_LOST = "SEED_LOST"


class TraceLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    REFLECTION = "REFLECTION"


class EnforcementLevel(Enum):
    """SRT-1 Enforcement Mode severity levels."""
    INFORMATIONAL = 0
    WARNING = 1
    SOFT_STOP = 2
    HARD_STOP = 3
    LOCKOUT = 4


# ==============================================================================
# EXECUTION TRACE (from SCIA production spec)
# ==============================================================================

@dataclass
class ExecutionTrace:
    """SRT-1 execution tracing — full production audit and traceability."""
    trace_id: str
    parent_trace: Optional[str]
    module: str
    operation: str
    input_hash: str
    output_hash: str
    duration_ms: int
    persona_active: Optional[str]
    methodology_used: Optional[str]
    reflection_applied: bool
    timestamp: datetime
    level: TraceLevel = TraceLevel.INFO
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "parent_trace": self.parent_trace,
            "module": self.module,
            "operation": self.operation,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "duration_ms": self.duration_ms,
            "persona_active": self.persona_active,
            "methodology_used": self.methodology_used,
            "reflection_applied": self.reflection_applied,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "metadata": self.metadata,
        }


# ==============================================================================
# SEED — The Original User Intent Anchor
# ==============================================================================

@dataclass
class Seed:
    """
    A Seed is the anchored representation of the user's original intent.
    Every reflection checkpoint compares current state back to this seed
    to detect drift and enforce coherence.
    """
    seed_id: str
    original_task: str
    intent_keywords: List[str]
    domain_context: str
    created_at: datetime
    coherence_threshold: float = 0.6
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_id": self.seed_id,
            "original_task": self.original_task,
            "intent_keywords": self.intent_keywords,
            "domain_context": self.domain_context,
            "created_at": self.created_at.isoformat(),
            "coherence_threshold": self.coherence_threshold,
            "metadata": self.metadata,
        }


# ==============================================================================
# REFLECTION CHECKPOINT
# ==============================================================================

@dataclass
class ReflectionCheckpoint:
    """
    Generated every N interactions. Contains a coherence assessment
    and an injection directive to push back into the AI context.
    """
    checkpoint_id: str
    seed_id: str
    interaction_count: int
    coherence_status: CoherenceStatus
    coherence_score: float
    operations_since_last: List[str]
    drift_indicators: List[str]
    injection_directive: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "seed_id": self.seed_id,
            "interaction_count": self.interaction_count,
            "coherence_status": self.coherence_status.value,
            "coherence_score": self.coherence_score,
            "operations_since_last": self.operations_since_last,
            "drift_indicators": self.drift_indicators,
            "injection_directive": self.injection_directive,
            "timestamp": self.timestamp.isoformat(),
        }


# ==============================================================================
# ENFORCEMENT EVENT — Violation Record
# ==============================================================================

@dataclass
class EnforcementEvent:
    """
    A recorded enforcement event. When SRT-1 detects a violation and blocks
    progression, this event captures the full lineage: what was violated,
    what was blocked, and how it was resolved (or overridden).
    """
    event_id: str
    level: EnforcementLevel
    violated_rule: str
    blocked_action: str
    reason: str
    required_resolution: str
    override_allowed: bool = True
    override_reason: Optional[str] = None
    override_actor: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "level": self.level.name,
            "level_value": self.level.value,
            "violated_rule": self.violated_rule,
            "blocked_action": self.blocked_action,
            "reason": self.reason,
            "required_resolution": self.required_resolution,
            "override_allowed": self.override_allowed,
            "override_reason": self.override_reason,
            "override_actor": self.override_actor,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "timestamp": self.timestamp.isoformat(),
        }

# ==============================================================================
# SRT v2.0 — THE CORE ENGINE
# ==============================================================================

class SRT:
    """
    Seed Reflection Tool v2.0

    Anti-hallucination guardrail. Plants seeds of user intent, tracks
    every operation, and every N interactions generates a reflection
    checkpoint that gets injected back into the AI's working context.
    """

    def __init__(self, reflection_interval: int = 3):
        self.reflection_interval = reflection_interval
        self._seeds: Dict[str, Seed] = {}
        self._active_seed_id: Optional[str] = None
        self._traces: List[ExecutionTrace] = []
        self._checkpoints: List[ReflectionCheckpoint] = []
        self._reflections: List[Dict[str, Any]] = []
        self._operation_count: int = 0
        self._trace_counter: int = 0
        self._checkpoint_counter: int = 0
        self._ops_since_last_reflection: List[str] = []

        # Enforcement Mode state
        self._enforcement_mode: str = "advisory"  # "advisory" or "enforcement"
        self._enforcement_events: List[EnforcementEvent] = []
        self._enforcements_issued: int = 0
        self._enforcements_complied: int = 0
        self._enforcements_ignored: int = 0

    # ------------------------------------------------------------------
    # SEED MANAGEMENT
    # ------------------------------------------------------------------

    def plant_seed(self, task: str, domain: str = "general",
                   keywords: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> Seed:
        """Plant the original user intent as a Seed — the coherence anchor."""
        if keywords is None:
            stop_words = {
                "the", "a", "an", "is", "are", "to", "of", "in", "for",
                "on", "with", "at", "by", "from", "it", "and", "but", "or",
                "not", "this", "that", "all", "each", "as", "up", "do", "if",
            }
            words = re.findall(r"[a-z][a-z0-9_]+", task.lower())
            keywords = [w for w in words if w not in stop_words and len(w) > 2]

        seed_id = self._generate_id("seed")
        seed = Seed(
            seed_id=seed_id,
            original_task=task,
            intent_keywords=keywords,
            domain_context=domain,
            created_at=datetime.now(),
            metadata=metadata or {},
        )
        self._seeds[seed_id] = seed
        self._active_seed_id = seed_id
        logger.info(f"[SRT] Seed planted: {seed_id} | Task: {task[:60]}...")
        return seed

    def get_active_seed(self) -> Optional[Seed]:
        if self._active_seed_id:
            return self._seeds.get(self._active_seed_id)
        return None

    # ------------------------------------------------------------------
    # EXECUTION TRACING
    # ------------------------------------------------------------------

    def trace_operation(self, module: str, operation: str,
                        input_data: Any = None, output_data: Any = None,
                        persona: Optional[str] = None,
                        methodology: Optional[str] = None,
                        parent_trace_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> ExecutionTrace:
        """Record an execution trace. Auto-triggers reflection every N ops."""
        start_time = time.time()
        input_hash = self._hash_content(input_data) if input_data else "none"
        output_hash = self._hash_content(output_data) if output_data else "none"
        duration_ms = int((time.time() - start_time) * 1000)

        self._trace_counter += 1
        trace_id = self._generate_id("trace")

        trace = ExecutionTrace(
            trace_id=trace_id,
            parent_trace=parent_trace_id or (self._traces[-1].trace_id if self._traces else None),
            module=module,
            operation=operation,
            input_hash=input_hash,
            output_hash=output_hash,
            duration_ms=duration_ms,
            persona_active=persona,
            methodology_used=methodology,
            reflection_applied=False,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        self._traces.append(trace)
        self._operation_count += 1
        self._ops_since_last_reflection.append(f"{module}.{operation}")

        # === THE CORE SRT-1 MECHANISM ===
        if self._operation_count % self.reflection_interval == 0:
            checkpoint = self._generate_reflection_checkpoint()
            trace.reflection_applied = True
            logger.info(
                f"[SRT] REFLECTION GATE at op #{self._operation_count} "
                f"| {checkpoint.coherence_status.value} ({checkpoint.coherence_score:.0%})"
            )

        return trace

    # ------------------------------------------------------------------
    # REFLECTION ENGINE (Anti-Hallucination Core)
    # ------------------------------------------------------------------

    def _generate_reflection_checkpoint(self) -> ReflectionCheckpoint:
        """Generate a coherence checkpoint — the heart of SRT-1."""
        self._checkpoint_counter += 1
        seed = self.get_active_seed()
        coherence_score, drift_indicators = self._compute_coherence()

        if coherence_score >= 0.8:
            status = CoherenceStatus.ON_TASK
        elif coherence_score >= 0.5:
            status = CoherenceStatus.MINOR_DRIFT
        elif coherence_score >= 0.2:
            status = CoherenceStatus.MAJOR_DRIFT
        else:
            status = CoherenceStatus.SEED_LOST

        directive = self._build_injection_directive(seed, status, coherence_score, drift_indicators)

        checkpoint = ReflectionCheckpoint(
            checkpoint_id=self._generate_id("checkpoint"),
            seed_id=self._active_seed_id or "no_seed",
            interaction_count=self._operation_count,
            coherence_status=status,
            coherence_score=coherence_score,
            operations_since_last=list(self._ops_since_last_reflection),
            drift_indicators=drift_indicators,
            injection_directive=directive,
            timestamp=datetime.now(),
        )

        self._checkpoints.append(checkpoint)
        self._ops_since_last_reflection = []
        return checkpoint

    def _compute_coherence(self) -> Tuple[float, List[str]]:
        """Compare recent operations against the original seed."""
        seed = self.get_active_seed()
        if not seed:
            return 0.0, ["NO_SEED_PLANTED"]

        drift_indicators: List[str] = []
        seed_keywords = set(seed.intent_keywords)

        recent_words: set = set()
        for op in self._ops_since_last_reflection:
            for part in op.lower().replace(".", "_").split("_"):
                if len(part) > 2:
                    recent_words.add(part)

        recent_trace_count = min(len(self._traces), self.reflection_interval)
        for trace in self._traces[-recent_trace_count:]:
            for key, value in trace.metadata.items():
                if isinstance(value, str):
                    for word in value.lower().split():
                        if len(word) > 2:
                            recent_words.add(word)

        if not seed_keywords:
            return 1.0, []

        overlap = seed_keywords & recent_words
        coherence_score = len(overlap) / len(seed_keywords)

        if coherence_score < seed.coherence_threshold:
            missing = seed_keywords - recent_words
            drift_indicators.append(f"MISSING_KEYWORDS: {', '.join(list(missing)[:5])}")

        return min(coherence_score, 1.0), drift_indicators

    def _build_injection_directive(self, seed: Optional[Seed],
                                   status: CoherenceStatus,
                                   score: float,
                                   drift_indicators: List[str]) -> str:
        """Build the text directive to inject back into AI context."""
        lines = [
            "=" * 60,
            "SRT-1 REFLECTION CHECKPOINT",
            "=" * 60,
            f"  Checkpoint at operation #{self._operation_count}",
            f"  Timestamp: {datetime.now().isoformat()}",
            f"  Coherence: {status.value} ({score:.0%})",
            "",
        ]
        if seed:
            lines += [
                "  ORIGINAL SEED (User Intent):",
                f"    Task: {seed.original_task}",
                f"    Keywords: {', '.join(seed.intent_keywords[:10])}",
                f"    Domain: {seed.domain_context}",
                "",
            ]
        status_messages = {
            CoherenceStatus.ON_TASK: "  STATUS: On task. Continue.",
            CoherenceStatus.MINOR_DRIFT: "  STATUS: Minor drift. Re-align to seed.",
            CoherenceStatus.MAJOR_DRIFT: "  STATUS: Major drift! Return to seed task.",
            CoherenceStatus.SEED_LOST: "  STATUS: Seed lost. HALT and re-read user request.",
        }
        lines.append(status_messages.get(status, ""))
        if seed and status in (CoherenceStatus.MAJOR_DRIFT, CoherenceStatus.SEED_LOST):
            lines.append(f"  REMINDER: User asked: {seed.original_task}")
        if drift_indicators:
            lines += ["", "  DRIFT INDICATORS:"]
            lines += [f"    - {d}" for d in drift_indicators]
        lines.append("=" * 60)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # PUBLIC QUERY METHODS
    # ------------------------------------------------------------------

    def get_latest_injection(self) -> Optional[str]:
        if self._checkpoints:
            return self._checkpoints[-1].injection_directive
        return None

    def get_coherence_history(self) -> List[Dict[str, Any]]:
        return [
            {
                "checkpoint": cp.checkpoint_id,
                "operation_count": cp.interaction_count,
                "coherence_score": cp.coherence_score,
                "status": cp.coherence_status.value,
                "timestamp": cp.timestamp.isoformat(),
            }
            for cp in self._checkpoints
        ]

    def get_trace_chain(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._traces]

    def force_reflection(self) -> ReflectionCheckpoint:
        return self._generate_reflection_checkpoint()

    # ------------------------------------------------------------------
    # ENFORCEMENT MODE
    # ------------------------------------------------------------------

    def set_enforcement_mode(self, mode: str) -> None:
        """Set enforcement mode: 'advisory' or 'enforcement'."""
        if mode not in ("advisory", "enforcement"):
            raise ValueError(f"Invalid enforcement mode: {mode}. Use 'advisory' or 'enforcement'.")
        self._enforcement_mode = mode
        logger.info(f"[SRT] Enforcement mode set to: {mode}")

    def register_violation(self, rule: str, action: str,
                           level: EnforcementLevel,
                           reason: str,
                           resolution: str,
                           override_allowed: bool = True) -> EnforcementEvent:
        """Register an enforcement violation. Returns the event."""
        event = EnforcementEvent(
            event_id=self._generate_id("enf"),
            level=level,
            violated_rule=rule,
            blocked_action=action,
            reason=reason,
            required_resolution=resolution,
            override_allowed=override_allowed,
        )
        self._enforcement_events.append(event)
        self._enforcements_issued += 1
        logger.warning(
            f"[SRT] ENFORCEMENT: {level.name} — {rule} | "
            f"Blocked: {action} | Reason: {reason}"
        )
        return event

    def check_enforcement(self, action: str) -> Optional[EnforcementEvent]:
        """
        Check if the proposed action is blocked by an active enforcement event.
        Returns the blocking event if blocked, None if clear.

        In advisory mode, always returns None (no blocking).
        In enforcement mode, returns the highest-severity active block.
        """
        if self._enforcement_mode == "advisory":
            return None

        active_blocks = self.get_active_blocks()
        if not active_blocks:
            return None

        # Find the highest-severity block
        blocking = max(active_blocks, key=lambda e: e.level.value)

        # If we have active blocks and an operation comes through,
        # that means the actor is ignoring the enforcement
        if blocking.level.value >= EnforcementLevel.HARD_STOP.value:
            self._enforcements_ignored += 1
            logger.warning(
                f"[SRT] ENFORCEMENT IGNORED: Actor attempted '{action}' "
                f"despite active {blocking.level.name} on '{blocking.violated_rule}'"
            )

        return blocking

    def resolve_violation(self, event_id: str) -> bool:
        """Mark a violation as resolved after remediation."""
        for event in self._enforcement_events:
            if event.event_id == event_id and not event.resolved:
                event.resolved = True
                event.resolved_at = datetime.now()
                self._enforcements_complied += 1
                logger.info(f"[SRT] ENFORCEMENT RESOLVED: {event_id}")
                return True
        return False

    def override_violation(self, event_id: str, reason: str,
                           actor: str = "unknown") -> bool:
        """
        Explicitly override a violation with logged reason.
        Returns False for non-overridable violations.
        Override does NOT erase the violation — it remains in history.
        """
        for event in self._enforcement_events:
            if event.event_id == event_id and not event.resolved:
                if not event.override_allowed:
                    logger.warning(
                        f"[SRT] OVERRIDE DENIED: {event_id} is non-overridable"
                    )
                    return False
                event.override_reason = reason
                event.override_actor = actor
                event.resolved = True
                event.resolved_at = datetime.now()
                self._enforcements_complied += 1
                logger.warning(
                    f"[SRT] ENFORCEMENT OVERRIDDEN: {event_id} by {actor} — {reason}"
                )
                return True
        return False

    def get_active_blocks(self) -> List[EnforcementEvent]:
        """Return all unresolved enforcement events."""
        return [e for e in self._enforcement_events if not e.resolved]

    def get_compliance_stats(self) -> Dict[str, Any]:
        """Return enforcement compliance statistics."""
        rate = 0.0
        if self._enforcements_issued > 0:
            rate = (self._enforcements_complied / self._enforcements_issued) * 100
        return {
            "mode": self._enforcement_mode,
            "enforcements_issued": self._enforcements_issued,
            "complied": self._enforcements_complied,
            "ignored": self._enforcements_ignored,
            "compliance_rate": round(rate, 1),
            "active_blocks": len(self.get_active_blocks()),
            "total_events": len(self._enforcement_events),
        }

    def get_enforcement_history(self) -> List[Dict[str, Any]]:
        """Return full enforcement event history."""
        return [e.to_dict() for e in self._enforcement_events]

    # ------------------------------------------------------------------
    # LEGACY v1 COMPATIBILITY (used by the indexer pipeline)
    # ------------------------------------------------------------------

    def add_reflection(self, reflection_type: str, content: str,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """v1-compatible interface. Also records as an execution trace."""
        metadata = metadata or {}
        reflection = {
            "id": f"reflection_{len(self._reflections) + 1}",
            "type": reflection_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
        }
        self._reflections.append(reflection)

        self.trace_operation(
            module=metadata.get("module", "reflector"),
            operation=reflection_type,
            input_data=content,
            metadata=metadata,
        )

        logger.info(f"Added {reflection_type} reflection: {reflection['id']}")
        return reflection

    def get_reflections(self, reflection_type: str = None) -> List[Dict[str, Any]]:
        if reflection_type:
            return [r for r in self._reflections if r["type"] == reflection_type]
        return self._reflections

    def summarize_reflections(self) -> Dict[str, Any]:
        if not self._reflections and not self._traces:
            return {"summary": "No reflections available"}

        type_counts: Dict[str, int] = {}
        for r in self._reflections:
            rt = r["type"]
            type_counts[rt] = type_counts.get(rt, 0) + 1

        latest_timestamp = ""
        if self._reflections:
            latest_timestamp = max(r["timestamp"] for r in self._reflections)

        coherence_data = {}
        if self._checkpoints:
            cp = self._checkpoints[-1]
            coherence_data = {
                "latest_coherence_score": cp.coherence_score,
                "latest_coherence_status": cp.coherence_status.value,
                "total_checkpoints": len(self._checkpoints),
                "total_traces": len(self._traces),
            }

        return {
            "total_reflections": len(self._reflections),
            "reflection_types": type_counts,
            "latest_timestamp": latest_timestamp,
            "summary": (
                f"SRT contains {len(self._reflections)} reflections "
                f"across {len(type_counts)} categories"
            ),
            "coherence": coherence_data,
            "total_operations": self._operation_count,
            "reflection_checkpoints": len(self._checkpoints),
        }

    # ------------------------------------------------------------------
    # INTERNAL UTILITIES
    # ------------------------------------------------------------------

    def _generate_id(self, prefix: str) -> str:
        self._trace_counter += 1
        raw = f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{self._trace_counter}"
        return f"{prefix}_{hashlib.sha256(raw.encode()).hexdigest()[:12]}"

    @staticmethod
    def _hash_content(data: Any) -> str:
        content_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()[:16]


# ==============================================================================
# SINGLETON
# ==============================================================================

_srt_instance: Optional[SRT] = None


def get_srt(reflection_interval: int = 3) -> SRT:
    global _srt_instance
    if _srt_instance is None:
        _srt_instance = SRT(reflection_interval=reflection_interval)
    return _srt_instance