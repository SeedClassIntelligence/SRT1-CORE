"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: CLI_ENTRY_POINT, SERVICE_LAYER, DATA_MODEL
Key Symbols: SCIARemoteAuth, main, __init__, generate_token, revoke_token ... and 11 more

Extracted Purposes:
  - SCIARemoteAuth: Token-based authentication for remote SRT-1 access.
  - main: CLI for managing SRT-1 remote auth tokens.
  - __init__: Args:
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 Remote Authentication Module
====================================

Secure, token-based authentication for remote SRT-1 access.
This is NOT ClawBot — SRT-1 doesn't need full system access.
It partners with AI assistants, it doesn't own the machine.

Security Model:
    - API tokens are generated per-project and stored locally
    - Tokens are hashed with SHA-256 before storage (never stored raw)
    - Rate limiting prevents brute force attempts
    - Public endpoints (/health) remain open
    - All other endpoints require Bearer token
    - Token rotation supported (revoke + regenerate)

Usage:
    auth = SCIARemoteAuth(project_name="my-project")
    token = auth.generate_token()  # Give this to the mobile app
    
    # In the HTTP handler:
    if not auth.authenticate(request_headers):
        return 401

Author : William Darnell Jernigan IV (Architect)
License: Business Source License 1.1
"""

import os
import json
import time
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger("srt1.auth")


class SCIARemoteAuth:
    """
    Token-based authentication for remote SRT-1 access.
    
    Generates, validates, and manages API tokens that allow
    mobile devices and remote clients to securely interact
    with SRT-1 without full system access.
    """

    # Endpoints that don't require authentication
    PUBLIC_ENDPOINTS = {"/health", "/"}

    # Rate limiting: max requests per window
    RATE_LIMIT_WINDOW = 60       # seconds
    RATE_LIMIT_MAX = 120          # requests per window
    RATE_LIMIT_BURST = 30        # max burst in 5 seconds

    # Token settings
    TOKEN_BYTE_LENGTH = 32       # 256-bit tokens
    TOKEN_PREFIX = "srt1_"       # Prefix for easy identification

    def __init__(self, project_name: str, auth_dir: Optional[str] = None):
        """
        Args:
            project_name: Name of the project this auth instance protects
            auth_dir: Directory to store auth data (default: ~/.srt1/auth/)
        """
        self.project_name = self._sanitize_name(project_name)

        if auth_dir:
            self.auth_dir = auth_dir
        else:
            self.auth_dir = os.path.join(os.path.expanduser("~"), ".srt1", "auth")
        os.makedirs(self.auth_dir, exist_ok=True)

        self.auth_file = os.path.join(self.auth_dir, f"{self.project_name}_tokens.json")

        # In-memory rate limiting
        self._rate_tracker: Dict[str, List[float]] = {}  # ip -> [timestamps]
        self._failed_attempts: Dict[str, List[float]] = {}  # ip -> [timestamps]

        # Load existing tokens
        self._tokens: Dict[str, Dict] = {}
        self._load_tokens()

    # -----------------------------------------------------------------
    # TOKEN GENERATION
    # -----------------------------------------------------------------

    def generate_token(self, label: str = "default", 
                       expires_days: Optional[int] = None) -> Dict[str, str]:
        """
        Generate a new API token for remote access.
        
        Args:
            label: Human-readable label (e.g., "mobile-app", "ci-server")
            expires_days: Optional expiry in days (None = never expires)
            
        Returns:
            Dict with 'token' (the raw token - show ONCE), 'token_id', 'label'
        """
        # Generate cryptographically secure token
        raw_token = self.TOKEN_PREFIX + secrets.token_urlsafe(self.TOKEN_BYTE_LENGTH)
        token_hash = self._hash_token(raw_token)
        token_id = f"tok_{secrets.token_hex(8)}"

        expires_at = None
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()

        # Store the hash, never the raw token
        self._tokens[token_id] = {
            "token_hash": token_hash,
            "label": label,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "last_used": None,
            "use_count": 0,
            "revoked": False,
            "permissions": ["read", "write", "seed"],  # All permissions by default
        }
        self._save_tokens()

        logger.info(f"Generated token '{label}' (ID: {token_id}) for project '{self.project_name}'")

        return {
            "token": raw_token,  # Show this ONCE to the user
            "token_id": token_id,
            "label": label,
            "expires_at": expires_at,
            "message": "⚠️ Save this token NOW. It will never be shown again.",
        }

    def revoke_token(self, token_id: str) -> bool:
        """Revoke a token by its ID."""
        if token_id in self._tokens:
            self._tokens[token_id]["revoked"] = True
            self._tokens[token_id]["revoked_at"] = datetime.now().isoformat()
            self._save_tokens()
            logger.info(f"Revoked token {token_id}")
            return True
        return False

    def list_tokens(self) -> List[Dict]:
        """List all tokens (without hashes) for management."""
        result = []
        for tid, data in self._tokens.items():
            result.append({
                "token_id": tid,
                "label": data["label"],
                "created_at": data["created_at"],
                "expires_at": data["expires_at"],
                "last_used": data["last_used"],
                "use_count": data["use_count"],
                "revoked": data["revoked"],
                "active": self._is_token_active(data),
            })
        return result

    def rotate_token(self, token_id: str, 
                     expires_days: Optional[int] = None) -> Optional[Dict]:
        """Revoke old token and generate a new one with the same label."""
        if token_id not in self._tokens:
            return None

        old_label = self._tokens[token_id]["label"]
        self.revoke_token(token_id)
        return self.generate_token(label=old_label, expires_days=expires_days)

    # -----------------------------------------------------------------
    # AUTHENTICATION
    # -----------------------------------------------------------------

    def authenticate(self, headers: Dict[str, str], 
                     client_ip: str = "127.0.0.1",
                     endpoint: str = "/") -> Tuple[bool, Optional[str]]:
        """
        Authenticate a request.
        
        Args:
            headers: HTTP request headers (must contain 'Authorization')
            client_ip: Client IP for rate limiting
            endpoint: The endpoint being accessed
            
        Returns:
            Tuple of (authenticated: bool, error_message: Optional[str])
        """
        # Public endpoints don't need auth
        if endpoint in self.PUBLIC_ENDPOINTS:
            return True, None

        # Check rate limiting first
        rate_ok, rate_msg = self._check_rate_limit(client_ip)
        if not rate_ok:
            return False, rate_msg

        # No tokens configured = auth disabled (first-run experience)
        if not self._tokens:
            return True, None

        # Extract token from Authorization header
        auth_header = headers.get("Authorization", "") or headers.get("authorization", "")
        if not auth_header:
            self._record_failed_attempt(client_ip)
            return False, "Missing Authorization header. Use: Authorization: Bearer <token>"

        if not auth_header.startswith("Bearer "):
            self._record_failed_attempt(client_ip)
            return False, "Invalid Authorization format. Use: Bearer <token>"

        raw_token = auth_header[7:].strip()
        if not raw_token:
            self._record_failed_attempt(client_ip)
            return False, "Empty token"

        # Validate the token
        token_hash = self._hash_token(raw_token)
        matched_id = None

        for tid, data in self._tokens.items():
            if data["token_hash"] == token_hash:
                matched_id = tid
                break

        if not matched_id:
            self._record_failed_attempt(client_ip)
            return False, "Invalid token"

        token_data = self._tokens[matched_id]

        # Check if active
        if not self._is_token_active(token_data):
            if token_data.get("revoked"):
                return False, "Token has been revoked"
            return False, "Token has expired"

        # Token is valid — update usage stats
        token_data["last_used"] = datetime.now().isoformat()
        token_data["use_count"] += 1

        # Save periodically (every 10 uses to avoid excessive IO)
        if token_data["use_count"] % 10 == 0:
            self._save_tokens()

        return True, None

    # -----------------------------------------------------------------
    # RATE LIMITING
    # -----------------------------------------------------------------

    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """Check if a client IP has exceeded rate limits."""
        now = time.time()

        # Check for too many failed attempts (lockout)
        if client_ip in self._failed_attempts:
            recent_failures = [t for t in self._failed_attempts[client_ip] 
                             if now - t < 300]  # 5-minute window
            self._failed_attempts[client_ip] = recent_failures
            if len(recent_failures) >= 10:
                return False, "Too many failed attempts. Locked out for 5 minutes."

        # Standard rate limiting
        if client_ip not in self._rate_tracker:
            self._rate_tracker[client_ip] = []

        # Clean old entries
        self._rate_tracker[client_ip] = [
            t for t in self._rate_tracker[client_ip] 
            if now - t < self.RATE_LIMIT_WINDOW
        ]

        # Check window limit
        if len(self._rate_tracker[client_ip]) >= self.RATE_LIMIT_MAX:
            return False, f"Rate limit exceeded ({self.RATE_LIMIT_MAX}/min). Try again later."

        # Check burst limit
        recent_burst = [t for t in self._rate_tracker[client_ip] if now - t < 5]
        if len(recent_burst) >= self.RATE_LIMIT_BURST:
            return False, "Burst limit exceeded. Slow down."

        # Record this request
        self._rate_tracker[client_ip].append(now)
        return True, None

    def _record_failed_attempt(self, client_ip: str) -> None:
        """Record a failed authentication attempt."""
        if client_ip not in self._failed_attempts:
            self._failed_attempts[client_ip] = []
        self._failed_attempts[client_ip].append(time.time())

    # -----------------------------------------------------------------
    # TOKEN HELPERS
    # -----------------------------------------------------------------

    def _hash_token(self, raw_token: str) -> str:
        """Hash a token with SHA-256. We never store raw tokens."""
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def _is_token_active(self, token_data: Dict) -> bool:
        """Check if a token is still active (not revoked, not expired)."""
        if token_data.get("revoked"):
            return False
        expires = token_data.get("expires_at")
        if expires:
            try:
                exp_time = datetime.fromisoformat(expires)
                if datetime.now() > exp_time:
                    return False
            except ValueError:
                pass
        return True

    def _sanitize_name(self, name: str) -> str:
        """Sanitize project name for filesystem use."""
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        return safe[:64]

    # -----------------------------------------------------------------
    # PERSISTENCE
    # -----------------------------------------------------------------

    def _load_tokens(self) -> None:
        """Load tokens from disk."""
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, "r", encoding="utf-8") as f:
                    self._tokens = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._tokens = {}

    def _save_tokens(self) -> None:
        """Save tokens to disk."""
        try:
            with open(self.auth_file, "w", encoding="utf-8") as f:
                json.dump(self._tokens, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save tokens: {e}")

    # -----------------------------------------------------------------
    # AUTH MIDDLEWARE FOR HTTP HANDLER
    # -----------------------------------------------------------------

    def wrap_handler(self, handler_method):
        """
        Decorator-style wrapper for HTTP handler methods.
        
        Usage in the SRT-1 HTTP server:
            def do_GET(self):
                ok, err = auth.authenticate(dict(self.headers), endpoint=path)
                if not ok:
                    self._json({"error": err}, 401)
                    return
                # ... normal handling
        """
        pass  # The integration happens in srt1.py directly


# =============================================================================
# CLI for token management
# =============================================================================

def main():
    """CLI for managing SRT-1 remote auth tokens."""
    import argparse

    parser = argparse.ArgumentParser(
        description="SRT-1 Remote Authentication — Token Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n\n"
            "  Generate a token for mobile access:\n"
            "    python srt1_remote_auth.py generate --project my-app --label mobile\n\n"
            "  List all tokens:\n"
            "    python srt1_remote_auth.py list --project my-app\n\n"
            "  Revoke a token:\n"
            "    python srt1_remote_auth.py revoke --project my-app --token-id tok_abc123\n\n"
            "  Rotate a token:\n"
            "    python srt1_remote_auth.py rotate --project my-app --token-id tok_abc123\n"
        ),
    )

    sub = parser.add_subparsers(dest="command", help="Command to run")

    # Generate
    gen = sub.add_parser("generate", help="Generate a new API token")
    gen.add_argument("--project", required=True, help="Project name")
    gen.add_argument("--label", default="default", help="Token label (e.g., 'mobile', 'ci')")
    gen.add_argument("--expires-days", type=int, help="Token expiry in days")

    # List
    lst = sub.add_parser("list", help="List all tokens")
    lst.add_argument("--project", required=True, help="Project name")

    # Revoke
    rev = sub.add_parser("revoke", help="Revoke a token")
    rev.add_argument("--project", required=True, help="Project name")
    rev.add_argument("--token-id", required=True, help="Token ID to revoke")

    # Rotate
    rot = sub.add_parser("rotate", help="Rotate (revoke + regenerate) a token")
    rot.add_argument("--project", required=True, help="Project name")
    rot.add_argument("--token-id", required=True, help="Token ID to rotate")
    rot.add_argument("--expires-days", type=int, help="New token expiry in days")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    auth = SCIARemoteAuth(project_name=args.project)

    if args.command == "generate":
        result = auth.generate_token(label=args.label, expires_days=args.expires_days)
        print()
        print("  ╔══════════════════════════════════════════════════════╗")
        print("  ║           SRT-1 API Token Generated                 ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print()
        print(f"  Token ID:  {result['token_id']}")
        print(f"  Label:     {result['label']}")
        print(f"  Expires:   {result['expires_at'] or 'Never'}")
        print()
        print(f"  🔑 YOUR TOKEN (save this — shown ONCE):")
        print(f"     {result['token']}")
        print()
        print(f"  Usage:")
        print(f"     curl -H 'Authorization: Bearer {result['token']}' http://your-srt1/status")
        print()

    elif args.command == "list":
        tokens = auth.list_tokens()
        if not tokens:
            print("  No tokens found.")
            return
        print()
        print(f"  Tokens for project '{args.project}':")
        print(f"  {'─' * 70}")
        for t in tokens:
            status = "✅ active" if t["active"] else "❌ inactive"
            uses = t["use_count"]
            last = t["last_used"] or "never"
            print(f"  {t['token_id']}  [{t['label']}]  {status}  uses={uses}  last={last}")
        print()

    elif args.command == "revoke":
        if auth.revoke_token(args.token_id):
            print(f"  ✅ Token {args.token_id} revoked.")
        else:
            print(f"  ❌ Token {args.token_id} not found.")

    elif args.command == "rotate":
        result = auth.rotate_token(args.token_id, expires_days=args.expires_days)
        if result:
            print(f"  ✅ Old token revoked. New token generated:")
            print(f"     Token ID: {result['token_id']}")
            print(f"     🔑 {result['token']}")
        else:
            print(f"  ❌ Token {args.token_id} not found.")


if __name__ == "__main__":
    main()
