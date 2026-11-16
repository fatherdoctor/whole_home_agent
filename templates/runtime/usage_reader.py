#!/usr/bin/env python3
"""usage_reader.py - read the assistant account's usage straight from its login; write one JSON file for Home Assistant.

Status: template (KIT-USE, 2026-10-24). Copied to house/usage/usage_reader.py at level 0-1 (templates/runtime/README.md,
"The usage reader"). The Claude reader: one reader per runtime, each writing the same file (FALLBACKS.md row "(card)").
Standard library only. Read by packages/assistant-usage.yaml (the sensors and the card) and, later, by the usage
gate (KIT-PRB).

What it does, every run (schedule it every 15-30 minutes where the login lives, e.g. the assistant app):
  1. reads the Claude login file (default ~/.claude/.credentials.json) for the access token, its expiry and the
     plan name; the token is held in memory only - never written, logged, printed or passed on the command line;
  2. NEVER refreshes the token (a refresh rotates the login and can sign the assistant out): an expired token is
     "stale" until Claude Code refreshes it itself;
  3. asks the account usage endpoint the Claude Code client uses for its /usage screen (no model call, no tokens
     spent) for the 5-hour (session) and weekly use, per-model weekly figures where the plan has them, and the
     reset times;
  4. works out today's use: the rise in the weekly % since local midnight, carried across the weekly reset. The
     reset is taken from the provider's reply (a later resets_at, or the weekly figure dropping), never from the
     clock alone: a read after the stored reset time that still carries the old window is "stale" until the
     provider rolls;
  5. writes the JSON file (rewritten whole, atomically). A failed read keeps the last good figures and their read
     time and says why in `status` / `reason`, so Home Assistant shows "unknown" once the read is old - a figure
     is never invented.

The endpoint is unofficial and may change. A reply without the weekly figure is status "unknown" (reason: the reply
shape changed) - open a fix row, never guess. Providers give percentages of their own limits only: no absolute
limits and no daily limit; daily use, the household's warning level and its daily budget are computed locally.

Use: python3 usage_reader.py --out /config/assistant_usage/usage.json [--credentials PATH] [--tz Area/City]
     [--reply SAVED.json] [--dry-run]
--tz is Home Assistant's own time zone (Settings > System > General): the card compares today's date with Home
Assistant's clock, so a different zone (most containers run in UTC) leaves today unknown between the two midnights.
exit 0 = a fresh read, 1 = a stale/error/unknown status (the file still says why), 2 = bad arguments. --dry-run
prints the file instead of writing it.
"""
import argparse
import contextlib
import json
import math
import os
import pathlib
import re
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

SCHEMA = 1
URL = "https://api.anthropic.com/api/oauth/usage"
HEADERS = {"anthropic-beta": "oauth-2025-04-20", "Accept": "application/json",
           "User-Agent": "whole-home-agent-usage-reader/1"}
DEFAULT_CREDENTIALS = "~/.claude/.credentials.json"
NOT_MODELS = ("oauth_apps",)  # seven_day_* keys that are not a model's own weekly figure
GAP = timedelta(hours=1)  # a read this close before midnight is the day's base; `since` then names that read
ROLL_DROP = 0.5  # a weekly figure that drops by more than this (rounding) means the provider's window rolled
ROLL_MOVE = timedelta(hours=1)  # a resets_at this much later than the stored one means the same
MAX_BODY = 5_000_000


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect: urllib would forward the Authorization header to whatever host a 3xx names."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # urllib then raises HTTPError with the 3xx code: "the usage endpoint answered 30x"


_OPENER = urllib.request.build_opener(_NoRedirect)


def _now():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds") if dt else None


def _parse_time(v):
    if not isinstance(v, str) or not v:
        return None
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _num(v):
    """A finite number as a float, else None (a bool, NaN and infinity are not figures)."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return None
    v = float(v)
    return v if math.isfinite(v) else None


def _pct(v):
    """A usage percentage: a finite number of 0 or more, else None (a negative is never a fresh read)."""
    v = _num(v)
    return v if v is not None and v >= 0 else None


SEVERITY = re.compile(r"[a-z][a-z_]{0,23}")  # a provider's severity word (`ok`, `warning`); anything else is dropped


def load_login(path):
    """-> (token, expires_at or None, plan dict) or raises ValueError with a reason that never holds the token."""
    try:
        data = json.loads(pathlib.Path(path).expanduser().read_text(encoding="utf-8"))
    except OSError:
        raise ValueError("no Claude login file at the given path (sign in to Claude Code there first)")
    except ValueError:
        raise ValueError("the Claude login file is not valid JSON")
    oauth = data.get("claudeAiOauth") if isinstance(data, dict) else None
    token = oauth.get("accessToken") if isinstance(oauth, dict) else None  # guard: allow no literal
    if not isinstance(token, str) or not token:
        raise ValueError("the Claude login file has no access token (an API-key login has no account usage)")
    exp = _num(oauth.get("expiresAt"))
    expires = datetime.fromtimestamp(exp / 1000, timezone.utc) if exp else None
    plan = {"plan": oauth.get("subscriptionType") if isinstance(oauth.get("subscriptionType"), str) else None,
            "tier": oauth.get("rateLimitTier") if isinstance(oauth.get("rateLimitTier"), str) else None}
    return token, expires, plan


def fetch_usage(token, opener=None, timeout=20):
    """GET the usage reply. -> (http status, parsed JSON or None). Errors raise OSError with a token-free message;
    a 200 whose body is not JSON (a proxy's page) is an error, not a changed reply shape. Redirects are refused."""
    opener = opener or _OPENER.open
    req = urllib.request.Request(URL, headers=dict(HEADERS, Authorization="Bearer " + token))
    try:
        with opener(req, timeout=timeout) as r:
            status, body = r.status, r.read(MAX_BODY)
    except urllib.error.HTTPError as e:
        return e.code, None
    except (OSError, urllib.error.URLError) as e:
        raise OSError(f"cannot reach the usage endpoint ({type(e).__name__})")
    try:
        return status, json.loads(body.decode("utf-8"))
    except ValueError:
        raise OSError(f"the usage endpoint answered {status} with a body that is not JSON")


def _limit(v):
    """{utilization, resets_at[, severity]} -> {pct, resets_at, severity} or None when it is not a limit."""
    if not isinstance(v, dict) or _pct(v.get("utilization")) is None:
        return None
    sev = v.get("severity")
    return {"pct": round(_pct(v["utilization"]), 1), "resets_at": _iso(_parse_time(v.get("resets_at"))),
            "severity": sev if isinstance(sev, str) and SEVERITY.fullmatch(sev) else None}


def parse_reply(reply):
    """-> {session, week, models} or raises ValueError when the weekly figure is missing (the shape changed)."""
    if not isinstance(reply, dict):
        raise ValueError("reply shape changed: not a JSON object")
    week = _limit(reply.get("seven_day"))
    if week is None:
        raw = reply.get("seven_day")
        if isinstance(raw, dict) and "utilization" in raw:
            raise ValueError("reply shape changed: seven_day.utilization is not a percentage (a negative, "
                             "non-finite or non-numeric value)")
        raise ValueError("reply shape changed: no seven_day.utilization")
    models = {}
    for k, v in sorted(reply.items()):
        m = re.fullmatch(r"seven_day_(\w+)", k)
        if m and m.group(1) not in NOT_MODELS and _limit(v) is not None:
            models[m.group(1)] = _limit(v)
    return {"session": _limit(reply.get("five_hour")), "week": week, "models": models}


def _zone(name):
    if not name:
        return datetime.now().astimezone().tzinfo
    if ZoneInfo is None:
        raise ValueError("--tz needs Python 3.9 or later")
    try:
        return ZoneInfo(name)
    except Exception:
        raise ValueError(f"unknown time zone {name!r}")


def week_rolled(prev, week, read_at):
    """-> (rolled, waiting). rolled: the provider's reply shows a new weekly window since the previous read (its
    resets_at moved later, or the weekly figure dropped). waiting: the clock passed the stored reset time but the
    reply still carries the old window - the read is not used, so today never counts the old window twice."""
    pweek = prev.get("week") if isinstance(prev.get("week"), dict) else {}
    last_pct, last_reset = _num(pweek.get("pct")), _parse_time(pweek.get("resets_at"))
    new_reset = _parse_time(week.get("resets_at"))
    rolled = ((new_reset is not None and last_reset is not None and new_reset - last_reset > ROLL_MOVE)
              or (last_pct is not None and week["pct"] < last_pct - ROLL_DROP))
    passed = last_reset is not None and read_at >= last_reset
    if not rolled and passed and new_reset is None and last_pct is not None and last_pct <= ROLL_DROP:
        rolled = True  # no reset time and too little use to see a drop: at most ROLL_DROP counted twice
    return rolled, not rolled and passed


def today_use(prev, week, read_at, tz, rolled=False):
    """Today's use = carried + week now - base, where base is the weekly % at local midnight (or 0 after a reset)
    and carried is what today used before a reset. prev is the previous file (or {}); rolled from week_rolled().
    `since` says from when today is counted: local midnight; the last read before midnight when that read (up to
    GAP before) is the base; the reset when the week rolled before this first read of the day; or this read when
    the reader was down over midnight - then today is a lower bound, never padded. -> (pct, day block)."""
    local = read_at.astimezone(tz)
    date = local.date().isoformat()
    midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
    day = prev.get("day") if isinstance(prev.get("day"), dict) else {}
    pweek = (prev.get("week") or {}) if isinstance(prev.get("week"), dict) else {}
    last_pct, last_reset = _num(pweek.get("pct")), _parse_time(pweek.get("resets_at"))
    last_read = _parse_time(prev.get("read_at"))
    if day.get("date") != date or _num(day.get("base")) is None:
        # A new day: from 0 when the week rolled since the last read (counted from the reset, before midnight
        # too); from the last read before midnight when it was recent; else from now (a lower bound).
        recent = last_read is not None and midnight - last_read <= GAP and last_pct is not None
        if rolled:
            base, since = 0.0, last_reset or last_read or local
        elif recent:
            base, since = last_pct, min(last_read, midnight)
        else:
            base, since = week["pct"], local
        carried = 0.0
    else:
        base, carried = _num(day["base"]), _num(day.get("carried")) or 0.0
        since = _parse_time(day.get("since")) or midnight
        if rolled and last_pct is not None:  # the week reset since the last read: keep what today used
            carried, base = carried + max(last_pct - base, 0.0), 0.0
    pct = round(max(carried + week["pct"] - base, 0.0), 1)
    return pct, {"date": date, "base": round(base, 1), "carried": round(carried, 1), "since": _iso(since)}


def build(prev, login_path, tz, now=None, fetch=fetch_usage, reply=None):
    """-> the new file contents. prev = the previous file (or {}). reply = a saved reply instead of a call."""
    now = now or _now()
    out = {k: prev.get(k) for k in ("plan", "tier", "read_at", "session", "week", "today", "models", "day")}
    out.update(schema=SCHEMA, provider="claude", attempt_at=_iso(now))
    token = None
    try:
        if reply is None:
            token, expires, plan = load_login(login_path)
            out.update(plan)
            if expires is not None and expires <= now:
                raise LookupError("the login's access token has expired; waiting for Claude Code to refresh it")
            code, reply = fetch(token)
            if code in (401, 403):
                raise LookupError(f"the usage endpoint refused the login ({code}); waiting for Claude Code to "
                                  "refresh it")
            if code != 200:
                raise OSError(f"the usage endpoint answered {code}")
        figures = parse_reply(reply)
    except LookupError as e:
        return _scrub_all(dict(out, status="stale", reason=str(e)), token)
    except ValueError as e:
        st = "unknown" if str(e).startswith("reply shape changed") else "error"
        return _scrub_all(dict(out, status=st, reason=str(e)), token)
    except OSError as e:
        return _scrub_all(dict(out, status="error", reason=str(e)), token)
    rolled, waiting = week_rolled(prev, figures["week"], now)
    if waiting:
        return _scrub_all(dict(out, status="stale", reason="waiting for the weekly window to roll (the reset time "
                                                           "has passed but the reply still carries the old window)"),
                          token)
    pct, day = today_use(prev, figures["week"], now, tz, rolled)
    out.update(figures, read_at=_iso(now), today={"pct": pct, "date": day["date"], "since": day["since"]}, day=day,
               status="ok", reason=None)
    return _scrub_all(out, token)


def _scrub(text, token):
    return text.replace(token, "<token>") if token else text


def _scrub_all(data, token):
    """Every string in the reading (keys too) with the token replaced: nothing written may carry it, whichever field
    of the reply (a model name, a severity, a reset time) echoed it."""
    if not token:
        return data
    if isinstance(data, str):
        return _scrub(data, token)
    if isinstance(data, dict):
        return {_scrub_all(k, token): _scrub_all(v, token) for k, v in data.items()}
    if isinstance(data, list):
        return [_scrub_all(v, token) for v in data]
    return data


def read_prev(path):
    try:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) and data.get("schema") == SCHEMA else {}
    except (OSError, ValueError):
        return {}


def write(path, data):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Home Assistant reads the file, often as another user: keep the mode the file had, or 0644 for a new one
    # (mkstemp alone would leave it 0600).
    try:
        mode = p.stat().st_mode & 0o777
    except OSError:
        mode = 0o644
    # A fresh temporary name, created exclusively (O_EXCL: it never opens or follows an existing file or link).
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=p.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            os.fchmod(fh.fileno(), mode)
            fh.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        os.replace(tmp, p)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def same_file(a, b):
    """True when two paths name the same file (after links), or would once the first is written."""
    pa, pb = pathlib.Path(a).expanduser(), pathlib.Path(b).expanduser()
    try:
        if pa.exists() and pb.exists():
            return os.path.samefile(pa, pb)
    except OSError:
        pass
    return pa.resolve() == pb.resolve()


def main(argv=None, now=None, fetch=fetch_usage):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="usage/usage.json", help="the JSON file Home Assistant reads")
    ap.add_argument("--credentials", default=DEFAULT_CREDENTIALS, help="the Claude login file")
    ap.add_argument("--tz", help="Home Assistant's time zone (Settings > System > General), e.g. Europe/Lisbon; "
                    "default: this host's zone, with a warning")
    ap.add_argument("--reply", help="use a saved usage reply (JSON) instead of calling the endpoint")
    ap.add_argument("--dry-run", action="store_true", help="print the file instead of writing it")
    a = ap.parse_args(argv)
    try:
        tz = _zone(a.tz)
        reply = json.loads(pathlib.Path(a.reply).read_text(encoding="utf-8")) if a.reply else None
    except (OSError, ValueError) as e:
        print(f"usage_reader: {e}", file=sys.stderr)
        return 2
    if not a.tz:
        print(f"usage_reader: warning: no --tz; 'today' uses this host's zone ({tz}), which must be Home Assistant's "
              "(Settings > System > General) or today shows unknown between the two midnights", file=sys.stderr)
    if not a.dry_run and same_file(a.out, a.credentials):
        print("usage_reader: --out names the Claude login file; refusing to overwrite it", file=sys.stderr)
        return 2
    data = build(read_prev(a.out), a.credentials, tz, now=now, fetch=fetch, reply=reply)
    if a.dry_run:
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0 if data["status"] == "ok" else 1
    write(a.out, data)
    print(f"usage_reader: {data['status']}" + (f" ({data['reason']})" if data.get("reason") else "")
          + (f", week {data['week']['pct']:g}%" if data.get("week") else ""))
    return 0 if data["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
