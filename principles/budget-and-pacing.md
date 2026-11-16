# Budget and pacing

*Status: written (O1, 2026-10-11; KIT-GATE 2026-11-01: preflight, monitoring never gated, fresh reads, ceiling, API-key caps; KIT-DRY.f6 2026-11-10: rule 10, plain cost answers and the house's own budget line). Distilled from a real install; the failure modes are written generically.*

Reading AI usage, a pace line with a buffer, idle-time work.

## The rule

1. [core] **Read the account's usage with a zero-cost probe** (weekly percentage, model-specific percentage, reset time),
   save every reading with a timestamp, and publish the latest where routines can read it.
2. [default, topic 9] **Compute a pace line**: (100 − buffer) × the fraction of the week elapsed before the reset, or before an
   earlier target time the owner sets ("95 % by Saturday 10:00"; `templates/pacing/pace_gate.py --target`), capped at
   the target. Starting values: buffer 20 % when the owner is away, 10 % otherwise; no floor (`--floor 0`, the
   default) unless the early-week starve below actually bites, since a floor also lets a week start fast. **The line
   is a ceiling, not a target**: being under it lets a run start; it is never a reason to add work.
3. [default, topic 9] **A no-model preflight first, every scheduled run** (`templates/pacing/preflight.py`). The scheduler runs it and
   starts the agent only on GO, so a skipped run costs nothing. It checks, in order: the off switch; whether the
   lane has an eligible row (nothing eligible is a SKIP: an empty queue is a good run); the budget. Budget: run only
   if the reading is under the line (both the all-models figure and the model-specific figure for the expensive
   lane). If the reading is more than **two hours** old, require ten extra points of margin; so schedule the usage
   reader every 15-30 minutes, and the margin is for its short outages. A reading more than **a day** old (24 h,
   `--max-age-hours`), or one with no read time, **never runs**: a dead reader is a stop, not a margin, and the
   SKIP line says "no usable read" until the reader is fixed. If the reading's reset time is already past, it is
   from last week: treat it as 0 % with the stale margin, and only while it is under the day's age limit. **Monitoring is never budget-blocked**: the support
   agent's checks always run (`--role monitor`); the budget decides only its idle work (rule 4).
4. [default, topic 9] **Idle-time work**: an on-box agent does one read-only item from an idle queue per pass, only while under the
   line and while its session is under 70 % of its own limit.
5. [core] **Trim expensive routines.** Measure tokens per run; a quiet check-in should be deterministic and only wake
   the model when a line says CHECK; prefer fresh sessions to long-lived ones (most usage came from sessions
   active eight hours or more).
6. [core] **One new nightly run at a time**; when the chain is starving, the least critical writer pauses first.
7. [core] **An API key spends real money: hard caps, not a pace.** A pay-as-you-go key has no weekly reset to stop it.
   Set a per-run cap in the agent itself where the runtime has one (`adapters/agents/<runtime>.md`), a monthly cap the
   preflight enforces (`--month-usd`, from a spend ledger the run's wrapper appends to from the agent's own cost
   report), and the provider's own spending limit as the last fence. The kit ships no such wrapper: the owner
   writes it around the agent's print mode, and it must (a) append `YYYY-MM-DD <lane> <usd>` to the spend ledger
   from the agent's cost report after every run, or the monthly cap never bites; (b) log a run that changed
   nothing (no commit) as such; and (c) after two such runs in a row on the same eligible rows, stop the schedule
   (for example by writing `pacing/STOP` with a note) until the board changes.
8. [core] **One off switch.** A single file (`pacing/STOP`) stops every scheduled run, monitoring included, until the owner
   removes it. Turning things off must not need a scheduler edit at 2 a.m.
9. [default, topic 9] **No budget, no unattended run.** With no usage figure to read, the preflight counts instead (count mode:
   `setup.budget.runs_per_day`; the brief stops after `items_per_session` items). `runs_per_day: 0` means no
   unattended runs at all.
10. [core] **Cost in plain words, and the house's spending on its own line.** Asked "does the bigger model cost me
   more?", answer in two lines: on a monthly plan the price is fixed, and a bigger model uses the allowance faster,
   so its limit comes sooner; with an API key every token is billed, and a bigger model costs several times more
   per token (rule 7's caps). The house's own spending is a second budget line, never folded into the AI plan:
   hardware (a sensor, a radio stick, a backup drive) and services (Home Assistant Cloud, more cloud-drive room),
   each with its price, once or monthly, read from the seller's page on the day rather than remembered. Every cost
   the agent proposes says which line it goes on, and nothing is added to either without the owner's yes. Until
   `house/docs/operations.md` exists, the hardware and services line is a comment under `setup.budget` in
   `house/profile.yaml`.

## Why

The weekly cap has stopped a whole nightly chain before. A buffer is what lets the owner still use the agent when
something breaks while they are away.

## How this goes wrong

- **The cap hits mid-week.** Routines run whenever they like until the account is out, and the nightly chain
  (backups, docs, health) stops for days. Rules 1, 3.
- **A pace line that starves day one.** Early in the usage week a strict pace line sits below what is already
  used, so every slot skips all day. A floor fixes it. Rule 2.
- **A reading from last week.** A figure taken before the weekly reset reads near 100 % and every routine skips.
  When the reading's reset time is in the past, treat it as zero. Rules 2, 3.
- **A day-old reading.** The sampler stalls for most of a day; the gate reads 57 % while the week is really at 74 %,
  and the lanes run far past the line on a figure that was true yesterday. Rule 3 (two hours, then the margin; a
  day, then no run at all - ten points of margin does not cover a day-old read).
- **Paying for nothing.** Every scheduled run starts the model, which reads its brief and finds no work. On a real
  install a third of one day's API spend went on runs with nothing to do. Rules 3, 7.
- **Monitoring that goes blind.** The checker shares the builders' gate; the week runs hot, and the house is
  unwatched for days while the owner is away. Rule 3.
- **Spending to the line.** The spare allowance is read as an instruction and work is invented to fill it; the
  owner then finds their own reserve gone. Rule 2.
- **An expensive routine nobody measured.** A frequent pass re-reads a large context each time, or a crash leaves
  two schedules running the same job. Measure tokens per run before tuning anything else. Rule 5.
- **One budget for everything.** A helper weighs a monthly service against the AI plan's price, decides privately
  that the owner cannot afford both, and never offers the service; or a sensor bought for one automation is
  counted nowhere. Rule 10.
- **Several new routines at once.** Three nightly runs are added the same week and the chain starves; nobody can
  tell which one did it. Rule 6.

## How to check it

- The latest usage reading is less than two hours old (the reader's `read_at`).
- The checker's schedule calls the preflight with `--role monitor`; the lanes' schedules call it with their lane.
- Every skipped run has a log line in one of the board's skip shapes (`templates/docs/board-format.md` section 7):
  week %, line % and the read time in percentage mode; the day's run count in count mode; "no usable read" and
  why when the reading was too old or unreadable.
- The buffer value is written in the brief and matches the owner's current instruction.
- Every proposal with a price names its budget line (the AI plan, or hardware and services), and the house's
  hardware and services line exists in the profile or `house/docs/operations.md`.

## Adapter notes

- Hardware-neutral.
- **AI agent.** The runtime's usage reader (`templates/runtime/usage_reader*.py`, one per runtime) reads its usage figure;
  the gate reads the reader's JSON directly (the first runtime's screen probe is `templates/pacing/usage_probe.sh`).
  Another provider needs its own quota read; if none exists, use count mode (rule 9) and, for an API key, the
  caps in rule 7.
