import unittest

from srt1_platform.doctrine_scanner import DoctrineScanner
from srt1_platform.taxonomy_validator import TaxonomyValidator


class RecordingLedger:
    def __init__(self):
        self.events = []

    def record(self, **kwargs):
        self.events.append(kwargs)


class DetectiveScannerTests(unittest.TestCase):
    def test_doctrine_scanner_reports_forbidden_terms_without_mutation(self):
        ledger = RecordingLedger()
        scanner = DoctrineScanner(ledger=ledger)
        artifact = {"note": "This should not become autonomous governance."}

        report = scanner.scan_artifact(artifact, "test-artifact")

        self.assertTrue(report["violations_found"])
        self.assertEqual(report["source"], "test-artifact")
        self.assertEqual(artifact["note"], "This should not become autonomous governance.")
        self.assertEqual(len(ledger.events), 1)

    def test_taxonomy_validator_reports_unjustified_protected_label(self):
        ledger = RecordingLedger()
        validator = TaxonomyValidator(ledger=ledger)
        manifest = {
            "symbol_table": {
                "app.py": [
                    {
                        "name": "render_view",
                        "dependencies": ["template"],
                        "reflection": {"architectural_role": "AUTH_SECURITY"},
                    }
                ]
            }
        }

        report = validator.validate_manifest(manifest)

        self.assertTrue(report["violations_found"])
        self.assertEqual(report["violations"][0]["symbol"], "render_view")
        self.assertEqual(len(ledger.events), 1)

    def test_taxonomy_validator_accepts_justified_protected_label(self):
        validator = TaxonomyValidator()
        manifest = {
            "symbol_table": {
                "security.py": [
                    {
                        "name": "hash_password",
                        "dependencies": ["sha256"],
                        "reflection": {"architectural_role": "CRYPTOGRAPHIC"},
                    }
                ]
            }
        }

        report = validator.validate_manifest(manifest)

        self.assertFalse(report["violations_found"])
        self.assertEqual(report["violations"], [])


if __name__ == "__main__":
    unittest.main()
