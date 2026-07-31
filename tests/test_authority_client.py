import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from srt1_code_indexer.authority_client import AuthorityClient
from srt1_code_indexer import engine as engine_module
from srt1_platform.change_proposal import ChangeProposalStore
from srt1_platform.workcell import WorkCellRegistry


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class AuthorityClientTests(unittest.TestCase):
    def test_required_authority_fails_without_fake_signature(self):
        client = AuthorityClient(endpoint="", api_key="")

        record = client.sign({"artifact": "change"}, phase="source_mutation", require_authority=True)

        self.assertEqual(record.status, "failed")
        self.assertFalse(record.authority_issued)
        self.assertEqual(record.signature_id, "")
        self.assertEqual(client.get_chain(), [])

    def test_optional_integrity_record_is_explicitly_unsigned(self):
        client = AuthorityClient(endpoint="", api_key="")

        record = client.sign({"artifact": "manifest"}, phase="manifest")

        self.assertEqual(record.status, "unsigned")
        self.assertFalse(record.authority_issued)
        self.assertTrue(record.signature_id.startswith("LOCAL-"))

    def test_remote_authority_response_is_marked_signed(self):
        client = AuthorityClient(endpoint="https://signature.example", api_key="session-key")
        response = _Response({"signature_id": "sig_authority_1", "authority_id": "seed-signature"})

        with patch("urllib.request.urlopen", return_value=response):
            record = client.sign({"artifact": "proposal"}, phase="change_proposal_apply", require_authority=True)

        self.assertEqual(record.status, "signed")
        self.assertTrue(record.authority_issued)
        self.assertEqual(record.signature_id, "sig_authority_1")
        self.assertEqual(record.operation_type, "change_proposal_apply")

    def test_remote_failure_remains_failed_when_authority_is_required(self):
        client = AuthorityClient(endpoint="https://signature.example", api_key="session-key")

        with patch("urllib.request.urlopen", side_effect=OSError("offline")):
            record = client.sign({"artifact": "proposal"}, require_authority=True)

        self.assertEqual(record.status, "failed")
        self.assertEqual(record.signature_id, "")
        self.assertFalse(record.authority_issued)

    def test_unsigned_change_proposal_cannot_mutate_source(self):
        with tempfile.TemporaryDirectory() as repo:
            target = Path(repo) / "app.py"
            target.write_text("value = 1\n", encoding="utf-8")
            engine = engine_module.SRT1Engine.__new__(engine_module.SRT1Engine)
            engine.repo_path = repo
            engine.workcell_registry = WorkCellRegistry(repo_path=repo)
            engine.workcell_registry.activate_execution(
                queue_seed_id="seed_unsigned",
                objective="Update app.py",
                manifest={"file_manifest": [{"file_path": "app.py"}]},
            )
            store = ChangeProposalStore(repo)
            proposal = store.create_from_provider_result(
                queue_seed_id="seed_unsigned",
                objective="Change app",
                provider_result={
                    "proposed_changes": [{
                        "file_path": "app.py",
                        "action": "MODIFY",
                        "new_content": "value = 2\n",
                    }],
                },
                allowed_paths=["app.py"],
            )
            proposal_id = proposal["proposal"]["proposal_id"]
            store.review_proposal(proposal_id, action="approve", actor="test")
            engine.change_proposal_store = store
            engine._sign_artifact = Mock(return_value={
                "status": "failed",
                "authority_issued": False,
                "signature_id": "",
            })

            result = engine._apply_change_proposal(proposal_id, actor="test")

            self.assertEqual(result["status"], "blocked")
            self.assertEqual(target.read_text(encoding="utf-8"), "value = 1\n")


if __name__ == "__main__":
    unittest.main()
