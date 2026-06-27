"""
SRT-1 Platform - Local Governance and Integration Surface

Live middleware, seed queue, mobile access, execution bridge, tracing, and
optional understanding intelligence. Private/Enterprise systems integrate
through bounded hooks and must fail closed when unavailable.

    from srt1_platform import SCIALiveEngine, SCIASeedQueue, SCIADispatchBridge
"""

import sys
import os

# License check
_license_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(_license_dir))

try:
    from validate_license import validate_license
    _valid, _message = validate_license("enterprise")
    if not _valid:
        raise ImportError(
            f"\n\n  [SRT-1 Platform] License required.\n  {_message}\n"
        )
except ModuleNotFoundError:
    pass  # validate_license not present during development / source installs

from srt1_platform.middleware import SCIALiveEngine
from srt1_platform.seed_queue import SCIASeedQueue
from srt1_platform.execution_bridge import SCIADispatchBridge
from srt1_platform.tracing_system import SRT1TracingSystem
from srt1_platform.intelligence_adapter import IntelligenceAdapter
from srt1_platform.llm_providers import TokenBudget, AnalysisCache, LLMResponse

try:
    from srt1_platform.remote_auth import SCIARemoteAuth
except ImportError:
    SCIARemoteAuth = None

# Backward-compatible aliases
SRT1LiveEngine = SCIALiveEngine
SRT1SeedQueue = SCIASeedQueue
SRT1ExecutionBridge = SCIADispatchBridge
SRT1RemoteAuth = SCIARemoteAuth

__version__ = "2.2.0"
__all__ = [
    "SCIALiveEngine", "SCIASeedQueue", "SCIADispatchBridge",
    "SRT1TracingSystem", "SCIARemoteAuth",
    "IntelligenceAdapter", "TokenBudget", "AnalysisCache", "LLMResponse",
    # Backward-compatible aliases
    "SRT1LiveEngine", "SRT1SeedQueue", "SRT1ExecutionBridge", "SRT1RemoteAuth",
]
