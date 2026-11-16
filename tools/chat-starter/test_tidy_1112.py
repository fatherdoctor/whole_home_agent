"""Regression checks for the guide, profile field, and starter CI coverage."""
import importlib.util
import pathlib
import re
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def flat(path):
    return re.sub(r'\s+', ' ', (ROOT / path).read_text(encoding='utf-8')).lower()


class TidyFollowup(unittest.TestCase):
    def test_house_automation_limits_use_the_priorities_field(self):
        text = (ROOT / 'interview/phase-1-house-profile-interview.md').read_text(encoding='utf-8')
        row = next(line for line in text.splitlines() if 'things you want the house not to automate' in line)
        self.assertIn('`priorities.never`', row)
        self.assertNotIn('`agent.never`', row)
        self.assertIn('design', row.lower())

    def test_proven_sequence_excludes_secrets_and_pairing_codes(self):
        rule = flat('00-start-here/from-a-chat-app.md').split('1. **one step at a time.**', 1)[1].split('2. **', 1)[0]
        self.assertIn('never bundle', rule)
        self.assertIn('secret', rule)
        self.assertIn('pairing code', rule)
        self.assertIn('chat', rule)

    def test_ignored_discovery_can_be_restored_in_both_paths(self):
        guide = flat('00-start-here/from-a-chat-app.md')
        for start, end in (('4. **if a "discovered" banner', 'then **your account'),
                           ('4. **skip the discovered devices', '5. **moving to wi-fi**')):
            section = guide.split(start, 1)[1].split(end, 1)[0]
            for phrase in ('settings > devices & services', 'filter', 'show ignored', 're-enable'):
                with self.subTest(path=start, phrase=phrase):
                    self.assertIn(phrase, section)

    def test_named_long_lines_are_reflowed(self):
        paths = {
            '00-start-here/from-a-chat-app.md': ('code, the two-step login', 'for an agent later installed',
                                                'those steps were skipped', 'ask it to read them before'),
            'templates/house-rules.md': ('install or read the instructions',),
        }
        for path, markers in paths.items():
            lines = (ROOT / path).read_text(encoding='utf-8').splitlines()
            for marker in markers:
                matches = [line for line in lines if marker in line.lower()]
                with self.subTest(path=path, marker=marker):
                    self.assertEqual(len(matches), 1)
                    self.assertLessEqual(len(matches[0]), 120)
        house = (ROOT / 'templates/house-rules.md').read_text(encoding='utf-8')
        self.assertNotIn('new session.\nThese instructions', house)

    def test_secrets_and_guard_rails_rule_continuations_wrap_at_120(self):
        text = (ROOT / '00-start-here/from-a-chat-app.md').read_text(encoding='utf-8')
        for start, end in (('3. **Keep secrets out of the chat.**', '4. **The goal first'),
                           ('7. **The owner decides.**', '8. **The owner builds')):
            block = text.split(start, 1)[1].split(end, 1)[0]
            for line in block.splitlines():
                with self.subTest(rule=start, line=line):
                    self.assertLessEqual(len(line), 120)

    def test_starter_entry_covers_all_chat_scripts_and_named_template_tests(self):
        spec = importlib.util.spec_from_file_location('starter_tests', HERE / 'test_build_starter.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        actual = {path.resolve() for path in module.additional_test_scripts()}
        expected = {path.resolve() for path in HERE.glob('test_*.py') if path.name != 'test_build_starter.py'}
        expected |= {(ROOT / 'templates/tests' / name).resolve() for name in
                     ('test_first_look.py', 'test_guard_rails_text.py')}
        self.assertEqual(actual, expected)
        self.assertTrue(callable(module.run_first_look_tests))
        self.assertTrue(issubclass(module.GuardRailsText, unittest.TestCase))
        discovered = unittest.TestLoader().loadTestsFromModule(module)
        self.assertGreaterEqual(discovered.countTestCases(), 5)
        with mock.patch.object(module, 'load_test_module', side_effect=SystemExit(1)):
            result = module.StarterRegressionSuites('test_first_look_cases').run()
        self.assertEqual(len(result.failures), 1, 'a failing first-look run must fail the starter job')


if __name__ == '__main__':
    unittest.main()
