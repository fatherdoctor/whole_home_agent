# The principles, in reading order

*Status: written (O1, 2026-10-11).*

Eighteen files. Each has the same five sections: **The rule** (imperative, numbered), **Why**, **How this goes
wrong** (the generic failure modes a typical install hits: the pattern, the symptom you would see, the rule it
motivates), **How to check it** (a grep, a lint, a review question) and **Adapter notes** (what changes per
radio, voice assistant, hardware, notification channel or agent; a core rule never changes, a default is the
interview's to set).

**Core and default (O1r F1, 2026-10-30).** Every numbered rule opens with a tag. `[core]` holds in any house: one
router, never send to verify, positive evidence, consent keyed to the number, life safety bypasses the levels, read an id
back. `[default, topic N]` is a starting value or a chosen shape this install found good (the four notification
levels and their class mapping, the ladder's shape, three pushes per hazard a day, Stay-only auto-arm, one switch
per code, the pace line's buffer and floor, the board and its sprints): the Phase 1 interview's topic N
(`interview/phase-1-house-profile-interview.md`) is where the household changes it, and what it writes into
`house/profile.yaml` and `house/docs/policies.md` outranks the default. An agent never imposes a default the
household has answered differently, and never changes a core rule.

Read them in this order. The first four are the ground every later file stands on.

| # | File | One line | Leans on |
|---|---|---|---|
| 1 | `working-with-the-agent.md` | Approvals, never send to verify, report faithfully, verify before claiming, secrets never in the repo. | - |
| 2 | `naming.md` | Names are for people, ids are the handle; read an id back, never guess it. | 1 |
| 3 | `automations.md` | Native conditions over templates, deliberate `mode`, positive evidence, idempotence, traces, restart artifacts. | 2 |
| 4 | `notifications-and-tiers.md` | One router, classes and levels, tags, one push per event, consent, the ladder, audience first. | 1, 3 |
| 5 | `safety-and-security.md` | What an agent or voice assistant may never do; Stay-only auto-arm; one switch per code; life safety inverts the rules. | 4 |
| 6 | `health-checks.md` | One count per subsystem, faults vs notices, stale is a state, watch the watchers, every check must be able to fire, time the reboot of a device that slides. | 3, 4 |
| 7 | `dashboards.md` | The 30-day test, seven kinds of thing, nothing settable on a first tab, the live page is the truth, test on the glass. | 2, 6 |
| 8 | `testing-and-simulation.md` | Nothing audible or sent, dry runs, replay history (and real pushes through a changed router), glass tests, an isolated clone, persona simulations. | 1, 4 |
| 9 | `change-control.md` | Freeze, pin, stage, rehearse, a fully successful config check, a rollback of record, a drift log. | 8 |
| 10 | `backups-and-recovery.md` | Tiers by failure with measured rollback times, off-box copies, monthly restore drills, backup size under each destination's cap. | 9 |
| 11 | `documentation.md` | CHANGELOG, gotchas, a household manual, a maintainer wiki (a file per page, archived manuals readable, honest page rules) with facts and citations, the live export outranks prose. | 1 |
| 12 | `backlog-and-planning.md` | One backlog, dated rulings, decisions as questions, points, a board with est/actual. | 11 |
| 12b | `board-and-lanes.md` | One board file as the only source of unattended work; claim, review, apply, checkout; the owner's cards; sprints, epics, one PLAN line; a slice per reader once the board is large. | 12 |
| 13 | `budget-and-pacing.md` | A usage probe, a pace line with a buffer and a floor, a budget gate before every unattended run. | 12 |
| 14 | `tier-2-support-agent.md` | An always-on watcher behind the automated back-stops, with enforced levels, a never list and its own health. | 5, 6, 13 |
| 15 | `house-records-and-equipment.md` | Photos and documents in, an inventory, archived manuals, procedures and guest shutoff pages out; facts in, secrets and identity documents out. | 1, 11, 12 |
| 16 | `maintenance-calendar.md` | A shared calendar is the schedule; HA alerts with acknowledge, defer, done; seasonal windows gated on rain and soil temperature. | 4, 15 |
| 17 | `updates.md` | Review, then update: a four-day wait, a written verdict, a rollback of record, a next-day checkout; the host too; a staging pre-check with an update-only allow-list. | 6, 8, 9, 10, 12 |
| 18 | `dashboards.md` and `testing-and-simulation.md` again | After the first build: the kiosk and the clone are where the second month is spent. | - |

## How they connect

- **Three rules recur everywhere** and are stated once each: *nothing reaches a person except the owner without
  their OK* (1, 4), *one cause, one warning* (3, 4, 6), and *positive evidence* (3, 6, 8). When two files seem to
  disagree, the one that states the rule wins.
- **The live export is the truth** (11) is what makes the checks in 2, 6 and 7 possible: every "how to check"
  that greps something greps the export, not a hand-kept mirror.
- **Routine updates** (17) are the one version change that is not design-only once the cadence runs: the weekly
  verdict is the design, the owner may delegate the go (17, rule 10), and firmware stays out of it.
- **Design-only areas** (12, rule 9) are the subjects of 5: alarm, locks, codes, consent, firmware and version
  changes get a design with a build plan, never an unattended implementation.
- **The support agent** (14) is the last thing to build. It assumes 4 (the router), 6 (the counts it reads), 13
  (the budget it respects) and 5 (the never list it enforces).

## What the interview generates from these

Phase 1 (`interview/phase-1-house-profile-interview.md`) turns the principles into the house's own files: a naming scheme
(2), notification classes and per-person levels (4), the voice exposure policy (5), a health-check plan (6), a
dashboard vocabulary (7), the freeze and backup tiers that fit the hardware (9, 10), the manual and wiki
skeletons (11), a backlog with points (12) and the budget buffer (13). `templates/` holds the starting files.
