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

    @staticmethod
    def rights_aware_catalog():
        release = "https://github.com/Beaten-to-it/paper/releases/download/artifacts-2026-08-11-v2/"
        artifacts = [
            {"id":"source","type":"source_paper","title":"원문","href":release + "source.pdf","storage":"release","size_bytes":1,"sha256":"a" * 64,"status":"complete","provenance":"publisher","access":"public"},
            {"id":"korean","type":"korean_version","title":"한국어본","href":release + "korean.pdf","storage":"release","size_bytes":1,"sha256":"b" * 64,"status":"complete","provenance":"researcher_generated","access":"public","translation_kind":"full_unofficial"},
            {"id":"analysis","type":"analysis","title":"분석","href":"downloads/analysis.md","storage":"pages","size_bytes":8,"sha256":"f44e85c4b8ea2addc796f8beab6600e801d767ccd26c800dce6d88fdaa5eb4e6","status":"complete","provenance":"researcher_generated","access":"public"},
            {"id":"prompt","type":"notebooklm_prompt","title":"프롬프트","href":"downloads/prompt.md","storage":"pages","size_bytes":6,"sha256":"cf07194ee232eb531e15f690000d19846dea69cf05504782658afcfacb9228a2","status":"complete","provenance":"researcher_generated","access":"public"},
            {"id":"run","type":"notebooklm_run","title":"실행기록","href":"downloads/run.md","storage":"pages","size_bytes":3,"sha256":"acba25512100f80b56fc3ccd14c65be55d94800cda77585c5f41a887e398f9be","status":"complete","provenance":"researcher_generated","access":"public"},
            {"id":"audio","type":"audio","title":"음성","href":release + "audio.m4a","storage":"release","size_bytes":1,"sha256":"c" * 64,"status":"complete","provenance":"notebooklm_generated","access":"public"},
            {"id":"slides","type":"slides","title":"PPT","href":release + "slides.pptx","storage":"release","size_bytes":1,"sha256":"d" * 64,"status":"complete","provenance":"researcher_generated","access":"public"},
            {"id":"slide-pdf","type":"slide_pdf","title":"PDF","href":release + "slides.pdf","storage":"release","size_bytes":1,"sha256":"e" * 64,"status":"complete","provenance":"researcher_generated","access":"public"},
            {"id":"infographic","type":"infographic","title":"인포그래픽","href":"downloads/graphic.png","storage":"pages","size_bytes":8,"sha256":"4c4b6a3be1314ab86138bef4314dde022e600960d8689a2c8f8631802d20dab6","status":"complete","provenance":"researcher_generated","access":"public"},
        ]
        return {
            "version": 2,
            "updated": "2026-08-11",
            "papers": [{
                "slug": "example-2026",
                "kind": "paper",
                "citation": "Example et al. (2026)",
                "year": 2026,
                "title": "Example paper",
                "summary": "연구 요약",
                "rights": {
                    "license": "CC-BY-4.0",
                    "redistribution": "allowed",
                    "translation_publication": "allowed_with_attribution",
                    "source_url": "https://doi.org/10.0000/example",
                    "checked_at": "2026-08-11",
                },
                "artifacts": artifacts,
            }],
        }

    @staticmethod
    def rights_aware_files():
        return {
            "downloads/analysis.md": b"analysis",
            "downloads/prompt.md": b"prompt",
            "downloads/run.md": b"run",
            "downloads/graphic.png": bytes([137, 80, 78, 71, 13, 10, 26, 10]),
        }

    @classmethod
    def restricted_rights_catalog(cls):
        catalog = cls.rights_aware_catalog()
        paper = catalog["papers"][0]
        paper["slug"] = "battilana-casciaro-2012"
        paper["rights"].update({
            "license": "author-manuscript-policy",
            "redistribution": "restricted",
            "translation_publication": "restricted",
            "source_url": "https://dash.harvard.edu/handle/1/9544459",
        })
        source = next(artifact for artifact in paper["artifacts"] if artifact["type"] == "source_paper")
        source.update({
            "storage": "external",
            "href": "https://doi.org/10.5465/amj.2009.0891",
            "size_bytes": 0,
            "sha256": "",
            "access": "official_link_plus_password_encrypted",
            "protected": {
                "href": "protected/bc2012-source.enc",
                "size_bytes": 13,
                "sha256": "98541417fc0f9ba6873acd18feb6b816e04e260d79d0561d3b9c5ffc45c2bdce",
                "container_version": 1,
                "algorithm": "AES-256-GCM",
                "kdf": "PBKDF2-HMAC-SHA-256",
                "iterations": 600000,
            },
        })
        korean = next(artifact for artifact in paper["artifacts"] if artifact["type"] == "korean_version")
        korean.update({
            "storage": "pages",
            "href": "downloads/korean-study-guide.md",
            "size_bytes": 5,
            "sha256": "83ca68be6227af2feb15f227485ed18aff8ecae99416a4bd6df3be1b5e8059b4",
            "access": "public_plus_password_encrypted",
            "translation_kind": "detailed_study_guide",
            "protected": {
                "href": "protected/bc2012-korean-full.enc",
                "size_bytes": 13,
                "sha256": "141a8393047d4a592c8f241ccc948df49e2cbb15a9edcebc021c6dc5a289083b",
                "container_version": 1,
                "algorithm": "AES-256-GCM",
                "kdf": "PBKDF2-HMAC-SHA-256",
                "iterations": 600000,
            },
        })
        return catalog

    @classmethod
    def restricted_rights_files(cls):
        files = cls.rights_aware_files()
        files["downloads/korean-study-guide.md"] = b"guide"
        files["protected/bc2012-source.enc"] = b"cipher-source"
        files["protected/bc2012-korean-full.enc"] = b"cipher-korean"
        return files

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

    def test_accepts_a_rights_aware_nine_slot_paper(self):
        result = self.run_validator(self.rights_aware_catalog(), self.rights_aware_files())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 papers, 9 artifacts", result.stdout)

    def test_rejects_public_redistribution_when_rights_disallow_it(self):
        catalog = self.rights_aware_catalog()
        catalog["papers"][0]["rights"]["redistribution"] = "restricted"

        result = self.run_validator(catalog, self.rights_aware_files())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rights do not allow public redistribution", result.stderr)

    def test_rejects_wrong_paper_slot_set(self):
        catalog = self.rights_aware_catalog()
        catalog["papers"][0]["artifacts"].pop()

        result = self.run_validator(catalog, self.rights_aware_files())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nine-slot contract", result.stderr)

    def test_accepts_official_link_with_declared_encrypted_companions(self):
        result = self.run_validator(self.restricted_rights_catalog(), self.restricted_rights_files())

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unapproved_external_source_host(self):
        catalog = self.restricted_rights_catalog()
        source = next(a for a in catalog["papers"][0]["artifacts"] if a["type"] == "source_paper")
        source["href"] = "https://example.com/paper"

        result = self.run_validator(catalog, self.restricted_rights_files())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe external url", result.stderr)

    def test_rejects_protected_path_traversal(self):
        catalog = self.restricted_rights_catalog()
        source = next(a for a in catalog["papers"][0]["artifacts"] if a["type"] == "source_paper")
        source["protected"]["href"] = "protected/../private.pdf"

        result = self.run_validator(catalog, self.restricted_rights_files())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe protected path", result.stderr)

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
