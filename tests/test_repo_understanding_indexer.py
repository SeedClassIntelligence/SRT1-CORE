import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from srt1_code_indexer.indexer import SRT1CodeIndexer
from srt1_code_indexer.language_parsers import dispatch_parser


class FakeSRTTool:
    reflection_interval = 3

    def trace_operation(self, *args, **kwargs):
        return None

    def get_reflections(self):
        return []

    def summarize_reflections(self):
        return {}

    def get_trace_chain(self):
        return []

    def get_coherence_history(self):
        return []


class RepoUnderstandingIndexerTests(unittest.TestCase):
    def test_dispatch_parser_extracts_code_symbols(self):
        source = """
public class Greeter {
    public string Hello(string name) { return name; }
}
"""
        symbols = dispatch_parser(source, "Greeter.cs", ".cs")
        names = {symbol["name"] for symbol in symbols}

        self.assertIn("Greeter", names)
        self.assertIn("Hello", names)
        self.assertTrue(all(symbol["category"] == "code" for symbol in symbols))

    def test_dispatch_parser_extracts_structural_anchors(self):
        html_symbols = dispatch_parser(
            '<section id="hero" class="landing primary"><button>Go</button></section>',
            "index.html",
            ".html",
        )
        css_symbols = dispatch_parser(".landing {\n  color: red;\n}\n:root {\n  --brand: #111;\n}", "style.css", ".css")
        md_symbols = dispatch_parser("# Title\n\n## Usage", "README.md", ".md")

        anchors = html_symbols + css_symbols + md_symbols
        anchor_names = {symbol["name"] for symbol in anchors}

        self.assertIn("hero", anchor_names)
        self.assertIn("landing", anchor_names)
        self.assertIn("Title", anchor_names)
        self.assertTrue(all(symbol["category"] == "anchor" for symbol in anchors))

    def test_indexer_tracks_language_coverage_for_code_and_anchor_symbols(self):
        with tempfile.TemporaryDirectory() as repo:
            repo_path = Path(repo)
            py_file = repo_path / "app.py"
            js_file = repo_path / "app.js"
            html_file = repo_path / "index.html"
            py_file.write_text("def run():\n    return True\n", encoding="utf-8")
            js_file.write_text("export function boot() { return run(); }\n", encoding="utf-8")
            html_file.write_text('<main id="app" class="shell"></main>\n', encoding="utf-8")

            indexer = SRT1CodeIndexer.__new__(SRT1CodeIndexer)
            indexer.file_manifest = [
                {"full_path": str(py_file), "file_path": "app.py", "extension": ".py"},
                {"full_path": str(js_file), "file_path": "app.js", "extension": ".js"},
                {"full_path": str(html_file), "file_path": "index.html", "extension": ".html"},
            ]
            indexer.symbol_table = {}
            indexer.code_manifest = {}
            indexer.srt_tool = FakeSRTTool()

            indexer._parse_source_files()

            coverage = indexer.code_manifest["language_coverage"]
            self.assertEqual(coverage[".py"]["parser"], "ast")
            self.assertGreaterEqual(coverage[".js"]["code_symbols"], 1)
            self.assertGreaterEqual(coverage[".html"]["anchor_symbols"], 1)
            self.assertIn("app.js", indexer.symbol_table)
            self.assertIn("index.html", indexer.symbol_table)

    def test_save_manifest_preserves_language_coverage(self):
        with tempfile.TemporaryDirectory() as repo:
            indexer = SRT1CodeIndexer.__new__(SRT1CodeIndexer)
            indexer.repo_path = repo
            indexer.file_manifest = []
            indexer.symbol_table = {}
            indexer.curation_report = {}
            indexer.srt_tool = FakeSRTTool()
            indexer.code_manifest = {
                "language_coverage": {
                    ".py": {
                        "parser": "ast",
                        "fidelity": "full",
                        "files": 1,
                        "code_symbols": 1,
                        "anchor_symbols": 0,
                        "total_symbols": 1,
                    }
                }
            }

            real_import = __import__

            def fail_closed_import(name, *args, **kwargs):
                if name == "scia_security.signing_client":
                    raise ImportError("optional signing unavailable in Core test")
                return real_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=fail_closed_import):
                indexer._save_manifest()

            manifest_path = Path(repo) / "srt1_code_manifest.json"
            saved = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["language_coverage"][".py"]["parser"], "ast")


if __name__ == "__main__":
    unittest.main()
