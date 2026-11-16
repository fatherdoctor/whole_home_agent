#!/usr/bin/env python3
"""first_look.py - the first look at an existing house: twelve read-only checks, written to house/docs/first-look.md.

Status: template (KIT-EXIST.b2, 2026-10-31). Copied to house/export/first_look.py beside export_house.py by Phase 0E
(AGENTS.md, "Phase 0E - an existing house", step 4; existing-house.md, "What to expect" 4). Standard library only.

    python3 house/export/first_look.py [--export house/export] [--out house/docs] [--config <configuration folder>]
        [--profile house/profile.yaml] [--inventory]
    python3 house/export/first_look.py --offline <folder> [--config <dir>] [--out <dir>] [--inventory]

Run it after export_house.py: it reads the export's twelve files, and for what the export does not keep it reads
the box itself (the same confirmed target and file-first credential reader as the export): the states now and
the last 24 hours of history for what is down (check 1), the error log and the saved
traces (check 2), each automation's and script's definition (checks 8 and 12: automations.yaml and scripts.yaml
first, the config GET for each one they do not hold; what neither reads is a `partial` note on both checks), and
the current stable versions (check 6, https://version.home-assistant.io/stable.json, only when the box's own update
entities are missing).
Every read is a GET, a read-only websocket command or a file read. Nothing on the box is changed.

--config <dir>  a copy of the configuration folder (the app reads /homeassistant itself): automations.yaml,
                scripts.yaml, blueprints/, configuration.yaml, packages/ and .storage/trace.saved_traces. Checks 10
                and 11 need it; from a computer without it they answer `unknown` / `ask` and say so.
--offline <dir> no network at all: the export's files from <dir>, and <dir>/live.json for the live reads
                ({"now", "mode", "states", "history", "error_log", "traces", "stable", "automation_configs",
                "script_configs"}; any may be missing, and a missing read answers `unknown`). For tests and dry runs.
--inventory     also write house/docs/inventory.md (the human read of the export, templates/docs/inventory.md).

Each finding has a kind in the words of principles/health-checks.md - fault, risk, notice - the evidence, the rule
it comes from and the offer (a tidy-up row, a level 0 or level 1 row, or "no action"). A check that cannot read its
source answers `unknown` with what would let it read; it never answers "nothing found". The output never holds a
secret (no error or trace text, no value from a YAML line, no user's name - files, lines, ids and counts only).
Exit 0 when it wrote the page (findings are not a failure); 2 when the export is missing.
"""
import argparse
import importlib.util
import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = pathlib.Path(__file__).resolve().parent
STABLE_URL = "https://version.home-assistant.io/stable.json"
BAD = ("unavailable", "unknown")
HISTORY_CHUNK = 50  # entity ids per history query (KIT-EXIST.b2r L1)
# Domains whose resting state is `unknown` (never activated, pressed or fired): only `unavailable` counts for them.
UNKNOWN_AT_REST = {"scene", "button", "input_button", "event", "notify", "image", "tts", "stt", "conversation",
                   "wake_word", "text", "date", "time", "datetime"}
SAFETY_DOMAINS = {"alarm_control_panel", "lock", "alarmo", "keymaster"}
CODE_SERVICE = r"[a-z0-9_]+\.\w*(?:user_?code|set_code|clear_code|set_pin|clear_pin)\w*"
CODE_SERVICE_PATTERN = re.compile(rf"^{CODE_SERVICE}$")
SAFETY_SERVICE = re.compile(rf"^(?:alarm_control_panel\.alarm_(?:arm|disarm|trigger)\w*|lock\.(?:lock|unlock|open)|"
                            rf"alarmo\.\w+|{CODE_SERVICE})$")
NOTIFY_EXEMPT = {"notify.persistent_notification"}
CHECKS = {  # number: (title, kind when it finds something, rule)
    1: ("Entities unavailable or unknown for more than a day", "fault", "principles/health-checks.md rule 3"),
    2: ("Automations that failed recently", "fault", "principles/health-checks.md rule 6"),
    3: ("Automations off, or never run", "notice", "principles/health-checks.md rule 4"),
    4: ("Backups: none in 7 days, none off the box, not encrypted", "risk", "levels.md L0-backup-week, L0-done-when"),
    5: ("Logins: multi-factor, administrators, old tokens", "risk", "principles/safety-and-security.md"),
    6: ("Core, OS or Supervisor behind the current stable", "notice", "principles/updates.md"),
    7: ("Apps: auto-update in a freeze, stopped with start on boot", "notice", "principles/updates.md"),
    8: ("Direct notify calls outside one router", "notice", "check H1-no-direct-notify"),
    9: ("No area, duplicate names, ids ending in _2", "notice", "principles/naming.md rules 5 and 7"),
    10: ("Secrets in YAML outside secrets.yaml", "risk", "principles/safety-and-security.md; the push guard"),
    11: ("An existing public exposure", "risk", "principles/safety-and-security.md"),
    12: ("Safety-list actions already automated", "risk", "principles/safety-and-security.md (safety)"),
}


# ---------------------------------------------------------------- small helpers
def when(v):
    if not v:
        return None
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v or "")))


def finding(check, evidence, offer, items=(), kind=None, title=None, safety=False):
    t, k, rule = CHECKS[check]
    return {"check": check, "kind": kind or k, "title": title or t, "evidence": evidence, "rule": rule,
            "offer": offer, "items": sorted(items), "safety": safety}


def result(check, findings=(), status=None, why=None, ask=None, note=None):
    """One check's answer: status is `findings`, `clean`, `unknown` (with why: what would let it read) or `ask`."""
    status = status or ("findings" if findings else "clean")
    return {"check": check, "title": CHECKS[check][0], "status": status, "findings": list(findings),
            "why": why, "ask": ask, "note": note}


def is_unknown(doc):
    return not isinstance(doc, (dict, list)) or (isinstance(doc, dict) and doc.get("status") == "unknown")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- definitions: what each automation and script calls
CALL = re.compile(r"(?<![\w-])(?:service|action)\s*:\s*['\"]?([a-z0-9_]+\.[a-z0-9_]+)")
ENTITY_SCRIPT = re.compile(r"\bscript\.([a-z0-9_]+)\b")
FIELD = re.compile(r"^\s*(?:-\s*)?(id|alias)\s*:\s*['\"]?([^'\"#\n]+?)['\"]?\s*(?:#.*)?$")
BLUEPRINT_PATH = re.compile(r"^\s*path\s*:\s*['\"]?([^'\"#\s]+)")


def _summary(calls, scripts, blueprint=None):
    """calls: every domain.service named; scripts: the scripts it runs (by object id)."""
    return {"calls": sorted(set(calls)), "scripts": sorted(set(scripts)), "blueprint": blueprint}


def _script_refs(calls, texts):
    verbs = ("turn_on", "turn_off", "toggle", "reload")
    out = [c.split(".", 1)[1] for c in calls if c.startswith("script.") and c.split(".", 1)[1] not in verbs]
    if any(c in ("script.turn_on", "script.toggle") for c in calls):
        for t in texts:
            out += [n for n in ENTITY_SCRIPT.findall(t) if n not in verbs]
    return out


def parse_automations_yaml(text):
    """{config id: summary} from automations.yaml: the top-level list split at each `- ` in column 0. Not a YAML
    parser: it reads only the service names, the `script.*` targets, the id and the blueprint path."""
    blocks, cur = [], []
    for line in text.splitlines():
        if line.startswith("- ") and cur:
            blocks.append(cur)
            cur = []
        if line.startswith("- ") or cur:
            cur.append(line)
    if cur:
        blocks.append(cur)
    out = {}
    for b in blocks:
        ident = alias = bp = None
        in_bp = False
        for line in b:
            bare = line.split(" #", 1)[0]
            m = FIELD.match(bare)
            if m and m.group(1) == "id" and ident is None:
                ident = m.group(2).strip()
            elif m and m.group(1) == "alias" and alias is None:
                alias = m.group(2).strip()
            if re.match(r"^\s*(?:-\s*)?use_blueprint\s*:", bare):
                in_bp = True
            elif in_bp and BLUEPRINT_PATH.match(bare):
                bp, in_bp = BLUEPRINT_PATH.match(bare).group(1), False
        body = [ln.split(" #", 1)[0] for ln in b]
        calls = [c for ln in body for c in CALL.findall(ln)]
        out[ident or alias or f"(unnamed {len(out) + 1})"] = _summary(calls, _script_refs(calls, body), bp)
    return out


def parse_scripts_yaml(text):
    """{object id: summary} from scripts.yaml: one block per top-level key."""
    out, name, body = {}, None, []
    for line in text.splitlines() + ["__end__:"]:
        m = re.match(r"^([a-z0-9_]+)\s*:\s*(?:#.*)?$", line)
        if m:
            if name:
                calls = [c for ln in body for c in CALL.findall(ln)]
                out[name] = _summary(calls, _script_refs(calls, body))
            name, body = m.group(1), []
        elif name:
            body.append(line.split(" #", 1)[0])
    return out


def summarize_config(cfg):
    """The same summary from a JSON definition (GET /api/config/<domain>/config/<id>)."""
    calls, texts = [], []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("service", "action") and isinstance(v, str) and re.fullmatch(r"[a-z0-9_]+\.[a-z0-9_]+", v):
                    calls.append(v)
                elif k == "entity_id":
                    texts.append(json.dumps(v))
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(cfg)
    bp = ((cfg or {}).get("use_blueprint") or {}).get("path") if isinstance(cfg, dict) else None
    return _summary(calls, _script_refs(calls, texts), bp)


def blueprint_calls(config_dir, path):
    if not config_dir or not path:
        return None
    f = pathlib.Path(config_dir) / "blueprints" / "automation" / path
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:
        return None
    return sorted(set(c for ln in text.splitlines() for c in CALL.findall(ln.split(" #", 1)[0])))


# ---------------------------------------------------------------- the twelve checks
def check_down(ctx):
    states, ents = ctx.get("states"), ctx["export"].get("entities.json") or []
    if states is None:
        return result(1, status="unknown", why="the states could not be read (HA_URL and HA_TOKEN, or live.json)")
    info = {e["entity_id"]: e for e in ents if isinstance(e, dict)}
    now, since = ctx["now"], ctx["now"] - timedelta(hours=24)
    cands = [s for s in states if s.get("state") == "unavailable" or
             (s.get("state") == "unknown" and s["entity_id"].split(".", 1)[0] not in UNKNOWN_AT_REST)]
    history = ctx.get("history")
    down = []
    for s in cands:
        rows = (history or {}).get(s["entity_id"])
        if rows:  # the whole window down: every record in the last 24 hours is unavailable or unknown
            if all(r.get("state") in BAD for r in rows) and (when(rows[0].get("last_changed")) or now) <= since + \
                    timedelta(minutes=5):
                down.append(s)
        elif (when(s.get("last_changed")) or now) <= since:
            down.append(s)
    groups = {}
    for s in down:
        e = info.get(s["entity_id"], {})
        key = (e.get("integration") or "no integration recorded", e.get("device_name") or "no device")
        groups.setdefault(key, []).append(s["entity_id"])
    out = [finding(1, f"{len(ids)} entit{'y' if len(ids) == 1 else 'ies'} of {integ} / {dev} down for the whole of "
                      f"the last 24 hours", "a tidy-up row for that device or integration", ids)
           for (integ, dev), ids in sorted(groups.items())]
    note = None if history is not None else "no history read: judged by last_changed alone (a restart resets it)"
    return result(1, out, note=note)


def check_failed(ctx):
    autos = [a for a in ctx["export"].get("automations.json") or [] if a["entity_id"].startswith("automation.")]
    by_id = {str(a.get("id")): a["entity_id"] for a in autos if a.get("id")}
    known = {a["entity_id"] for a in autos}
    hits, read = {}, []
    traces = ctx.get("traces")
    if traces is not None:
        read.append("saved traces")
        for t in traces:
            if t.get("error"):
                key = str(t.get("automation", "")).split(".", 1)[-1]
                e = by_id.get(key) or f"automation.{key}"
                hits.setdefault(e, set()).add("its saved trace ended in error")
    log = ctx.get("error_log")
    if log is not None:
        read.append("error log")
        for line in log.splitlines():
            if not re.search(r"\b(ERROR|CRITICAL)\b|Error while executing", line):
                continue
            for oid in set(re.findall(r"automation\.([a-z0-9_]+)", line)):
                e = by_id.get(oid) or f"automation.{oid}"
                if e in known:
                    hits.setdefault(e, set()).add("the error log names it")
    if not read:
        return result(2, status="unknown", why="neither the error log nor the traces could be read "
                                               "(an administrator's token; the app or --config for the traces)")
    out = [finding(2, f"{e}: {'; '.join(sorted(why))}", f"a tidy-up row for {e}", [e])
           for e, why in sorted(hits.items())]
    return result(2, out, note="read: " + ", ".join(read))


def check_idle(ctx):
    autos = [a for a in ctx["export"].get("automations.json") or [] if a["entity_id"].startswith("automation.")]
    off = [a["entity_id"] for a in autos if a.get("enabled") is False]
    never = [a["entity_id"] for a in autos if a.get("enabled") is not False and "last_triggered" in a
             and not a.get("last_triggered")]
    if autos and not any("last_triggered" in a for a in autos):
        return result(3, [finding(3, f"{len(off)} off", "keep, fix or delete? (one row)", off)] if off else [],
                      status="findings" if off else "unknown", why="the export has no last_triggered (run it "
                      "without --basic)")
    out = []
    if off or never:
        parts = ([f"{len(off)} off"] if off else []) + ([f"{len(never)} never ran"] if never else [])
        out.append(finding(3, ", ".join(parts), "keep, fix or delete? per item, in one tidy-up row", off + never))
    # Home Assistant keeps no creation date for an automation, so "never ran" stands on its own (KIT-EXIST.b2's
    # answer to the lived-in key's open question 1); a person who just wrote one says "leave it".
    return result(3, out, note="never ran: Home Assistant keeps no creation date, so the 30-day age is not tested")


def check_backups(ctx):
    doc = ctx["export"].get("backups.json")
    if is_unknown(doc):
        return result(4, status="unknown", why=(doc or {}).get("why", "backups.json is missing"),
                      ask=(doc or {}).get("ask"))
    rows = [b for b in doc.get("backups") or [] if isinstance(b, dict)]
    settings = doc.get("settings") if isinstance(doc.get("settings"), dict) else {}
    out, now = [], ctx["now"]
    dates = sorted(d for d in (when(b.get("date")) for b in rows) if d)
    if not dates:
        out.append(finding(4, "no backup at all", "a level 0 row (L0-backup-week): stays listed until done",
                           title="No backup"))
    elif now - dates[-1] > timedelta(days=7):
        out.append(finding(4, f"the newest backup is {(now - dates[-1]).days} days old", "a level 0 row "
                           "(L0-backup-week): stays listed until done", title="No backup in the last 7 days"))
    places = {p for b in rows for p in b.get("locations") or []}
    if settings.get("status") != "unknown":
        places |= set(settings.get("locations") or [])
    if dates and not places - {"local"}:
        out.append(finding(4, "every backup and the backup settings name the box itself only (local)",
                           "a level 0 row (L0-done-when): stays listed until done", title="No backup off the box"))
    if settings.get("status") != "unknown" and "encrypted" in settings:
        if settings.get("encrypted") is False:
            out.append(finding(4, "the backup settings have no encryption key", "a level 0 row",
                               title="Backups not encrypted"))
    elif rows and not rows[-1].get("protected"):
        out.append(finding(4, "the newest backup is not protected (settings not read)", "a level 0 row",
                           title="Backups not encrypted"))
    return result(4, out)


def check_logins(ctx):
    doc = ctx["export"].get("users.json")
    ask = "the owner alone: does your own login use a second factor? (recorded as source: person)"
    if is_unknown(doc):
        return result(5, status="unknown", ask=ask, why="from a computer there is no source for other users' "
                      "multi-factor state or token ages: the app, or --config with a copy of the configuration "
                      "folder and its .storage/, given to export_house.py, would let it read")
    out = []
    owner = doc.get("owner") or {}
    if owner.get("administrator") and owner.get("mfa") is False:
        out.append(finding(5, "the owner's login has no multi-factor module entry", "a level 0 row",
                           title="Multi-factor login off for the owner"))
    others = doc.get("other_administrators") or {}
    if others.get("count"):
        missing = others["count"] - (others.get("with_mfa") or 0)
        out.append(finding(5, f"{doc.get('administrators')} administrators (the owner and {others['count']} more)",
                           "a level 0 row: keep, or make the others ordinary users",
                           title="More than one administrator"))
        if missing:
            out.append(finding(5, f"{missing} other administrator(s) without multi-factor login", "a level 0 row",
                               title="Multi-factor login off for an administrator"))
    tokens = doc.get("long_lived_tokens") or {}
    if (tokens.get("oldest_days") or 0) > 365:
        out.append(finding(5, f"the oldest of {tokens.get('count')} long-lived tokens is {tokens['oldest_days']} "
                              "days old", "a level 0 row: replace or delete it", title="A long-lived token older "
                              "than a year"))
    return result(5, out)


def check_versions(ctx):
    meta = ctx["export"].get("meta.json") or {}
    versions = dict(meta.get("versions") or {})
    stable = ctx.get("stable")
    if stable:
        latest = {"core": (stable.get("homeassistant") or {}).get("default"), "supervisor": stable.get("supervisor"),
                  "os": (stable.get("hassos") or {}).get("ova")}
        for k, v in latest.items():
            if v and not (versions.get(k) or {}).get("latest"):
                installed = (versions.get(k) or {}).get("installed") or (meta.get("version") if k == "core" else None)
                if installed:
                    versions[k] = {"installed": installed, "latest": v}
    if not any((v or {}).get("latest") for v in versions.values()):
        return result(6, status="unknown", why="no update entities in the export and the stable versions could not "
                                               "be fetched (" + STABLE_URL + ")")
    behind = [f"{k} {v['installed']} (stable {v['latest']})" for k, v in sorted(versions.items())
              if v and v.get("installed") and v.get("latest")
              and version_tuple(v["installed"]) < version_tuple(v["latest"])]
    out = [finding(6, "; ".join(behind), "one row, under principles/updates.md", [b.split()[0] for b in behind])] \
        if behind else []
    return result(6, out)


def freezes(profile_path, now):
    """profile.operations.freezes: [{from: date, to: date, why: ...}]; True when now is inside one."""
    try:
        text = pathlib.Path(profile_path).read_text(encoding="utf-8")
    except (OSError, TypeError):
        return None
    m = re.search(r"^\s*freezes\s*:(.*?)(?=^\s*[a-z_]+\s*:(?!\s*\d)|\Z)", text, re.M | re.S)
    if not m:
        return False
    for a, b in re.findall(r"from\s*:\s*(\d{4}-\d{2}-\d{2}).*?to\s*:\s*(\d{4}-\d{2}-\d{2})", m.group(1), re.S):
        if a <= now.date().isoformat() <= b:
            return True
    return False


def check_addons(ctx):
    doc = ctx["export"].get("addons.json")
    if is_unknown(doc):
        return result(7, status="unknown", why=(doc or {}).get("why", "addons.json is missing"),
                      ask=(doc or {}).get("ask"))
    rows = doc.get("addons") or []
    frozen = freezes(ctx.get("profile"), ctx["now"])
    out = []
    if frozen:
        auto = [a["slug"] for a in rows if a.get("auto_update")]
        if auto:
            out.append(finding(7, f"{len(auto)} app(s) auto-update during the declared freeze", "one row", auto,
                               title="Apps auto-updating during a freeze"))
    stopped = [a["slug"] for a in rows if a.get("boot") == "auto" and a.get("running") is False]
    if stopped:
        out.append(finding(7, f"{len(stopped)} app(s) stopped although they start on boot", "one row", stopped,
                           title="Apps stopped with start on boot"))
    note = None if frozen is not None else "no profile read: freezes not checked"
    return result(7, out, note=note)


def check_notify(ctx):
    defs = ctx.get("definitions")
    if defs is None:
        return result(8, status="unknown", why="the automations' definitions could not be read (the app, "
                      "--config with automations.yaml, or an administrator's token)")
    direct = sorted(e for e, d in defs["automations"].items()
                    if any(c.startswith("notify.") and c not in NOTIFY_EXEMPT for c in d["calls"]))
    senders = sorted(s for s, d in defs["scripts"].items()
                     if any(c.startswith("notify.") and c not in NOTIFY_EXEMPT for c in d["calls"]))
    items = direct + ([f"script.{s}" for s in senders] if len(senders) > 1 else [])
    note = unread_note(defs, scripts=True)
    if not items:
        return result(8, note=note)
    ev = f"{len(direct)} automation(s) call notify.* directly" + (
        f"; {len(senders)} scripts send, so no single router" if len(senders) > 1 else "")
    return result(8, [finding(8, ev, "one row: \"a router, when you want one\"", items)], note=note)


def check_names(ctx):
    ents = [e for e in ctx["export"].get("entities.json") or [] if isinstance(e, dict)]
    out = []
    no_area = [e["entity_id"] for e in ents if e.get("device") and not e.get("area")]
    if no_area:
        out.append(finding(9, f"{len(no_area)} device-backed entit{'y' if len(no_area) == 1 else 'ies'} with no "
                              "area", "one tidy-up row for areas", no_area, title="Things with no area"))
    names = {}
    for e in ents:
        names.setdefault(str(e.get("name") or "").strip().lower(), []).append(e["entity_id"])
    dups = sorted(i for n, ids in names.items() if n and len(ids) > 1 for i in ids)
    suffix = sorted(e["entity_id"] for e in ents if re.search(r"_[2-9]$", e["entity_id"]))
    if dups or suffix:
        parts = ([f"{len(dups)} entities share a name"] if dups else []) + (
            [f"{len(suffix)} id(s) end in _2 or higher"] if suffix else [])
        out.append(finding(9, ", ".join(parts), "one tidy-up row for duplicates", set(dups) | set(suffix),
                           title="Duplicate names and ids ending in _2"))
    return result(9, out)


def guard_shapes():
    for p in (HERE.parent / "guard" / "push_guard.py", HERE.parents[1] / "guard" / "push_guard.py"):
        if p.is_file():
            g = load_module(p, "push_guard")
            return [(n, rx) for n, rx in g.SHAPES if n != "phone"], g.ALLOW
    return None, None


def check_secrets(ctx):
    cfg = ctx.get("config_dir")
    if not cfg:
        return result(10, status="unknown", why="from a computer there is no file access: the app, or the "
                      "person's copy of the configuration folder given to first_look.py --config <dir>, would let "
                      "it read")
    shapes, allow = guard_shapes()
    if shapes is None:
        return result(10, status="unknown", why="the push guard is not installed (guard/push_guard.py): its "
                                                "patterns are the check")
    root = pathlib.Path(cfg)
    files = sorted(set(root.glob("*.yaml")) | set((root / "packages").rglob("*.yaml")))
    hits = []
    for f in files:
        if f.name == "secrets.yaml":
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            if allow in line:
                continue
            kinds = []  # the guard has several shapes per kind: one hit per kind per line
            for kind, rx in shapes:
                if kind not in kinds and rx.search(line):
                    kinds.append(kind)
                    hits.append(f"{f.relative_to(root).as_posix()}:{n} ({kind})")
    if not hits:
        return result(10, note=f"{len(files)} YAML files read")
    return result(10, [finding(10, f"{len(hits)} line(s) hold a value shaped like a secret (the value is not "
                                   "shown)", "a level 1 row: move each to secrets.yaml; stays listed until done",
                               hits)])


def check_exposure(ctx):
    ask = "Can the box be reached from outside the house: a port forward on the router, a reverse proxy, Nabu Casa?"
    cfg = ctx.get("config_dir")
    if not cfg:
        return result(11, status="ask", ask=ask, why="configuration.yaml not read (the app, or --config)")
    try:
        text = (pathlib.Path(cfg) / "configuration.yaml").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return result(11, status="ask", ask=ask, why="configuration.yaml not found in --config")
    text = "\n".join(ln.split(" #", 1)[0] for ln in text.splitlines())
    out = []
    if re.search(r"type\s*:\s*trusted_networks", text):
        if re.search(r"allow_bypass_login\s*:\s*true", text, re.I):
            out.append(finding(11, "auth_providers: trusted_networks with allow_bypass_login: true",
                               "a level 1 row, and the question", title="trusted_networks without a password"))
        if not re.search(r"type\s*:\s*homeassistant", text):
            out.append(finding(11, "auth_providers: trusted_networks without the homeassistant provider beside it",
                               "a level 1 row, and the question", title="trusted_networks as the only login"))
    proxy = bool(re.search(r"use_x_forwarded_for\s*:\s*true", text, re.I))
    note = "a reverse proxy is configured (use_x_forwarded_for): ask whether it has a login" if proxy else None
    return result(11, out, status=None if out else "ask", ask=ask, note=note)


def check_safety(ctx):
    defs = ctx.get("definitions")
    if defs is None:
        return result(12, status="unknown", why="the automations' definitions could not be read (the app, "
                      "--config with automations.yaml, or an administrator's token)")
    scripts, out, partial = defs["scripts"], [], []
    has_code_change = False
    for e, d in sorted(defs["automations"].items()):
        why = [c for c in d["calls"] if SAFETY_SERVICE.match(c)]
        for s in d["scripts"]:  # one level into a script.* call
            why += [f"{c} via script.{s}" for c in (scripts.get(s) or {}).get("calls", []) if SAFETY_SERVICE.match(c)]
            if s not in scripts:
                partial.append(f"script.{s} (called by {e}) not read")
        if d.get("blueprint"):
            calls = blueprint_calls(ctx.get("config_dir"), d["blueprint"])
            if calls is None:
                partial.append(f"blueprint {d['blueprint']} (used by {e}) not read")
            why += [f"{c} via blueprint {d['blueprint']}" for c in calls or [] if SAFETY_SERVICE.match(c)]
        if why:
            has_code_change |= any(CODE_SERVICE_PATTERN.match(call.split(" via ", 1)[0]) for call in why)
            out.append(finding(12, f"{e}: {', '.join(sorted(set(why)))}, automated (no confirmation step read)",
                               "a safety row in the backlog's tidy-up section, or a line in policies.md, "
                               "\"Where this house differs\"", [e],
                               safety=True))
    unread = unread_note(defs)
    partial = ([unread] if unread else []) + partial
    note = "; ".join(partial) if partial else None
    if has_code_change:
        note = ((note + "; ") if note else "") + ("ask whether a code window was set by a person; "
                                                    "a person-set code window counts as that person's act")
    note = ((note + "; ") if note else "") + "who receives each notification is confirmed in Phase 1 (the phones)"
    return result(12, out, note=note)


CHECK_FUNCS = (check_down, check_failed, check_idle, check_backups, check_logins, check_versions, check_addons,
               check_notify, check_names, check_secrets, check_exposure, check_safety)


def run_checks(ctx):
    return [f(ctx) for f in CHECK_FUNCS]


# ---------------------------------------------------------------- gathering the inputs
def load_export(folder):
    out = {}
    for f in sorted(pathlib.Path(folder).glob("*.json")):
        if f.name == "live.json":
            continue
        try:
            out[f.name] = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            out[f.name] = {"status": "unknown", "why": f"{f.name} is not valid JSON"}
    return out


def file_definitions(export, config_dir):
    """What automations.yaml and scripts.yaml yield: ({config id: summary}, {object id: summary}, why) or None when
    there is no automations.yaml. A file that parses as fewer than two blocks while it holds indented `- id:` lines
    and the export has more than one automation (a hand-indented list) is not trusted: its automations come back
    empty, with why, so the API reads them."""
    a_path = pathlib.Path(config_dir) / "automations.yaml" if config_dir else None
    if not (a_path and a_path.is_file()):
        return None
    text = a_path.read_text(encoding="utf-8", errors="replace")
    parsed = parse_automations_yaml(text)
    n = sum(1 for a in export.get("automations.json") or [] if a["entity_id"].startswith("automation."))
    indented = len(re.findall(r"(?m)^[ \t]+- (?:id|alias)\s*:", text))
    why = None
    if len(parsed) < 2 and n > 1 and indented > 1:
        parsed, why = {}, "automations.yaml read as one block (indented list?): definitions read from the API"
    s_path = pathlib.Path(config_dir) / "scripts.yaml"
    scripts = parse_scripts_yaml(s_path.read_text(encoding="utf-8", errors="replace")) if s_path.is_file() else {}
    return parsed, scripts, why


def definitions(export, config_dir=None, auto_cfgs=None, script_cfgs=None):
    """{"automations": {entity_id: summary}, "scripts": {object id: summary}, "source": ..., "unread": {...}} or None.
    The files first, then the config GETs for whatever the files did not hold (a package, another include); what
    neither read is counted in "unread" so checks 8 and 12 say so instead of "nothing found"."""
    exported = export.get("automations.json") or []
    autos = [a for a in exported if a["entity_id"].startswith("automation.")]
    script_ids = sorted(a["entity_id"].split(".", 1)[1] for a in exported if a["entity_id"].startswith("script."))
    id_to_entity = {str(a.get("id")): a["entity_id"] for a in autos if a.get("id")}
    files = file_definitions(export, config_dir)
    if files is None and auto_cfgs is None:
        return None
    parsed, scripts, why = files if files is not None else ({}, {}, None)
    out = {id_to_entity.get(k, f"automation.{k}"): v for k, v in parsed.items()}
    for k, v in (auto_cfgs or {}).items():
        out.setdefault(id_to_entity.get(k, f"automation.{k}"), summarize_config(v))
    scripts = dict(scripts)
    for k, v in (script_cfgs or {}).items():
        scripts.setdefault(k, summarize_config(v))
    unread = {"automations": sorted(a["entity_id"] for a in autos if a["entity_id"] not in out),
              "scripts": [k for k in script_ids if k not in scripts]}
    source = "files" if files is not None and not auto_cfgs else "api" if files is None else "files+api"
    return {"source": source, "automations": out, "scripts": scripts, "unread": unread, "why": why}


def unread_note(defs, scripts=False):
    """The `partial` note for checks 8 and 12: how many definitions neither the files nor the API read."""
    u = defs.get("unread") or {}
    na, ns = len(u.get("automations") or []), len(u.get("scripts") or []) if scripts else 0
    if not (na or ns):
        return defs.get("why")
    where = "outside automations.yaml " if defs.get("source", "").startswith("files") and not defs.get("why") else ""
    parts = ([f"{na} automation(s) {where}not read"] if na else []) + (
        [f"{ns} script(s) {'outside scripts.yaml ' if where else ''}not read"] if ns else [])
    return "partial: " + ", ".join(parts) + (f" ({defs['why']})" if defs.get("why") else "")


def history_by_entity(raw):
    """GET /api/history/period's list of lists -> {entity_id: [rows]}; tolerates the already-keyed shape."""
    if isinstance(raw, dict):
        return raw
    out = {}
    for series in raw or []:
        if series and isinstance(series, list):
            eid = series[0].get("entity_id")
            out[eid] = series
    return out


def gather_live(export, base, token, config_dir, mode, now):
    """The live reads, each its own try: a failed read is None (the check then answers unknown)."""
    exp = load_module(HERE / "export_house.py", "export_house")
    fetch = exp.http_fetch(base, token)
    live = {"now": now, "mode": mode}

    def attempt(fn):
        try:
            return fn()
        except (exp.ReadError, OSError, ValueError):
            return None

    live["states"] = attempt(lambda: fetch("GET", "/api/states"))
    bad = [s["entity_id"] for s in live["states"] or [] if s.get("state") in BAD]
    if bad:
        start = urllib.parse.quote((now - timedelta(hours=24)).isoformat(timespec="seconds"))
        hist = {}
        for i in range(0, len(bad), HISTORY_CHUNK):  # fifty ids a query: a dead hub can outgrow the URL limit
            q = (f"/api/history/period/{start}?filter_entity_id={','.join(bad[i:i + HISTORY_CHUNK])}"
                 "&minimal_response&no_attributes")
            part = attempt(lambda: history_by_entity(fetch("GET", q)))
            if part is None:
                hist = None  # one failed read: the check falls back to last_changed, and says so
                break
            hist.update(part)
        live["history"] = hist
    else:
        live["history"] = {}

    def error_log():
        req = urllib.request.Request(base.rstrip("/") + "/api/error_log", headers={"Authorization": "Bearer " + token})
        with exp.OPENER.open(req, timeout=60) as r:  # no redirect: the token stays with this host
            return r.read().decode(errors="replace")

    live["error_log"] = attempt(error_log)
    if config_dir and (pathlib.Path(config_dir) / ".storage").is_dir():
        live["traces"] = attempt(lambda: exp.trace_errors(exp.storage_reader(config_dir)))
    else:
        def ws_traces():
            ws = exp.lazy_ws(base, token)
            rows = ws({"type": "trace/list", "domain": "automation"}) or []
            return [{"automation": f"automation.{r.get('item_id')}",
                     "error": r.get("script_execution") == "error" or bool(r.get("error"))} for r in rows]
        live["traces"] = attempt(ws_traces)
    files = file_definitions(export, config_dir)
    in_files, scripts_in_files = (set(files[0]), set(files[1])) if files else (set(), set())
    cfgs = {}
    for a in export.get("automations.json") or []:  # each exported automation the files did not yield
        if a["entity_id"].startswith("automation.") and a.get("id") and str(a["id"]) not in in_files:
            c = attempt(lambda: fetch("GET", "/api/config/automation/config/" + urllib.parse.quote(str(a["id"]),
                                                                                                     safe="")))
            if isinstance(c, dict):
                cfgs[str(a["id"])] = c
    scfgs = {}
    for s in export.get("automations.json") or []:  # and each script not in scripts.yaml
        if s["entity_id"].startswith("script.") and s["entity_id"].split(".", 1)[1] not in scripts_in_files:
            oid = s["entity_id"].split(".", 1)[1]
            c = attempt(lambda: fetch("GET", f"/api/config/script/config/{oid}"))
            if isinstance(c, dict):
                scfgs[oid] = c
    live["automation_configs"] = cfgs or (None if files is None else {})
    live["script_configs"] = scfgs
    if not any((v or {}).get("latest") for v in ((export.get("meta.json") or {}).get("versions") or {}).values()):
        def stable():
            with urllib.request.urlopen(STABLE_URL, timeout=30) as r:
                return json.loads(r.read().decode())
        live["stable"] = attempt(stable)
    return live


def context(export, live, config_dir=None, profile=None):
    now = live.get("now")
    now = when(now) if isinstance(now, str) else (now or datetime.now(timezone.utc))
    traces = live.get("traces")
    if traces is None and config_dir and (pathlib.Path(config_dir) / ".storage").is_dir():
        exp = load_module(HERE / "export_house.py", "export_house")  # the whitelisted reader: id and error only
        try:
            traces = exp.trace_errors(exp.storage_reader(config_dir))
        except exp.ReadError:
            traces = None
    return {"export": export, "now": now, "mode": live.get("mode") or (export.get("meta.json") or {}).get("mode"),
            "states": live.get("states"), "history": history_by_entity(live["history"]) if "history" in live else None,
            "error_log": live.get("error_log"), "traces": traces, "stable": live.get("stable"),
            "config_dir": config_dir, "profile": profile,
            "definitions": definitions(export, config_dir, live.get("automation_configs"), live.get("script_configs"))}


# ---------------------------------------------------------------- the two pages
def _template(name, fallback):
    for p in (HERE.parent / "docs" / name, HERE.parents[1] / "docs" / name):
        if p.is_file():
            return p.read_text(encoding="utf-8")
    return fallback


def _cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def render_first_look(results, ctx):
    findings = [f for r in results for f in r["findings"]]
    counts = {k: sum(1 for f in findings if f["kind"] == k) for k in ("fault", "risk", "notice")}
    order = {"risk": 0, "fault": 1, "notice": 2}
    top = sorted(findings, key=lambda f: (not f["safety"], order[f["kind"]], f["check"]))[:3]
    unknowns = [r for r in results if r["status"] == "unknown"]
    summary = (f"{counts['fault']} fault(s), {counts['risk']} risk(s) and {counts['notice']} notice(s)"
               + (f"; {len(unknowns)} check(s) could not read their source ("
                  + ", ".join(str(r["check"]) for r in unknowns) + ")" if unknowns else "")
               + ". " + (("The ones that matter most: " + "; ".join(f["title"].lower() + (" (safety)" if f["safety"]
                          else "") for f in top) + ". ") if top else "")
               + "Nothing has been changed on the box. Each line is an offer; \"leave it\" is an answer to any "
                 "of them.")
    rows = ["| # | Kind | Check | Finding | Evidence | Rule | Offer |", "|---|---|---|---|---|---|---|"]
    for i, f in enumerate(sorted(findings, key=lambda f: (f["check"], f["title"])), 1):
        ev, items = f["evidence"], f["items"]
        if items and not all(x in ev for x in items):  # the items, unless the evidence already names them all
            ev += ": " + ", ".join(items[:12]) + (", ..." if len(items) > 12 else "")
        kind = f["kind"] + (" (safety)" if f["safety"] else "")
        rows.append("| " + " | ".join(_cell(x) for x in (i, kind, f["check"], f["title"], ev, f["rule"], f["offer"]))
                    + " |")
    if not findings:
        rows.append("| - | - | - | nothing found by a check that could read | - | - | - |")
    checks = ["| Check | Result | Note |", "|---|---|---|"]
    for r in results:
        res = {"findings": f"{len(r['findings'])} finding(s)", "clean": "nothing found", "unknown": "unknown",
               "ask": "a question"}[r["status"]]
        note = "; ".join(x for x in (r.get("why"), ("ask: " + r["ask"]) if r.get("ask") else None, r.get("note")) if x)
        checks.append(f"| {r['check']}. {_cell(r['title'])} | {res} | {_cell(note) or '-'} |")
    text = _template("first-look.md", FIRST_LOOK_FALLBACK)
    text = re.sub(r"<!--.*?-->\n?", "", text, flags=re.S)
    return (text.replace("{{date}}", ctx["now"].date().isoformat()).replace("{{mode}}", str(ctx.get("mode") or "-"))
            .replace("{{summary}}", summary).replace("{{findings}}", "\n".join(rows))
            .replace("{{checks}}", "\n".join(checks)))


FIRST_LOOK_FALLBACK = """# First look ({{date}})

Read-only; read from: {{mode}}. Nothing on the box was changed.

{{summary}}

## Findings

{{findings}}

## The twelve checks

{{checks}}
"""

NAME_PATTERNS = (("Category - Target", re.compile(r"^\S.*\s-\s\S.*$")),
                 ("snake_case", re.compile(r"^[a-z0-9]+(_[a-z0-9]+)+$")),
                 ("a sentence", re.compile(r".")))


def naming_pattern(names):
    """(line, counts): the pattern the house uses most, when two in three names follow it; else no single one."""
    counts = {p: 0 for p, _ in NAME_PATTERNS}
    for n in names:
        for p, rx in NAME_PATTERNS:
            if rx.match(n or ""):
                counts[p] += 1
                break
    total = sum(counts.values())
    if not total:
        return "no automations or scripts", counts
    best = max(counts, key=counts.get)
    shares = ", ".join(f"{p} {c}" for p, c in counts.items() if c)
    if counts[best] * 3 >= total * 2:
        return f"most names follow `{best}` ({counts[best]} of {total}; {shares})", counts
    return f"no single pattern ({shares}, of {total})", counts


def render_inventory(export, ctx):
    ents = [e for e in export.get("entities.json") or [] if isinstance(e, dict)]
    areas = export.get("areas.json") or []
    by_area = {}
    for e in ents:
        by_area.setdefault(e.get("area"), []).append(e)
    area_rows = ["| Area | Floor | Devices | Entities |", "|---|---|---|---|"]
    for a in areas:
        es = by_area.get(a.get("area"), [])
        area_rows.append(f"| {_cell(a.get('name') or a.get('area'))} | {_cell(a.get('floor') or '-')} | "
                         f"{len({e['device'] for e in es if e.get('device')})} | {len(es)} |")
    no_area = [e["entity_id"] for e in ents if e.get("device") and not e.get("area")]
    integ = {}
    for e in ents:
        integ[e.get("integration") or "(none recorded)"] = integ.get(e.get("integration") or "(none recorded)", 0) + 1
    integ_rows = ["| Integration | Entities |", "|---|---|"] + [f"| {_cell(k)} | {v} |"
                                                                for k, v in sorted(integ.items())]
    autos = export.get("automations.json") or []
    a_names = [a.get("name") for a in autos if a["entity_id"].startswith("automation.")]
    s_names = [a.get("name") for a in autos if a["entity_id"].startswith("script.")]
    pattern, _ = naming_pattern(a_names + s_names)
    off = sum(1 for a in autos if a["entity_id"].startswith("automation.") and a.get("enabled") is False)
    dash = export.get("dashboards.json") or {}
    dash_line = ("unknown (" + dash.get("why", "not read") + ")" if is_unknown(dash) else
                 "; ".join(f"{d.get('title')} ({d.get('mode')}, {d.get('views')} views, {d.get('cards')} cards)"
                           for d in dash.get("dashboards") or []))
    addons = export.get("addons.json") or {}
    add_line = ("unknown (" + addons.get("why", "not read") + ")" if is_unknown(addons) else
                f"{len(addons.get('addons') or [])} apps, "
                f"{sum(1 for a in addons.get('addons') or [] if a.get('running'))} running")
    hacs = (addons.get("hacs") or {}).get("repositories") or []
    backups = export.get("backups.json") or {}
    b_line = ("unknown (" + backups.get("why", "not read") + ")" if is_unknown(backups) else
              f"{len(backups.get('backups') or [])} backups, the newest "
              f"{max((b.get('date') or '' for b in backups.get('backups') or []), default='-')[:10]}")
    users = export.get("users.json") or {}
    u_line = ("unknown (the app, or --config, reads it)" if is_unknown(users) else
              f"{users.get('users')} users, {users.get('administrators')} administrators, "
              f"{(users.get('long_lived_tokens') or {}).get('count')} long-lived tokens")
    helpers = (export.get("helpers.json") or {}).get("helpers") or []
    sc = export.get("scripts_scenes.json") or {}
    text = _template("inventory.md", INVENTORY_FALLBACK)
    text = re.sub(r"<!--.*?-->\n?", "", text, flags=re.S)
    subs = {
        "date": ctx["now"].date().isoformat(), "mode": str(ctx.get("mode") or "-"),
        "version": str((export.get("meta.json") or {}).get("version")),
        "counts": f"{len(ents)} entities, {len(areas)} areas, {len(integ)} integrations, {len(a_names)} automations "
                  f"({off} off), {len(sc.get('scripts') or s_names)} scripts, {len(sc.get('scenes') or [])} scenes, "
                  f"{len(helpers)} helpers",
        "areas": "\n".join(area_rows), "no_area": ", ".join(no_area) or "none",
        "integrations": "\n".join(integ_rows), "naming": pattern, "dashboards": dash_line or "none",
        "addons": add_line + (f"; legacy HACS: {len(hacs)} repositories" if hacs else "")
                  + "; Marketplace repositories not inventoried", "backups": b_line,
        "users": u_line,
    }
    for k, v in subs.items():
        text = text.replace("{{" + k + "}}", v)
    return text


INVENTORY_FALLBACK = """# Inventory ({{date}})

Home Assistant {{version}}; read from: {{mode}}. {{counts}}.

## By area
{{areas}}

Device-backed entities with no area: {{no_area}}

## By integration
{{integrations}}

## Automations and scripts
Naming: {{naming}}

## Dashboards, apps, backups, users
- Dashboards: {{dashboards}}
- Apps: {{addons}}
- Backups: {{backups}}
- Users: {{users}}
"""


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".", help="household repository root")
    ap.add_argument("--export", default=str(HERE), help="the export folder (default: this one)")
    ap.add_argument("--out", help="where first-look.md goes (default: ../docs beside the export folder)")
    ap.add_argument("--config", help="a copy of the configuration folder (the app reads /homeassistant)")
    ap.add_argument("--profile", help="house/profile.yaml, for the declared freezes (check 7)")
    ap.add_argument("--offline", metavar="DIR", help="read the export and live.json from DIR; no network")
    ap.add_argument("--inventory", action="store_true", help="also write inventory.md")
    args = ap.parse_args(argv)
    folder = pathlib.Path(args.offline or args.export)
    export = load_export(folder)
    if "automations.json" not in export or "entities.json" not in export:
        print(f"first look: no export in {folder}: run export_house.py first", file=sys.stderr)
        return 2
    meta = export.get("meta.json") or {}
    config_dir = args.config
    if not config_dir and meta.get("mode") == "addon" and pathlib.Path("/homeassistant/automations.yaml").is_file():
        config_dir = "/homeassistant"
    profile = args.profile or next((str(p) for p in (folder.parent / "profile.yaml",) if p.is_file()), None)
    if args.offline:
        lp = folder / "live.json"
        live = json.loads(lp.read_text(encoding="utf-8")) if lp.is_file() else {}
    else:
        try:
            base, token = load_module(HERE / "export_house.py", "export_access").confirmed_access(
                args.root, profile or "house/profile.yaml")
        except Exception:
            print("first look: confirmed profile and private credential required (or use --offline)", file=sys.stderr)
            return 2
        live = gather_live(export, base, token, config_dir, meta.get("mode"), datetime.now(timezone.utc))
    ctx = context(export, live, config_dir, profile)
    results = run_checks(ctx)
    out = pathlib.Path(args.out) if args.out else folder.parent / "docs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "first-look.md").write_text(render_first_look(results, ctx), encoding="utf-8")
    if args.inventory:
        (out / "inventory.md").write_text(render_inventory(export, ctx), encoding="utf-8")
    n = {k: sum(1 for r in results for f in r["findings"] if f["kind"] == k) for k in ("fault", "risk", "notice")}
    unk = [str(r["check"]) for r in results if r["status"] == "unknown"]
    print(f"first look: {n['fault']} faults, {n['risk']} risks, {n['notice']} notices"
          + (f"; unknown: checks {', '.join(unk)}" if unk else "") + f" -> {out / 'first-look.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
