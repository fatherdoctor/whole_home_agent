# The board file: format of record

*Status: written (KIT-BRD, 2026-10-25). The grammar of `house/docs/board.md` at every level, so that a person, a
lane and a script all read the same file the same way. The chapter that says why is
`principles/board-and-lanes.md`; the file a household copies is `templates/docs/board.md`; the checker is
`templates/docs/board_check.py`. Needs: nothing (a text file in the repository).*

The board is one Markdown file. It is the only source of unattended work: a lane that cannot find its work on the
board does nothing. Everything below is what a reader may rely on; anything the grammar does not fix is free text.

## 1. Where it lives and who writes what

| Path | What |
|---|---|
| `house/docs/board.md` | the board |
| `house/docs/card-names.tsv` | one plain-English line per card, `CODE<TAB>plain name` |
| `house/docs/reviews/<CODE>-<YYYY-MM-DD>.md` | one review file per review row (`templates/docs/review.md`) |
| `house/docs/asks/D-<CODE>.md` | one page per owner card that is more than a sentence (`principles/backlog-and-planning.md` rule 11) |
| `house/docs/backlog.md` | stays: the rulings and the questions for the owner (rules 1 to 3). From level 2 its item list moves to the board and its top says so. |

Write scopes, so that two writers never fight over one cell:

| Writer | May change |
|---|---|
| a lane (builder, reviewer, mechanical, writer) | its own row's Status, Link and Decisions cells; a new run-log line; new rows it is told to create (a fix row, an owner card) with their `card-names.tsv` line in the same commit |
| the planner | status words and the QUEUED prefixes, `-> closer:` tags, priority and sprint tokens, new review rows and their points, the PLAN and SPRINT CAPACITY lines, the Sprints table; never a row's title, detail, points or decisions text |
| the on-box session (`lead`) | anything, as the owner's hands; apply and checkout rows are usually its |
| the owner | anything |

Nobody rewrites another writer's text; a correction is a new line or a `Was:` note after the tokens (section 5).
Every write goes through the push guard; the board holds no secret, no phone number, no street address.

## 2. Sections, in order

Level 2 (one board, one session):

```
# <House name> board
<one paragraph: what this file is, the points scale, where the rulings live>
## Items
## Run log
```

Level 6 (the planner, more lanes) adds four sections and keeps the two:

```
# <House name> board
<paragraph>
## Plans          PLAN lines newest first, then the SPRINT CAPACITY line, then standing rulings (ROLES, PRIORITY)
## Sprints        one row per sprint: code, dates, what it allows, capacity
## Epics          one row per epic: code, name, goal, done when, target, owner
## Items
## Routines       (optional) recurring model work that is not a card: code, what, lane, points a run, runs a day
## Run log
```

A section is a level-2 heading with exactly that name; a tool may stop parsing at an unknown heading and must not
fail on one. Headings a household adds are allowed below `## Run log` only.

## 3. The Items table

```
| Item | Lane | Pts | Status | Link | Decisions needed |
|---|---|---|---|---|---|
```

One row per card, six cells, in this order. Open rows sit in priority order within their lane; the planner keeps
that order at level 6, the owner at level 2. Closed rows (DONE, DROPPED, RETIRED) stay where they are: the board is
also the record.

**Item.** `**CODE Title**` followed by free text: who asked and when, the detail a lane needs to do the work, why
it waits, in words. The machine-read "after" condition goes in the status cell (section 4), never only here: the
preflight and the slice do not read it in the Item cell, and the checker warns when an open row's Item cell says
`after <a code on the board>`. A runtime tag (`[BOX]`) may sit anywhere in the Item cell or the status. The code is the first word inside the bold; the title is the rest of the bold. A code
starts with a capital letter and has letters, digits, hyphens and dots only, no spaces (`N3`, `KIT-BRD`, `N3.f`,
`D-N3`). Codes are unique for the life of the board, closed rows included; before creating one, search the file.

**Lane.** Who does the work, as a role: level 2 `agent` or `owner`; level 5 adds `builder` and, for the review
habit, `reviewer`; level 6 adds `mechanical`, `writer`, `planner` and `lead` (the on-box session). `owner` remains
available at every level. A role may carry a part in parentheses,
`writer (manual)`. The household maps roles to models in `house/runtime.yaml`; the board never names a model.

**Pts.** The estimate on the kit's scale (1 point = 0.1 % of the weekly assistant limit; `principles/backlog-and-planning.md`
rule 5): a number, halves allowed (`0.5`, `2`, `12`). Nothing above 20: split first (rule 10). A note may follow
in parentheses (`8 (was 5: the tests doubled)`). Only the row's creator and the planner's re-size rule change it;
review rows' points are the planner's to set.

Without a usable usage reader, points remain rough planning estimates on this same scale. They are not hours;
do not claim they measure the household's allowance. Record `actual unknown` for an unmeasured run (section 7).

**Status.** Section 4.

**Link.** The deliverable: a pull request, a design document, a review file, an ask page, as a Markdown link or a
bare path. Empty until there is one.

**Decisions needed.** What the owner must decide, in one line, or `see D-<CODE>` when the row has an owner card
(it must, when the decision is more than a sentence: rule 11). Empty when nothing is needed.

## 4. Statuses

The status cell is, in order: an optional queue prefix, one status word, optional detail in free text, an optional
closer, then the tokens, then an optional `Was:` history. The word decides what the row is; the rest explains.

```
[QUEUED (12h) | QUEUED (12-24h) ]WORD[ detail][ -> closer: <lane>[ YYYY-MM-DD] [<what>]] [Pn] [Sn] [EP-x | UPKEEP][. Was: ...]
```

**"After" conditions** are written in the status cell, after the word: `BACKLOG (after X)` (X is DONE),
`BACKLOG (after X in review)` (X is in review or later), `BACKLOG (after X merged)`, and `(after X: met <date>)` once
X is archived. X is a card code on the board; a condition on an event that is not a card ("after the Tuesday
export") is `BLOCKED by <that event>` instead, because the preflight reads any capitalized word after "after" as a
code and a code not on the board is never met (it names the row on stderr when it skips for nothing eligible).

After a queue prefix the word may be left out: `QUEUED (12h) [P1] [S2] [EP-GUEST]` reads as a queued `BACKLOG` row
(the planner prepends the prefix and drops a leading BACKLOG, keeping every other word the status had).

| Word | Means | Set by | Leaves it when |
|---|---|---|---|
| `BACKLOG` | sized, not scheduled; `BACKLOG (owner)` is an owner card waiting on the owner | creator, planner | the planner queues it (level 6) or a session picks it (level 2) |
| `IN PROGRESS <lane> <time>` | claimed; the claim is committed and pushed before any work | the lane | the same run sets a finished word |
| `READY FOR REVIEW` | a deliverable exists; the row waits on its closer | the lane | the closer passes (DONE, or PASSED - MERGE when the work has not landed) or fails it (a fix row, `PARTIAL`) |
| `PASSED - MERGE <date> ... waits on <what lands it> -> <who merges>` | the review passed but the work has not reached where it runs: an unmerged branch or pull request, a file the box runs from its own copy not yet put in place. Written e.g. `PASSED - MERGE 2026-03-04 (review PASS) waits on PR #12 merge -> lead` | the closer | the named merge owner lands it (DONE with `landed: <commit or PR>`) |
| `NEEDS OWNER` | nothing moves until the owner decides; `Decisions needed` says what, or names `D-<CODE>` | the lane, the planner | the owner answers (the answer is a dated ruling in `backlog.md`) |
| `BLOCKED by <what>` | an input is missing: a file only the box has, a photo, an answer, another row. Never filled with a guess (`principles/working-with-the-agent.md` rule 12). | anyone | the input arrives |
| `PARTIAL` | work stopped short of the row; the next step is written in the detail; the next run continues it | the lane | the next run finishes |
| `DONE <date>` | the closer passed AND the work landed (merged, in place where it runs), and the row says so in one line; for a live change, its checkout card passed | the closer, or the merge owner from PASSED - MERGE | never |
| `DROPPED <date>` | will not be done; the detail says why and what replaced it | planner, owner | never |
| `RETIRED <date>` | a standing row (a routine, a cadence) that no longer runs | planner, owner | never |

Rules on the word:

- **DONE means landed.** A passed review on work still sitting on a branch is `PASSED - MERGE`, never DONE: a board of
  DONE rows over a pile of unmerged pull requests looks finished while the house runs none of it. As evidence for
  another row's review ("after X in review"), PASSED - MERGE counts as passed; as a dependency to build on ("after
  X"), it does not, because the work is not there yet. The checker requires the date, `waits on` and `-> <who>`.
- **A finished word never keeps a queue prefix.** Here the finished words are `DONE`, `DROPPED`, `RETIRED`,
  `READY FOR REVIEW`, `PASSED - MERGE`, `NEEDS OWNER` and `BLOCKED`: none is runnable by its queued lane. This does not mean they
  are all closed or complete. `QUEUED (12h) READY FOR REVIEW` is a fault. `IN PROGRESS` and `PARTIAL` may keep
  their prefix (work is left). The checker flags a prefix on any finished word.
- **The queue prefixes exist only at level 6.** `QUEUED (12h)` is the planner's next block; `QUEUED (12-24h)` the one
  after. A lane takes `(12h)` rows in priority order (board order breaks ties), then `(12-24h)` the same way, then
  (only when its lane has none) its highest priority `BACKLOG` row whose "after" is met, and says so in its run-log
  line.
- **Every row in review has exactly one closer** (`principles/backlog-and-planning.md` rule 12), written as
  `-> closer: <lane>[ YYYY-MM-DD] [<what>]`: `reviewer [review]` (a design or public code; the reviewer is never the author's model
  when the household has two), `mechanical [closure]` (tests pass, files exist, links resolve, nothing to judge),
  `lead <date> [apply]` (waits for its apply day), `owner [ask]` (an owner card exists), `owner [read]` (only the
  owner's read is left; the row is listed on the rolling `D-READ` card).
- **A row closes on evidence, by script.** When the closer's verdict is on the record (the verdict line of a review
  file, a closure check's DONE, a checkout card passed, a merge), a closing script moves the row to its finished word
  (DONE, or PASSED - MERGE when the work has not landed) and writes one run-log line naming the evidence; a person
  re-reading the row and typing DONE is not the mechanism. Three tiers keep review proportional: a **nit** (a fraction
  of a point, named by a review) is done on the same branch in the author's next run with no card and noted in the
  parent row; a **fix list** (a High or Medium finding, or a fix over half a point) gets one fix row and one closure - a `CODE.fc` row when the fix was over 2 points, otherwise a `Closure:` line in the review file; the **protected domains** (the live
  house, life safety and the alarm, public code, secrets) get the full lifecycle every time: review, fix row, closure.
  One review level: the reviewer is the other model.
- **Blocked by an event, never queued.** A row that can move only when something else happens (an export, an
  answer, another row's merge) is `BLOCKED by <that event>`, not `QUEUED`, so no worker wakes to re-check it; a lane
  that finds its row still waiting sets the word once, logs one line and takes its next row. Work that needs one
  particular machine carries a runtime tag in its Item cell (`[BOX]` for the house's own machine), a worker that
  cannot serve the tag skips the row, and the slice and the preflight read the tag anywhere in the Item cell.
- **A row that waits on the owner says so twice**: `NEEDS OWNER` or `BLOCKED by D-<CODE>` in its own status, and the
  `D-<CODE>` card in the `owner` lane.

## 5. Tokens (level 6; optional at level 2)

Tokens sit at the end of the status cell, after the detail and the closer, in this order; a `Was:` history may
follow them. A parser finds them by shape anywhere in the cell, so a hand-written row that puts them early still
reads.

| Token | Values | Rule |
|---|---|---|
| `[Pn]` | `[P1]` high, `[P2]` medium, `[P3]` low, `[P4]` back burner | every open row carries one; no token reads as `[P3]`. The planner re-ranks by need date and by what a row blocks; the owner's own call in a row is left alone. |
| `[Sn]` | a sprint code from the Sprints table; the last sprint in the table is the holding bucket | every open row carries one; only the current sprint's rows are queued; a row's sprint must end on or before its epic's target. |
| `[EP-x]` or `[UPKEEP]` | an epic code from the Epics table, or the upkeep mark | every open row carries exactly one. Recurring cards (weekly checks, monthly sweeps, checkouts after an epic's last apply) are `[UPKEEP]`: tracked and totaled, not part of an epic. Kept when the row closes. |

## 6. Codes: the family of a card

A piece of work is a family of rows with one root code. The suffixes are conventions, not grammar, but every tool
and every brief in the kit uses these:

| Row | Code | Lane | Points | Created by |
|---|---|---|---|---|
| the build or the design | `CODE` | builder (or reviewer for a design) | its estimate | the owner, the planner, a lane that splits |
| its review | `CODE` + `r` (`N3r`) | the other model, as reviewer | 0.5 a memo, 1 a design or small code, 2 a large branch | the planner, when the row reaches READY FOR REVIEW |
| the fixes a review asked for | `CODE.f` | the author's lane | sized by the fixer | the reviewer, with FINDINGS |
| the closure check of the fixes | `CODE.fc` (a row only when `CODE.f` was over 2 points; otherwise the reviewer appends `Closure: <commit> checked - PASS` to the review file, no row) | the original reviewer | 0.5 to 1 | the planner |
| the apply (a live change) | `A-CODE` | lead | 1 to 2 | whoever creates a row that changes the live house, in the same commit, with a date |
| the checkout, the day after the apply | `CK-CODE` | lead | 0.5 to 1 | the same commit as the apply row |
| the owner's card | `D-CODE` | owner | 1 to 4 of the owner's own time; counts 0 toward capacity | whoever creates a row that will need the owner at any step, in the same commit, `BLOCKED by CODE (...)` until that step |
| a split | `CODE.1`, `CODE.2` or `CODEa`, `CODEb` | as the parent | the parts add up to the parent | whoever re-sizes past 20 |
| a repeated card | `CODE-S3`, `CODE-2026-11` | as the parent | as the parent | the planner |

A `D-READ` card is the one rolling owner card: every row whose only open step is the owner's read is listed on its
ask page with a direct link and what "accept" does, and removed when read.

## 7. The run log

One line per run, newest first, in the declared local time zone (`principles/working-with-the-agent.md` rule 5).
Two shapes for a run (`M` is a number or the literal `unknown`), three for a budget skip:

```
YYYY-MM-DD HH:MM-HH:MM TZ <lane> <CODE> est N / actual M (<outcome in a few words>) helpers: none
YYYY-MM-DD HH:MM-HH:MM TZ <lane> <CODE> est N / actual M (<outcome>) helpers: <role> <what it did>
YYYY-MM-DD HH:MM TZ <lane> skipped: budget (week X %, <role> Y %, line Z %, read <YYYY-MM-DD HH:MM TZ>)
YYYY-MM-DD HH:MM TZ <lane> skipped: budget (count mode: N of M runs today)
YYYY-MM-DD HH:MM TZ <lane> skipped: budget (no usable read: <why>)
```

The three skip shapes are what `templates/pacing/preflight.py` prints on a budget SKIP: percentage mode, count
mode, and a reading too old, without a read time or without figures. Any of them may end with
`; month $X.XX of $Y.YY` when an API key's monthly cap was checked.

`est` is the row's estimate when the run began; numeric `actual` is the measured spend on the same point scale
(the planner's calibration check, never a reason to change the scale). When there is no usable usage reader or
the run's spend cannot be measured, write `actual unknown`, never the estimate, elapsed hours or a guessed zero.
Keep the numeric estimate for planning. An unknown actual is a completed log entry, not a budget skip or a claim
that the work is finished; the outcome says what happened. For example:

```
2026-03-02 09:00-09:20 CST agent ROUTER-1 est 3 / actual unknown (PARTIAL: the router step waits on the owner) helpers: none
```

A skip for budget is a good run and is logged like one. `helpers:` is never omitted: it is how cost is read, not a
target to raise. A run that did several small items writes one line per item.

**The archive.** The board keeps one sprint of history. When a sprint closes, its finished rows and the run-log lines
of its dates move verbatim to `docs/plans/board-archive/<sprint>.md` (the same Items and Run log sections, nothing
rewritten), and the board page reads the archive back, so counts and charts stay whole while the board stays small
enough to read in one slice. Codes stay unique across the board and the archive: a new row never reuses an archived
code, finished or dropped.

## 8. The PLAN line and the SPRINT CAPACITY line (level 6)

The planner writes one PLAN line at the top of `## Plans` each run, under 900 characters, in this order of fields
(a field that does not apply says `none`):

```
PLAN <YYYY-MM-DD HH:MM TZ> (planner): facts: <path> | none; budget read <time> week X % (<role> Y %), reset <when>;
lane cost F x; allowable A points next 12 h + B the 12 h after, routines R; block A: <lane> [CODE pts, ...], <lane> [...];
block B: [...]; in review: n rows / p pts (was q), closers set [...]; sprint S<n> load L / capacity C, <d> days
left, pulled forward [...]; epics: <code> done/total pts <on track | AT RISK -N | inconsistent (rows) | DONE>;
upkeep: S<n> <pts> planned / <pts> done; waiting on owner [D-CODE ask, ...];
stale premise [CODE (term) -> <card>, ...] | none;
plain names added N; projection: <points before the next gate>, at <points>/day done by <date>.
```

**Counted fields and the facts file.** Four fields are counts a script can make from the board: `in review` (rows,
points and the previous figure), the sprint's `load` and `capacity` with its days left, `epics` done/total points,
and `upkeep` planned/done. When the run has a generated facts file (a script writes it from the board before the
planner runs; `principles/board-and-lanes.md` rule 14), the line names it in `facts: <path>` and these four counted
fields are optional: leave them out, or keep only the part that is judgment (an epic's `AT RISK -N`, what was
`pulled forward`). Without a facts file, `facts: none` and all four are required. Every other field is judgment and
is required either way: the budget read and allowable points, the blocks, the closers set, waiting on owner, stale
premise, plain names added and the projection. Anything the owner or the on-box session must do is a card the line
names, never a task written in the line.

Right under the newest PLAN line, replacing the previous one: `SPRINT CAPACITY <n> (<date time>: <base> / <factor>)`,
the estimate points a sprint holds for lanes and routines after the owner's own reserve and the planning overhead.
The board page draws each sprint's ideal line to it.

## 9. What a parser may rely on

For `templates/docs/board_check.py` today and the board view (`KIT-BRDv`) and page (`KIT-BRDp`) later:

1. Section headings are exact (`## Items`, `## Run log`, and at level 6 `## Plans`, `## Sprints`, `## Epics`,
   `## Routines`). Content before the first heading is the header paragraph.
2. Inside `## Items`, every line that starts with `|` after the two header lines is a row with exactly six cells;
   a `|` inside a cell is written `\|`. A row whose Item cell does not start with `**` is not a card (a note row);
   the checker flags it, a renderer skips it.
3. The code is `^\*\*([A-Z][A-Za-z0-9.-]*)\s` on the Item cell; the title runs to the closing `**`.
4. The status word is the first match of the word list in section 4 after an optional queue prefix (a prefix
   not followed by a recognized status word reads as `BACKLOG`, retaining the remainder as detail); tokens are
   `\[P[1-4]\]`, `\[S[0-9]+\]`, `\[EP-[A-Za-z0-9]+\]`, `\[UPKEEP\]` anywhere in the cell; the closer is
   `-> closer: (\S+)(?: (\d{4}-\d{2}-\d{2}))? \[([^\]]+)\]`.
   Groups are lane, optional date, and purpose. The parser keeps `closer` as `(lane, purpose)` and exposes the
   optional date as `closer_date` (`None` for an undated closer).
5. Run-log lines match section 7's shapes; anything else under `## Run log` is a fault, not a crash.
   `parse_board` returns numeric `actual` values as floats and `actual unknown` as `None`; unknown is not zero.
6. The PLAN line is free text after its stamp; a renderer shows the newest whole; the SPRINT CAPACITY line's first
   number is the capacity.
7. `card-names.tsv`: comment lines start with `#`; every other line is `CODE<TAB>name`; every code on the board has
   a line, and the checker reports each one that is missing.

## 10. The level-6 form, by example

The full sample lives in `templates/docs/board.md` (level 2). This fragment shows what level 6 adds; the generic
house below is invented for the example.

```markdown
## Plans
PLAN 2026-03-02 05:30 CST (planner): facts: house/docs/plan-facts.md; budget read 05:12 week 31 % (reviewer 28 %),
reset Sat 22:00; lane cost 1.0x; allowable 28 points next 12 h + 30 the 12 h after, routines 2; block A: builder
[HC-2 8, N3.f 3], reviewer [N3r 1], mechanical [CK-A-N2 1]; block B: builder [GST-1 8], writer [MAN-3 4]; closers set
[N3 -> reviewer, HC-1 -> mechanical]; pulled forward [GST-1 from S3]; waiting on owner [D-N3 ask]; stale premise
none; plain names added 1; projection: 38 points before the freeze, at 9/day done by 03-06.
SPRINT CAPACITY 70 (2026-03-02 05:30: 70 / 1.0)
ROLES 2026-02-20 (owner): planner, builder, reviewer, mechanical, writer as mapped in house/runtime.yaml; lead = the on-box session.

## Sprints
| Sprint | Dates | Allows | Capacity |
|---|---|---|---|
| S1 | 02-21..02-28 | build and stage; live changes only on an apply day | 70 |
| S2 | 02-28..03-07 | guest-ready; house changes until 03-05 23:59, then freeze | 70 |
| S3 | 03-07..03-14 | away week: repo-only (designs, docs, records) | 70 |
| S4 | 03-14..03-21 | anything | 70 |
| S5 | holding bucket | unplanned work; no dates, no capacity; pulled from, never queued | - |

## Epics
| Epic | Name | Goal | Done when | Target | Owner |
|---|---|---|---|---|---|
| EP-GUEST | Guest-ready | A sitter can run the house for a week from the manual alone | guest pages printed, the walkthrough held, the freeze on 03-05 | 2026-03-05 | lead |

## Items
| Item | Lane | Pts | Status | Link | Decisions needed |
|---|---|---|---|---|---|
| **N3 Route every direct sender through the notification router** Owner 02-22: the two automations that call a phone directly go through `script.notify`. | builder | 5 | READY FOR REVIEW 2026-03-01 14:10 CST: draft PR #12, DEPLOY-N3.md -> closer: reviewer [review] [P1] [S2] [EP-GUEST] | PR #12 | see D-N3 |
| **N3r Review N3** One pass against its row; PASS -> N3 DONE; FINDINGS -> N3.f. | reviewer | 1 | QUEUED (12h) [P1] [S2] [EP-GUEST] | | |
| **A-N3 Apply N3 on the box** After N3r passes. | lead | 1 | BACKLOG 2026-03-04 [P1] [S2] [EP-GUEST] | | |
| **CK-N3 Checkout of N3, the day after** The two automations' traces show the router; nothing reached a phone that should not have. | lead | 0.5 | BACKLOG 2026-03-05 [P1] [S2] [EP-GUEST] | | |
| **D-N3 Which phone receives the "reminders" class?** | owner | 1 | BACKLOG (owner) [P1] [S2] [EP-GUEST] | [what the owner does](asks/D-N3.md) | |
| **UPD-S2 Weekly review-then-update** | lead | 2 | BACKLOG [P3] [S2] [UPKEEP] | | |
```
