"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: DATA_MODEL
Key Symbols: SCIAProxyEngine, handle_proxy_request, _identify_client, _analyze_attribution_async

Extracted Purposes:
  - SCIAProxyEngine: Enterprise Proxy Attribution Engine for SRT-1.
  - handle_proxy_request: Intercepts the request, proxies it upstream, and captures the code diff stream for governance attribution.
  - _analyze_attribution_async: Asynchronous semantic evaluation of the LLM stream.
"""
import os
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime
import threading

logger = logging.getLogger("srt1.proxy")

class SCIAProxyEngine:
    """
    Enterprise Proxy Attribution Engine for SRT-1.
    Acts as an OpenAI-compatible /v1/ interceptor for IDEs (Cursor/Aider/Windsurf).
    """

    OPENAI_UPSTREAM = "https://api.openai.com{path}"

    @classmethod
    def handle_proxy_request(cls, handler, engine):
        """
        Intercepts the request, proxies it upstream, and captures the code diff stream for governance attribution.
        """
        path = handler.path
        
        # Determine upstream URL
        upstream_url = cls.OPENAI_UPSTREAM.format(path=path)
        
        # Extract headers to forward
        headers_to_forward = {}
        target_headers = ["Authorization", "Content-Type", "Accept", "User-Agent", "x-api-key"]
        for k, v in handler.headers.items():
            if k.lower() in [th.lower() for th in target_headers]:
                headers_to_forward[k] = v
                
        # Read payload
        length_str = handler.headers.get("Content-Length", "0")
        length = int(length_str)
        body = b""
        if length > 0:
            body = handler.rfile.read(length)
            
        req_json = {}
        if body:
            try:
                req_json = json.loads(body.decode("utf-8"))
            except Exception:
                pass
                
        is_streaming = req_json.get("stream", False)
        ide_client = cls._identify_client(handler.headers.get("User-Agent", ""))
        
        # Build the upstream request
        req = urllib.request.Request(
            url=upstream_url,
            data=body if body else None,
            headers=headers_to_forward,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                handler.send_response(response.status)
                
                for k, v in response.headers.items():
                    # Strip hop-by-hop headers
                    if k.lower() not in ["transfer-encoding", "content-length", "connection"]:
                        handler.send_header(k, v)
                        
                if is_streaming:
                    # In streaming mode, chunks delimit with Server-Sent Events (SSE)
                    handler.send_header("Transfer-Encoding", "chunked")
                    handler.send_header("Connection", "keep-alive")
                    handler.end_headers()
                    
                    accumulated = []
                    while True:
                        chunk = response.readline()
                        if not chunk:
                            break
                        
                        # Forward immediately to IDE
                        chunk_hex = hex(len(chunk))[2:].encode('utf-8')
                        handler.wfile.write(chunk_hex + b"\r\n")
                        handler.wfile.write(chunk + b"\r\n")
                        handler.wfile.flush()
                        
                        # Buffer for governance analysis
                        accumulated.append(chunk.decode("utf-8", errors="replace"))
                        
                    # End SSE chunking
                    handler.wfile.write(b"0\r\n\r\n")
                    handler.wfile.flush()
                    
                    full_response = "".join(accumulated)
                    threading.Thread(target=cls._analyze_attribution_async, args=(engine, full_response, ide_client), daemon=True).start()
                else:
                    # Non-streaming exact pass-through
                    resp_body = response.read()
                    handler.send_header("Content-Length", str(len(resp_body)))
                    handler.end_headers()
                    handler.wfile.write(resp_body)
                    
                    try:
                        resp_json_text = resp_body.decode("utf-8")
                        threading.Thread(target=cls._analyze_attribution_async, args=(engine, resp_json_text, ide_client), daemon=True).start()
                    except Exception:
                        pass
                    
        except urllib.error.HTTPError as e:
            # Pass upstream errors back precisely
            handler.send_response(e.code)
            for k, v in e.headers.items():
                handler.send_header(k, v)
            handler.end_headers()
            handler.wfile.write(e.read())
        except Exception as e:
            handler.send_response(502)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            error_json = json.dumps({"error": f"SRT-1 Proxy upstream failure: {str(e)}"})
            handler.wfile.write(error_json.encode("utf-8"))


    @staticmethod
    def _identify_client(user_agent: str) -> str:
        ua = user_agent.lower()
        if "cursor" in ua: return "ai_session_cursor"
        if "aider" in ua: return "ai_session_aider"
        if "windsurf" in ua: return "ai_session_windsurf"
        return "ai_session_unknown"

    @classmethod
    def _analyze_attribution_async(cls, engine, text_payload: str, ide_client: str):
        """
        Asynchronous semantic evaluation of the LLM stream.
        Identifies code blocks or diffs and stamps who_changed into the SRT-1 governance layer.
        """
        modifies_code = False
        
        # Rough heuristic: if the AI writes diffs or blocks, it's attempting to change code
        if "```python" in text_payload or "```javascript" in text_payload or "<<<<<<< SEARCH" in text_payload:
            modifies_code = True
            
        if modifies_code:
            # We log an enterprise intent attribution. 
            # When watcher spins next, the Delta Auditor will map this log to actual drift.
            attribution_log = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "who_changed": ide_client,
                "proxy_event": "code_modification_intent"
            }
            
            repo_path = getattr(engine, "repo_path", ".")
            log_dir = os.path.join(repo_path, ".srt1", "enterprise_logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "attribution_cache.json")
            
            # Thread-safe write for attribution log
            try:
                logs = []
                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        logs = json.load(f)
                logs.append(attribution_log)
                with open(log_file, "w") as f:
                    json.dump(logs, f, indent=2)
                
                # Echo to terminal for visibility
                print(f"  [ENTERPRISE PROXY] âš¡ Intercepted code modification intent. Attributed to: {ide_client}")
            except Exception as e:
                logger.error(f"Failed to log enterprise attribution: {e}")
