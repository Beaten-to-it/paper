import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"


class SiteContractTests(unittest.TestCase):
    def test_public_text_files_use_lf_for_stable_catalog_hashes(self):
        text_extensions = {".css", ".html", ".js", ".json", ".md", ".svg"}
        offending = [
            path.relative_to(REPO_ROOT).as_posix()
            for path in SITE_ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in text_extensions
            and b"\r\n" in path.read_bytes()
        ]

        self.assertEqual(offending, [], f"public text files must use LF: {offending}")

    def test_homepage_loads_catalog_and_exposes_filters(self):
        homepage = SITE_ROOT / "index.html"
        app_script = SITE_ROOT / "assets" / "app.js"
        self.assertTrue(homepage.is_file(), "site/index.html must exist")
        self.assertTrue(app_script.is_file(), "site/assets/app.js must exist")
        html = homepage.read_text(encoding="utf-8")
        script = app_script.read_text(encoding="utf-8")

        self.assertIn('id="paper-list"', html)
        self.assertIn('id="type-filter"', html)
        self.assertIn("data/catalog.json", script)
        self.assertIn("artifact.status", script)

    def test_final_catalog_has_five_complete_nine_slot_papers_and_four_design_artifacts(self):
        catalog = json.loads((SITE_ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
        papers = [paper for paper in catalog["papers"] if paper["kind"] == "paper"]
        research_design = [paper for paper in catalog["papers"] if paper["kind"] == "research-design"]

        self.assertEqual(catalog["version"], 2)
        self.assertEqual(len(papers), 5)
        self.assertEqual(len(research_design), 1)
        self.assertTrue(all(len(paper["artifacts"]) == 9 for paper in papers))
        self.assertEqual(len(research_design[0]["artifacts"]), 4)
        artifacts = [artifact for paper in catalog["papers"] for artifact in paper["artifacts"]]
        self.assertEqual(len(artifacts), 49)
        self.assertTrue(all(artifact["status"] == "complete" for artifact in artifacts))

    def test_homepage_distinguishes_rights_and_locked_companions(self):
        script = (SITE_ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn('source_paper: "원문"', script)
        self.assertIn('korean_version: "한국어본"', script)
        self.assertIn("rights-badge", script)
        self.assertIn("protected-viewer.html?id=", script)
        self.assertIn("암호 입력 후 열기", script)
        self.assertIn("공식 원문", script)

    def test_pages_workflow_deploys_only_the_site_directory(self):
        workflow_path = REPO_ROOT / ".github" / "workflows" / "pages.yml"
        self.assertTrue(workflow_path.is_file(), ".github/workflows/pages.yml must exist")
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("path: site", workflow)
        self.assertNotIn("path: '.'", workflow)
        self.assertIn("node --test tests/protected_crypto.test.mjs", workflow)

    def test_markdown_artifacts_have_an_internal_reader(self):
        viewer = SITE_ROOT / "viewer.html"
        viewer_script = SITE_ROOT / "assets" / "viewer.js"
        self.assertTrue(viewer.is_file(), "site/viewer.html must exist")
        self.assertTrue(viewer_script.is_file(), "site/assets/viewer.js must exist")

        app_script = (SITE_ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        viewer_source = viewer_script.read_text(encoding="utf-8")
        self.assertIn("viewer.html?file=", app_script)
        self.assertIn('startsWith("downloads/")', viewer_source)

    def test_infographics_render_a_preview(self):
        app_script = (SITE_ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn('artifact.type === "infographic"', app_script)
        self.assertIn('class="artifact__preview"', app_script)

    def test_public_notebooklm_logs_do_not_expose_private_workspace_urls(self):
        for run_log in SITE_ROOT.glob("downloads/*/notebooklm-run.md"):
            public_text = run_log.read_text(encoding="utf-8")
            self.assertNotIn("notebook.google.com/notebook/", public_text, run_log)

    def test_protected_viewer_uses_a_memory_only_password_boundary(self):
        viewer = SITE_ROOT / "protected-viewer.html"
        viewer_script = SITE_ROOT / "assets" / "protected-viewer.js"
        crypto_script = SITE_ROOT / "assets" / "protected-crypto.js"
        self.assertTrue(viewer.is_file(), "site/protected-viewer.html must exist")
        self.assertTrue(viewer_script.is_file(), "site/assets/protected-viewer.js must exist")
        self.assertTrue(crypto_script.is_file(), "site/assets/protected-crypto.js must exist")

        html = viewer.read_text(encoding="utf-8")
        script = viewer_script.read_text(encoding="utf-8")
        self.assertIn('type="password"', html)
        self.assertIn('autocomplete="off"', html)
        self.assertIn('http-equiv="Content-Security-Policy"', html)
        self.assertIn('type="module"', html)
        self.assertIn('fetch("data/catalog.json", {cache: "no-store"})', script)
        self.assertIn('cache: "no-store"', script)
        self.assertIn("AbortController", script)
        self.assertIn("unlockVersion", script)
        self.assertIn("verifyEncryptedPayload", script)
        self.assertIn('passwordInput.value = ""', script)
        self.assertIn("URL.createObjectURL", script)
        self.assertIn("URL.revokeObjectURL", script)
        self.assertNotIn("localStorage", script)
        self.assertNotIn("sessionStorage", script)
        self.assertNotIn("document.cookie", script)

    def test_protected_viewer_declares_the_client_side_security_limit(self):
        html = (SITE_ROOT / "protected-viewer.html").read_text(encoding="utf-8")
        self.assertIn("오프라인 대입 공격", html)
        self.assertIn("서버 인증", html)


if __name__ == "__main__":
    unittest.main()
