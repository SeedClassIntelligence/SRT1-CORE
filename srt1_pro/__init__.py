"""
SRT-1 Pro — Intelligence Layer

Context bundling, governed execution, remediation.
Requires a valid SRT-1 Pro or Enterprise license.

    from srt1_pro import SCIAContextBundler, SCIAExecutionEngine, SCIARemediationEngine
"""

import sys
import os

# License check
_license_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(_license_dir))

try:
    from validate_license import validate_license
    _valid, _message = validate_license("pro")
    if not _valid:
        raise ImportError(
            f"\n\n  [SRT-1 Pro] License required.\n  {_message}\n"
        )
except ModuleNotFoundError:
    pass  # validate_license not present during development / source installs

from srt1_pro.context_bundler import SCIAContextBundler
from srt1_pro.execution_engine import SCIAExecutionEngine
from srt1_pro.self_heal import SCIARemediationEngine
from srt1_pro.seed_templates import SeedTemplate, SeedTemplateRegistry, get_registry
from srt1_pro.analytics import AnalyticsEngine
from srt1_pro.completeness import SeedTreeValidator, CompletenessReport

# Backward-compatible aliases
SRT1ContextBundler = SCIAContextBundler
SRT1ExecutionEngine = SCIAExecutionEngine
SRT1SelfHealEngine = SCIARemediationEngine

__version__ = "2.1.0"
__all__ = [
    "SCIAContextBundler", "SCIAExecutionEngine", "SCIARemediationEngine",
    "SRT1ContextBundler", "SRT1ExecutionEngine", "SRT1SelfHealEngine",  # aliases
    "SeedTemplate", "SeedTemplateRegistry", "get_registry",
    "AnalyticsEngine", "SeedTreeValidator", "CompletenessReport"
]

