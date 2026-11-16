"""Regression tests for list fences and links into partially inlined sources."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('starter_builder_n', HERE / 'build_starter.py')
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


class StarterEdgeCases(unittest.TestCase):
    def test_list_fence_closer_uses_content_indent(self):
        source = '## A\n1. step\n   ```\n   # literal\n      ```\n   text\n## B\n'
        self.assertEqual(bs.section(source, 'A'),
                         '## A\n1. step\n   ```\n   # literal\n      ```\n   text\n')
        self.assertTrue(bs.demote(source).endswith('   text\n#### B\n'))
        self.assertEqual(bs.section('## A\n    ```\n## B\n', 'A'), '## A\n    ```\n')

    def test_inline_and_nested_list_fences_close_in_their_container(self):
        inline = '## A\n- ```text\n  # literal\n     ```\n## B\n'
        self.assertEqual(bs.section(inline, 'A'), '## A\n- ```text\n  # literal\n     ```\n')
        nested = '## A\n- parent\n  - child\n    ~~~~\n    # literal\n       ~~~~\n## B\n'
        self.assertEqual(bs.section(nested, 'A'),
                         '## A\n- parent\n  - child\n    ~~~~\n    # literal\n       ~~~~\n')
        self.assertTrue(bs.demote(nested).endswith('       ~~~~\n#### B\n'))

    def test_fence_inside_an_empty_list_item_uses_list_indent(self):
        source = '## A\n-\n  ```\n  # literal\n     ```\n## B\n'
        self.assertEqual(bs.section(source, 'A'), '## A\n-\n  ```\n  # literal\n     ```\n')
        self.assertTrue(bs.demote(source).endswith('     ```\n#### B\n'))

    def test_partial_source_fragment_uses_original_document_numbering(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'a.md').write_text('# A\n[earlier](b.md#steps) [included](b.md#steps-1)\n')
            (root / 'b.md').write_text('## Steps\nnot included\n## Install\n### Steps\nincluded\n## Next\n')
            with mock.patch.object(bs, 'SOURCES', [('a.md', None), ('b.md', 'Install')]):
                output = bs.build(root)
        self.assertIn('[earlier](b.md#steps)', output)
        self.assertIn('[included](#starter-part-2--steps-1)', output)
        self.assertIn('id="starter-part-2--steps-1"', output)

    def test_whole_file_link_to_partial_source_remains_external(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'a.md').write_text('# A\n[whole](b.md) [section](b.md#install)\n')
            (root / 'b.md').write_text('## Before\nnot included\n## Install\nincluded\n## Next\n')
            with mock.patch.object(bs, 'SOURCES', [('a.md', None), ('b.md', 'Install')]):
                output = bs.build(root)
        self.assertIn('[whole](b.md)', output)
        self.assertIn('[section](#starter-part-2--install)', output)

    def test_header_wrap_keeps_the_complete_instruction_together(self):
        line = bs.build().splitlines()[2]
        self.assertIn('do not edit by hand', line)
        self.assertLessEqual(len(line), 120)


if __name__ == '__main__':
    unittest.main()
