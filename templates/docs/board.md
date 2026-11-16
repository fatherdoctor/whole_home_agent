# <House name> board

**Status (YYYY-MM-DD): started at level 2 from `templates/docs/board.md`. The only source of work for every session
and lane. Points: 1 point = 0.1 % of the weekly assistant limit. Rulings and questions for the owner stay in
`backlog.md`; its item list moved here on this date.**

<!-- Template: templates/docs/board.md (kit KIT-BRD). Format of record: templates/docs/board-format.md.
     Chapter: principles/board-and-lanes.md. Check it: python3 templates/docs/board_check.py house/docs/board.md
     How to use it:
     - One row per card, six cells: Item (**CODE Title** then detail), Lane (agent | owner at level 2), Pts, Status,
       Link, Decisions needed. Codes are unique for the life of the board; search before you make one.
     - Status words: BACKLOG, IN PROGRESS <lane> <time>, READY FOR REVIEW, NEEDS OWNER, BLOCKED by <what>, PARTIAL,
       DONE <date>, DROPPED <date>. Claim a row (IN PROGRESS, committed) before working on it.
     - Every row that changes the live house gets its apply row (A-CODE, dated) and its checkout row (CK-CODE, the day
       after) in the same commit; every row that will need the owner gets its D-CODE card in the same commit.
     - Every code gets a line in card-names.tsv in the same commit: CODE<TAB>plain name, about ten words.
     - The run log: one line per run, newest first, with `est N / actual M` and `helpers:` on every line. Without a
       usable usage reader, keep the estimate for planning and write `actual unknown`; never invent a measurement.
     - Level 6 (a planner and more lanes) adds the Plans, Sprints and Epics sections and the [Pn] [Sn] [EP-x] tokens:
       board-format.md sections 2, 5 and 10. Do not add them before the planner exists.
     The five rows below are a seed showing one of each kind: replace them with the house's own as they are written;
     keep the run-log line until the first real one replaces it. Delete this comment then. -->

## Items

| Item | Lane | Pts | Status | Link | Decisions needed |
|---|---|---|---|---|---|
| **PORCH-1 Porch light on at dusk, off at the owner's bedtime** The first request (backlog item 1). Dusk from the sun; bedtime from `input_datetime.house_bedtime`; the light is `light.porch`. Test: trigger by hand in Developer tools, read `last_triggered`, nothing sent. | agent | 2 | DONE 2026-01-20 (CHANGELOG 2026-01-20 "Porch light at dusk", undo in the entry) | | |
| **ROUTER-1 The notification router** Copy `templates/packages/notification-router.yaml` and `templates/custom_templates/notify.jinja`; phones from `docs/notifications.md`; dry-run every class; the owner sends the first real push. | agent | 3 | READY FOR REVIEW 2026-01-24 19:40 CST: `ha/packages/notification_router.yaml` on branch `build/router-1`, dry run logged every class, nothing sent -> closer: owner [read] | branch `build/router-1` | Which phone gets the "reminders" class: the owner's only (recommended), or every adult's |
| **HEALTH-1 The first health count** Copy `templates/packages/health-check.yaml` and `health.jinja`; CHECKS from `docs/health-checks.md`; make every check fire once from a simulated state. | agent | 3 | BLOCKED by ROUTER-1 (health pushes go through the router) | | |
| **DRILL-1 Backup restore drill** Restore the newest backup to the drill target; time it; write the time into `docs/operations.md` section 1. | owner | 1 | NEEDS OWNER | | A drill target: a spare boot drive, a second board, or a VM on the owner's computer; or set the drill to quarterly and say so in `docs/operations.md` |
| **MANUAL-1 The manual's first chapter** `docs/user-manual/` "Everyday": the porch light, in plain words, for the household. | agent | 2 | BACKLOG (after PORCH-1: met) | | |

## Run log

2026-01-24 19:05-19:40 CST agent ROUTER-1 est 3 / actual 2 (READY FOR REVIEW: router package on `build/router-1`, dry run clean, nothing sent) helpers: none
