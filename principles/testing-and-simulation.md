# Testing and simulation

*Status: written (O1, 2026-10-11); rule 14 added (KIT-RPLAY, 2026-10-31). Distilled from a real install; the failure
modes are written generically.*

Dry runs, simulators, scenario suites, persona simulations.

## The rule

1. [core] **Nothing audible, nothing sent, no real alarm event unless the owner is present.** Every build-and-test
   session is scoped "no push notifications, no changes to the alarm, no audible tests", and its write-up says so
   or says what was sent.
2. [core] **Dry runs exist for every actuating script** (notify, announce, actuate, inbound-message replies) and must not
   spend real rate limits or write journal lines that read like real actions. Prefix them.
3. [core] **Simulate states, not devices.** Fire a finding or a health check from a simulated state and confirm it stays
   quiet on the live house at the same time.
4. [core] **Replay history as the fixture** before tuning any threshold: count how many times the proposed rule would
   have fired over N days and name each false alarm.
5. [core] **Glass tests** for anything a flag cannot prove. An audio stop proves the stream stopped, not that the dialog
   is gone; a lock-screen flag says nothing about what is on screen; a voice test needs an ear.
6. [core] **A test harness slower than production can hide the bug**, and one passing test proves nothing for an
   intermittent fault. Vary one input and count both outcomes.
7. [core] **A page designed to be empty cannot be tested by looking at it.** Assert rows against the verdict in code.
8. [default, topic 9] **A staging clone** is restored from a real backup into an isolated network: start-at-boot off, every USB line
   deleted BEFORE first boot, auto-arm off before anything runs, and an isolation probe against the real house that
   must fail at once (the restored clone holds every notify and SMS credential). Re-apply isolation after every
   restore. If the clone is ever given a narrow internet path to install candidate updates, `updates.md` rule 13
   applies: the probe must then prove that only the allow-listed hosts answer.
9. [default, topic 9] **Scenario suites with baselines.** Record each scenario twice on the clone, demand zero differences between
   captures, then compare the new system against that. A skipped scenario is counted; a "fixed" row must move the
   skip count.
10. [core] **Drills and rehearsals are timed and written up**: the restore drill (download, restore, entity counts, boot
    errors that are isolation-only), the major-migration rehearsal (each step's must-print line, house-down window,
    rollback time), with a stop rule: if a step cannot finish, stop and re-plan; never skip ahead.
11. [default, topic 9] **Persona simulations of the household.** Every persona agent can only read; one fact-checker has read-only
    house tools and nothing else; a facilitator keeps a minute-by-minute house log derived mechanically from the
    design; where an account and the log disagree, the log is what the house did and the gap is the finding.
    Personas invent no capability and no failure the house could not produce; a gap in the brief is a finding.
12. [core] **Re-sync ground truth against live immediately before a run**, not after each decision.
13. [core] **Freeze before you leave**: a named snapshot, versions recorded, and every live change afterwards gets a drift
    row (`change-control.md`).
14. [core] **Replay real traffic through a changed router before it is applied.** Before a change to the notification
    router (or any script that decides who hears what) goes live, rebuild every message it sent over the last
    weeks from its own log, plus the history of every setting it reads (each phone's level, the guest slots,
    the sending switches, who was home, the alarm's state), and run each one through the old router and the new
    one side by side, each at that message's own time. Report every difference before the apply: who gets it,
    whether it was merged or held, and the words. An audience difference that no written ruling explains is a
    finding against the router, not against the replay. First check the check: the old-router model must
    reproduce the log's own recipients, and every message where it does not is explained one by one. Write down
    what the replay cannot see (messages never sent, flags the log does not keep, senders that bypass the router,
    speech), and re-run it after each later change to the router. Outline: `templates/docs/router-replay-outline.md`.

## Why

The house is a family's production system. A test that arms it, texts four phones or speaks at 3 a.m. is an
incident, and the life-safety path cannot be exercised at all because running it sounds every speaker (and,
where the house chose it, unlocks doors). Replay is the cheapest honest fixture, and for a router it is the only test that uses the real
mix of messages and settings: a unit test checks the cases someone thought of; a month of real pushes holds the
ones nobody did. Personas find friction that no config audit sees, but only if
they cannot touch the house and cannot invent it.

## How this goes wrong

- **A simulation that can act.** Persona agents given the house's normal tools are not a simulation; they are
  unattended agents acting on a sleeping family. Give them read-only tools so the rule is structural, not a line in
  a prompt. Rules 1, 11.
- **A safety build that cannot be run.** Smoke and CO handling sounds every speaker (and unlocks doors where the
  house chose that, `safety-and-security.md` rule 16), so it cannot be tested for real. Ship it saying exactly what was not run, then read every path back; a read-back finds defects
  a test would have. Rule 1.
- **A dry run with real side effects.** The dry run still spends a real rate limit, or its log lines look like
  real actions. Symptom: a quota gone, or a journal nobody can trust. Rule 2.
- **Testing a check against a healthy house.** A check that is quiet on a healthy house proves nothing about
  whether it can fire. Simulate the failing state, see it fire, then see it quiet on live. Rule 3.
- **Tuning by intuition.** A threshold picked because it sounds right fires several times a week on normal
  behavior. Replay recorded history and count the would-be alarms first. Rule 4.
- **Flags that lie.** The log says a popup closed, but the screen did not repaint under the screensaver; device
  flags say a panel woke when it did not, or the reverse. A muted panel that is still reachable fails silently.
  Look at the glass, and send time-critical speech to two channels. Rule 5.
- **A harness kinder than production.** Two separate test calls leave a gap that one production call does not, so
  every test passes and production fails; each new theory survives exactly one confirming test. Rule 6.
- **A clone that is not isolated.** A restored copy boots and immediately tries to push, reach the radios or claim
  devices on the house network; a restore meant to be partial runs as full. The first-boot isolation probe must fail
  to connect, or the drill stops. Rule 8.
- **Scenarios that do not count.** Skipped scenarios are reported as passes, or one scenario's state bleeds into
  the next. Demand zero differences between two recordings before trusting a baseline. Rule 9.
- **An upgrade that only a rehearsal catches.** A new version disables some scripts at startup over a changed
  option shape; after the upgrade the house would send nothing. Found on the clone, not the house. Rule 10.
- **A router change judged by its unit tests.** Every test passes, and on the first evening a guest gets the
  nightly-job failures, or a parent stops getting the door alerts, because no test held that mix of levels and
  slots. Replay the real month through both routers first. Rule 14.
- **A replay that trusts the log.** The push log was written before the sending switch was checked, so for
  every hour sending was off it lists people who got nothing; a replay that took the log as the truth would
  call the correct router wrong, or hide a real gap. Make the old-router model match the log, explain every
  message where it does not, and fix the log to record who was actually sent to. Rule 14.
- **Ground truth that reads as built.** A description of the house says a feature works that was only designed;
  simulated people, and then real ones, rely on it. Re-sync against live right before each run. Rules 11, 12.

## How to check it

- Every test write-up carries the line "nothing sent, nothing audible, alarm untouched", or says what was.
- Dry-run output is prefixed and the counters are unchanged after it.
- The clone's config shows no USB passthrough, an isolated bridge, start-at-boot off, and the probe fails.
- The baseline directory has two captures per scenario with zero differences; the skip count is a number.
- Each persona agent file lists read-only tools; only the verifier lists house read tools; the runner refuses to
  start without the owner's approval line.
- A drill record with timings exists for restore and for a major migration; the stopped runs are kept, not deleted.
- Every router change has a replay report from before its apply: messages replayed, differences by kind, each
  audience difference with the ruling that explains it, how many logged audiences the old-router model reproduced,
  and the list of what the replay could not see. A report with zero differences states its date range and count.

## Adapter notes

- **Pi / HA Green.** No VM snapshot or clone; staging is a second card or a container restored from a backup on
  an isolated VLAN, and the isolation probe matters more because there is no bridge to unplug. Rollback is minutes
  of reflashing, not a snapshot revert.
- **Mini PC / VM.** Snapshot from the command line, never a GUI snapshot that includes RAM (it pauses the house and
  trips the clock-jump heal).
- **Radios.** A restored clone must never see the sticks; delete passthrough before first boot. Zigbee needs a
  reload after any USB re-plug.
- **AI agent.** Persona and facilitator agents are plain Markdown briefs with a tool allowlist; any runtime that can
  restrict tools per helper agent works. The verifier needs read-only house tools that exist only on the box; a cloud
  session must say "unverified".
