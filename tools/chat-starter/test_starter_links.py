"""Broken included links stop a build; fenced examples remain literal."""
import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('starter_links_builder', HERE / 'build_starter.py')
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


class StarterLinks(unittest.TestCase):
    def build_fixture(self, a, b='# Target\n## Setup\n', heading=None):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            (root / 'a.md').write_text(a, encoding='utf-8')
            (root / 'b.md').write_text(b, encoding='utf-8')
            with mock.patch.object(bs, 'SOURCES', [('a.md', None), ('b.md', heading)]):
                return bs.build(root)

    def test_renamed_heading_rejects_the_old_fragment(self):
        with self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#setup'):
            self.build_fixture('[backup](b.md#setup)\n', '# Target\n## Setup safely\n')

    def test_bad_fragment_rejects_rebuilding_and_checking(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            (root / 'a.md').write_text('# Start\n[backup](#missing)\n')
            (root / 'output.md').write_text('previous valid output\n')
            with mock.patch.object(bs, 'ROOT', root), mock.patch.object(bs, 'OUT', 'output.md'), \
                    mock.patch.object(bs, 'SOURCES', [('a.md', None)]), \
                    mock.patch.object(bs, 'build', wraps=lambda: original_build(root)):
                for args in ([], ['--check']):
                    with self.subTest(args=args), self.assertRaisesRegex(SystemExit, 'unresolved.*#missing'):
                        bs.main(args)
            self.assertEqual((root / 'output.md').read_text(), 'previous valid output\n')

    def test_partial_source_preserves_existing_excluded_sections_only(self):
        output = self.build_fixture('[outside](b.md#later) [included](b.md#setup)\n',
                                    '# Target\n## Setup\nSteps\n## Later\nMore\n', 'Setup')
        self.assertIn('[outside](b.md#later)', output)
        self.assertIn('[included](#starter-part-2--setup)', output)
        with self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
            self.build_fixture('[bad](b.md#missing)\n', heading='Setup')

    def test_external_links_and_code_spans_are_not_validated(self):
        source = '[web](https://example.invalid/#missing) [other](other.md#missing) `[code](#missing)`\n'
        self.assertIn(source, self.build_fixture(source))

    def test_blockquoted_fences_preserve_literal_links_and_resume_prose(self):
        for opening, closing in [('```md', '```'), ('~~~~md', '~~~~')]:
            for prefix in ('> ', '> > ', '> - '):
                # Synthetic quoted examples deliberately contain invalid links.
                continuation = '>   ' if prefix == '> - ' else prefix
                source = ('# Start\n' + prefix + opening + '\n' + continuation
                          + '[literal](b.md#setup) [missing](b.md#missing)\n' + continuation + closing
                          + '\n' + continuation + '\n[real](b.md#setup)\n')
                with self.subTest(prefix=prefix, opening=opening):
                    output = self.build_fixture(source)
                    self.assertIn(continuation + '[literal](b.md#setup) [missing](b.md#missing)', output)
                    self.assertIn('[real](#starter-part-2--setup)', output)
                    self.assertIn(continuation + closing + '\n' + continuation + '\n[real]', output)

    def test_reference_definitions_validate_and_rewrite_included_targets(self):
        for target in ('b.md#missing', '<b.md#missing>'):
            with self.subTest(target=target), self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
                self.build_fixture('[backup][target]\n\n[target]: ' + target + ' "Title"\n')
        output = self.build_fixture('[backup][target]\n\n[target]: <b.md#setup> "Title"\n')
        self.assertIn('[target]: #starter-part-2--setup "Title"', output)

    def test_reference_definitions_preserve_excluded_targets_and_code(self):
        source = ('[outside][later]\n[later]: b.md#later\n'
                  '```md\n[example]: b.md#missing\n```\n')
        output = self.build_fixture(source, '# Target\n## Setup\nSteps\n## Later\nMore\n', 'Setup')
        self.assertIn('[later]: b.md#later', output)
        self.assertIn('[example]: b.md#missing', output)
        # Include a rewritten definition so this also detects removal of the fix.
        self.assertIn('[inside]: #starter-part-2--setup',
                      self.build_fixture('[inside]: b.md#setup\n'))

    def test_quoted_reference_definition_rejects_missing_heading(self):
        with self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
            self.build_fixture('> [t]: b.md#missing\n')

    def test_list_marker_reference_definition_rejects_missing_heading(self):
        for prefix in ('- ', '+ ', '* ', '1. ', '2) ', '> - ', '- > ', '> > '):
            with self.subTest(prefix=prefix), self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
                self.build_fixture(prefix + '[t]: b.md#missing\n')

    def test_quoted_reference_definition_rewrites_valid_heading_and_keeps_prefix(self):
        source = '> See [x][t].\n>\n> [t]: b.md#setup\n'
        self.assertIn('> See [x][t].\n>\n> [t]: #starter-part-2--setup\n', self.build_fixture(source))
        for prefix in ('- ', '> - ', '- > ', '> > '):
            with self.subTest(prefix=prefix):
                self.assertIn(prefix + '[t]: #starter-part-2--setup "Title"',
                              self.build_fixture(prefix + '[t]: <b.md#setup> "Title"\n'))

    def test_list_continuation_reference_definitions_reject_missing_headings(self):
        for start, prefix in (('- outer\n  - inner\n', '    '),
                              ('- outer\n  - inner\n', '    > '),
                              ('123. item\n', '     '),
                              ('> - outer\n>   - inner\n', '>     ')):
            with self.subTest(start=start, prefix=prefix), \
                    self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
                self.build_fixture(start + '\n' + prefix + '[t]: b.md#missing\n\n'
                                   + prefix + '[x][t]\n')

    def test_list_continuation_reference_definitions_rewrite_and_keep_prefixes(self):
        for start, prefix in (('- outer\n  - inner\n', '    '),
                              ('- outer\n  - inner\n', '    > '),
                              ('123. item\n', '     '),
                              ('> - outer\n>   - inner\n', '>     ')):
            with self.subTest(start=start, prefix=prefix):
                source = start + '\n' + prefix + '[t]: <b.md#setup> "Title"\n\n' + prefix + '[x][t]\n'
                output = self.build_fixture(source)
                self.assertIn(prefix + '[t]: #starter-part-2--setup "Title"\n', output)
                self.assertIn(prefix + '[x][t]\n', output)

    def test_reference_destination_on_next_line_is_checked_and_rewritten(self):
        for start, prefix in (('', ''), ('- outer\n  - inner\n\n', '    '), ('', '> ')):
            with self.subTest(start=start, prefix=prefix):
                label = start + prefix + '[t]:\n'
                with self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
                    self.build_fixture(label + prefix + '  b.md#missing\n')
                self.assertIn(label + prefix + '  #starter-part-2--setup "Title"\n',
                              self.build_fixture(label + prefix + '  <b.md#setup> "Title"\n'))
        self.assertIn('[real](#starter-part-2--setup)',
                      self.build_fixture('> [t]:\n[real](b.md#setup)\n'))

    def test_next_line_reference_does_not_consume_a_sibling_item(self):
        for first, second in (('- ', '- '), ('1. ', '2. '),
                              ('> - ', '> - '), ('- outer\n  - ', '  - ')):
            for target in ('missing', 'setup'):
                with self.subTest(first=first, target=target):
                    source = first + '[t]:\n' + second + 'b.md#' + target + '\n'
                    try:
                        output = self.build_fixture(source)
                    except SystemExit as exc:
                        self.fail('literal sibling item was checked as a reference: ' + str(exc))
                    self.assertIn(source, output)

    def test_next_line_reference_does_not_cross_quote_and_list_containers(self):
        for first, second in (('> ', '- '), ('- ', '> '),
                              ('> > ', '> - '), ('> - ', '> > ')):
            for target in ('missing', 'setup'):
                with self.subTest(first=first, second=second, target=target):
                    source = first + '[t]:\n' + second + 'b.md#' + target + '\n'
                    try:
                        output = self.build_fixture(source)
                    except SystemExit as exc:
                        self.fail('literal new container was checked as a reference: ' + str(exc))
                    self.assertIn(source, output)

    def test_next_line_reference_keeps_the_same_item_or_quote(self):
        for first, second in (('- ', '  '), ('> ', '>'),
                              ('> - ', '>   '), ('- > ', '  > ')):
            with self.subTest(first=first, second=second):
                label = first + '[t]:\n'
                with self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
                    self.build_fixture(label + second + 'b.md#missing\n')
                self.assertIn(label + second + '#starter-part-2--setup\n',
                              self.build_fixture(label + second + 'b.md#setup\n'))

    def test_indented_reference_example_is_not_an_active_definition(self):
        source = 'Paragraph.\n\n    [t]: b.md#missing\n    [literal][t]\n'
        self.assertIn(source, self.build_fixture(source))

    def test_blank_line_before_nested_fence_preserves_literals_and_resumes_prose(self):
        for start, prefix in (('- outer\n  - inner\n', '    '),
                              ('123. item\n', '     '),
                              ('> - outer\n>   - inner\n', '>     ')):
            for target in ('missing', 'setup'):
                with self.subTest(start=start, target=target):
                    literal = (prefix + '```md\n' + prefix + '[literal](b.md#' + target + ')\n'
                               + prefix + '[t]: b.md#' + target + '\n' + prefix + '```\n')
                    source = start + '\n' + literal + '\n[real](b.md#setup)\n'
                    try:
                        output = self.build_fixture(source)
                    except SystemExit as exc:
                        self.fail('A fenced literal was processed as prose: ' + str(exc))
                    self.assertIn(literal, output)
                    self.assertIn('[real](#starter-part-2--setup)', output)
                    with self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
                        self.build_fixture(start + '\n' + literal + '\n[real](b.md#missing)\n')

    def test_quote_marker_inside_top_level_fence_is_literal(self):
        source = '```md\n> [example](b.md#missing)\n```\n[real](b.md#setup)\n'
        output = self.build_fixture(source)
        self.assertIn('```md\n> [example](b.md#missing)\n```', output)
        self.assertIn('[real](#starter-part-2--setup)', output)

    def test_extra_quote_marker_inside_quoted_fence_is_literal(self):
        source = '> ```md\n> > [example](b.md#setup)\n> ```\n[real](b.md#setup)\n'
        output = self.build_fixture(source)
        self.assertIn('> > [example](b.md#setup)', output)
        self.assertIn('[real](#starter-part-2--setup)', output)

    def test_quote_inside_list_fence_is_literal(self):
        for source in ('- ```md\n  > [example](b.md#missing)\n  ```\n',
                       '- > ```md\n  > > [example](b.md#missing)\n  > ```\n'):
            with self.subTest(source=source):
                output = self.build_fixture(source + '[real](b.md#setup)\n')
                self.assertIn(source, output)
                self.assertIn('[real](#starter-part-2--setup)', output)

    def test_leaving_an_unclosed_quote_does_not_hide_bad_prose_links(self):
        with self.assertRaisesRegex(SystemExit, 'unresolved.*b.md#missing'):
            self.build_fixture('> ```md\n> literal\n[real](b.md#missing)\n')

    def test_review_heading_rename_in_real_sources_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            for path, _ in bs.SOURCES:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((bs.ROOT / path).read_text(), encoding='utf-8')
            source = root / '00-start-here/from-a-chat-app.md'
            old = '## First change on a box already running\n'
            text = source.read_text()
            self.assertIn(old, text)
            source.write_text(text.replace(old, old.rstrip() + ' safely\n'), encoding='utf-8')
            with self.assertRaisesRegex(SystemExit, 'unresolved.*first-change-on-a-box-already-running'):
                bs.build(root)


original_build = bs.build

if __name__ == '__main__':
    unittest.main()
