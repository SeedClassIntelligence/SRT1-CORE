import json
import tempfile
import unittest
from pathlib import Path

from srt1_platform.auto_injector import SCIADocumentGenerator
from srt1_platform.execution_bridge import SCIADispatchBridge


class RuntimeContextOwnershipTests(unittest.TestCase):
    def test_context_dispatch_never_mutates_standing_instructions(self):
        with tempfile.TemporaryDirectory() as repo:
            standing = {
                "AGENTS.md": "agent policy\n",
                "CLAUDE.md": "claude policy\n",
                ".cursorrules": "cursor policy\n",
            }
            for name, content in standing.items():
                Path(repo, name).write_text(content, encoding="utf-8")
            bridge = SCIADispatchBridge(repo_path=repo)

            result = bridge._dispatch_context_injection("seed_context", "Update app.py", "blueprint")
            bridge._clean_context_injection("seed_context")

            self.assertTrue(result["success"])
            self.assertFalse(result["standing_instructions_mutated"])
            for name, content in standing.items():
                self.assertEqual(Path(repo, name).read_text(encoding="utf-8"), content)
            metadata = json.loads(
                Path(repo, ".srt1", "context", "active_seed.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["status"], "completed")

    def test_auto_injector_writes_only_runtime_context(self):
        with tempfile.TemporaryDirectory() as repo:
            Path(repo, "AGENTS.md").write_text("standing policy\n", encoding="utf-8")
            generator = SCIADocumentGenerator(repo_path=repo)
            generator._build_universal_context = lambda: "runtime intelligence\n"

            generator._generate_all_context_files()

            self.assertEqual(Path(repo, "AGENTS.md").read_text(encoding="utf-8"), "standing policy\n")
            self.assertEqual(
                Path(repo, ".srt1", "context", "repository_context.md").read_text(encoding="utf-8"),
                "runtime intelligence\n",
            )
            self.assertFalse(Path(repo, "CLAUDE.md").exists())
            self.assertFalse(Path(repo, ".cursorrules").exists())


if __name__ == "__main__":
    unittest.main()
