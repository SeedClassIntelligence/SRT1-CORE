import json
import tempfile
import unittest
from pathlib import Path

from srt1_platform.seed_queue import SCIASeedQueue, Seed


class SeedQueueCompatibilityTests(unittest.TestCase):
    def test_new_seed_includes_continuity_compatibility_fields(self):
        seed = Seed("seed_0001_test", "Add compatibility fields")
        data = seed.to_dict()

        self.assertIsNone(data["srt_anchor_id"])
        self.assertIsNone(data["manifest_hash"])
        self.assertEqual(data["lifecycle_version"], 1)
        self.assertIsNone(data["completion_state"])
        self.assertIsNone(data["verification_result"])
        self.assertIsNone(data["human_acceptance"])
        self.assertEqual(
            data["trust_state"],
            {
                "signature": "unsigned",
                "verification": "unverified",
                "lineage": "missing",
            },
        )

    def test_legacy_seed_record_loads_with_safe_defaults(self):
        legacy_seed = {
            "seed_id": "seed_0001_legacy",
            "intent": "Legacy queue record",
            "source": "api",
            "priority": 5,
            "tags": [],
            "stage": "planted",
            "growth": 0,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "history": [],
        }

        seed = Seed.from_dict(legacy_seed)

        self.assertIsNone(seed.srt_anchor_id)
        self.assertIsNone(seed.manifest_hash)
        self.assertEqual(seed.lifecycle_version, 1)
        self.assertEqual(seed.trust_state["signature"], "unsigned")
        self.assertEqual(seed.trust_state["verification"], "unverified")
        self.assertEqual(seed.trust_state["lineage"], "missing")
        self.assertIsNone(seed.completion_state)
        self.assertIsNone(seed.verification_result)
        self.assertIsNone(seed.human_acceptance)

    def test_legacy_seed_queue_file_loads_with_safe_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue_dir = Path(tmp)
            queue_file = queue_dir / "seed_queue.json"
            queue_file.write_text(
                json.dumps(
                    {
                        "_counter": 1,
                        "seeds": {
                            "seed_0001_legacy": {
                                "seed_id": "seed_0001_legacy",
                                "intent": "Legacy queue record",
                                "stage": "growing",
                                "growth": 50,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            queue = SCIASeedQueue(queue_dir=str(queue_dir))
            loaded = queue.get_seed("seed_0001_legacy")

        self.assertIsNotNone(loaded)
        self.assertIsNone(loaded["srt_anchor_id"])
        self.assertIsNone(loaded["manifest_hash"])
        self.assertEqual(loaded["lifecycle_version"], 1)
        self.assertEqual(loaded["trust_state"]["signature"], "unsigned")

    def test_completion_metadata_paths_preserve_legacy_bloom_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = SCIASeedQueue(queue_dir=tmp)
            seed = queue.plant("Complete with review metadata")

            proposed = queue.propose_completion(
                seed.seed_id,
                summary="Ready for review",
                files_modified=["srt1_platform/seed_queue.py"],
            )
            self.assertEqual(proposed.completion_state, "awaiting_review")
            self.assertEqual(proposed.stage.value, "planted")

            verified = queue.record_verification_result(
                seed.seed_id,
                verified=True,
                details={"source": "unit_test"},
            )
            self.assertEqual(verified.completion_state, "verified_completion")
            self.assertTrue(verified.verification_result["verified"])

            accepted = queue.accept_completion(
                seed.seed_id,
                summary="Accepted",
                actor="human",
            )
            self.assertEqual(accepted.stage.value, "bloomed")
            self.assertEqual(accepted.completion_state, "human_accepted")
            self.assertEqual(accepted.human_acceptance["actor"], "human")

            loaded = SCIASeedQueue(queue_dir=tmp).get_seed(seed.seed_id)

        self.assertEqual(loaded["stage"], "bloomed")
        self.assertEqual(loaded["completion_state"], "human_accepted")
        self.assertTrue(loaded["verification_result"]["verified"])

    def test_returned_and_partial_completion_are_representable(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = SCIASeedQueue(queue_dir=tmp)
            seed = queue.plant("Return for revision")

            partial = queue.mark_partial(seed.seed_id, note="Some files changed")
            self.assertEqual(partial.completion_state, "partial_completion")

            returned = queue.return_for_revision(seed.seed_id, reason="Needs more work")
            self.assertEqual(returned.completion_state, "returned_for_revision")
            self.assertEqual(returned.stage.value, "planted")


if __name__ == "__main__":
    unittest.main()
