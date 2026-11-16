"""Synthetic label, exception and command-line behavior; standard library only."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ha_terms_checker', HERE / 'check_ha_terms.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class TermsTests(unittest.TestCase):
    def setUp(self):
        self.data = checker.load_data(HERE / 'ha-terms.json')
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def findings(self, text, path='guide.md'):
        return checker.check_text(text, path, self.data)

    def test_old_labels_fail_and_current_labels_do_not(self):
        self.assertEqual({x['rule'] for x in self.findings('Open Add-ons, Developer Tools and HACS.')},
                         {'apps', 'tools', 'marketplace'})
        self.assertEqual(self.findings('Open Apps, Tools and Marketplace.'), [])
        self.assertTrue(self.findings('An ADD-ON; add-ons; addons; addon.'))
        self.assertFalse(self.findings('Superaddons and addons_info are identifiers.'))

    def test_visible_inline_labels_and_link_labels_are_checked(self):
        self.assertEqual(len(self.findings('Open `Developer Tools` or [HACS](https://example.invalid/hacs).')), 2)
        self.assertTrue(self.findings('Developer **Tools**'))

    def test_code_identifiers_and_urls_are_exempt(self):
        self.assertEqual(self.findings('Use `hacs.repositories`, `hassio/addons`, `hacs` and https://example.invalid/hacs.'), [])
        self.assertTrue(self.findings('Open `HACS`.'))

    def test_fenced_code_is_exempt_but_plaintext_output_is_checked(self):
        text = '```yaml\nlegacy_label: HACS\n```\n~~~python\nlabel = "add-ons"\n~~~\n'
        self.assertEqual(self.findings(text), [])
        self.assertEqual(self.findings('```text\nOpen Developer Tools\n```')[0]['line'], 2)

    def test_exact_history_phrase_does_not_hide_another_old_label(self):
        self.data['allowlist'].append({'path': 'guide.md', 'text': 'formerly called add-ons', 'reason': 'Synthetic history.'})
        self.assertEqual(self.findings('Apps were formerly called add-ons.'), [])
        self.assertEqual(self.findings('Apps were formerly called add-ons. Open HACS.')[0]['rule'], 'marketplace')
        self.assertEqual(self.findings('HACS', 'examples/dry-run-2026-10-14.md'), [])
        self.assertTrue(self.findings('HACS', 'examples/current-guide.md'))

    def test_whole_file_history_exception_cannot_be_broad(self):
        data = copy.deepcopy(self.data)
        data['allowlist'] = [{'path': '*.md', 'scope': 'file', 'reason': 'too broad'}]
        path = self.root / 'terms.json'; path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            checker.load_data(path)

    def test_invalid_and_duplicate_term_data_are_rejected(self):
        path = self.root / 'terms.json'
        for data in ([], {}, {'schema_version': 1, 'terms': []},
                     {**self.data, 'terms': self.data['terms'] * 2}):
            with self.subTest(data_type=type(data).__name__):
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    checker.load_data(path)

    def test_no_symlink_or_private_storage_reads_and_no_file_mutation(self):
        target = self.root / 'guide.md'; target.write_text('Open HACS.\n')
        (self.root / 'linked.md').symlink_to(target)
        (self.root / '.storage').mkdir(); (self.root / '.storage/private.md').write_text('add-ons')
        (self.root / 'token.txt').write_text('add-ons')
        before = target.read_bytes()
        report = checker.check_root(self.root, self.data)
        self.assertEqual(report['files'], 1)
        self.assertEqual(report['findings'][0]['path'], 'guide.md')
        self.assertEqual(target.read_bytes(), before)

    def test_enforce_report_only_clean_and_error_exit_codes(self):
        guide = self.root / 'guide.md'; guide.write_text('HACS.\nPRIVATE_SOURCE_CANARY\n')
        for extra, expected in (([], 1), (['--report-only'], 0)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = checker.main(['--root', str(self.root), '--json', *extra])
            self.assertEqual(code, expected)
            self.assertEqual(json.loads(output.getvalue())['count'], 1)
            self.assertNotIn('PRIVATE_SOURCE_CANARY', output.getvalue())
        guide.write_text('Marketplace.\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main(['--root', str(self.root)]), 0)
        bad = self.root / 'invalid.json'; bad.write_text('{}')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(checker.main(['--root', str(self.root), '--data', str(bad), '--report-only']), 2)
            self.assertEqual(checker.main(['--root', str(self.root / 'missing'), '--report-only']), 2)
            guide.write_bytes(b'\xff')
            self.assertEqual(checker.main(['--root', str(self.root), '--report-only']), 2)
            guide.write_text('Marketplace.')
            def denied_directory(*args, **kwargs):
                kwargs['onerror'](OSError('synthetic directory denial'))
                return iter(())
            with mock.patch.object(checker.os, 'walk', side_effect=denied_directory):
                self.assertEqual(checker.main(['--root', str(self.root), '--report-only']), 2)


    def test_emphasized_old_labels_fail_in_enforcing_mode(self):
        guide = self.root / 'guide.md'
        for marker in ('_', '__', '*', '**', '***'):
            with self.subTest(marker=marker):
                guide.write_text('Open ' + ', '.join(marker + name + marker for name in
                                 ('HACS', 'Add-ons', 'Developer Tools')) + '.')
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = checker.main(['--root', str(self.root), '--json'])
                self.assertEqual(code, 1)
                self.assertEqual({f['rule'] for f in json.loads(output.getvalue())['findings']},
                                 {'apps', 'tools', 'marketplace'})

    def test_soft_wrapped_visible_labels_keep_their_starting_line(self):
        text = 'Current guide.\n\nOpen _Developer\nTools_ and Home Assistant\nCommunity Store.\n'
        rows = self.findings(text)
        self.assertEqual([(r['rule'], r['line']) for r in rows], [('tools', 3), ('marketplace', 4)])
        self.assertTrue(self.findings('Devel*oper* Tools'))
        self.assertTrue(self.findings('Open [Developer\nTools](https://example.invalid/menu).'))

    def test_identifiers_and_separate_paragraphs_do_not_become_old_labels(self):
        for text in ('HACS_config and addons_info.', 'Use `hacs.repositories` and `hassio/addons`.',
                     'Developer\n\nTools', '- Developer\n- Tools', 'Developer `hacs` Tools'):
            with self.subTest(text=text):
                self.assertEqual(self.findings(text), [])
        self.assertEqual(self.findings('`Developer _Tools_`'), [])

    def test_fences_in_list_and_quote_containers_leave_following_prose_visible(self):
        examples = [
            ('1. Section\n\n    ```yaml\n    addons: HACS\n    ```\n\nOpen HACS.', 7),
            ('> ```yaml\n> addons: HACS\n> ```\n\nOpen HACS.', 5),
            ('- > ~~~python\n  > label = "HACS"\n  > ~~~\n\nOpen Add-ons.', 5),
            ('> ```text\n> Open HACS.\n> ```', 2),
            ('> ````yaml\n> HACS\n> ```\n> Add-ons\n> ````\nOpen HACS.', 6),
        ]
        for text, line in examples:
            with self.subTest(text=text):
                rows = self.findings(text)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['line'], line)

    def test_leaving_a_fence_container_does_not_hide_later_prose(self):
        for text in ('> ```yaml\n> addons: HACS\nOpen HACS.',
                     '- ```yaml\n  addons: HACS\nOpen HACS.'):
            with self.subTest(text=text):
                self.assertEqual([(r['rule'], r['line']) for r in self.findings(text)], [('marketplace', 3)])

    def test_formerly_add_ons_is_only_a_history_span_exception(self):
        self.assertEqual(self.findings('Apps (formerly add-ons).', 'install/README.md'), [])
        rows = self.findings('Apps (formerly add-ons).\n\nOpen Add-ons.', 'install/README.md')
        self.assertEqual([(r['rule'], r['line']) for r in rows], [('apps', 3)])
        self.assertTrue(self.findings('Formerly add-ons; open HACS.'))

    def test_escaped_and_inline_menu_paths_are_visible(self):
        for text in ('Open Add\\-ons.', 'Open `Settings/Add-ons`.', 'Open `HACS.`'):
            with self.subTest(text=text):
                self.assertEqual(len(self.findings(text)), 1)

    def test_nonprose_markdown_shapes_are_not_labels(self):
        for text in ('Example:\n\n    HACS Add-ons\n\nUse Apps.',
                     '<!-- HACS\nAdd-ons -->\nUse Apps.',
                     '[hacs]: https://example.invalid\nUse Apps.',
                     'Count: {{addons}}.', 'Use `addon-config`.'):
            with self.subTest(text=text):
                self.assertEqual(self.findings(text), [])

    def test_history_exceptions_are_case_and_path_exact(self):
        self.assertEqual(self.findings('Apps (formerly add-ons).', 'install/README.md'), [])
        self.assertTrue(self.findings('Apps (FORMERLY ADD-ONS).', 'install/README.md'))
        self.assertTrue(self.findings('Apps (formerly add-ons).', 'other.md'))

    def test_baseline_rejects_new_text_paths_and_repeated_findings(self):
        guide = self.root / 'guide.md'
        guide.write_text('Open HACS.\n')
        initial = checker.check_root(self.root, self.data)
        baseline = checker.baseline_counts(initial['findings'])
        self.assertEqual(checker.new_findings(initial['findings'], baseline), [])
        for path, text in ((guide, 'Open HACS.\n\nOpen HACS.\n'),
                           (guide, 'Install from HACS.\n'),
                           (self.root / 'new.md', 'Open HACS.\n')):
            with self.subTest(path=path.name, text=text):
                guide.write_text('Open HACS.\n')
                path.write_text(text)
                self.assertTrue(checker.new_findings(checker.check_root(self.root, self.data)['findings'], baseline))
                if path != guide:
                    path.unlink()
        guide.write_text('Marketplace.\n')
        self.assertEqual(checker.new_findings(checker.check_root(self.root, self.data)['findings'], baseline), [])

    def test_ratchet_cli_reports_existing_but_fails_new_findings(self):
        guide = self.root / 'guide.md'
        guide.write_text('Open HACS.\n')
        report = checker.check_root(self.root, self.data)
        self.data['baseline'] = [dict(row, count=1) for row in
                                 ({key: finding[key] for key in ('path', 'rule', 'sha256')}
                                  for finding in report['findings'])]
        data = self.root / 'terms.json'
        data.write_text(json.dumps(self.data))
        args = ['--root', str(self.root), '--data', str(data), '--report-only', '--ratchet', '--json']
        approved = mock.patch.dict(checker.REVIEWED_BASELINE_LIMITS, {
            checker.baseline_identity(self.data['baseline'][0]): 1}, clear=True)
        approved.start()
        self.addCleanup(approved.stop)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(checker.main(args), 0)
        self.assertEqual(json.loads(output.getvalue())['count'], 1)
        guide.write_text('Open HACS.\n\nOpen Developer Tools.\n')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(checker.main(args), 1)
        self.assertEqual(json.loads(output.getvalue())['new_count'], 1)
        self.data['baseline'][0]['count'] = False
        data.write_text(json.dumps(self.data))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(checker.main(args), 2)

    def test_plain_hyphenated_identifier_is_not_a_menu_label(self):
        self.assertEqual(self.findings('Use addon-config.'), [])
        self.assertEqual(self.findings('Use addon-config, then open Add-ons.' )[0]['rule'], 'apps')
        self.assertTrue(self.findings('Open Add-on settings or Add-ons.'))

    def test_source_and_matching_baseline_addition_cannot_bless_a_new_finding(self):
        guide = self.root / 'guide.md'
        guide.write_text('Open HACS.\n')
        report = checker.check_root(self.root, self.data)
        self.data['baseline'].extend(dict(row, count=1) for row in
            ({key: finding[key] for key in ('path', 'rule', 'sha256')} for finding in report['findings']))
        data = self.root / 'terms.json'
        data.write_text(json.dumps(self.data))
        args = ['--root', str(self.root), '--data', str(data), '--ratchet', '--json']
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(checker.main(args), 1)
        result = json.loads(output.getvalue())
        self.assertEqual(len(result['baseline_growth']), 1)

    def test_baseline_count_growth_fails_even_without_a_new_source_finding(self):
        self.data['baseline'][0]['count'] += 1
        data = self.root / 'terms.json'
        data.write_text(json.dumps(self.data))
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(checker.main(['--root', str(self.root), '--data', str(data), '--ratchet', '--json']), 1)
        self.assertEqual(len(json.loads(output.getvalue())['baseline_growth']), 1)

    def test_baseline_can_shrink_without_new_permission(self):
        self.data['baseline'] = [row for row in self.data['baseline'] if row['count'] > 1]
        for row in self.data['baseline']:
            row['count'] -= 1
        data = self.root / 'terms.json'
        data.write_text(json.dumps(self.data))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main(['--root', str(self.root), '--data', str(data), '--ratchet', '--json']), 0)



if __name__ == '__main__':
    unittest.main()
