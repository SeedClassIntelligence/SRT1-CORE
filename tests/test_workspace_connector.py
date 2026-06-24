import tempfile
import unittest
from pathlib import Path

from srt1_pro.workspace_connector import ModuleScanner


class WorkspaceConnectorScannerTests(unittest.TestCase):
    def test_module_scanner_extracts_javascript_and_typescript_exports(self):
        with tempfile.TemporaryDirectory() as module_dir:
            root = Path(module_dir)
            (root / "api.js").write_text(
                "export function fetchUser(id) { return id; }\n"
                "export class ApiClient {}\n",
                encoding="utf-8",
            )
            (root / "types.ts").write_text(
                "export interface UserRecord { id: string }\n"
                "export const buildUser = (id: string) => ({ id });\n",
                encoding="utf-8",
            )

            summary = ModuleScanner(str(root), "demo").scan()

            self.assertEqual(summary["total_files"], 2)
            self.assertEqual(summary["web_files"], 2)
            self.assertIn("ApiClient", summary["class_names"])
            self.assertIn("fetchUser", summary["public_exports"])
            self.assertIn("buildUser", summary["public_exports"])
            self.assertIn("UserRecord", summary["public_exports"])


if __name__ == "__main__":
    unittest.main()
