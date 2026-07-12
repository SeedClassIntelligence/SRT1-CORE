from pathlib import Path
import unittest


class PublicWebsiteMessagingTests(unittest.TestCase):
    def test_srt1_core_homepage_centers_idea_to_completion_lifecycle(self):
        root = Path(__file__).resolve().parents[1]
        homepage = (root / "srt1_platform" / "pwa" / "srt1-core.html").read_text(encoding="utf-8")
        hero = (root / "srt1_platform" / "pwa" / "templates" / "home-hero.html").read_text(encoding="utf-8")
        pricing = (root / "srt1_platform" / "pwa" / "templates" / "home-pricing.html").read_text(encoding="utf-8")
        dashboard = (root / "srt1_platform" / "pwa" / "dashboard.html").read_text(encoding="utf-8")
        experience = (root / "srt1_platform" / "pwa" / "experience.html").read_text(encoding="utf-8")
        auth = (root / "srt1_platform" / "pwa" / "auth.html").read_text(encoding="utf-8")

        for content in (homepage, hero):
            self.assertIn("Bring the idea once.", content)
            self.assertIn("SRT-1 carries it to completion.", content)
            self.assertIn("living work environments", content)
            self.assertIn("approve completion without re-explaining the mission", content)
            self.assertNotIn("Your AI finally understands", content)

        self.assertIn("A seed grows into", homepage)
        self.assertIn("Plant Seed", homepage)
        self.assertIn("Create WorkCell", homepage)
        self.assertIn("Talk With The Work", homepage)
        self.assertIn("Verify And Complete", homepage)
        self.assertIn("Projects: choose what SRT-1 should understand and manage", homepage)
        self.assertIn("Active Work dashboard", pricing)
        self.assertIn("Welcome to SRT-1 Active Work", dashboard)
        self.assertIn("Plant ideas, guide WorkCells, verify progress, and approve completion", dashboard)
        self.assertIn("href=\"experience.html\"", homepage)
        self.assertIn("next=experience.html", homepage)
        self.assertIn("target = 'experience.html'", auth)
        self.assertIn("https://seedreflections.netlify.app/", homepage)

        self.assertIn("What would you like to work on?", experience)
        self.assertIn("Add a project", experience)
        self.assertIn("Continue previous work", experience)
        self.assertIn("Capture an idea for later", experience)
        self.assertIn("Open Advanced", experience)
        self.assertIn("dashboard.html", experience)
        self.assertIn("/api/v1/repositories/register-path", experience)
        self.assertIn("/api/v1/repositories/browse-folder", experience)
        self.assertIn("/api/v1/repositories/register-current", experience)
        self.assertIn("/api/v1/workcells", experience)
        self.assertIn("/messages?limit=20", experience)
        self.assertIn("/chat", experience)
        self.assertIn("project-pending", experience)
        self.assertNotIn("RecallPacket", experience)


if __name__ == "__main__":
    unittest.main()
