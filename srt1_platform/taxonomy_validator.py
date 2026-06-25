# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)

"""
Semantic Taxonomy Validator
===========================
Detective system. Scans the codebase manifest/symbol_table for Semantic Label Inflation.

Doctrine:
    DETECT ONLY. Report ONLY. Log ONLY.
    NO mutation of the symbol table.
    Protects against fake protected domains and escalation abuse.
"""

from typing import Dict, Any, List

class TaxonomyValidator:
    def __init__(self, ledger=None):
        self._ledger = ledger
        
        # Valid constitutional tags
        self._protected_tags = {
            "AUTH_SECURITY", 
            "CRYPTOGRAPHIC", 
            "TRACING_AUDIT", 
            "CONTINUITY_MEMORY", 
            "GOVERNANCE_TRUTH", 
            "OPERATIONAL_MEMORY", 
            "OBSERVABILITY_LAYER", 
            "EXECUTION_RUNTIME"
        }
        
        # Patterns or known dependencies that justify a tag
        # If a function has a tag but none of the justifications, it is flagged.
        self._justifications = {
            "AUTH_SECURITY": ["login", "auth", "token", "secret", "password", "boundary", "permission", "jwt"],
            "CRYPTOGRAPHIC": ["hash", "sha256", "sign", "encrypt", "decrypt", "cipher", "crypto"],
            "TRACING_AUDIT": ["ledger", "log", "audit", "trace", "record", "history"],
            "GOVERNANCE_TRUTH": ["sponsor", "lease", "approve", "rule", "policy"]
        }

    def validate_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan a generated manifest for semantic label inflation.
        Does NOT alter the manifest. Returns a report of violations.
        """
        violations = []
        symbol_table = manifest.get("symbol_table", {})
        
        for filepath, symbols in symbol_table.items():
            for symbol in symbols:
                reflection = symbol.get("reflection", {})
                role = reflection.get("architectural_role")
                
                if role in self._protected_tags:
                    name = symbol.get("name", "").lower()
                    deps = [d.lower() for d in symbol.get("dependencies", [])]
                    
                    # Check justification
                    if role in self._justifications:
                        justified = False
                        keywords = self._justifications[role]
                        
                        # Check name
                        if any(k in name for k in keywords):
                            justified = True
                        
                        # Check dependencies
                        if any(k in dep for dep in deps for k in keywords):
                            justified = True
                            
                        if not justified:
                            violations.append({
                                "file": filepath,
                                "symbol": symbol.get("name"),
                                "role": role,
                                "reason": f"Semantic Label Inflation: {role} applied without matching dependencies or naming conventions."
                            })
                            
        report = {
            "violations_found": len(violations) > 0,
            "violations": violations
        }
        
        if violations and self._ledger:
            self._ledger.record(
                component="taxonomy_validator",
                operation="semantic_label_inflation_detected",
                severity="WARN",
                detail={"violations": violations}
            )
            
        return report
