#!/usr/bin/env python3
"""Keep the no-duplicate check ahead of both plug setup routes in the starter."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AlexaPlugOrder(unittest.TestCase):
    def test_exposure_check_precedes_native_add_and_matter_share(self):
        for path in ('install/voice-assistants.md', '00-start-here/chat-app-starter.md'):
            with self.subTest(path=path):
                text = (ROOT / path).read_text()
                text = text[text.index('A maker cloud skill cannot be shared'):]
                start = text.index('Before the first native plug add')
                native = text.index('Native add, including when discovery finds nothing')
                share = text.index('SHARE: leave voice working')
                self.assertLess(start, native)
                self.assertLess(start, share)
                check = text[start:native]
                self.assertIn('Expose new entities', check)
                self.assertIn('Settings > Voice assistants > Expose', check)
                self.assertIn('turn it off', check)
                self.assertIn('off by default', check)

    def test_each_add_checks_effective_exposure_and_original_routines(self):
        for path in ('install/voice-assistants.md', '00-start-here/chat-app-starter.md'):
            with self.subTest(path=path):
                text = (ROOT / path).read_text()
                start = text.index('After each add, before adding another plug')
                end = text.index('Native add, including when discovery finds nothing', start)
                check = text[start:end]
                for required in ('exposed list', 'Alexa device list', 'maker-skill entry',
                                 'hide only the new HA copy', 'retest its saved routines'):
                    self.assertIn(required, check)


class ExposureChoices(unittest.TestCase):
    def guides(self):
        for path in ('install/voice-assistants.md', '00-start-here/chat-app-starter.md'):
            yield path, (ROOT / path).read_text()

    def test_yaml_filter_guard_precedes_the_first_add(self):
        for path, text in self.guides():
            with self.subTest(path=path):
                text = text[text.index('A maker cloud skill cannot be shared'):]
                before = text[:text.index('Native add, including when discovery finds nothing')]
                for required in ('YAML filter', 'filter decides exposure', '`switch`', 'grayed out',
                                 'pause before adding the plug', 'Do not guess a YAML edit'):
                    self.assertIn(required, before)

    def test_script_add_uses_the_alexa_card_before_the_unexposed_entity_picker(self):
        for path, text in self.guides():
            with self.subTest(path=path):
                start = text.index('The goal is one phrase that sets chosen lamps')
                example = text[start:text.index('Turning off a running script', start)]
                card = example.index('On the **Amazon Alexa** card')
                button = example.index('**entities exposed** button')
                picker = example.index('Then choose **Expose entities**')
                confirm = example.index('Confirm only after')
                icons = example.index('assistant icons afterward')
                self.assertLess(card, button)
                self.assertLess(button, picker)
                self.assertLess(picker, confirm)
                self.assertLess(confirm, icons)
                for required in ('new script may not appear', 'individual script',
                                 'unfiltered', 'other assistants', 'master exposure switch'):
                    self.assertIn(required, example)
                self.assertNotIn('assistant filter', example)
                self.assertNotIn('filter by Alexa', example)

    def test_script_dialog_scope_uses_the_actual_title_and_subtitle(self):
        for path, text in self.guides():
            with self.subTest(path=path):
                start = text.index('The goal is one phrase that sets chosen lamps')
                example = text[start:text.index('Turning off a running script', start)]
                title = example.index('title must be **Expose entities**')
                subtitle = example.index('subtitle **to Amazon Alexa**')
                confirm = example.index('Confirm only after')
                self.assertLess(title, subtitle)
                self.assertLess(subtitle, confirm)
                self.assertNotIn('Expose to: Amazon Alexa', example)

    def test_preference_undo_is_shared_at_the_route_heading_level(self):
        for path, text in self.guides():
            with self.subTest(path=path):
                headings = [line for line in text.splitlines() if line.startswith('#')]
                move = next(line for line in headings if ' 3. MOVE:' in line)
                undo = next(line for line in headings if line.endswith(' Undo the exposure preference'))
                self.assertEqual(undo.split()[0], move.split()[0])
                self.assertIn('SHARE, KEEP, MOVE and the scene-script lesson', text)

    def test_preference_has_a_saved_value_and_an_explicit_undo_choice(self):
        for path, text in self.guides():
            with self.subTest(path=path):
                body = text[text.index('A maker cloud skill cannot be shared'):]
                before = body[:body.index('Native add, including when discovery finds nothing')]
                self.assertIn('record the old', before.lower())
                start = body.index('Undo the exposure preference')
                undo = body[start:body.index('Many Wi-Fi plugs: one pilot, then small batches', start)]
                for required in ('keep it off', 'restore the earlier value', 'future entities',
                                 'Do not restore it automatically', 'actual exposed list'):
                    self.assertIn(required, undo)
                self.assertGreaterEqual(body.count('undo-the-exposure-preference'), 2)

    def test_routine_pilot_exception_has_one_rule_and_early_handoffs(self):
        for path, text in self.guides():
            with self.subTest(path=path):
                body = text[text.index('The goal is to control each chosen device'):]
                start = body.index('Many Wi-Fi plugs: one pilot, then small batches')
                self.assertGreaterEqual(body[:start].count('many-wi-fi-plugs-one-pilot-then-small-batches'), 2)
                exception = body[start:body.index('Keep a private checklist', start)]
                for required in ('If every plug has a routine', 'saved complete routine',
                                 'agreed interruption', 'test every action'):
                    self.assertIn(required, exception)


if __name__ == '__main__':
    unittest.main()
