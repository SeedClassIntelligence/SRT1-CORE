import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ContextPacket:
    mode: str
    priority: int
    content: str
    source: str
    timestamp: str
    ttl: int
    resolved: bool = False
    queue_seed_id: Optional[str] = None
    srt_anchor_id: Optional[str] = None
    source_type: Optional[str] = None
    freshness_state: Optional[str] = None
    trust_state: Optional[Dict[str, str]] = None
    degradation_reason: Optional[str] = None
    warning: Optional[str] = None


class SCIAReinjector:
    """Build bounded runtime context from already-retrieved packets.

    Standing assistant instructions are source-owned files. Reinjection writes
    only to SRT-1 runtime state so seed activity cannot corrupt repository
    policy files.
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.context_dir = os.path.join(repo_path, ".srt1", "context")
        self.output_path = os.path.join(self.context_dir, "reinjection.md")
        self.state_file = os.path.join(repo_path, ".srt1", "reinjector_state.json")

    def _load_active_packets(self) -> List[ContextPacket]:
        """Load active packets and apply one execution-cycle TTL decay."""
        if not os.path.isfile(self.state_file):
            return []
        try:
            with open(self.state_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            active = []
            for item in data:
                packet = ContextPacket(**item)
                if packet.resolved:
                    continue
                if packet.ttl > 0:
                    packet.ttl -= 1
                    active.append(packet)
            self._save_packets(active)
            return active
        except (OSError, TypeError, ValueError):
            return []

    def _save_packets(self, packets: List[ContextPacket]) -> None:
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        temporary_path = self.state_file + ".tmp"
        with open(temporary_path, "w", encoding="utf-8") as handle:
            json.dump([asdict(packet) for packet in packets], handle, indent=2)
        os.replace(temporary_path, self.state_file)

    def _normalize_recall_packet(self, packet: Any) -> ContextPacket:
        """Normalize RecallPacket-shaped data without performing retrieval."""
        if hasattr(packet, "to_reinjection_dict"):
            data = packet.to_reinjection_dict()
        elif hasattr(packet, "to_dict"):
            data = packet.to_dict()
        elif isinstance(packet, dict):
            data = dict(packet)
        else:
            data = {"content": str(packet)}

        freshness = data.get("freshness_state")
        degradation_reason = data.get("degradation_reason")
        warning = None
        if freshness in ("degraded", "unknown") or degradation_reason:
            warning = degradation_reason or f"Recall freshness is {freshness or 'unknown'}"

        return ContextPacket(
            mode=data.get("mode", "recall"),
            priority=data.get("priority", 40),
            content=data.get("content", ""),
            source=data.get("source") or data.get("source_type", "knowledge_graph"),
            timestamp=data.get("created_at") or data.get("timestamp") or _utc_now(),
            ttl=data.get("ttl", 3),
            resolved=data.get("resolved", False),
            queue_seed_id=data.get("queue_seed_id"),
            srt_anchor_id=data.get("srt_anchor_id"),
            source_type=data.get("source_type"),
            freshness_state=freshness,
            trust_state=data.get("trust_state"),
            degradation_reason=degradation_reason,
            warning=warning,
        )

    def route_and_create_packets(
        self,
        active_task: str,
        warnings: List[str],
        reflections: List[Dict],
    ) -> List[ContextPacket]:
        """Route caller-provided context; this method performs no recall lookup."""
        packets = self._load_active_packets()
        for warning in warnings:
            if not any(packet.content == warning and packet.mode == "enforcement" for packet in packets):
                packets.append(ContextPacket(
                    mode="enforcement",
                    priority=100,
                    content=warning,
                    source="drift_engine",
                    timestamp=_utc_now(),
                    ttl=10,
                ))

        if active_task:
            packets = [packet for packet in packets if packet.mode != "alignment"]
            packets.append(ContextPacket(
                mode="alignment",
                priority=80,
                content=f"Active Goal: {active_task} | Do not perform changes outside this scope.",
                source="seed_task",
                timestamp=_utc_now(),
                ttl=5,
            ))

        for reflection in reflections:
            recall_packet = self._normalize_recall_packet(reflection)
            if not any(packet.content == recall_packet.content for packet in packets):
                packets.append(recall_packet)

        self._save_packets(packets)
        return packets

    def inject_packets(
        self,
        active_task: str,
        warnings: List[str],
        reflections: Optional[List[Dict]] = None,
    ) -> bool:
        """Write an atomic runtime context artifact, never standing instructions."""
        packets = self.route_and_create_packets(active_task, warnings, reflections or [])
        groups = {
            "Enforcement": sorted(
                [packet for packet in packets if packet.mode == "enforcement"],
                key=lambda packet: -packet.priority,
            ),
            "Alignment": sorted(
                [packet for packet in packets if packet.mode == "alignment"],
                key=lambda packet: -packet.priority,
            ),
            "Recall": sorted(
                [packet for packet in packets if packet.mode == "recall"],
                key=lambda packet: -packet.priority,
            ),
        }

        lines = [
            "# SRT-1 Runtime Reinjection Context",
            "",
            "Generated runtime context. Standing assistant instructions remain source-owned.",
        ]
        for heading, group in groups.items():
            lines.extend(["", f"## {heading}"])
            if not group:
                lines.append("- None")
                continue
            for packet in group:
                metadata = {
                    "queue_seed_id": packet.queue_seed_id,
                    "srt_anchor_id": packet.srt_anchor_id,
                    "source_type": packet.source_type,
                    "freshness": packet.freshness_state,
                    "trust_state": packet.trust_state,
                    "degradation_reason": packet.degradation_reason,
                    "warning": packet.warning,
                }
                visible = [
                    f"{key}={value}"
                    for key, value in metadata.items()
                    if value not in (None, "", {})
                ]
                suffix = f" ({'; '.join(visible)})" if visible else ""
                prefix = f"HARD STOP [{packet.priority}]: " if heading == "Enforcement" else ""
                lines.append(f"- {prefix}{packet.content}{suffix}")

        os.makedirs(self.context_dir, exist_ok=True)
        temporary_path = self.output_path + ".tmp"
        with open(temporary_path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines).rstrip() + "\n")
        os.replace(temporary_path, self.output_path)
        return True
