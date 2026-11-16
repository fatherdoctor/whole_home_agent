"""Regression tests for section fences, inlined links and the starter header."""
import importlib.util
import pathlib
import re
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('builder_under_test', HERE / 'build_starter.py')
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


class StarterReviewFix(unittest.TestCase):
    def test_section_ignores_headings_inside_fences_before_and_within_selection(self):
        source = ('```md\n## Install\nwrong\n```\n## Install\nBefore\n```sh\n'
                  '## an example comment\necho hello\n```\nAfter\n## Next\n')
        expected = '## Install\nBefore\n```sh\n## an example comment\necho hello\n```\nAfter\n'
        self.assertEqual(bs.section(source, 'Install'), expected)

    def test_heading_demotion_preserves_tilde_and_long_backtick_fences(self):
        source = '## Steps\n~~~text\n# literal content\n~~~\n````text\n```\n# still literal\n````\n'
        expected = '#### Steps\n~~~text\n# literal content\n~~~\n````text\n```\n# still literal\n````\n'
        self.assertEqual(bs.demote(source), expected)

    def test_inlined_links_use_unique_source_scoped_anchors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            (root / 'a.md').write_text('# A\n## Shared\n[A](#shared) [B](nested/b.md#shared) '
                                       '[outside](other.md#shared) `[code](nested/b.md#shared)`\n~~~md\n[B](nested/b.md#shared)\n~~~\n')
            (root / 'nested').mkdir()
            (root / 'nested/b.md').write_text('# B\n## Shared\n[Back](../a.md#shared)\n'
                                             '## Shared\n[second](#shared-1)\n## Shared-1\n[third](#shared-1-1)\n')
            with mock.patch.object(bs, 'SOURCES', [('a.md', None), ('nested/b.md', None)]):
                output = bs.build(root)
        for needle in ('id="starter-part-1--shared"', 'id="starter-part-2--shared"',
                       'id="starter-part-2--shared-1"', 'id="starter-part-2--shared-1-1"', '[A](#starter-part-1--shared)',
                       '[B](#starter-part-2--shared)', '[Back](#starter-part-1--shared)',
                       '[second](#starter-part-2--shared-1)', '[third](#starter-part-2--shared-1-1)',
                       '[outside](other.md#shared)', '`[code](nested/b.md#shared)`',
                       '~~~md\n[B](nested/b.md#shared)\n~~~'):
            with self.subTest(needle=needle):
                self.assertIn(needle, output)

    def test_actual_inlined_links_do_not_point_to_separate_files(self):
        output = bs.build()
        self.assertIn('[Coming back](#starter-part-1--coming-back-without-an-agent-on-the-box)', output)
        self.assertIn('[Your first automation](#starter-part-10)', output)
        self.assertIn('id="starter-part-10"', output)

    def test_generated_anchors_are_unique_and_rewritten_links_resolve(self):
        output = bs.build()
        ids = re.findall(r'<a id="([^"]+)"></a>', output)
        links = re.findall(r'\]\(#(starter-part-[^)]*)\)', output)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(links)
        self.assertEqual(set(links) - set(ids), set())

    def test_real_part_text_is_preserved_apart_from_link_destinations(self):
        root = HERE.parents[1]
        parts = []
        for number, (path, section) in enumerate(bs.SOURCES, 1):
            source = (root / path).read_text(encoding='utf-8')
            body = bs.section(source, section) if section else source
            anchors = bs.heading_anchors(body, number, source=source, section_heading=section)
            parts.append((path, body, anchors, section is None))
        targets = {path: (number, anchors, whole) for number, (path, _, anchors, whole) in enumerate(parts, 1)}

        def canonical(text):
            text = re.sub(r'^<a id="[^"]+"></a>\n', '', text, flags=re.M)
            return re.sub(r'\]\([^)]*\)', '](TARGET)', text)

        for path, body, anchors, _ in parts:
            with self.subTest(path=path):
                rendered = bs.render_part(body, path, anchors, targets)
                self.assertEqual(canonical(rendered), canonical(bs.demote(body)))

    def test_malformed_external_target_does_not_break_building(self):
        line = '[external](http://[)'
        self.assertEqual(bs.rewrite_links(line, 'a.md', {}), line)

    def test_header_omits_global_source_hash(self):
        self.assertNotIn('sources hash', bs.build().splitlines()[2])


if __name__ == '__main__':
    unittest.main()
