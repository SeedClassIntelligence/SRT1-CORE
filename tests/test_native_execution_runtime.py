import tempfile
import unittest
from pathlib import Path

from srt1_platform.native_execution_runtime import (
    NativeExecutionBoundaryError,
    NativeExecutionPackage,
    NativeExecutionResult,
    SRT1NativeExecutionRuntime,
)


class NativeExecutionRuntimeTests(unittest.TestCase):
    def _package(self, repo: str) -> NativeExecutionPackage:
        repo_path = Path(repo)
        package_dir = repo_path / ".srt1" / "workcells" / "seed_native"
        package_dir.mkdir(parents=True)
        (package_dir / "workcell.md").write_text("Native WorkCell package", encoding="utf-8")
        (repo_path / "src").mkdir()
        (repo_path / "src" / "auth.py").write_text("ok = True\n", encoding="utf-8")
        return NativeExecutionPackage(
            queue_seed_id="seed_native",
            objective="Fix auth safely",
            repo_path=repo,
            workcell_package_path=str(package_dir),
            allowed_paths=["src/auth.py"],
            restricted_paths=["src/secrets.py"],
            verification_commands=["python -m unittest"],
            acceptance_criteria=["Auth change is verified"],
        )

    def test_native_execution_requires_workcell_package_and_scope(self):
        with tempfile.TemporaryDirectory() as repo:
            runtime = SRT1NativeExecutionRuntime(repo)
            package = self._package(repo)
            package.allowed_paths = []

            with self.assertRaises(NativeExecutionBoundaryError):
                runtime.create_execution(package)

    def test_native_execution_rejects_non_workcell_package_path(self):
        with tempfile.TemporaryDirectory() as repo:
            runtime = SRT1NativeExecutionRuntime(repo)
            package = self._package(repo)
            outside = Path(repo) / "random_package"
            outside.mkdir()
            package.workcell_package_path = str(outside)

            with self.assertRaises(NativeExecutionBoundaryError):
                runtime.create_execution(package)

    def test_native_execution_lifecycle_records_state_and_result(self):
        with tempfile.TemporaryDirectory() as repo:
            runtime = SRT1NativeExecutionRuntime(repo)
            package = self._package(repo)

            execution_id = runtime.create_execution(package)
            self.assertEqual(runtime.status(execution_id)["status"], "queued")

            started = runtime.start(execution_id)
            self.assertEqual(started["status"], "running")

            state = runtime.record_result(NativeExecutionResult(
                execution_id=execution_id,
                queue_seed_id="seed_native",
                status="completed",
                summary="Auth change completed inside WorkCell scope.",
                files_changed=["src/auth.py"],
                tests_run=[{"command": "python -m unittest", "status": "passed"}],
                verification_evidence=[{"type": "test", "status": "passed"}],
                proposed_changes=[{"file_path": "src/auth.py", "action": "modify"}],
            ))
            self.assertEqual(state["status"], "completed")

            result = runtime.collect_result(execution_id)
            self.assertEqual(result.status, "completed")
            self.assertEqual(result.files_changed, ["src/auth.py"])

    def test_native_execution_rejects_out_of_scope_changes(self):
        with tempfile.TemporaryDirectory() as repo:
            runtime = SRT1NativeExecutionRuntime(repo)
            package = self._package(repo)
            execution_id = runtime.create_execution(package)
            runtime.start(execution_id)

            with self.assertRaises(NativeExecutionBoundaryError):
                runtime.record_result(NativeExecutionResult(
                    execution_id=execution_id,
                    queue_seed_id="seed_native",
                    status="completed",
                    files_changed=["src/billing.py"],
                    verification_evidence=[{"type": "manual", "status": "passed"}],
                ))

    def test_native_execution_rejects_completion_without_evidence(self):
        with tempfile.TemporaryDirectory() as repo:
            runtime = SRT1NativeExecutionRuntime(repo)
            package = self._package(repo)
            execution_id = runtime.create_execution(package)
            runtime.start(execution_id)

            with self.assertRaises(NativeExecutionBoundaryError):
                runtime.record_result(NativeExecutionResult(
                    execution_id=execution_id,
                    queue_seed_id="seed_native",
                    status="completed",
                    files_changed=["src/auth.py"],
                ))

    def test_native_execution_rejects_secret_fields(self):
        with tempfile.TemporaryDirectory() as repo:
            runtime = SRT1NativeExecutionRuntime(repo)
            package = self._package(repo)
            package.metadata = {"api_key": "must-not-enter-runtime-package"}

            with self.assertRaises(NativeExecutionBoundaryError):
                runtime.create_execution(package)


if __name__ == "__main__":
    unittest.main()
