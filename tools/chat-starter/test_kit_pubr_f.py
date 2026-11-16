"""KIT-PUBr.f: the public-release review's must-fix findings stay fixed (F1 the public name, F2 the hook reads the
pushed refs, F8 the beta page names only public items). F2's real pushes and F3's separators are in
templates/guard/selftest.py, which runs them; this file checks the text that tells a stranger about them."""
import importlib.util
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class PublicName(unittest.TestCase):
    def test_readme_title(self):
        self.assertEqual(read("README.md").splitlines()[0], "# Whole Home Agent")

    def test_no_second_project_name(self):
        self.assertNotIn("Formerly", read("README.md"))

    def test_starter_first_line(self):
        self.assertTrue(read("00-start-here/chat-app-starter.md").startswith("# Whole Home Agent - "))

    def test_reader_client_strings(self):
        self.assertIn('"whole-home-agent-usage-reader/1"', read("templates/runtime/usage_reader.py"))
        self.assertIn('"whole-home-agent-usage-reader"', read("templates/runtime/usage_reader_codex.py"))

    def test_old_name_gone_from_the_tree(self):
        for path in ROOT.rglob("*"):
            skip = ".git" in path.parts or "__pycache__" in path.parts or path.name == pathlib.Path(__file__).name
            if not skip and path.is_file() and path.suffix in (".md", ".py", ".yaml", ".json", ".txt"):
                text = path.read_text(encoding="utf-8", errors="replace")
                self.assertNotIn("Whole Home Assistant", text, str(path.relative_to(ROOT)))
                self.assertNotIn("whole-home-assistant", text, str(path.relative_to(ROOT)))


class HookReadsPushedRefs(unittest.TestCase):
    def test_readme_hook_is_the_checked_stub(self):
        stub = re.search(r"HOOK_STUB = b'(.*)'", read("templates/guard/selftest.py")).group(1)
        hook_line = stub.split("\\n")[1]
        self.assertIn("--pushed-refs", hook_line)
        self.assertIn(hook_line, read("templates/guard/README.md"))

    def test_readme_and_docstring_say_what_the_hook_reads(self):
        for path in ("templates/guard/README.md", "templates/guard/push_guard.py"):
            text = " ".join(read(path).split())
            for words in ("--pushed-refs", "standard input", "a tag", "--all", "--tags"):
                self.assertIn(words, text, path)


def load_guard():
    spec = importlib.util.spec_from_file_location("push_guard", ROOT / "templates/guard/push_guard.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TagSignature(unittest.TestCase):
    """KIT-PUBr.f.pr4 F2: only a well-formed signature block at the end of a tag message is left out of the scan.
    The real pushes with a marker in the middle are in selftest.py; this checks the signed-tag shape itself."""

    def tag_lines(self, message):
        guard = load_guard()
        with tempfile.TemporaryDirectory() as tmp:
            def git(*args, data=None):
                return subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                                       *args], input=data, capture_output=True, check=True, text=True).stdout.strip()
            git("init", "-q")
            git("commit", "-q", "--allow-empty", "-m", "base")
            head = git("rev-parse", "HEAD")
            tag = git("mktag", data=f"object {head}\ntype commit\ntag v1\ntagger t <t@example.invalid> 0 +0000\n\n"
                                    + message)
            return [line for _, _, line in guard.message_lines(tmp, tag, "tag")]

    def test_trailing_signature_block_is_left_out(self):
        block = "-----BEGIN PGP SIGNATURE-----\n\niQEzBAABCAAdFiEE0aBcDeF1234+/abc=\n=AbCd\n-----END PGP SIGNATURE-----\n"
        self.assertEqual([line for line in self.tag_lines("release 1.0\n" + block) if line], ["release 1.0"])

    def test_text_after_a_marker_is_read(self):
        lines = self.tag_lines("release\n-----BEGIN SSH SIGNATURE-----\nnote: after the marker\n")
        self.assertIn("note: after the marker", lines)

    def test_text_after_an_end_marker_is_read(self):
        block = "-----BEGIN PGP SIGNATURE-----\n\niQEz=\n-----END PGP SIGNATURE-----\n"
        self.assertIn("note: after the block", self.tag_lines("release\n" + block + "note: after the block\n"))


class BetaPage(unittest.TestCase):
    def test_no_private_repository_link(self):
        self.assertNotIn("github.com/fatherdoctor/ha_severe_weather", read("blueprints/beta-testing.md"))

    def test_examples_name_no_private_item(self):
        # KIT-PUBr.f.pr F5: the switch, update entity and sample notice used the private item as their example.
        page = read("blueprints/beta-testing.md").lower()
        for words in ("severe_weather", "severe weather"):
            self.assertNotIn(words, page)


if __name__ == "__main__":
    unittest.main()
