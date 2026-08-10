import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"


class SiteContractTests(unittest.TestCase):
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

    def test_pages_workflow_deploys_only_the_site_directory(self):
        workflow_path = REPO_ROOT / ".github" / "workflows" / "pages.yml"
        self.assertTrue(workflow_path.is_file(), ".github/workflows/pages.yml must exist")
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("path: site", workflow)
        self.assertNotIn("path: '.'", workflow)

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


if __name__ == "__main__":
    unittest.main()
