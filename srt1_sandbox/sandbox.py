"""
SRT-1 Sandbox Policy — Logical Isolation Definitions

Defines the types of sandboxes and their default policies.
No Docker, no VM — enforced through manifest-governed context injection.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class SandboxType(Enum):
    REPO = "repo"
    FOLDER = "folder"
    COMPONENT = "component"
    FILE = "file"
    PATCH = "patch"


@dataclass
class SandboxPolicy:
    """Defines what a sandbox allows and forbids."""

    sandbox_type: SandboxType
    read_patterns: List[str] = field(default_factory=list)
    write_patterns: List[str] = field(default_factory=list)
    forbidden_patterns: List[str] = field(default_factory=list)
    max_files: int = 0
    max_lines_changed: int = 0
    require_approval_above: int = 0

    @classmethod
    def repo_default(cls) -> "SandboxPolicy":
        return cls(
            sandbox_type=SandboxType.REPO,
            read_patterns=["**/*"],
            write_patterns=["**/*.py", "**/*.js", "**/*.ts", "**/*.html", "**/*.css"],
            forbidden_patterns=[".env", "*.key", "*.pem", ".git/**"],
        )

    @classmethod
    def folder_default(cls, folder: str) -> "SandboxPolicy":
        return cls(
            sandbox_type=SandboxType.FOLDER,
            read_patterns=["**/*"],
            write_patterns=[f"{folder}/**"],
            forbidden_patterns=[".env", "*.key", "*.pem", ".git/**"],
        )

    @classmethod
    def file_default(cls, filepath: str) -> "SandboxPolicy":
        return cls(
            sandbox_type=SandboxType.FILE,
            read_patterns=["**/*"],
            write_patterns=[filepath],
            forbidden_patterns=[".env", "*.key", "*.pem", ".git/**"],
            max_files=1,
        )

    @classmethod
    def patch_default(cls, files: List[str]) -> "SandboxPolicy":
        return cls(
            sandbox_type=SandboxType.PATCH,
            read_patterns=["**/*"],
            write_patterns=files,
            forbidden_patterns=[".env", "*.key", "*.pem", ".git/**"],
            max_files=len(files),
            max_lines_changed=500,
            require_approval_above=200,
        )

    def to_dict(self) -> dict:
        return {
            "sandbox_type": self.sandbox_type.value,
            "read_patterns": self.read_patterns,
            "write_patterns": self.write_patterns,
            "forbidden_patterns": self.forbidden_patterns,
            "max_files": self.max_files,
            "max_lines_changed": self.max_lines_changed,
            "require_approval_above": self.require_approval_above,
        }
