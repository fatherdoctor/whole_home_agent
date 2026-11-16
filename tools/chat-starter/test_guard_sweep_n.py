"""Regression checks for the guard-sweep follow-up's guide and profile fixes."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def flat(path):
    return re.sub(r'\s+', ' ', read(path)).lower()


class GuardSweepFollowup(unittest.TestCase):
    def test_rule_identifies_interview_topic_and_person_set_code_window(self):
        rule = flat('principles/safety-and-security.md').split('19. [default, topic 4]', 1)[1].split('## why', 1)[0]
        for phrase in ('code window', 'a person set', "person's act", 'rule 4', 'rule 16'):
            self.assertIn(phrase, rule)

    def test_interview_invites_owner_to_set_and_change_limits(self):
        section = flat('interview/phase-1-house-profile-interview.md').split('## topic 3', 1)[1].split('## topic 4', 1)[0]
        self.assertNotIn('must never automate', section)
        self.assertNotIn('never removed from it', section)
        self.assertIn('owner may change', section)

    def test_profile_records_house_rules_choice(self):
        setup = read('interview/profile-template.yaml').split('\nsetup:', 1)[1].split('\nprofile:', 1)[0]
        self.assertRegex(setup, r'(?m)^  house_rules: not yet\s+#.*Careful start.*Direct.*not yet')

    def test_followup_guidance_describes_both_addon_routes_and_names_source(self):
        guide = flat('00-start-here/from-a-chat-app.md')
        plan = guide.split('**what the plan answer means for tonight.**', 1)[1].split('**time, roughly.**', 1)[0]
        self.assertIn('at the hand-off', plan)
        self.assertIn('jumping ahead', plan)
        handoff = guide.split('## the hand-off to the agent on the box', 1)[1]
        self.assertIn('if no on-box agent is installed yet', handoff)
        phase = flat('interview/phase-0-setup-interview.md')
        self.assertRegex(phase, r'which start is yours.{0,65}00-start-here/from-a-chat-app\.md')

    def test_specified_ragged_wraps_are_reflowed_and_within_120(self):
        examples = (
            ('install/agent-access.md', "home assistant. check the runtime's"),
            ('templates/house-rules.md', "change the assistant's actual access"),
            ('templates/house-rules.md', 'changes. back up before editing.'),
            ('00-start-here/loosening-your-rules.md', 'return to careful start at any time.'),
            ('00-start-here/from-a-chat-app.md', 'the rules as installed; if the agent cannot do it, pause'),
        )
        for path, phrase in examples:
            with self.subTest(path=path, phrase=phrase):
                lines = read(path).splitlines()
                relevant = [line for line in lines if phrase in line.lower()]
                self.assertEqual(len(relevant), 1)
                self.assertLessEqual(len(relevant[0]), 120)
                self.assertGreater(len(relevant[0]), 70)


if __name__ == '__main__':
    unittest.main()
