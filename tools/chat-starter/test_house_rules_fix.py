"""Regression checks for the house-rule hand-off (KIT-ASK-LESS.f)."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def text(path):
    return re.sub(r'\s+', ' ', (ROOT / path).read_text(encoding='utf-8'))


class HouseRuleHandoff(unittest.TestCase):
    def test_any_installed_agent_reaches_rules_and_knows_its_file(self):
        guide = text('00-start-here/from-a-chat-app.md')
        phase = text('interview/phase-0-setup-interview.md')
        rules = text('templates/house-rules.md')
        handoff = guide.split('## The hand-off to the agent on the box', 1)[1].split('## Coming back', 1)[0]
        self.assertIn('skip steps 1 and 2', handoff)
        self.assertIn('/config/AGENTS.md', handoff)
        self.assertIn('/config/CLAUDE.md', handoff)
        self.assertIn('/config/AGENTS.md', phase)
        self.assertIn('/config/CLAUDE.md', phase)
        self.assertIn('/config/AGENTS.md', rules)
        self.assertIn('/config/CLAUDE.md', rules)
        self.assertIn('kit\'s address', handoff.split('3. **Choose and install house rules.**', 1)[1].split('templates/house-rules.md', 1)[0])

    def test_choice_and_extra_limits_survive_the_handoff(self):
        guide = text('00-start-here/from-a-chat-app.md')
        phase = text('interview/phase-0-setup-interview.md')
        self.assertIn('House rules: <Careful start | Direct | not yet>', guide)
        self.assertIn('extra limits: <none | which | not yet>', guide)
        self.assertIn('setup.house_rules', phase)
        self.assertIn('not yet', phase)

    def test_direct_keeps_hard_to_undo_confirmation(self):
        direct = text('templates/house-rules.md').split('## Direct', 1)[1]
        for action in ('deleting', 'restarting', 'firmware', 'version changes'):
            with self.subTest(action=action):
                self.assertIn(action, direct)
        guide = text('00-start-here/loosening-your-rules.md')
        self.assertNotRegex(guide, r'\bCareful\b(?! start)')


if __name__ == '__main__':
    unittest.main()
