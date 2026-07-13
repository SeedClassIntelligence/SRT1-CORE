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

        front_door = experience.split("<!-- FRONT DOOR -->", 1)[1].split("<!-- END FRONT DOOR -->", 1)[0]
        self.assertIn("Good afternoon, Darnell.", front_door)
        self.assertIn("SCIA is active.", front_door)
        self.assertIn("Bring the idea once.", front_door)
        self.assertIn("keeps the assistant on task", front_door)
        self.assertIn("carries the work to completion", front_door)
        self.assertIn("Message SRT-1.", front_door)
        self.assertIn("Connect Project", front_door)
        self.assertIn("Continue Work", front_door)
        self.assertIn("Plant Seed", front_door)
        self.assertIn("Ask SRT-1 to Check", front_door)
        self.assertIn("Control Room", front_door)
        self.assertIn("Continuity", front_door)
        self.assertIn("without re-explaining the mission", front_door)
        self.assertNotIn("Register Path", front_door)
        self.assertNotIn("Active Work", front_door)
        self.assertNotIn("Project Conversation", front_door)
        self.assertNotIn("Reading project files", front_door)
        self.assertNotIn("Preparing project memory", front_door)
        self.assertNotIn("Creating focused workspace", front_door)

        self.assertIn("Tell me about your idea.", experience)
        self.assertIn("Plant Seed", experience)
        self.assertIn("Choose Folder", experience)
        self.assertIn("Import GitHub", experience)
        self.assertIn("Recent Projects", experience)
        self.assertIn("SRT-1 is preparing your project.", experience)
        self.assertIn("Project Controller", experience)
        self.assertIn("Talk to the project", experience)
        self.assertIn("pause work, resume work", experience)
        self.assertIn("Advanced", experience)
        self.assertIn("dashboard.html", experience)
        self.assertIn("/api/v1/repositories/register-path", experience)
        self.assertIn("/api/v1/repositories/browse-folder", experience)
        self.assertIn("/api/v1/repositories/register-current", experience)
        self.assertIn("/api/v1/workcells", experience)
        self.assertIn("/messages?limit=20", experience)
        self.assertIn("/chat", experience)
        self.assertIn("Seed captured.", experience)
        self.assertNotIn("RecallPacket", experience)


if __name__ == "__main__":
    unittest.main()
