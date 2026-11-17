#!/usr/bin/env python3
"""selftest.py - test the guard in scratch repositories, or check the installed pre-push hook.

Status: template (KIT-GRD, 2026-10-23; more plants KIT-SAFE, 2026-11-01; long line and WebP KIT-SAFE.f, 2026-11-02;
direct hook check KIT-DRY.f4, 2026-11-10). The level-1 readiness test: `python3 guard/selftest.py` from the house
repository, or `python3 templates/guard/selftest.py` in the kit. Default exit 0 = all guard and hook fixtures passed;
1 = a fixture failed or hook cases could not run; 2 = setup error. The guard must block every planted item and pass the clean commits.
The default also tests hook verification in scratch repositories. It never runs the current repository's hooks.
Use --guard-only for the original planted/clean checks without direct-executable hook fixtures, including when
validating a manual guard path on a restricted runtime.
To run the installed hook directly, without pushing:
    python3 guard/selftest.py --check-hook --repo . --remote origin
This prints only JSON status/method/reason, never hook output, paths or remote locations. Check-mode exits:
0 = the exact shipped hook stub delegates to an existing guard and exits 0; 1 = guard refused, errored or timed out
(fix it, never bypass); 2 = execution denied after permission sanity checks (diagnosis required); 3 = installation,
wiring or lookup error (fix it). Missing execute bits and malformed/custom hooks are installation or wiring errors.
No result automatically selects manual mode. Unknown custom hooks need separate review, never arbitrary shell parsing.
An empty stdin exercises the installed hook; then real pushes in a scratch repository, through the same hook and
guard, prove that another branch, a tag, --all and --tags are judged (KIT-PUBr F2), and that a tag of a blob or a
tree, a YAML block value after a bare carriage return and a diff.noprefix setting do not let a secret through. The default fixtures separately
test the guard's planted items.
Standard library only. Nothing is pushed outside scratch repositories. Only --check-hook runs an existing repository's hook.
"""
import argparse
import errno
import json
import math
import os
import pathlib
import signal
import struct
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
GUARD = HERE / "push_guard.py"
# Built from pieces so this file does not trip the guard itself.
PLANTS = [
    ("literal password", "ha/wifi.yaml", "wifi_" + "password: " + "hunter22"),
    ("password in JSON", "tools/cfg.json", '{"user": "x", "pass' + 'word": "' + 'hunter22"}'),
    ("password in a URL", "docs/notes.md", "rtsp://admin:" + "hunter22" + "@camera.local/stream"),
    ("door code in prose", "docs/guests.md", "The door " + "code is " + "4821."),
    ("GitHub token", "tools/push.sh", "TOKEN_IS " + "ghp_" + "A1b2C3x4" * 5),
    ("sk- API key", "docs/setup.md", "key " + "sk-" + "ant-api03-" + "x9Y8z7W6" * 4),
    ("long hex", "docs/notes.md", "webhook " + "0123456789abcdef" * 3),
    ("phone number", "docs/contacts.md", "call 555" + "-201-" + "4477"),
    ("phone, ten bare digits", "docs/contacts.md", "call 205" + "555" + "0147"),
    ("phone, E.164", "docs/contacts.md", "call +1" + "205" + "555" + "0147"),
    ("household name", "docs/notes.md", "Ask Sample Person to check the porch light."),
    ("recorder database", "ha/home-assistant_v2.db", "not a database"),
    ("git credentials", ".git-credentials", "placeholder"),
]
# KIT-XR-GUARD F1-F5: a value the line diff never showed whole. A plant is a path and its text, or a list of them.
ACCENTED = "Zo" + "\u00eb" + " Example"  # an accented listed name, which json.dumps writes as an escape


def escaped(text):
    return "".join("\\u%04x" % ord(c) for c in text)


UNKNOWN_BINARY = b"\x1f\x8b\x08\x00" + bytes(6) + bytes(range(256)) * 2
PLANTS_XR = [
    ("password in a YAML block scalar (F1)", "ha/wifi.yaml", "wifi_" + "password: |-\n  " + "hunter22"),
    ("password in a UTF-16 file (F2)", "tools/cfg.json", ('{"pass' + 'word": "hunter22"}\n').encode("utf-16")),
    ("password a .gitattributes -diff hides (F2)", [(".gitattributes", "tools/cfg.json -diff"),
                                                    ("tools/cfg.json", '{"pass' + 'word": "hunter22"}')]),
    ("binary of a kind the guard cannot read (F2)", "fw/node.bin", UNKNOWN_BINARY),
    ("password key written as escapes (F3)", "tools/cfg.json", '{"' + escaped("pass" + "word") + '": "hunter22"}'),
    ("accented listed name escaped by json.dumps (F3)", "tools/cfg.json", json.dumps({"contact": ACCENTED})),
    ("listed name in a file name (F5)", "docs/Sample Person.md", "ordinary text"),
]
# KIT-PUBr F3: a character an editor shows as a line break, inside one line of the file, must not hide what follows.
SEPARATORS = [("carriage return", "\r"), ("vertical tab", "\x0b"), ("form feed", "\x0c"),
              ("file separator", "\x1c"), ("group separator", "\x1d"), ("record separator", "\x1e"),
              ("next line", "\x85"), ("line separator", "\u2028"), ("paragraph separator", "\u2029")]
PLANTS_XR += [(f"password after a {name} inside one line (KIT-PUBr F3)", "ha/notes.yaml",
               "note: ok" + sep + "wifi_" + "password: " + "hunter22") for name, sep in SEPARATORS]
PLANTS_XR.append(("password in a YAML block value after a bare carriage return (KIT-PUBr.f.pr F2)", "ha/wifi.yaml",
                  ("wifi_" + "password: |\r  " + "hunter22\n").encode()))
PLANTS_XR.append(("an allow marker covers only its own piece of a split line (KIT-PUBr F3)", "ha/notes.yaml",
                  "note: example guard: allow sample text\r" + "wifi_" + "password: " + "hunter22"))
CLEAN = [
    ("ha/packages/porch.yaml", "alias: Porch light on at sunset"),
    ("docs/links.md", "See https://github.com/owner/repo/commit/" + "0a1b2c3d4e" * 4 + " for the fix."),
    ("docs/wifi.md", "The password is in secrets.yaml under wifi_password."),
    ("ha/notes.yaml", "description: |\n  The porch light turns on at sunset."),
    ("ha/wifi.yaml", "wifi_" + "password: >-\n  !secret wifi_password"),
    ("docs/utf16.txt", "Porch light notes, saved by a Windows editor.\n".encode("utf-16")),
    ("fw/listed.bin", UNKNOWN_BINARY),  # on binary.txt: the owner has looked at it
]
BINARY_LIST = "fw/listed.bin"
# The plants, five photo/long-line/list plants, the KIT-XR-GUARD plants, the long-line pass and the clean commits.
GUARD_CASES = len(PLANTS) + 5 + len(PLANTS_XR) + 3
SHRINK_LIST = "docs/board.md"
# A long one-line file (a minified script, a blob) of runs that once made two shapes backtrack for minutes (KIT-SAFE.f
# F1); the guard must pass it, and quickly.
LONG_LINE = "sk-" * 20000 + "z" * 60000 + "://" + "x" * 20000
LONG_LINE_LIMIT = 20
HOOK_TIMEOUT = 10
HOOK_EXIT = {"pass": 0, "fail": 1, "unavailable": 2, "error": 3}
HOOK_STUB = b'#!/bin/sh\nexec python3 guard/push_guard.py --repo . --remote "$1" --pushed-refs\n'


PUSHED_SECRET = "wifi_" + "pass" + "word: " + "hunter22" + "hunter22"  # guard: allow invented fixture value
# KIT-PUBr F2: pushes that send refs other than the checked-out branch, and (KIT-PUBr.f.pr F1-F3) three ways a
# push once went through with a secret: a tag of a blob or a tree, a YAML block value after a bare carriage return,
# and a repository with diff.noprefix set. Each case: (label, how it is made, the push, whether it plants a secret).
# KIT-PUBr.f.pr2 and .pr3 added six more: a block key changed over an old value (also in UTF-16), a PIN after a UTF-8
# byte-order mark, a block value after YAML's non-specific tag, a commit message, and an annotated tag's message on
# a commit the remote already has. KIT-PUBr.f.pr4 added a message after a signature marker (F2) and tag chains at and
# past the depth the guard reads (F3). A clean chain of 21 is refused, not passed unread; a clean chain of 20 and the
# last case, a clean branch, must go through.
# v1.1 added fourteen: a character that prints as nothing or marks the one before it (one per Unicode class), a value
# on the line after its key (YAML plain, YAML quoted, JSON), a value inside a signature-shaped block at the end of a
# tag message, near copies of secrets.yaml and .env, a token as a branch name, the message a merge copies from a
# signed tag into its header, and two that must go through: a pin mapping under a key that names a pin, and a
# submodule.
# The v1.1 review added eighteen (FILES, and a submodule update that must go through): a comment line between a key
# and its value, a quoted value with a colon, a braille blank and two controls before a key, copies of secrets.yaml
# named before the extension, a `Subproject commit` line in a text file, and two templates that must go through.
# A quoted four-digit value under a PIN key, split so this file does not carry the shape itself.
PUSHED_PIN = "alarm_" + "pin: " + '"48' + '21"'  # guard: allow invented fixture value
REF_TOKEN = "gh" + "p_" + "A1b2C3x4" * 5  # guard: allow invented fixture value
# v1.1 review (KIT-GUARD-NEXTr) cases: one file on the side branch each. how: (label, path, text, planted).
_VALUE = PUSHED_SECRET.split(": ")[1]
_PIN_KEY, _PIN_VALUE = PUSHED_PIN.split(": ")
_PW_KEY = "wifi_" + "pass" + "word"
FILES = {
    "file comment": ("a password after a comment line under its YAML key (F1, R10)", "ha/side.yaml",
                     f"{_PW_KEY}:\n  # the guest network\n  {_VALUE}\n", True),
    "file comment pin": ("a quoted PIN after a comment line under its YAML key (F1, R25)", "ha/side.yaml",
                         f"{_PIN_KEY}:\n  # keypad\n  {_PIN_VALUE}\n", True),
    "file colon": ("a quoted next-line value with a colon and a space (F2, R14)", "ha/side.yaml",
                   f'{_PW_KEY}:\n  "{_VALUE}: {_VALUE}"\n', True),
    "file braille": ("a PIN after a braille blank (F3, R02)", "ha/side.yaml", "\u2800" + PUSHED_PIN + "\n", True),
    "file delete": ("a PIN after a delete control (F3, R03)", "ha/side.yaml", "\x7f" + PUSHED_PIN + "\n", True),
    "file escape": ("a PIN after an escape control (F3, R06)", "ha/side.yaml", "\x1b" + PUSHED_PIN + "\n", True),
    "file finder": ("a Finder copy of secrets.yaml (F4, R40)", "ha/secrets copy.yaml", "home_zip: 00000\n", True),
    "file download": ("a browser copy of secrets.yaml (F4, R41)", "ha/secrets (1).yaml", "home_zip: 00000\n", True),
    "file yml": ("secrets.yml (F4, R42)", "ha/secrets.yml", "home_zip: 00000\n", True),
    "file underscore": ("secrets.yaml_bak (F4, R43)", "ha/secrets.yaml_bak", "home_zip: 00000\n", True),
    "file dash": ("secrets-backup.yaml (F4, R44)", "ha/secrets-backup.yaml", "home_zip: 00000\n", True),
    "file env underscore": (".env_local (F4, R45)", ".env_local", "API_TOKEN=<your token>\n", True),
    "file swap": ("an editor swap file of secrets.yaml (F4, R46)", "ha/.secrets.yaml.swp", "home_zip: 00000\n", True),
    "file windows": ("a Windows copy of secrets.yaml (F4, R48)", "ha/secrets - Copy.yaml", "home_zip: 00000\n", True),
    "file subproject": ("a 40-hex value written as a submodule line in a text file (F6, R54)", "docs/notes.md",
                        "Subproject commit " + "0a1b2c3d4e" * 4 + "\n", True),
    "file dist": ("a .env.dist template with placeholders (F5, A09)", ".env.dist", "API_TOKEN=<your token>\n", False),
    "file template": ("a secrets.example.yaml template with placeholders", "ha/secrets.example.yaml",
                      "home_zip: <your zip>\n", False),
}
PUSH_CASES = [("a push of another branch", "branch", ["push", "origin", "side"], True),
              ("a push of a tag only that tag holds", "tag", ["push", "origin", "v9"], True),
              ("git push --all", "branch", ["push", "--all", "origin"], True),
              ("git push --tags", "tag", ["push", "--tags", "origin"], True),
              ("a tag of a blob", "blob tag", ["push", "origin", "v9"], True),
              ("a tag of a tree", "tree tag", ["push", "origin", "v9"], True),
              ("a YAML block value after a bare carriage return", "cr block", ["push", "origin", "side"], True),
              ("a commit, with diff.noprefix set", "noprefix", ["push", "origin", "side"], True),
              ("a merge commit, with diff.noprefix set", "noprefix merge", ["push", "origin", "side"], True),
              ("a block key changed over an old value", "key change", ["push", "origin", "side"], True),
              ("a UTF-16 block key changed over an old value", "key change utf16", ["push", "origin", "side"], True),
              ("a PIN after a UTF-8 byte-order mark", "bom", ["push", "origin", "side"], True),
              ("a block value after YAML's non-specific tag", "tag block", ["push", "origin", "side"], True),
              ("a commit message", "message", ["push", "origin", "side"], True),
              ("a tag message on a commit the remote has", "tag message", ["push", "origin", "v9"], True),
              ("a commit message after a PGP signature marker", "sig commit pgp", ["push", "origin", "side"], True),
              ("a commit message after an SSH signature end marker", "sig commit ssh", ["push", "origin", "side"],
               True),
              ("a tag message after a signature marker", "sig tag", ["push", "origin", "v9"], True),
              ("a planted tag inside a chain of 20 tags", "chain 20 planted", ["push", "origin", "v9"], True),
              ("a planted tag inside a chain of 21 tags", "chain 21 planted", ["push", "origin", "v9"], True),
              ("a clean chain of 21 tags, deeper than the guard reads", "chain 21", ["push", "origin", "v9"], True),
              ("a clean chain of 20 tags", "chain 20", ["push", "origin", "v9"], False),
              ("a PIN after a right-to-left override (format character)", "mark cf", ["push", "origin", "side"], True),
              ("a token key after a variation selector (combining mark)", "mark mn", ["push", "origin", "side"], True),
              ("a PIN after an enclosing mark", "mark me", ["push", "origin", "side"], True),
              ("a password on the line after its YAML key", "next yaml", ["push", "origin", "side"], True),
              ("a quoted PIN on the line after its YAML key", "next quoted", ["push", "origin", "side"], True),
              ("a password on the line after its JSON key", "next json", ["push", "origin", "side"], True),
              ("a key id inside a signature-shaped block at the end of a tag message", "sig block",
               ["push", "origin", "v9"], True),
              ("a copy of secrets.yaml under a near name", "near secrets", ["push", "origin", "side"], True),
              ("a .env file under a near name", "near env", ["push", "origin", "side"], True),
              ("a token as the branch name", "clean", ["push", "origin", "side:refs/heads/" + REF_TOKEN], True),
              ("a tag message a merge copies into its commit header", "mergetag", ["push", "origin", "side"], True),
              ("an ESPHome pin mapping under a secret-shaped key", "pin mapping", ["push", "origin", "side"], False),
              ("a submodule added", "submodule", ["push", "origin", "side"], False),
              ("a submodule updated", "submodule update", ["push", "origin", "side"], False),
              *[(label, how, ["push", "origin", "side"], planted) for how, (label, _, _, planted) in FILES.items()],
              ("a clean branch", "clean", ["push", "origin", "side"], False)]
AUTHOR = ["-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid"]
PUSHED_VALUE = PUSHED_SECRET.split(": ")[1]
SIGNATURE_START = "-----BEGIN PGP SIGNATURE-----"


# A key id in the shape of the AWS documentation's example, split so this file does not carry the shape itself.
KEY_ID = "AK" + "IA" + "IOSFODNN7" + "EXAMPLE"
MARKS = {"mark cf": "\u202e", "mark mn": "\ufe0f", "mark me": "\u20dd"}


def mergetag_commit(work, side):
    """A merge commit of main and side whose header copies a signed tag of side (`mergetag`), as `git merge` writes
    it for a signed tag, with the planted value in the copied tag's message. Made by hand: no signing key is needed."""
    tag = (f"object {side}\ntype commit\ntag v1\ntagger selftest <selftest@example.invalid> 0 +0000\n\nrelease\n"
           f"{PUSHED_SECRET}\n{SIGNATURE_START}\n\niQEz=\n{SIGNATURE_START.replace('BEGIN', 'END')}\n")
    first, *rest = tag.rstrip("\n").split("\n")
    header = "mergetag " + first + "\n" + "".join(" " + line + "\n" for line in rest)
    person = "selftest <selftest@example.invalid> 0 +0000"
    body = (f"tree {git_out(work, 'rev-parse', side + '^{tree}')}\nparent {git_out(work, 'rev-parse', 'main')}\n"
            f"parent {side}\nauthor {person}\ncommitter {person}\n{header}\nmerge v1\n")
    return git_out(work, "hash-object", "-t", "commit", "-w", "--stdin", input=body.encode())


def block(key, props=""):
    """A YAML block scalar: `key: [props] |` and the planted value on the next line."""
    return f"{key}: {props}|\n  {PUSHED_VALUE}\n"


def plant_ref(work, how):
    """Make the ref one push case sends (`side` or `v9`), with the secret only there; main stays checked out."""
    secret_file = PUSHED_SECRET.encode() + b"\n"
    if how in ("blob tag", "tree tag"):
        blob = git_out(work, "hash-object", "-w", "--stdin", input=secret_file)
        target = blob if how == "blob tag" else git_out(work, "mktree", input=f"100644 blob {blob}\tnote.yaml\n".encode())
        git(work, "tag", "v9", target)
        return
    if how == "tag message":  # main is already on the remote: only the tag object and its message are new
        git(work, *AUTHOR, "tag", "-a", "v9", "-m", PUSHED_SECRET, "main")
        return
    if how == "sig block":  # a block shaped like a signature, at the very end of the message, holding a key id
        end = SIGNATURE_START.replace("BEGIN", "END")
        git(work, *AUTHOR, "tag", "-a", "v9", "--cleanup=verbatim", "-m",
            f"release\n\n{SIGNATURE_START}\n\n{KEY_ID}\n{end}\n", "main")
        return
    if how == "sig tag":
        git(work, *AUTHOR, "tag", "-a", "v9", "-m", "release\n\n" + SIGNATURE_START + "\n" + PUSHED_SECRET, "main")
        return
    if how.startswith("chain"):  # tags of tags on main; with "planted", the innermost tag carries the secret
        depth, target = int(how.split()[1]), "main"
        for n in range(depth - 1):
            git(work, *AUTHOR, "-c", "advice.nestedTag=false", "tag", "-a", "chain-tmp", "-m",
                PUSHED_SECRET if n == 0 and how.endswith("planted") else f"step {n}", target)
            target = git_out(work, "rev-parse", "chain-tmp")
            git(work, "tag", "-d", "chain-tmp")  # the object stays; only the outermost tag gets a name
        git(work, *AUTHOR, "-c", "advice.nestedTag=false", "tag", "-a", "v9", "-m", "release", target)
        return
    git(work, "checkout", "-q", "-b", "scratch", "main")
    if how.startswith("key change"):  # the value goes in under a plain key, then only the key changes
        codec = "utf-16" if how.endswith("utf16") else "utf-8"
        commit(work, "ha/side.yaml", block("label").encode(codec))
        commit(work, "ha/side.yaml", block("wifi_" + "password").encode(codec))
    elif how in MARKS:
        key = "porch_api_" + "token: " + PUSHED_VALUE if how == "mark mn" else PUSHED_PIN
        commit(work, "ha/side.yaml", MARKS[how] + key + "\n")
    elif how == "next yaml":
        commit(work, "ha/side.yaml", "wifi_" + "password:\n  " + PUSHED_VALUE + "\n")
    elif how == "next quoted":
        commit(work, "ha/side.yaml", PUSHED_PIN.replace(": ", ":\n  ") + "\n")
    elif how == "next json":
        commit(work, "tools/cfg.json", '{\n  "wifi_' + 'password":\n    "' + PUSHED_VALUE + '"\n}\n')
    elif how == "near secrets":
        commit(work, "ha/secrets.yaml.bak", "home_zip: 00000\n")
    elif how == "near env":
        commit(work, ".env.local", "API_TOKEN=" + "abcdefghijklmnopqrstuvwx" + "\n")
    elif how == "mergetag":
        commit(work, "ha/side.yaml", "alias: Porch light")
        merge = mergetag_commit(work, git_out(work, "rev-parse", "HEAD"))
        git(work, "update-ref", "refs/heads/scratch", merge)
    elif how == "pin mapping":
        commit(work, "esphome/node.yaml", "interrupt_" + "pin:\n  number: GPIO4\n  inverted: true\n")
    elif how.startswith("submodule"):
        git(work, "update-index", "--add", "--cacheinfo", f"160000,{'0a1b2c3d4e' * 4},vendor/lib")
        git(work, *AUTHOR, "commit", "-qm", "add a submodule")
        if how == "submodule update":  # the remote has the first commit; only the update is new
            git(work, "push", "-q", "--no-verify", "origin", "scratch:refs/heads/side")
            git(work, "update-index", "--cacheinfo", f"160000,{'e4d3c2b1a0' * 4},vendor/lib")
            git(work, *AUTHOR, "commit", "-qm", "update a submodule")
    elif how in FILES:
        _, path, text, _ = FILES[how]
        commit(work, path, text)
    elif how == "bom":
        commit(work, "ha/side.yaml", b"\xef\xbb\xbf" + PUSHED_PIN.encode() + b"\n")
    elif how == "tag block":
        commit(work, "ha/side.yaml", block("wifi_" + "password", "! ").encode())
    elif how == "message" or how.startswith("sig commit"):
        message = {"message": PUSHED_SECRET,
                   "sig commit pgp": "fix\n\n" + SIGNATURE_START + "\n" + PUSHED_SECRET,
                   "sig commit ssh": "fix\n\n" + SIGNATURE_START.replace("PGP", "SSH") + "\n"
                                     + SIGNATURE_START.replace("PGP", "SSH").replace("BEGIN", "END") + "\n"
                                     + PUSHED_SECRET}[how]
        (work / "ha").mkdir(exist_ok=True)
        (work / "ha/side.yaml").write_text("alias: Porch light\n")
        git(work, "add", "ha/side.yaml")
        git(work, *AUTHOR, "commit", "-q", "--cleanup=verbatim", "-m", message)
    elif how == "noprefix merge":  # the merge itself adds the line, so only the merge rule can see it
        commit(work, "ha/other.yaml", "alias: Porch light")
        git(work, "checkout", "-q", "-b", "scratch-2", "main")
        commit(work, "ha/third.yaml", "alias: Hall light")
        git(work, *AUTHOR, "merge", "-q", "--no-commit", "scratch")
        (work / "ha/side.yaml").write_bytes(secret_file)
        git(work, "add", "ha/side.yaml")
        git(work, *AUTHOR, "commit", "-qm", "merge")
        git(work, "branch", "-q", "-D", "scratch")
        git(work, "branch", "-q", "-m", "scratch")
    elif how == "cr block":
        commit(work, "ha/side.yaml", b"wifi_" + b"password: |\r  " + PUSHED_SECRET.split(": ")[1].encode() + b"\n")
    else:
        commit(work, "ha/side.yaml", "alias: Porch light" if how == "clean" else PUSHED_SECRET)
    if how == "tag":
        git(work, *AUTHOR, "tag", "-a", "v9", "-m", "release")
    else:
        git(work, "branch", "-f", "side")
    if how.startswith("noprefix"):
        git(work, "config", "diff.noprefix", "true")
    git(work, "checkout", "-q", "main")
    git(work, "branch", "-q", "-D", "scratch")


def pushed_refs_proof(guard_file, hook_bytes=HOOK_STUB, timeout=60):
    """Real pushes to a scratch bare repository through a pre-push hook made of hook_bytes and a copy of guard_file,
    with main checked out and clean. Returns the labels of the cases that went wrong (a planted secret sent, or the
    clean branch refused); an empty list means the hook judges what each push sends, not the checked-out branch."""
    wrong = []
    with tempfile.TemporaryDirectory() as tmp:
        work, bare = pathlib.Path(tmp) / "work", pathlib.Path(tmp) / "remote.git"
        git(tmp, "init", "-q", "--bare", str(bare))
        git(tmp, "init", "-q", str(work))
        git(work, "checkout", "-q", "-b", "main")
        commit(work, "README.md", "scratch")
        (work / "guard").mkdir()
        (work / "guard/push_guard.py").write_bytes(pathlib.Path(guard_file).read_bytes())
        hook = work / ".git/hooks/pre-push"
        hook.write_bytes(hook_bytes)
        hook.chmod(0o755)
        git(work, "remote", "add", "origin", str(bare))
        git(work, "push", "-q", "--no-verify", "origin", "main")  # the remote's history: the tag-message case uses it
        for label, how, push, planted in PUSH_CASES:
            plant_ref(work, how)
            sent = subprocess.run(["git", "-C", str(work), *push], capture_output=True, timeout=timeout).returncode == 0
            if sent == planted:
                wrong.append(label)
            # Take the case's ref and setting away again, so the next case is judged on its own.
            git(work, "config", "--unset-all", "diff.noprefix", check=False)
            git(work, "tag", "-d", "v9", check=False)  # each case makes v9, side or both
            git(work, "branch", "-D", "side", check=False)
            git(work, "push", "-q", "--no-verify", "origin", ":refs/heads/side", ":refs/tags/v9",
                ":refs/heads/" + REF_TOKEN, check=False)
    return wrong


def manual_push_proof(guard_file):
    """The by-hand route (KIT-PUBr.f.pr3 F1): `push_guard.py --push origin side`, with main checked out, must refuse
    a planted secret on side and send nothing, and must send a clean side. Real pushes to a scratch bare repository;
    no hook is installed. Returns the labels of the cases that went wrong."""
    wrong = []
    with tempfile.TemporaryDirectory() as tmp:
        work, bare = pathlib.Path(tmp) / "work", pathlib.Path(tmp) / "remote.git"
        git(tmp, "init", "-q", "--bare", str(bare))
        git(tmp, "init", "-q", str(work))
        git(work, "checkout", "-q", "-b", "main")
        commit(work, "README.md", "scratch")
        git(work, "remote", "add", "origin", str(bare))
        git(work, "push", "-q", "origin", "main")
        for label, text, planted in (("by hand: a secret on a branch not checked out", PUSHED_SECRET, True),
                                     ("by hand: a clean branch not checked out", "alias: Porch light", False)):
            git(work, "checkout", "-q", "-b", "side", "main")
            commit(work, "ha/side.yaml", text)
            git(work, "checkout", "-q", "main")
            rc = subprocess.run([sys.executable, str(guard_file), "--repo", str(work), "--names", os.devnull,
                                 "--push", "origin", "side"], capture_output=True, timeout=60).returncode
            sent = bool(git_out(work, "ls-remote", "origin", "refs/heads/side"))
            if (rc == 0) == planted or sent == planted:
                wrong.append(label)
            git(work, "branch", "-q", "-D", "side")
            git(work, "push", "-q", "origin", ":refs/heads/side", check=False)
        # KIT-PUBr.f.pr4 F1: with push.followTags set, a push of a clean branch must not also send an annotated tag
        # the guard never read.
        git(work, "config", "push.followTags", "true")
        git(work, "checkout", "-q", "-b", "side", "main")
        commit(work, "ha/side.yaml", "alias: Porch light")
        git(work, *AUTHOR, "tag", "-a", "v9", "-m", PUSHED_SECRET)
        git(work, "checkout", "-q", "main")
        rc = subprocess.run([sys.executable, str(guard_file), "--repo", str(work), "--names", os.devnull,
                             "--push", "origin", "side"], capture_output=True, timeout=60).returncode
        if git_out(work, "ls-remote", "origin", "refs/tags/v9") or rc not in (0, 1):
            wrong.append("by hand with push.followTags: an unread tag sent")
    return wrong


def hook_result(status, reason):
    """A fixed vocabulary: no hook output, repository path or remote location enters the result."""
    method = {"pass": "hook", "fail": "hook", "unavailable": "unverified", "error": "unverified"}[status]
    return {"status": status, "method": method, "reason": reason}


def check_hook(repo, remote="origin", timeout=HOOK_TIMEOUT):
    """Resolve and directly execute Git's effective pre-push hook. Return sanitized status/method/reason.

    Git resolves core.hooksPath (including worktree configuration) and the shared hooks of linked worktrees.
    Require the exact shipped two-line stub and an existing guard target. Then run from the worktree root with
    Git's two hook arguments and empty stdin. No shell fallback or arbitrary shell parsing is used. Custom hooks
    remain unverified. The checker never installs or edits a hook in the repository it checks, and never pushes from
    it; to prove the installed guard reads every pushed ref, it copies that guard and the shipped stub into a
    temporary repository and pushes there, to a temporary bare repository only. The guard's actual protections
    are checked separately by --guard-only; stub verification alone does not attest to the target script's contents.
    """
    if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        return hook_result("error", "invalid_timeout")

    def query(*args):
        return subprocess.run(["git", "-C", str(repo), *args], stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                              errors="surrogateescape", timeout=HOOK_TIMEOUT)

    try:
        root = query("rev-parse", "--show-toplevel")
        if root.returncode:
            return hook_result("error", "repository_lookup_failed")
        root = pathlib.Path(root.stdout.rstrip("\n"))
        # Resolve relative hooksPath from the same directory Git uses when invoking pre-push.
        repo = root
        resolved = query("rev-parse", "--path-format=absolute", "--git-path", "hooks/pre-push")
        if resolved.returncode or not resolved.stdout.rstrip("\n"):
            return hook_result("error", "hook_lookup_failed")
        hook = pathlib.Path(resolved.stdout.rstrip("\n"))
        if not hook.is_file():
            return hook_result("error", "hook_missing_or_not_file")
        if not hook.stat().st_mode & 0o111:
            return hook_result("error", "hook_execute_bits_missing")
        if not os.access(hook, os.X_OK):
            return hook_result("error", "hook_access_denied")
        with hook.open("rb") as source:
            if source.read(len(HOOK_STUB) + 1) != HOOK_STUB:
                return hook_result("error", "hook_wiring_unverified")
        if not (root / "guard/push_guard.py").is_file():
            return hook_result("error", "guard_target_missing")
        location = query("remote", "get-url", "--push", "--", remote)
        if location.returncode or not location.stdout.rstrip("\n"):
            return hook_result("error", "remote_lookup_failed")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return hook_result("error", "hook_lookup_failed")

    try:
        process = subprocess.Popen([str(hook), remote, location.stdout.rstrip("\n")], cwd=root,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=(os.name == "posix"))
    except OSError as error:
        if error.errno == errno.EACCES:
            return hook_result("unavailable", "hook_execution_denied")
        if error.errno == errno.ENOEXEC:
            return hook_result("error", "hook_exec_format")
        return hook_result("error", "hook_start_failed")
    except ValueError:
        return hook_result("error", "hook_start_failed")
    try:
        rc = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        # A timeout is always a failed check, even if process cleanup itself meets a permission restriction.
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
        except OSError:
            try:
                process.kill()
            except OSError:
                pass
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        return hook_result("fail", "hook_timed_out")
    if rc != 0:
        return hook_result("fail", "hook_refused" if rc == 1 else "hook_error")
    # KIT-PUBr F2: the installed guard, behind the same hook, must judge what a push sends (PUSH_CASES). Proved by
    # real pushes in a scratch repository; nothing in this repository is pushed.
    try:
        if pushed_refs_proof(root / "guard/push_guard.py"):
            return hook_result("fail", "hook_misses_pushed_refs")
    except (OSError, subprocess.SubprocessError):
        return hook_result("error", "pushed_refs_proof_failed")
    return hook_result("pass", "hook_exit_0")


def jpeg(gps):
    """A tiny JPEG whose EXIF block holds GPS coordinates (gps=True) or only the GPS version tag (False)."""
    tags = [(0x0000, 1, 4, 0x00000202)]  # GPSVersionID 2.2.0.0, written in place
    if gps:
        tags += [(0x0002, 5, 3, 0), (0x0004, 5, 3, 0)]  # GPSLatitude, GPSLongitude (offsets patched below)
    gps_ifd = 8 + 2 + 12 + 4
    data_at = gps_ifd + 2 + 12 * len(tags) + 4
    tiff = b"II*\x00" + struct.pack("<I", 8)
    tiff += struct.pack("<H", 1) + struct.pack("<HHII", 0x8825, 4, 1, gps_ifd) + struct.pack("<I", 0)
    tiff += struct.pack("<H", len(tags))
    for k, (tag, typ, cnt, val) in enumerate(tags):
        tiff += struct.pack("<HHII", tag, typ, cnt, data_at + 24 * (k - 1) if typ == 5 else val)
    tiff += struct.pack("<I", 0) + b"\x00" * 24 * (len(tags) - 1)
    app1 = b"Exif\x00\x00" + tiff
    return b"\xff\xd8\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1 + b"\xff\xd9"


def git(repo, *args, check=True):
    subprocess.run(["git", "-C", str(repo), *args], check=check, capture_output=True, text=True)


def git_out(repo, *args, input=None):
    """The output of a git command that reads bytes on standard input, without its final new line."""
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          input=input).stdout.decode().strip()


def commit(repo, path, text=None):
    if isinstance(path, list):  # several files, one commit each
        for p, t in path:
            commit(repo, p, t)
        return
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        target.write_bytes(text)
    else:
        target.write_text(text + "\n")
    git(repo, "add", "-f", path)
    git(repo, "-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid", "commit", "-qm", "plant")


def webp(gps):
    """A WebP holding the same EXIF block bare in its EXIF chunk, as libwebp writes it (no "Exif\\0\\0")."""
    tiff = jpeg(gps)[12:-2]
    body = b"WEBP" + b"VP8X" + struct.pack("<I", 10) + b"\x08" + b"\x00" * 9 + b"EXIF" + struct.pack("<I", len(tiff)) + tiff
    return b"RIFF" + struct.pack("<I", len(body)) + body


def guard(repo, names, shrink, timeout=None, binary=None):
    """The guard's exit status; "timeout" when it ran past the time limit (a hook that hangs blocks every push)."""
    try:
        return subprocess.run([sys.executable, str(GUARD), "--repo", str(repo), "--range", "base..HEAD", "--names",
                               str(names), "--shrink", str(shrink)] + (["--binary", str(binary)] if binary else []), capture_output=True, text=True,
                              timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return "timeout"


def hook_fixtures(repo):
    """Exercise the real checker and CLI using only this temporary repository and its linked worktree."""
    failures = 0
    skipped = 0
    restricted = False
    git(repo, "remote", "add", "origin", "fixture-remote")
    default = repo / ".git/hooks/pre-push"
    spy = ("import pathlib, sys\n"
           "if sys.argv[1:] != ['--repo', '.', '--remote', 'origin', '--pushed-refs']: sys.exit(7)\n"
           "if not pathlib.Path('README.md').is_file(): sys.exit(7)\n"
           "refs = sys.stdin.buffer.read()\n"
           "if refs:  # the pushed-refs proof: a real push, judged by the real guard\n"
           "    import subprocess\n"
           f"    sys.exit(subprocess.run([sys.executable, {str(GUARD)!r}, *sys.argv[1:]], input=refs).returncode)\n"
           "print('guard fixture output')\n"
           "print('guard fixture diagnostic', file=sys.stderr)\n")

    def install(path, body=HOOK_STUB, executable=True):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        path.chmod(0o755 if executable else 0o644)

    def install_spy(root=repo, result=0, delay=False):
        target = root / "guard/push_guard.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(spy + ("import time\ntime.sleep(2)\n" if delay else "") + f"sys.exit({result})\n")

    def case(label, status="pass", method="hook", reason="hook_exit_0", target=repo,
             remote="origin", timeout=HOOK_TIMEOUT, cli_exit=None):
        nonlocal failures, skipped
        if restricted and status in ("pass", "fail"):
            skipped += 1
            print("SKIP hook check: " + label)
            return
        expected = {"status": status, "method": method, "reason": reason}
        if cli_exit is None:
            ok = check_hook(target, remote=remote, timeout=timeout) == expected
        else:
            result = subprocess.run([sys.executable, str(HERE / "selftest.py"), "--check-hook", "--repo",
                                     str(target), "--remote", remote], capture_output=True, text=True,
                                    timeout=HOOK_TIMEOUT + 5)
            try:
                ok = result.returncode == cli_exit and not result.stderr and json.loads(result.stdout) == expected
            except ValueError:
                ok = False
        failures += not ok
        # Never print a failed hook's output or an unexpected result that might contain private data.
        print(("ok   " if ok else "FAIL ") + f"hook check: {label}")

    install_spy()
    install(default)
    restricted = check_hook(repo)["reason"] == "hook_execution_denied"
    if restricted:
        print(f"selftest: this computer or sandbox ({sys.platform}) will not run hook files; use --guard-only and the by-hand push")
    case("canonical hook passes guard arguments, empty stdin and the worktree root")
    if not restricted:
        wrong = pushed_refs_proof(GUARD)
        failures += bool(wrong)
        print(("ok   " if not wrong else "FAIL ") + f"pushed refs: {sum(c[3] for c in PUSH_CASES)} pushes refused "
              "(another branch, tags, --all, --tags, a CR block value, diff.noprefix, a changed block key, a byte-order "
              "mark, a YAML tag, commit and tag messages, signature markers, tag chains of 20 and 21, format "
              "characters, combining marks, controls and a braille blank, a value on the line after its key or "
              "after a comment line, a quoted value with a colon, a signature-shaped block, near copies of secret "
              "files, a token as a branch name, a merged tag's message, a submodule line in a text file), a clean "
              "chain of 20 tags, a pin mapping, a submodule added and updated, two templates and a clean branch sent" + (f" (wrong: {', '.join(wrong)})" if wrong else ""))
        install(default, b'#!/bin/sh\nexec python3 guard/push_guard.py --repo . --remote "$1"\n')
        case("a hook from before --pushed-refs is not accepted", "error", "unverified", "hook_wiring_unverified")
        install(default)
    case("CLI returns only sanitized JSON and exit 0", cli_exit=0)
    nested = repo / "hook-fixture-subdir"
    nested.mkdir()
    case("repository subdirectory still uses the worktree root", target=nested)

    default.unlink()
    case("missing hook requires installation", "error", "unverified", "hook_missing_or_not_file", cli_exit=3)
    default.mkdir()
    case("a directory is not a hook", "error", "unverified", "hook_missing_or_not_file")
    default.rmdir()
    install(default, executable=False)
    case("missing execute bits require installation repair", "error", "unverified",
         "hook_execute_bits_missing", cli_exit=3)
    install(default)
    with patch("os.access", return_value=False):
        case("failed access sanity requires diagnosis", "error", "unverified", "hook_access_denied")
    install(default, b"exit 0\n")
    case("malformed hook is an installation error", "error", "unverified", "hook_wiring_unverified")
    install(default, f"#!{repo / 'missing-interpreter'}\n".encode())
    case("unknown interpreter requires installation review", "error", "unverified", "hook_wiring_unverified")
    install(default, b"#!/bin/sh\nexit 0\n")
    case("an exit-zero no-op cannot prove guard wiring", "error", "unverified", "hook_wiring_unverified", cli_exit=3)
    install(default, HOOK_STUB + b"exit 0\n")
    case("custom commands are not accepted by text matching", "error", "unverified", "hook_wiring_unverified")
    install(default)
    (repo / "guard/push_guard.py").unlink()
    case("canonical stub requires a guard target", "error", "unverified", "guard_target_missing")
    install_spy()

    original_popen = subprocess.Popen

    def deny_start(args, *positional, **keywords):
        if str(args[0]) == str(default):
            raise PermissionError(errno.EACCES, "fixture execution restriction")
        return original_popen(args, *positional, **keywords)

    with patch("subprocess.Popen", side_effect=deny_start):
        case("EACCES after mode/access checks remains unverified", "unavailable", "unverified",
             "hook_execution_denied")

    def bad_start(args, *positional, **keywords):
        if str(args[0]) == str(default):
            raise OSError(errno.ENOEXEC, "fixture executable format error")
        return original_popen(args, *positional, **keywords)

    with patch("subprocess.Popen", side_effect=bad_start):
        case("exec format errors require repair and never get a shell fallback", "error", "unverified",
             "hook_exec_format")

    def missing_start(args, *positional, **keywords):
        if str(args[0]) == str(default):
            raise FileNotFoundError(errno.ENOENT, "fixture missing interpreter")
        return original_popen(args, *positional, **keywords)

    with patch("subprocess.Popen", side_effect=missing_start):
        case("missing stub interpreter is a startup error", "error", "unverified", "hook_start_failed")
    install_spy(result=1)
    case("refusal cannot select manual bypass; output stays private", "fail", "hook", "hook_refused", cli_exit=1)
    install_spy(result=2)
    case("guard error cannot select manual bypass", "fail", "hook", "hook_error")
    install_spy(result=126)
    case("exit 126 is a failure, not proof of unavailable execution", "fail", "hook", "hook_error")
    install_spy(delay=True)
    case("timeout requires diagnosis", "fail", "hook", "hook_timed_out", timeout=0.05)
    if os.name == "posix":
        with patch("os.killpg", side_effect=PermissionError):
            case("timeout cleanup restriction cannot select manual bypass", "fail", "hook", "hook_timed_out",
                 timeout=0.05)

    install_spy()
    install(default, b"#!/bin/sh\nexit 0\n")
    relative = pathlib.Path("hook-fixture-relative hooks")
    install(repo / relative / "pre-push")
    git(repo, "config", "core.hooksPath", str(relative))
    case("relative core.hooksPath overrides the default hook")
    absolute = repo.parent / "hook-fixture-absolute hooks"
    install(absolute / "pre-push")
    git(repo, "config", "core.hooksPath", str(absolute))
    case("absolute core.hooksPath with spaces")
    (absolute / "pre-push").unlink()
    case("missing configured hook never falls back to the default", "error", "unverified",
         "hook_missing_or_not_file")

    git(repo, "config", "--unset", "core.hooksPath")
    install(default)
    linked = repo.parent / "hook-fixture-worktree"
    git(repo, "worktree", "add", "--quiet", "--detach", str(linked), "HEAD")
    install_spy(linked)
    case("linked worktree uses the shared default hook", target=linked)
    install(default, b"#!/bin/sh\nexit 0\n")
    install(repo / relative / "pre-push", b"#!/bin/sh\nexit 0\n")
    install(linked / relative / "pre-push")
    git(repo, "config", "core.hooksPath", str(relative))
    case("linked worktree resolves relative hooksPath at its own root", target=linked)
    git(repo, "config", "extensions.worktreeConfig", "true")
    install(absolute / "pre-push")
    git(linked, "config", "--worktree", "core.hooksPath", str(absolute))
    case("linked worktree's own hook configuration takes precedence", target=linked)
    case("missing remote is a setup error", "error", "unverified", "remote_lookup_failed", target=linked,
         remote="fixture-missing")
    case("invalid repository returns a sanitized lookup error", "error", "unverified", "repository_lookup_failed",
         target=repo.parent / "hook-fixture-missing")
    return failures, skipped


def fixture_selftest(guard_only=False):
    names_src = pathlib.Path(os.environ.get("GUARD_NAMES", HERE / "names.txt"))
    if not names_src.exists():
        names_src = HERE / "names.example.txt"
        print(f"selftest: no names.txt next to the guard; using {names_src.name}")
    failures = 0
    skipped = 0
    with tempfile.TemporaryDirectory() as tmp:
        repo = pathlib.Path(tmp) / "scratch"
        repo.mkdir()
        try:
            git(repo, "init", "-q")
            git(repo, "checkout", "-q", "-b", "main")
            commit(repo, "README.md", "scratch")
            commit(repo, SHRINK_LIST, "\n".join(f"| row {i} |" for i in range(40)))
            git(repo, "tag", "base")
            names = pathlib.Path(tmp) / "names.txt"
            names.write_text(names_src.read_text(encoding="utf-8") + "\nSample Person\n" + ACCENTED + "\n",
                             encoding="utf-8")  # the plants are always on the list
            binary = pathlib.Path(tmp) / "binary.txt"
            binary.write_text(BINARY_LIST + "\n")
            shrink = pathlib.Path(tmp) / "shrink.txt"
            shrink.write_text(SHRINK_LIST + "\n")
            plants = PLANTS + [("photo with GPS", "docs/photos/label.jpg", jpeg(True)),
                               ("WebP photo with GPS", "docs/photos/label.webp", webp(True)),
                               ("renamed photo with GPS (F4)", "docs/photos/label.dat", jpeg(True)),
                               ("token past the cut of a long line", "web/app.min.js", LONG_LINE + " ghp_" + "A1b2C3x4" * 5),
                               ("list file wiped", SHRINK_LIST, "| row 0 |")] + PLANTS_XR
            for label, path, *text in plants:
                commit(repo, path, *text)
                rc = guard(repo, names, shrink, binary=binary)
                ok = rc == 1
                failures += not ok
                print(("ok   " if ok else "FAIL ") + f"planted {label}: guard exit {rc} (want 1)")
                git(repo, "reset", "-q", "--hard", "base")
            commit(repo, "web/app.min.js", LONG_LINE)
            rc = guard(repo, names, shrink, timeout=LONG_LINE_LIMIT)
            ok = rc == 0
            failures += not ok
            print(("ok   " if ok else "FAIL ") + f"a {len(LONG_LINE):,}-character minified line passes inside "
                  f"{LONG_LINE_LIMIT} s: guard exit {rc} (want 0)")
            git(repo, "reset", "-q", "--hard", "base")
            for path, text in CLEAN + [("docs/photos/plain.jpg", jpeg(False)), ("docs/photos/plain.webp", webp(False)),
                                       ("docs/photos/plain.dat", jpeg(False))]:
                commit(repo, path, text)
            rc = guard(repo, names, shrink, binary=binary)
            ok = rc == 0
            failures += not ok
            print(("ok   " if ok else "FAIL ") + f"clean commits (a commit link, a password named by its key, a "
                  f"photo with no location, a YAML block, a UTF-16 note, a listed binary): guard exit {rc} (want 0)")
            wrong = manual_push_proof(GUARD)
            failures += bool(wrong)
            print(("ok   " if not wrong else "FAIL ") + "by-hand push (--push): a secret on a branch not checked out "
                  "refused and not sent, a clean one sent, no unread tag sent with push.followTags" + (f" (wrong: {', '.join(wrong)})" if wrong else ""))
            if not guard_only:
                hook_failures, skipped = hook_fixtures(repo)
                failures += hook_failures
                # Deny direct hook execution in the child while permitting Git and the Python interpreter.
                restricted = ("import errno, runpy, subprocess, sys\n"
                              "original = subprocess.Popen\n"
                              "def restricted(args, *positional, **keywords):\n"
                              "    if args[0] not in ('git', sys.executable):\n"
                              "        raise PermissionError(errno.EACCES, 'fixture direct execution restricted')\n"
                              "    return original(args, *positional, **keywords)\n"
                              "subprocess.Popen = restricted\n"
                              "sys.argv = [sys.argv[1], '--guard-only']\n"
                              "runpy.run_path(sys.argv[0], run_name='__main__')\n")
                result = subprocess.run([sys.executable, "-c", restricted, str(HERE / "selftest.py")],
                                        capture_output=True, text=True, timeout=60)
                ok = (result.returncode == 0 and not result.stderr and
                      sum(line.startswith("ok   ") for line in result.stdout.splitlines()) == GUARD_CASES and
                      "hook check:" not in result.stdout)
                failures += not ok
                print(("ok   " if ok else "FAIL ") + f"guard-only mode: the {GUARD_CASES} guard cases with direct hook execution denied")
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"selftest: setup failed: {e}", file=sys.stderr)
            return 2
    success = "the guard blocks the planted items" + ("" if guard_only else " and hook checks pass")
    if skipped:
        print(f"\n{failures} failing; {skipped} hook cases skipped because this runtime cannot run hook files")
    else:
        print(f"\n{failures} failing" if failures else f"\nall pass: {success}")
    return 1 if failures or skipped else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-hook", action="store_true", help="verify and directly run the shipped pre-push hook")
    mode.add_argument("--guard-only", action="store_true", help="run original guard fixtures without hook execution tests")
    parser.add_argument("--repo", default=".", help="repository to check (check mode only)")
    parser.add_argument("--remote", default="origin", help="push remote name (check mode only)")
    parser.add_argument("--timeout", type=float, default=HOOK_TIMEOUT, help="hook time limit in seconds (check mode only)")
    args = parser.parse_args()
    if args.check_hook:
        result = check_hook(args.repo, remote=args.remote, timeout=args.timeout)
        print(json.dumps(result, sort_keys=True))
        return HOOK_EXIT[result["status"]]
    # Fixtures must not inherit a live hook directory, repository override, or injected Git configuration.
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    with patch.dict(os.environ, environment, clear=True):
        return fixture_selftest(guard_only=args.guard_only)


if __name__ == "__main__":
    sys.exit(main())
