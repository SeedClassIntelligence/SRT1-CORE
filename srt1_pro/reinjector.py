import os
import re
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
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
            if not any(p.content == r.get("content") for p in packets):
                packets.append(ContextPacket(
                    mode=r.get("mode", "recall"),
                    priority=r.get("priority", 40),
                    content=r.get("content", ""),
                    source=r.get("source", "knowledge_graph"),
                    timestamp=datetime.now().isoformat(),
                    ttl=r.get("ttl", 3),
                    resolved=False
                ))

        self._save_packets(packets)
        return packets

    def inject_packets(self, active_task: str, warnings: List[str], reflections: List[Dict] = None) -> bool:
        """
        Segment injection logic. Formats and overrides the 3 distinct JIT zones in AGENTS.md.
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
            recall_str = "\n".join([f"- **RECALL:** {p.content}" for p in recall_packets])

        # Replace Enforcement Zone
        pattern_enf = r"(## ⚠️ ACTIVE ENFORCEMENT \(BLOCKING\)\n\*\([^)]+\)\*\n)(.*?)(?=\n\n## 🎯 ACTIVE ALIGNMENT)"
        content = re.sub(pattern_enf, lambda m: m.group(1) + enforcement_str, content, flags=re.DOTALL)

        # Replace Alignment Zone
        pattern_align = r"(## 🎯 ACTIVE ALIGNMENT \(GUIDANCE\)\n\*\([^)]+\)\*\n)(.*?)(?=\n\n## 🧠 RELEVANT MEMORY)"
        content = re.sub(pattern_align, lambda m: m.group(1) + alignment_str, content, flags=re.DOTALL)

        # Replace Recall Zone
        pattern_recall = r"(## 🧠 RELEVANT MEMORY \(RECALL\)\n\*\([^)]+\)\*\n)(.*?)(?=\n\n---)"
        content = re.sub(pattern_recall, lambda m: m.group(1) + recall_str, content, flags=re.DOTALL)

        with open(self.agents_md_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return True
