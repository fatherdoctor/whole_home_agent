# Automations

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

One cause one warning; positive evidence; idempotence; modes; traces; no logic hidden in dashboards.

## The rule

1. [core] **Templates are a last resort.** Prefer native triggers, trigger ids, `state` / `numeric_state` / `sun` / `time`
   conditions and `choose` branches, even when verbose. A template that only picks a branch is always replaceable
   by native conditions. If a template is genuinely unavoidable, say why BEFORE presenting the YAML. Message text
   interpolation and plain value copies do not count; control flow does.
2. [core] **Pick `mode` deliberately.** `single` drops an overlapping trigger with only a warning in the log; `queued`
   serializes; `restart` cancels the run in flight. Anything with a `delay` or `wait` and more than one plausible
   trigger defaults to `queued`, unless canceling is the point (a "last transition wins" wake, a recovery that
   should cancel a pending alert).
3. [core] **One cause, one warning.** One push carries one cause. When two automations can report the same event, one of
   them owns it and the other stands down. Housekeeping actions never push. A roll-up sensor never pushes.
4. [core] **Positive evidence only.** An HTTP 200 means accepted, not done. Read the entity back after acting on it. Test
   the path that should succeed, not only the path that should be refused. On an intermittent fault one passing
   test proves nothing: vary one input and count both outcomes. A status flag is not visibility; a screenshot is
   evidence about the page, not the glass.
5. [core] **Idempotent, and never self-disabling.** Re-running a no-op is free; a silent permanent disable is not. An
   automation never turns its own enable switch off. Anything that disables other automations needs an on-start and
   periodic reconcile. A tool that rebuilds a page must be stable over three consecutive runs.
6. [core] **Read the trace before theorizing.** A condition against a nonexistent entity evaluates false and the
   automation simply never runs, with a clean trace. A stale `last_triggered` is the tell for a run eaten by a
   restart.
7. [core] **Guard event-entity triggers against restore artifacts.** `not_from: [unavailable]` on every plain state
   trigger on an `event.*` entity (not `unknown`: that discards a real first press). `from: 'on'` on state triggers
   that must not fire after a restart.
8. [core] **Restarts and reloads are not free.** They reset `last_changed` on nearly every entity, kill runs parked in a
   `delay`, and a time trigger that already fired does not fire again. Stamp durations you depend on into an
   `input_datetime`.
9. [core] **No numbers buried in templates.** Thresholds are helpers without `initial:`, shown on a page. When a
   measurement's unit changes, every threshold in the old unit is wrong, including the ones in comments.
10. [core] **No logic hidden in dashboards.** The dashboard shows state and offers controls; helpers are the interface;
    automations hold the logic.
11. [core] **Nothing reaches a person except the owner without their permission for that send; never send to verify.**
    (The full rule is in `notifications-and-tiers.md`.)
12. [core] **Decide kickability.** A branch gated only on `trigger.id` cannot be re-run by hand (safe for anything that
    pages); a state-gated branch can be re-kicked (good for retrying an API call). Prove it once with
    `automation.trigger` and the logbook.
13. [default, topic 10] **Packages or includes: choose at the start and keep one twin.** Adding `packages:` later needs a restart and
    a drift register between the live file and its repository copy. A fresh install should start with packages
    (one file per subsystem) and the repository as the only hand-edited copy.
14. [core] **Never name a script field or a variable after a template built-in** (`log`, `now`, `states`, `float`,
    `int`, `max`): a caller that leaves the field out gets the function itself, which renders as text and reads as
    true, so `{{ log | default(true) }}` never sees its default; the test that works is `{{ log is not boolean or
    log }}`. For every optional field of a shared script, test the call that omits it, not only the one that sets it.

## Why

Home Assistant fails quietly. A bad template, the wrong mode, a missing entity, a restored event state, a
self-disabled schedule: none of these logs an error a person sees. The rules force the evidence to come from the
house's behavior, not from the YAML looking right.

## How this goes wrong

- **A template where a native option exists.** A template is added to tell tap types apart when a native attribute
  condition would do. The exception that stands: `mode: restart` with waits in flight genuinely needs the trigger's
  captured values. Rule 1.
- **`single` dropping the run that mattered.** A toggle flips off seconds after it flipped on; the second run is
  dropped with a log warning, and the house stays in the first state. Rule 2.
- **Two pushes for one event.** Two automations react to the same arrival and push in the same second; after a
  radio restart, replayed events push blank messages. Rule 3.
- **A 200 that proves nothing.** A string of digits coerced to a number at a `variables:` boundary makes the
  CORRECT code fail, while every test only checked that wrong codes fail. A service call on an entity that does not
  exist returns success. Rule 4.
- **Self-disabling and fighting.** A one-shot that turns a schedule off disables it for good the first time a
  branch misfires; two automations managing the same label undo each other. A restart in the middle of a long wait
  means the transition after it never happens. Rule 5.
- **Theory before trace.** A rule changes the arm mode, and the arrival disarm, which only handles the old mode,
  never fires again; the trace and `last_triggered` show it in a minute. Rule 6.
- **An event replayed on reload.** Reloading an integration restores an event entity's last state as if it were
  new, and an old triple-tap turns a child's light on at night. Guard with `not_from: [unavailable]`; adding
  `unknown` to that guard also drops a real first press. Rule 7.
- **"Quiet for N minutes" after a restart.** A restart or reload resets `last_changed` on nearly every entity, so
  every quiet-house timer starts over; frequent reloads mean the house is never quiet long enough. Rule 8.
- **A number on the wrong scale.** A threshold stays in old units after the sensor changes what it counts, so it
  can never fire. A helper with `initial:` resets its value on every restart. Rule 9.
- **Logic in a card.** A timer written in a card's template refreshes only when the card re-renders, so a popup
  closes early or never. Rule 10.
- **Sending to test.** See `notifications-and-tiers.md` rules 5 and 6. Rule 11.
- **The field named after a function.** A shared notification script had an optional `log` field; every caller that
  left it out passed the template function of that name, so the record of every push was silently lost for a day
  while the pushes themselves went out. Rule 14.

## How to check it

- The config check must be fully successful. "Successful config (partial)" is a failure.
- Automation count before and after every reload, with "0 unavailable".
- grep `condition: template` and `value_template` in automations; every hit is on a written, justified list.
- grep every automation for `mode:`; grep every `event.` state trigger for `not_from`.
- grep helpers for `initial:`; expect none.
- After a restart taken while someone may be in transit: read the presence automations' `last_triggered` and the
  house-mode helper.
- Review questions: "What is the trace for the last run?" "What re-fires this after a restart?" "Which other
  automation already pushes for this cause?" "Did we test the path that should succeed?" "Can this turn itself
  off?"

## Adapter notes

### Reusing a script for voice and automations

A script names the actions; an automation supplies a trigger and optional conditions.
An Alexa routine can supply a different trigger for that same script.
Calling the script directly does not check the conditions of an automation that also calls it.
Put a required check inside the script when every caller must obey it.
Test each caller separately, including the real voice phrase or scheduled trigger.
Stopping a script does not reverse actions that already completed; define explicit off actions when needed.
The [first automation lesson](../00-start-here/your-first-automation.md) teaches the pieces.
The [voice walkthrough](../install/voice-assistants.md#4-a-safe-scene-script-with-an-alexa-phrase) connects a safe scene script to Alexa through Home Assistant Cloud.

### Device-specific notes

- **Z-Wave scene paddles.** Taps need a plain state trigger (a repeated value does not change the attribute);
  hold and release need attribute triggers; gate release with `from: KeyHeldDown`; `mode: queued`. Models differ:
  one sends a single hold and no release on a quick tap, another a clean double-tap event. Do not build debounce
  for a storm that is not there. Battery nodes read `asleep`, which is normal; `dead` is the fault. A lock can
  acknowledge and not execute; wait for the state you asked for.
- **Hub-bridged bulbs (Hue).** No start/stop dimming in core; "transition then freeze" does not work because the
  bridge reports the end state immediately. Zigbee and Z-Wave JS have raw level-change commands.
- **Wi-Fi lights.** Color and brightness in one call can drop whichever arrives second when a mode switch is
  needed; split and delay 500 ms.
- **Cloud thermostats.** Polled, minutes of lag; holds are indefinite and survive schedule transitions, which cuts
  both ways. Ignore their occupancy sensors as presence.
- **ESPHome.** A boolean attribute arrives as the string `on` / `off`, `None` as an empty string.
- **Android push.** `ttl: 0` and `priority: high` for anything time-critical; `notify.notify` with an entity
  target silently no-ops.
- **Matter / Thread, other voice assistants.** No incident recorded.
