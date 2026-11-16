"""Regression checks for KIT-GUARD-SWEEP.f's house-safety guidance."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def flat(path):
    return re.sub(r'\s+', ' ', read(path)).lower()


class GuardSweepFix(unittest.TestCase):
    def test_assist_uses_voice_exposure_default_and_control(self):
        voice = flat('adapters/voice/assist.md')
        self.assertIn('rule 2', voice)
        self.assertIn('settings → voice assistants → expose', voice)
        self.assertIn('no locks or alarm', voice)
        self.assertIn('misheard sentence', voice)
        self.assertNotIn('../../templates/agent-guard-rails.md', voice)

    def test_automation_default_names_both_exceptions_and_is_cited(self):
        safety = flat('principles/safety-and-security.md')
        rule = safety.split('19. [default, topic 4]', 1)[1].split('## why', 1)[0]
        for phrase in ('arming', 'disarming', 'locking', 'unlocking', 'code changes', 'person', 'rule 4', 'rule 16'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rule)
        self.assertIn('rule 19', flat('interview/generated-files.md'))

    def test_new_profile_has_no_fixed_lock_or_alarm_ban(self):
        profile = read('interview/profile-template.yaml')
        section = profile.rsplit('\n  agent:\n', 1)[1].split('\n  operations:', 1)[0]
        get = lambda name: re.search(r'^    '+name+r': \[([^]]*)\]', section, re.M).group(1).split(', ')
        self.assertEqual(get('never'), ['codes', 'contacts', 'consent'])
        self.assertEqual(get('may'), ['read-all-but-secrets', 'everything-not-limited'])
        self.assertIn('templates/agent-guard-rails.md', section)

    def test_leftover_prose_describes_the_person_in_the_loop(self):
        for path in ('principles/README.md', 'principles/safety-and-security.md', 'examples/lived-in-house.md'):
            with self.subTest(path=path):
                content = flat(path)
                self.assertIn('should not run without a person', content)
                self.assertNotIn('what an agent may never automate', content)
                self.assertNotIn('an agent must never do, already automated', content)

    def test_access_explanation_is_once_per_section_and_uses_lock_line(self):
        access = flat('install/agent-access.md')
        a = access.split('**be honest about the limit, whatever the runtime.**', 1)[1].split('what still needs a decision', 1)[0]
        b = access.split('3. **be honest about the limit.**', 1)[1].split('## 2.', 1)[0]
        for section in (a, b):
            with self.subTest(section=section[:35]):
                self.assertEqual(section.count('not access controls'), 1)
                self.assertIn('lock line', section)
                self.assertNotIn('permission boundary', section)

    def test_reviewed_lines_are_wrapped(self):
        markers = {'install/agent-access.md': ('done when',),
                   'adapters/agents/claude-code.md': ('optional guard rails',),
                   'adapters/voice/assist.md': ('exposure follows', 'misheard sentence')}
        for path, needles in markers.items():
            for line in read(path).splitlines():
                if any(needle in line.lower() for needle in needles):
                    with self.subTest(path=path, line=line):
                        self.assertLessEqual(len(line), 120)


if __name__ == '__main__':
    unittest.main()
