#!/usr/bin/env python3
"""board_check.py - check a board file against templates/docs/board-format.md. Standard library only.

Status: written (KIT-BRD, 2026-10-25). Run from the house repository's root:
    python3 templates/docs/board_check.py house/docs/board.md [--names house/docs/card-names.tsv]
Exit 0 = clean, 1 = faults (printed as a table: line, code, fault), 2 = the file could not be read.
The names file defaults to card-names.tsv beside the board; pass --names - to skip that check.

The level is read from the file: a `## Plans` section means level 6 (tokens, closers and the Sprints and Epics tables
are required on open rows); otherwise level 2 (tokens optional, no queue prefixes). `parse_board(text)` is importable
by the board view and the board page so that every tool reads the file the same way (board-format.md section 9).
"""
import re
import sys
from pathlib import Path

WORDS = ("BACKLOG", "IN PROGRESS", "READY FOR REVIEW", "PASSED - MERGE", "NEEDS OWNER", "BLOCKED", "PARTIAL", "DONE",
         "DROPPED",
         "RETIRED")
CLOSED = {"DONE", "DROPPED", "RETIRED"}
FINISHED = CLOSED | {"READY FOR REVIEW", "PASSED - MERGE", "NEEDS OWNER", "BLOCKED"}
LANES = {"agent", "owner", "builder", "reviewer", "mechanical", "writer", "planner", "lead"}
KNOWN_SECTIONS = ("Plans", "Sprints", "Epics", "Items", "Routines", "Run log")
ITEMS_HEADER = "| Item | Lane | Pts | Status | Link | Decisions needed |"
CODE_RE = re.compile(r"^\*\*([A-Z][A-Za-z0-9.-]*)\s+(.*?)\*\*")
BARE_CODE_RE = re.compile(r"^[A-Z][A-Za-z0-9.-]*$")
QUEUE_RE = re.compile(r"^(QUEUED \(12h\)|QUEUED \(12-24h\)) ")
CLOSER_RE = re.compile(r"-> closer: (\S+)(?: (\d{4}-\d{2}-\d{2}))? \[([^\]]+)\]")
TOKEN_RE = {"priority": re.compile(r"\[P([1-4])\]"), "sprint": re.compile(r"\[(S[0-9]+)\]"),
            "epic": re.compile(r"\[(EP-[A-Za-z0-9]+)\]|\[(UPKEEP)\]")}
PTS_RE = re.compile(r"^(\d+(?:\.5)?)(?:\s*\(.*\))?$")
STAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"
RUN_RE = re.compile(rf"^{STAMP}-\d{{2}}:\d{{2}} \S+ (\S+) (\S+) est (\d+(?:\.5)?) / actual (\d+(?:\.5)?|unknown) \(.+\) "
                    r"helpers: (none|\S+ .+)$")
SKIP_RE = re.compile(rf"^{STAMP} \S+ (\S+) skipped: budget \("
                     rf"(?:week \d+(?:\.\d+)? %, \S+ \d+(?:\.\d+)? %, line \d+(?:\.\d+)? %, read {STAMP} \S+"
                     r"|count mode: \d+ of \d+ runs today"
                     r"|no usable read: .+?)"
                     r"(?:; month \$\d+\.\d\d of \$\d+\.\d\d)?\)$")
ITEM_AFTER_RE = re.compile(r"\bafter ([A-Z][A-Za-z0-9.-]*[A-Za-z0-9])\b")
IN_PROGRESS_RE = re.compile(rf"^IN PROGRESS (\S+) {STAMP}")


def split_cells(line):
    """Cells of a Markdown table row; `\\|` inside a cell is kept as a pipe."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", body)]


def parse_board(text):
    """Return {'level', 'sections', 'items', 'runlog', 'sprints', 'epics', 'faults', 'warnings'} for a board file's
    text. Each item carries its whole Item cell as 'item' (the preflight reads runtime tags anywhere in it).
    Run-log actuals are floats when measured, or None for the literal 'actual unknown'."""
    out = {"sections": {}, "items": [], "runlog": [], "sprints": set(), "epics": set(), "faults": [], "warnings": []}
    section, order = None, []
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
            order.append(section)
            out["sections"].setdefault(section, [])
            continue
        if section is not None:
            out["sections"][section].append((n, line))
    out["level"] = 6 if "Plans" in out["sections"] else 2
    seen_run = False
    for s in order:
        if s == "Run log":
            seen_run = True
        elif s not in KNOWN_SECTIONS and not seen_run:
            out["faults"].append((0, "-", f"unknown section '## {s}' above '## Run log' (board-format.md section 2)"))
    for name in ("Items", "Run log"):
        if name not in out["sections"]:
            out["faults"].append((0, "-", f"missing section '## {name}'"))
    if out["level"] == 6:
        for name in ("Sprints", "Epics"):
            if name not in out["sections"]:
                out["faults"].append((0, "-", f"level 6 board without '## {name}'"))
    for name, key in (("Sprints", "sprints"), ("Epics", "epics")):
        rows = [c for _, l in out["sections"].get(name, []) if l.startswith("|") for c in [split_cells(l)]]
        out[key] = {r[0] for r in rows[2:] if r and BARE_CODE_RE.match(r[0])}
    _parse_items(out)
    _parse_runlog(out)
    return out


def _parse_items(out):
    rows = out["sections"].get("Items", [])
    table = [(n, l) for n, l in rows if l.startswith("|")]
    if not table:
        return
    if table[0][1].strip() != ITEMS_HEADER:
        out["faults"].append((table[0][0], "-", "Items header must be exactly: " + ITEMS_HEADER))
    codes = {}
    for n, line in table[2:]:
        cells = split_cells(line)
        if len(cells) != 6:
            out["faults"].append((n, "-", f"{len(cells)} cells, expected 6"))
            continue
        item, lane, pts, status, link, decisions = cells
        m = CODE_RE.match(item)
        if not m:
            out["faults"].append((n, "-", "Item cell must start with **CODE Title** (code: capital letter, then "
                                          "letters, digits, hyphens, dots)"))
            continue
        code, title = m.group(1), m.group(2)
        if code.endswith("."):
            out["faults"].append((n, code, "code ends with a dot"))
        if code in codes:
            out["faults"].append((n, code, f"duplicate code (first at line {codes[code]})"))
        codes.setdefault(code, n)
        row = {"line": n, "code": code, "title": title, "item": item, "lane": lane, "pts": pts, "status": status,
               "link": link,
               "decisions": decisions, "word": None, "queued": None, "closer": None, "tokens": {}}
        out["items"].append(row)
        lane_role = lane.split(" (")[0]
        if lane_role not in LANES:
            out["faults"].append((n, code, f"unknown lane '{lane}' (roles: {', '.join(sorted(LANES))})"))
        if code.startswith("D-") and lane_role != "owner":
            out["faults"].append((n, code, "an owner card (D-) must be in the owner lane"))
        pm = PTS_RE.match(pts)
        if not pm:
            out["faults"].append((n, code, f"Pts '{pts}' is not a number (halves allowed; a note may follow in parentheses)"))
        elif float(pm.group(1)) > 20 and not any(status.startswith(w) for w in CLOSED):
            out["faults"].append((n, code, f"{pm.group(1)} points: split first (cap 20)"))
        rest = status
        q = QUEUE_RE.match(rest)
        if q:
            row["queued"] = q.group(1)
            rest = rest[q.end():]
            if out["level"] == 2:
                out["faults"].append((n, code, "queue prefix on a level-2 board (no planner)"))
        word = next((w for w in WORDS if rest.startswith(w)), None)
        if word is None and row["queued"]:
            word = "BACKLOG"  # a queued row with its BACKLOG word dropped (board-format.md section 4)
        row["word"] = word
        if word is None:
            out["faults"].append((n, code, f"status must start with one of: {', '.join(WORDS)}"))
            continue
        if row["queued"] and word in FINISHED:
            out["faults"].append((n, code, f"finished row keeps a queue prefix ({row['queued']} {word})"))
        if word == "IN PROGRESS" and not IN_PROGRESS_RE.match(rest):
            out["faults"].append((n, code, "IN PROGRESS must say '<lane> YYYY-MM-DD HH:MM'"))
        if word in ("DONE", "DROPPED", "RETIRED") and not re.match(rf"^{word} \d{{4}}-\d{{2}}-\d{{2}}", rest):
            out["faults"].append((n, code, f"{word} needs its date"))
        if word == "PASSED - MERGE" and not re.match(r"^PASSED - MERGE \d{4}-\d{2}-\d{2}.*\bwaits on .+-> \S+", rest):
            out["faults"].append((n, code, "PASSED - MERGE must say '<date> ... waits on <what lands it> -> <who merges>'"))
        if word == "BLOCKED" and not rest.startswith("BLOCKED by "):
            out["faults"].append((n, code, "BLOCKED must say 'BLOCKED by <what>'"))
        if word == "NEEDS OWNER" and not decisions.strip():
            out["faults"].append((n, code, "NEEDS OWNER with an empty Decisions cell (say what, or 'see D-CODE')"))
        c = CLOSER_RE.search(rest)
        if c:
            row["closer"] = (c.group(1), c.group(3))
            row["closer_date"] = c.group(2)  # preserve the optional apply date without changing the closer tuple
            if c.group(1) not in LANES:
                out["faults"].append((n, code, f"closer lane '{c.group(1)}' is not a role"))
        for key, rx in TOKEN_RE.items():
            tm = rx.search(status)
            if tm:
                row["tokens"][key] = next(g for g in tm.groups() if g)
        if out["level"] == 6 and word not in CLOSED:
            for key in ("priority", "sprint", "epic"):
                if key not in row["tokens"]:
                    out["faults"].append((n, code, f"open row without a {key} token ([Pn] [Sn] [EP-x] or [UPKEEP])"))
            if row["tokens"].get("sprint") and row["tokens"]["sprint"] not in out["sprints"]:
                out["faults"].append((n, code, f"sprint {row['tokens']['sprint']} is not in the Sprints table"))
            ep = row["tokens"].get("epic")
            if ep and ep != "UPKEEP" and ep not in out["epics"]:
                out["faults"].append((n, code, f"epic {ep} is not in the Epics table"))
            if word == "READY FOR REVIEW" and not c:
                out["faults"].append((n, code, "in review without a closer (-> closer: <lane> [<what>])"))
    out["codes"] = codes
    for row in out["items"]:  # board-format.md section 4: the machine-read "after X" lives in the status cell
        if row["word"] in CLOSED:
            continue
        free = CODE_RE.sub("", row["item"], count=1)
        for x in ITEM_AFTER_RE.findall(free):
            if x in codes and x != row["code"]:
                out["warnings"].append((row["line"], row["code"], f"'after {x}' in the Item cell is not read by the "
                                        "preflight or the slice: write it in the status, e.g. BACKLOG (after "
                                        f"{x}) (board-format.md section 4)"))


def _parse_runlog(out):
    for n, line in out["sections"].get("Run log", []):
        if not line.strip() or line.startswith("<!--") or line.startswith("#"):
            continue
        m = RUN_RE.match(line.strip())
        if m:
            out["runlog"].append({"line": n, "lane": m.group(1), "code": m.group(2), "est": float(m.group(3)),
                                  "actual": None if m.group(4) == "unknown" else float(m.group(4)),
                                  "helpers": m.group(5)})
            continue
        if SKIP_RE.match(line.strip()):
            out["runlog"].append({"line": n, "lane": SKIP_RE.match(line.strip()).group(1), "code": None, "skipped": True})
            continue
        out["faults"].append((n, "-", "run-log line matches neither shape (board-format.md section 7)"))


def check_names(board, names_text):
    """Faults for codes on the board with no line in card-names.tsv, and for malformed tsv lines."""
    faults, named = [], set()
    for n, line in enumerate(names_text.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2 or not BARE_CODE_RE.match(parts[0]) or not parts[1].strip():
            faults.append((n, "-", "card-names.tsv line is not CODE<TAB>plain name"))
            continue
        named.add(parts[0])
    for row in board["items"]:
        if row["code"] not in named:
            faults.append((row["line"], row["code"], "no plain name in card-names.tsv"))
    return faults


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = Path(argv[0])
    names = None
    if "--names" in argv:
        names = argv[argv.index("--names") + 1]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"cannot read {path}: {type(e).__name__}")
        return 2
    board = parse_board(text)
    faults = list(board["faults"])
    if names != "-":
        npath = Path(names) if names else path.with_name("card-names.tsv")
        if npath.exists():
            faults += check_names(board, npath.read_text(encoding="utf-8"))
        else:
            faults.append((0, "-", f"no names file at {npath} (pass --names <path>, or - to skip)"))
    print(f"{path}: level {board['level']}, {len(board['items'])} rows, {len(board['runlog'])} run-log lines, "
          f"{len(faults)} faults")
    if faults:
        print(f"{'line':>5}  {'code':<14} fault")
        for n, code, msg in sorted(faults):
            print(f"{n:>5}  {code:<14} {msg}")
    for n, code, msg in sorted(board["warnings"]):  # warnings never fail the check
        print(f"{n:>5}  {code:<14} warning: {msg}")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
