"""Newcomer screen and installation routes, including the generated starter."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def existing_install(text):
    return text.split('## 4. Home Assistant already running', 1)[1].split('## Onboarding', 1)[0]


class NewcomerRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = [
            existing_install((ROOT / '00-start-here/from-a-chat-app.md').read_text()),
            existing_install((ROOT / '00-start-here/chat-app-starter.md').read_text()),
        ]

    def test_system_information_supplies_version_and_installation_type(self):
        for route in self.routes:
            with self.subTest(document=route[:30]):
                self.assertNotIn('Settings > About', route)
                self.assertIn('Settings > System > Repairs', route)
                self.assertRegex(route, r'(?s)System information.{0,180}version.{0,100}installation type')

    def test_supervised_keeps_its_app_route_and_support_caveat(self):
        for route in self.routes:
            with self.subTest(document=route[:30]):
                self.assertRegex(route, r'(?is)Supervised.{0,180}unsupported.{0,180}apps')
                self.assertRegex(route, r'(?is)Container.{0,90}Core.{0,100}no apps')

    def test_marketplace_and_older_hacs_are_separate_from_apps(self):
        for route in self.routes:
            with self.subTest(document=route[:30]):
                self.assertIn('Settings > Apps', route)
                self.assertIn('Settings > Marketplace', route)
                self.assertRegex(route, r'(?is)2026\.11 or later.{0,100}Settings > Marketplace')
                self.assertRegex(route, r'(?is)older (?:releases|versions).{0,100}HACS')

    def test_first_file_editor_install_uses_the_store(self):
        text = (ROOT / 'install/secrets.md').read_text()
        self.assertIn('Settings > Apps > Install app', text)
        self.assertRegex(text, r'(?is)already installed.{0,100}Settings > Apps')


if __name__ == '__main__':
    unittest.main()
