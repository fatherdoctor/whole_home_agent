# The board and the lanes

*Status: written (KIT-BRD, 2026-10-25). Distilled from a real install that ran a board for two sprints with a planner
and five lanes; the failure modes are the ones it hit. The file format is `templates/docs/board-format.md`; the
file to copy is `templates/docs/board.md`; the planner's brief and the lane brief that levels 5-6 need
are not in v1.0 (`00-start-here/levels.md`, "Not in v1.0"); they will be written against this chapter; rule 20
added (KIT-BSLICE, 2026-10-31); rule 24's model-free merge job added (KIT-SYNC-1107, 2026-11-08); rule 7 lightened to the three tiers (KIT-LOW F14, 2026-11-09). Needs: nothing for the board itself;
`schedule` and `git_push` for lanes.*

One file is the only source of work. Every card has a life cycle with a review and a checkout. Every run leaves a
line. The owner's own tasks are cards too.

## The rule

1. [default, topic 9] **The board is the only source of unattended work.** `house/docs/board.md`, one Markdown file in the
   repository (`templates/docs/board-format.md` is its grammar). A lane that cannot find its work on the board does
   nothing and says so. A request in a chat, a note in a wiki queue or a line in another brief is not work until it
   is a row; whoever meets it makes the row. The backlog file keeps the rulings and the owner's questions; from
   level 2 its item list lives on the board.
2. [default, topic 9] **One row per card, six cells, one status word.** Item (`**CODE Title**` then the detail a lane needs), Lane (a
   role, never a model), Points (the kit's scale: 1 point = 0.1 % of the weekly limit, nothing above 20), Status (one
   word from the fixed list, then detail, then the tokens), Link (the deliverable), Decisions needed. The status word
   says what the row is; everything else explains. Codes are unique for the life of the board, closed rows included.
3. [core] **Claim before working; log after.** A run's first write is `IN PROGRESS <lane> <time>` on its row, committed and
   pushed; if the push races, re-fetch and pick again. Its last write is the row's finished word and one run-log
   line: `start-end lane CODE est N / actual M (outcome) helpers: ...`. A skip for budget is logged like a run. A run
   that never reached the board did not happen, as far as the next run can tell.
4. [core] **Finished means a closer passed.** A row is DONE only when its closer said so in one line with the date: the
   other model's review for a design or public code, a mechanical closure check for anything with nothing to judge,
   the on-box session on the apply day for a live change, or the owner through their card. A finished word never
   keeps a queue prefix: `QUEUED (12h) READY FOR REVIEW` is work for nobody.
5. [default, topic 9] **Every piece of work has all its cards, from idea to checkout.** Idea (a row) -> design, where the area is
   design-only -> build -> review or closure -> apply, dated -> checkout, dated the day after -> DONE. The apply row
   (`A-CODE`) and the checkout row (`CK-CODE`) are created in the same commit as any row that changes the live
   house; the checkout says what to confirm (what the change touched, plus the standing checks: radios, locks, the
   alarm, notifications to the owner only, open repairs) and what to do on failure (a fix row, or the CHANGELOG
   undo). A build DONE with no apply card and no "nothing to apply" note is a planning finding.
6. [default, topic 9] **The owner's tasks are cards in the owner lane** (`D-CODE`), created in the same commit as the row that will
   need them, `BLOCKED by CODE` until the owner's step is reached, then `BACKLOG (owner)` with an ask page
   (`house/docs/asks/D-CODE.md`: what to do, direct links, how long, the decision wanted, what happens after). The
   owner's cards count 0 toward capacity and are never pushed to a later sprint to make room. A row waiting on the
   owner says so in its own status (`NEEDS OWNER` or `BLOCKED by D-CODE`) and its Decisions cell names the card. The
   owner never has to hunt: a rolling `D-READ` card lists every row whose only open step is their read, each with a
   direct link and what "accept" does.
7. [default, topic 9] **Reviews are rows, by the other model.** When a row reaches READY FOR REVIEW, the planner (or at level 2 the
   session) adds `CODEr` right under it, at the parent's priority: one pass against the row; PASS -> the parent is
   DONE with a one-line verdict if the work has landed, else `PASSED - MERGE` naming what lands it and who (rule 24); FINDINGS -> the review file (`templates/docs/review.md`: High, Medium, Low, Nit, each
   reproduced or reasoned, each with its fix). A High or Medium finding, any finding in a protected domain
   (`templates/docs/board-format.md` section 4) or a fix over half a point gets a fix row `CODE.f` for the author's
   lane; Low findings and nits are carried by the author in its next push on the same branch, no row, and the verdict
   reads `PASS WITH NITS`. The fixes get a closure by the original reviewer: each finding fixed or reasonably declined,
   nothing newly broken, no new round - as a `CODE.fc` row only when the fix row was over 2 points, otherwise as one
   line `Closure: <commit> checked - PASS` appended to the review file in the reviewer's next run. Review stops at one
   level: a fix commit never gets its own `r` row. Public code and the protected domains take the full path (review,
   fix row, closure row) every time, however small the finding. The reviewer is never the author's model when the household has two; with one model, a fresh session that
   has not seen the work, or the owner.
8. [default, topic 9] **Kinds of review, by what changed.** A full review for the first publication of anything public and for any
   change of behavior or new feature; a diff-only check for a patch; none for wording, comments and tests. A closure
   check costs about half a point; a full review of a large branch about two. Points on review rows are the
   planner's to set.
9. [default, topic 9] **Review is work, and the planner owns it.** Every row in review has exactly one closer, written in its status
   (`-> closer: reviewer [review]`, `mechanical [closure]`, `lead <date> [apply]`, `owner [ask]`, `owner [read]`).
   Review rows compete at their parent's priority; while the review column holds more than about a third of a
   block's points, at least a third of every plan goes to it, and a lane never has more new builds queued than it has
   open reviews. Otherwise review grows silently while builds start, and nothing is ever DONE.
10. [default, topic 9] **Priority is a token, re-ranked by need.** `[P1]` to `[P4]` on every open row; no token reads as P3. A near
    need date, an epic target or a row that blocks a higher one raises a row; a date that moved out lowers it. A
    dated row can be built early; only its change to the house waits for its day. Spare capacity goes to the next
    priority down rather than waiting because the work is dated later; but spare capacity is never a reason to
    create rows (`backlog-and-planning.md` rule 14).
11. [default, topic 9] **Plan in sprints with gates by kind of change** (`backlog-and-planning.md` rule 17). The board's Sprints table
    says what each sprint allows; every open row carries its `[Sn]`; only the current sprint's rows are queued; the
    last sprint is the holding bucket (no dates, no capacity, pulled from, never queued). Capacity is estimate points
    per sprint, calibrated from measured spend; a full sprint is load at or under capacity, load counting one point
    per in-review row. Earlier sprints are filled first from later ones when they empty, lowest sprint then priority,
    only with work their gates allow.
12. [default, topic 9] **Epics are the long efforts; their targets are need dates.** Each epic has a goal, a done-when and a target in
    the Epics table; every open row carries one epic token or `[UPKEEP]`. An epic's target applies to every member
    without an earlier date, and every member sits in a sprint that ends by that target (an invariant: on a
    violation, pull the row forward, re-home a recurring row to upkeep, propose a split, or ask the owner for a new
    target; never leave it standing, never change a target yourself). Recurring upkeep has no epic: it is tracked
    and totaled, reassessed at the retrospective, and joins an epic only when it uncovers one.
13. [default, topic 9] **Two queue blocks, so the next one is never empty** (level 6). The planner runs twice a day (one full
    plan a day plus a rules-only evening check is on trial in the source house; twice a day stays the default until
    that trial is judged) and writes
    `QUEUED (12h)` on the next block's rows and `QUEUED (12-24h)` on the one after, within an allowance computed
    from the budget reading (`budget-and-pacing.md`) and the owner's reserve; a lane takes `(12h)` by priority (board
    order breaking ties), then `(12-24h)`, then its highest-priority eligible BACKLOG row, saying so. A run does one row (up to 20 points)
    or batches small ones (2 points or less each) up to about 4 points or 3 items, re-checking the budget gate
    before each. Lanes are limited by run slots as well as points: a block's queue for a lane fits
    `runs x batch`.
14. [default, topic 9] **One PLAN line per planner run, under 900 characters, in a fixed field order** (board-format.md section 8):
    budget read, allowance, each lane's block A and B, the review column, sprint load and capacity, epics, upkeep,
    waiting on the owner, superseded premises, plain names added, a projection. The owner reads one line and knows
    what the next twelve hours hold; the retrospective reads the sequence. Numbers a script can count (open rows,
    points per lane, review ages) belong in a generated facts file the PLAN line cites, so the line holds judgment.
    The format allows both: with a `facts: <path>` field the counted fields may be left out of the line; without one
    they stay in it (board-format.md section 8).
    **Anything the owner or the on-box session must do is a card, never a note in a PLAN line:** notes in plan
    lines go unread. Helper use is not counted as a goal; the run log's `helpers:` field is for cost, not a target.
    **Give each row to the cheapest role that holds the quality**: the interactive session only for what needs a
    person in the loop, and a helper only when it lowers total cost, never at the same model as its parent.
15. [default, topic 9] **A plain name for every card**, in `house/docs/card-names.tsv`, about ten words a non-programmer understands,
    added in the same commit as the card. The owner reads headlines, not codes.
16. [core] **Check the premises.** The planner keeps a short table of superseded terms (a dropped plan, a retired tool, a
    reversed decision) and each run cards every open row whose task still depends on one (the PLAN line's `stale
    premise` field names the card, rule 14); the on-box session clears them through that card. A row written for a plan that no longer exists is work nobody should start.
17. [core] **Calibrate, never rescale.** Every run-log line carries `est N / actual M`; the planner compares yesterday's
    measured spend per delivered point and flags a drift that lasts three days; neither changes the point's
    definition or the cards' sizes. When a row turns out bigger or smaller, re-size its siblings in the same commit.
18. [default, topic 9] **Retrospective each sprint, planning-only proposals applied by the planner.** The first plan of a new sprint
    queues the retrospective as the reviewer lane's first row; its proposals that are re-ranks, re-splits or lane
    moves the planner applies and names; everything else waits for the owner.
19. [core] **The board holds no secret and no quote.** Door and alarm codes, tokens, phone numbers and addresses never; the owner's words
    only where the exact words carry a decision (a number, a scope). Every write to it goes through the push guard.
20. [default, topic 9] **Runs read a slice of the board, not the board** (level 6, once the board is large). A tool prints what
    one reader needs: the newest planner lines, that lane's eligible rows in the order it takes them (the first
    few in full, the rest as code + status), the rows they depend on, its other open rows as codes and the recent
    run log; the planner gets every open row and no finished ones. The slice uses the board check's own parser,
    and the rule for "eligible" is one function shared with the run's preflight, so the two cannot disagree. The
    board stays the record: rows are edited there by code, and a reader that needs another row greps for its code.
    Outline: `templates/docs/board-slice-outline.md`; the shared function is `eligible()` in
    `templates/pacing/preflight.py`.
21. [core] **One run, then stop.** An unattended run does its item (or its batch), writes the board, pushes and ends. It
    never subscribes to pull-request or issue activity and never schedules a follow-up of itself: a subscribed or
    self-rescheduling run stays alive, wakes on every later commit or comment, and spends each time. Answers reach
    the next run through the board and the owner's cards, which it reads.
22. [core] **A lane pushes a message to the owner only when it must:** the run failed, it is blocked, or the owner has a new
    decision card. "I ran and all is well" is not a message; the run log says it. One short line, through the
    agent's own channel (the runtime's push), never a Home Assistant notification from a lane.
23. [core] **One executor per scheduled job.** A job that runs on a schedule has exactly one scheduler entry and one claim on
    the board; a second copy of the same job (a resumed conversation, a session cron, a duplicated routine) is a
    fault, not a backup. Jobs that must survive live in a real scheduler (the cloud scheduler, cron on the box),
    never in a session's own timer; the adapter page says how to spot a duplicate
    (`adapters/agents/<runtime>.md`, "Scheduled jobs"). The scheduler must not overlap runs of one lane
    (`flock -n pacing/<lane>.lock`, or the scheduler's own no-overlap setting): a lane's own claim is eligible so an
    interrupted run can continue, so a run that outlasts its interval would otherwise meet the next one on the same
    row.
24. [core] **Passed is not landed; every pull request has a merge owner.** A row is DONE only when its work reached where it
    runs (`templates/docs/board-format.md`, `PASSED - MERGE`). Every row that opens a pull request names, in its
    status, how it merges: `merge after <review> PASS` (nothing runs on the box) or `merge right after <apply card>
    passes` (a live change). One role owns merging, named in the owner's written ruling in `backlog.md` (usually the
    on-box session, never a cloud run): the forge often cannot record an approval on your own pull request, so the
    ruling IS the standing permission. The merge owner's first step each run is to land every PASSED - MERGE row
    whose review passed, and to put in place any file the box runs from its own copy; a deploy note's "this updates
    itself" is checked on the box, never trusted. The merge owner may be a model-free job instead of a session: when
    a review closes PASS, the reviewer writes a machine-readable merge token on the work card (the PR, the reviewed
    commit, and repo-only or the apply card it waits for); the job merges only a PR that carries a token, only while
    the PR head still equals the reviewed commit, only when the token's condition is met, then checks the merged
    diff equals the reviewed one and closes the card. A live change still waits for its apply card.

## Why

A single assistant session can work from a plain backlog because one mind holds the state. Unattended runs cannot:
each one wakes with no memory of the last, and two may wake at once. A file with claimed rows, fixed words and a
run log is the memory they share. The life cycle exists because "DONE" was the most misleading word on the first
board: a build that merged and a build the house ran were both DONE until the apply and checkout cards split them.
Reviews became rows because reviews that were not rows were never done. The owner's cards exist because an owner
who is not told what waits on them is the slowest lane in the system without knowing it.

## How this goes wrong

- **A row that nobody reads.** Work filed in a chat, a queue or a brief that no lane reads. Symptom: an old item
  nobody disputes and nobody does. Rule 1.
- **Done, but not live.** A build merged, the row said DONE, and the house ran the old behavior for weeks; or the
  new one broke something the day nobody looked. Rules 4 and 5.
- **Review that grows silently.** Builds start faster than reviews close; the board fills with READY FOR REVIEW
  and nothing is DONE. Symptom: a review column larger than a block's allowance for a week. Rule 9.
- **The author reviews itself.** The same model, or the same session, reviews what it wrote and finds nothing.
  Symptom: every review is a PASS; the first outside reader finds a High. Rule 7.
- **The owner as the hidden bottleneck.** Decisions left in a cell, a PR body or a chat; the owner never saw a
  card. Symptom: "waiting on the owner" rows older than a week, and an owner who did not know. Rule 6.
- **Two runs on one row.** No claim, or a claim not pushed; two lanes build the same thing on two branches.
  Rule 3.
- **A finished row still queued.** The planner prepended `QUEUED` to a row that then finished; the next lane read
  it as work and started again. Rule 4.
- **Duplicate codes.** Two rows share a code; the page shows the second as `CODE#2`, the run log cannot say which
  one ran, and a closer closes the wrong one. Rule 2.
- **Points by hours.** Estimates in hours drift with every model change; a budget in percent does not. Symptom: a
  week planned to fit runs over by a third. `backlog-and-planning.md` rule 5; rule 17 here.
- **A plan with no gates.** A dashboard refactor lands the day before guests arrive, or a live change in the week
  the owner is away. Rule 11.
- **Stale premises.** Rows written for a plan the owner dropped stay open and get built. Rule 16.
- **Every run reads the whole board.** By the second sprint the file is a hundred thousand tokens or more, and
  each lane run spends more reading rows it will never take than doing its item. Symptom: the cost per point
  rises week on week while the work does not change. Rule 20.
- **Two rules for "eligible".** The preflight that decides whether a run starts and the list the run then reads
  were written separately; the run wakes and finds nothing, or skips a row that was there. Rule 20.
- **Codes the owner cannot read.** `RS1.2r` on a card headline; the owner stops reading the board. Rule 15.
- **Reviewed and never merged.** Dozens of PRs pass review and wait for one busy session to merge them; work that
  is done reads as open for days. Rule 24.

## How to check it

- `python3 templates/docs/board_check.py house/docs/board.md`: six cells on every row, a known status word, unique
  codes, no queue prefix on a finished row, a closer on every in-review row (level 6), tokens on every open row
  (level 6) that resolve to the Sprints and Epics tables, a plain name for every code, both run-log shapes only.
- Every run in the lanes' schedule has a run-log line, with `est / actual` and `helpers:` on each.
- Every row that changes the live house has `A-CODE` and `CK-CODE`. For a row waiting on an owner decision,
  more than a sentence at level 2, or any such row at level 6, needs an open `D-CODE` named in its Decisions cell;
  an owner-lane row is its own card. No `D-` card is older than a week without a word from the owner.
- The review column (rows in review, by points) is at or under a block's allowance; no row has been in review for
  more than two plans without a closer.
- The newest PLAN line is under 900 characters and names every field, `none` where none applies.
- Grep the board for phone-number shapes, `token`, `password` and the household's names list, with `-l` (file names) or `-c` (counts) so a real hit never prints into the transcript: nothing.
- No PR has sat at review PASS for more than a day without merging (rule 24).
- Once a slice tool exists (rule 20): its tests show the slice and the preflight agree on every fixture row, and a
  lane run's log or input measure shows it read the slice, not the board.

## Adapter notes

- Hardware-neutral.
- **AI agent.** The board is a text file committed by scheduled runs, so it needs `git_push` and, for level 5 and
  up, `schedule` (`templates/runtime/FALLBACKS.md`). Without a scheduler, the owner starts a lane run by hand with
  the same prompt; the board does not change. With one model, the reviewer is a fresh session or the owner (rule 7).
  A runtime whose file tool writes without a stale-content check must re-fetch before every board write
  (`working-with-the-agent.md`).
- **Level 2** uses the Items and Run log sections and the status words only: lanes `agent` and `owner`, no queue
  prefixes, tokens optional, the session is its own planner (it picks the top eligible row and says so). **Level 6**
  adds the Plans, Sprints and Epics sections, the tokens, the two queue blocks and the PLAN line. Nothing in between
  needs a new form: level 5's one builder lane works a level-2 board with `builder` as a lane.
