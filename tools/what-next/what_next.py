#!/usr/bin/env python3
"""what_next.py - gather the facts the "what next?" helper needs, for levels 0-2. Facts only: it never suggests.

Status: early slice (KIT-NEXT0, 2026-10-26), levels 0-2 only; the full helper (levels 3-7, the side tracks, the
health and usage inputs) is KIT-NEXT. The prompt that reads this output is `WHAT-NEXT.md` in this folder; the
readiness tests it runs are `00-start-here/levels.md`. Standard library only (PyYAML is used when installed).

Run from the root of the house repository:
    python3 tools/what-next/what_next.py [--root DIR] [--today YYYY-MM-DD] [--no-network] [--no-selftest] [--json]

It reads files and runs three local commands: `git` (remote, hook, ignore rules, a dry-run push that sends
nothing), `python3 guard/selftest.py` (the level-1 guard test, in a scratch repository) and
`python3 templates/docs/board_check.py house/docs/board.md`. It never writes a file, never touches the box and
never sends anything to a person. `--no-network` skips the dry-run push, `--no-selftest` the guard selftest; the
checks they feed then read "unknown".

Output: a table for the person, then one JSON block between the lines `--- facts (json) ---` and `--- end ---`.
Every check is {id, level, kind, result, evidence}: kind is auto | ask | once; result is pass | fail | unknown | manual for
auto checks, ask for an ask check, and pass (with the date) or ask for a once check. Anything the script cannot
read is "unknown" and says why; a gap is never filled.

A house adopted on path C (`setup.existing_house: true`, KIT-EXIST.d) also gets level 0's five `E0` lines
(levels.md): `E0-backup-first` (ask, once), `E0-inventory`, `E0-first-look`, `E0-untouched` (the definitions-only
diff of `export_house.py --diff`, loaded from house/export/ or templates/export/) and `E0-differs-written`; and the
`tidy_up` facts (the backlog's tidy-up section, which no check counts and the helper never suggests on its own).

Exit 0 = facts gathered (whatever they say); 2 = not run from a house repository (no AGENTS.md and no house/).
"""
import argparse
import datetime
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

LEVELS = (0, 1, 2)  # this slice; levels 3+ are reported as not checked
SEED_CODES = ("PORCH-1", "ROUTER-1", "HEALTH-1", "DRILL-1", "MANUAL-1")  # templates/docs/board.md's sample rows
REQUIRED_TOPICS = ("people", "areas", "devices", "priorities", "agent")  # topics 1-4 and 8 (levels.md, level 1)
PACE_DAYS = {"weekly": 7, "biweekly": 14, "monthly": 30}
SKIP_DAYS = 60
IN_PROGRESS_DAYS = 7
BUSY_ROWS = 3
TIMEOUT = 60
# The `once` checks of levels 0-2 and their keys in adoption.once_done (levels.md, "For the helper").
ONCE = {"L0-backup-proven": 0, "E0-backup-first": 0}
ASKS = {
    "L0-done-when": (0, "Every line of the 'Done when' list in install/network-and-backups-first.md is checked, "
                        "from the box's screen."),
    "L0-backup-week": (0, "A backup from the last seven days is listed at the off-box location."),
    "L0-backup-proven": (0, "The backup has been proven usable: one downloaded and opened, or a restore rehearsed on a "
                             "spare drive, board or VM (once; record the date)."),
    "E0-backup-first": (0, "One backup was downloaded off the box (to a phone or a computer) before the inventory ran "
                           "(once; record the date; opening it is L0-backup-proven's job, which this line does not "
                           "stand in for)."),
    "L1-private": (1, "Only the household can read the repository (a private host repository, or a bare repository "
                      "on a computer you own)."),
    "L1-secrets-undo": (1, "You can say, without looking, where your secrets live and how you would undo your most "
                           "recent change."),
    "L2-own-row": (2, "You have written one board row yourself and sized it."),
    "L2-statuses": (2, "You can say what each status means and who moves a row out of READY FOR REVIEW."),
}
# Path C only (setup.existing_house: true; levels.md level 0 and "An existing house").
EXISTING_ONLY = {"E0-backup-first"}
# The twelve inventory files: the five every house has and the seven of path C (export_house.py).
INVENTORY_FILES = ("entities.json", "areas.json", "integrations.json", "automations.json", "meta.json",
                   "scripts_scenes.json", "helpers.json", "dashboards.json", "addons.json", "backups.json",
                   "users.json", "blueprints.json")
# first-look.md's lines E0-first-look needs: the backup, login and secrets checks (first_look.py CHECKS 4, 5, 10).
FIRST_LOOK_LINES = {4: "backup", 5: "login", 10: "secrets"}
FIRST_LOOK_RESULTS = ("finding(s)", "nothing found", "unknown", "a question")
# An optional list number is tolerated: generated-files.md lists the page's sections as "7. Where this house differs".
DIFFERS_RE = re.compile(r"^#{2,4}\s+(?:\d+\.\s+)?Where this house differs", re.I)
TIDY_RE = re.compile(r"^##\s+Tidy-up\b", re.I)
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
ENTRY_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\b(.*)$")
IN_PROGRESS_RE = re.compile(r"^IN PROGRESS \S+ (\d{4}-\d{2}-\d{2})")


# ---------------------------------------------------------------- reading YAML without PyYAML

def _scalar(text):
    t = text.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    if t.startswith("{") and t.endswith("}"):
        out = {}
        for part in _split_flow(t[1:-1]):
            if ":" in part:
                k, v = part.split(":", 1)
                out[k.strip()] = _scalar(v)
        return out
    if t.startswith("[") and t.endswith("]"):
        return [_scalar(x) for x in _split_flow(t[1:-1])]
    low = t.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    return t


def _split_flow(text):
    parts, depth, cur, quote = [], 0, "", None
    for ch in text:
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'" and not cur.strip():
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
            continue
        cur += ch
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def _strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'" and (i == 0 or line[i - 1] in " :[{,-"):
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def mini_yaml(text):
    """Block mappings, block lists of scalars, flow maps or small mappings, and flow scalars: the profile
    template's shapes. Enough to read the keys this script needs; not a YAML parser."""
    lines = []
    for raw in text.splitlines():
        line = _strip_comment(raw)
        if line.strip() and not line.lstrip().startswith("---"):
            lines.append((len(line) - len(line.lstrip()), line.strip()))

    def block(i, indent):
        if i < len(lines) and lines[i][1].startswith("- "):
            out = []
            while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                body = lines[i][1][2:].strip()
                if re.match(r"^[A-Za-z_][\w-]*:(\s|$)", body):
                    k, v = body.split(":", 1)
                    item = {k.strip(): _scalar(v) if v.strip() else None}
                    i += 1
                    if i < len(lines) and lines[i][0] > indent:
                        more, i = block(i, lines[i][0])
                        if isinstance(more, dict):
                            item.update(more)
                    out.append(item)
                else:
                    out.append(_scalar(body))
                    i += 1
            return out, i
        out = {}
        while i < len(lines) and lines[i][0] == indent:
            key, _, rest = lines[i][1].partition(":")
            i += 1
            if rest.strip():
                out[key.strip()] = _scalar(rest)
            elif i < len(lines) and (lines[i][0] > indent or (lines[i][0] == indent and lines[i][1].startswith("- "))):
                out[key.strip()], i = block(i, lines[i][0])
            else:
                out[key.strip()] = None
        return out, i

    if not lines:
        return {}
    data, _ = block(0, lines[0][0])
    return data


def load_yaml(path):
    """(data, how) - data is None when the file is missing or unreadable; how says which reader or why not."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "missing"
    except OSError as e:
        return None, f"unreadable ({type(e).__name__})"
    try:
        import yaml  # noqa: PLC0415
        data = yaml.safe_load(text)
        how = "pyyaml"
    except ImportError:
        data, how = mini_yaml(text), "built-in reader"
    except Exception as e:  # noqa: BLE001
        return None, f"not valid YAML ({type(e).__name__})"
    return (data if isinstance(data, dict) else {}), how


def get(data, dotted):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def on_date(entry):
    """The `on:` date of a skipped or once_done entry. PyYAML reads a bare `on` key as the boolean True (YAML 1.1),
    so both keys are tried."""
    return to_date(entry.get("on", entry.get(True)))


def to_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    m = DATE_RE.search(str(value or ""))
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None


# ---------------------------------------------------------------- documents

def _read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _absent(path):
    """(result, words) for a file that could not be read: `fail` when it simply does not exist yet (the level
    itself writes it), `unknown` when it exists but cannot be read (levels.md, "Missing gives")."""
    if not path.exists():
        return "fail", "missing"
    return "unknown", "unreadable"


def _absent_how(how):
    """The same split for load_yaml's `how`: missing -> fail; unreadable or not valid YAML -> unknown."""
    return "fail" if how == "missing" else "unknown"


def _no_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def changelog_entries(text):
    """[(date, title, body)] for every dated `## YYYY-MM-DD ...` entry outside HTML comments, newest first."""
    out, cur = [], None
    for line in _no_comments(text).splitlines():
        m = ENTRY_RE.match(line)
        if m:
            cur = [to_date(m.group(1)), m.group(2).strip(" -"), []]
            out.append(cur)
        elif line.startswith("## "):
            cur = None
        elif cur is not None:
            cur[2].append(line)
    return [(d, t, "\n".join(b)) for d, t, b in out if d]


def has_undo(body):
    m = re.search(r"\*\*Undo:\*\*\s*(.*)", body)
    return bool(m and m.group(1).strip() and not m.group(1).strip().startswith("<"))


def gotcha_entries(text):
    """The `### ` headings whose block carries an `- **Incident:** <real date>` line (the shape
    templates/docs/gotchas.md defines). The template's area headings and its sample entry are not entries."""
    out, cur = [], None
    for line in _no_comments(text).splitlines():
        if line.startswith("#"):
            cur = line[4:].strip() if line.startswith("### ") and not line[4:].lstrip().startswith("<") else None
        elif cur is not None and re.match(r"\s*- \*\*Incident:\*\*", line) and to_date(line):
            out.append(cur)
            cur = None
    return out


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(cmd, root, timeout=TIMEOUT):
    """A finished process; one that hangs past the timeout comes back with returncode None, so the caller reports
    `unknown` instead of a traceback."""
    try:
        return subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, None, "", f"timed out after {timeout} s")


# ---------------------------------------------------------------- the checks

def check(cid, level, kind, result, evidence):
    return {"id": cid, "level": level, "kind": kind, "result": result, "evidence": evidence}


def level0(root, profile, how):
    out = []
    if profile is None:
        out.append(check("L0-profile", 0, "auto", _absent_how(how), f"house/profile.yaml {how}"))
    else:
        done, on = get(profile, "setup.done"), get(profile, "setup.installed_on")
        ok = done is True and to_date(on) is not None
        out.append(check("L0-profile", 0, "auto", "pass" if ok else "fail",
                         f"setup.done={done!r}, setup.installed_on={on!r} ({how})"))
    text = _read(root / "house/docs/CHANGELOG.md")
    if text is None:
        res, words = _absent(root / "house/docs/CHANGELOG.md")
        out.append(check("L0-changelog-first", 0, "auto", res, f"house/docs/CHANGELOG.md {words}"))
    else:
        hit = [e for e in changelog_entries(text) if re.search(r"home assistant installed", e[1], re.I)]
        out.append(check("L0-changelog-first", 0, "auto", "pass" if hit else "fail",
                         f"entry {hit[-1][0]} '{hit[-1][1]}'" if hit else
                         "no dated entry titled 'Home Assistant installed (Phase 0)'"))
    return out


def level1(root, profile, how, network, selftest, probe_git):
    out = []
    # The remote and a push that would succeed (privacy is the ask L1-private: no file says it).
    if not network:
        out.append(check("L1-remote", 1, "auto", "unknown", "dry-run push skipped (--no-network)"))
    elif probe_git is None:
        out.append(check("L1-remote", 1, "auto", "unknown", "templates/runtime/probe_runtime.py missing"))
    else:
        value, why = probe_git(root)
        # The network or git itself failed: the push is not proven broken, only unread.
        unread = re.search(r"remote not reachable|timed out|git failed", why)
        out.append(check("L1-remote", 1, "auto", "pass" if value == "yes" else ("unknown" if unread else "fail"), why))
    # Both the installed hook and the planted-item checks must prove protection.
    manual = re.search(r"(?m)^\s*(?:[-*]\s*)?(?:\*\*)?L1-guard: method=manual; reason=([^\n*]+)",
                       _read(root / "house/docs/CHANGELOG.md") or "")
    method, result, evidence = "unverified", "unknown", "guard checks skipped (--no-selftest)"
    checker = root / "guard/selftest.py"
    if selftest:
        if not checker.is_file():
            result, evidence = "fail", "guard/selftest.py missing"
        else:
            r = run([sys.executable, "guard/selftest.py", "--check-hook", "--repo", ".", "--remote", "origin"], root)
            try:
                data = json.loads(r.stdout)
            except (ValueError, TypeError):
                data = None
            good = isinstance(data, dict)
            hook_pass = good and r.returncode == 0 and data == {
                "status": "pass", "method": "hook", "reason": "hook_exit_0"}
            denied = good and r.returncode == 2 and data == {
                "status": "unavailable", "method": "unverified", "reason": "hook_execution_denied"}
            if hook_pass or (denied and manual):
                planted = run([sys.executable, "guard/selftest.py", "--guard-only"], root)
                if planted.returncode == 0:
                    method = "hook" if hook_pass else "manual"
                    result = "pass" if hook_pass else "manual"
                    evidence = ("hook runs; planted-item checks exit 0" if hook_pass else
                                "guard run by hand recorded; hook execution denied; planted-item checks exit 0; "
                                "confirm the guard before every push")
                else:
                    result = "unknown" if planted.returncode is None else "fail"
                    evidence = "planted-item checks did not pass"
            elif denied:
                evidence = "hook execution denied; diagnose this runtime before recording a manual method"
            elif r.returncode is None or not good:
                evidence = "hook checker timed out or returned no verified result"
            else:
                result = "fail"
                known_reasons = {
                    "invalid_timeout", "repository_lookup_failed", "hook_lookup_failed", "hook_missing_or_not_file",
                    "hook_execute_bits_missing", "hook_access_denied", "hook_wiring_unverified", "guard_target_missing",
                    "remote_lookup_failed", "hook_exec_format", "hook_start_failed", "hook_refused", "hook_error",
                    "hook_timed_out",
                }
                reason = data.get("reason")
                evidence = "hook check did not pass; repair installation or resolve the refusal"
                if isinstance(reason, str) and reason in known_reasons:
                    evidence += "; " + reason
    guard_check = check("L1-guard", 1, "auto", result, evidence)
    guard_check["method"] = method
    out.append(guard_check)
    # The names list and the ignore rules.
    names = _read(root / "guard/names.txt")
    count = len([l for l in (names or "").splitlines() if l.strip() and not l.lstrip().startswith("#")])

    faults, unread = [], []
    if not count:
        faults.append("guard/names.txt " + ("has no names" if names is not None else "missing"))
    for p in ("guard/names.txt", "secrets.yaml", "ha/secrets.yaml"):
        # The ignore rules alone are not enough: a file committed before its rule stays tracked and keeps pushing.
        ign = run(["git", "check-ignore", "-q", "--no-index", p], root)
        tracked = run(["git", "ls-files", "--", p], root)
        if ign.returncode is None or tracked.returncode is None:
            unread.append(f"{p}: git timed out")
        elif tracked.stdout.strip():
            faults.append(f"{p} tracked by git (git rm --cached {p})")
        elif ign.returncode != 0:
            faults.append(f"{p} not ignored by git")
    out.append(check("L1-ignored", 1, "auto", "fail" if faults else ("unknown" if unread else "pass"),
                     "; ".join(faults + unread) or f"{count} name(s); names list and secrets.yaml ignored, not tracked"))
    # The profile topics.
    if profile is None:
        out.append(check("L1-topics", 1, "auto", _absent_how(how), f"house/profile.yaml {how}"))
    else:
        topics = get(profile, "profile.topics") or {}
        missing = [t for t in REQUIRED_TOPICS if (topics.get(t) if isinstance(topics, dict) else None) != "done"]
        ok = get(profile, "profile.done") is True or not missing
        out.append(check("L1-topics", 1, "auto", "pass" if ok else "fail",
                         "profile.done" if get(profile, "profile.done") is True else
                         ("topics 1-4 and 8 done" if ok else "not done: " + ", ".join(missing))))
    # Three changes with their undo, one gotcha.
    text = _read(root / "house/docs/CHANGELOG.md")
    entries = changelog_entries(text) if text else []
    undone = [e for e in entries if has_undo(e[2])]
    if text is None:
        res, words = _absent(root / "house/docs/CHANGELOG.md")
        out.append(check("L1-changelog-3", 1, "auto", res, f"house/docs/CHANGELOG.md {words}"))
    else:
        out.append(check("L1-changelog-3", 1, "auto", "pass" if len(undone) >= 3 else "fail",
                         f"{len(entries)} dated entries, {len(undone)} with an undo line"))
    g = _read(root / "house/docs/gotchas.md")
    if g is None:
        res, words = _absent(root / "house/docs/gotchas.md")
        out.append(check("L1-gotchas", 1, "auto", res, f"house/docs/gotchas.md {words}"))
    else:
        n = len(gotcha_entries(g))
        out.append(check("L1-gotchas", 1, "auto", "pass" if n else "fail",
                         f"{n} entr{'y' if n == 1 else 'ies'} with a dated Incident line"))
    return out


def level2(root, today, board_mod):
    out = []
    path = root / "house/docs/board.md"
    text = _read(path)
    board = board_mod.parse_board(text) if (text is not None and board_mod) else None
    board_absent = _absent(path) if text is None else None
    if text is None:
        out.append(check("L2-board", 2, "auto", board_absent[0], f"house/docs/board.md {board_absent[1]}"))
    elif not (root / "templates/docs/board_check.py").exists():
        out.append(check("L2-board", 2, "auto", "unknown", "templates/docs/board_check.py missing"))
    else:
        r = run([sys.executable, "templates/docs/board_check.py", "house/docs/board.md"], root)
        last = (r.stdout.strip().splitlines() or [""])[0]
        seed = [c for c in SEED_CODES if board and c in {i["code"] for i in board["items"]}]
        res = "unknown" if r.returncode is None else ("pass" if r.returncode == 0 and not seed else "fail")
        out.append(check("L2-board", 2, "auto", res, f"board_check exit {r.returncode}: {last}"
                         + (f"; template seed rows still on the board: {', '.join(seed)}" if seed else "")))
    b = _read(root / "house/docs/backlog.md")
    if b is None:
        res, words = _absent(root / "house/docs/backlog.md")
        out.append(check("L2-backlog-moved", 2, "auto", res, f"house/docs/backlog.md {words}"))
    else:
        top = "\n".join(_no_comments(b).splitlines()[:8])
        says = re.search(r"board", top, re.I) is not None
        # The tidy-up section (path C) is optional old work: no readiness test counts its rows (backlog.md, Tidy-up).
        items = [l for l in _without_section(_no_comments(b), TIDY_RE).splitlines() if l.startswith("### ")]
        out.append(check("L2-backlog-moved", 2, "auto", "pass" if says and not items else "fail",
                         ("top names the board" if says else "top does not say the items moved to the board")
                         + f"; {len(items)} item heading(s) left"))
    if board is None:
        for cid in ("L2-done-3", "L2-runlog-3", "L2-in-progress-age"):
            out.append(check(cid, 2, "auto", board_absent[0] if text is None else "unknown",
                             f"house/docs/board.md {board_absent[1]}" if text is None else "board_check.py missing"))
        return out, None
    # Only the dated entries count, titles and bodies: not a comment or a stray paragraph.
    log = "\n".join(f"{t}\n{b}" for _d, t, b in changelog_entries(_read(root / "house/docs/CHANGELOG.md") or ""))
    done = [i["code"] for i in board["items"] if i["word"] == "DONE"]
    logged = [c for c in done if re.search(rf"(?<![\w.-]){re.escape(c)}(?![\w-]|\.\w)", log)]
    out.append(check("L2-done-3", 2, "auto", "pass" if len(logged) >= 3 else "fail",
                     f"{len(done)} DONE, {len(logged)} named in the CHANGELOG"
                     + (f" ({', '.join(logged[:5])})" if logged else "")))
    runs = [r for r in board["runlog"] if not r.get("skipped")]
    out.append(check("L2-runlog-3", 2, "auto", "pass" if len(runs) >= 3 else "fail",
                     f"{len(runs)} run-log line(s) with est / actual"))
    old, dateless = [], []
    for i in board["items"]:
        if i["word"] != "IN PROGRESS":
            continue
        m = IN_PROGRESS_RE.match(i["status"])
        d = to_date(m.group(1)) if m else None
        if d is None:
            dateless.append(i["code"])  # the git-history read is KIT-NEXT's
        elif (today - d).days > IN_PROGRESS_DAYS:
            old.append(f"{i['code']} since {d}")
    if old:
        res, why = "fail", "; ".join(old)
    elif dateless:
        res, why = "unknown", "IN PROGRESS with no date: " + ", ".join(dateless)
    else:
        res, why = "pass", f"no row IN PROGRESS over {IN_PROGRESS_DAYS} days"
    out.append(check("L2-in-progress-age", 2, "auto", res, why))
    return out, board


def _section(text, heading_re):
    """The lines under the first heading heading_re matches, up to the next heading of the same or a higher level;
    None when there is no such heading."""
    lines, out, depth = text.splitlines(), None, 0
    for line in lines:
        m = re.match(r"^(#+)\s", line)
        if out is None:
            if heading_re.match(line):
                out, depth = [], len(m.group(1)) if m else 2
        elif m and len(m.group(1)) <= depth:
            break
        else:
            out.append(line)
    return out


def _without_section(text, heading_re):
    body = _section(text, heading_re)
    if body is None:
        return text
    lines, out, skip, depth = text.splitlines(), [], False, 0
    for line in lines:
        m = re.match(r"^(#+)\s", line)
        if not skip and heading_re.match(line):
            skip, depth = True, len(m.group(1)) if m else 2
            continue
        if skip and m and len(m.group(1)) <= depth:
            skip = False
        if not skip:
            out.append(line)
    return "\n".join(out)


def _table_rows(lines):
    """Data rows of the markdown tables in lines: not the header (the line before a |---| line) nor the rule."""
    rows = [l.strip() for l in lines if l.strip().startswith("|")]
    rule = [i for i, l in enumerate(rows) if re.fullmatch(r"\|[\s:|-]+\|", l)]
    headers = {i - 1 for i in rule}
    return [l for i, l in enumerate(rows) if i not in rule and i not in headers]


def _git_date(root, rel):
    """The last commit date of a file, else its modification date; None when neither can be read. A file with
    uncommitted changes (git status lists it) is dated by its modification date: its last edit is not committed yet."""
    st = run(["git", "status", "--porcelain", "--", rel], root)
    dirty = st.returncode == 0 and bool(st.stdout.strip())
    r = None if dirty else run(["git", "log", "-1", "--format=%cs", "--", rel], root)
    d = to_date(r.stdout) if r is not None and r.returncode == 0 else None
    if d is None and (root / rel).exists():
        d = datetime.date.fromtimestamp((root / rel).stat().st_mtime)
    return d


def _diff_module(root):
    for rel in ("house/export/export_house.py", "templates/export/export_house.py"):
        if (root / rel).exists():
            try:
                mod = load_module(root / rel, "export_house")
            except Exception:  # noqa: BLE001 - a broken copy is unreadable, not a pass
                continue
            if hasattr(mod, "diff"):
                return mod, rel
    return None, None


def existing_house(root, profile, today):
    """Level 0's four `auto` E0 lines (levels.md), for a house with setup.existing_house: true. E0-backup-first is
    an ask (asks())."""
    out = []
    export, docs = root / "house/export", root / "house/docs"
    # E0-inventory: the twelve files, inventory.md, setup.inventoried_on; stale is said, not failed.
    missing = [n for n in INVENTORY_FILES if not (export / n).is_file()]
    inv_text = _read(docs / "inventory.md")
    on = to_date(get(profile, "setup.inventoried_on"))
    faults = []
    if missing:
        faults.append(f"house/export/ lacks {len(missing)} of the twelve files ({', '.join(missing[:4])}"
                      f"{', ...' if len(missing) > 4 else ''})")
    if inv_text is None:
        faults.append("house/docs/inventory.md " + _absent(docs / "inventory.md")[1])
    else:
        m = re.search(r"^# Inventory \((\d{4}-\d{2}-\d{2})\)", inv_text, re.M)
        if not m:
            faults.append("house/docs/inventory.md has no dated '# Inventory (YYYY-MM-DD)' heading")
    if on is None:
        faults.append("setup.inventoried_on not set")
    if faults:
        unread = inv_text is None and (docs / "inventory.md").exists()
        out.append(check("E0-inventory", 0, "auto", "unknown" if unread and len(faults) == 1 else "fail",
                         "; ".join(faults)))
    else:
        meta = None
        try:
            meta = json.loads((export / "meta.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        # meta.json's "exported" is an ISO date-time (2026-01-05T09:00:00+00:00); DATE_RE's \b does not split at T.
        m = re.match(r"(\d{4}-\d{2}-\d{2})", str(meta.get("exported") or "")) if isinstance(meta, dict) else None
        exported = to_date(m.group(1)) if m else None
        edited = _git_date(root, "house/profile.yaml")
        if exported is None or edited is None:
            fresh = "freshness unknown (" + ("meta.json has no 'exported' date" if exported is None
                                             else "the profile's last edit unread") + ")"
        elif exported >= edited:
            fresh = f"export {exported}, profile last edited {edited}"
        else:
            fresh = f"stale: export {exported} is older than the profile's last edit {edited}; re-run export_house.py"
        out.append(check("E0-inventory", 0, "auto", "pass", f"12 files, inventory.md, inventoried_on {on}; {fresh}"))
    # E0-first-look: the page, its date, and the backup, login and secrets lines with a result.
    path = docs / "first-look.md"
    text = _read(path)
    if text is None:
        res, words = _absent(path)
        out.append(check("E0-first-look", 0, "auto", res, f"house/docs/first-look.md {words}"))
    else:
        text = _no_comments(text)
        dated = re.search(r"^# First look \((\d{4}-\d{2}-\d{2})\)", text, re.M)
        lacking = []
        for n, word in FIRST_LOOK_LINES.items():
            row = re.search(rf"^\|\s*{n}\.[^|]*\|([^|]*)\|", text, re.M)
            if not row or not any(r in row.group(1) for r in FIRST_LOOK_RESULTS):
                lacking.append(f"{word} ({n})")
        ok = dated and not lacking
        out.append(check("E0-first-look", 0, "auto", "pass" if ok else "fail",
                         (f"dated {dated.group(1)}" if dated else "no dated '# First look (YYYY-MM-DD)' heading")
                         + ("; backup, login and secrets lines present" if not lacking
                            else "; lines missing or without a result: " + ", ".join(lacking))))
    # E0-untouched: the two Phase 0E snapshots, definitions only (export_house.py --diff).
    start, end = export / ".phase0e-start", export / ".phase0e-end"
    absent = [p.name for p in (start, end) if not p.is_dir()]
    mod, where = _diff_module(root)
    if absent:
        out.append(check("E0-untouched", 0, "auto", "fail",
                         f"snapshot not written yet: house/export/{', house/export/'.join(absent)}"))
    elif mod is None:
        out.append(check("E0-untouched", 0, "auto", "unknown",
                         "export_house.py with --diff not found (house/export/ or templates/export/)"))
    else:
        try:
            differences, unknowns = mod.diff(start, end)
        except Exception as e:  # noqa: BLE001 - a snapshot that cannot be read is unknown, never untouched
            out.append(check("E0-untouched", 0, "auto", "unknown", f"{where} --diff failed ({type(e).__name__})"))
        else:
            if differences:
                entry = [t for _d, t, _b in changelog_entries(_read(docs / "CHANGELOG.md") or "")
                         if re.search(r"phase 0e", t, re.I)]
                out.append(check("E0-untouched", 0, "auto", "fail",
                                 f"{len(differences)} definition(s) changed: " + "; ".join(differences[:5])
                                 + ("; ..." if len(differences) > 5 else "")
                                 + ("; the Phase 0E CHANGELOG entry must say what changed and why" if not entry else
                                    f"; the Phase 0E entry '{entry[-1]}' must say what changed and why")))
            elif unknowns:
                out.append(check("E0-untouched", 0, "auto", "unknown",
                                 "no definition changed in what could be compared; not compared: "
                                 + "; ".join(unknowns)))
            else:
                out.append(check("E0-untouched", 0, "auto", "pass",
                                 "no definition changed between .phase0e-start and .phase0e-end"))
    # E0-differs-written: the policies section, with rows or "none yet".
    path = docs / "policies.md"
    text = _read(path)
    if text is None:
        res, words = _absent(path)
        out.append(check("E0-differs-written", 0, "auto", res, f"house/docs/policies.md {words}"))
    else:
        body = _section(_no_comments(text), DIFFERS_RE)
        if body is None:
            out.append(check("E0-differs-written", 0, "auto", "fail",
                             "house/docs/policies.md has no 'Where this house differs' section"))
        else:
            rows = _table_rows(body)
            none_yet = re.search(r"\bnone yet\b", "\n".join(body), re.I) is not None
            out.append(check("E0-differs-written", 0, "auto", "pass" if rows or none_yet else "fail",
                             f"{len(rows)} row(s)" if rows else ("'none yet'" if none_yet else
                                                                 "section empty: rows or 'none yet' needed")))
    return out


def tidy_up_facts(root):
    """The backlog's tidy-up section (templates/docs/backlog.md): counted for the person, never by a readiness test, and
    never a suggestion of the helper's own. `first_ask` is true while the what-next log has no line yet."""
    b = _read(root / "house/docs/backlog.md")
    body = _section(_no_comments(b), TIDY_RE) if b is not None else None
    rows = None
    if body is not None:
        rows = len(_table_rows(body)) + len([l for l in body if l.startswith("### ")])
    return {"section": "absent" if body is None else "present", "rows": rows,
            "first_ask": last_log(root) is None}


def asks(adoption, today, existing=False):
    out = []
    done = {}
    for e in (adoption.get("once_done") or []) if isinstance(adoption, dict) else []:
        if isinstance(e, dict) and e.get("check"):
            done[str(e["check"])] = on_date(e)
    for cid, (level, words) in ASKS.items():
        if cid in EXISTING_ONLY and not existing:
            continue
        if cid in ONCE:
            on = done.get(cid)
            out.append(check(cid, level, "once", "pass" if on else "ask",
                             f"recorded {on}" if on else words))
        else:
            out.append(check(cid, level, "ask", "ask", words))
    return out


# ---------------------------------------------------------------- the rest of the facts

def adoption_facts(adoption, today):
    a = adoption if isinstance(adoption, dict) else {}
    pace = a.get("pace") or "on-request"
    paused = to_date(a.get("paused_until"))
    last_new = to_date(a.get("last_new_piece"))
    due = None
    if pace in PACE_DAYS:
        due = (last_new + datetime.timedelta(days=PACE_DAYS[pace])).isoformat() if last_new else "now"
    skipped = []
    for s in a.get("skipped") or []:
        if isinstance(s, dict) and s.get("piece") is not None:
            on = on_date(s)
            until = on + datetime.timedelta(days=SKIP_DAYS) if on else None
            skipped.append({"piece": str(s["piece"]), "on": on.isoformat() if on else None,
                            "until": until.isoformat() if until else None,
                            "active": bool(until and until > today) or on is None, "why": s.get("why")})
    opted_out = []
    for o in a.get("opted_out") or []:
        if isinstance(o, dict) and o.get("what") is not None:
            on = on_date(o)
            checks = o.get("checks") or []
            opted_out.append({"what": str(o["what"]), "on": on.isoformat() if on else None, "why": o.get("why"),
                              "checks": [str(c) for c in (checks if isinstance(checks, list) else [checks])]})
    level = a.get("level")
    passed = None
    if isinstance(a.get("levels_passed"), list):
        passed = [{"level": e["level"], "on": str(to_date(on_date(e)) or "") or None}
                  for e in a["levels_passed"] if isinstance(e, dict) and isinstance(e.get("level"), int)]
    return {
        "present": bool(a),
        "level": level if isinstance(level, int) else None,
        "level_passed_on": str(to_date(a.get("level_passed_on")) or "") or None,
        "levels_passed": passed,
        "tracks": a.get("tracks") if isinstance(a.get("tracks"), dict) else {},
        "pace": pace,
        "paused_until": paused.isoformat() if paused else None,
        "paused": bool(paused and paused > today),
        "last_suggested": str(to_date(a.get("last_suggested")) or "") or None,
        "last_new_piece": last_new.isoformat() if last_new else None,
        "next_piece_due": due if pace != "on-request" else "when asked",
        "skipped": skipped,
        "opted_out": opted_out,
    }


def busy_facts(root, board, today):
    rows = {"in_progress": [], "ready_for_review": []}
    for i in (board or {}).get("items", []):
        if i["word"] == "IN PROGRESS":
            rows["in_progress"].append(i["code"])
        elif i["word"] == "READY FOR REVIEW":
            rows["ready_for_review"].append(i["code"])
    text = _read(root / "house/docs/CHANGELOG.md")
    entries = changelog_entries(text) if text else []
    last = max((e[0] for e in entries), default=None)
    ops = _read(root / "house/docs/operations.md")
    freeze = "unknown (no house/docs/operations.md)" if ops is None else "none found"
    if ops is not None:
        for line in _no_comments(ops).splitlines():
            dates = [to_date(d) for d in DATE_RE.findall(line)]
            if re.search(r"\bfreeze\b", line, re.I) and len(dates) >= 2 and dates[0] and dates[1] \
                    and dates[0] <= today <= dates[1]:
                freeze = f"on: {line.strip()[:120]}"
                break
    n = len(rows["in_progress"]) + len(rows["ready_for_review"])
    return {"board_rows": rows if board else None, "open_rows": n if board else None,
            "over_three": (n > BUSY_ROWS) if board else None,
            "last_changelog": last.isoformat() if last else None,
            "days_since_changelog": (today - last).days if last else None,
            "freeze": freeze,
            "usage": "not read by this slice (levels 0-2 have no usage gate; KIT-NEXT adds it)"}


def last_log(root):
    text = _read(root / "house/docs/what-next-log.md")
    if text is None:
        return None
    lines = [l.strip() for l in _no_comments(text).splitlines() if DATE_RE.match(l.strip())]
    return lines[-1] if lines else None


def runtime_facts(root):
    data, how = load_yaml(root / "house/runtime.yaml")
    if data is None:
        return {"file": how}
    entries = {k: str(to_date((v or {}).get("detected_on")) or "") or None
               for k, v in (data.get("runtimes") or {}).items() if isinstance(v, dict)} \
        if isinstance(data.get("runtimes"), dict) else {}
    return {"file": "present", "entries": entries}


def gather(root, today, network=True, selftest=True):
    profile, how = load_yaml(root / "house/profile.yaml")
    probe = root / "templates/runtime/probe_runtime.py"
    probe_git = load_module(probe, "probe_runtime").probe_git if probe.exists() else None
    bc = root / "templates/docs/board_check.py"
    board_mod = load_module(bc, "board_check") if bc.exists() else None
    existing = get(profile, "setup.existing_house") is True if profile else False
    checks = level0(root, profile, how)
    if existing:
        checks += existing_house(root, profile, today)
    checks += level1(root, profile, how, network, selftest, probe_git)
    l2, board = level2(root, today, board_mod)
    checks += l2
    adoption = get(profile, "adoption") if profile else None
    checks += asks(adoption, today, existing)
    checks.sort(key=lambda c: (c["level"], c["kind"] != "auto"))
    passed_through = None
    for lv in LEVELS:
        if all(c["result"] == "pass" for c in checks if c["level"] == lv and c["kind"] == "auto"):
            passed_through = lv
        else:
            break
    ad = adoption_facts(adoption, today)
    # The levels whose standing checks are re-run (levels.md, "Reading a profile"): those in levels_passed; a
    # profile without the key (written before 2026-10-27) is read as 0 through level, but never above 3.
    if ad["levels_passed"] is not None:
        held, held_from = sorted({e["level"] for e in ad["levels_passed"]}), "levels_passed"
    elif ad["level"] is not None:
        held, held_from = list(range(0, min(ad["level"], 3) + 1)), "level (no levels_passed: read as 0 through " \
            f"{min(ad['level'], 3)})"
    else:
        held, held_from = [], "nothing recorded"
    # A check the owner opted out of (adoption.opted_out[].checks; AGENTS.md, "The kit serves the owner") is
    # still run and shown, but is never a standing failure: the helper does not suggest restoring a dropped rail.
    dropped = {c for o in ad["opted_out"] for c in o["checks"]}
    standing = [c["id"] for c in checks if c["kind"] == "auto" and c["result"] == "fail" and c["level"] in held
                and c["id"] not in dropped]
    unreadable = [{"id": c["id"], "evidence": c["evidence"]} for c in checks
                  if c["kind"] == "auto" and c["result"] == "unknown"]
    return {
        "today": today.isoformat(),
        "profile": how if profile is None else f"read ({how})",
        "schema": ("v3" if isinstance(get(profile, "setup"), dict) and "existing_house" in get(profile, "setup")
                   else "v2") if adoption is not None else
                  ("v1 (no adoption block: level unknown)" if profile else None),
        "existing_house": existing,
        "adoption": ad,
        "auto_pass_through": passed_through,
        "levels_checked": list(LEVELS),
        "levels_not_checked": "3-7 and the side tracks (KIT-NEXT)",
        "levels_held": held,
        "levels_held_from": held_from,
        "standing_failures": standing,
        "unreadable": unreadable,
        "checks": checks,
        "busy": busy_facts(root, board, today),
        "last_log": last_log(root),
        "runtime": runtime_facts(root),
        "tidy_up": tidy_up_facts(root) if existing else None,
    }


def table(facts):
    ad = facts["adoption"]
    lines = [f"what_next.py facts, {facts['today']} (levels 0-2; facts only, no suggestions)",
             f"profile: {facts['profile']}; schema {facts['schema']}"
             + ("; existing house (path C: the E0 lines apply)" if facts.get("existing_house") else ""),
             f"recorded level: {ad['level'] if ad['level'] is not None else 'unknown'}"
             f" (passed {ad['level_passed_on'] or '-'}); auto checks pass through level "
             f"{facts['auto_pass_through'] if facts['auto_pass_through'] is not None else 'none'}",
             f"pace: {ad['pace']}; next new piece: {ad['next_piece_due']}; paused: "
             f"{'until ' + ad['paused_until'] if ad['paused'] else 'no'}; "
             f"last new piece: {ad['last_new_piece'] or '-'}",
             f"levels passed: {', '.join(map(str, facts['levels_held'])) or 'none'} (from {facts['levels_held_from']})",
             f"standing failures (failing checks of those levels): {', '.join(facts['standing_failures']) or 'none'}",
             "unreadable: " + (", ".join(u["id"] for u in facts["unreadable"]) or "none"),
             "", f"{'check':<22} {'lvl':>3} {'kind':<5} {'result':<8} evidence"]
    for c in facts["checks"]:
        lines.append(f"{c['id']:<22} {c['level']:>3} {c['kind']:<5} {c['result']:<8} {c['evidence']}")
    b = facts["busy"]
    rows = b["board_rows"]
    lines += ["",
              "busy: " + (f"{len(rows['in_progress'])} in progress, {len(rows['ready_for_review'])} in review"
                          if rows else "no board") +
              f"; last CHANGELOG entry {b['last_changelog'] or '-'}; freeze {b['freeze']}",
              "skipped: " + (", ".join(f"{s['piece']} until {s['until']}" for s in ad["skipped"] if s["active"])
                             or "none"),
              "opted out (the owner's choice; never re-offered): "
              + (", ".join(f"{o['what']} {o['on'] or '-'}" for o in ad["opted_out"]) or "none"),
              f"last what-next log line: {facts['last_log'] or 'none'}",
              f"runtime record: {facts['runtime'].get('file')}"]
    t = facts.get("tidy_up")
    if t:
        lines.append("tidy-up section: " + (f"{t['rows']} row(s), optional; never counted, never suggested on its own"
                                            if t["section"] == "present" else "absent")
                     + ("; first what-next: name it once" if t["first_ask"] else ""))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today, local time)")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--no-selftest", action="store_true")
    ap.add_argument("--json", action="store_true", help="the JSON block only")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root).resolve()
    if not (root / "AGENTS.md").exists() and not (root / "house").is_dir():
        print(f"{root}: not a house repository (no AGENTS.md, no house/); run from its root or pass --root")
        return 2
    today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
    facts = gather(root, today, network=not a.no_network, selftest=not a.no_selftest)
    blob = json.dumps(facts, indent=1, default=str)
    print(blob if a.json else f"{table(facts)}\n\n--- facts (json) ---\n{blob}\n--- end ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
