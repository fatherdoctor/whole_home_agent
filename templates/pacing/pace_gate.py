#!/usr/bin/env python3
"""pace_gate.py - the budget gate every unattended run passes first (principles/budget-and-pacing.md rules 2-3).

Status: template (O3b, 2026-10-13; KIT-GATE 2026-11-01: reads the usage reader's JSON, 2 h stale, no floor;
KIT-GATE.f 2026-11-02: a read older than 24 h never runs).
Copied to pacing/pace_gate.py. Standard library only. Usually called through pacing/preflight.py, which also
checks that the lane has work, the off switch, count mode and an API-key spending cap; use it alone only to test.

Reads the latest usage reading and answers RUN or SKIP:
  - the reading is either `templates/runtime/usage_reader.py`'s JSON file (`usage/usage.json`, the usual source)
    or `usage_probe.sh`'s text file (`usage/latest.txt`, for an install without the reader); the format is told
    apart by the first character;
  - the week runs from (reset - 7 days) to the reset, or to --target when the owner set an earlier finish line;
  - pace line = (100 - buffer) x the fraction of that week elapsed, capped at 100 - buffer; no floor by default
    (`--floor N` sets one; a floor also lets a week start fast, so add it only if the early-week starve bites);
  - run only if the all-models figure is under the line, and the --model figure too when one is named
    (the expensive lane's own limit);
  - a read more than 2 h old (`--stale-hours`) needs 10 points of margin under the line: schedule the reader
    every 15-30 minutes so that a fresh read is the normal case. A reader file whose status is not "ok" keeps
    its last good figures with their own read time, so it goes stale on its own;
  - a read older than --max-age-hours (default 24) never runs: SKIP "no usable read: usage read too old". A dead
    reader is a stop, not a margin (KIT-GATE.r F1); a read with no read time never runs either;
  - a read whose reset time has already passed is last week's: its figures count as 0 % and the stale margin applies,
    and only while that read is under the age limit (its real case is the quarter hour after the reset, before the
    reader rolls over);
  - a file with no figures, or no reset time, never runs.

The gate is a CEILING, not a target: being under the line lets a run start; it is never a reason to add work.
Monitoring (the support agent's checks) is never gated by this file: only its idle work is (preflight.py --role monitor).

Use: `python3 pacing/pace_gate.py --file usage/usage.json --buffer 10 --model Opus` (`--floor 15` for a floor);
exit 0 = run, exit 1 = skip (log the printed line on the board: a skip is a good run; a missing or unreadable
reading is a skip too), exit 2 = bad arguments (a --target that is not an ISO time).
A text reading's reset line is read in the reader's local time unless it names a zone in parentheses, e.g.
"(Europe/Lisbon)".
"""
import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

DEFAULT_FLOOR, STALE_HOURS, STALE_MARGIN, MAX_AGE_HOURS = 0.0, 2.0, 10.0, 24.0


def _zone(name):
    if not name or ZoneInfo is None:
        return None
    try:
        return timezone.utc if name.upper() == "UTC" else ZoneInfo(name)
    except Exception:
        return None


def _iso_time(value):
    try:
        t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def parse_json(text):
    """usage_reader.py's file -> the same shape as parse(). Figures from a failed read are its last good ones, with
    their own read_at, so they age into the stale margin; a figure is never invented."""
    out = {"read": None, "sections": {}}
    try:
        data = json.loads(text)
    except ValueError:
        return out
    if not isinstance(data, dict):
        return out
    out["read"] = _iso_time(data.get("read_at")) if data.get("read_at") else None
    figures = [("all models", data.get("week"))] + sorted((data.get("models") or {}).items())
    for label, v in figures:
        pct = v.get("pct") if isinstance(v, dict) else None
        # NaN, infinity or a negative is not a reading: left out (missing), never compared with the line.
        if (isinstance(pct, (int, float)) and not isinstance(pct, bool) and math.isfinite(pct) and pct >= 0
                and v.get("resets_at")):
            out["sections"][label.lower()] = [float(pct), _iso_time(v["resets_at"])]
    return out


def parse(text, now):
    """A reading -> {read, sections: {label: (pct, reset)}}. label is 'all models' or the model name, lower case.
    JSON (usage_reader.py) or the probe's latest.txt."""
    if text.lstrip().startswith("{"):
        return parse_json(text)
    out = {"read": None, "sections": {}}
    m = re.search(r"^read (\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?: (\S+))?", text, re.M)
    if m:
        z = _zone(m.group(2)) or now.tzinfo
        out["read"] = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M").replace(tzinfo=z)
    label = None
    for line in text.splitlines():
        s = line.strip()
        wk = re.match(r"Current week \((.+)\)", s)
        if wk:
            label = wk.group(1).strip().lower()
            out["sections"][label] = [None, None]
            continue
        if label is None:
            continue
        pct = re.match(r"(\d+(?:\.\d+)?)% used", s)
        if pct:
            out["sections"][label][0] = float(pct.group(1))
        rs = re.match(r"Resets (\w{3}) (\d{1,2}), (\d{1,2})(?::(\d{2}))?\s*([ap]m)(?: \((.+)\))?", s, re.I)
        if rs:
            mon, day, hh, mm, ap, zname = rs.groups()
            z = _zone(zname) or now.tzinfo
            h = int(hh) % 12 + (12 if ap.lower() == "pm" else 0)
            base = now.astimezone(z)
            month = datetime.strptime(mon, "%b").month
            year = base.year + (1 if month < base.month - 6 else 0) - (1 if month > base.month + 6 else 0)
            out["sections"][label][1] = datetime(year, month, int(day), h, int(mm or 0), tzinfo=z)
    return out


def decide(text, now=None, buffer=10.0, model=None, target=None, floor=DEFAULT_FLOOR, stale_hours=STALE_HOURS,
           max_age_hours=MAX_AGE_HOURS):
    now = now or datetime.now().astimezone()
    p = parse(text, now)
    allm = p["sections"].get("all models")
    if not allm or allm[0] is None or allm[1] is None:
        return {"run": False, "why": "no usable read: no all-models figure or reset time in the file", "line": None}
    if p["read"] is None:
        return {"run": False, "why": "no usable read: the read time is unknown", "line": None}
    age_h = (now - p["read"]).total_seconds() / 3600
    if age_h > max_age_hours:
        return {"run": False, "line": None,
                "why": f"no usable read: usage read too old ({age_h:.0f} h, limit {max_age_hours:g} h; fix the reader), "
                       f"read {p['read']:%Y-%m-%d %H:%M}"}
    reset = allm[1]
    start = reset - timedelta(days=7)
    end = target or reset
    week_pct = allm[0]
    model_pct = None
    if model:
        sec = p["sections"].get(model.lower())
        if not sec or sec[0] is None:
            return {"run": False, "why": f"no usable read: no {model} figure in the file", "line": None}
        model_pct = sec[0]
    stale = (now - p["read"]) > timedelta(hours=stale_hours)
    if reset <= now:  # a read from last week: its figures no longer apply
        week_pct, model_pct, stale = 0.0, (0.0 if model else None), True
        start, end = reset, reset + timedelta(days=7)
    frac = min(max((now - start) / (end - start), 0.0), 1.0)
    line = max(min((100 - buffer) * frac, 100 - buffer), floor)
    need = line - (STALE_MARGIN if stale else 0.0)
    over = [f"week {week_pct:g}%"] if week_pct >= need else []
    if model and model_pct >= need:
        over.append(f"{model} {model_pct:g}%")
    why = (f"week {week_pct:g}%" + (f", {model} {model_pct:g}%" if model else "") + f", line {line:.1f}%"
           + (f" (stale read: need {need:.1f}%)" if stale else "")
           + f", read {p['read']:%Y-%m-%d %H:%M}")
    return {"run": not over, "why": why, "line": line, "week_pct": week_pct, "model_pct": model_pct,
            "stale": stale, "read": p["read"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", default="usage/usage.json", help="usage_reader.py's JSON, or the probe's latest.txt")
    ap.add_argument("--buffer", type=float, default=10.0, help="percent kept in reserve (20 while the owner is away)")
    ap.add_argument("--model", help="also gate on this model's own weekly figure, e.g. Opus")
    ap.add_argument("--floor", type=float, default=DEFAULT_FLOOR, help="lowest pace line, percent (default 0 = no floor)")
    ap.add_argument("--stale-hours", type=float, default=STALE_HOURS, help="a read older than this needs the margin")
    ap.add_argument("--max-age-hours", type=float, default=MAX_AGE_HOURS, help="a read older than this never runs")
    ap.add_argument("--target", help="finish line before the reset, ISO time with offset, e.g. 2026-01-17T10:00-06:00")
    a = ap.parse_args(argv)
    try:
        target = datetime.fromisoformat(a.target) if a.target else None
    except ValueError as e:
        print(f"bad --target: {e}")
        return 2
    try:
        text = open(a.file, encoding="utf-8").read()
    except OSError as e:
        print(f"SKIP: no usable read: {e}")
        return 1
    r = decide(text, buffer=a.buffer, model=a.model, target=target, floor=a.floor, stale_hours=a.stale_hours,
               max_age_hours=a.max_age_hours)
    print(("RUN: " if r["run"] else "SKIP: budget (") + r["why"] + ("" if r["run"] else ")"))
    return 0 if r["run"] else 1


if __name__ == "__main__":
    sys.exit(main())
