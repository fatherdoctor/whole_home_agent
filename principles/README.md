# Principles

*Status: written (O1, 2026-10-11). Every file: the rule, why, how it goes wrong, how to check it, adapter notes. Start with `00-index.md`, which gives the reading order and how the files connect.*

- `00-index.md` - The principles, in reading order, and how they connect.
- `naming.md` - Entity, device, area, helper and automation naming; ids that survive renames.
- `automations.md` - One cause one warning; positive evidence; idempotence; modes; traces; no logic hidden in dashboards.
- `notifications-and-tiers.md` - Routers, tiers (house/maintainer/alarm/life-safety), tags and replacement, consent, never send to verify.
- `health-checks.md` - A health count per subsystem, faults vs notices, what makes a good check, watching the watchers.
- `safety-and-security.md` - Alarm, locks, codes, guests; what should not run without a person.
- `change-control.md` - Freezes, version pins, staging clones, rehearsals, drift logs, rollback of record.
- `updates.md` - Review, then update: the weekly cadence, host updates, a staging pre-check, what a freeze changes.
- `backups-and-recovery.md` - Tiers T0-T4, off-box copies, restore drills, a recovery chapter in the manual.
- `documentation.md` - CHANGELOG, gotchas, a user manual for the household, a maintainer wiki for the builder.
- `backlog-and-planning.md` - A backlog with rulings, planning-poker points, decisions written as questions.
- `board-and-lanes.md` - The board as the only source of unattended work: rows, statuses, the life cycle from idea to checkout, reviews as rows, the owner's cards, sprints, epics, the PLAN line.
- `budget-and-pacing.md` - Reading AI usage, a pace line with a buffer, idle-time work.
- `tier-2-support-agent.md` - An always-on watcher with fenced actions, race rails, ask-before-act, and its own health.
- `house-records-and-equipment.md` - Photos and documents in, an inventory, archived manuals, procedures and guest shutoff pages out; secrets and identity documents out.
- `maintenance-calendar.md` - A shared calendar is the schedule; HA alerts with acknowledge, defer, done; seasonal windows gated on rain and soil temperature.
- `dashboards.md` - Design rules, a reference tab, kiosk panels, testing on the glass.
- `testing-and-simulation.md` - Dry runs, simulators, scenario suites, persona simulations.
- `working-with-the-agent.md` - Approvals, reporting faithfully, verifying before claiming, timestamps, memory.
