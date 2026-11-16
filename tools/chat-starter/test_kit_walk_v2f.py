"""Regression checks for newcomer backup, install and hand-off guidance."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


def flat(path):
    return re.sub(r'\s+', ' ', (ROOT / path).read_text(encoding='utf-8')).lower()


class WalkFollowup(unittest.TestCase):
    def test_backup_setup_distinguishes_first_time_and_existing_in_both_guides(self):
        for path in ('00-start-here/from-a-chat-app.md', 'install/network-and-backups-first.md'):
            with self.subTest(path=path):
                text = flat(path)
                self.assertIn('first-time', text)
                self.assertIn('**custom**', text)
                self.assertIn('configure backup settings', text)
                self.assertIn('daily', text)
                self.assertIn('share folder', text)
                self.assertIn('retention', text)
                self.assertIn('recommended', text)

    def test_pi_nvme_default_and_card_first_prerequisites(self):
        text = flat('install/raspberry-pi.md')
        self.assertIn('default: use a usb enclosure', text)
        self.assertIn('monitor, keyboard, mouse', text)
        self.assertIn('raspberry pi os desktop', text)
        self.assertIn('display cable', text)

    def test_path_b_skips_onboarding_if_already_onboarded(self):
        text = flat('00-start-here/README.md').split('## path b:', 1)[1].split('## path a:', 1)[0]
        self.assertIn('already onboarded', text)
        self.assertIn('skip step 1', text)
        self.assertIn('confirm the owner account', text)

    def test_handoff_records_actual_installation_type(self):
        text = flat('00-start-here/from-a-chat-app.md')
        note = text.split('hand-off from a chat app (<date>)', 1)[1].split('```', 1)[0]
        self.assertIn('<installation type from system information>', note)
        self.assertNotIn('<version>, home assistant os,', note)

    def test_password_prompt_offers_session_sign_out_and_token_review(self):
        text = flat('00-start-here/from-a-chat-app.md')
        step = text.split('3. **a new password.**', 1)[1].split('4. **who is still signed in.**', 1)[0]
        self.assertIn('sign out other sessions', step)
        self.assertIn('**yes**', step)
        self.assertIn('long-lived tokens', step)
        self.assertIn('owner', step)
        self.assertNotIn('does not sign out devices', step)

if __name__ == '__main__':
    unittest.main()
