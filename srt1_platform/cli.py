"""Public Core command line entrypoint for SRT-1.

This module is intentionally thin. It wraps the existing local engine,
dashboard, repository activation, and runtime registry without introducing a
new runtime architecture or dependency.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import webbrowser
from typing import Any, Dict, List, Optional


DEFAULT_PORT = 7484
DEFAULT_HOST = "127.0.0.1"


def _origin(port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> str:
    return f"http://{host}:{port}"


def _request_json(
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]] = None,
    timeout: float = 4.0,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    data = None
    request_headers = {"Accept": "application/json"}
    request_headers.update(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def _runtime_session_headers(origin: str) -> Dict[str, str]:
    session = _request_json("GET", f"{origin}/api/v1/runtime/session")
    token = session.get("session_token")
    return {"X-SRT1-Session": str(token), "X-SRT1-Request": "cli"} if token else {}


def _active_engines() -> List[Dict[str, Any]]:
    try:
        from srt1_platform.operational_registry import OperationalRegistry

        registry = OperationalRegistry()
        return registry.get_active_engines()
    except Exception:
        return []


def _select_engine(port: Optional[int] = None, repo_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    engines = _active_engines()
    if port is not None:
        for engine in engines:
            if int(engine.get("port") or 0) == int(port):
                return engine
        return None
    if repo_path:
        target = os.path.realpath(repo_path)
        for engine in engines:
            if os.path.realpath(engine.get("workspace_path", "")) == target:
                return engine
        return None
    return engines[0] if engines else None


def _print_json(data: Dict[str, Any]) -> int:
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def command_start(args: argparse.Namespace) -> int:
    from srt1_code_indexer.engine import SRT1Engine, init_db

    repo_path = os.path.realpath(args.repo)
    init_db()
    engine = SRT1Engine(repo_path=repo_path, task=args.task, port=args.port)
    print(f"SRT-1 starting for {repo_path}")
    print(f"Dashboard: {_origin(args.port)}/dashboard")
    engine.start()
    return 0


def command_dashboard(args: argparse.Namespace) -> int:
    engine = _select_engine(port=args.port, repo_path=args.repo)
    port = args.port or int((engine or {}).get("port") or DEFAULT_PORT)
    url = f"{_origin(port)}/dashboard"
    if not args.no_open:
        webbrowser.open(url)
    print(url)
    return 0


def command_status(args: argparse.Namespace) -> int:
    engine = _select_engine(port=args.port, repo_path=args.repo)
    if not engine:
        payload = {
            "status": "stopped",
            "message": "No active SRT-1 runtime found.",
            "active_engines": [],
        }
        if args.json:
            return _print_json(payload)
        print(payload["message"])
        return 0

    port = int(engine.get("port") or DEFAULT_PORT)
    origin = _origin(port)
    status: Dict[str, Any]
    try:
        status = _request_json("GET", f"{origin}/status")
    except Exception as exc:
        status = {"status": "unreachable", "error": str(exc)}

    payload = {
        "status": "running" if status.get("status") != "unreachable" else "unreachable",
        "dashboard": f"{origin}/dashboard",
        "engine": engine,
        "engine_status": status,
    }
    if args.json:
        return _print_json(payload)

    active_seed = status.get("active_seed") or {}
    print(f"SRT-1: {payload['status']}")
    print(f"Dashboard: {payload['dashboard']}")
    print(f"Repository: {engine.get('workspace_name') or 'unknown'}")
    print(f"Path: {engine.get('workspace_path') or 'unknown'}")
    print(f"Port: {port}")
    if engine.get("pid"):
        print(f"PID: {engine.get('pid')}")
    if status.get("codebase_files") is not None:
        print(f"Files: {status.get('codebase_files')}")
    if status.get("codebase_symbols") is not None:
        print(f"Symbols: {status.get('codebase_symbols')}")
    if active_seed:
        seed_id = active_seed.get("queue_seed_id") or active_seed.get("seed_id") or "unknown"
        state = active_seed.get("lifecycle_state") or active_seed.get("stage") or "unknown"
        print(f"Active seed: {seed_id} ({state})")
    return 0


def command_stop(args: argparse.Namespace) -> int:
    engine = _select_engine(port=args.port, repo_path=args.repo)
    if not engine:
        print("No active SRT-1 runtime found.")
        return 0

    port = int(engine.get("port") or DEFAULT_PORT)
    origin = _origin(port)
    try:
        result = _request_json(
            "POST",
            f"{origin}/api/v1/runtime/shutdown",
            payload={},
            headers=_runtime_session_headers(origin),
        )
    except urllib.error.URLError as exc:
        print(f"SRT-1 runtime on port {port} did not accept shutdown: {exc}")
        return 1
    except Exception as exc:
        print(f"SRT-1 shutdown failed: {exc}")
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def command_register(args: argparse.Namespace) -> int:
    engine = _select_engine(port=args.port)
    if not engine:
        print("No active SRT-1 runtime found. Start SRT-1 before registering repositories.")
        return 1

    repo_path = os.path.realpath(args.path)
    port = int(engine.get("port") or DEFAULT_PORT)
    origin = _origin(port)
    try:
        result = _request_json(
            "POST",
            f"{origin}/api/v1/repositories/register-path",
            payload={"path": repo_path},
            headers=_runtime_session_headers(origin),
        )
    except Exception as exc:
        print(f"Repository registration failed: {exc}")
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") in {"registered", "ready"} else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="srt1",
        description="SRT-1 Core command line tools",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start the local SRT-1 runtime")
    start.add_argument("--repo", "--repo-path", dest="repo", default=".", help="Repository path to manage")
    start.add_argument("--port", type=int, default=DEFAULT_PORT, help="Runtime port")
    start.add_argument("--task", help="Optional active task/seed text")
    start.set_defaults(func=command_start)

    status = sub.add_parser("status", help="Show active SRT-1 runtime status")
    status.add_argument("--repo", "--repo-path", dest="repo", help="Filter by repository path")
    status.add_argument("--port", type=int, help="Filter by runtime port")
    status.add_argument("--json", action="store_true", help="Print full runtime status JSON")
    status.set_defaults(func=command_status)

    dashboard = sub.add_parser("dashboard", help="Open the SRT-1 dashboard")
    dashboard.add_argument("--repo", "--repo-path", dest="repo", help="Open dashboard for repository path")
    dashboard.add_argument("--port", type=int, help="Open dashboard for runtime port")
    dashboard.add_argument("--no-open", action="store_true", help="Print URL without opening a browser")
    dashboard.set_defaults(func=command_dashboard)

    register = sub.add_parser("register", help="Register a local repository path with the active runtime")
    register.add_argument("path", help="Repository path to register")
    register.add_argument("--port", type=int, help="Runtime port to register through")
    register.set_defaults(func=command_register)

    stop = sub.add_parser("stop", help="Stop a local SRT-1 runtime")
    stop.add_argument("--repo", "--repo-path", dest="repo", help="Stop runtime for repository path")
    stop.add_argument("--port", type=int, help="Stop runtime on a specific port")
    stop.set_defaults(func=command_stop)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
