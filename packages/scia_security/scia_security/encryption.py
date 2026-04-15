"""
AES-256-GCM Encryption at Rest — Enterprise Grade

Encrypts data before it hits disk. Decrypts on read. Used by
RegenerativeMemory and ExecutionGraph to protect persisted data.

Key derivation: PBKDF2-HMAC-SHA256 from a master secret.
Cipher: AES-256-GCM (authenticated encryption — tamper detection built in).
Each encryption operation gets a unique 12-byte nonce.

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

import os
import base64
import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# Fixed salt for key derivation (per-deployment, not per-operation)
_DEFAULT_SALT = b"scia-encryption-salt-v1"


def derive_key(master_secret: str, salt: bytes = _DEFAULT_SALT) -> bytes:
    """Derive a 256-bit AES key from a master secret using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(master_secret.encode("utf-8"))


class DataEncryptor:
    """AES-256-GCM encryption for data at rest.

    Usage:
        enc = DataEncryptor("my-secret-key")
        ciphertext = enc.encrypt("sensitive data")
        plaintext = enc.decrypt(ciphertext)

    The encrypted output is a base64 string containing:
        nonce (12 bytes) + ciphertext + GCM tag (16 bytes)

    If no master_secret is provided, reads from SCIA_ENCRYPTION_KEY
    environment variable. If that's also missing, encryption is
    DISABLED and data passes through unencrypted (with a flag).
    """

    def __init__(self, master_secret: str = None):
        secret = master_secret or os.environ.get("SCIA_ENCRYPTION_KEY")
        if secret:
            self._key = derive_key(secret)
            self._aesgcm = AESGCM(self._key)
            self.enabled = True
        else:
            self._key = None
            self._aesgcm = None
            self.enabled = False

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string. Returns base64-encoded ciphertext.

        If encryption is disabled (no key), returns the plaintext
        prefixed with 'PLAIN:' so decrypt() knows to pass through.
        """
        if not self.enabled:
            return f"PLAIN:{plaintext}"

        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(
            nonce, plaintext.encode("utf-8"), None
        )
        # nonce + ciphertext packed together
        return "ENC:" + base64.b64encode(nonce + ciphertext).decode("ascii")

    def decrypt(self, data: str) -> str:
        """Decrypt a string. Handles both encrypted and plaintext data.

        If data starts with 'PLAIN:', returns the plaintext directly.
        If data starts with 'ENC:', decrypts with AES-256-GCM.
        """
        if data.startswith("PLAIN:"):
            return data[6:]

        if not data.startswith("ENC:"):
            # Legacy unencrypted data — return as-is
            return data

        if not self.enabled:
            raise ValueError(
                "Encrypted data found but no SCIA_ENCRYPTION_KEY set. "
                "Cannot decrypt without the key."
            )

        raw = base64.b64decode(data[4:])
        nonce = raw[:12]
        ciphertext = raw[12:]
        plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    def encrypt_dict(self, data: dict) -> str:
        """Encrypt a dict (serialized as JSON)."""
        return self.encrypt(json.dumps(data, default=str, sort_keys=True))

    def decrypt_dict(self, data: str) -> dict:
        """Decrypt back to a dict."""
        return json.loads(self.decrypt(data))
