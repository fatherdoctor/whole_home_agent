# Push guard

*Status: template (O4, 2026-10-14; more shapes, photo location and the shrink list KIT-SAFE, 2026-11-01; fewer false
refusals, token values and long lines KIT-SAFE.f, 2026-11-02; YAML blocks, binary and UTF-16 files, escapes, photos
by their bytes and names in paths KIT-XR-GUARD.f, 2026-11-11).
`principles/working-with-the-agent.md` rule 9; a backlog item the Phase 1 generation adds (1 point).*

`push_guard.py` refuses a push whose new lines or paths look like a secret: a token (Home Assistant, GitHub, an
`sk-` API key, an AWS key id, a bearer or Basic authorization value, a long hex string), a password, token or API
key written as a value (in YAML, JSON, a URL or a sentence), a door code or PIN written as digits after the word, a private key, a phone number, `secrets.yaml`,
`.storage/`, the recorder database, a git or agent credentials file, a backup archive or the backup emergency kit;
a photo whose EXIF still holds GPS coordinates; and, with a shrink list, a listed file cut under half. Exit 0 is
clean, 1 is refused, 2 is an error. Standard library only; any agent runtime can call it. It prints the file, line
and kind of each finding, never the matched text.

The guard is the owner's default, not a lock: they may relax a rule, drop a check or uninstall it. The agent says
once what it protects against, does what they chose, and records it in the CHANGELOG with the undo and in
`adoption.opted_out` or the rail's own setting (`AGENTS.md`, "The kit serves the owner").

## Install (once per clone of the house repository)
Use Git 2.31 or newer for the hook check. Run the check from the same place you push from, including the same terminal or editor.
The installed location is **`guard/` at the repository root**. Before the first push, ask the owner to fill the
ignored names list privately, or say plainly: **the household names check is off; the other guard checks still
run**. Never ask for those names in chat. If first names are listed, the profile and every other committed file
use roles such as `Owner`, `Adult 2` and `Guest`. Do not commit an already-filled profile until it follows that rule.

```sh
mkdir -p guard
cp <kit>/templates/guard/push_guard.py <kit>/templates/guard/selftest.py <kit>/templates/guard/names.example.txt guard/
echo /guard/names.txt >> .gitignore
kit_hook=$(git rev-parse --git-path hooks/pre-push)
mkdir -p "$(dirname "$kit_hook")"
# Refuse to replace an existing hook; integrate it deliberately instead.
(set -C; cat > "$kit_hook" <<'HOOK'
#!/bin/sh
exec python3 guard/push_guard.py --repo . --remote "$1" --pushed-refs
HOOK
) && chmod +x "$kit_hook"
```
If an existing hook prevented installation, stop and review how to retain its checks; do not overwrite it.
`git rev-parse` finds the effective hooks directory, including `core.hooksPath` and linked worktrees.
`exec` hands the guard's exit status to git, which aborts the push on anything but 0. `--pushed-refs` makes the guard
read what the push sends: git gives the hook one line per ref on standard input, and the guard scans each one: a
branch that is not checked out, a tag, and every ref of `git push --all` or `--tags`. It also reads the message of
each new commit and of each annotated tag the push sends, even a tag on a commit the remote already has. The whole
message is read, a signed tag's signature block included, and so is the message of a signed tag that a merge copies
into its commit. The name of each branch and tag the push sends is scanned too. A chain of more than 20 tags (a tag of a tag, and so on) is refused, because the guard reads no further. A ref being
deleted sends nothing. A hook without `--pushed-refs` (installed before this change) scans only the checked-out branch; replace
it, and the hook check below refuses it until you do. `--remote "$1"` names the
remote being pushed to, so a commit that only another remote holds is still scanned on its way to this one; a remote with
no name (a path or URL, spaces allowed) has nothing pushed yet, so the whole history is read. Files are read under their
real names, accents, quotes and spaces included.

**A hook file is not proof that it runs.** After installing it, run:
```sh
python3 guard/selftest.py --check-hook --repo . --remote origin
```
Exit **0** means Git's chosen hook runs and the guard answered. The check also pushes, in a scratch repository and
through the same hook and guard, a planted secret on another branch, on a tag, with `--all` and with `--tags`; each
must be refused and a clean branch sent. Nothing in your repository is pushed. The checker accepts the two-line hook shown
above. If you already have a different hook, keep it and review how to add the guard without losing its checks.
A missing hook, missing execute permission or missing interpreter means installation is unfinished. Repair it.
If the guard refuses a commit, errors or takes too long, fix the cause before pushing. Never bypass a refusal.
Exit **2** means this computer denied execution after the basic permission checks. Diagnose that restriction
before choosing the by-hand route below. The checker does not print the hook's output.

Also run `python3 guard/selftest.py --guard-only`. It plants fake secrets and private photo metadata in temporary
repositories, checks that the guard blocks them, and checks that clean commits pass. Exit 0 means these checks
passed. Both this check and the installed-hook check must pass for an automatic hook.
The default `python3 guard/selftest.py` also tests hook handling in temporary repositories. On a computer that
cannot run hook files, it says the computer or sandbox denied execution and counts those cases as skipped. Its exit stays 1.

### When this runtime cannot execute hooks
Use this route only after diagnosing an execution restriction. A broken installation or refused commit needs
repair instead. Write this line in the CHANGELOG, replacing the reason with what was diagnosed:

`L1-guard: method=manual; reason=<diagnosed restriction>`

Push through the guard, not after it. With `--push`, the guard checks exactly what that push sends and then
pushes it, only when the check is clean:
```sh
python3 guard/push_guard.py --repo . --push origin <branch>
```
Replace `<branch>` with the branch or tag you push. It need not be the branch you have checked out. To push
several refs, name each one: `--push origin main v1.0`. For a different name on the remote, write
`<local>:<remote name>`. A leading `+` forces that ref, as in `git push`. The guard does not take `--all` or
`--tags`: name the refs. It pushes the commits it checked by their ids, so a commit made after the check is not
sent. It also turns off `push.followTags` and `push.recurseSubmodules` for that push, so a Git setting cannot add a
tag or another repository the guard did not read. Exit 0 means checked and pushed, 1 means refused and nothing pushed, 2 means an error.
Do not run the guard and then a separate `git push`: that push can send a branch the guard did not read.
Also require `python3 guard/selftest.py --guard-only` exit 0.
Write the guard's result with each push. The helper reports **manual**, not a passing automatic hook, when it
finds the recorded reason, the execution restriction and passing planted-item checks. A record alone does not
bypass a broken hook. With `--no-selftest`, the helper leaves protection unknown. Check again when you change
computer, terminal or editor.

## Limits: what the guard does not catch
The guard looks for known shapes. It is a net for mistakes, not proof that a push is safe. It does not catch:
- a secret under a key that does not name one (`note: <value>`), unless the value has a known token shape (a JWT,
  `ghp_`, `sk-`, an AWS key id, 40 or more hex characters);
- a password or code written in plain words, or split across lines or files, or a list of values under a secret key
  (`wifi_passwords:` and `- <value>` on the lines below);
- a copy of `secrets.yaml` with another word in front of the name (`house_secrets.yaml`, `Kopie von secrets.yaml`);
  its lines are still scanned. The guard knows the copies that tools and editors make
  (`Copy of`, `old_`, `backup-`, `#...#`) and the names in the next section;
- a value encoded so that it no longer looks like itself (base64, hex of text, a compressed or encrypted file);
- a name that is not on the names list, a nickname, or a name in another spelling;
- the author, committer and tagger names and e-mail addresses on each commit and tag (set them before the first
  commit); a branch or tag name is scanned, with the shapes and the names list, but a ref being deleted is not;
- a file the guard cannot read as text and that is listed in `binary.txt`;
- a value on the line after its key in a form that formatters do not write: a JSON key that is not first on its
  line (`{"wifi_password":` and the value below), a JSON colon on the next line, a YAML complex key
  (`? wifi_password` and `: <value>` below); and any value on the line after its key outside a `.yaml`, `.yml` or
  `.json` file (a YAML example in a Markdown code block);
- a commit header field other than `mergetag` (git writes no other field that holds text, but a hand-made commit
  can carry one);
- a push that does not run it: `git push --no-verify`, a computer that does not run the hook, or a tool that
  pushes without git.
Keep secrets out of the repository in the first place: in `secrets.yaml` (never committed) and `!secret` references.

## What it lets through on purpose
- A full commit id inside a GitHub `/commit/`, `/blob/` or `/tree/` link, a GitHub Actions step pinned as
  `uses: owner/repo@<commit>`, a 40-character commit id under a key that names it (`commit`, `export`, `ref`,
  `sha`: `"repo_commit": "..."`), and a 64-character digest under `sha256`, `checksum`, `digest` or `hash`: only
  that value is masked; the rest of the line is still scanned. A commit id or checksum anywhere else (in a
  sentence, under another key) is refused; mark it `guard: allow commit id`.
- The commit a submodule points at: a submodule entry is not a file, so its `Subproject commit <id>` line is not
  read. The same line written in a text file is read like any other.
- A template of a secret file with placeholders, whose name ends in `example`, `sample`, `template`, `dist` or
  `defaults`: `.env.example`, `.env.dist`, `secrets.yaml.sample`, `secrets.example.yaml`. Its lines are scanned
  like any other file's. A template word can follow `.`, `_` or `-`: `.env-example` and `.env_sample` are
  templates too. Every other file whose name starts with `secrets` and has `.yaml` or `.yml` in it is a forbidden
  path (`secrets.yaml.bak`, `secrets copy.yaml`, `secrets (1).yaml`, `secrets-backup.yaml`, `secrets.yml`,
  `.secrets.yaml.swp`), and so is a copy named in front (`Copy of secrets.yaml`, `old_secrets.yaml`,
  `#secrets.yaml#`) and `.env` followed by `.`, `_`, `-`, `~` or a space (`.env.local`, `.env_local`, `.env copy`).
  A file of your own with such a name, such as a workflow `secrets-scan.yml`, is refused too: rename it, for example
  to `secret-scan.yml`. The guard has no way to allow a forbidden path.
- A password named by its key or by `!secret`, any other YAML tag (`!lambda`, `!include`), a template
  (`{{ ... }}`), an environment variable (`$VAR`, `${VAR}`), a `<placeholder>` (also as a URL's password); a number
  that is part of a date, a version or a decimal.
- Code and configuration that only look like a key and a value: an ESPHome pin (`interrupt_pin: GPIO4`), a
  variable set from a call or an index (`code = m.group(1)`, `token = os.environ["HA_TOKEN"]`), a name set to a
  name (`has_pin = PIN_SUBMIT`, `"code": code`), and a word after `password:` in a sentence. A bare `code`, `pin`
  or `token` key counts as a value only when it is quoted or four to eight digits; an unquoted `password` value
  in the middle of a line, or a `KEY = value` without quotes, only when it holds a digit.
- A bare number with no word in front of it, including ten digits in a row (a datestamp such as `2026110200`, a
  model or firmware number): ten bare digits are a phone number only after a word such as `call`, `phone`, `text`,
  `cell` or `number`. The guard cannot tell a door code from a quantity; the rule against writing codes down is
  what covers it.

## What it refuses that you might not expect
- Four to eight digits after the word `code` or `PIN`, in prose too: a zip code, an error code or a year written
  as digits right after the word "code". A zip code is the house's location, so that refusal is wanted; an error
  code or a year written that way gets `guard: allow error code` on its line.
- A business's phone number written with separators (a plumber, the gas company). Put it on the line with
  `guard: allow business number`.
- A line longer than 4,000 characters (a minified script, a base64 blob) is scanned in overlapping pieces, so a
  long line costs time in proportion to its length and nothing past the first 4,000 characters is skipped; the
  guard says on stderr how many it read that way.

## Photos
A JPEG, PNG, TIFF, HEIC or WebP is refused when its EXIF block holds GPS latitude or longitude (phones add them by
default; `principles/house-records-and-equipment.md` rule 9). Strip the metadata and commit again; on most systems
an export or "save for web" without metadata does it, or `exiftool -all= <file>` where it is installed. A photo
taken with location off (a GPS block with no coordinates) passes.

## Files git calls binary
Git shows no lines for a binary file, so the guard reads its bytes. A UTF-16 or UTF-32 file (a Windows redirect writes
one) and a text file that a `.gitattributes` `-diff` hides are decoded and their new lines scanned like any other. A
photo is known by its bytes, so renaming `photo.jpg` to `photo.dat` does not skip the location check. Fonts, GIFs,
icons and Python bytecode pass. Anything else the guard cannot read (a zip, a PDF, a firmware image, which can hold a
Wi-Fi password) is refused, because the guard cannot say it is clean. Look inside it yourself, then put its path on
`guard/binary.txt` (one repository path per line, comments as in `names.txt`; `--binary PATH` points at another
file); the list can be committed. A photo on the list still gets the location check.

## Shrink list (level 6)
`guard/shrink.txt` names the shared files that must never be wiped by accident: one repository path per line,
comments as in `names.txt` (for example `house/docs/board.md`, `house/docs/card-names.tsv`,
`house/docs/CHANGELOG.md`). A push that ends with one of them under half its line count at the start of the push,
when it had 20 lines or more, or deletes it, is refused: that is the trace of a truncating write. With no file the
check is off. The list can be committed (it holds paths, not secrets). For a deliberate cut, comment the line out
for that one push and say why in the CHANGELOG. `--shrink PATH` points at another file.

## Household names
`guard/names.txt` holds the words that must never leave the house repository: the people's names and nicknames, the
street, the town. One per line; blank lines, lines starting with `#` and anything after a ` #` (a `#` that follows
whitespace) are comments, so a name cannot contain ` #`; a match is a whole word, case-insensitive (`Sam` does not
match `Samuel`, so list both when you need both). The guard reads the file next to itself, or the path given by
`--names`; with no file it says so on stderr and skips the check. A listed word is refused in a file's path too
(`docs/<name>.md`), and in a line that writes it with escapes (`Zo\u00eb`, as `json.dumps` writes an accented name). The file `--names` points at is never scanned, so it
can name the very words it forbids. That also means nothing stops you committing it, so the install git-ignores it and
each clone fills in its own. Ask before the first push, even if Phase 1 has not started; the owner fills it
privately, or the agent reports that the household names check is off. The example words are not evidence that
the real names are protected. When writing `house/profile.yaml` and other committed text, use roles once first
names are listed; keep the name-to-role mapping in the private list or the owner's private notes. Revisit it
whenever someone joins the household. A deliberate mention carries
`guard: allow <reason>`.

## Rules
- The verdict is the exit status. A wrapper that prints ABORT and carries on is not a guard.
- A false positive gets `guard: allow <reason>` at the end of that line, never a weaker pattern.
- A hook lives in Git's effective hooks directory and is not part of the installed `guard/` source files: every
  new clone installs and execution-checks it again. A runtime that cannot execute hooks uses the explicit guarded
  push above and records the manual method; a file-existence check does not replace that evidence.
- The guard catches shapes and the words on `names.txt`, not meaning. A name nobody listed still passes, and so does
  an address in a form the list does not spell; the repository rules (`AGENTS.md`, "Secrets never in the repository") still apply.
