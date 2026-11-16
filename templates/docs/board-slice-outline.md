# Board slice: a tool outline

*Status: written (KIT-BSLICE, 2026-10-31). An outline, not code: the house's agent writes `house/docs/board_slice.py`
from these steps once the board outgrows a run's reading (rule of thumb: past about 100 KB, or when a lane run
spends more on reading the board than on its item). The rule is `principles/board-and-lanes.md` rule 20. Lived on
a real install: the board was about 160 thousand tokens long by its second sprint; a lane's slice was 7-16 KB.*

## What it answers

"What does THIS run need from the board?" One command per reader prints a few KB; the board stays the record,
and every edit is still made to the board by code, never to the slice.

    python3 house/docs/board_slice.py <lane>    # a build or review lane
    python3 house/docs/board_slice.py --plan    # the planner: every open row, no finished ones

## One parser, one eligibility rule

- **Parse with `templates/docs/board_check.py`'s `parse_board`**, the same parser the board check and the board
  view use. A row the check accepts is a row the slice sees; a second parser drifts within a week.
- **Eligibility is one function** (`eligible(row, lane, now)`), imported by the slice AND by whatever decides
  whether a lane run starts at all (the run's preflight, next to `pacing/pace_gate.py`). If the preflight and the
  slice disagree, a run either wakes for nothing or skips work that was there. The function reads the lane, the
  status word and queue prefix, the "after" condition, a `[BOX]` or other runtime tag the lane cannot serve, and a
  claim by another lane. An "after X" is met when X reached the state the condition means, not only when X is
  finished: a review row's parent is in review, an apply row's parent is merged. Write the state into the
  condition ("after X in review") or mark it ("after X: met <date>") so the function does not have to guess.

## A lane's slice, in this order

1. **Calibration:** today's calibration lines for every lane (done marks kept), live hand-off lines from today and
   yesterday, and only the newest line of each kind the planner writes (PLAN, capacity, budget).
2. **The lane's rows:** rows named by its open calibration line first, then its eligible rows in the order the
   lane brief takes them (its own claimed rows, `QUEUED (12h)`, `QUEUED (12-24h)`, then BACKLOG; inside each block by
   priority, board order breaking ties: `preflight.ordered()`). The first few verbatim (as many as a run may batch, plus one or two); the next ten
   as code + status.
3. **Their dependencies:** the rows those name in their status ("after X", "BLOCKED by X"), as code + status.
4. **The lane's other open rows** as codes only, grouped by waiting, blocked and in review.
5. **The lane's routines and the run log:** the last ten lines, plus the lane's own last three.

The `--plan` slice is the calibration block, the Sprints and Epics tables, every open row verbatim, the routines
and the last twenty run-log lines. Finished rows (DONE, DROPPED) are never printed; a reader that needs one greps
the board for its code.

## Failure behavior

- The board cannot be read or parsed: print `FAILED <reason>` and exit 1; the brief then says to grep the board's
  calibration section and the lane's rows by hand. Never print a partial slice as if it were whole.
- Exit 0 printed, 1 failed, 2 bad arguments. Standard library only; `--ref <git ref>` reads the board at a ref,
  `--now <ISO time>` fixes the clock for tests.

## Changes to the briefs (the same commit)

- The lane brief (levels 5-6, not in v1.0; when it is written): "read the slice, not the board; grep the board for a named code; edit rows on the board by code."
- The planner's brief: "read `--plan`." Measure one run's input before and after and note it on the row.
- Optional, once finished rows dominate: move DONE rows older than a few days into a dated archive file the slice
  never reads (codes stay unique across the archive, `board-and-lanes.md` rule 2).

## Tests for the tool

- A fixture board with one row of each status word, a claimed row, a row with an unmet "after", a review row
  whose "after" is met because its parent is in review, and a `[BOX]` row: the slice prints exactly the eligible
  ones, in order.
- The slice and the preflight agree on every fixture row (call both; one shared function makes this trivial).
- A malformed board prints `FAILED` and exits 1.
- A lane with nothing eligible prints its sections with an empty rows list, so the run logs "nothing eligible".

## Cost

Nothing on the box. Saves most of every run's reading once the board is large; costs one small script and its
tests.
