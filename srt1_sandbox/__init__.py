"""
SRT-1 Sandbox & Workcell — Logical Isolation Layer

Provides scoped execution environments for AI coding assistants.
Each workcell defines what an assistant can read, write, and depend on.

    from srt1_sandbox import Workcell, WorkcellRegistry

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

from srt1_sandbox.workcell import Workcell, WorkcellRegistry, WorkcellScope
from srt1_sandbox.sandbox import SandboxPolicy, SandboxType

__all__ = [
    "Workcell", "WorkcellRegistry", "WorkcellScope",
    "SandboxPolicy", "SandboxType",
]

__version__ = "0.1.0"
