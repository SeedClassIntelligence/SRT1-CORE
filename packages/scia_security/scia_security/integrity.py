"""
SCIA Integrity Validator — Content hash verification utilities.

Provides SHA-256 content hashing, tamper detection, and hash
comparison for any SCIA system. This is a LOCAL utility for
integrity checking only.

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

import hashlib
import json
import os
from typing import Dict, Any


class IntegrityValidator:
    """Content integrity utilities — hash, compare, detect tampering."""

    @staticmethod
    def hash_content(content: str) -> str:
        """SHA-256 hash of string content (first 16 hex chars)."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def hash_dict(data: Dict[str, Any]) -> str:
        """SHA-256 hash of a JSON-serializable dict (deterministic)."""
        content_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_file(file_path: str) -> str:
        """SHA-256 hash of a file's raw bytes."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def verify_content(content: str, expected_hash: str) -> bool:
        """Check if content matches an expected hash."""
        actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return actual.startswith(expected_hash)

    @staticmethod
    def verify_file(file_path: str, expected_hash: str) -> bool:
        """Check if a file matches an expected hash."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest() == expected_hash

    @staticmethod
    def verify_dict(data: Dict[str, Any], expected_hash: str) -> bool:
        """Check if a dict matches an expected hash."""
        content_str = json.dumps(data, sort_keys=True, default=str)
        actual = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
        return actual == expected_hash

    @staticmethod
    def compute_checksum(file_path: str) -> Dict[str, str]:
        """Compute multiple checksums for a file."""
        sha256 = hashlib.sha256()
        md5 = hashlib.md5()
        size = 0
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
                md5.update(chunk)
                size += len(chunk)
        return {
            "sha256": sha256.hexdigest(),
            "md5": md5.hexdigest(),
            "size_bytes": str(size),
            "file_name": os.path.basename(file_path),
        }

    @staticmethod
    def detect_tampering(
        original_hash: str, current_content: str
    ) -> Dict[str, Any]:
        """Compare current content against a known-good hash."""
        current_hash = hashlib.sha256(
            current_content.encode("utf-8")
        ).hexdigest()
        tampered = current_hash != original_hash
        return {
            "tampered": tampered,
            "original_hash": original_hash,
            "current_hash": current_hash,
            "status": "MODIFIED" if tampered else "INTACT",
        }
