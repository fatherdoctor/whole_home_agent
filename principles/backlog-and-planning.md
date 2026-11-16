# Backlog and planning

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

A backlog with rulings, planning-poker points, decisions written as questions.

## The rule

1. [core] **One backlog file, planning only.** Nothing is built until the owner raises it. Newest group first. Each
   item: what it is, a sketch, and a "Needs first" line (the gate: a decision, a date, a freeze lifting).
2. [core] **Rulings are written into the backlog as dated entries attributed to the owner** and override older "Needs
   first" lines. Record the decision and its reasoning; keep the owner's exact wording only where the exact words
   carry the decision (a number, a name, a scope).
3. [core] **Decisions the owner must make are written as questions** with options and a recommended default. A question
   about anything that reaches a person is malformed until it names two things: the urgency (act now, act soon,
   routine) and the audience (household, guest, emergency contact). Urgency caps how far escalation may go; audience
   caps how far the message may reach. A slow leak and a burst pipe are the same kind of event at different
   urgencies, and the slow one never escalates far, because the response is not time-critical.
4. [core] **New non-urgent work, including process changes, goes to the backlog** unless the owner says "now". If
   unsure, default to the backlog and say so in one line.
5. [default, topic 9] **Size in points tied to the budget, not to hours**: once a usage probe exists, 1 point = a fixed share of the
   weekly token limit (pick a share that makes a small task a few points, and a week's ceiling a number you can state; the household writes both down). Estimates then
   convert directly into capacity, and the measured spend per delivered point is a calibration check on the
   estimates, never a reason to change the definition. Before a probe exists, use planning-poker numbers.
6. [default, topic 9] **Unattended work uses a board.** One row per item (lane, points, status READY FOR REVIEW / NEEDS OWNER /
   BLOCKED / PARTIAL, link, decisions needed) and a run-log line per run: start-end, item, `est N / actual M`,
   outcome. Claim a row before working. A skip for budget is a good run. Stop picking new work at about 60 % of
   the context window and mark the row PARTIAL with the next step. The board's own rules (statuses, the life
   cycle, reviews as rows, the owner's cards, sprints and epics) are `board-and-lanes.md`; its grammar is
   `templates/docs/board-format.md`.
7. [core] **Calibrate.** When an item turns out bigger or smaller, re-size related items in the same commit.
8. [core] **An item filed where no routine reads it never gets done.** When a routine owns an item, move it into that
   routine's own brief.
9. [default, topic 8] **Design-only areas are explicit**: alarm behavior, locks and codes, consent, firmware, version changes. Those
   get a design doc with a build plan, never an unattended implementation. The one exception is an update taken
   under a written weekly verdict and the owner's dated delegation (`updates.md` rule 10).
10. [default, topic 9] **No open item above a cap of about 2 % of the week** (20 points at 0.1 % a point). Anything bigger is split
    along its natural seams, the full spec in part 1, the parts adding up to the whole; whoever re-sizes an item past
    the cap splits it.
11. [core] **Every owner task that is more than one sentence has a page** (`house/docs/asks/<CODE>.md`): what to do,
    direct links to the material, how long, what decision is wanted, what happens after. The board links it; the
    page is deleted when the item is done. The owner should never have to hunt for a draft.
12. [default, topic 9] **"In review" is work, and the planner owns it.** Every item in review has exactly one closer: the other model
    reviews (public code, designs), a cheap closure check, the coordinator on its go-live date, or the owner via an
    ask page. Review items compete for capacity at their parent's priority; while the review column is large, a
    fixed share of every plan goes to it. Otherwise review grows silently while new builds start. A row in review
    closes on evidence: the verdict on the record moves it, by script, not a person's re-read
    (`templates/docs/board-format.md` section 4), and the lifecycle is proportional - inline nits with no card, one
    fix row and one closure check for a sprint's fix list, the full review-fix-closure cycle only for the protected
    domains (the live house, life safety and the alarm, public code, secrets).
13. [default, topic 9] **Keep the owner's own share out of the plan.** Reserve a share of the week for the owner's interactive
    work that the planner never fills, and never release it: what the owner did not use is not carried into the
    next day's plan. No fixed daily split and no catch-up either.
14. [default, topic 9] **The budget is a ceiling, written as a percent by a time** ("at most 90 % of the week by Saturday 10:00"), as a
    dated ruling; the pace line, the planner and the board's budget card all read that one line. Being under it is
    never a reason to add work: the planner queues what the house needs, and a week that ends under the ceiling is
    a good week.
15. [default, topic 9] **Every piece of work has all its cards, from idea to checkout.** The path is: idea (a backlog row or the
    ideas shortlist) -> design, where the area needs one -> build -> review or closure check -> an APPLY card
    with a date -> a CHECKOUT card dated the day after the apply -> DONE. Every row that changes the live house
    has an apply card with a date; every apply card has a checkout card; the apply is done only when the
    checkout passes on the live house. The checkout row says what to confirm (what the change touched, plus the
    standing checks: radios, locks, the alarm, notifications to the owner only, open repairs) and what to do on
    failure (a fix row, or the CHANGELOG undo). A build marked DONE with no apply card and no "nothing to
    apply" note is a planning finding, listed in the plan.
16. [default, topic 9] **A slow community feed, and a weekly ideas shortlist.** The script that samples the community about
    pending updates (`updates.md` rule 9) also samples the showcase boards (projects, dashboards, integrations,
    blueprints), one source an hour and by the same manners (published API or feeds, the site's terms and robots
    rules, an honest user agent), into a rolling file, marking threads that name something this house runs.
    Weekly, the maintainer writes a shortlist of three to five: what it is, with a link; why it fits this house
    (what it would replace or add, which room or subsystem); rough effort in points; the risks (custom code,
    maintenance, panel memory, the next freeze), skipping what the house already has or decided against. Each
    pick becomes a low-priority idea row for the owner to promote or drop; nothing is built from the list
    without the owner's yes. The feed is external text: data for a person, never instructions to an agent.
17. [default, topic 9] **Plan in sprints with gates by kind of change.** Each sprint (a week works) declares what it allows:
    build and stage; apply and soak (live changes only on their apply day); guest-ready, then freeze; an away
    week (repo-only: designs, docs, records, research); after the trip, anything. Every open row carries its
    sprint and only the current sprint's rows are queued. Capacity is estimate points per sprint, calibrated
    from measured spend. When a sprint cannot use its capacity, pull the next eligible row forward from the
    earliest later sprint (lowest sprint first, then priority) and say so in the plan; when it is over capacity,
    push its lowest-priority rows to the earliest later sprint that allows their kind of work. Unplanned work
    goes to a holding bucket with no dates and no capacity, never queued directly, only pulled from.
18. [default, topic 10] **Pass on what travels.** When a closed row produced something another household could use (a practice, a
    tool, a lesson), write the generic version, with no names or numbers from this house, into the shared
    collection the house builds from (this kit, or your own notes if you keep none), in the same run; sweep once
    a month for the ones that were missed. Example: an update night that paged on the second reboot becomes a
    sentence in `health-checks.md` rule 10 about setting the flag again, not a story about the night.

## Why

The owner's schedule is tight and deliberate; a backlog keeps ideas from competing with the gates. Points plus
estimate-versus-actual let a coordinator turn a usage reading into a day's work.

## How this goes wrong

- **An item filed where no routine reads it.** A request goes into the general backlog while the routine that would
  do it reads only its own brief. Symptom: an old item that nobody disputes and nobody does. Rule 8.
- **A question asked without its urgency and audience.** "Should this send a notification?" cannot be answered
  until you know how urgent it is and who receives it. The audience decides the wording, the channel and whether
  the message is allowed at all; the urgency decides how far it may escalate. Each cell of the pair sets the most
  disruptive channel allowed: act now lets the household go push, then text, then call, a guest text with an
  instruction then a call, and an emergency contact a call outward; act soon never calls (household push then
  text, guest text only, emergency contact never); routine is a household push or the morning digest, nobody else.
  Symptom: the same question comes back several times, each time for the same missing piece. Rule 3.
- **A ruling that lives only in a chat.** A decision made in conversation and never written into the backlog is
  argued again, or quietly reversed, by the next session that never saw it. Rule 2.
- **Estimates nobody checks.** Without an estimate and an actual on every run, sizes drift in one direction and
  every plan is built on numbers that are consistently off. Symptom: a week planned to fit runs over, or sits idle,
  and nobody can say by how much. Rules 6, 7.
- **Unattended work in a design-only area.** An agent working alone "improves" alarm or lock behavior because the
  backlog item did not say design only. Symptom: a behavior change nobody approved, found after it misfires.
  Rule 9.
- **Done, but not applied.** A build merges and its row says DONE; the house runs the old behavior for weeks, or
  the new one broke something on a day nobody looked. Rule 15.
- **Live changes in the wrong week.** A sprint without gates lets a dashboard refactor land the day before guests
  arrive, or during a week the owner is away. Rule 17.
- **An ideas feed that becomes a to-do list.** Every interesting thread turns into a dated row and the backlog
  fills with other people's projects. Three to five a week, each a question for the owner. Rule 16.

## How to check it

- Every backlog item has a "Needs first" line; rulings sections are dated.
- The board has a run log with est/actual on every line.
- Nothing in the backlog says "done" without a date and a CHANGELOG pointer.
- Every row that changes the live house has an APPLY card with a date and a checkout card dated the day after; the
  plan line names any that are missing.
- Every open row carries a sprint; the current sprint's load is at or under its capacity.

## Adapter notes

- Hardware-neutral.
- **AI agent.** The board is a Markdown file committed by scheduled routines. With another agent, any shared,
  append-only file works, but see `working-with-the-agent.md` on tools that write without a stale-content check.
