"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: CLI_ENTRY_POINT, DATA_MODEL
Key Symbols: SCIAMCPEngine, MCPServer, main, __init__, _index ... and 15 more

Extracted Purposes:
  - SCIAMCPEngine: The SRT-1 engine adapted for MCP.
  - MCPServer: MCP Server implementing the Model Context Protocol.
  - _build_synopsis: Build plain-English synopsis.
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 MCP Server — The Continuous Injection Layer
==================================================

This is the piece that makes SRT-1 work INSIDE AI coding tools.

MCP (Model Context Protocol) is the standard that Claude Desktop,
Cursor, and VS Code are adopting. An MCP server runs alongside the
AI tool and provides tools + context that the AI calls AUTOMATICALLY
during its work.

SRT-1 as an MCP server means:
- Every time the developer gives an instruction, SRT-1 sees it
- Every time the AI does something, SRT-1 tags it
- Every 2-3 interactions, SRT-1 fires a reflection checkpoint
- The AI gets the injection AUTOMATICALLY — no pasting, no API calls
- SRT-1 monitors coherence throughout the ENTIRE conversation

HOW TO INSTALL:
    Add this to your Claude Desktop config (claude_desktop_config.json):

    {
      "mcpServers": {
        "srt1": {
          "command": "python",
          "args": ["/path/to/srt1_mcp_server.py"],
          "env": {
            "SRT1_REPO_PATH": "/path/to/your\\project"
          }
        }
      }
    }

    Or for Cursor, add to .cursor/mcp.json in your project:

    {
      "mcpServers": {
        "srt1": {
          "command": "python",
          "args": ["srt1_mcp_server.py"],
          "env": {
            "SRT1_REPO_PATH": "."
          }
        }
      }
    }

Author : William Darnell Jernigan IV (Architect)
License: Business Source License 1.1
"""

import os
import sys
import json
import hashlib
import time
from contextlib import redirect_stdout
from datetime import datetime
from typing import Dict, List, Any, Optional

# ---- Import Core SCIA IP ----
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from srt import SRT
    from srt1_code_indexer import SRT1CodeIndexer
except ImportError:
    try:
        from srt1_code_indexer.srt import SRT
        from srt1_code_indexer.indexer import SRT1CodeIndexer
    except ImportError:
        # Will fail gracefully
        pass


class SCIAMCPEngine:
    """
    The SRT-1 engine adapted for MCP.
    Monitors conversations, tags interactions, fires checkpoints.
    """

    REFLECTION_INTERVAL = 3

    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.srt_tool = SRT(reflection_interval=self.REFLECTION_INTERVAL)

        # Codebase knowledge
        self.manifest: Dict[str, Any] = {}
        self.symbol_table: Dict[str, List[Dict]] = {}
        self.curation_report: Dict[str, Any] = {}
        self.call_graph: Dict[str, List[str]] = {}
        self.synopsis: str = ""

        # Session tracking
        self.current_task: Optional[str] = None
        self.interactions: List[Dict] = []  # Every developer instruction + AI response
        self.injections: List[Dict] = []
        self.interaction_count: int = 0

        # Index on startup
        self._index()
        self._build_synopsis()

    def _index(self) -> None:
        try:
            indexer = SRT1CodeIndexer(self.repo_path)
            with redirect_stdout(sys.stderr):
                self.manifest = indexer.index_repository()
            self.symbol_table = indexer.symbol_table
            self.curation_report = indexer.curation_report
        except Exception:
            pass

    def _build_synopsis(self) -> None:
        """Build plain-English synopsis."""
        total_files = len(self.manifest.get("file_manifest", []))
        total_syms = sum(len(s) for s in self.symbol_table.values())
        repo = os.path.basename(self.repo_path)

        classes = []
        risk_counts: Dict[str, int] = {}

        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                ref = sym.get("reflection", {})
                if sym["type"] == "class" and sym["name"] != "__init__":
                    classes.append({
                        "name": sym["name"], "file": fpath,
                        "purpose": ref.get("purpose", "")
                    })
                for r in ref.get("risk_profile", []):
                    if r != "LOW_RISK":
                        risk_counts[r] = risk_counts.get(r, 0) + 1

        parts = [f"{repo}: {total_files} files, {total_syms} symbols."]
        if classes:
            top = classes[:5]
            parts.append("Key components: " + ", ".join(
                f"{c['name']} ({c['purpose'][:60]})" for c in top if c["purpose"]
            ))
        if risk_counts:
            parts.append("Risks: " + ", ".join(
                f"{v} {k}" for k, v in risk_counts.items()
            ))

        overlaps = self.curation_report.get("functional_overlaps", [])
        if overlaps:
            dupes = [ov["instances"][0]["function"] for ov in overlaps]
            parts.append(f"Duplicated functions: {', '.join(dupes)}")

        self.synopsis = " ".join(parts)

    def generate_blueprint(self, seed: str) -> Dict:
        """Generate a detailed blueprint prompt from a seed idea."""
        seed_words = set(self._task_keywords())
        # Add words from the seed itself
        for w in seed.lower().replace(',', ' ').replace('.', ' ').split():
            if len(w) > 2:
                seed_words.add(w)

        relevant = []
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                ref = sym.get("reflection", {})
                name_l = sym["name"].lower()
                purpose_l = ref.get("purpose", "").lower()
                score = sum(3 if w in name_l else (2 if w in purpose_l else 0) for w in seed_words)
                if score > 0:
                    relevant.append({
                        "name": sym["name"], "file": fpath, "line": sym["line"],
                        "purpose": ref.get("purpose", ""),
                        "risk": ref.get("risk_profile", []),
                        "score": score,
                    })
        relevant.sort(key=lambda x: -x["score"])
        top = relevant[:12]

        lines = [
            f"# Blueprint: {seed}",
            "",
            f"Generated by SRT-1 with knowledge of {sum(len(s) for s in self.symbol_table.values())} symbols.",
            "",
        ]
        if top:
            lines.append("## Existing Code (DO NOT RECREATE)")
            lines.append("")
            for r in top:
                risk_s = f" [{', '.join(r['risk'])}]" if r['risk'] and r['risk'] != ['LOW_RISK'] else ""
                lines.append(f"- {r['name']} ({r['file']}:{r['line']}): {r['purpose'][:80]}{risk_s}")
            lines.append("")

        lines.extend([
            "## Rules",
            "1. Use existing functions — do not duplicate.",
            "2. Respect risk tags (AUTH_SENSITIVE, WRITES_TO_DB, etc.).",
            "3. Follow existing patterns and naming conventions.",
            f"4. Stay focused on: {seed}",
            "",
            f"*SRT-1 v2.0 — {datetime.now().isoformat()}*",
        ])
        return {"blueprint": "\n".join(lines), "seed": seed, "relevant_count": len(top)}

    # -----------------------------------------------------------------
    # CORE: Monitor interactions and fire checkpoints
    # -----------------------------------------------------------------

    def log_interaction(self, role: str, content: str,
                        files: Optional[List[str]] = None) -> Dict:
        """
        Log EVERY interaction — developer instructions AND AI responses.
        This is the CORE of SRT-1. It watches the conversation.

        Args:
            role: "user" (developer instruction) or "assistant" (AI response)
            content: What was said
            files: Files being touched/discussed

        Returns:
            Result with optional injection if checkpoint fires
        """
        self.interaction_count += 1
        files = files or []

        interaction = {
            "number": self.interaction_count,
            "role": role,
            "content": content[:500],  # Truncate for storage
            "files": files,
            "timestamp": datetime.now().isoformat(),
        }
        self.interactions.append(interaction)

        # Trace through SRT
        self.srt_tool.trace_operation(
            module="conversation",
            operation=f"{role}: {content[:80]}",
            input_data={"role": role, "files": files},
            output_data={"interaction": self.interaction_count},
            metadata={
                "context": " ".join(self._task_keywords()),
                "content_snippet": content[:200],
            },
        )

        # Check if checkpoint fires
        result: Dict[str, Any] = {
            "interaction_number": self.interaction_count,
            "logged": True,
            "checkpoint": None,
        }

        if self.interaction_count % self.REFLECTION_INTERVAL == 0:
            checkpoint = self._fire_checkpoint(files, content)
            self.injections.append(checkpoint)
            result["checkpoint"] = checkpoint
            result["message"] = (
                f"SRT-1 CHECKPOINT #{len(self.injections)}: "
                f"Coherence {checkpoint['coherence']['status']} "
                f"({checkpoint['coherence']['score']:.0%})"
            )
        else:
            remaining = self.REFLECTION_INTERVAL - (
                self.interaction_count % self.REFLECTION_INTERVAL
            )
            result["message"] = f"Logged. Next checkpoint in {remaining} interaction(s)."

        return result

    def _fire_checkpoint(self, files: List[str], recent_content: str) -> Dict:
        """Generate a reflection checkpoint — the injection."""
        cp = self.srt_tool.force_reflection()

        # Get relevant code for files being discussed
        relevant = []
        for fp in files:
            for sym in self.symbol_table.get(fp, []):
                ref = sym.get("reflection", {})
                relevant.append({
                    "file": fp, "symbol": sym["name"],
                    "purpose": ref.get("purpose", ""),
                    "risk": ref.get("risk_profile", []),
                })

        # Gather warnings
        warnings = []
        for ov in self.curation_report.get("functional_overlaps", []):
            func = ov["instances"][0]["function"]
            canon = ov.get("canonical", "")
            # Check if this function is mentioned in recent content
            if func.lower() in recent_content.lower() or not recent_content:
                warnings.append(
                    f"'{func}()' already exists at {canon}. "
                    f"Do NOT create a new version — import the existing one."
                )

        for fp in files:
            for sym in self.symbol_table.get(fp, []):
                risk = sym.get("reflection", {}).get("risk_profile", [])
                if "AUTH_SENSITIVE" in risk or "WRITES_TO_DB" in risk:
                    warnings.append(
                        f"CAUTION: {sym['name']} in {fp} is {', '.join(risk)}."
                    )

        return {
            "checkpoint_number": len(self.injections) + 1,
            "timestamp": datetime.now().isoformat(),
            "coherence": {
                "score": cp.coherence_score,
                "status": cp.coherence_status.value,
            },
            "task": self.current_task,
            "interactions_so_far": self.interaction_count,
            "relevant_code": relevant,
            "warnings": warnings,
            "directive": self._build_directive(cp, relevant, warnings),
        }

    def _build_directive(self, checkpoint, relevant, warnings) -> str:
        """Build the injection text that goes back into the AI's context."""
        lines = [
            "",
            "=" * 60,
            "SRT-1 REFLECTION CHECKPOINT",
            "=" * 60,
        ]

        if self.current_task:
            lines.append(f"ACTIVE TASK: {self.current_task}")
            lines.append(f"STATUS: {checkpoint.coherence_status.value} "
                        f"({checkpoint.coherence_score:.0%})")
        lines.append(f"INTERACTIONS MONITORED: {self.interaction_count}")
        lines.append("")

        if relevant:
            lines.append("CODE THAT EXISTS (relevant to this conversation):")
            for r in relevant[:8]:
                risk_s = ", ".join(r["risk"]) if r["risk"] else "LOW_RISK"
                lines.append(f"  - {r['symbol']} in {r['file']}: {r['purpose'][:60]} [{risk_s}]")
            lines.append("")

        if warnings:
            lines.append("⚠ WARNINGS:")
            for w in warnings:
                lines.append(f"  - {w}")
            lines.append("")

        if checkpoint.coherence_score < 0.5:
            lines.append(">>> DRIFTED. Stop and return to the original task. <<<")
        elif checkpoint.coherence_score < 0.8:
            lines.append(">>> Minor drift. Re-read the active task and stay focused. <<<")
        else:
            lines.append(">>> On track. Use existing functions. Don't duplicate. <<<")

        lines.extend(["", "=" * 60, ""])
        return "\n".join(lines)

    def set_task(self, task: str) -> Dict:
        """Set the developer's task — the seed."""
        self.current_task = task
        self.interactions = []
        self.injections = []
        self.interaction_count = 0
        self.srt_tool = SRT(reflection_interval=self.REFLECTION_INTERVAL)
        self.srt_tool.plant_seed(
            task=task, domain="code_development",
            keywords=self._task_keywords(),
        )
        return {
            "task": task,
            "codebase_files": len(self.manifest.get("file_manifest", [])),
            "codebase_symbols": sum(len(s) for s in self.symbol_table.values()),
            "message": f"Task set. SRT-1 will monitor every interaction and "
                      f"fire checkpoints every {self.REFLECTION_INTERVAL} interactions.",
        }

    def get_context(self) -> str:
        """Get the full context injection for the AI right now."""
        parts = [
            "# SRT-1 Codebase Intelligence",
            "",
            f"Repository: {os.path.basename(self.repo_path)}",
            f"Synopsis: {self.synopsis}",
            "",
        ]

        if self.current_task:
            parts.append(f"ACTIVE TASK: {self.current_task}")
            parts.append("Stay focused on this task. Do not drift.")
            parts.append("")

        # Curation warnings
        warnings = []
        for ov in self.curation_report.get("functional_overlaps", []):
            func = ov["instances"][0]["function"]
            canon = ov.get("canonical", "")
            warnings.append(f"'{func}()' exists at {canon}. Don't duplicate.")

        if warnings:
            parts.append("WARNINGS:")
            for w in warnings:
                parts.append(f"  - {w}")
            parts.append("")

        # Key symbols
        parts.append("CODE MAP:")
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                if sym["name"] in ("__init__", "__post_init__"):
                    continue
                ref = sym.get("reflection", {})
                purpose = ref.get("purpose", "")
                risk = ref.get("risk_profile", [])
                risk_s = f" [{', '.join(risk)}]" if risk and risk != ["LOW_RISK"] else ""
                if purpose:
                    parts.append(f"  {sym['name']} ({fpath}:{sym['line']}): {purpose[:80]}{risk_s}")

        return "\n".join(parts)

    def _task_keywords(self) -> List[str]:
        if not self.current_task:
            return ["code", "development"]
        noise = {"a","an","the","to","in","on","at","for","of","and","or","is",
                 "it","my","i","we","do","that","this","with","from","into"}
        words = self.current_task.lower().replace(",", " ").split()
        kw = [w for w in words if w not in noise and len(w) > 2]
        kw.extend(["code", "development", "task", "function"])
        return list(set(kw))


# =============================================================================
# MCP PROTOCOL HANDLER (JSON-RPC 2.0 over stdin/stdout)
# =============================================================================

class MCPServer:
    """
    MCP Server implementing the Model Context Protocol.
    Communicates via JSON-RPC 2.0 over stdin/stdout.

    This is what Claude Desktop and Cursor call automatically.
    """

    def __init__(self, engine: SCIAMCPEngine):
        self.engine = engine

    def run(self) -> None:
        """Main loop: read JSON-RPC from stdin, respond on stdout."""
        # Read header-delimited messages (Content-Length protocol)
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                # Parse Content-Length header
                if line.startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())
                    sys.stdin.readline()  # Empty line after header
                    body = sys.stdin.read(content_length)
                    request = json.loads(body)
                    response = self._handle_request(request)
                    if response:
                        self._send(response)
                elif line.strip():
                    # Try raw JSON (some clients don't use Content-Length)
                    try:
                        request = json.loads(line)
                        response = self._handle_request(request)
                        if response:
                            self._send(response)
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass

    def _send(self, data: Dict) -> None:
        """Send a JSON-RPC response."""
        body = json.dumps(data)
        message = f"Content-Length: {len(body)}\r\n\r\n{body}"
        sys.stdout.write(message)
        sys.stdout.flush()

    def _handle_request(self, request: Dict) -> Optional[Dict]:
        """Route JSON-RPC requests."""
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            return self._rpc_response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                },
                "serverInfo": {
                    "name": "srt1",
                    "version": "2.0.0",
                },
            })

        elif method == "notifications/initialized":
            return None  # No response needed

        elif method == "tools/list":
            return self._rpc_response(req_id, {
                "tools": [
                    {
                        "name": "srt1_get_context",
                        "description": (
                            "Get SRT-1 codebase intelligence. Call this BEFORE making "
                            "any changes to understand what already exists in the codebase. "
                            "Returns a synopsis, code map, warnings about duplicated code, "
                            "and risk tags. ALWAYS call this before creating new functions."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                    {
                        "name": "srt1_log_interaction",
                        "description": (
                            "Log an interaction with SRT-1. Call this after EVERY action "
                            "you take — reading a file, writing code, making a decision. "
                            "SRT-1 monitors these interactions and fires a reflection "
                            "checkpoint every 3 actions to check if you're still on task. "
                            "If you've drifted, it will tell you."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "description": {
                                    "type": "string",
                                    "description": "What you just did or are about to do",
                                },
                                "files": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Files touched or discussed",
                                },
                            },
                            "required": ["description"],
                        },
                    },
                    {
                        "name": "srt1_set_task",
                        "description": (
                            "Set the developer's current task. This plants the seed — "
                            "everything from this point is measured against this task "
                            "for coherence. Call this when the user gives a new instruction."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task": {
                                    "type": "string",
                                    "description": "The developer's task/instruction",
                                },
                            },
                            "required": ["task"],
                        },
                    },
                    {
                        "name": "srt1_check_function",
                        "description": (
                            "Check if a function already exists in the codebase before "
                            "creating a new one. Returns the existing location, purpose, "
                            "and risk tags if found. ALWAYS call this before defining "
                            "a new function."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "function_name": {
                                    "type": "string",
                                    "description": "Name of the function to check",
                                },
                            },
                            "required": ["function_name"],
                        },
                    },
                    {
                        "name": "srt1_generate_blueprint",
                        "description": (
                            "Generate a detailed development blueprint from a seed idea. "
                            "SRT-1 knows the entire codebase and will generate a "
                            "comprehensive prompt that includes: what to build, what "
                            "already exists, risk areas, architectural patterns to follow, "
                            "and duplication warnings. Use this when starting a new feature."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "seed": {
                                    "type": "string",
                                    "description": "The idea/feature to generate a blueprint for",
                                },
                            },
                            "required": ["seed"],
                        },
                    },
                ],
            })

        elif method == "tools/call":
            tool_name = params.get("name", "")
            args = params.get("arguments", {})
            return self._handle_tool_call(req_id, tool_name, args)

        elif method == "resources/list":
            return self._rpc_response(req_id, {
                "resources": [
                    {
                        "uri": "srt1://synopsis",
                        "name": "Codebase Synopsis",
                        "description": "Plain-English summary of the entire codebase",
                        "mimeType": "text/plain",
                    },
                    {
                        "uri": "srt1://context",
                        "name": "Full SRT-1 Context",
                        "description": "Complete codebase intelligence for the AI",
                        "mimeType": "text/plain",
                    },
                ],
            })

        elif method == "resources/read":
            uri = params.get("uri", "")
            return self._handle_resource_read(req_id, uri)

        # Unknown method
        return self._rpc_response(req_id, None, error={
            "code": -32601, "message": f"Unknown method: {method}"
        })

    def _handle_tool_call(self, req_id, tool_name: str, args: Dict) -> Dict:
        """Handle MCP tool calls."""

        if tool_name == "srt1_get_context":
            context = self.engine.get_context()
            return self._rpc_response(req_id, {
                "content": [{"type": "text", "text": context}],
            })

        elif tool_name == "srt1_log_interaction":
            desc = args.get("description", "")
            files = args.get("files", [])
            result = self.engine.log_interaction(
                role="assistant", content=desc, files=files
            )

            response_text = result["message"]
            if result.get("checkpoint"):
                cp = result["checkpoint"]
                response_text = cp["directive"]

            return self._rpc_response(req_id, {
                "content": [{"type": "text", "text": response_text}],
            })

        elif tool_name == "srt1_set_task":
            task = args.get("task", "")
            result = self.engine.set_task(task)
            return self._rpc_response(req_id, {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            })

        elif tool_name == "srt1_check_function":
            func_name = args.get("function_name", "")
            found = []

            for fpath, symbols in self.engine.symbol_table.items():
                for sym in symbols:
                    if sym["name"].lower() == func_name.lower():
                        ref = sym.get("reflection", {})
                        found.append({
                            "file": fpath,
                            "line": sym["line"],
                            "type": sym["type"],
                            "purpose": ref.get("purpose", "Unknown"),
                            "risk": ref.get("risk_profile", []),
                            "params": sym.get("parameters", []),
                        })

            if found:
                text = f"YES — '{func_name}' already exists:\n\n"
                for f in found:
                    risk_s = ", ".join(f["risk"]) if f["risk"] else "LOW_RISK"
                    text += (
                        f"  Location: {f['file']}:{f['line']}\n"
                        f"  Type: {f['type']}\n"
                        f"  Purpose: {f['purpose']}\n"
                        f"  Risk: {risk_s}\n"
                        f"  Params: {', '.join(f['params'])}\n\n"
                    )
                text += "DO NOT create a new version. Import and use the existing one."
            else:
                text = f"No — '{func_name}' does not exist in the codebase. Safe to create."

            return self._rpc_response(req_id, {
                "content": [{"type": "text", "text": text}],
            })

        elif tool_name == "srt1_generate_blueprint":
            seed_text = args.get("seed", "")
            result = self.engine.generate_blueprint(seed_text)
            return self._rpc_response(req_id, {
                "content": [{"type": "text", "text": result["blueprint"]}],
            })

        return self._rpc_response(req_id, None, error={
            "code": -32601, "message": f"Unknown tool: {tool_name}"
        })

    def _handle_resource_read(self, req_id, uri: str) -> Dict:
        """Handle MCP resource reads."""
        if uri == "srt1://synopsis":
            return self._rpc_response(req_id, {
                "contents": [{
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": self.engine.synopsis,
                }],
            })
        elif uri == "srt1://context":
            return self._rpc_response(req_id, {
                "contents": [{
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": self.engine.get_context(),
                }],
            })

        return self._rpc_response(req_id, None, error={
            "code": -32602, "message": f"Unknown resource: {uri}"
        })

    @staticmethod
    def _rpc_response(req_id, result=None, error=None) -> Dict:
        """Build a JSON-RPC 2.0 response."""
        resp: Dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}
        if error:
            resp["error"] = error
        else:
            resp["result"] = result
        return resp


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    repo_path = os.environ.get("SRT1_REPO_PATH", ".")

    # Log startup to stderr (stdin/stdout reserved for MCP protocol)
    sys.stderr.write(f"[SRT-1 MCP] Starting with repo: {repo_path}\n")
    sys.stderr.flush()

    engine = SCIAMCPEngine(repo_path)

    sys.stderr.write(f"[SRT-1 MCP] Indexed {len(engine.manifest.get('file_manifest', []))} files, "
                     f"{sum(len(s) for s in engine.symbol_table.values())} symbols\n")
    sys.stderr.write(f"[SRT-1 MCP] Ready. Waiting for AI tool connections.\n")
    sys.stderr.flush()

    server = MCPServer(engine)
    server.run()


if __name__ == "__main__":
    main()
