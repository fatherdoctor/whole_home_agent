#!/usr/bin/env python3
"""probe_runtime.py - run STEP 0's probes and keep this runtime's entry in house/runtime.yaml.

Status: template (KIT-RT0s, 2026-10-23). Python 3 standard library only. Run from the house repository's root:

    python3 templates/runtime/probe_runtime.py --runtime claude-cloud --set schedule=yes --set subagents=yes
    python3 templates/runtime/probe_runtime.py --runtime claude-code --place box   # entry key claude-code/box

What it does (templates/runtime/STEP-0.md, steps b and c):
- probes what a script can observe for itself: shell, read_files, write_files, git_push, web, box_access;
- finds out where it runs (KIT-STEP0): `where` is box (the Supervisor's token, or /share beside the config folder),
  cloud (a cloud session's marker, or --runtime claude-cloud) or computer; --where overrides it when the agent knows
  better. A chat with no shell cannot run this script; STEP-0.md says what it does instead;
- checks GitHub read-only (KIT-STEP0): git present, this folder a repository with an `origin`, a credential set up
  (an environment variable's name, a git credential helper or `gh auth status`; never its value or the account),
  and whether `origin` answers `git ls-remote`; with the push dry run that gives `github`: push | read-only |
  no-reach | none. Only the host's kind is said (GitHub or another git server), never the address;
- takes what only the agent can observe (schedule, subagents, long_context, persistent_memory, notify_owner, and
  the runtime's name) from --runtime and --set; a key the agent does not pass keeps the entry's value, or unknown;
- writes or updates one entry in house/runtime.yaml, and rewrites the file only when a value changed or the entry
  is over 7 days old (an unattended run calls this every time without a commit per run);
- prints the probe table, STEP 0's one-line report (step d) and two plain lines for the owner: where this is and
  what that changes, and what GitHub can do from here.

When the same runtime runs in more than one place (a terminal agent on a laptop and on the box), give each a
--place: the entry key becomes <runtime>/<place>, so neither run rewrites the other's entry.

It never sends anything to a person, never prints a token or the box's address, and writes nothing but
house/.probe (deleted again) and house/runtime.yaml (through house/runtime.yaml.tmp beside it, removed again if the
replace fails). Values under `can` may be read as yes/no/unknown strings or as
YAML booleans (true/false); they are written as yes/no/unknown. Comments inside an entry are not kept on a rewrite;
put a note that must last in `variant`. A hand-added key under an entry may hold a scalar, never a nested mapping
(the script refuses such a file rather than drop the mapping on a rewrite). The shell probe runs `sh`; a runtime
without it (plain Windows) records `shell: no` even where another shell works.

Exit 0 when the record is current (written, unchanged, or printed for the person to save); 2 on bad arguments or a
runtime.yaml this script cannot read safely (it refuses rather than overwrite it).
"""
import argparse
import datetime
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

RUNTIMES = ("claude-code", "claude-cloud", "claude-app", "other")
KEYS = ("shell", "read_files", "write_files", "git_push", "web", "schedule", "subagents", "long_context",
        "persistent_memory", "box_access", "notify_owner")
PROBED = ("shell", "read_files", "write_files", "git_push", "web", "box_access")
TOLD = tuple(k for k in KEYS if k not in PROBED)
ROLES = ("planner", "builder", "reviewer", "mechanical", "writer")
WHERE = ("box", "cloud", "computer")              # a chat has no shell and records nothing (STEP-0.md)
GITHUB = ("push", "read-only", "no-reach", "none")
PLACE_KEYS = ("where", "github")                  # entry scalars beside `can`, written by this script
STALE_DAYS = 7
WEB_URL = "https://version.home-assistant.io/stable.json"
TIMEOUT = 20

HEADER = """\
# house/runtime.yaml - what each assistant runtime can do in this house.
# Written by STEP 0 (templates/runtime/STEP-0.md), one entry per runtime the household uses, by hand or by
# templates/runtime/probe_runtime.py. Values under `can` are yes / no / unknown; `fallbacks_in_use` lists the keys
# that are not yes, one templates/runtime/FALLBACKS.md row each. model_roles maps the kit's roles to the models
# this runtime offers. A rewrite by the script keeps this header and drops comments inside entries.
"""


# ---------------------------------------------------------------- values

def norm(value):
    """yes / no / unknown from a YAML boolean or a string in any case; None when it is none of them."""
    if value is True:
        return "yes"
    if value is False:
        return "no"
    v = str(value).strip().strip("\"'").lower()
    if v in ("yes", "true", "on", "y"):
        return "yes"
    if v in ("no", "false", "off", "n"):
        return "no"
    if v in ("unknown", "", "null", "~", "none"):
        return "unknown"
    return None


# ---------------------------------------------------------------- the record (the template's shape only)

class RecordError(Exception):
    pass


def _strip_comment(line):
    """Drop a trailing comment. A quote opens only at the start of a scalar (line start, after `: `, or after `[`
    or `,` in a flow list), as in YAML; a quote mid-word (Dad's laptop) is plain text."""
    out, quote, start, flow = [], None, True, False
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
            out.append(ch)
            continue
        if ch in "\"'" and start:
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
        if ch in " \t":
            start = start or (i > 0 and line[i - 1] == ":")
        elif ch == "[" and start:
            flow = True
        else:
            start = flow and ch == ","
    return "".join(out).rstrip()


def _scalar(text):
    t = text.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    if t.startswith("[") and t.endswith("]"):
        return [_scalar(x) for x in t[1:-1].split(",") if x.strip()]
    if t.lower() in ("true", "false"):
        return t.lower() == "true"
    return t


def parse_record(text):
    """Read house/runtime.yaml: block mappings of scalars and flow lists, two-space indents, as the template is.
    Anything else (anchors, block lists, multi-line strings, tabs) raises RecordError, so the caller refuses
    rather than rewrite a file it did not understand."""
    root, stack = {}, [(-1, None)]
    stack[0] = (-1, root)
    opened = []  # (depth, parent, key, mapping, line) for every `key:` with nothing after it
    for n, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise RecordError(f"line {n}: tab indent")
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if body.startswith(("- ", "&", "*", "|", ">")) or body == "-":
            raise RecordError(f"line {n}: unsupported YAML ({body[:20]!r})")
        m = re.match(r'^("[^"]*"|\'[^\']*\'|[^:]+?):(?:\s+(.*))?$', body)
        if not m:
            raise RecordError(f"line {n}: not a 'key: value' line")
        key, rest = _scalar(m.group(1)), (m.group(2) or "").strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise RecordError(f"line {n}: bad indent")
        parent = stack[-1][1]
        if not isinstance(parent, dict) or key in parent:
            raise RecordError(f"line {n}: duplicate or misplaced key {key!r}")
        if rest:
            if rest.startswith(("&", "*", "|", ">", "{")):
                raise RecordError(f"line {n}: unsupported YAML ({rest[:20]!r})")
            parent[key] = _scalar(rest)
        else:
            parent[key] = {}
            opened.append((len(stack) - 1, parent, key, parent[key], n))
            stack.append((indent, parent[key]))
    for depth, parent, key, mapping, n in opened:
        expects_mapping = depth < 2 or (depth == 2 and key in ("model_roles", "can"))
        if not mapping and not expects_mapping:
            parent[key] = ""  # `variant:` with no deeper line is an empty value, not a mapping
        elif mapping and not expects_mapping:
            raise RecordError(f"line {n}: `{key}` is a mapping the template does not have; put a note in "
                              "`variant` or move it out of runtime.yaml")
    runtimes = root.get("runtimes", {})
    if set(root) - {"runtimes"} or not isinstance(runtimes, dict):
        raise RecordError("top level must be only `runtimes:`")
    for name, entry in runtimes.items():
        if not isinstance(entry, dict):
            raise RecordError(f"runtime {name!r} is not a mapping")
    return runtimes


def _q(value):
    v = "" if value is None else str(value)
    if (v == "" or re.search(r"[:#\[\]{},&*!|>'\"%@`]", v) or v != v.strip() or norm(v) in ("yes", "no")
            or v[0] in "-?+.~0123456789" or v.lower() == "null"):
        return json.dumps(v)  # quoted, so a YAML reader keeps "yes", "- x", "123" or "null" as text
    return v


def dump_record(runtimes):
    out = [HEADER.rstrip("\n"), "runtimes:"]
    for name, e in runtimes.items():
        out.append(f"  {_q(name)}:")
        out.append(f"    variant: {_q(e.get('variant', ''))}")
        d = str(e.get("detected_on", ""))
        out.append("    detected_on: " + (d if re.fullmatch(r"\d{4}-\d\d-\d\d", d) else _q(d)))
        for k in PLACE_KEYS:
            if k in e:
                out.append(f"    {k}: {_q(e[k])}")
        out.append("    model_roles:")
        roles = e.get("model_roles") if isinstance(e.get("model_roles"), dict) else {}
        for r in list(ROLES) + [r for r in roles if r not in ROLES]:
            out.append(f"      {_q(r)}: {_q(roles.get(r, 'FILL'))}")
        out.append("    can:")
        can = e.get("can") if isinstance(e.get("can"), dict) else {}
        for k in list(KEYS) + [k for k in can if k not in KEYS]:
            out.append(f"      {_q(k)}: {norm(can.get(k, 'unknown')) or 'unknown'}")
        fb = e.get("fallbacks_in_use") or []
        out.append("    fallbacks_in_use: [" + ", ".join(_q(x) for x in fb) + "]")
        for k, v in e.items():  # keys a person added by hand survive a rewrite (scalars only)
            if (k not in ("variant", "detected_on", "model_roles", "can", "fallbacks_in_use") + PLACE_KEYS
                    and not isinstance(v, dict)):
                out.append(f"    {_q(k)}: {_q(v)}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- probes (each returns (value, evidence))

def _run(cmd, cwd, timeout=TIMEOUT):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="echo", SSH_ASKPASS="echo", LC_ALL="C")
    env["GIT_SSH_COMMAND"] = env.get("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)


def probe_shell(root):
    try:
        r = _run(["sh", "-c", "echo ok"], root)
        return ("yes", "echo ok printed ok") if r.stdout.strip() == "ok" else ("no", "echo ok did not print ok")
    except Exception as e:  # noqa: BLE001 - any failure is "no"
        return "no", f"sh failed ({type(e).__name__})"


def probe_read(root):
    try:
        first = (root / "AGENTS.md").read_text(encoding="utf-8").splitlines()[0]
        return ("yes", "AGENTS.md first line read") if first.strip() else ("no", "AGENTS.md first line empty")
    except Exception as e:  # noqa: BLE001
        return "no", f"AGENTS.md not read ({type(e).__name__})"


def probe_write(root, today):
    house = root / "house"
    if not house.is_dir():
        return "no", "house/ is missing (copy the kit's house/ first)"
    p = house / ".probe"
    try:
        p.write_text(today + "\n", encoding="utf-8")
        back = p.read_text(encoding="utf-8").strip()
        p.unlink()
        if back == today and not p.exists():
            return "yes", "house/.probe written, read back, deleted"
        return "no", "house/.probe round trip did not match"
    except Exception as e:  # noqa: BLE001
        try:
            p.unlink()
        except OSError:
            pass
        return "no", f"house/.probe round trip failed ({type(e).__name__})"


def probe_git(root):
    """The KIT-RT0r M3 form: `git push --dry-run --no-verify origin HEAD`, exit 0 = yes (an up-to-date branch and a
    branch with no upstream both count; the dry run pushes nothing, so skipping the pre-push hook loses nothing)."""
    try:
        if _run(["git", "rev-parse", "--is-inside-work-tree"], root).returncode != 0:
            return "no", "not a git repository"
        if _run(["git", "symbolic-ref", "-q", "HEAD"], root).returncode != 0:
            return "no", "detached HEAD"
        if _run(["git", "remote", "get-url", "origin"], root).returncode != 0:
            return "no", "no origin remote"
        r = _run(["git", "push", "--dry-run", "--no-verify", "--porcelain", "origin", "HEAD"], root, timeout=60)
    except subprocess.TimeoutExpired:
        return "no", "git push --dry-run timed out"
    except Exception as e:  # noqa: BLE001
        return "no", f"git failed ({type(e).__name__})"
    if r.returncode == 0:
        return "yes", "git push --dry-run --no-verify origin HEAD exit 0"
    err = ((r.stderr or "") + (r.stdout or "")).lower()
    if re.search(r"auth|permission|denied|403|401|credential", err):
        return "no", "git push --dry-run: authentication refused"
    if re.search(r"non-fast-forward|fetch first|\[rejected\]", err):
        return "yes", "dry run reached the remote; branch behind origin (fetch before pushing)"
    why = "remote not reachable" if re.search(r"resolve|connect|timed out|network", err) else f"exit {r.returncode}"
    return "no", f"git push --dry-run: {why}"


def probe_web(fetch=None):
    fetch = fetch or _fetch
    try:
        status, body = fetch(WEB_URL, {})
        if status == 200 and isinstance(json.loads(body), dict):
            return "yes", "stable.json fetched"
        return "no", f"stable.json: HTTP {status}"
    except Exception as e:  # noqa: BLE001
        return "no", f"stable.json not fetched ({type(e).__name__})"


SUPERVISOR_CORE = "http://supervisor/core"   # the Supervisor proxies Core at <this>/api/..., reachable from inside an add-on


def _read_tool(name):
    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / (name + ".py")
    spec = importlib.util.spec_from_file_location("_kit_" + name, path)
    if spec is None or spec.loader is None:
        raise ValueError("read_tool_unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def probe_box(env=None, fetch=None, profile=None, root=None, token_path=None):
    """install/agent-access.md section 3: GET /api/ is 200, GET /api/states counts. Prints the count only.
    Two ways in: HA_URL + HA_TOKEN (an agent outside the box), or SUPERVISOR_TOKEN alone (an agent running as an
    add-on inside the box, KIT-BASE: the Supervisor proxies Core at SUPERVISOR_CORE, no agent user or token needed).
    The path is named by where it goes, not by which variable named it (KIT-BASEr M1): the add-on exports
    HA_URL=http://supervisor/core and HA_TOKEN=$SUPERVISOR_TOKEN itself at each start, so inside it both are set and
    the answer is still "via the Supervisor (inside an add-on)"."""
    env = os.environ if env is None else env
    fetch = fetch or _fetch
    reader = None
    try:
        reader = _read_tool("ha_read")
        if profile is None:
            if root is None:
                return "no", "box target not confirmed in profile"
            path = pathlib.Path(root) / "house/profile.yaml"
            if not path.is_file():
                return "unknown", "no house/profile.yaml yet; confirm the box in install/agent-access.md section 2"
            profile = _read_tool("profile_check").load_profile(path)
        url = reader.require_target(reader.selected_url(env), profile)
        # Reach only the pinned endpoint first, without looking up a credential or following redirects.
        status, body = fetch(url + "/api/", {})
        def api_running(text):
            try:
                data = json.loads(text)
                return isinstance(data, dict) and data.get("message") == "API running."
            except (ValueError, TypeError):
                return False
        if status != 401 and not (status == 200 and api_running(body)):
            return "no", "box endpoint not verified before credentials"
        token = reader.read_token(env, url, root or pathlib.Path.cwd(), token_path)
        via = "the Supervisor (inside an add-on)" if url == SUPERVISOR_CORE.rstrip("/") else "HA_URL"
        headers = {"Authorization": "Bearer " + token}
        status, body = fetch(url + "/api/", headers)
        if status != 200:
            return "no", f"/api/ returned {status}"
        if not api_running(body):
            return "no", "/api/ did not return the expected Home Assistant response"
        status, body = fetch(url + "/api/states", headers)
        states = json.loads(body) if status == 200 else None
        if not isinstance(states, list):
            return "no", f"/api/states returned {status}"
        return "yes", f"200, {len(states)} entities, via {via}"
    except Exception as e:  # noqa: BLE001 - never echo the exception text: it can name the URL
        if reader is not None and isinstance(e, reader.ReadError):
            return "no", "box read blocked (" + str(e) + ")"
        return "no", f"box read failed ({type(e).__name__})"


def detect_where(env=None, exists=None, runtime=None):
    """Where this run is (KIT-STEP0), from evidence: (where, evidence). The box first: an app on the box has the
    Supervisor's token, and a shell on the box sees /share beside the config folder. Then a cloud session: the
    runtime named claude-cloud, or the marker a cloud session sets. Anything else with a shell is a computer."""
    env = os.environ if env is None else env
    exists = exists or os.path.exists
    if env.get("SUPERVISOR_TOKEN"):
        return "box", "SUPERVISOR_TOKEN is set (an app on the box)"
    if exists("/share") and (exists("/homeassistant/configuration.yaml") or exists("/config/configuration.yaml")):
        return "box", "/share and the config folder are here"
    if runtime == "claude-cloud":
        return "cloud", "the runtime is a cloud session (--runtime claude-cloud)"
    if str(env.get("CLAUDE_CODE_REMOTE", "")).strip().lower() in ("1", "true", "yes"):
        return "cloud", "a cloud session's marker is set (CLAUDE_CODE_REMOTE)"
    return "computer", ("a shell; no box folders and no cloud marker found (in another vendor's cloud container, "
                        "pass --where cloud)")


def _remote_kind(url):
    """GitHub or another git server, from the remote's address; the address itself is never returned."""
    m = re.match(r"^(?:[a-z+]+://)?(?:[^@/]*@)?([^/:]+)", url.strip(), re.I)
    host = (m.group(1) if m else "").lower()
    return "GitHub" if host in ("github.com", "www.github.com", "ssh.github.com") else "a git server (not GitHub)"


def local_remote_kind(root):
    """The remote's kind from the local config only (no network), for a run that probes nothing; "" when unknown."""
    try:
        r = _run(["git", "remote", "get-url", "origin"], root)
    except Exception:  # noqa: BLE001
        return ""
    return _remote_kind(r.stdout) if r.returncode == 0 and r.stdout.strip() else ""


def probe_github(root, env=None, which=None):
    """KIT-STEP0's GitHub check, read-only: (state, kind, evidence) with state none | no-reach | reach. Nothing is
    pushed and nothing printed names the remote, the account or a token: a credential is reported by kind only."""
    env = os.environ if env is None else env
    which = which or shutil.which
    if not which("git"):
        return "none", "", "git is not installed"
    try:
        if _run(["git", "rev-parse", "--is-inside-work-tree"], root).returncode != 0:
            return "none", "", "this folder is not a git repository"
        r = _run(["git", "remote", "get-url", "origin"], root)
        if r.returncode != 0 or not r.stdout.strip():
            return "none", "", "a repository with no origin remote"
        kind = _remote_kind(r.stdout)
        creds = [n for n in ("GH_TOKEN", "GITHUB_TOKEN") if env.get(n)]
        if _run(["git", "config", "--get-all", "credential.helper"], root).stdout.strip():
            creds.append("a git credential helper")
        if which("gh"):
            try:
                if _run(["gh", "auth", "status"], root).returncode == 0:
                    creds.append("gh is signed in")
            except subprocess.TimeoutExpired:
                creds.append("gh auth status timed out")
        cred = ("credential: " + ", ".join(creds)) if creds else "no credential set up"
        ls = _run(["git", "ls-remote", "--exit-code", "origin", "HEAD"], root, timeout=60)
    except subprocess.TimeoutExpired:
        return "no-reach", "", "git ls-remote timed out"
    except Exception as e:  # noqa: BLE001
        return "no-reach", "", f"git failed ({type(e).__name__})"
    if ls.returncode in (0, 2):  # 2: reached, but the remote has no HEAD yet (an empty repository)
        return "reach", kind, f"origin on {kind} answers git ls-remote; {cred}"
    return "no-reach", kind, f"origin on {kind} did not answer git ls-remote; {cred}"


def github_state(reach, git_push):
    """push | read-only | no-reach | none, from probe_github's state and the push dry run."""
    if reach == "reach":
        return "push" if git_push == "yes" else "read-only"
    return reach


def owner_lines(entry, kind=""):
    """The plain lines Step 0 tells the owner (KIT-STEP0): where this is and what that changes; GitHub, and where
    the house folder lives from here. A line whose value the entry does not hold is left out, never defaulted."""
    where, box, gh = entry.get("where"), entry.get("can", {}).get("box_access"), entry.get("github")
    lines = []
    if where == "box":
        lines.append("I am running on your Home Assistant box itself: I skip the install steps and read the box "
                     "directly" + ("." if box == "yes" else
                                   ", once you confirm it is your box (install/agent-access.md section 2)."))
    elif where == "cloud":
        lines.append("I am running in a cloud session with a fresh copy of the repository"
                     + (": even with a way into your box, I change nothing on it from here; "
                        if box == "yes" else " and no way into your box: I change nothing on the box from here; ")
                     + "I hand you the steps, or we carry on in a session on the box.")
    elif where == "computer":
        lines.append("I am running on a computer with a shell, and "
                     + ("I can read your box." if box == "yes" else
                        "I cannot read your box from here yet (install/agent-access.md sets that up, or you read it "
                        "to me)."))
    if gh not in GITHUB or where not in WHERE:
        return tuple(lines)
    name = kind or "GitHub"
    # Where the house folder lives when it is not pushed (KIT-STEP0r F2): only the box has the box's backups, and
    # a cloud session's folder is thrown away with it.
    keep = {
        "box": "your house folder stays local and in the box's backups",
        "computer": "your house folder is on this computer only (a copy on the box or on a remote is your choice)",
        "cloud": "nothing written here outlives this session: I hand you the files or the diff before it ends",
    }[where]
    if gh == "push":
        lines.append(f"{name}: I can reach your repository and push to it, so " + {
            "box": "your house folder is kept there as well as in the box's backups.",
            "computer": "your house folder is kept there as well as on this computer.",
            "cloud": "I push each change there before this session ends; nothing else written here outlives it.",
        }[where])
    elif gh == "read-only":
        lines.append(f"{name}: I can read the repository but not push to it as it stands, so "
                     + ("I keep changes here and hand you the push (or a diff); " if where != "cloud" else "")
                     + keep + ".")
    elif gh == "no-reach":
        lines.append(f"{name}: the repository's remote did not answer, so " + keep
                     + ("" if where == "cloud" else " until it does") + "; GitHub is optional.")
    else:
        lines.append("GitHub: this folder is not connected to one, so " + keep + "; GitHub is optional.")
    return tuple(lines)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def _fetch(url, headers):
    req = urllib.request.Request(url, headers=dict(headers, **{"User-Agent": "kit-probe-runtime"}))
    try:
        opener = urllib.request.build_opener(NoRedirect)
        with opener.open(req, timeout=TIMEOUT) as r:  # fixed public URL or profile-pinned HA_URL
            return r.status, r.read(5_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


# ---------------------------------------------------------------- the entry

def merge(old, observed, told, variant, roles, today, place=None):
    """Return (entry, changed). `changed` is True when a value differs or the entry is new or stale; then
    detected_on becomes today. `place` holds the entry scalars `where` and `github` (KIT-STEP0); a key it does not
    hold keeps the entry's value."""
    old = old or {}
    can_old = old.get("can") if isinstance(old.get("can"), dict) else {}
    can = {}
    for k in KEYS:
        if k in observed:
            can[k] = observed[k]
        elif k in told:
            can[k] = told[k]
        else:
            can[k] = norm(can_old.get(k, "unknown")) or "unknown"
    for k, v in can_old.items():  # a key a newer kit added by hand is kept
        if k not in KEYS:
            can[k] = norm(v) or "unknown"
    old_roles = old.get("model_roles") if isinstance(old.get("model_roles"), dict) else {}
    new_roles = {r: str(old_roles.get(r, "FILL")) for r in ROLES}
    new_roles.update({r: str(v) for r, v in old_roles.items() if r not in ROLES})
    new_roles.update(roles)
    entry = {k: v for k, v in old.items() if k not in ("variant", "detected_on", "model_roles", "can",
                                                      "fallbacks_in_use")}
    entry.update({
        "variant": old.get("variant", "") if variant is None else variant,
        "detected_on": str(old.get("detected_on", "")),
        "model_roles": new_roles,
        "can": can,
        "fallbacks_in_use": [k for k in KEYS if can[k] != "yes"],
    })
    entry.update(place or {})
    same = (old and {k: norm(v) or "unknown" for k, v in can_old.items()} == can
            and str(old.get("variant", "")) == entry["variant"]
            and {r: str(v) for r, v in old_roles.items()} == new_roles
            and list(old.get("fallbacks_in_use") or []) == entry["fallbacks_in_use"]
            and all(str(old.get(k, "")) == str(v) for k, v in (place or {}).items()))
    changed = not same or is_stale(entry["detected_on"], today)
    if changed:
        entry["detected_on"] = today
    return entry, changed


def is_stale(detected_on, today):
    try:
        d = datetime.date.fromisoformat(str(detected_on))
    except ValueError:
        return True
    return (datetime.date.fromisoformat(today) - d).days >= STALE_DAYS


def report_line(name, entry):  # name is the entry key, <runtime> or <runtime>/<place>
    can = entry["can"]
    parts = [f"{k} {can[k]}" for k in KEYS]
    fb = entry["fallbacks_in_use"]
    tail = ("; fallbacks (templates/runtime/FALLBACKS.md): " + ", ".join(fb)) if fb else "; no fallbacks needed"
    return f"{name}: " + ", ".join(parts) + tail


# ---------------------------------------------------------------- main

def parse_args(argv):
    ap = argparse.ArgumentParser(description="Run STEP 0's probes and keep house/runtime.yaml current.")
    ap.add_argument("--runtime", required=True, help="the runtime you observe: " + " | ".join(RUNTIMES))
    ap.add_argument("--place", help="where it runs when the same runtime runs in more than one place (letters, digits, "
                    "-); the entry key becomes <runtime>/<place>")
    ap.add_argument("--where", choices=WHERE, help="where this runs, when you know better than the evidence "
                    "(default: detected; a chat with no shell does not run this script)")
    ap.add_argument("--variant", help="free text, e.g. 'scheduled run' (kept from the entry when omitted)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="a value only you can observe: " + ", ".join(TOLD) + " (yes/no/unknown, or true/false)")
    ap.add_argument("--role", action="append", default=[], metavar="ROLE=MODEL",
                    help="map a role (" + ", ".join(ROLES) + ") to a model this runtime offers")
    ap.add_argument("--root", default=".", help="the house repository's root (default: here)")
    ap.add_argument("--file", help="the record (default: <root>/house/runtime.yaml)")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today's local date)")
    ap.add_argument("--if-stale", action="store_true",
                    help="interactive step a: when the entry exists and is under 7 days old, report it and probe nothing")
    ap.add_argument("--dry-run", action="store_true", help="probe and report; write nothing but house/.probe")
    ap.add_argument("--no-web", action="store_true", help="skip the web probe (keeps the entry's web value, unknown when new)")
    ap.add_argument("--no-box", action="store_true", help="do not read credentials or contact Home Assistant; box_access unknown")
    a = ap.parse_args(argv)
    if a.runtime not in RUNTIMES:
        ap.error(f"--runtime must be one of {', '.join(RUNTIMES)} (name another runtime 'other' and use --variant)")
    if a.place is not None and not re.fullmatch(r"[A-Za-z0-9-]+", a.place):
        ap.error("--place: letters, digits and - only (e.g. box, laptop)")
    a.name = a.runtime + ("/" + a.place if a.place else "")
    told = {}
    for kv in a.set:
        k, sep, v = kv.partition("=")
        k = k.strip()
        if not sep or k not in KEYS:
            ap.error(f"--set {kv!r}: KEY must be one of {', '.join(KEYS)}")
        if k in PROBED:
            ap.error(f"--set {k}: the script probes {k} itself; it does not take it on trust")
        if norm(v) is None:
            ap.error(f"--set {kv!r}: VALUE must be yes, no or unknown")
        told[k] = norm(v)
    roles = {}
    for kv in a.role:
        r, sep, m = kv.partition("=")
        if not sep or not r.strip() or not m.strip():
            ap.error(f"--role {kv!r}: use ROLE=MODEL")
        roles[r.strip()] = m.strip()
    try:
        today = a.today or datetime.date.today().isoformat()
        datetime.date.fromisoformat(today)
    except ValueError:
        ap.error("--today must be YYYY-MM-DD")
    return a, told, roles, today


def main(argv=None, probes=None):
    a, told, roles, today = parse_args(sys.argv[1:] if argv is None else argv)
    root = pathlib.Path(a.root).resolve()
    path = pathlib.Path(a.file) if a.file else root / "house" / "runtime.yaml"

    runtimes = {}
    if path.exists():
        try:
            runtimes = parse_record(path.read_text(encoding="utf-8"))
        except (RecordError, OSError, UnicodeDecodeError) as e:
            print(f"refusing: {path} is not in the template's shape ({e}); fix it by hand or move it aside",
                  file=sys.stderr)
            return 2
    runtimes = {k: v for k, v in runtimes.items() if not str(k).startswith("FILL")}
    name = a.name
    old = runtimes.get(name)

    # An entry from before KIT-STEP0 has no `where` or `github`: it is probed, never read as a default (KIT-STEP0r F1).
    if (a.if_stale and old and not is_stale(old.get("detected_on", ""), today)
            and all(old.get(k) for k in PLACE_KEYS)):
        entry, _ = merge(old, {}, {}, None, {}, str(old.get("detected_on")))
        print(f"{path.name}: entry for {name} is from {old.get('detected_on')}, under {STALE_DAYS} days; "
              "nothing probed")
        print(report_line(name, entry))
        print("\n".join(owner_lines(dict(entry, where=old["where"], github=old["github"]),
                                     local_remote_kind(root))))
        return 0

    probes = probes or {
        "shell": lambda: probe_shell(root),
        "read_files": lambda: probe_read(root),
        "write_files": lambda: probe_write(root, today),
        "git_push": lambda: probe_git(root),
        "web": probe_web,
        "box_access": lambda: probe_box(root=root),
    }
    observed, evidence = {}, {}
    for k in PROBED:
        if k == "box_access" and a.no_box:
            observed[k], evidence[k] = "unknown", "not probed (--no-box)"
            continue
        if k == "web" and a.no_web:  # not observed: keep the entry's value, so the flag never forces a rewrite
            evidence[k] = "skipped (--no-web); kept from the entry" if old else "not probed (--no-web)"
            continue
        observed[k], evidence[k] = probes[k]()
    for k in TOLD:
        evidence[k] = "told (--set)" if k in told else ("kept from the entry" if old else "not told")
    if a.where:
        where, evidence["where"] = a.where, "told (--where)"
    else:
        where, evidence["where"] = probes.get("where", lambda: detect_where(runtime=a.runtime))()
    reach, kind, evidence["github"] = probes.get("github", lambda: probe_github(root))()
    git_push = observed.get("git_push", norm((old or {}).get("can", {}).get("git_push", "")) if old else "unknown")
    place = {"where": where, "github": github_state(reach, git_push)}

    entry, changed = merge(old, observed, told, a.variant, roles, today, place)

    print(f"{'key':<18} {'value':<8} evidence")
    for k in KEYS:
        print(f"{k:<18} {entry['can'][k]:<8} {evidence[k]}")
    for k in PLACE_KEYS:
        print(f"{k:<18} {entry[k]:<8} {evidence[k]}")
    print()

    runtimes[name] = entry
    text = dump_record(runtimes)
    if not changed:
        print(f"{path}: unchanged (entry from {entry['detected_on']})")
    elif a.dry_run:
        print(f"{path}: would be {'updated' if old else 'written'} (--dry-run); the entry:\n")
        print(dump_record({name: entry}))
    elif entry["can"]["write_files"] != "yes":
        print(f"{path}: not written (write_files {entry['can']['write_files']}); save this entry there:\n")
        print(dump_record({name: entry}))
    else:
        tmp = path.with_name(path.name + ".tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(text, encoding="utf-8")
            if path.exists():
                shutil.copymode(path, tmp)
            tmp.replace(path)
            print(f"{path}: {'updated' if old else 'written'} (entry dated {today})")
        except OSError as e:
            try:
                tmp.unlink()
            except OSError:
                pass
            print(f"{path}: not written ({type(e).__name__}); save this entry there:\n")
            print(dump_record({name: entry}))
    print(report_line(name, entry))
    print("\n".join(owner_lines(entry, kind)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
