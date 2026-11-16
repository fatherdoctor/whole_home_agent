"""Checks for the owner-facing optional guard-rails template."""

import re
import unittest
from pathlib import Path


TEXT = (Path(__file__).resolve().parents[1] / "agent-guard-rails.md").read_text()


class GuardRailsText(unittest.TestCase):
    def test_plain_language(self):
        for phrase in ("technical access control", "runtime", "adapter", "higher-priority",
                       "enforced restriction", "household's usual change record"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, TEXT.lower())

    def test_points_at_house_rules_and_addon_setting(self):
        self.assertIn("house-rules.md", TEXT)
        self.assertRegex(TEXT, r"(?is)app.{0,40}permission setting")
        self.assertNotRegex(TEXT, r"(?is)both.{0,80}(?:apps|add-ons).{0,100}ask.{0,35}before")

    def test_messages_require_owner_ok_and_record_changes(self):
        self.assertRegex(TEXT, r"(?im)^- .*messages.*people.*without my (?:ok|permission)")
        self.assertRegex(TEXT, r"(?i)write down.*(?:change|choice)")

    def test_instruction_caveat_is_said_once(self):
        self.assertEqual(len(re.findall(r"(?i)instructions? (?:are|is) not a lock", TEXT)), 1)


if __name__ == "__main__":
    unittest.main()
