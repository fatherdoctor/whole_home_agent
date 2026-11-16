#!/usr/bin/env python3
"""usage_reader_codex.py - read the Codex account's usage from its own client; write the usage card's JSON file.

Status: template (CX-KIT, 2026-11-09). The Codex reader for the usage card (KIT-USE): the second reader, writing the
same file as usage_reader.py (FALLBACKS.md row "(card)"), so the package, the macros, the card and the pace gate read
it unchanged. Copied to house/usage/ next to usage_reader.py (it uses that file's day and weekly-reset bookkeeping, so
the two always agree on what "today" means). Standard library only. Setup: adapters/agents/codex.md, "The usage card".

What it does, every run (schedule it every 15-30 minutes where the Codex sign-in lives):
  1. starts the Codex client's own app server (`codex app-server`, JSON lines over stdin/stdout) and asks it for the
     account's rate limits (`initialize`, `initialized`, then `account/rateLimits/read`). One deadline (TIMEOUT,
     counted from just before the client starts) bounds the waits for its replies; the process is always stopped
     afterwards, which adds at most STOP_WAIT seconds. The requests are a few hundred bytes written to the client's
     input, not timed separately. No model call: no tokens are spent;
  2. never opens the sign-in file, never sees a token, never starts or forces a sign-in: the client answers from its
     own sign-in, and a signed-out client is an error that a person fixes by signing in;
  3. places each window the reply names by its length, not its slot (a plan with only a weekly window sends it as
     `primary`): a window of exactly a week (10080 minutes, the length seen in a real reply) is the weekly figure,
     one of exactly 300 minutes the session (5-hour) figure (that length is the documented one, not yet seen in a
     captured reply); a window of any other length is not named and not used;
  3a. checks the figures: a percentage outside 0-100 (or not a finite number), a window length that is not a
     positive whole number of minutes, or a weekly window without a usable reset time makes the reply "unknown"
     (reason: the reply shape changed), the last good figures kept;
  4. works out today's use and the weekly reset exactly as usage_reader.py does (its `week_rolled` and `today_use`);
  5. writes the JSON file (rewritten whole, atomically). A failed read keeps the last good figures and their read time
     and says why in `status` / `reason`; a figure is never invented. Figures and day bookkeeping are kept only from
     a previous file this reader wrote (`provider: codex`): a file another reader wrote starts afresh, so another
     account's figures are never shown as this one's and its weekly window never reads as a roll.

The app server's methods are the client's own interface, not a published web API, and may change between client
versions. A reply without a weekly window is status "unknown" (reason: the reply shape changed) - open a fix row,
never guess. A JSON-RPC error (for example the client is signed out) is status "error" with the client's own words.
Codex sends no per-model weekly figures: `models` is always empty.

Use: python3 usage_reader_codex.py --out /config/assistant_usage/usage.json [--codex PATH] [--codex-home DIR]
     [--tz Area/City] [--reply SAVED] [--dry-run]
--tz is Home Assistant's own time zone, as for usage_reader.py. --reply replays a saved reply offline: either the bare
`account/rateLimits/read` result (one JSON object) or an app-server transcript (JSON lines; the reply to id 2 is
used, and an `account/updated` notice gives the plan). exit 0 = a fresh read, 1 = a stale/error/unknown status (the
file still says why), 2 = bad arguments. --dry-run prints the file instead of writing it.
"""
import argparse
import json
import math
import os
import pathlib
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import usage_reader as base  # noqa: E402  (the file beside this one: the day and reset bookkeeping)

SCHEMA = base.SCHEMA
TIMEOUT = 20  # seconds: the waits for the client's replies, counted from just before it starts
STOP_WAIT = 5  # seconds at most to stop the client afterwards (3 to end, then 2 after a kill)
SESSION_MINS = 5 * 60  # the session (5-hour) window: the documented length, not yet in a captured reply
WEEK_MINS = 7 * 24 * 60  # the weekly window: the length a real reply gave
PROVIDER = "codex"
READ_ID = 2
CLIENT = {"name": "whole-home-agent-usage-reader", "title": "Usage reader", "version": "1"}
MAX_LINE = 1_000_000


def _pump(stream, lines):
    """Put each line the app server writes on the queue, then None at the end of its output."""
    try:
        for line in stream:
            lines.put(line)
    except (OSError, ValueError):
        pass
    finally:
        lines.put(None)


def _reply(lines, request_id, deadline, notices):
    """The result of one request, skipping notices (kept in `notices`). Raises LookupError on a JSON-RPC error,
    OSError on a timeout, the end of output or a line that is not JSON."""
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise OSError("Codex did not answer the usage read in time")
        try:
            line = lines.get(timeout=remaining)
        except queue.Empty:
            raise OSError("Codex did not answer the usage read in time")
        if line is None:
            raise OSError("Codex closed the connection before answering the usage read")
        if len(line) > MAX_LINE:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            raise OSError("Codex answered with a line that is not JSON")
        if not isinstance(msg, dict):
            continue
        if "method" in msg and "id" not in msg:
            notices.append(msg)
            continue
        if msg.get("id") != request_id:
            continue
        if msg.get("error") is not None:
            err = msg["error"] if isinstance(msg["error"], dict) else {}
            raise LookupError(str(err.get("message") or "the usage read failed")[:300])
        return msg.get("result") if isinstance(msg.get("result"), dict) else {}


def read_app_server(codex="codex", codex_home=None, timeout=TIMEOUT, popen=subprocess.Popen):
    """Ask the client's app server for the account's rate limits. -> (result dict, notices list)."""
    env = dict(os.environ)
    if codex_home:
        env["CODEX_HOME"] = str(pathlib.Path(codex_home).expanduser())
    deadline = time.monotonic() + timeout
    try:
        proc = popen([codex, "app-server", "--config", "check_for_update_on_startup=false"],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                     bufsize=1, env=env)
    except OSError as e:
        raise OSError(f"cannot start the Codex client ({type(e).__name__}); check --codex")
    notices = []
    try:
        lines = queue.Queue()
        threading.Thread(target=_pump, args=(proc.stdout, lines), daemon=True).start()

        def send(msg):
            try:
                proc.stdin.write(json.dumps(msg) + "\n")
                proc.stdin.flush()
            except (OSError, ValueError):
                raise OSError("Codex closed the connection before answering the usage read")

        send({"id": 1, "method": "initialize", "params": {"clientInfo": CLIENT}})
        _reply(lines, 1, deadline, notices)
        send({"method": "initialized"})
        send({"id": READ_ID, "method": "account/rateLimits/read", "params": {}})
        return _reply(lines, READ_ID, deadline, notices), notices
    finally:
        _stop(proc)


def _stop(proc):
    try:
        proc.stdin.close()
    except (AttributeError, OSError, ValueError):
        pass
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:  # noqa: BLE001 - a process that will not stop is killed
        try:
            proc.kill()
            proc.wait(timeout=2)
        except Exception:  # noqa: BLE001
            pass


def load_saved(path):
    """A saved reply -> (result dict, notices). A bare result object, or a JSON-lines app-server transcript."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    try:
        whole = json.loads(text)
    except ValueError:
        whole = None
    if isinstance(whole, dict) and "id" not in whole and "method" not in whole:
        return whole, []
    notices = []
    for line in (text.splitlines() if whole is None else [text]):
        if not line.strip():
            continue
        msg = json.loads(line)
        if isinstance(msg, dict) and "method" in msg and "id" not in msg:
            notices.append(msg)
        elif isinstance(msg, dict) and msg.get("id") == READ_ID:
            if msg.get("error") is not None:
                err = msg["error"] if isinstance(msg["error"], dict) else {}
                raise LookupError(str(err.get("message") or "the usage read failed")[:300])
            return (msg.get("result") if isinstance(msg.get("result"), dict) else {}), notices
    raise ValueError(f"no reply to the usage read (id {READ_ID}) in the saved file")


def _window(v, slot):
    """{usedPercent, windowDurationMins, resetsAt (epoch seconds)} -> (minutes, {pct, resets_at, severity}), None
    for an empty slot. Raises ValueError("reply shape changed: ...") for a window whose figures cannot be used."""
    if v is None:
        return None
    if not isinstance(v, dict):
        raise ValueError(f"reply shape changed: {slot} is not a window")
    pct, mins = base._num(v.get("usedPercent")), base._num(v.get("windowDurationMins"))
    if pct is None or not math.isfinite(pct) or not 0 <= pct <= 100:
        raise ValueError(f"reply shape changed: {slot} usedPercent is not a percentage")
    if mins is None or not math.isfinite(mins) or mins <= 0 or mins != int(mins):
        raise ValueError(f"reply shape changed: {slot} windowDurationMins is not a length in minutes")
    reset = base._num(v.get("resetsAt"))
    resets_at = None
    if reset is not None:
        try:
            resets_at = base._iso(datetime.fromtimestamp(reset, timezone.utc)) if reset > 0 else None
        except (OverflowError, OSError, ValueError):
            resets_at = None
        if resets_at is None:
            raise ValueError(f"reply shape changed: {slot} resetsAt is not a time")
    return int(mins), {"pct": round(pct, 1), "resets_at": resets_at, "severity": None}


def parse_result(result, notices=()):
    """-> {session, week, models, plan} or raises ValueError when no weekly window is named (the shape changed)."""
    if not isinstance(result, dict):
        raise ValueError("reply shape changed: not a JSON object")
    limits = result.get("rateLimits")
    if not isinstance(limits, dict):
        raise ValueError("reply shape changed: no rateLimits")
    session = week = None
    for slot in ("primary", "secondary"):
        w = _window(limits.get(slot), slot)
        if w is None:
            continue
        mins, fig = w
        if mins == SESSION_MINS and session is None:
            session = fig
        elif mins == WEEK_MINS and week is None:
            week = fig
    if week is None:
        raise ValueError("reply shape changed: no weekly window in rateLimits")
    if week["resets_at"] is None:
        raise ValueError("reply shape changed: the weekly window has no reset time")
    plan = limits.get("planType") if isinstance(limits.get("planType"), str) else None
    for n in notices:
        p = n.get("params") if n.get("method") == "account/updated" else None
        if plan is None and isinstance(p, dict) and isinstance(p.get("planType"), str):
            plan = p["planType"]
    return {"session": session, "week": week, "models": {}, "plan": plan}


def build(prev, tz, now=None, read=None):
    """-> the new file contents. prev = the previous file (or {}). read() -> (result, notices): the client by
    default, or a saved reply (main's --reply)."""
    now = now or base._now()
    if not isinstance(prev, dict) or prev.get("provider") != PROVIDER:
        prev = {}  # another reader's file (or none): its figures and its day are not this account's
    out = {k: prev.get(k) for k in ("plan", "tier", "read_at", "session", "week", "today", "models", "day")}
    out.update(schema=SCHEMA, provider=PROVIDER, attempt_at=base._iso(now), tier=None)
    try:
        result, notices = (read or read_app_server)()
        figures = parse_result(result, notices)
    except LookupError as e:
        return dict(out, status="error", reason=f"the Codex client refused the usage read: {e}")
    except ValueError as e:
        st = "unknown" if str(e).startswith("reply shape changed") else "error"
        return dict(out, status=st, reason=str(e))
    except OSError as e:
        return dict(out, status="error", reason=str(e))
    rolled, waiting = base.week_rolled(prev, figures["week"], now)
    if waiting:
        return dict(out, status="stale", reason="waiting for the weekly window to roll (the reset time has passed "
                                                "but the reply still carries the old window)")
    pct, day = base.today_use(prev, figures["week"], now, tz, rolled)
    out.update(figures, read_at=base._iso(now), today={"pct": pct, "date": day["date"], "since": day["since"]},
               day=day, status="ok", reason=None)
    return out


def main(argv=None, now=None, read=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="usage/usage.json", help="the JSON file Home Assistant reads")
    ap.add_argument("--codex", default="codex", help="the Codex client to run (default: `codex` on PATH)")
    ap.add_argument("--codex-home", help="the client's home folder when it is not the default (sets CODEX_HOME)")
    ap.add_argument("--tz", help="Home Assistant's time zone (Settings > System > General), e.g. Europe/Lisbon; "
                    "default: this host's zone, with a warning")
    ap.add_argument("--reply", help="use a saved reply (a result object or an app-server transcript)")
    ap.add_argument("--dry-run", action="store_true", help="print the file instead of writing it")
    a = ap.parse_args(argv)
    try:
        tz = base._zone(a.tz)
        if a.reply:
            pathlib.Path(a.reply).read_text(encoding="utf-8")  # unreadable is a bad argument, like usage_reader.py
    except (OSError, ValueError) as e:
        print(f"usage_reader_codex: {e}", file=sys.stderr)
        return 2
    if not a.tz:
        print(f"usage_reader_codex: warning: no --tz; 'today' uses this host's zone ({tz}), which must be Home "
              "Assistant's (Settings > System > General) or today shows unknown between the two midnights",
              file=sys.stderr)
    if a.reply:
        read = lambda: load_saved(a.reply)  # noqa: E731 - a saved error reply is replayed as one
    elif read is None:
        read = lambda: read_app_server(a.codex, a.codex_home)  # noqa: E731
    data = build(base.read_prev(a.out), tz, now=now, read=read)
    if a.dry_run:
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0 if data["status"] == "ok" else 1
    base.write(a.out, data)
    print(f"usage_reader_codex: {data['status']}" + (f" ({data['reason']})" if data.get("reason") else "")
          + (f", week {data['week']['pct']:g}%" if data.get("week") else ""))
    return 0 if data["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
