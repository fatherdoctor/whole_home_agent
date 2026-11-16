# The levels: how far to take it, and how to tell you are ready for the next step

*Status: written (KIT-LEVELS, 2026-10-26; KIT-LEVELS.f 2026-10-27 enacted the KIT-LEVELSr review: check ids, the
skip-aware record, budget modes, the report-only boundary, evidence contracts; KIT-EXIST.a 2026-10-31 added the
existing-house section, the five `E0` lines and the `equivalent:` rule). For the person first, and for the
"what next?" helper, which runs the readiness tests on this page and suggests the next small step
(`tools/what-next/WHAT-NEXT.md`; levels 0-2 so far). Twenty minutes to read; you come back to one level at a time.*

The kit can run a whole machine: a board, a planner, builder lanes that work while you sleep, a monitoring agent that
fixes things at night, a staging copy of the house. **You should not install that machine.** You climb a ladder one
level at a time, and each level has a test that says whether it is working. Most households should stop at level 3
or 4: a well-kept, monitored house that tells you when something is wrong. Everything above that is for people who
enjoy running the machine, and the kit says so here so that nothing else in it has to push you upward. The ladder
is an offer, not a requirement: you can stop, skip a level or a test, or leave the ladder at any point; the helper
says once what the skipped part was there for, records your choice (`adoption.opted_out` or the rail's own
setting; a skipped level or test: `adoption.skipped`), and keeps helping (`AGENTS.md`, "The kit serves the owner").

On this page, **"level" means adoption level.** The kit uses the word in two other places with other meanings:
a phone's *notification level* (0 to 3, `principles/notifications-and-tiers.md`) and the monitoring agent's
*action level* (L1 to L4, `templates/tier2/BRIEF.md`). The house profile keeps them apart by name
(`adoption.level`, `people[].notify_level`, the agent's policy file).

## How the ladder works

- **A level is a set of pieces** (files, habits, one or two scripts). Every piece starts in its quietest mode: the
  fewest messages, the fewest runs, report-only where that is a choice. You turn things up later, never the kit.
- **Each level has a readiness test**: a short checklist. When every line passes, the level is working and you may
  start the next one. The test is not a quiz; it describes a house where the level's pieces are alive, not merely
  present. A level whose pieces are installed but whose test fails is *not* done.
- **The sign it is working is a standing check.** It is re-run every time you ask "what next". If it stops passing
  (the guard is no longer installed, a backup is missing this week, a review has waited 14 days), the helper
  suggests the fix and nothing new. Broken before new, always.
- **Every check has an id** (`L1-guard`, `R2-calendar`), written beside it in this page. The id is the name the
  helper, the log and `once_done` use; no helper invents another. Checks are tagged `auto` or `ask`. An `auto`
  check is one the helper (or you, with the file open) can verify from the repository, the box or the usage file;
  an `ask` check is one only you can answer, and the helper asks it in plain words and records your answer. A
  check marked `once` is done one time and recorded under its id with its date, and is permanent unless its line
  says `once per <period>`: then it is due again when that period has passed since the recorded date (the helper
  says "due", not "failed"). Every other check is re-run on every "what next". What each `auto` check reads, and
  what it answers when the evidence is missing, is in "Evidence the checks read" at the end of this page: a check
  whose evidence cannot be read answers `unknown`, never `pass`; a file the level itself writes and that does not
  exist yet answers `fail` (not written yet).
- **Where a test passes is written down**: `adoption.levels_passed` (every level whose test passed in full, with
  the date), `adoption.level` (the highest of them) and `adoption.skipped` (the levels and pieces you declined, with
  your reason) in `house/profile.yaml` (the block at the end of this page), by the helper with your OK or by you. A
  house without the block is at the level its tests say: the helper runs them upward from level 0 until one fails,
  which takes a minute; above level 3 it follows the needs-first rule below ("For the helper", detection).
- **Needs first** is the helper's rule for what it suggests; the ladder order is the recommended one. The helper
  suggests skipping a level only when no later level you want lists it under "Needs first", and never suggests
  skipping levels 0 to 3: each later level needs them. You may still skip anything, after one plain warning of
  what the later level loses.
  Levels 5 to 7 are not in v1.0 ("Not in v1.0" below), so the next three choices apply from a later version.
  Level 4 may be skipped by a household that wants lanes but no monitoring agent (level 5 then installs the budget
  gate itself, and level 7 is closed until level 4 is done). Level 6 may be skipped by a household that wants
  level 7 without the planner. Level 7 may be skipped entirely. A skipped level is recorded, not inferred: the
  helper never reads a level below `adoption.level` as passed unless `levels_passed` lists it.
- **Costs** are given twice: your own time (once, then per week) and the assistant budget in points, where one point
  is 0.1 % of your weekly assistant allowance (the same scale the board uses). The figures are from a real install
  and your house will differ; the usage card (`templates/README.md`, "Assistant usage card") shows your own.
- **Where a piece's template is not in the kit yet**, the level says what the piece must do and the templates index
  (`templates/README.md`) says what ships. A level is never gated on a template; it is gated on its test.

## The ladder at a glance

| Level | Name | What you get | Your time | Budget |
|---|---|---|---|---|
| 0 | A working house | Home Assistant installed, reachable at a stable name or address, backed up off the box | 2-4 h once | a few points |
| 1 | The repo and the habit | Every change in a private repository, with its undo written down, and a guard that keeps secrets out | 1-2 h once | ~10 points |
| 2 | One board, one session | The work on a board with statuses and points; one assistant session at a time, in a loop you can see | 1 h, then 1-2 h a week | what the items cost |
| 3 | Health and the weekly review | The house counts what is wrong; updates are reviewed before they are applied; a weekly digest; one restore drill | 2 h, then 20-30 min a week | ~10 points a week |
| 4 | The monitoring agent, report-only | A scheduled checker and a daily brief that explain, never act; a budget gate on its idle work (monitoring itself is never gated) | 2-3 h, then 10 min a day | 1-2 points a run |
| 5 | One builder lane (not in v1.0) | Unattended work from the board, delivered as change packages you apply; a review for every delivery | 2-4 h, then 30 min a day | the rows, plus ~1 point a run |
| 6 | The planner, the board page and more lanes (not in v1.0) | Two plans a day, sprints, epics, a burn-down page, your own card list | 6-10 h over a month, 15 min a day | ~12 points a day plus the lanes |
| 7 | The agent acts, staging rehearses (not in v1.0) | The agent fixes small things at night under your written policy; changes are rehearsed on a copy first | 6-12 h over a month, hardware for staging | 2-4 points a day plus the rehearsals |

**Recommended stopping points.** Level 3 for a household that wants a reliable house and a weekly habit. Level 4
for one that wants to be told, every morning, that nothing is wrong. Level 5 and up only if you want to run a small
software team and read what it did every day (not in v1.0).

**Not in v1.0: levels 5 to 7.** Version 1.0 supports the ladder through level 4. Levels 5 and 6 are described below
so you can see where the ladder goes, but the lane brief and the planner's brief they rely on, and the tools around
them, are not shipped yet; level 7 needs level 5's lanes. Do not improvise a lane or planner brief from these pages:
every fence a real lane needs lives in that brief. The side tracks keep their own gates.

## The levels

### Level 0 - A working house

**What it adds.** Home Assistant installed, onboarded and updated; reachable at a stable name or address; multi-factor
login on the owner account; automatic daily backups with one copy off the box; the emergency kit in two places; the
agent's secrets deny list, installed before its first read of the box (`adapters/agents/<runtime>.md`, "The secrets deny list"; the
standing rule "A secret in your output is a leak" in `AGENTS.md`). This
is the kit's Phase 0 (`AGENTS.md`), walked with the agent from `install/`. If Home Assistant is already installed
and onboarded when you arrive, the install steps are marked done from evidence and you start at
`install/network-and-backups-first.md`.

A router reservation is optional. The network goal also passes when you have declined router changes, recorded
that choice and the tested access kind in the profile, and can open the box using that name or current address.
Keep a private address in your note off the repository. The router may give the box a new address. Record how to
find it again; `install/network-and-backups-first.md` section 1 walks both routes. This does not waive the backup or other checks.

**Needs first.** Nothing. The agent may run on your computer or inside the box (`templates/runtime/STEP-0.md`).

**Cost.** 2-4 hours once; a few points (the agent reads and walks the guide; it does not build).

**The sign it is working.** A backup made this week is listed at the off-box location.

**Readiness test.**
- `L0-profile` `auto` `house/profile.yaml` exists with `setup.done: true` and `setup.installed_on` set.
- `L0-done-when` `ask` Every line of the "Done when" list in `install/network-and-backups-first.md` is checked, by
  you, from the box's screen.
- `L0-changelog-first` `auto` `house/docs/CHANGELOG.md` has its first entry, "Home Assistant installed (Phase 0)",
  with the date.
- `L0-backup-week` `ask` A backup from the last seven days is listed at the off-box location (the helper can read
  the box's backup list when it has box access; otherwise it asks).
- `L0-backup-proven` `ask` `once` The backup has been proven usable, either way: one backup downloaded to a
  computer and opened, or a restore rehearsed on a spare drive, board or VM. Record the date.

Five more lines apply only to a house adopted on path C (`setup.existing_house: true`; "An existing house" below):
- `E0-backup-first` `ask` `once` One backup was downloaded off the box (to a phone or a computer) **before** the
  inventory ran (`existing-house.md`, step 2); recorded under its own id in `once_done`. It does not stand in for
  `L0-backup-proven`: opening the archive, or rehearsing a restore, is that line's job, recorded separately and
  only when it happened, as its own words say.
- `E0-inventory` `auto` `house/export/` holds the twelve inventory files (the five every house has and the seven
  of path C) and `house/docs/inventory.md`, dated `setup.inventoried_on`, and the export is newer than the
  profile's last edit, or the helper says "stale".
- `E0-first-look` `auto` `house/docs/first-look.md` exists with its date and at least the backup, login and
  secrets lines, present with their result, whatever it is.
- `E0-untouched` `auto` The export taken at the end of Phase 0E (`house/export/.phase0e-end/`, written once) equals
  the one taken at its start (`house/export/.phase0e-start/`) on automations, scripts, scenes, helpers, areas,
  dashboards and integrations, **comparing definitions only**: ids, names, modes, options and ranges, areas and
  blueprint use, dashboard paths and card types, integration domains. On, off, `last_triggered`, `last_changed` and
  every other runtime field are left out (`export_house.py --diff` drops them): on a lived-in house automations fire
  during the thirty minutes of Phase 0E, and that is not a change by the agent. A file the person read to the agent
  (`source: person`) answers `unknown` for its part: two recitations are not a comparison. A difference in a
  definition is named and the line `fail`s; the CHANGELOG's Phase 0E entry then has to say what changed and why
  before level 0 is recorded.
- `E0-differs-written` `auto` `house/docs/policies.md` has the section "Where this house differs from the kit",
  with rows or "none yet".

**Record.** `adoption.levels_passed: [{level: 0, on: <date>}]`, `adoption.level: 0`.

### Level 1 - The repo and the habit

**What it adds.** A private git repository that holds the house's configuration and documents; the push guard as
the repository's pre-push hook, with the household's names list (`templates/guard/`); `secrets.yaml` and the rule
that a secret is named by its key, never quoted; `house/profile.yaml` filled by the Phase 1 interview; a CHANGELOG
with an undo on every entry (`templates/docs/CHANGELOG.md`); a gotchas file (`templates/docs/gotchas.md`).

**Needs first.** Level 0. An account at a git host, or a bare repository on a computer you own (the kit does not
care which; the guard runs either way).

**Cost.** 1-2 hours once (the interview is about half an hour); about 10 points.

**The sign it is working.** Every change to the house has a CHANGELOG line with its undo, written the same day.

**Readiness test.**
- `L1-remote` `auto` The repository has a remote and a dry-run push succeeds.
- `L1-private` `ask` Only the household can read the repository: a private repository at the host, or a bare
  repository on a computer you own that nobody else can log in to (no file says this; a host's "private" flag is
  one answer, access to the computer is the other).
- `L1-guard` `auto` Run `python3 guard/selftest.py --check-hook --repo . --remote origin` from the same place
  you push from. Exit 0 means the installed hook runs and the guard answered. Also require
  `python3 guard/selftest.py --guard-only` exit 0: the guard must block the planted fake secrets.
  A missing, broken or refusing hook needs repair. If this computer cannot run hook files, diagnose why before
  using the by-hand push in `templates/guard/README.md`. Record `L1-guard: method=manual; reason=<diagnosed restriction>`
  in the CHANGELOG. Run the guard successfully before every push and record its result. The helper calls this
  **manual**, never a passing automatic hook; a written claim alone does not prove protection. Check again when
  the computer, terminal or editor changes.
- `L1-ignored` `auto` `guard/names.txt` exists with at least one name and is ignored by git; `secrets.yaml` is
  ignored by git.
- `L1-topics` `auto` The profile's required topics are done: `profile.done: true`, or at least topics 1-4 and 8
  (people, areas, devices, priorities, the agent's limits) marked `done`.
- `L1-changelog-3` `auto` The CHANGELOG has at least three entries, each with an undo line.
- `L1-gotchas` `auto` `house/docs/gotchas.md` has at least one entry.
- `L1-secrets-undo` `ask` You can say, without looking, where your secrets live (the file, the kit, the password
  manager) and how you would undo your most recent change.

**Record.** `adoption.level: 1`. Side tracks R (records) and D (documentation) open here.

### Level 2 - One board, one session

**What it adds.** The board file `house/docs/board.md` (`templates/docs/board.md`, grammar in
`templates/docs/board-format.md`): one row per card with code, plain name, lane (`agent` or `owner`), points,
status, link and decisions; the nine status words of `templates/docs/board-format.md` (BACKLOG, IN PROGRESS, READY
FOR REVIEW, NEEDS OWNER, BLOCKED, PARTIAL, DONE, DROPPED, RETIRED; that file's table is the authority); a run log
with `est / actual` on every line; `card-names.tsv`. The backlog file keeps the rulings and the questions; its
items move to the board. One assistant session at a time works the Phase 2 loop (pick, plan, approve, build, test,
record, report; `AGENTS.md`). Points on the 0.1 % scale. Optionally, a page rendered from the board file, for
reading on a phone; the file stays the record.

**Needs first.** Level 1 (the CHANGELOG the board's DONE rows point at; the guard the board's commits go through).

**Cost.** 1 hour to learn, then 1-2 hours a week; the budget is what the items cost.

**The sign it is working.** Nothing is built that is not a row, and no row is IN PROGRESS for more than a week.

**Readiness test.**
- `L2-board` `auto` `house/docs/board.md` exists, `python3 templates/docs/board_check.py house/docs/board.md`
  exits 0, and none of the template's sample rows remain on it.
- `L2-backlog-moved` `auto` `house/docs/backlog.md` says at its top that its items moved to the board, and lists no
  items of its own.
- `L2-done-3` `auto` Three rows are DONE, and each has a CHANGELOG entry that names its code.
- `L2-runlog-3` `auto` The run log has a line per session: at least three lines, each with `est N / actual M`.
- `L2-in-progress-age` `auto` No row has been IN PROGRESS for more than seven days.
- `L2-own-row` `ask` You have written one row yourself and sized it.
- Optional: the owner-written row in [your first automation lesson](your-first-automation.md) can satisfy `L2-own-row`; the lesson is never required.
- `L2-statuses` `ask` You can say what each status means and who moves a row out of READY FOR REVIEW.

**Record.** `adoption.level: 2`. The helper asks, once, which pace you want for new pieces (on request, monthly,
biweekly, weekly) and writes `adoption.pace`.

### Level 3 - Health and the weekly review

**What it adds.** The health-check package on the box (`templates/packages/health-check.yaml`,
`templates/custom_templates/health.jinja`): one integer count per subsystem of things that are wrong, with notices
and unknowns kept apart (`principles/health-checks.md`), read on a dashboard and never re-implemented. The
notification router in its smallest form, you as the only audience (`templates/packages/notification-router.yaml`,
`notify.jinja`): health pushes go through it, and the full household model of classes, levels and audiences is
track H's first piece. The weekly review-then-update habit (`principles/updates.md`: read the notes, wait four or
five days, verdict, snapshot or backup, apply, check, CHANGELOG with the undo), as one board row a week. A weekly
digest to you: one message or one email a week with the health counts, what changed, and what waits; an automation
through the router is enough. The first restore drill (`templates/docs/board.md`, the DRILL-1 seed row).

**Needs first.** Level 2 (the weekly row lives on the board). Level 0's off-box backup, for the drill.

**Cost.** 2 hours once, 20-30 minutes a week; about 10 points a week.

**The sign it is working.** A health count rose, the digest said so, and you know why.

**Readiness test.**
- `L3-health-readable` `auto` The health counts are readable on the box and none has been unknown for more than
  seven days (the box's history of the count sensors; without box access, `unknown`, and the helper asks).
- `L3-health-fired` `ask` `once` Every health check has fired once from a simulated state (the CHANGELOG entry for
  the package says so), each in its own way: a fault check raised its subsystem's fault count and a dry-run push; a
  notice check (`silent`, `is_off`, a missing source, and the notice lines of `battery` and `above`) raised the notice count
  only, with no push, which is correct. A notice that did not push has passed. Record the date.
- `L3-update-applied` `auto` `once` One update has been applied through the review habit: a verdict of ALL CLEAR or
  CLEAR WITH ACTIONS written on the row or in a review file (a HOLD is a review, not an application), a CHANGELOG
  entry with the undo, and the next day's check noted on the row or in the entry (`principles/updates.md`). The
  three are tied by the update row's code: the CHANGELOG entry names it, the verdict is on that row or in the review
  file the row links, and the check is dated a later day than the entry. Any of the three not found is `fail`; a
  board or review file that cannot be read is `unknown`.
- `L3-restore-drill` `auto` `once` The restore drill has been done and its time written into
  `house/docs/operations.md` section 1.
- `L3-digest-4wk` `ask` The digest has arrived four weeks running (the helper reads the digest's log when it writes
  one).
- `L3-review-age` `auto` The last review row is under ten days old.

**Record.** `adoption.level: 3`. Track H (house features) opens here. **This is a good place to stop.**

### Level 4 - The monitoring agent, report-only

**What it adds.** The tier-2 monitoring agent (`principles/tier-2-support-agent.md`, `templates/tier2/`): the
scripted checker on a schedule, waking the model only on a finding; the brief; the journal; dedupe (one cause, one
warning); the daily brief. At this level the agent is **report-only**: it reads through the read wrapper, writes
the journal and the brief, pushes you through the router, and changes nothing in the house. Of the brief's action
table (`templates/tier2/BRIEF.md` section 3) only L1's *reads* are on; L1's reloads, and L2 and L3, are turned on
one at a time at level 7. Report-only is enforced, not promised: either no act wrapper is installed (the agent has
the read wrapper and nothing else), or the installed act wrapper's policy denies every verb that changes the house
and the check below proves it offline. The no-model preflight in front of every scheduled run
(`templates/pacing/preflight.py`, with `pace_gate.py` beside it, fed by `templates/runtime/usage_reader.py`'s JSON
in **percentage mode**, or the **count mode** of `setup.budget` - `runs_per_day` counted by the preflight,
`items_per_session` read by the brief - when the provider shows no usage figure; `principles/budget-and-pacing.md`
rules 3 and 7-9). The usage reader is unofficial: it reads the assistant's own login file and calls a usage address
the provider does not document, so whether to install it is your choice; count mode needs neither. **The checker itself is never budget-blocked** (`preflight.py --role monitor` always answers GO):
a house over its line must not go blind, least of all while the owner is away. The budget decides only its idle
work. Planned-restart markers so that maintenance is not an alarm (`principles/health-checks.md`).

**Needs first.** Level 3 (the counts the checker reads; the router it pushes through). A way to run on a schedule:
a runtime whose `house/runtime.yaml` entry says `can.schedule: yes`, or a cron on the box; failing both, you start
the run by hand each morning and the level still counts.

**Cost.** 2-3 hours once, 10 minutes a day to read the brief; 1-2 points a run, one or two runs a day.

**The sign it is working.** A week of briefs in which every finding is either explained or became a board row.

**Readiness test.**
- `L4-selftest` `auto` `python3 house/tier2/checker.py --selftest` exits 0.
- `L4-wake` `auto` A finding can wake the agent: the checker's schedule sets `WAKE_CMD`, and
  `python3 house/tier2/checker.py --wake-test`, run with that same setting, exits 0 and the agent answers that it got
  `T0:wake-test`. An unset `WAKE_CMD` (exit 2) is `fail`: the checker would only print "would wake". Run it again
  after any change to the wake command or the agent's session.
- `L4-schedule` `auto` A schedule exists for the checker (a scheduled task in the runtime, or a cron line), or
  `L4-hand-started` `ask` you have started it by hand on at least ten of the last fourteen days.
- `L4-journal-days` `auto` The journal has entries on at least ten of the last fourteen days.
- `L4-act-denied` `auto` The act path is closed. Two parts, both needed:
  - the act wrapper: none is installed, or the installed wrapper, run offline against its policy file, refuses a
    reload, a restart, a configuration change and a turn-off (each refusal names the policy) while a read and a
    journal line go through;
  - every other way to write: the agent's runtime settings (`house/runtime.yaml` names the file) deny it a shell,
    direct calls to the Home Assistant API that change state, Home Assistant tools that change state, and file
    writes outside the journal and the brief, and one harmless attempt through each is refused. A missing wrapper
    proves nothing on its own: a shell or a write-capable tool can change the house without it. Settings that
    cannot be read, or a runtime with no way to deny those paths, give `unknown`, never `pass`.
  A brief that *says* report-only is not evidence; the refusals are.
- `L4-gate` `auto` The preflight is in front of every scheduled run and works, in the mode the profile configures;
  the checker's schedule calls it with `--role monitor` (never budget-blocked; the gate decides its idle work only;
  the one exception is your off switch: while `pacing/STOP` exists the preflight answers SKIP for monitoring too,
  on purpose, so turning the agents off turns the checker off as well):
  - percentage mode (`setup.usage_probe: true`): the usage reading is under two hours old (the reader runs every
    15-30 minutes; a reading over 24 h old never runs), and the gate's log shows a run evaluated against the pace
    line in the last seven days;
  - count mode (`setup.usage_probe: false`): `setup.budget.items_per_session` and `setup.budget.runs_per_day` are
    set (`runs_per_day` above 0 once the checker is scheduled), and the gate's log shows the ceiling applied in
    the last seven days; the runs log (`pacing/runs.log`) has one `GO idle` line for each idle start the monitor
    was given, never more a day than `runs_per_day`;
  - either mode: `python3 pacing/pace_gate.py --file <an over-budget fixture>` exits 1 with a SKIP line (the helper
    writes a reading of 99 % read now, with a reset a week ahead, to a scratch file and runs the gate on it; a
    fixture with a past reset reads as last week's, and one read over 24 h ago skips for its age instead), and `python3 pacing/preflight.py checker
    --role monitor --usage <that fixture>` still exits 0 with `idle work: no`. A real skipped run is welcome evidence
    but not required: readiness must not depend on spending the week.
- `L4-threshold-tuned` `ask` `once` You have tuned at least one threshold (a CHANGELOG or gotchas entry names it).
  Record the date.
- `L4-false-alarms` `ask` False alarms in the last two weeks: fewer than two.
- `L4-findings-explained` `ask` Every finding in the last week is explained in the journal or is a row on the board.

**Record.** `adoption.level: 4`. **The second good place to stop.**

### Level 5 - One builder lane

*Not in v1.0 (see "Not in v1.0" above).*

**What it adds.** Unattended work from the board: one lane, a scheduled run (or a prompt you start by hand) that
takes the first BACKLOG row whose "needs first" is met, in board order (you order the board; the queue prefixes
belong to the planner at level 6), builds on a branch, never deploys, and delivers a change package: a DEPLOY file
with the exact edits, pre-checks, test plan and rollback, which you or an on-box session apply. It writes its
run-log line with `est / actual` and `helpers:`, and commits through the guard. The review habit: every READY FOR
REVIEW row gets a review row and a review file (`templates/docs/review.md`) by another model, a fresh session, or
you. The usage probe and the pace line in front of every run; the lanes `builder` and `reviewer` on the board.

**Needs first.** Level 3 (the health counts and the weekly review that tell you when a delivered change broke
something), level 2 (the board), level 1 (the guard), and the budget gate from level 4 (install it now if you skipped
level 4; `L5-gate` below checks it either way). A runtime that runs unattended: one whose `house/runtime.yaml` entry
says `can.schedule: yes`, or an on-box schedule (`templates/runtime/FALLBACKS.md`); without one, you start the lane
prompt by hand, and the level still counts.

**Cost.** 2-4 hours once, 30 minutes a day to apply and review; the rows' own points plus about 1 point a run.

**The sign it is working.** A lane run delivered a change you applied with one command and one CHANGELOG line.

**Readiness test.**
- `L5-runs-5` `auto` Five lane runs in the run log, each with `est N / actual M` and `helpers:`.
- `L5-board-runlog` `auto` `board_check.py` exits 0 and every run-log line matches a row's status change.
- `L5-review-age` `auto` No READY FOR REVIEW row is older than fourteen days without a review row.
- `L5-gate` `auto` The budget gate stands in front of the lane: the same test as `L4-gate`, in the configured
  mode, read from the lane's own gate log. It passes whether level 4 was done or skipped.
- `L5-deploy-cited` `auto` `once` One CHANGELOG entry cites a DEPLOY file from a lane branch.
- `L5-rejected-one` `ask` `once` You have rejected at least one delivery (sent a row back from READY FOR REVIEW, or
  dropped it), so that you know you can.
- `L5-guard-quiet` `ask` The guard has not had to stop a lane push (the run-log lines would say so).

**Record.** `adoption.level: 5`. The two keeping-current loops (below) may be turned on from here.

### Level 6 - The planner, the board page and more lanes

*Not in v1.0 (see "Not in v1.0" above).*

**What it adds.** The planner routine: two plans a day (one a day is on trial in the source house; two stays the
default until that is judged) (a budget read, the allowable points, two 12-hour blocks of
queued rows, a PLAN line and a SPRINT CAPACITY line; `templates/docs/board-format.md` section 8); the queue prefixes
`QUEUED (12h)` and `QUEUED (12-24h)`; priority tokens P1-P4, sprint tokens with a holding bucket, epics with
targets (section 5); a review burn-down with a named closer on every review; owner cards (`BACKLOG (owner)`) and ask
pages, so your own to-do list is on the board; plain names for every card; lanes by role (planner, builder, reviewer,
mechanical, writer); a retrospective at the start of every sprint. With it, and never before it, the full board
page: cards by column, a sprint selector, burn-down and burn-up with the capacity line, the all-work forecast, an
epics view, refreshed by a job on the box or in CI; the usage ledger; a measure of your own interactive use, so the
planner knows what is left for the lanes; the lane-cost calibration in each plan; the board, the card names file and
the CHANGELOG on the push guard's shrink list (`guard/shrink.txt`, `templates/guard/README.md`), because with
several lanes writing one file, a truncating write is the likeliest way to lose it. The planner's sprints are read
on the page, which is why the two arrive together.

**Needs first.** Level 5. A runtime with a scheduler for the planner (twice a day). Somewhere to publish the page
(the box's `www` folder, or a static page from CI).

**Cost.** 6-10 hours over a month, 15 minutes a day to read the plan and the page; about 12 points a day of planning
overhead plus the lanes. The page itself is deterministic scripts and costs no points.

**The sign it is working.** You read one PLAN line and the burn-down and know what will happen in the next twelve
hours; your owner cards show what waits on you.

**Readiness test.**
- `L6-sections` `auto` The board has the level-6 sections (Plans, Sprints, Epics) and `board_check.py` exits 0
  with tokens on every open row and a plain name for every code.
- `L6-plan-fresh` `auto` The newest PLAN line is under fourteen hours old; the page's newest refresh line is under
  a day old.
- `L6-two-sprints` `auto` `once` Two sprints have ended (two Sprints rows with end dates in the past) and the
  refresh log has no failed line between the first sprint's start and the second's end (`unknown` when the log does
  not reach back that far).
- `L6-retro` `auto` `once` One retrospective file exists and a later PLAN line cites a proposal from it.
- `L6-pace-held` `auto` For seven days the budget held, in the configured mode: percentage mode, every usage
  reading under the pace line, no run started on a reading over 24 h old, and the reserve never spent; count mode, no day with more runs than `runs_per_day`
  and no run past its ceiling (the gate logs).
- `L6-slope` `ask` `once` The burn-down's slope matched the plan at least once; you could say why when it did not.
- `L6-plan-aloud` `ask` You can read the latest PLAN line aloud and say what the lanes will do next.

**Record.** `adoption.level: 6`.

### Level 7 - The agent acts, staging rehearses

*Not in v1.0 (see "Not in v1.0" above).*

**What it adds.** The monitoring agent's action levels turned on one at a time (L1, then L2, then L3 with Hold and
Go; `templates/tier2/BRIEF.md` section 3), each named in your written policy and never beyond it; the single action
wrapper with its rate limits; Suggest on demand; the daily reset. A staging copy of the box (a VM or a second
machine) with a refresh procedure, a harness, baselines and a rollback drill; pre-checks on staging before updates
reach the house.

**Needs first.** Level 4 run report-only for at least a month, with the sign passing. Level 5 (the lanes that write
the rehearsals). Hardware for staging. Your policy file names each action level as you turn it on, with the date.

**Cost.** 6-12 hours over a month; 2-4 points a day for the agent plus the rehearsals' points.

**The sign it is working.** A change was rehearsed on staging before it reached the house; the agent fixed something
at night and the journal shows the act and its undo.

**Readiness test.** Not a gate: this is the top of the ladder. The standing checks are:
- `L7-undo-lines` `auto` every act in the journal has its undo line;
- `L7-staging-fresh` `auto` the newest staging refresh is under a month old (`house/docs/operations.md` section 1,
  the refresh entry's date);
- `L7-rollback-drill` `auto` `once per quarter` the rollback drill was done in the last 90 days (recorded in
  `once_done` with its date; due again, not failed, when the 90 days have passed);
- `L7-no-act-incident` `auto` no act happened during an alarm, a life-safety event or an open ask: every act line
  in the journal carries the rails the wrapper saw when it acted (`rails: clear`, or the rail that was up), and none
  says a rail was up (`unknown` for a journal whose act lines carry no rails field).

The side tracks and the keeping-current loops continue.

## The side tracks

A track is a set of pieces picked up one at a time, in order, any time after its gate level. The helper offers a
track piece only when the current level's sign is passing and the pace allows, and never more than one new piece at
a time. Each piece is small; its own readiness line says when it is done.

### R. Records and maintenance (gate: level 1, or the records-only gate; works with or without Home Assistant)

Rules: `principles/house-records-and-equipment.md`, `principles/maintenance-calendar.md`. Templates:
`templates/docs/house-records/`.

**The records-only gate.** A household with no Home Assistant (or none yet) opens this track when the repository
half of level 1 passes: `L1-remote`, `L1-private`, `L1-guard` and `L1-ignored`, plus `house/profile.yaml` with the
people and areas topics done. The rest of levels 0 and 1 is not needed for records; the helper records the track's
pieces as usual and `adoption.level` stays null until level 0 passes.

| Piece | What it is | Done when |
|---|---|---|
| R1 | The records inbox (one folder anyone drops photos and papers into) and the equipment inventory from label photos: one row per item, maker, model, the maker's schedule and the expected service intervals | `R1-inventory` `auto` the inventory has ten or more rows with a source photo each; `R1-found-fast` `ask` a thing broke and you found its model and manual in under a minute |
| R2 | The maintenance calendar: renewals, filters, service intervals, reminders 30 days ahead, no invites | `R2-calendar` `auto` every inventory row with a schedule has a calendar entry; `R2-reminder` `ask` one reminder arrived and you acted on it |
| R3 | Vehicles: the same inventory and calendar per car (registration, insurance, service) | `R3-vehicles` `auto` one row and one calendar entry per vehicle |
| R4 | Local service vendors: who to call, contractors and utilities, never maker help lines | `R4-vendors` `auto` every inventory row of a serviced kind names a vendor; `R4-called` `ask` you called one from the list |
| R5 | The breaker map and the shutoff and emergency guides (guest shutoffs first) | `R5-shutoff` `ask` someone else in the house found the water shutoff from the guide in under a minute |
| R6 | Floor plans and the component map | `R6-places` `ask` every inventory row has a place on a plan |
| R7 | The Records Clerk as a routine (reads the inbox, files, writes facts, makes calendar entries) | needs level 5 or a hand-run prompt; `R7-inbox-empty` `auto` the inbox is empty now (a snapshot: it does not prove every run succeeded; the clerk's run-log lines do) |

Cost of the first piece: about an hour to photograph labels, then 10 minutes per batch; 2-4 points a batch.
The sign the track is working: a thing broke and you found its model, its manual and who to call in under a minute.

### D. Documentation (gate: level 1; needs no lanes and fits a small plan with hand-run sessions)

Rules: `principles/documentation.md`. Templates: `templates/docs/wiki/SCHEMA.md`, `templates/docs/user-manual/`.

| Piece | What it is | Done when |
|---|---|---|
| D1 | The home wiki, right-sized: one page per house system, connected to Home Assistant or not (heating and cooling, water heater, plumbing and shutoffs, electrical panel, roof and attic, appliances, well, septic and irrigation where present, garage doors, network, generator, outdoor and structure, vehicles). Each page: what it is, where, its inventory row, how to operate it, how to shut it off in an emergency, its maintenance schedule, who services it, its history. One page per hand-run session from the inbox and the inventory; a coverage list says which systems have no page | `D1-coverage` `auto` every system on the coverage list has a page; `D1-found-fast` `ask` a thing broke and you found how to shut it off, who to call and when it was last serviced on one page |
| D2 | The user manual skeleton for the household and guests: one page per thing a person uses | `D2-guest-used` `ask` a guest or sitter used it for one thing without asking you |
| D3 | The page queue, the build check and the librarian routine (keeper, checker, manual writer in one run that writes only what has a queue item) | needs level 5 or a hand run; `D3-queue-empty` `auto` the queue is empty now and the build check passes (the build command is the one `house/docs/wiki/SCHEMA.md` names; none named, `unknown`) |
| D4 | The quick reference and the printed guest sheet | `D4-printed` `ask` the sheet is printed and where a guest will see it |

Cost of the first piece: about an hour to set up, then about 20 minutes and 1-2 points per page, by hand.

### H. House features (gate: level 3; needs the box; each a kit chapter plus a package or blueprint)

| Piece | What it is | Done when |
|---|---|---|
| H1 | The notification router for the whole household: categories, levels and audiences, every sender through it (`principles/notifications-and-tiers.md`; level 3 installed the router with you as the only audience) | `H1-why-who` `ask` for any message the house sent, you can say which category it was and why that person got it; `H1-no-direct-notify` `auto` no automation calls a notify service directly (the automations export) |
| H2 | The update policy and the freeze calendar | `H2-freeze` `auto` `house/docs/operations.md` names the freeze dates and the policy; the review rows honor them |
| H3 | The guest and visitor model: profiles, presence, what guests may control | `H3-guest-stay` `ask` one guest stay ran on it with no message to the guest you did not approve |
| H4 | Alarm and arming automations (design-only in the kit; you build with the agent under your own policy) | `H4-design-approved` `ask` the design is written, reviewed by a second session, and you approved it before anything was built |
| H5 | The contact ladder: who gets called, in what order, with consent recorded | `H5-consent` `ask` every person on it consented, in writing, in the profile |
| H6 | Wall panel patterns: kiosk, watchdog, memory checks | `H6-watchdog` `ask` the watchdog's restart count is on a dashboard and you can name the sensor (an `ask` until the kit's panel chapter names the sensor; then `auto`); `H6-week` `ask` the panel survived a week without a hand restart |
| H7 | Severe weather routing | `H7-warning` `ask` one real warning reached the right audience and nobody else |

Cost of the first piece: about 2 hours; 8-12 points.

## Keeping current

Two loops, both optional, both off until level 5:

- **Upstream.** The kit is published with tags. Your repository keeps the kit as a folder it can refresh (a git
  subtree, or a plain copy with a `KIT-VERSION` file); a monthly board row, mechanical lane, diffs the current tag
  against your copy and lists what changed, chapter by chapter, for you to take or decline. Nothing is overwritten:
  your files live under `house/`, the kit's under its own folders.
- **Carry-over.** Only if you publish (your own fork of the kit, or contributions upstream): the planner's rule that
  every DONE row with a reusable practice gets a kit row, and a monthly sweep. A household that does not publish
  gets the sweep as a reminder to write the lesson into `house/docs/gotchas.md` instead.

## An existing house

A house that already has devices, automations and dashboards (path C, `existing-house.md`) climbs the same ladder
with the same tests. Nothing is renamed or replaced to pass one; the kit's naming and rules apply to new work from
the adoption date, and the old is a tidy-up backlog you may never take. What changes is how the evidence is read.

**Five lines are added to level 0's test** (above, `E0-backup-first` to `E0-differs-written`), only for a house with
`setup.existing_house: true`: a backup downloaded off the box before the inventory, the inventory and the first
look written, the agent's first session proven to have changed no definition, and the "Where this house differs"
section present.

**What passes from evidence on day one.** `L0-profile`, `L0-changelog-first` (the Phase 0E entry), usually
`L0-backup-week`; `L1-remote`, `L1-private`, `L1-guard`, `L1-ignored` once the repository exists with the guard,
which `getting-the-kit.md` part 2 already installs; `L1-topics` after Phase 1. `L1-changelog-3` and `L1-gotchas`
count from the adoption date (three real changes, one lesson), not from the house's past: the house may be years
old and still at level 0 on the first day, which is the honest reading, and it reaches level 1 in its first week
of new work.

**Equivalents.** An `auto` check whose evidence is the kit's own template shape (`L3-health-readable` reads the
health-count sensors of `templates/packages/health-check.yaml`; `H1-no-direct-notify` reads for the router)
accepts the house's own mechanism when `house/docs/health-checks.md` (or `notifications.md`) records it under
`equivalent:` with the entity or automation ids to read: the helper reads those ids instead. With no `equivalent:`
line and no kit package, the check stays `unknown` and says what would let it read. The row is in "Evidence the
checks read" below; the early helper (levels 0 to 2) needs only the five `E0` lines (KIT-EXIST.d), and the
`equivalent:` rule reaches the helper's facts script when level 3 lands.

**What an existing house skips.** Nothing in the ladder. What it does not do: the install guide (done from
evidence), the Phase 0 setup interview (replaced by the inventory and four questions), the thirty-minute Phase 1
(twenty, pre-filled), and the generated build items it already has an equivalent for. Side track R (records)
opens at level 1 as today and is where a lived-in house usually goes first: it already has the equipment, the
manuals and the service history that track R files.

**A difference on the safety list** (an automation that arms, unlocks or changes a code with nobody in the loop; a
message reaching a person the owner never said may be messaged; a secret in the configuration; no backup off the
box; no second factor on an administrator) is said once, plainly, with the fix on offer, and after that is the
house's choice like any other "stands" row: it does not hold a readiness test open on its own. The ladder's own
lines still answer as they find: a house with no off-box backup does not pass `L0-backup-week`, whatever the
policies page says.

## For the helper: the `adoption` block

`house/profile.yaml` carries the ladder's state in one block (schema v2; `interview/profile-template.yaml`).
Written by the helper with the person's OK, or by the person; read by the helper and by every lane brief. A profile
without the block is read as "unknown level": the helper runs the tests upward from level 0 and proposes the block.

```yaml
adoption:
  level: 5                 # the highest level in levels_passed; null until level 0 passes
  level_passed_on: null    # date that level's test last passed in full
  levels_passed:           # every level whose full test passed, with the date; a level not here is not passed,
    - {level: 0, on: 2026-11-02}   # whatever `level` says
    - {level: 1, on: 2026-11-09}
    - {level: 2, on: 2026-11-20}
    - {level: 3, on: 2026-12-14}
    - {level: 5, on: 2027-01-10}
  tracks: {records: 1, documentation: 0, house: 0}   # the last piece done on each track; 0 = not started
  pace: on-request         # on-request | monthly | biweekly | weekly; on-request until level 2
  paused_until: null       # a date; until then only maintenance suggestions
  skipped:                 # levels (L4) and pieces (H6) declined, with the date and the person's reason; a piece is
    - {piece: L4, on: 2026-12-20, why: no monitoring agent wanted}   # not offered again for 60 days; a level stays
    - {piece: H6, on: 2026-12-01, why: no wall panel}                # skipped until a later level needs it
  opted_out:               # rails changed or dropped, or the kit's path left (what: kit-path), by the owner's choice
                           # after one warning; the helper never restores or re-offers one
    - {what: gotchas habit, on: 2027-01-05, why: keeps lessons in a notebook, undo: CHANGELOG 2027-01-05,
       checks: [L1-gotchas]}   # the check ids it turns off: still run and shown, never a "broken before new"
  last_suggested: null     # date of the last suggestion, so the pace can be kept
  last_new_piece: null     # date the last new piece was turned on
  once_done:               # the `once` checks that passed, by check id, with their dates
    - {check: L0-backup-proven, on: 2026-11-02}
    - {check: L7-rollback-drill, on: 2027-03-02}   # a `once per quarter` check: due again 90 days after `on`
```

**Reading a profile.** `level` is for the lane briefs: the one number that says how far the house has climbed.
`levels_passed` is for the helper: the levels whose standing checks it re-runs. The helper never infers a level
from `level`; a v2 profile that has `level` but no `levels_passed` (written before 2026-10-27) is read as levels 0
through `level` passed only up to level 3, because no level below 4 can be skipped; anything above 3 it re-tests
and records. A profile without the block (v1) gets the whole block proposed. The helper never writes `level`
upward on its own: it reports the test's result and asks.

**Detection: which level is the house at?** The helper does not stop at the first failing level; it follows
"Needs first":

1. Run the tests of levels 0, 1, 2 and 3 in order and stop at the first level whose test fails. Those levels
   cannot be skipped, so the walk is exact; the early helper (`tools/what-next/WHAT-NEXT.md`, levels 0-2) does
   exactly this and nothing more.
2. Above level 3, a level's test is run when every level its "Needs first" names is in `levels_passed`, with one
   substitute: level 5 may stand on a skipped level 4 when `L5-gate` passes. A level whose needs are not met is
   not tested; the helper names the missing level.
3. Each level ends in one of five words, kept apart in what the helper shows and records:
   - `passed` - every line of the test passed; the level goes into `levels_passed` with today's date (with the
     person's OK);
   - `failed` - the test ran and a line failed; the line is named; a failed line at a level already in
     `levels_passed` is a standing failure and comes first (broken before new);
   - `skipped` - in `adoption.skipped` by the person's choice; not tested, not offered again for 60 days, and
     named when a later level needs it;
   - `unknown` - a line's evidence could not be read (no box access, a log that does not exist yet); the helper
     says which line and what would let it read it, and treats the level as not passed;
   - `not needed` - above every level the house has or is climbing to, and named by no level's "Needs first"
     that the house wants (level 6 for a house at 7 without the planner; level 7 for most houses).
4. `level` is the highest level in `levels_passed`. Standing checks are re-run for every level in `levels_passed`
   and for no other.
5. **In v1.0 the helper stops at level 4.** It does not test levels 5 to 7; when the house has passed level 4 and
   asks "what next", it names level 5 as "not in this version" and offers the side tracks instead. Step 2 and the
   two examples below describe a later version.

Two worked examples (from a later version; not in v1.0):

- *Lanes without the monitoring agent.* A house at level 3 skips level 4 (`skipped: {piece: L4, ...}`), installs
  the budget gate and the lane, and passes level 5: `levels_passed` is 0, 1, 2, 3, 5; `level: 5`. Level 4 is
  `skipped`, not inferred as passed; the helper offers level 7 only after it names level 4 as needed first and the
  person turns it on.
- *The agent acts, no planner.* A house at level 5 with level 4 passed goes to level 7 without level 6:
  `levels_passed` is 0, 1, 2, 3, 4, 5, 7; `level: 7`; level 6 is `not needed`, offered as a new piece only if the
  person asks for the planner.

**The `once` keys.** Every `once` check's key is its check id as written beside it on this page, and nothing else
(`L0-backup-proven`, `E0-backup-first`, `L3-health-fired`, `L3-update-applied`, `L3-restore-drill`, `L4-threshold-tuned`,
`L5-deploy-cited`, `L5-rejected-one`, `L6-two-sprints`, `L6-retro`, `L6-slope`, `L7-rollback-drill`). A recorded
`once` is permanent except `L7-rollback-drill`, which is `once per quarter`: it is `due` when 90 days have passed
since its `on` date, and a new pass replaces the entry. A key not on this page is a mistake, not a new check.

## Evidence the checks read

Every `auto` check names here what it reads. A file the level itself writes and that does not exist yet gives
`fail` (not written yet); a file that exists but cannot be read or parsed, a history that does not reach back far
enough, or a box the helper cannot reach gives `unknown`, with the reason, never `pass`. A check that depends on
something only the person can see is tagged `ask` on this page until a template gives it a readable source.

| Check | Reads | Missing gives |
|---|---|---|
| L0-profile, L1-topics | `house/profile.yaml` | `fail` (no file yet, or keys absent), `unknown` (unreadable or not valid YAML) |
| L0-changelog-first, L1-changelog-3, L2-done-3, L3-update-applied, L5-deploy-cited | `house/docs/CHANGELOG.md`: `## YYYY-MM-DD` entries, an undo line in each (`templates/docs/CHANGELOG.md`); for L3-update-applied also the board row whose code the entry names, its verdict and dated next-day check, and the review file that row links | `fail` (no file yet, or no row, verdict or later-day check to match), `unknown` (unreadable) |
| L1-remote | `git remote`, `git push --dry-run` (the runtime probe, `templates/runtime/probe_runtime.py`) | `unknown` with `--no-network`, or when the remote cannot be reached or git fails; `fail` for no remote, a detached HEAD or refused authentication |
| L1-guard, L1-ignored | run `python3 guard/selftest.py --check-hook --repo . --remote origin` from the place you push; also run `--guard-only`; record whether the hook runs or the guard is run by hand; use `git check-ignore` and `git ls-files` to check private files stay out of git | a hook file alone is insufficient; manual protection needs confirmation; `unknown` when the selftest is skipped |
| L1-gotchas | `house/docs/gotchas.md`, entries: a `### ` heading with a `- **Incident:** <date>` line | `fail` (no file yet), `unknown` (unreadable) |
| L2-board, L2-backlog-moved, L2-runlog-3, L2-in-progress-age, L5-runs-5, L5-board-runlog, L5-review-age, L6-sections, L6-plan-fresh (PLAN) | `house/docs/board.md` through `templates/docs/board_check.py`'s parser: rows, statuses with their dates, run-log lines, PLAN lines; git history when a status carries no date | `fail` (no board yet), `unknown` (unreadable, or an IN PROGRESS row with no date until the history read lands) |
| L3-health-readable | the box: the health count sensors of `templates/packages/health-check.yaml` and their last seven days from the recorder (`/api/history/period`); the export file has no states and is not enough | `unknown` without box access |
| L3-restore-drill, L7-staging-fresh, H2-freeze | `house/docs/operations.md` section 1 (dated entries for the drill and each staging refresh) and the freeze section | `unknown` |
| L3-review-age | the newest review row on the board (`templates/docs/review.md`) | `unknown` |
| L4-selftest | `python3 house/tier2/checker.py --selftest` | `fail` (non-zero), `unknown` (missing) |
| L4-wake | the checker's schedule (its `WAKE_CMD`) and `python3 house/tier2/checker.py --wake-test` run with it; the agent's answer | `fail` (exit 2: no `WAKE_CMD`; exit 1: the command failed), `unknown` (no schedule found) |
| L4-schedule | the runtime's scheduled-task list (`can.schedule`), or the box's crontab | `unknown` -> ask L4-hand-started |
| L4-journal-days, L7-undo-lines, L7-no-act-incident | the journal the brief names (`house/tier2/journal.log` unless `house/docs/operations.md` says otherwise): one line per entry, starting with an ISO timestamp; an act line carries `undo:` and `rails:`; kept at least 90 days. `templates/tier2` honors this shape when the journal template lands | `unknown` (no file, or no `rails:` on act lines) |
| L7-rollback-drill | `house/profile.yaml`: the `adoption.once_done` entry for `L7-rollback-drill`; its `on` date is the drill, due again after 90 days | `unknown` (no profile) |
| L4-act-denied | the act wrapper's offline policy run (`ha_act --check-policy <policy file>` or the wrapper's own selftest), expecting a refusal for reload, restart, configuration and turn-off and a pass for a read and a journal line (no wrapper installed passes this part only); and the runtime's permission settings, named in `house/runtime.yaml`, with one refused attempt each through a shell, a state-changing API call, a state-changing Home Assistant tool and a file write outside the journal | `unknown` (a wrapper with no offline check, settings that cannot be read, or a runtime that cannot deny one of those paths) |
| L4-gate, L5-gate, L6-pace-held | `setup.usage_probe` and `setup.budget` in the profile; `usage/usage.json` (its `read_at`; `usage/latest.txt` for a probe-only install); the gate's log: one line per run, `<ISO time> RUN|SKIP <the gate's printed line>` (`pacing/gate.log` unless the brief names another), kept at least 30 days; the offline fixture run of `pace_gate.py` | `unknown` (no log or no reading) |
| L6-plan-fresh (page), L6-two-sprints | the page refresh log: one line per refresh, `<ISO time> ok|fail <words>` (`house/docs/page-refresh.log` unless the brief names another), kept at least 90 days | `unknown` |
| L6-retro | the retrospective file the board's RETRO row links, and the PLAN lines after it | `unknown` |
| R1-inventory, R2-calendar, R3-vehicles, R4-vendors | the inventory and calendar files under `house/docs/house-records/` (`templates/docs/house-records/`) | `unknown` |
| R7-inbox-empty, D3-queue-empty | the inbox folder; the page queue and the build check named in `house/docs/wiki/SCHEMA.md` | `unknown` (no build command named) |
| D1-coverage | the coverage list and the pages under `house/docs/wiki/` | `unknown` |
| H1-no-direct-notify | the automations export (`templates/export/export_house.py`) scanned for `notify.` service calls outside the router | `unknown` (no export) |
| E0-inventory, E0-first-look, E0-untouched, E0-differs-written (path C only, `setup.existing_house: true`) | `house/export/` (the twelve files and the two dated snapshot folders), `house/docs/inventory.md`, `house/docs/first-look.md`, `house/docs/policies.md`'s "Where this house differs" section; `export_house.py --diff <start> <end>` on definitions only | `fail` (not written yet), `unknown` (a `source: person` file in the comparison; the export's existing-house parts not landed) |
| the `equivalent:` rule (L3-health-readable, H1-no-direct-notify, and any later check that reads for a kit template) | `house/docs/health-checks.md` or `house/docs/notifications.md`: an `equivalent:` line naming the entity or automation ids that carry the house's own count or router; the helper reads those ids instead of the template's | `unknown` with what would let it read (no `equivalent:` line and no kit package) |
