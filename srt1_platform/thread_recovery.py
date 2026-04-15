#!/usr/bin/env python3
"""
SRT-1 Thread Recovery — The Seed Miner
=======================================

WHAT THIS DOES:
    Takes a conversation thread (from ChatGPT, Claude, Cursor, any AI tool),
    runs deep SRT-1 reflection on the ENTIRE conversation, and extracts:

    1. Every SEED — ideas, decisions, requirements, feature requests
    2. Every DRIFT POINT — where the conversation went off track
    3. Every FORGOTTEN SEED — ideas that were mentioned but never completed
    4. Every TOPIC SHIFT — sudden changes in conversation direction
    5. Timestamps and dates — so you remember WHEN things were discussed

    This is SRT-1 doing for CONVERSATIONS what it does for CODE.

HOW TO USE:

    # Method 1: Paste text directly
    python srt1_thread_recovery.py --text "your conversation text here"

    # Method 2: From a file (copy-paste your thread into a .txt file)
    python srt1_thread_recovery.py --file conversation.txt

    # Method 3: From a JSON export (ChatGPT, Claude exports)
    python srt1_thread_recovery.py --file conversation.json

    # Method 4: Interactive mode — paste directly into terminal
    python srt1_thread_recovery.py --interactive

    # Method 5: From clipboard
    python srt1_thread_recovery.py --clipboard

    Output goes to stdout AND saves to a recovery report file.

Author : William Darnell Jernigan IV (Architect)
License: Proprietary - Seed-Class Intelligence Architecture (SCIA)
"""

import os
import sys
import re
import json
import hashlib
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import SRT core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from srt import SRT
except ImportError:
    try:
        from srt1_code_indexer.srt import SRT
    except ImportError:
        sys.exit("[FATAL] Cannot import SRT. Ensure srt.py is available.")


# =============================================================================
# SEED PATTERNS — What constitutes a "seed" in a conversation
# =============================================================================

# These patterns identify when someone plants a seed (an idea, requirement, etc.)
SEED_PATTERNS = [
    # Direct requests / requirements
    (r'\b(?:I want|I need|we need|can you|could you|please|let\'s|we should|I\'d like)\b\s+(.{10,120})',
     'requirement', 'direct_request'),

    # Feature ideas
    (r'\b(?:what if|how about|maybe we could|it would be great if|we could also)\b\s+(.{10,120})',
     'idea', 'feature_idea'),

    # Decisions made
    (r'\b(?:let\'s go with|I\'ll use|we\'ll use|the plan is|decided to|going with)\b\s+(.{10,80})',
     'decision', 'decision_made'),

    # Goals and objectives
    (r'\b(?:the goal is|objective is|aim is|purpose is|trying to)\b\s+(.{10,120})',
     'goal', 'objective'),

    # Problems identified
    (r'\b(?:the problem is|issue is|bug is|error is|broken|doesn\'t work|not working)\b\s+(.{10,100})',
     'problem', 'issue_identified'),

    # Architecture / design decisions
    (r'\b(?:architecture|design|pattern|structure|layout|schema|database|api|endpoint)\b.*?(?:should|will|must)\s+(.{10,100})',
     'architecture', 'design_decision'),

    # TODO / future work
    (r'\b(?:todo|to-do|later|next step|follow up|come back to|revisit|eventually)\b\s*:?\s*(.{5,100})',
     'todo', 'future_work'),

    # Explicit naming of features
    (r'\b(?:feature|component|module|system|engine|service|tool|widget)\b\s+(?:called|named|for)\s+(.{5,60})',
     'feature', 'named_feature'),
]

# Drift indicators — signs the conversation went off track
DRIFT_PATTERNS = [
    (r'\b(?:actually|wait|hold on|never ?mind|forget that|scratch that|on second thought)\b',
     'topic_change'),
    (r'\b(?:going back to|returning to|as I was saying|back to the original)\b',
     'course_correction'),
    (r'\b(?:that reminds me|oh also|by the way|btw|while we\'re at it|one more thing)\b',
     'tangent'),
    (r'\b(?:no|wrong|that\'s not what I meant|I meant|let me clarify|to be clear)\b',
     'clarification'),
]

# Completion indicators — signs a seed was addressed
COMPLETION_PATTERNS = [
    r'\b(?:done|completed|finished|implemented|built|created|added|fixed)\b',
    r'\b(?:here\'s the|here is the|I\'ve created|I\'ve added|I\'ve implemented)\b',
    r'\b(?:✅|✓|check|works|working|success|looks good)\b',
]


# =============================================================================
# THE SEED MINER
# =============================================================================

class SCIASeedMiner:
    """
    Mines conversation threads for seeds, drift, and forgotten ideas.
    This is SRT-1 doing for conversations what it does for code.
    """

    def __init__(self):
        self.srt_tool = SRT(reflection_interval=3)
        self.seeds: List[Dict[str, Any]] = []
        self.drift_points: List[Dict[str, Any]] = []
        self.topic_shifts: List[Dict[str, Any]] = []
        self.messages: List[Dict[str, Any]] = []
        self.current_topic: Optional[str] = None

    def mine(self, conversation_text: str, source: str = "unknown") -> Dict[str, Any]:
        """
        Run deep reflection on an entire conversation.

        Args:
            conversation_text: The raw conversation text or JSON
            source: Where this conversation came from (file name, tool name, etc.)

        Returns:
            Complete recovery report
        """
        print("\n  ╔══════════════════════════════════════════════════════╗")
        print("  ║           SRT-1 THREAD RECOVERY                     ║")
        print("  ║           The Seed Miner                            ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print()

        # Step 1: Parse the conversation
        print("  [1/5] Parsing conversation...")
        self.messages = self._parse_conversation(conversation_text)
        print(f"         Found {len(self.messages)} messages.")

        # Plant the seed for SRT tracking
        self.srt_tool.plant_seed(
            task="Mine conversation thread for seeds, drift, and forgotten ideas",
            domain="thread_recovery",
            keywords=["seed", "idea", "drift", "recovery", "thread", "conversation",
                      "requirement", "feature", "decision", "lost", "forgotten"],
        )

        # Step 2: Extract seeds
        print("  [2/5] Mining seeds...")
        self._extract_seeds()
        print(f"         Found {len(self.seeds)} seed(s).")

        # Step 3: Detect drift
        print("  [3/5] Detecting drift...")
        self._detect_drift()
        print(f"         Found {len(self.drift_points)} drift point(s).")

        # Step 4: Track completion
        print("  [4/5] Tracking completion...")
        self._track_completion()
        completed = sum(1 for s in self.seeds if s.get("completed"))
        forgotten = sum(1 for s in self.seeds if not s.get("completed"))
        print(f"         {completed} completed, {forgotten} forgotten/unresolved.")

        # Step 5: Detect topic shifts
        print("  [5/5] Analyzing conversation flow...")
        self._detect_topic_shifts()
        print(f"         {len(self.topic_shifts)} topic shift(s) detected.")

        # SRT coherence check
        checkpoint = self.srt_tool.force_reflection()

        # Build the recovery report
        report = self._build_report(source, checkpoint)

        print()
        print(f"  Recovery complete. {len(self.seeds)} seeds mined.")
        print()

        return report

    # -----------------------------------------------------------------
    # PARSING
    # -----------------------------------------------------------------

    def _parse_conversation(self, text: str) -> List[Dict[str, Any]]:
        """Parse conversation text into structured messages."""
        messages = []

        # Try JSON first (ChatGPT / Claude export format)
        try:
            data = json.loads(text)
            messages = self._parse_json_conversation(data)
            if messages:
                return messages
        except (json.JSONDecodeError, TypeError):
            pass

        # Try common text formats
        messages = self._parse_text_conversation(text)
        return messages

    def _parse_json_conversation(self, data: Any) -> List[Dict[str, Any]]:
        """Parse JSON conversation export (ChatGPT, Claude, etc.)."""
        messages = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    msg = self._extract_json_message(item)
                    if msg:
                        messages.append(msg)
                    # Check for nested messages
                    for key in ("messages", "mapping", "children"):
                        if key in item and isinstance(item[key], (list, dict)):
                            sub = item[key]
                            if isinstance(sub, dict):
                                sub = list(sub.values())
                            for sub_item in sub:
                                if isinstance(sub_item, dict):
                                    msg = self._extract_json_message(sub_item)
                                    if msg:
                                        messages.append(msg)

        elif isinstance(data, dict):
            # ChatGPT format with 'mapping'
            if "mapping" in data:
                for node_id, node in data["mapping"].items():
                    if isinstance(node, dict) and "message" in node:
                        msg = self._extract_json_message(node["message"])
                        if msg:
                            messages.append(msg)

            # Simple format with 'messages' array
            elif "messages" in data:
                for item in data["messages"]:
                    msg = self._extract_json_message(item)
                    if msg:
                        messages.append(msg)

        return messages

    def _extract_json_message(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Extract a single message from a JSON object."""
        if not isinstance(item, dict):
            return None

        role = item.get("role") or item.get("author", {}).get("role", "")
        content = ""

        # Handle different content formats
        content_field = item.get("content", "")
        if isinstance(content_field, str):
            content = content_field
        elif isinstance(content_field, dict):
            parts = content_field.get("parts", [])
            content = " ".join(str(p) for p in parts if p)
        elif isinstance(content_field, list):
            content = " ".join(str(p) for p in content_field if p)

        # Get text from 'text' field as fallback
        if not content:
            content = item.get("text", "")

        if not content or not content.strip():
            return None

        # Extract timestamp
        timestamp = None
        for ts_key in ("create_time", "timestamp", "created_at", "date", "time"):
            if ts_key in item:
                ts = item[ts_key]
                if isinstance(ts, (int, float)):
                    try:
                        timestamp = datetime.fromtimestamp(ts).isoformat()
                    except (ValueError, OSError):
                        pass
                elif isinstance(ts, str):
                    timestamp = ts
                if timestamp:
                    break

        return {
            "role": role if role in ("user", "assistant", "system") else "unknown",
            "content": content.strip(),
            "timestamp": timestamp,
            "index": 0,  # Will be set later
        }

    def _parse_text_conversation(self, text: str) -> List[Dict[str, Any]]:
        """Parse plain text conversation into messages."""
        messages = []
        lines = text.split("\n")

        # Detect conversation format
        # Format 1: "User: ..." / "Assistant: ..."
        role_pattern = re.compile(
            r'^(User|Human|You|Me|Developer|Assistant|AI|Claude|ChatGPT|Bot|System)\s*:\s*',
            re.IGNORECASE
        )

        current_role = "unknown"
        current_content = []
        current_timestamp = None
        msg_index = 0

        # Try to detect timestamps
        timestamp_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?)|'
            r'(\d{1,2}/\d{1,2}/\d{2,4}\s+\d{1,2}:\d{2}(?:\s*[AP]M)?)|'
            r'(\w+\s+\d{1,2},?\s+\d{4})',
            re.IGNORECASE
        )

        for line in lines:
            # Check for role change
            role_match = role_pattern.match(line)
            if role_match:
                # Save previous message
                if current_content:
                    messages.append({
                        "role": self._normalize_role(current_role),
                        "content": "\n".join(current_content).strip(),
                        "timestamp": current_timestamp,
                        "index": msg_index,
                    })
                    msg_index += 1

                role_text = role_match.group(1)
                current_role = role_text
                current_content = [line[role_match.end():].strip()]
                current_timestamp = None

                # Check for timestamp in line
                ts_match = timestamp_pattern.search(line)
                if ts_match:
                    current_timestamp = ts_match.group(0)
            else:
                # Check for timestamp line
                ts_match = timestamp_pattern.match(line.strip())
                if ts_match and not current_content:
                    current_timestamp = ts_match.group(0)
                elif line.strip():
                    current_content.append(line)

        # Save last message
        if current_content:
            messages.append({
                "role": self._normalize_role(current_role),
                "content": "\n".join(current_content).strip(),
                "timestamp": current_timestamp,
                "index": msg_index,
            })

        # If no role markers found, split by paragraphs and alternate
        if not messages or (len(messages) == 1 and len(text) > 500):
            messages = self._split_by_paragraphs(text)

        return messages

    def _split_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """Last resort: split long text by double newlines, alternate roles."""
        paragraphs = re.split(r'\n\s*\n', text)
        messages = []
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para or len(para) < 10:
                continue
            messages.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": para,
                "timestamp": None,
                "index": i,
            })
        return messages

    def _normalize_role(self, role: str) -> str:
        """Normalize role names."""
        role_l = role.lower().strip()
        user_roles = {"user", "human", "you", "me", "developer"}
        ai_roles = {"assistant", "ai", "claude", "chatgpt", "bot", "gpt"}
        if role_l in user_roles:
            return "user"
        elif role_l in ai_roles:
            return "assistant"
        return "user"  # Default to user

    # -----------------------------------------------------------------
    # SEED EXTRACTION
    # -----------------------------------------------------------------

    def _extract_seeds(self) -> None:
        """Extract every seed from the conversation."""
        for msg in self.messages:
            content = msg["content"]

            for pattern, seed_type, category in SEED_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    seed_text = match.group(1) if match.lastindex else match.group(0)
                    seed_text = seed_text.strip().rstrip('.,;:!?')

                    # Skip very short or noisy seeds
                    if len(seed_text) < 8:
                        continue

                    # Generate a seed ID
                    seed_id = hashlib.sha256(
                        f"{seed_text}:{msg['index']}".encode()
                    ).hexdigest()[:12]

                    # SRT trace
                    self.srt_tool.trace_operation(
                        module="seed_miner",
                        operation=f"seed_found:{seed_type}",
                        input_data={"text": seed_text[:100]},
                        output_data={"seed_id": seed_id},
                        metadata={"context": "seed idea requirement feature decision thread recovery"},
                    )

                    self.seeds.append({
                        "id": seed_id,
                        "text": seed_text,
                        "type": seed_type,
                        "category": category,
                        "message_index": msg["index"],
                        "role": msg["role"],
                        "timestamp": msg.get("timestamp"),
                        "completed": False,
                        "completion_message": None,
                        "context": content[:200],
                    })

        # Deduplicate seeds with very similar text
        self._deduplicate_seeds()

    def _deduplicate_seeds(self) -> None:
        """Remove near-duplicate seeds."""
        unique = []
        seen_texts = set()

        for seed in self.seeds:
            # Normalize for comparison
            norm = re.sub(r'\s+', ' ', seed["text"].lower().strip())
            if norm not in seen_texts:
                seen_texts.add(norm)
                unique.append(seed)

        self.seeds = unique

    # -----------------------------------------------------------------
    # DRIFT DETECTION
    # -----------------------------------------------------------------

    def _detect_drift(self) -> None:
        """Detect points where the conversation drifted."""
        for msg in self.messages:
            content = msg["content"]

            for pattern, drift_type in DRIFT_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    self.drift_points.append({
                        "type": drift_type,
                        "message_index": msg["index"],
                        "role": msg["role"],
                        "timestamp": msg.get("timestamp"),
                        "context": content[:200],
                    })
                    break  # One drift point per message max

    # -----------------------------------------------------------------
    # COMPLETION TRACKING
    # -----------------------------------------------------------------

    def _track_completion(self) -> None:
        """Track which seeds were completed in the conversation."""
        for seed in self.seeds:
            seed_words = set(
                w.lower() for w in seed["text"].split()
                if len(w) > 3
            )

            # Look at messages AFTER the seed was planted
            for msg in self.messages:
                if msg["index"] <= seed["message_index"]:
                    continue

                # Check if this message contains completion of the seed
                content_lower = msg["content"].lower()

                # Check completion patterns
                has_completion = any(
                    re.search(p, content_lower) for p in COMPLETION_PATTERNS
                )

                # Check if seed words appear in a completion context
                word_overlap = sum(1 for w in seed_words if w in content_lower)
                relevance = word_overlap / max(len(seed_words), 1)

                if has_completion and relevance > 0.3:
                    seed["completed"] = True
                    seed["completion_message"] = msg["index"]
                    break

    # -----------------------------------------------------------------
    # TOPIC SHIFT DETECTION
    # -----------------------------------------------------------------

    def _detect_topic_shifts(self) -> None:
        """Detect significant topic shifts in the conversation."""
        if len(self.messages) < 2:
            return

        prev_words = set()
        for i, msg in enumerate(self.messages):
            # Get current topic words
            content = msg["content"].lower()
            words = set(
                w for w in re.findall(r'\b[a-z]{4,}\b', content)
                if w not in {
                    'that', 'this', 'with', 'from', 'have', 'will', 'been',
                    'just', 'when', 'what', 'they', 'them', 'then', 'than',
                    'your', 'here', 'there', 'were', 'would', 'could',
                    'should', 'about', 'some', 'like', 'also', 'each',
                    'make', 'more', 'very', 'does', 'want', 'need',
                }
            )

            if prev_words and words:
                overlap = len(words & prev_words)
                total = max(len(words | prev_words), 1)
                similarity = overlap / total

                if similarity < 0.1 and i > 0:
                    # Major topic shift
                    self.topic_shifts.append({
                        "message_index": msg["index"],
                        "role": msg["role"],
                        "timestamp": msg.get("timestamp"),
                        "similarity": similarity,
                        "new_topic_words": list(words - prev_words)[:8],
                        "old_topic_words": list(prev_words - words)[:8],
                        "context": msg["content"][:150],
                    })

            prev_words = words

    # -----------------------------------------------------------------
    # REPORT GENERATION
    # -----------------------------------------------------------------

    def _build_report(self, source: str, checkpoint) -> Dict[str, Any]:
        """Build the complete recovery report."""
        report_text = self._build_report_text(source, checkpoint)

        return {
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_messages": len(self.messages),
                "total_seeds": len(self.seeds),
                "seeds_completed": sum(1 for s in self.seeds if s["completed"]),
                "seeds_forgotten": sum(1 for s in self.seeds if not s["completed"]),
                "drift_points": len(self.drift_points),
                "topic_shifts": len(self.topic_shifts),
                "srt_coherence": checkpoint.coherence_score,
            },
            "seeds": self.seeds,
            "forgotten_seeds": [s for s in self.seeds if not s["completed"]],
            "completed_seeds": [s for s in self.seeds if s["completed"]],
            "drift_points": self.drift_points,
            "topic_shifts": self.topic_shifts,
            "report": report_text,
        }

    def _build_report_text(self, source: str, checkpoint) -> str:
        """Build human-readable recovery report."""
        L = []
        L.append("# SRT-1 Thread Recovery Report")
        L.append("")
        L.append(f"> **Source:** {source}")
        L.append(f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        L.append(f"> **Messages Analyzed:** {len(self.messages)}")
        L.append(f"> **SRT Coherence:** {checkpoint.coherence_score:.0%}")
        L.append("")

        # Summary
        forgotten = [s for s in self.seeds if not s["completed"]]
        completed = [s for s in self.seeds if s["completed"]]

        L.append("## 📊 Summary")
        L.append("")
        L.append(f"| Metric | Count |")
        L.append(f"|--------|-------|")
        L.append(f"| Seeds Found | {len(self.seeds)} |")
        L.append(f"| ✅ Completed | {len(completed)} |")
        L.append(f"| ❌ Forgotten/Unresolved | {len(forgotten)} |")
        L.append(f"| ⚡ Drift Points | {len(self.drift_points)} |")
        L.append(f"| 🔀 Topic Shifts | {len(self.topic_shifts)} |")
        L.append("")

        # Forgotten seeds — THE KEY OUTPUT
        if forgotten:
            L.append("## ❌ FORGOTTEN SEEDS (Ideas You Lost)")
            L.append("")
            L.append("These ideas were planted but never completed or resolved:")
            L.append("")
            for i, seed in enumerate(forgotten, 1):
                ts = ""
                if seed.get("timestamp"):
                    ts = f" _{seed['timestamp']}_"
                L.append(f"### {i}. [{seed['type'].upper()}] {seed['text']}")
                L.append(f"")
                L.append(f"- **Type:** {seed['category'].replace('_', ' ').title()}")
                L.append(f"- **Said by:** {seed['role']}")
                if ts:
                    L.append(f"- **When:** {ts}")
                L.append(f"- **Message #{seed['message_index'] + 1}**")
                L.append(f"- **Context:** \"{seed['context'][:150]}...\"")
                L.append("")
        else:
            L.append("## ✅ No Forgotten Seeds")
            L.append("")
            L.append("All ideas in this conversation were addressed. Clean thread.")
            L.append("")

        # Completed seeds
        if completed:
            L.append("## ✅ Completed Seeds")
            L.append("")
            for seed in completed:
                ts = f" ({seed['timestamp']})" if seed.get("timestamp") else ""
                L.append(f"- **{seed['text']}** [{seed['type']}]{ts}")
                L.append(f"  - Completed at message #{seed['completion_message'] + 1}")
            L.append("")

        # Drift points
        if self.drift_points:
            L.append("## ⚡ Drift Points")
            L.append("")
            L.append("The conversation went off track at these points:")
            L.append("")
            for dp in self.drift_points:
                ts = f" ({dp['timestamp']})" if dp.get("timestamp") else ""
                L.append(f"- **Message #{dp['message_index'] + 1}** "
                        f"[{dp['type'].replace('_', ' ').upper()}]{ts}")
                L.append(f"  - \"{dp['context'][:120]}...\"")
            L.append("")

        # Topic shifts
        if self.topic_shifts:
            L.append("## 🔀 Topic Shifts")
            L.append("")
            L.append("The conversation changed direction significantly at these points:")
            L.append("")
            for ts in self.topic_shifts:
                timestamp = f" ({ts['timestamp']})" if ts.get("timestamp") else ""
                new_topics = ", ".join(ts["new_topic_words"][:5])
                L.append(f"- **Message #{ts['message_index'] + 1}**{timestamp}")
                L.append(f"  - New topics: {new_topics}")
                L.append(f"  - Similarity to previous: {ts['similarity']:.0%}")
            L.append("")

        # All seeds timeline
        if self.seeds:
            L.append("## 🌱 All Seeds (Timeline)")
            L.append("")
            L.append("Every idea, decision, and requirement in chronological order:")
            L.append("")
            for seed in sorted(self.seeds, key=lambda s: s["message_index"]):
                status = "✅" if seed["completed"] else "❌"
                ts = f" ({seed['timestamp']})" if seed.get("timestamp") else ""
                L.append(f"- {status} **[{seed['type'].upper()}]** {seed['text']}{ts}")
                L.append(f"  - Message #{seed['message_index'] + 1} ({seed['role']})")
            L.append("")

        L.append("---")
        L.append(f"*SRT-1 Thread Recovery v1.0 — {datetime.now().isoformat()}*")

        return "\n".join(L)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SRT-1 Thread Recovery — Mine seeds from conversation threads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n\n"
            "  # From a file\n"
            "  python srt1_thread_recovery.py --file my_conversation.txt\n\n"
            "  # From a JSON export\n"
            "  python srt1_thread_recovery.py --file chatgpt_export.json\n\n"
            "  # Interactive mode (paste and press Ctrl+D / Ctrl+Z)\n"
            "  python srt1_thread_recovery.py --interactive\n\n"
            "  # Direct text\n"
            "  python srt1_thread_recovery.py --text 'User: I want to add search'\n\n"
            "  # Save report to file\n"
            "  python srt1_thread_recovery.py --file chat.txt --output report.md\n"
        ),
    )

    parser.add_argument("--file", "-f", help="Path to conversation file (.txt, .json, .md)")
    parser.add_argument("--text", "-t", help="Raw conversation text (quoted string)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Interactive mode: paste conversation, then Ctrl+D/Ctrl+Z to process")
    parser.add_argument("--clipboard", "-c", action="store_true",
                       help="Read from system clipboard (requires pyperclip)")
    parser.add_argument("--output", "-o", help="Save report to this file path")

    args = parser.parse_args()

    conversation_text = ""
    source = "unknown"

    if args.file:
        if not os.path.exists(args.file):
            print(f"[ERROR] File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            conversation_text = f.read()
        source = os.path.basename(args.file)

    elif args.text:
        conversation_text = args.text
        source = "direct_text"

    elif args.interactive:
        print("  Paste your conversation below. Press Ctrl+D (Linux/Mac) or Ctrl+Z+Enter (Windows) when done:")
        print("  ---")
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            conversation_text = "\n".join(lines)
        except KeyboardInterrupt:
            conversation_text = "\n".join(lines) if 'lines' in dir() else ""
        source = "interactive_paste"

    elif args.clipboard:
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True, text=True
            )
            conversation_text = result.stdout
            source = "clipboard"
        except Exception as e:
            print(f"[ERROR] Could not read clipboard: {e}")
            sys.exit(1)

    else:
        parser.print_help()
        print("\n[ERROR] Provide --file, --text, --interactive, or --clipboard")
        sys.exit(1)

    if not conversation_text.strip():
        print("[ERROR] No conversation text provided.")
        sys.exit(1)

    # Run the mining
    miner = SCIASeedMiner()
    report = miner.mine(conversation_text, source=source)

    # Print the report
    print(report["report"])

    # Save to file if requested
    output_path = args.output
    if not output_path:
        # Default: save next to the input file or in current dir
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"srt1_recovery_{timestamp}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report["report"])
    print(f"\n  Report saved to: {output_path}")

    # Also save the full data as JSON
    json_path = output_path.rsplit(".", 1)[0] + ".json"
    # Make the report JSON-serializable
    json_report = {k: v for k, v in report.items() if k != "report"}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2, default=str)
    print(f"  Data saved to:   {json_path}")


if __name__ == "__main__":
    main()
