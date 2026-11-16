"""Battery Optimizer, against a real Home Assistant.

Part 1 runs every test of the two blueprints it combines against it, unchanged: an instance converts by changing
only the blueprint path, so each test must pass with the same inputs. Two input defaults differ by design and are
set here: the keeper tests' faults stay silent (the optimizer's default action is empty; nothing to fire), and the
fault-watch tests get the old default event and a keeper whose window never acts (floor 0, ceiling 100), so the
test sees only the watch. Part 2 tests the two jobs together.
"""

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState

import test_battery_window_keeper as keeper_tests
import test_charger_fault_watch as watch_tests
from conftest import BATTERY, HEIGHTENED, IDLE, PLUG, POWER

BP = "battery_optimizer.yaml"
OLD_EVENT = [{"event": "charger_fault_watch", "event_data": {
    k: "{{ " + k + " }}" for k in ("status", "kind", "fault_id", "fault_ids", "message", "battery", "plug_entity")}}]
AS_WATCH = {"fault_action": OLD_EVENT, "normal_floor": 0, "normal_ceiling": 100}


def _port(test, defaults):
    async def ported(kit):
        setup = kit.setup

        async def optimizer(_blueprint, inputs, extra=None):
            await setup(BP, {**defaults, **inputs}, extra)

        kit.setup = optimizer
        if "real_trace" in test.__name__:
            # The replay sets the plug from the recorded trace, so the trace owns it: commands are recorded but
            # do not switch it (at 100 % the keeper, whose ceiling cannot be above 100, would switch it off).
            async def record_only(call):
                kit.calls.append((call.service, call.data["entity_id"]))

            kit.hass.services.async_register("switch", "turn_on", record_only)
            kit.hass.services.async_register("switch", "turn_off", record_only)
        await test(kit)

    ported.__name__ = test.__name__
    return ported


@pytest.mark.parametrize("test", [getattr(keeper_tests, n) for n in dir(keeper_tests) if n.startswith("test_")],
                         ids=lambda t: t.__name__)
async def test_as_keeper(kit, test):
    await _port(test, {})(kit)


@pytest.mark.parametrize("test", [getattr(watch_tests, n) for n in dir(watch_tests) if n.startswith("test_")],
                         ids=lambda t: t.__name__)
async def test_as_fault_watch(kit, test):
    await _port(test, AS_WATCH)(kit)


# ---- Part 2: both jobs in one automation ---------------------------------------------------------------


FULL = {"charger_plug": PLUG, "battery_sensor": BATTERY, "idle_sensor": IDLE, "power_sensor": POWER,
        "fault_action": OLD_EVENT}


async def start(kit, battery, plug, power=None, idle="on", inputs=None, full=True):
    kit.set(PLUG, plug, {"friendly_name": "Tablet charger"})
    kit.set(BATTERY, battery, {"device_class": "battery"})
    kit.set(IDLE, idle)
    kit.set(POWER, power if power is not None else plug)
    base = FULL if full else {"charger_plug": PLUG, "battery_sensor": BATTERY}
    await kit.setup(BP, {**base, **(inputs or {})})


async def level(kit, value):
    kit.set(BATTERY, value, {"device_class": "battery"})
    await kit.settle()


async def test_full_cycle_with_a_working_charger_raises_nothing(kit):
    await start(kit, 79, "on")
    await level(kit, 80)
    assert kit.state(PLUG) == "off"
    kit.set(POWER, "off")  # the device sees the plug go off
    for value in range(79, 49, -1):  # drains through the window
        await kit.minutes(10)
        await level(kit, value)
    assert kit.state(PLUG) == "on"
    kit.set(POWER, "on")
    for value in range(51, 81):  # charges back
        await kit.minutes(5)
        await level(kit, value)
    assert kit.state(PLUG) == "off"
    assert kit.calls == [("turn_off", PLUG), ("turn_on", PLUG), ("turn_off", PLUG)]
    assert kit.events == []


async def test_keeper_turns_off_at_the_ceiling_and_a_stuck_relay_is_reported_not_fought(kit):
    await start(kit, 79, "on")
    await level(kit, 80)
    assert kit.calls == [("turn_off", PLUG)]
    await kit.minutes(5)  # the device still reports power: the relay did not open
    [fault] = kit.faults("power_without_plug")
    assert "stuck on" in fault["message"]
    await kit.minutes(60)  # four re-checks
    assert kit.calls == [("turn_off", PLUG)]  # neither job switches it back on
    kit.set(POWER, "off")
    await kit.minutes(5)
    assert len(kit.faults("power_without_plug", "clear")) == 1


async def test_keeper_turns_on_at_the_floor_and_a_dead_charger_is_caught(kit):
    await start(kit, 51, "off")
    await level(kit, 50)
    assert kit.state(PLUG) == "on"
    kit.set(POWER, "on")
    for value in (49, 48):  # falling on the charger, the screen idle
        await kit.minutes(30)
        await level(kit, value)
    [fault] = kit.faults("not_charging")
    assert "fell from 50% to 48%" in fault["message"]
    assert kit.state(PLUG) == "on"
    assert kit.calls == [("turn_on", PLUG)]


async def test_plug_back_from_unavailable_one_change_serves_both_jobs(kit):
    """The same state change ends a fault, wakes the keeper, and starts a watch: one command, one clear."""
    await start(kit, 60, "on")
    kit.set(PLUG, "unavailable")
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable")) == 1
    await level(kit, 45)  # drained below the floor while the plug was gone
    assert kit.calls == []  # an unreachable plug is not commanded
    kit.set(PLUG, "off", {"friendly_name": "Tablet charger"})
    kit.set(POWER, "off")
    await kit.settle()
    assert kit.state(PLUG) == "on"
    assert kit.calls == [("turn_on", PLUG)]
    kit.set(POWER, "on")
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable", "clear")) == 1
    assert kit.faults("no_power") == [] and kit.faults("power_without_plug") == []


async def test_low_battery_fault_and_the_floor_agree(kit):
    """A floor under the low level (an odd but valid setup): the fault turns the plug on and the keeper, inside
    its window, leaves it on."""
    await start(kit, 45, "off", inputs={"normal_floor": 20, "normal_ceiling": 80, "low_level": 40,
                                        "low_minutes": 15})
    await level(kit, 39)
    await kit.minutes(15)
    assert len(kit.faults("low_battery")) == 1
    assert kit.state(PLUG) == "on"
    await kit.minutes(60)
    assert kit.calls == [("turn_on", PLUG)]


async def test_silent_by_default_but_still_safe(kit):
    await start(kit, 45, "off", full=False, inputs={"low_level": 40, "low_minutes": 15, "normal_floor": 20})
    await level(kit, 39)
    await kit.minutes(15)
    assert kit.events == []  # no action given: nothing is sent
    assert kit.state(PLUG) == "on"  # but the fault still turned the plug on


async def test_one_switch_turns_both_jobs_off_and_on(kit):
    await start(kit, 70, "on")
    await kit.hass.services.async_call("automation", "turn_off", {"entity_id": "automation.under_test"},
                                       blocking=True)
    await level(kit, 85)
    kit.set(POWER, "off")
    await kit.minutes(30)
    assert kit.state(PLUG) == "on" and kit.calls == [] and kit.events == []
    await kit.hass.services.async_call("automation", "turn_on", {"entity_id": "automation.under_test"},
                                       blocking=True)
    await kit.minutes(15)  # the re-check repairs the window
    assert kit.state(PLUG) == "off"


async def test_reload_resets_once_rechecks_the_window_and_watches_again(kit):
    await start(kit, 70, "on")
    await kit.hass.services.async_call("automation", "turn_off", {"entity_id": "automation.under_test",
                                                                  "stop_actions": False}, blocking=True)
    await level(kit, 85)  # changed while the automation was off
    await kit.minutes(1)  # the clock is frozen between ticks; a real restart is never at the plug's last change
    await kit.hass.services.async_call("automation", "turn_on", {"entity_id": "automation.under_test"},
                                       blocking=True)
    await watch_tests.reload(kit)
    [reset] = [e for e in kit.events if e["status"] == "reset"]
    assert len(reset["fault_ids"]) == 5
    assert kit.state(PLUG) == "off"  # the keeper ran with the restart, not 15 minutes later
    kit.set(POWER, "on")  # stuck relay: the new watch is live
    await kit.minutes(5)
    assert len(kit.faults("power_without_plug")) == 1


async def test_heightened_switch_while_a_fault_is_open(kit):
    await start(kit, 85, "off", power="off", inputs={"heightened_switch": HEIGHTENED})
    kit.set(HEIGHTENED, "off")
    kit.set(POWER, "on")  # stuck relay while off
    await kit.minutes(5)
    assert len(kit.faults("power_without_plug")) == 1
    kit.set(HEIGHTENED, "on")
    await kit.settle()
    assert kit.state(PLUG) == "off"  # 85 is inside the Heightened window: keep
    await level(kit, 70)
    assert kit.state(PLUG) == "on"  # the Heightened floor
    await kit.minutes(5)
    [clear] = kit.faults("power_without_plug", "clear")  # plug on and power on: consistent again
    assert "relay is tested at the next turn-off" in " ".join(clear["message"].split())


async def test_a_burst_of_reports_ends_on_the_latest_answer(kit):
    await start(kit, 79, "on")
    for value in (80, 79, 81, 50, 82):
        kit.set(BATTERY, value, {"device_class": "battery"})
    await kit.settle()
    assert kit.state(PLUG) == "off"
    await kit.minutes(15)
    assert kit.state(PLUG) == "off"


# ---- Part 3: restarts (review BOf 2026-10-17: M1-M3, L2, L3) ---------------------------------------------


async def ha_start(kit, battery, plug, power=None, inputs=None):
    """A Home Assistant start: the automation is set up while Home Assistant is not running, and its triggers
    attach at `started`, so the `homeassistant` start trigger fires (a reload never fires it)."""
    kit.set(PLUG, plug, {"friendly_name": "Tablet charger"})
    kit.set(BATTERY, battery, {"device_class": "battery"})
    kit.set(IDLE, "on")
    kit.set(POWER, power if power is not None else plug)
    kit.hass.set_state(CoreState.not_running)
    await kit.setup(BP, {**FULL, **(inputs or {})})
    await kit.minutes(1)  # the clock is frozen between ticks; a real start is never at the plug's last change
    assert kit.events == [] and kit.calls == []  # nothing runs before `started`
    kit.hass.set_state(CoreState.running)
    kit.hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await kit.settle()


async def fall_on_a_dead_charger(kit, start_level):
    kit.set(POWER, "on")  # the cable is in; the charger behind it is dead
    for value in (start_level - 1, start_level - 2):
        await kit.minutes(35)
        await level(kit, value)
    await kit.minutes(10)


@pytest.mark.parametrize("restart", ["start", "reload"])
async def test_a_restart_where_the_keeper_switches_the_plug_watches_the_phase_once(kit, restart):
    """M1: the keeper's turn-on at the restart starts a `watch` run; the restart run must not watch the same
    phase too, or a dead charger is reported twice."""
    if restart == "start":
        await ha_start(kit, 48, "off", power="off")
    else:
        await start(kit, 48, "off", power="off")
        await kit.hass.services.async_call("automation", "turn_off", {"entity_id": "automation.under_test"},
                                           blocking=True)
        await kit.minutes(1)  # off, so the re-check cannot switch the plug before the reload does
        await kit.hass.services.async_call("automation", "turn_on", {"entity_id": "automation.under_test"},
                                           blocking=True)  # turning on runs nothing (README: "One switch")
        await watch_tests.reload(kit)
    assert kit.calls == [("turn_on", PLUG)]  # the restart's keeper: below the floor
    assert len([e for e in kit.events if e["status"] == "reset"]) == 1
    await fall_on_a_dead_charger(kit, 48)
    assert len(kit.faults("not_charging")) == 1
    assert kit.faults("no_power") == [] and kit.faults("power_without_plug") == []


async def test_a_start_raises_a_fault_that_still_holds_once(kit):
    """M3: the start path (the `homeassistant` trigger, which skips the run count) sends one reset, runs the
    keeper (inside the window: no command), and raises a fault that held through the restart once."""
    await ha_start(kit, 60, "on", power="off")  # plug on, no power reaching the device
    [reset] = [e for e in kit.events if e["status"] == "reset"]
    assert len(reset["fault_ids"]) == 5
    await kit.minutes(5)
    assert len(kit.faults("no_power")) == 1
    await kit.minutes(30)
    assert len(kit.faults("no_power")) == 1 and kit.calls == []
    kit.set(POWER, "on")
    await kit.minutes(5)
    [clear] = kit.faults("no_power", "clear")
    assert "sees power again" in clear["message"]


async def test_the_keeper_ends_a_phase_while_a_fault_is_open_without_ping_pong(kit):
    """M3: a not_charging fault open at 88 % in the Heightened window when the switch drops to Normal: the keeper
    turns the plug off, the fault clears as the phase ending, and nothing turns it back on."""
    kit.set(HEIGHTENED, "on")
    await start(kit, 88, "off", power="off", inputs={"heightened_switch": HEIGHTENED})
    kit.set(PLUG, "on", {"friendly_name": "Tablet charger"})  # turned on by hand: inside the window, kept
    await kit.settle()
    await fall_on_a_dead_charger(kit, 88)
    assert len(kit.faults("not_charging")) == 1 and kit.calls == []
    kit.set(HEIGHTENED, "off")  # Normal: 86 is above its ceiling
    await kit.settle()
    assert kit.calls == [("turn_off", PLUG)]
    kit.set(POWER, "off")
    await kit.minutes(5)
    [clear] = kit.faults("not_charging", "clear")
    assert "charging phase ended" in clear["message"]
    await kit.minutes(60)
    assert kit.calls == [("turn_off", PLUG)] and kit.state(PLUG) == "off"
    assert len(kit.faults("not_charging")) == 1


async def test_an_unchanged_reload_with_no_live_run_sends_a_reset(kit):
    """M2, pinned: with a plugged-in sensor and the plug off no run is alive, and a reload that did not change
    the automation cannot be told from one that did: one reset (the action should treat it silently)."""
    await start(kit, 70, "off", power="off")
    await kit.minutes(1)
    await watch_tests.reload(kit, changed=False)
    [reset] = kit.events
    assert reset["status"] == "reset" and reset["kind"] == "all"
    assert kit.calls == []
    await kit.minutes(30)
    assert len(kit.events) == 1


async def test_a_plug_that_goes_unknown_is_a_plug_fault(kit):
    """L2: an MQTT plug that loses its retained state goes `unknown`, not `unavailable`. Unlike an unavailable
    plug it may still hear a command, so the keeper still sends one."""
    await start(kit, 60, "on")
    kit.set(PLUG, "unknown")
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable")) == 1
    assert kit.calls == []  # inside the window: nothing to command
    await level(kit, 45)
    assert kit.calls == [("turn_on", PLUG)] and kit.state(PLUG) == "on"
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable", "clear")) == 1
