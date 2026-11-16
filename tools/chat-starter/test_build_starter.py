#!/usr/bin/env python3
"""test_build_starter.py - checks for the chat-app starter file. Run: python3 tools/chat-starter/test_build_starter.py

Status: written (KIT-CHAT0, 2026-11-10). Standard library only. Exit 0 = every case passes.
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("build_starter", HERE / "build_starter.py")
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


def load_test_module(name, path):
    module_spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


template_tests = ROOT / "templates" / "tests"
GuardRailsText = load_test_module("starter_guard_rails_tests", template_tests / "test_guard_rails_text.py").GuardRailsText


def run_first_look_tests():
    # This standalone test executes its cases at import and finishes with sys.exit(result).
    try:
        load_test_module("starter_first_look_tests", template_tests / "test_first_look.py")
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    raise AssertionError("first-look test did not report its result")


def additional_test_scripts():
    """Tests included by the starter CI entry point, run individually and in order."""
    chat = sorted(path for path in HERE.glob("test_*.py") if path.name != "test_build_starter.py")
    templates = ROOT / "templates" / "tests"
    return chat + [templates / "test_first_look.py", templates / "test_guard_rails_text.py"]


class StarterRegressionSuites(unittest.TestCase):
    def test_additional_suites(self):
        for script in additional_test_scripts():
            if script.parent == template_tests:
                continue  # Imported: first-look cases and GuardRailsText.
            with self.subTest(script=script.relative_to(ROOT)):
                run = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_ha_terms_report_only(self):
        checker = ROOT / 'tools' / 'ha-terms' / 'check_ha_terms.py'
        run = subprocess.run([sys.executable, str(checker), '--report-only', '--ratchet', '--json'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        report = json.loads(run.stdout)
        self.assertGreater(report['files'], 0)
        self.assertEqual(report['new_count'], 0)

    def test_first_look_cases(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = run_first_look_tests()
        self.assertEqual(result, 0, output.getvalue())


class StarterFile(unittest.TestCase):
    def setUp(self):
        self.text = bs.build()

    def test_committed_copy_is_current(self):
        committed = (ROOT / bs.OUT).read_text(encoding="utf-8")
        self.assertEqual(committed, self.text, "rebuild: python3 tools/chat-starter/build_starter.py")

    def test_check_flag_passes_on_the_committed_copy(self):
        run = subprocess.run([sys.executable, str(HERE / "build_starter.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_every_source_is_a_part_in_order(self):
        heads = re.findall(r"^## Part (\d+): `([^`]+)`", self.text, re.M)
        self.assertEqual([p for _, p in heads], [p for p, _ in bs.SOURCES])
        self.assertEqual([int(n) for n, _ in heads], list(range(1, len(bs.SOURCES) + 1)))

    def test_the_evening_is_inline(self):
        # The things the card asks the one file to carry: Phase 0 questions, the install guide for each start
        # (Green, Pi, mini PC, a VM), onboarding, the account review, backups with Home Assistant Cloud first,
        # router optional, goal first, the hand-off.
        for needle in ("Phase 0", "Home Assistant Green", "mini PC", "Onboarding (starts 2, 3",
                       "Raspberry Pi Imager", "Proxmox", "You know nothing about this person",
                       "Refresh tokens", "sign out other sessions",
                       "Home Assistant Cloud first", "Router changes are optional", "The goal first",
                       "The hand-off to the agent on the box", "Hand-off from a chat app",
                       "Install on the box and sign in", "Git can wait", "needs a computer once"):
            self.assertIn(needle, self.text, needle)

    def test_return_without_agent_link_points_to_inline_section(self):
        self.assertIn('[Coming back without an agent on the box](#starter-part-1--coming-back-without-an-agent-on-the-box)', self.text)
        self.assertIn('id="starter-part-1--coming-back-without-an-agent-on-the-box"', self.text)
        self.assertRegex(self.text, r'(?m)^#{1,6} Coming back without an agent on the box\s*$')

    def test_only_one_top_level_heading(self):
        outside = []
        fence = False
        for line in self.text.splitlines():
            if line.lstrip().startswith("```"):
                fence = not fence
            elif not fence and re.match(r"#\s", line):
                outside.append(line)
        self.assertEqual(len(outside), 1, outside)

    def test_build_is_stable_and_check_detects_stale_output(self):
        self.assertEqual(bs.build(), self.text)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            for path, _ in bs.SOURCES:
                (tmp / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / path, tmp / path)
            same = bs.build(tmp)
            self.assertEqual(same, self.text)
            first = tmp / bs.SOURCES[0][0]
            first.write_text(first.read_text(encoding="utf-8") + "\nOne more line.\n", encoding="utf-8")
            changed = bs.build(tmp)
            self.assertNotEqual(changed, same)
            self.assertNotIn("sources hash", same.splitlines()[2])
            target = tmp / bs.OUT
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(same, encoding="utf-8")
            with mock.patch.object(bs, "ROOT", tmp), mock.patch.object(bs, "build", return_value=changed):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(bs.main(["--check"]), 1)
                    target.write_text(changed, encoding="utf-8")
                    self.assertEqual(bs.main(["--check"]), 0)

    def test_missing_section_is_refused(self):
        with self.assertRaises(SystemExit):
            bs.section("# Title\n\n## Something else\ntext\n", "Install on the box and sign in")

    def test_section_stops_at_next_heading_and_demote_skips_fences(self):
        src = "# T\n## A\nkeep\n### sub\nkeep too\n## B\ndrop\n"
        self.assertEqual(bs.section(src, "A"), "## A\nkeep\n### sub\nkeep too\n")
        self.assertEqual(bs.demote("# H\n```\n# not a heading\n```\n"), "### H\n```\n# not a heading\n```\n")

    def test_nothing_private_or_secret_shaped(self):
        # A coarse net; the kit's own push guard is the real check before a push.
        for pattern in (r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b", r"[\w.+-]+@[\w-]+\.[\w.]+",
                        r"\b(?:\d{1,3}\.){3}\d{1,3}\b(?<!0\.0\.0\.0)", r"ghp_\w{20,}", r"github_pat_\w{20,}"):
            hits = [m.group(0) for m in re.finditer(pattern, self.text)]
            hits = [h for h in hits if not h.startswith(("192.168.", "10.", "127.", "0.0.0.0", "1.1.1.1"))]
            self.assertEqual(hits, [], pattern)


if __name__ == "__main__":
    unittest.main(verbosity=1)
