"""
SCIA Signing Service Client — calls the private signing authority.

This client calls a remote signing service API to request signatures
and verify content. It does not contain signing logic. The signing
authority, provenance chain, and registry live on the service.

Usage:
    client = SigningServiceClient("http://localhost:7484")
    result = client.sign({"data": "to sign"}, phase="production")
    verified = client.verify({"data": "to sign"}, result)

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

import json
import os
from typing import Dict, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError


class SigningServiceClient:
    """HTTP client for the SCIA private signing service.

    All signing authority lives on the service. This client:
    - Sends content to the service to be signed
    - Sends signed content back to the service for verification
    - Retrieves signature records and chain state
    - Checks policy (merge/deploy decisions)

    The service runs the hashing, chain management, and registry.
    This client never signs locally.
    """

    def __init__(self, service_url: str = None, api_key: str = None):
        self.service_url = (
            service_url
            or os.environ.get("SCIA_SIGNING_SERVICE_URL", "http://localhost:7484")
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("SCIA_SIGNING_API_KEY", "")

    def _request(self, method: str, path: str,
                 body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the signing service."""
        url = f"{self.service_url}{path}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = json.dumps(body).encode() if body else None
        req = Request(url, data=data, headers=headers, method=method)

        try:
            with urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except URLError as e:
            return {"error": str(e), "service_url": self.service_url}

    # ── Signing ───────────────────────────────────────────────────────

    def sign(self, artifact: Dict[str, Any],
             signature_type: str = "comprehensive",
             phase: str = "unknown") -> Dict[str, Any]:
        """Request the service to sign an artifact."""
        return self._request("POST", "/sign", {
            "artifact": artifact,
            "signature_type": signature_type,
            "phase": phase,
        })

    # ── Verification ──────────────────────────────────────────────────

    def verify(self, artifact: Dict[str, Any],
               signature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify an artifact against its signature via the authority."""
        return self._request("POST", "/verify", {
            "artifact": artifact,
            "signature_data": signature_data,
        })

    # ── Lookup ────────────────────────────────────────────────────────

    def get_signature(self, signature_id: str) -> Dict[str, Any]:
        """Retrieve a signature record by ID."""
        return self._request("GET", f"/signature/{signature_id}")

    def get_lineage(self, signature_id: str) -> Dict[str, Any]:
        """Retrieve the lineage chain for a signature."""
        return self._request("GET", f"/lineage/{signature_id}")

    def get_chain(self) -> Dict[str, Any]:
        """Get the full signature chain."""
        return self._request("GET", "/chain")

    def check_chain_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the signature chain."""
        return self._request("GET", "/chain/integrity")

    # ── Policy ────────────────────────────────────────────────────────

    def check_policy(self, signature_id: str = None,
                     content_hash: str = None,
                     action: str = "merge") -> Dict[str, Any]:
        """Check if an item is allowed to merge or deploy."""
        body = {"action": action}
        if signature_id:
            body["signature_id"] = signature_id
        if content_hash:
            body["content_hash"] = content_hash
        return self._request("POST", "/policy/check", body)

    # ── Health ────────────────────────────────────────────────────────

    def health(self) -> Dict[str, Any]:
        """Check if the signing service is reachable."""
        return self._request("GET", "/health")

    def is_available(self) -> bool:
        """Quick check — is the service responding?"""
        result = self.health()
        return result.get("status") == "healthy"
