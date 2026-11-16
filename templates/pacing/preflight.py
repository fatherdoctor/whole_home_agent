#!/usr/bin/env python3
"""preflight.py - decide GO or SKIP for an unattended run BEFORE any model starts. Standard library only.

Status: template (KIT-GATE, 2026-11-01; KIT-GATE.f 2026-11-02). Copied to pacing/preflight.py with pace_gate.py; reads the board with
docs/board_check.py's parser. Principle: principles/budget-and-pacing.md rules 3 and 7-9, principles/board-and-lanes.md
"One run, then stop".

Why it exists: a routine whose model reads its brief and then finds nothing to do has already paid for the read.
On a real install, about a third of a day's API spend went on runs that had nothing eligible. So the scheduler
runs this script first, and starts the agent only on exit 0:

    flock -n pacing/builder.lock sh -c 'python3 pacing/preflight.py builder --board docs/board.md \\
        --usage usage/usage.json --model Opus && claude -p "$(cat briefs/builder.md)" ...'

`flock -n` (or the scheduler's own no-overlap setting) keeps a run that outlasts its interval from meeting the next
one: the lane's own claim is eligible so an interrupted run can continue, which also means two overlapping runs
would both take it (principles/board-and-lanes.md rule 23).

The checks, in order (the first that fails decides):
  1. the off switch: a file named by --stop (default pacing/STOP) exists -> SKIP for every role, monitoring
     included (the owner turned the house's agents off on purpose);
  2. --role monitor (the support agent's checks): ALWAYS GO. Monitoring is never budget-blocked - a house over its
     line must not go blind, least of all while the owner is away. The budget only decides its IDLE work: the line
     says `idle work: yes` or `idle work: no (<why>)`;
  3. --role lane: the lane has an eligible row (`eligible()` below; `nothing eligible` is a SKIP, and a skip is a good
     run). The board slice imports the same function, so the slice and the preflight cannot disagree;
  4. the budget, in the household's mode (`setup.budget` in the profile):
     - percentage mode (`--usage`): pace_gate.py's line, fresh-read rule, model figure and age limit (a read older
       than --max-age-hours, default 24, never runs);
     - count mode (`--runs-per-day N`, for a provider with no usage figure): at most N GO answers a day for this
       lane, counted in --runs-log (default pacing/runs.log; this script appends one line per GO, and for
       --role monitor one line per `idle work: yes`, since the agent asks just before it starts idle work). The
       count and the append happen under one lock on the log, so two runs at once cannot both take the last place;
  5. API-key spending (`--month-usd N`): the month's total in --spend-ledger (one line per run,
     `YYYY-MM-DD <lane> <usd>`, written by the run's wrapper from the agent's own cost report) must be under N.
     The per-run cap is the agent's own flag (Claude Code: `--max-budget-usd` in print mode); both are hard caps,
     because an API key spends real money with no weekly reset to stop it.

Output: one line, `GO <why>` or `SKIP <why>`; on a budget SKIP the line has one of the board's skip shapes
(templates/docs/board-format.md section 7: percentage, count mode, or no usable read, each with an optional
`; month $X of $Y`) so the wrapper can append it to the run log as is. `nothing eligible` and the off switch log
nothing on the board: the scheduler's own log is enough (a board commit per empty run is noise). On `nothing
eligible`, each of the lane's open rows that is not eligible is listed on stderr with the reason, so a mis-written
"after" condition (a word that is not a code on the board) does not starve a row in silence.
Exit 0 = GO, 1 = SKIP, 2 = bad arguments or an unreadable board. `--now ISO` fixes the clock for tests.
"""
import argparse
import fcntl
import importlib.util
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPEN_WORDS = ("BACKLOG", "PARTIAL")
AFTER_RE = re.compile(r"\bafter ([A-Z][A-Za-z0-9.-]*[A-Za-z0-9])(?: (in review|merged))?")
MET_RE = re.compile(r"\bafter ([A-Z][A-Za-z0-9.-]*[A-Za-z0-9])(?: in review| merged)?: met\b")
TAG_RE = re.compile(r"\[([A-Z]{2,})\]")  # [BOX], [PC]: a runtime the row needs; [P1], [S2], [EP-x] are not tags
NOT_TAGS = {"UPKEEP"}
QUEUE_ORDER = {"QUEUED (12h)": 0, "QUEUED (12-24h)": 1, None: 2}


def _load(name, *candidates):
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError(f"{name}.py not found in: " + ", ".join(str(p) for p in candidates))


def _role(lane_cell):
    return lane_cell.split(" (")[0].strip()


def after_met(cond_code, mode, rows_by_code):
    """An "after X" is met when X reached the state the condition means: DONE by default, in review or later for
    "after X in review", DONE for "after X merged" (a PASSED - MERGE row has not landed yet). A code not on the
    board is NOT met: archive rows
    are DONE, so the writer marks the condition "after X: met <date>" when it archives X (board-and-lanes.md)."""
    x = rows_by_code.get(cond_code)
    if x is None:
        return False
    word = x.get("word") or ""
    if word == "DONE":
        return True
    if mode == "in review":
        return word in ("READY FOR REVIEW", "PASSED - MERGE", "NEEDS OWNER")
    return False  # "after X" and "after X merged" both wait for DONE: PASSED - MERGE has not landed


def eligible(row, lane, rows_by_code, cannot=("BOX",)):
    """-> (True, "") or (False, why). The ONE eligibility rule; the board slice imports it.

    A row is eligible for `lane` when: its lane cell's role is `lane`; its status word is BACKLOG or PARTIAL (a
    queued row reads as BACKLOG), or it is IN PROGRESS claimed by this lane (an interrupted run continues); every
    "after X" in its status is met (the condition lives in the status cell, board-format.md section 4); it carries
    no runtime tag the lane cannot serve (`[BOX]` by default for a cloud lane) anywhere in its Item cell or its
    status. BLOCKED, READY FOR REVIEW, NEEDS OWNER, DONE, DROPPED and RETIRED are never eligible.
    """
    if _role(row.get("lane", "")) != lane:
        return False, "another lane"
    word, status = row.get("word") or "", row.get("status", "")
    if word == "IN PROGRESS":
        if not re.search(rf"IN PROGRESS {re.escape(lane)}\b", status):
            return False, "claimed by another lane"
    elif word not in OPEN_WORDS:
        return False, f"status {word or 'unreadable'}"
    met_marked = set(MET_RE.findall(status))
    for code, mode in AFTER_RE.findall(status):
        if code in met_marked:
            continue
        if not after_met(code, mode, rows_by_code):
            unknown = "" if code in rows_by_code else (f" (no row {code} on the board: name a code, or mark it "
                                                       f"'after {code}: met <date>')")
            return False, f"after {code}{' ' + mode if mode else ''} not met{unknown}"
    text = " ".join((row.get("item") or row.get("title", ""), status))
    for tag in TAG_RE.findall(text):
        if tag in cannot and tag not in NOT_TAGS:
            return False, f"[{tag}] row"
    return True, ""


def _priority(row):
    m = re.search(r"\[P([1-4])\]", row.get("status", ""))
    return int(m.group(1)) if m else 3


def ordered(rows, lane, cannot=("BOX",)):
    """The lane's eligible rows in the order a lane brief takes them: its own claims, QUEUED (12h), QUEUED (12-24h),
    then BACKLOG; inside each block priority first, board order breaks ties."""
    by_code = {r["code"]: r for r in rows}
    ok = [r for r in rows if eligible(r, lane, by_code, cannot)[0]]
    return sorted(ok, key=lambda r: (0 if r.get("word") == "IN PROGRESS" else 1,
                                     QUEUE_ORDER.get(r.get("queued"), 2), _priority(r), r.get("line", 0)))


def why_not(rows, lane, cannot=("BOX",)):
    """The lane's open rows (BACKLOG, PARTIAL, its own claim) that are not eligible, with the reason: printed on a
    `nothing eligible` SKIP. BLOCKED and review rows are left out: they say why in their own status."""
    by_code = {r["code"]: r for r in rows}
    out = []
    for r in rows:
        if _role(r.get("lane", "")) != lane or (r.get("word") or "") not in OPEN_WORDS + ("IN PROGRESS",):
            continue
        ok, why = eligible(r, lane, by_code, cannot)
        if not ok:
            out.append((r["code"], why))
    return out


def runs_today(log_path, lane, day):
    try:
        lines = Path(log_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0
    return sum(1 for ln in lines if ln.startswith(day) and ln.split()[2:3] == [lane])


def claim_run(log_path, lane, now, ceiling, what="GO"):
    """Count mode: take one of today's `ceiling` places for `lane` and record it, under an exclusive lock on the log
    so the count and the append are one step. -> (taken: bool, runs today before this one)."""
    log = Path(log_path)
    log.parent.mkdir(parents=True, exist_ok=True)
    day = now.strftime("%Y-%m-%d")
    with log.open("a+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        n = sum(1 for ln in f.read().splitlines() if ln.startswith(day) and ln.split()[2:3] == [lane])
        if n >= ceiling:
            return False, n
        f.write(f"{now:%Y-%m-%d %H:%M} {lane} {what}\n")
        f.flush()
    return True, n


def month_spend(ledger_path, month):
    total = 0.0
    try:
        lines = Path(ledger_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0.0
    for ln in lines:
        parts = ln.split()
        if len(parts) >= 3 and parts[0].startswith(month):
            try:
                total += float(parts[2])
            except ValueError:
                continue
    return total


def decide(a, now, board_text=None, usage_text=None, gate=None, board=None):
    """-> (go: bool, line: str). Pure apart from reading the files named in `a`; tests pass the texts in."""
    stamp = now.strftime("%Y-%m-%d %H:%M ") + (now.strftime("%Z") or "local")
    if Path(a.stop).exists():
        return False, f"SKIP off switch ({a.stop} exists; remove it to turn the agents back on)"
    budget_go, budget_why = False, "no budget mode: pass --usage or --runs-per-day (budget-and-pacing.md rule 9)"
    if a.usage:
        g = gate.decide(usage_text, now=now, buffer=a.buffer, model=a.model, target=a.target, floor=a.floor,
                        stale_hours=a.stale_hours, max_age_hours=getattr(a, "max_age_hours", gate.MAX_AGE_HOURS))
        budget_go, budget_why = g["run"], g["why"]
        if g.get("line") is not None:  # the board's skip shape (board-format.md section 7)
            read = g.get("read")
            budget_why = (f"week {g['week_pct']:g} %, {a.model or 'all'} "
                          f"{(g['model_pct'] if a.model else g['week_pct']):g} %, line {g['line']:.1f} %, read "
                          + (read.strftime("%Y-%m-%d %H:%M ") + (read.strftime("%Z") or "UTC") if read else "unknown"))
    elif a.runs_per_day is not None:
        n = runs_today(a.runs_log, a.lane, now.strftime("%Y-%m-%d"))
        budget_go, budget_why = n < a.runs_per_day, f"count mode: {n} of {a.runs_per_day} runs today"
    if budget_go and a.month_usd is not None:
        spent = month_spend(a.spend_ledger, now.strftime("%Y-%m"))
        budget_go = spent < a.month_usd
        budget_why += f"; month ${spent:.2f} of ${a.month_usd:.2f}"
    if a.role == "monitor":
        return True, f"GO monitor (never budget-blocked); idle work: " + (
            f"yes ({budget_why})" if budget_go else f"no ({budget_why})")
    parsed = board.parse_board(board_text)
    rows = ordered(parsed["items"], a.lane, tuple(a.cannot))
    if not rows:
        return False, f"SKIP nothing eligible for {a.lane} (an empty queue is a good run)"
    if not budget_go:
        return False, f"{stamp} {a.lane} skipped: budget ({budget_why})"
    first = rows[0]
    return True, f"GO {a.lane}: {len(rows)} eligible, first {first['code']}; {budget_why}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lane", help="the lane role from the board's Lane column (builder, reviewer, ...), or any name "
                    "with --role monitor")
    ap.add_argument("--role", choices=("lane", "monitor"), default="lane")
    ap.add_argument("--board", default="docs/board.md")
    ap.add_argument("--cannot", action="append", default=None,
                    help="a runtime tag this lane cannot serve, e.g. BOX for a cloud lane (repeatable; default BOX)")
    ap.add_argument("--usage", help="percentage mode: usage_reader.py's JSON (or the probe's latest.txt)")
    ap.add_argument("--buffer", type=float, default=10.0)
    ap.add_argument("--model")
    ap.add_argument("--target", help="finish line before the reset, ISO time with offset")
    ap.add_argument("--floor", type=float, default=0.0)
    ap.add_argument("--stale-hours", type=float, default=2.0)
    ap.add_argument("--max-age-hours", type=float, default=24.0, help="a usage read older than this never runs")
    ap.add_argument("--runs-per-day", type=int, help="count mode: GO answers a day for this lane")
    ap.add_argument("--runs-log", default="pacing/runs.log")
    ap.add_argument("--month-usd", type=float, help="API key: the month's hard spending cap in dollars")
    ap.add_argument("--spend-ledger", default="pacing/spend.log")
    ap.add_argument("--stop", default="pacing/STOP", help="the off switch: while this file exists nothing runs")
    ap.add_argument("--now", help="ISO time with offset (tests)")
    a = ap.parse_args(argv)
    a.cannot = a.cannot if a.cannot is not None else ["BOX"]
    try:
        now = datetime.fromisoformat(a.now) if a.now else datetime.now().astimezone()
        target = datetime.fromisoformat(a.target) if a.target else None
    except ValueError as e:
        print(f"SKIP bad arguments: {e}")
        return 2
    a.target = target
    gate = _load("pace_gate", HERE / "pace_gate.py")
    board = _load("board_check", HERE.parent / "docs" / "board_check.py", HERE.parent / "templates" / "docs" / "board_check.py",
                  HERE.parent.parent / "templates" / "docs" / "board_check.py")
    usage_text, board_text = None, None
    try:
        if a.usage:
            usage_text = Path(a.usage).read_text(encoding="utf-8")
    except OSError as e:
        usage_text = ""  # an unreadable reading never runs (pace_gate: no figures)
        print(f"preflight: usage file: {e}", file=sys.stderr)
    if a.role == "lane":
        try:
            board_text = Path(a.board).read_text(encoding="utf-8")
        except OSError as e:
            print(f"SKIP board unreadable: {e}")
            return 2
    go, line = decide(a, now, board_text, usage_text, gate, board)
    count_mode = a.runs_per_day is not None and not a.usage
    if go and a.runs_per_day is not None and (a.role == "lane" or (count_mode and "idle work: yes" in line)):
        # percentage mode decides on the usage read; the log line is then a record, never a second limit
        ceiling = a.runs_per_day if count_mode else float("inf")
        try:
            taken, n = claim_run(a.runs_log, a.lane, now, ceiling, "GO" if a.role == "lane" else "GO idle")
        except OSError as e:
            # The run cannot be recorded, so it cannot be counted. Lane work fails closed. The monitor keeps
            # running: a broken budget log must never stop the health checks (levels.md, level 3).
            print(f"preflight: runs log: {e}", file=sys.stderr)
            why = f"count mode: runs log not writable ({e.__class__.__name__})"
            if a.role == "lane":
                go = False
                line = f"{now:%Y-%m-%d %H:%M} {(now.strftime('%Z') or 'local')} {a.lane} skipped: budget ({why})"
            else:
                line = f"GO monitor (never budget-blocked); idle work: no ({why})"
            print(line)
            return 0 if go else 1
        if not taken:  # another run took the last place between the read and the lock
            why = f"count mode: {n} of {a.runs_per_day} runs today"
            if a.role == "lane":
                go = False
                line = f"{now:%Y-%m-%d %H:%M} {(now.strftime('%Z') or 'local')} {a.lane} skipped: budget ({why})"
            else:
                line = f"GO monitor (never budget-blocked); idle work: no ({why})"
    print(line)
    if not go and line.startswith("SKIP nothing eligible"):
        for code, why in why_not(board.parse_board(board_text)["items"], a.lane, tuple(a.cannot)):
            print(f"preflight: {code} not eligible: {why}", file=sys.stderr)
    return 0 if go else 1


if __name__ == "__main__":
    sys.exit(main())
