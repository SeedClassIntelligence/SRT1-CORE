import os
import re
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class ContextPacket:
    mode: str          # "enforcement" | "alignment" | "recall"
    priority: int      # 100 (Hard Stop) to 1 (Low proximity recall)
    content: str       # The actual payload / instruction
    source: str        # "drift_engine" | "seed_task" | "knowledge_graph"
    timestamp: str     # ISO8601 creation time
    ttl: int           # Time-to-Live (e.g., number of execution cycles)
    resolved: bool = False
    queue_seed_id: Optional[str] = None
    srt_anchor_id: Optional[str] = None
    source_type: Optional[str] = None
    freshness_state: Optional[str] = None
    trust_state: Optional[Dict[str, str]] = None
    degradation_reason: Optional[str] = None
    warning: Optional[str] = None

class SCIAReinjector:
    """
    SRT-1 Live Reinjection Layer (Middleware) - PROACTIVE ENGINE
    
    Dynamically fetches packets from the contextual memory store and injecting
    them into 3 discrete behavior zones in AGENTS.md:
    1. Enforcement (Blocking)
    2. Alignment (Guidance)
    3. Recall (Historical Wisdom)
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.agents_md_path = os.path.join(repo_path, "AGENTS.md")
        self.state_file = os.path.join(repo_path, ".srt1", "reinjector_state.json")

    def _load_active_packets(self) -> List[ContextPacket]:
        """Loads active packets from local JSON state, stripping expired ones."""
        if not os.path.isfile(self.state_file):
            return []
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            active = []
            for p_dict in data:
                packet = ContextPacket(**p_dict)
                # TTL Decay logic
                if packet.resolved:
                    continue
                if packet.ttl > 0:
                    packet.ttl -= 1
                    active.append(packet)
            
            # Save decremented states back
            self._save_packets(active)
            return active
        except Exception:
            return []

    def _save_packets(self, packets: List[ContextPacket]):
        """Persists packets to state JSON."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump([asdict(p) for p in packets], f, indent=2)

    def _normalize_recall_packet(self, packet: Any) -> ContextPacket:
        """Normalize RecallPacket-shaped data without performing recall lookup."""
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
            timestamp=data.get("created_at") or data.get("timestamp") or datetime.now().isoformat(),
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

    def route_and_create_packets(self, active_task: str, warnings: List[str], reflections: List[Dict]) -> List[ContextPacket]:
        """Routes inputs into prioritized memory streams."""
        packets = self._load_active_packets()
        
        # 1. Enforcement (Priority 90-100)
        # Any new drift warning becomes an Enforcement packet
        for w in warnings:
            # Check if this exact warning already exists
            if not any(p.content == w and p.mode == "enforcement" for p in packets):
                packets.append(ContextPacket(
                    mode="enforcement",
                    priority=100,
                    content=w,
                    source="drift_engine",
                    timestamp=datetime.now().isoformat(),
                    ttl=10, # Long TTL for hard stops
                    resolved=False
                ))
        
        # 2. Alignment (Priority 50-89)
        # The active task defines current alignment boundaries
        if active_task:
            # Remove old alignments to prevent seed drift
            packets = [p for p in packets if p.mode != "alignment"]
            packets.append(ContextPacket(
                mode="alignment",
                priority=80,
                content=f"Active Goal: {active_task} | Do not perform changes outside this scope.",
                source="seed_task",
                timestamp=datetime.now().isoformat(),
                ttl=5, # Lasts for task duration
                resolved=False
            ))
            
        # 3. Recall (Priority 1-49)
        # Historical lessons relevant to the task hydrated from Backend
        for r in reflections:
            recall_packet = self._normalize_recall_packet(r)
            if not any(p.content == recall_packet.content for p in packets):
                packets.append(recall_packet)

        self._save_packets(packets)
        return packets

    def inject_packets(self, active_task: str, warnings: List[str], reflections: List[Dict] = None) -> bool:
        """
        Segment injection logic. Formats and overrides the 3 distinct JIT zones in AGENTS.md.
        Uses string splitting instead of regex to avoid catastrophic backtracking on large files.
        """
        if reflections is None:
            reflections = []

        if not os.path.isfile(self.agents_md_path):
            return False

        packets = self.route_and_create_packets(active_task, warnings, reflections)
        
        # Filter by mode and sort by priority descending
        enforcement_packets = sorted([p for p in packets if p.mode == "enforcement"], key=lambda x: -x.priority)
        alignment_packets = sorted([p for p in packets if p.mode == "alignment"], key=lambda x: -x.priority)
        recall_packets = sorted([p for p in packets if p.mode == "recall"], key=lambda x: -x.priority)

        with open(self.agents_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Generate markdown blocks
        enforcement_str = "- **HARD STOP:** `None`"
        if enforcement_packets:
            enforcement_str = "\n".join([f"- **HARD STOP [{p.priority}]:** {p.content}" for p in enforcement_packets])

        alignment_str = "- **CURRENT ALIGNMENT:** `None`"
        if alignment_packets:
            alignment_str = "\n".join([f"- **ALIGNMENT:** {p.content}" for p in alignment_packets])

        recall_str = "- **RELEVANT LESSONS:** `None`"
        if recall_packets:
            recall_lines = []
            for p in recall_packets:
                meta = []
                if p.queue_seed_id:
                    meta.append(f"queue_seed_id={p.queue_seed_id}")
                if p.srt_anchor_id:
                    meta.append(f"srt_anchor_id={p.srt_anchor_id}")
                if p.source_type:
                    meta.append(f"source_type={p.source_type}")
                if p.freshness_state:
                    meta.append(f"freshness={p.freshness_state}")
                if p.warning:
                    meta.append(f"warning={p.warning}")
                suffix = f" ({'; '.join(meta)})" if meta else ""
                recall_lines.append(f"- **RECALL:** {p.content}{suffix}")
            recall_str = "\n".join(recall_lines)

        # Replace zones using fast string splitting (no regex)
        def replace_zone(text, zone_header, next_header, new_content):
            """Replace content between zone_header and next_header with new_content."""
            if zone_header not in text:
                return text
            parts = text.split(zone_header, 1)
            if len(parts) < 2:
                return text
            before = parts[0]
            after_zone = parts[1]
            # Find the metadata line (starts with '*(' and ends with ')*')
            lines = after_zone.split('\n')
            meta_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('*(') and line.strip().endswith(')*'):
                    meta_end = i + 1
                    break
            if meta_end == 0:
                meta_end = 1  # Skip first line if no meta found
            meta_lines = '\n'.join(lines[:meta_end])
            # Find where next section starts
            remaining = '\n'.join(lines[meta_end:])
            if next_header and next_header in remaining:
                old_content, rest = remaining.split(next_header, 1)
                return before + zone_header + meta_lines + '\n' + new_content + '\n\n' + next_header + rest
            else:
                # Last zone — find the next '---' separator
                if '\n\n---' in remaining:
                    old_content, rest = remaining.split('\n\n---', 1)
                    return before + zone_header + meta_lines + '\n' + new_content + '\n\n---' + rest
                return before + zone_header + meta_lines + '\n' + new_content + '\n'

        content = replace_zone(content, "## ⚠️ ACTIVE ENFORCEMENT (BLOCKING)\n", "## 🎯 ACTIVE ALIGNMENT", enforcement_str)
        content = replace_zone(content, "## 🎯 ACTIVE ALIGNMENT (GUIDANCE)\n", "## 🧠 RELEVANT MEMORY", alignment_str)
        content = replace_zone(content, "## 🧠 RELEVANT MEMORY (RECALL)\n", None, recall_str)

        with open(self.agents_md_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return True

