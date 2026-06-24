import os
import tempfile
import unittest
from pathlib import Path

from srt1_platform.filecell import (
    FileCellBoundaryViolation,
    FileCellGuard,
    FileCellManifest,
)
from srt1_platform.manifest_deriver import LeastPrivilegeManifestDeriver
from srt1_platform.verification import PostExecutionVerifier, VerificationResult


class WorkcellBoundaryTests(unittest.TestCase):
    def test_filecell_read_and_write_scopes_are_separate(self):
        with tempfile.TemporaryDirectory() as repo:
            repo_path = Path(repo)
            read_path = repo_path / "read.txt"
            write_path = repo_path / "write.txt"
            read_path.write_text("read", encoding="utf-8")
            write_path.write_text("write", encoding="utf-8")

            manifest = FileCellManifest.generate(
                task_intent="separate read and write scopes",
                allowed_reads=[str(read_path)],
                allowed_writes=[str(write_path)],
            )
            guard = FileCellGuard()

            self.assertTrue(guard.validate_read(str(read_path), manifest))
            self.assertTrue(guard.validate_write(str(write_path), manifest))

            with self.assertRaises(FileCellBoundaryViolation):
                guard.validate_write(str(read_path), manifest)

            with self.assertRaises(FileCellBoundaryViolation):
                guard.validate_read(str(write_path), manifest)

    def test_filecell_forbidden_paths_override_allowed_scopes(self):
        with tempfile.TemporaryDirectory() as repo:
            repo_path = Path(repo)
            blocked_path = repo_path / ".env"
            blocked_path.write_text("SECRET=1", encoding="utf-8")

            manifest = FileCellManifest.generate(
                task_intent="forbidden path precedence",
                allowed_reads=[str(blocked_path)],
                allowed_writes=[str(blocked_path)],
                forbidden_paths=[str(blocked_path)],
            )
            guard = FileCellGuard()

            with self.assertRaises(FileCellBoundaryViolation):
                guard.validate_read(str(blocked_path), manifest)

            with self.assertRaises(FileCellBoundaryViolation):
                guard.validate_write(str(blocked_path), manifest)

    def test_manifest_deriver_uses_workcell_output_dir_and_filters_forbidden(self):
        with tempfile.TemporaryDirectory() as repo:
            repo_path = Path(repo)
            app_path = repo_path / "app.py"
            env_path = repo_path / ".env"
            app_path.write_text("def main():\n    return 1\n", encoding="utf-8")
            env_path.write_text("SECRET=1", encoding="utf-8")

            deriver = LeastPrivilegeManifestDeriver(
                workspace_root=repo,
                symbol_table={
                    "app.py": [
                        {
                            "name": "main",
                            "dependencies": [],
                            "reflection": {"architectural_role": "GENERAL"},
                        }
                    ]
                },
            )

            manifest = deriver.derive(
                seed_id="seed_0001",
                task="update app",
                files_likely=["app.py"],
                explicit_reads=[".env"],
                explicit_writes=[".env"],
            )

            expected_output_dir = os.path.realpath(
                repo_path / ".srt1" / "workcells" / "seed_0001"
            )
            env_realpath = os.path.realpath(env_path)

            self.assertIn(os.path.realpath(app_path), manifest.allowed_reads)
            self.assertIn(expected_output_dir, manifest.allowed_writes)
            self.assertTrue(Path(expected_output_dir).is_dir())
            self.assertNotIn(env_realpath, manifest.allowed_reads)
            self.assertNotIn(env_realpath, manifest.allowed_writes)

    def test_verifier_detects_scope_violation_and_collateral_damage(self):
        with tempfile.TemporaryDirectory() as repo:
            repo_path = Path(repo)
            allowed_path = repo_path / "allowed.py"
            protected_path = repo_path / "protected.py"
            allowed_path.write_text("VALUE = 1\n", encoding="utf-8")
            protected_path.write_text("PROTECTED = 1\n", encoding="utf-8")

            verifier = PostExecutionVerifier(workspace_root=repo)
            verifier.capture_snapshot(
                proposal_id="proposal_1",
                files_to_watch=["allowed.py"],
                files_must_not_change=["protected.py"],
            )

            protected_path.write_text("PROTECTED = 2\n", encoding="utf-8")
            result = verifier.verify(
                proposal_id="proposal_1",
                files_write=["allowed.py"],
                files_must_not_change=["protected.py"],
            )

            self.assertEqual(result.verdict, VerificationResult.FAILED)
            self.assertEqual(result.stats["scope_violations"], 1)
            self.assertEqual(result.stats["collateral_damage_count"], 1)
            self.assertEqual(
                Path(result.scope_violations[0]["file"]).name,
                "protected.py",
            )


if __name__ == "__main__":
    unittest.main()
