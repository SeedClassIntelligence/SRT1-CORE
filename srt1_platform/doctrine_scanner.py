# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)

"""
Doctrine Scanner
================
Detective system. Scans artifacts, narratives, and codebase for terminology
drift and constitutional violations.

Doctrine:
    DETECT ONLY. Report ONLY. Log ONLY.
    NO file editing.
    NO automated remediation.
    NO self-healing.
"""

import re
from typing import List, Dict, Any, Optional

# Outlawed terminology indicating drift toward autonomous governance or legacy concepts
OUTLAWED_TERMS = {
    "AI supervisor",
    "control plane",
    "admin console",
    "autonomous governance",
    "SION brain",
    "self-healing",
    "one-click undo",
    "operator cockpit",
    "runtime authority",
    "AI decides",
    "automatic remediation",
    "apply this patch",       # Narrative remediation
    "you should merge this",  # Narrative command
}

class DoctrineScanner:
    def __init__(self, ledger=None):
        """
        ledger: Optional event recorder for logging doctrine breaches.
        """
        self._ledger = ledger
        self._patterns = [(term, re.compile(re.escape(term), re.IGNORECASE)) for term in OUTLAWED_TERMS]

    def scan_text(self, text: str, source_identifier: str) -> Dict[str, Any]:
        """
        Scan a single string (e.g., a narrative, file content) for outlawed terms.
        Returns a report of violations.
        """
        violations = []
        for term, pattern in self._patterns:
            matches = pattern.findall(text)
            if matches:
                violations.append({
                    "term": term,
                    "count": len(matches)
                })

        report = {
            "source": source_identifier,
            "violations_found": len(violations) > 0,
            "violations": violations
        }

        if violations and self._ledger:
            self._ledger.record(
                component="doctrine_scanner",
                operation="forbidden_term_detected",
                severity="WARN",
                detail={"source": source_identifier, "violations": violations}
            )

        return report

    def scan_artifact(self, artifact: Dict[str, Any], source_identifier: str) -> Dict[str, Any]:
        """
        Recursively scan a dictionary artifact (e.g., drift analysis report).
        """
        text_content = self._extract_text(artifact)
        return self.scan_text(text_content, source_identifier)

    def _extract_text(self, obj: Any) -> str:
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, dict):
            return " ".join(self._extract_text(v) for v in obj.values())
        elif isinstance(obj, list):
            return " ".join(self._extract_text(v) for v in obj)
        return ""
