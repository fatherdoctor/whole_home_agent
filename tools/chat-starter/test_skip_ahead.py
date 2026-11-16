"""Regression checks for the optional early on-box agent hand-off."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def normalized(path):
    return re.sub(r'\s+', ' ', (ROOT / path).read_text(encoding='utf-8')).lower()


class SkipAhead(unittest.TestCase):
    def test_rule_points_to_a_jump_route_with_two_prerequisites(self):
        text = normalized('00-start-here/from-a-chat-app.md')
        rule = text.split('7. **the owner decides.**', 1)[1].split('8. **the owner builds', 1)[0]
        self.assertIn('#jumping-ahead', rule)
        section = text.split('## jumping ahead', 1)[1].split('## ', 1)[0]
        for phrase in ('one local backup', 'first update', 'off-box copy', 'two-step login', 'chatgpt', 'claude'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)
        self.assertLess(section.index('one local backup'), section.index('first update'))

    def test_skips_have_a_dated_handoff_and_are_offered_later(self):
        for path in ('00-start-here/from-a-chat-app.md', 'interview/phase-0-setup-interview.md'):
            with self.subTest(path=path):
                text = normalized(path)
                section = text.split('## jumping ahead', 1)[1].split('## ', 1)[0]
                self.assertIn("skipped at owner's request, <date>", section)
                self.assertIn('each skipped step', section)
                self.assertIn('offer', section)
        self.assertIn("skipped at owner's request, <date>", normalized('00-start-here/from-a-chat-app.md').split('4. **the hand-off note.**', 1)[1])

    def test_chatgpt_install_is_unwalked_and_points_to_its_own_docs(self):
        for path in ('00-start-here/from-a-chat-app.md', 'interview/phase-0-setup-interview.md'):
            with self.subTest(path=path):
                section = normalized(path).split('## jumping ahead', 1)[1].split('## ', 1)[0]
                for phrase in ('lab notes only', "app's own documentation", 'do not guess'):
                    self.assertIn(phrase, section)
                self.assertNotIn('codex login', section)
                self.assertNotRegex(section, r'https?://')


if __name__ == '__main__':
    unittest.main()
