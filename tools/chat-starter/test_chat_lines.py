#!/usr/bin/env python3
"""Regression checks for the chat guide's return and device-discovery advice."""
import re
import unittest
from pathlib import Path


GUIDE = Path(__file__).resolve().parents[2] / "00-start-here/from-a-chat-app.md"
TEXT = re.sub(r"\s+", " ", GUIDE.read_text(encoding="utf-8"))
RETURN = TEXT.split("## Coming back without an agent on the box", 1)[1].split("## Git can wait", 1)[0]


class ChatReturnAdvice(unittest.TestCase):
    def test_first_return_can_start_without_a_progress_note(self):
        self.assertIn("no progress note", RETURN.lower())
        self.assertIn("start one", RETURN.lower())
        self.assertIn('"not recorded"', RETURN)

    def test_secrets_include_maker_app_accounts(self):
        rules = TEXT.split("Rules for every evening:", 1)[1].split("4. **The goal first", 1)[0]
        self.assertIn("maker-app account", rules.lower())

    def test_discovery_cards_are_left_visible(self):
        discovery = TEXT.split('4. **If a "discovered" banner', 1)[1].split("5. **Moving to Wi-Fi**", 1)[0]
        self.assertGreaterEqual(discovery.count("**Ignore**"), 2)
        self.assertGreaterEqual(discovery.lower().count("hides"), 2)

    def test_proven_steps_can_be_bundled_with_a_stop_condition(self):
        rules = TEXT.split("Rules for every evening:", 1)[1].split("2. **Believe their screen", 1)[0].lower()
        for phrase in ("proven", "bundle", "unexpected"):
            self.assertIn(phrase, rules)

    def test_batch_clues_and_read_model_list_once(self):
        for phrase in ("same brand", "clues", "read the list once", "each model"):
            self.assertIn(phrase, RETURN.lower())

    def test_note_distinguishes_names_and_records_each_change(self):
        for phrase in ("home assistant name", "voice name", "goal and time for this or next session", "one line per change", "actual test result", "undo"):
            self.assertIn(phrase, RETURN.lower())


if __name__ == "__main__":
    unittest.main()
