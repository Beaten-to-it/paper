import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "tools" / "validate_catalog.py"


class CatalogValidationTests(unittest.TestCase):
    @staticmethod
    def valid_catalog():
        return {
            "version": 1,
            "updated": "2026-08-11",
            "papers": [
                {
                    "slug": "example-2026",
                    "citation": "Example et al. (2026)",
                    "year": 2026,
                    "title": "Example paper",
                    "summary": "연구 요약",
                    "artifacts": [
                        {
                            "id": "example-analysis",
                            "type": "analysis",
                            "title": "분석 카드",
                            "href": "downloads/example-analysis.md",
                            "storage": "pages",
                            "size_bytes": 13,
                            "sha256": "e35e56bbdee091ca9998b54adaa744a398087d139aaeff6cc72ba07cd077dbf6",
                            "status": "complete",
                            "provenance": "researcher_generated",
                        }
                    ],
                }
            ],
        }

    def run_validator(self, catalog: dict, files: dict[str, bytes] | None = None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public_root = root / "site"
            public_root.mkdir()
            catalog_path = root / "catalog.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            for relative_path, content in (files or {}).items():
                path = public_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(catalog_path), str(public_root)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

    def test_accepts_a_valid_public_catalog(self):
        catalog = self.valid_catalog()

        result = self.run_validator(
            catalog,
            {"downloads/example-analysis.md": "분석 카드".encode("utf-8")},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 papers, 1 artifacts", result.stdout)

    def test_rejects_third_party_source_pdfs(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0].update(
            {
                "type": "source_paper_pdf",
                "title": "제3자 논문 원문",
                "href": "downloads/source-paper.pdf",
                "size_bytes": 4,
            }
        )

        result = self.run_validator(catalog, {"downloads/source-paper.pdf": b"PDF!"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source_paper_pdf is not public", result.stderr)

    def test_rejects_large_files_from_pages_storage(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0]["size_bytes"] = 50 * 1024 * 1024 + 1

        result = self.run_validator(
            catalog,
            {"downloads/example-analysis.md": "분석 카드".encode("utf-8")},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("files over 50 MiB must use release storage", result.stderr)

    def test_rejects_missing_pages_files(self):
        catalog = self.valid_catalog()

        result = self.run_validator(catalog)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing pages file", result.stderr)

    def test_rejects_pages_file_hash_mismatch(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0]["sha256"] = "f" * 64

        result = self.run_validator(
            catalog,
            {"downloads/example-analysis.md": "분석 카드".encode("utf-8")},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256 mismatch", result.stderr)

    def test_rejects_pages_path_traversal(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0]["href"] = "../private.txt"

        result = self.run_validator(catalog, {"../private.txt": b"private"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe pages path", result.stderr)

    def test_rejects_non_github_release_url(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0].update(
            {
                "storage": "release",
                "href": "javascript:alert(1)",
            }
        )

        result = self.run_validator(catalog)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe release url", result.stderr)

    def test_rejects_unknown_storage(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0].update(
            {
                "storage": "external",
                "href": "javascript:alert(document.domain)",
            }
        )

        result = self.run_validator(catalog)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported storage", result.stderr)

    def test_rejects_complete_artifact_with_none_storage(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0].update(
            {
                "storage": "none",
                "href": "javascript:alert(document.domain)",
            }
        )

        result = self.run_validator(catalog)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete artifacts require public storage", result.stderr)

    def test_rejects_release_path_traversal(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0].update(
            {
                "storage": "release",
                "href": "https://github.com/Beaten-to-it/paper/releases/download/../../../attacker/repo/releases/download/v1/setup.exe",
            }
        )

        result = self.run_validator(catalog)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe release url", result.stderr)

    def test_rejects_undeclared_public_file(self):
        catalog = self.valid_catalog()

        result = self.run_validator(
            catalog,
            {
                "downloads/example-analysis.md": "분석 카드".encode("utf-8"),
                "downloads/qa-notes.zip": b"private",
            },
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("undeclared public file", result.stderr)

    def test_rejects_pdf_disguised_as_analysis(self):
        catalog = self.valid_catalog()
        catalog["papers"][0]["artifacts"][0].update(
            {
                "href": "downloads/source-paper.pdf",
                "size_bytes": 4,
                "sha256": "13fe9d84310e77f13a6bcb86c45b9f39517f5a98e1e6a18cea2b1b756bf59198",
            }
        )

        result = self.run_validator(catalog, {"downloads/source-paper.pdf": b"PDF!"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid pages artifact type or extension", result.stderr)


if __name__ == "__main__":
    unittest.main()
