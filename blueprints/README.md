# Charger Blueprints
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.10%2B-blue.svg)](https://www.home-assistant.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)

Three automation blueprints for a device that lives on a charger: a wall tablet, a kiosk, a dashboard phone, or a
screenless battery board (an ESP32 with a charger chip, say). Only a smart plug and a battery % sensor are required.
Leaving such a device at 100 % for months swells its battery; cycling it between two levels with a smart plug
keeps it healthy. Battery Optimizer does that and tells you when the charger stops working, in one automation;
the battery window keeper and the charger fault watch are the same two jobs as separate automations.

- [Charger Blueprints](#charger-blueprints)
  - [Introduction](#introduction)
    - [Features](#features)
  - [Installation](#installation)
  - [Updating](#updating)
  - [Uninstalling](#uninstalling)
  - [Usage](#usage)
    - [Battery window keeper](#battery-window-keeper)
    - [Charger fault watch](#charger-fault-watch)
      - [The faults](#the-faults)
      - [Without a plugged-in sensor](#without-a-plugged-in-sensor)
      - [The action](#the-action)
    - [Battery Optimizer](#battery-optimizer)
      - [Migrating from the two blueprints](#migrating-from-the-two-blueprints)
    - [Migrating from hand-written automations](#migrating-from-hand-written-automations)
  - [Versions](#versions)
  - [Making contributions](#making-contributions)
    - [Tests](#tests)
  - [License](#license)

## Introduction

> Status: battery window keeper v1.1.0, charger fault watch v1.2.0, written October 2026, revised after an adversarial
> review by a second model. Tested against a real Home Assistant (see "Tests");
> published 2026-10-15 as unlisted (secret) gists, linked under "Installation". Battery Optimizer v1.0.1 (both in one) written
> 2026-10-15, tested and reviewed (the findings enacted, the closure check passed): cleared for publication, not yet published. Nothing here is specific to one home.

| Blueprint | What it does | Notifies? |
|---|---|---|
| [`automation/battery_window_keeper.yaml`](automation/battery_window_keeper.yaml) | Switches the plug off at a ceiling and on at a floor; two ranges (Normal, Heightened) | No: it changes the plug and nothing else |
| [`automation/charger_fault_watch.yaml`](automation/charger_fault_watch.yaml) | Raises and clears faults (charger not delivering, low battery, plug unreachable, power and plug disagreeing) | Runs your action; the default fires an event |
| [`automation/battery_optimizer.yaml`](automation/battery_optimizer.yaml) | Both of the above in one automation per device, with one on/off | Only if you give it an action; empty = silent |
| [`automation/beta_update_notice.yaml`](automation/beta_update_notice.yaml) | For a beta tester: a phone notice when an update for an item you test is ready, saying if it is a pre-release; keeps the Pre-release switches on. See [beta-testing.md](beta-testing.md) | Yes: your phone's notify action |

Use the first two together (one instance of each per device), or Battery Optimizer alone (one instance per device). They share no helpers and need none. Never point two instances of
the same blueprint at one plug: the fault watch's runs talk to each other through an internal event keyed by the plug, so
two would cross-talk.

### Features

- Cycles a device's battery between a floor and a ceiling with a smart plug, so it is never held at 100 %.
- Two ranges, Normal and Heightened, switched by any on/off entity you choose; the blueprint does not need to know why.
- Safe side: the plug is held on (charging) when a range is invalid or the battery cannot be seen.
- Five faults (`not_charging`, `low_battery`, `plug_unavailable`, `no_power`, `power_without_plug`), each raised and cleared on its own.
- Needs only a plug and a battery % sensor; a plugged-in sensor and a device idle sensor make fault detection faster and more exact.
- Notifications are yours to route: the action receives ready-made variables and a stable tag per fault.
- Tested in a real Home Assistant, including a replay of ten days of a real wall tablet.

## Installation

Import these blueprints through Home Assistant or copy their files. Use one of these:

- **By URL**: Settings > Automations & scenes > Blueprints > Import blueprint, and paste one of these:
  - Battery window keeper v1.1.0: https://gist.github.com/fatherdoctor/f8fa16cf923a61101f5ec475668284a4
  - Charger fault watch v1.2.0: https://gist.github.com/fatherdoctor/6326544a320a9e6593fc05a271d1948c
- **By file only** for Battery Optimizer and Beta update notice (they have no import address yet), or for any of
  the four: copy the YAML into `<config>/blueprints/automation/<any folder>/` and reload automations (or restart).

Then "Create automation" from each blueprint and fill in the inputs. Needs Home Assistant 2024.10 or newer (the
`triggers:` syntax); tested on 2026.2. Battery Optimizer needs 2025.4 or newer.

## Updating

Re-import from the same link (or copy the new file over the old one). Re-importing overwrites the blueprint and
keeps your automations' inputs. Inputs are never renamed or removed, so an update does not break an automation;
see [Versions](#versions) for what changed and for any changed default.

## Uninstalling

Delete the automations created from the blueprint, then delete the blueprint (Settings > Automations & scenes >
Blueprints > the three-dot menu > Delete), or remove its file from `<config>/blueprints/automation/`. The blueprints
create no helpers and no entities, so nothing else is left behind. A notification still showing on a phone from a
fault that was open at that moment stays until it is cleared by hand.

## Usage

Each blueprint is configured through its inputs in the automation editor; the tables below list every input.

### Battery window keeper

Superseded by [Battery Optimizer](#battery-optimizer) once that is published; this one stays published and
maintained for the automations that use it.

| Input | Default | Notes |
|---|---|---|
| Charger plug | - | A `switch` or `light` entity (some plugs show up as lights). |
| Battery level | - | A `sensor` with device class battery. |
| Normal floor / ceiling | 50 / 80 % | The plug turns on at or below the floor, off at or above the ceiling. Between them nothing changes, so the battery cycles. |
| Use the Heightened range while this is on | empty | Optional. Any on/off entity. Empty or unavailable = Normal. |
| Heightened floor / ceiling | 70 / 95 % | Used while that entity is on. A ceiling of 100 turns the plug off only at a full 100 %, which some devices never report: in effect, charge continuously. |
| Grace period for an unreachable device | 5 min | The battery sensor must be unavailable this long before the plug is held on. |
| Treat a silent battery as unreachable after | 0 = off | Optional. A battery sensor that has not reported anything (not merely not changed) for this long is treated as unreachable, so the plug is held on. Catches a kiosk app that stopped reporting and left its last level standing. 120 min suits a tablet whose app reports every few minutes; leave it off for a device that reports rarely, or the plug is held on and the battery charged to full. |
| Re-check | every 15 min | Repairs a missed change (a plug switched by hand, an event lost in a restart). |

**Why a Heightened range, and why the blueprint does not know why.** Some days you want more charge in hand: the
home is empty and nobody will notice a dead panel for a day, a guest is using the panel, the alarm is armed and the
panel is its keypad. Each home has its own reasons, so the blueprint takes one on/off entity and leaves the reasons
to you. If there is more than one reason, make a template binary sensor that is on when any of them holds:

```yaml
# configuration.yaml (or a package) - adjust the conditions to your home
template:
  - binary_sensor:
      - name: Keep more charge in hand
        state: >
          {{ is_state('alarm_control_panel.home_alarm', 'armed_away')
             or is_state('input_boolean.house_guests', 'on') }}
```

**Safe side.** The plug is held ON (charging) when a range is invalid (each floor must be below its ceiling; no
ceiling above 100) or when the battery sensor has been unreachable past the grace period. A device that cannot be
seen is better charging than dying.

### Charger fault watch

Superseded by [Battery Optimizer](#battery-optimizer) once that is published; this one stays published and
maintained for the automations that use it.

| Input | Default | Notes |
|---|---|---|
| Charger plug, Battery level | - | As above. |
| Device idle | empty | Optional, **recommended when the device's use varies** (a screen): on while it is in its low-drain state (screen off or on its screensaver, a board asleep). Leave empty for a steady drain. |
| External power detected | empty | Optional: on while the device reports it is plugged in. Catches `no_power` and `power_without_plug` within the grace period. Without it, see "Without a plugged-in sensor" below. |
| Charging at least | 60 min | The not-charging check starts only after the plug has been on this long. |
| Device idle at least | 45 min | With a device idle sensor. |
| Fallen by at least | 2 % | Below the level when the device went idle (or charging started, if later; without an idle sensor, when charging started). Keep it at 2 or more (sensors report whole percents). |
| Expect a rise within | 0 = off | Without a plugged-in sensor only: `no_power` if the plug has been on this long (and the device idle this long, with an idle sensor) and the battery has not risen at all. For a charger that clearly outpaces the drain; 15 min suits many small battery boards. |
| Risen while unplugged by at least | 2 % | Without a plugged-in sensor only: `power_without_plug` when the battery rises this far above its level when the plug turned off. |
| Low battery level / Low for at least | 35 % / 60 min | `low_battery`: a backstop well under the charging floor (a busy screen can hold a working slow charger a few points under the floor for hours; the real trace below dipped to 45 %). |
| Grace period for device problems | 5 min | For `plug_unavailable`, `no_power`, `power_without_plug`. |
| Turn the plug on when a fault starts | on | Charging is the safe state. Not for `power_without_plug`: a plug command cannot fix a relay stuck on. |
| Action | fire `charger_fault_watch` | Runs at every fault and every clear. |

#### The faults

| `kind` | Raised when | Cleared when (held 5 min) |
|---|---|---|
| `not_charging` | Plug on for the settle time, device idle for the idle time (if a sensor is given), and the battery has **fallen** by the set amount since the device went idle (since charging started, without an idle sensor) | The battery rises above the level at the fault, or the plug turns off |
| `low_battery` | Battery below the low level for the set time | Back at or above the low level |
| `plug_unavailable` | Plug unavailable for the grace period | Plug available |
| `no_power` | Plug on but the device reports no power, for the grace period (dead cable, dead relay). Without a plugged-in sensor, and only if "Expect a rise within" is set: the battery has not risen in that time | They agree again (inferred: the battery rises above the level at the fault) |
| `power_without_plug` | Plug off but the device still powered, for the grace period (relay stuck on). Without a plugged-in sensor: the battery has risen by the set amount since the plug turned off | They agree again (inferred: the battery falls below the level at the fault, or the plug turns on) |

**Why "fallen while idle", not "not rising".** A small charger on a tablet that is in use can lose ground: in the
real install these blueprints came from, the charger added about 3.7 %/h with the screensaver up, and the screen
being awake cost about 7 %/h. A rule of "charging an hour and the battery has not risen" fired twelve times in ten
days on a charger that never failed; flat hours happen at every level, and every hour more than half awake is flat
or falling. A working charger, though, practically never lets the battery *fall* while the screen is idle. A dead
one does, at the idle drain rate, so it is caught within about an hour of the screen going idle.

The fall is measured from the level when the screen last went idle, not from the start of charging. Measured from
the start, a phase that began with two busy hours (down three points) and then sat flat and idle still looks like a
dead charger; the real trace has exactly that afternoon, and the first draft of this rule flagged it. A pulled cable or a
dead relay is caught faster by `no_power`, if the device reports power.

**Why not a Trend helper.** The level when charging started is held by the run that watches that charging phase,
so the blueprint needs no helper. (A Trend binary sensor was considered: it only recalculates when the battery
changes, so after a fall while the screen is in use followed by a flat idle stretch it still reports a falling
trend, which is exactly the false alarm this rule exists to avoid.) The cost: a Home Assistant restart, or a reload
that changed the automation, restarts the watch from the current level, so a fault in progress is found one settle
period later, never falsely. The runs waiting for a clear are gone too, so the action runs once with `status`
`reset` (see "The action"); a plug, power or low-battery fault that still holds is raised again after its grace
period. A reload that did not change the automation leaves its runs alone, and the blueprint does nothing then.

#### Without a plugged-in sensor

Some devices report only a battery level: a board that measures its cell's voltage and has no screen, for example.
Both blueprints work with just the plug and the battery. What changes in the fault watch:

| Fault | With a plugged-in sensor | With only the battery |
|---|---|---|
| Relay stuck on (`power_without_plug`) | Within the grace period | When the battery rises 2 % above its level at switch-off. A battery cannot charge itself; on the ten-day trace below it never rose even 1 % after switch-off. |
| Dead cable or relay (`no_power`) | Within the grace period | From "Expect a rise within", if set; otherwise later, as `not_charging` once the battery has fallen 2 % (an hour or more on a low-drain board), and finally `low_battery`. |

A board with a steady drain needs no idle sensor: every fall counts, from the start of charging.

**A board that reports voltage, not percent.** Both blueprints take a battery % sensor. Convert on the device (in
ESPHome, a `calibrate_linear` or `calibrate_polynomial` filter from your cell's voltage curve) or with a template
sensor with device class battery. Two cautions: a cell reads higher while charging, so the window keeper stops a
little early, which is the gentle side; and a board that sleeps between reports must keep its sensor available
while it sleeps, or the unreachable grace period will hold the plug on at every sleep (check how your firmware
reports a sleeping device before relying on it).

#### The action

Variables available to your action:

| Variable | Example |
|---|---|
| `status` | `fault`, `clear`, or `reset` (after a restart, and at a reload that finds no run alive: withdraw every tag in `fault_ids`; may come with nothing to withdraw) |
| `kind` | `not_charging`, `low_battery`, `plug_unavailable`, `no_power`, `power_without_plug`; `all` for a reset |
| `fault_id` | `switch_tablet_charger_not_charging`: stable per plug and kind; use it as the notification tag so the clear replaces the fault |
| `fault_ids` | All five tags this plug can use, for a reset |
| `message` | A ready-made sentence, e.g. "Tablet charger: charging for 64 min but the battery fell from 50% to 48% with the device idle. The charger is not delivering." |
| `battery` | The battery sensor's state when the action runs, as a string (`"48"`, or `"unavailable"`) |
| `plug_entity` | The plug's entity id |

A `reset` is a tag withdrawal, not news: send it on silently. It comes after every restart, and also at any
`automation.reload` (each save of any automation in the UI reloads them all) that finds no run of this automation
alive, for example with a plugged-in sensor and the plug off, when nothing is being watched. An unchanged reload
with no runs looks the same as a changed one, so the blueprint cannot tell whether anything is left to withdraw.

A push to a phone through the Companion app, replacing the fault with its clear, and withdrawing leftovers after a
restart without showing anything:

```yaml
- if: "{{ status == 'reset' }}"
  then:
    - repeat:
        for_each: "{{ fault_ids }}"
        sequence:
          - action: notify.mobile_app_your_phone
            data:
              message: clear_notification
              data:
                tag: "{{ repeat.item }}"
  else:
    - action: notify.mobile_app_your_phone
      data:
        title: "{{ 'Charger fault' if status == 'fault' else 'Charger OK' }}"
        message: "{{ message }}"
        data:
          tag: "{{ fault_id }}"
```

The fault watch also uses an event of its own, `charger_fault_watch_internal`, to hand a fault it inferred to a run
of its own; nothing else needs to listen to it.

If you route notifications through your own script (recommended: one place decides who hears what and when; see
`principles/` on notifications), call it here instead with a maintenance-level category.

### Battery Optimizer

One automation per device that does what the keeper and the fault watch do, with the same inputs under the same
names (the tables above apply unchanged), in five sections: **Device** (plug, battery, optional plugged-in and idle
sensors), **Ranges** (Normal, Heightened and its optional switch), **Timing** (the keeper's grace period,
silent-battery rule and re-check), **Faults** (always on; the fault watch's rules, including "Turn the plug on when a
fault starts") and **Notifications** (the action).

- **One switch.** The automation's own on/off turns both jobs off or on; there is no "cycling enabled" helper.
  Turning it off stops every run, so an open fault gets no clear; after turning it back on, the next re-check
  repairs the window and the next plug change starts a new watch. Turning it back on sends no `reset` either, so a
  notification raised before the switch-off stays until the next fault of its kind; run `automation.reload` (or
  restart) after turning it back on to withdraw the leftovers.
- **Notifications are optional.** The action defaults to empty: the plug is kept and faults still turn it on, but
  nothing is sent. The variables and the `reset` (after a restart, or a reload with no run alive) are the fault
  watch's.
- **How the jobs share one automation.** The keeper's runs are short (one decision, at most one plug command);
  each fault runs on its own as in the fault watch (its internal event is `battery_optimizer_internal`, so an
  optimizer and an old fault watch on the same plug during a migration do not cross-talk); a restart runs the
  keeper, then the reset and the watch. A keeper run decides again after its command and acts again if the answer
  changed meanwhile, so overlapping runs end on the latest state. Up to 30 runs at once.
- **A fault the restart re-checks is not raised twice.** After a restart a plug fault that still holds is raised
  again only if the plug has not changed since; if the keeper switched it at the restart, the plug's own trigger
  raises it instead. In the same way the restart watches the plug's phase for the inferred faults only if the
  keeper left the plug as it was; if the keeper switched it, the run that change started watches the new phase. (The separate fault watch can double such a fault when the separate keeper switches the
  plug within a grace period of a restart: a candidate for fault watch 1.2.1.)
- Needs Home Assistant 2025.4 or newer (the keeper's re-decision keeps a variable across repeat iterations).

#### Migrating from the two blueprints

1. Open the keeper's automation, switch to "Edit in YAML" and change `use_blueprint: path:` to the optimizer's
   path. Every input carries over.
2. Copy the fault watch's inputs that differ from their defaults into it (the idle and plugged-in sensors, any
   rule you changed, and your action).
3. **The one difference:** the fault watch's default action fired the event `charger_fault_watch`; the optimizer's
   default is silent. If something listens for that event and you never set an action, set the action to an Event
   action firing `charger_fault_watch` with the variables listed under "The action".
4. Delete (or turn off) the two old automations. Running all three on one plug is safe for a day (they agree on the
   plug and their internal events differ) but sends every fault twice.

### Migrating from hand-written automations

If you already cycle a charger with your own automations, the blueprints usually replace them and their helpers:
the phase start is the plug's own `last_changed`, the level at charge start lives in the watch, and each fault is
its own run, so "phase since", "level at charge start" and "active faults" helpers can go. Check before deleting a
helper that nothing else (a dashboard, a health check) reads it. Kiosk-app checks (is the app in front, is its
heartbeat fresh) are specific to the app and stay a plain automation.

## Versions

The version is the first line of each blueprint's description. Inputs are never renamed or removed; new inputs are
optional with a default that keeps the old behavior. A changed default (named in the table) affects automations
that left that input at its default. Re-importing overwrites the file and keeps your automations'
inputs.

| Version | Change |
|---|---|
| 1.0.0 | First release: both blueprints. |
| Fault watch 1.1.0 | "Screen idle" is now "Device idle" (same input). Without a plugged-in sensor: `power_without_plug` from the battery rising while the plug is off, and an optional "Expect a rise within" for `no_power`. A stuck relay no longer gets a plug turn-on. |
| Fault watch 1.2.0 | Each fault runs on its own, so two faults open at once keep their own `kind` and `fault_id` (before, on Home Assistant 2025.4 and later, a `not_charging` fault raised while an inferred `no_power` was open went out as `no_power`). The clear waits test the state, so a relapse is never missed. After a restart: `status` `reset` with `fault_ids`, and faults that still hold are raised again. An unreachable plug is no longer commanded on. Up to 25 runs at once (was 10). |
| Battery Optimizer 1.0.0 | First release: keeper 1.1.0 and fault watch 1.2.0 in one automation, same inputs; optional, silent-by-default action; restart runs the keeper; no double raise of a re-checked plug fault; up to 30 runs. Not published. |
| Battery Optimizer 1.0.1 | The review's findings (2026-10-17). A restart whose keeper switches the plug no longer watches the new phase twice (one `not_charging`, not two). A plug that goes `unknown` is a `plug_unavailable` fault, and its return wakes the keeper. A relay or cable fault the keeper's own switching ends now says so ("the plug is on again; the relay is tested at the next turn-off"). The `reset` at a reload with no run alive is documented, with the notifier handling it silently; the silent-battery rule is named in the description. No input changed. Not yet published (closure check first). |
| Keeper 1.1.0 | Optional "Treat a silent battery as unreachable after" (default off). Heightened ceiling default 95 % (was 100 %, which some devices never reach, so the plug never turned off). An unavailable Heightened switch means Normal (unchanged; now stated). |

## Making contributions

Report a problem with the blueprint version, the Home Assistant version, the inputs you set (without private
entity names if you prefer) and the automation's trace. Proposals are welcome as issues first. Before sending a
change, run the tests below; a change to a blueprint's behavior needs a test that fails without it.

### Tests

`tests/` runs the blueprints in a real Home Assistant
([pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)),
with a minute-by-minute clock:

```bash
python3.13 -m venv .venv && .venv/bin/pip install -r blueprints/tests/requirements.txt
.venv/bin/pytest blueprints/tests -q
```

`tests/traces/wall-tablet-sample.csv` is ten days of a real wall tablet at 15-minute samples (battery %,
external power, screen idle; the dates are shifted, the times of day kept), from a home where the old "not rising" rule raised twelve false faults. The replay
test asserts that the old rule still finds them on this data and that the fault watch raises none (no fault of any
kind, with the default inputs); a second test replays the same days with the charger killed at the start of a
charging phase and asserts it is caught within 75 minutes; a third replays them without the plugged-in sensor
(the inferred stuck-relay check must stay quiet). Each replay takes about three minutes.

`test_battery_optimizer.py` runs every keeper and fault-watch test again against Battery Optimizer, unchanged
(the fault-watch tests give it the old default event and a window of 0-100 %, and in the trace replays the trace
owns the plug), plus tests of the two jobs together: a full cycle raising nothing, a stuck relay after the keeper's
turn-off, a dead charger after its turn-on, one plug change serving both jobs, the one on/off, a reload re-checking
the window and watching again, a silent default, a burst of reports. Then restarts: a Home Assistant start (the
automation is set up while Home Assistant is not running, so the `homeassistant` start trigger fires) and a reload
where the keeper switches the plug and the charger is dead (one `not_charging`), a start with a fault still
holding (raised once), the keeper ending a phase while a fault is open (no ping-pong), an unchanged reload with
no run alive (one `reset`), and a plug that goes `unknown`.

The test clock is frozen and advanced one minute at a time; `conftest.py` settles the event loop without
`async_block_till_done`, because that call also waits for the fault watch's runs, which wait by design.

## License

MIT. See [`../LICENSE`](../LICENSE).
