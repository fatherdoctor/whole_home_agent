"""Regression checks for the jumping-ahead review findings."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def flat(path):
    return re.sub(r'\s+', ' ', (ROOT / path).read_text(encoding='utf-8')).lower()


def section(path, header):
    return flat(path).split(header, 1)[1].split('## ', 1)[0]


class JumpFollowup(unittest.TestCase):
    def test_midway_two_step_login_is_resolved_first(self):
        for path, heading in (('00-start-here/from-a-chat-app.md', '## jumping ahead'),
                              ('interview/phase-0-setup-interview.md', '## jumping ahead')):
            with self.subTest(path=path):
                body = section(path, heading)
                for phrase in ('half', 'setup key', 'fresh sign-in', 'off'):
                    self.assertIn(phrase, body)
                self.assertIn('never leave it half on', body)

    def test_helper_account_steps_are_explained_and_recorded(self):
        body = section('00-start-here/from-a-chat-app.md', '## jumping ahead')
        for phrase in ('someone else', 'former helper', 'new password', 'old sessions', 'long-lived tokens'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        skips = body.split('each skipped step', 1)[1]
        for phrase in ('new password', 'old sessions', 'long-lived tokens'):
            self.assertIn(phrase, skips)
        handoff = flat('00-start-here/from-a-chat-app.md').split('## the hand-off to the agent on the box', 1)[1]
        self.assertNotIn("the box is installed, the owner's and backed up", handoff)
        self.assertIn("account is the owner's unless those steps were skipped", handoff)

    def test_both_routes_use_canonical_backup_and_update_steps(self):
        for path in ('00-start-here/from-a-chat-app.md', 'interview/phase-0-setup-interview.md'):
            with self.subTest(path=path):
                body = section(path, '## jumping ahead')
                self.assertIn('first change on a box already running', body)
                self.assertIn('steps 1-3', body)
                self.assertIn('do not repeat', body)
        canonical = section('00-start-here/from-a-chat-app.md', '## first change on a box already running')
        self.assertIn('automatically before updating', canonical)
        self.assertIn('release notes', canonical)
        self.assertIn('confirm the installed version', canonical)
        self.assertIn('jumping ahead', canonical)
        self.assertIn('still make the local backup', canonical)

    def test_normal_chatgpt_handoff_points_to_own_documentation(self):
        body = section('00-start-here/from-a-chat-app.md', '## the hand-off to the agent on the box')
        preamble = body.split('1. **add the agent', 1)[0]
        self.assertIn("chatgpt app's own documentation", preamble)
        self.assertIn('step 3', preamble)

    def test_new_install_and_publisher_instructions_are_clear(self):
        for path in ('00-start-here/from-a-chat-app.md', 'interview/phase-0-setup-interview.md'):
            with self.subTest(path=path):
                body = section(path, '## jumping ahead')
                self.assertIn('onboarding', body)
                self.assertIn('instructions page where you found the app', body)
                self.assertIn('do not guess', body)

    def test_starter_has_one_unqualified_jump_heading(self):
        starter = (ROOT / '00-start-here/chat-app-starter.md').read_text(encoding='utf-8')
        self.assertEqual(len(re.findall(r'^#### Jumping ahead\s*$', starter, re.M)), 1)
        self.assertIn('#### Jumping ahead (Phase 0)', starter)


if __name__ == '__main__':
    unittest.main()
