"""Charger fault watch, against a real Home Assistant, including a replay of ten days of a real wall tablet."""

from datetime import timedelta

import yaml
from homeassistant.util import dt as dt_util

from conftest import BATTERY, IDLE, PLUG, POWER, load_trace

BP = "charger_fault_watch.yaml"
FULL = {"charger_plug": PLUG, "battery_sensor": BATTERY, "idle_sensor": IDLE, "power_sensor": POWER}


async def start(kit, battery=50, plug="off", idle="on", power=None, inputs=None):
    kit.set(PLUG, plug, {"friendly_name": "Tablet charger"})
    kit.set(BATTERY, battery, {"device_class": "battery"})
    kit.set(IDLE, idle)
    kit.set(POWER, power if power is not None else plug)
    await kit.setup(BP, {**FULL, **(inputs or {})})


async def reload(kit, changed=True):
    """automation.reload. Home Assistant replaces (and so stops the runs of) only an automation whose
    configuration changed; `changed` edits the alias first to get that case."""
    if changed:
        path = kit.hass.config.path("configuration.yaml")
        with open(path) as f:
            conf = yaml.safe_load(f)
        conf["automation"][0]["alias"] += " (edited)"
        with open(path, "w") as f:
            yaml.safe_dump(conf, f)
    await kit.hass.services.async_call("automation", "reload", blocking=True)
    await kit.settle()


async def plug_on(kit):
    kit.set(PLUG, "on", {"friendly_name": "Tablet charger"})
    kit.set(POWER, "on")
    await kit.settle()


async def drain(kit, start, minutes_per_percent, total_minutes):
    """A dead charger: the battery falls at the idle drain rate while the plug stays on."""
    level, elapsed = start, 0
    while elapsed < total_minutes:
        await kit.minutes(minutes_per_percent)
        elapsed += minutes_per_percent
        level -= 1
        kit.set(BATTERY, level, {"device_class": "battery"})
        await kit.settle()
    return level


# ---- not_charging ---------------------------------------------------------------------------------------


async def test_dead_charger_with_the_screen_idle_is_caught_after_the_settle_time(kit):
    await start(kit, battery=50)
    await plug_on(kit)
    start_time = dt_util.utcnow()
    await drain(kit, 50, 22, 44)  # 48 % at 44 min: fallen 2, but not yet charging 60 min
    assert kit.faults() == []
    await kit.minutes(16)
    [fault] = kit.faults("not_charging")
    assert fault["fault_id"] == "switch_tablet_charger_not_charging"
    assert fault["at"] - start_time == timedelta(minutes=60)
    assert "fell from 50% to 48%" in fault["message"]
    # repaired: the battery rises, and the clear follows 5 minutes later, under the same fault_id
    kit.set(BATTERY, 49, {"device_class": "battery"})
    await kit.minutes(4)
    assert kit.faults(status="clear") == []
    await kit.minutes(1)
    [clear] = kit.faults("not_charging", "clear")
    assert clear["fault_id"] == fault["fault_id"]


async def test_watch_rebaselines_after_a_clear_and_can_fault_again(kit):
    await start(kit, battery=60)
    await plug_on(kit)
    await drain(kit, 60, 30, 60)  # 58 at 60 min -> fault
    assert len(kit.faults("not_charging")) == 1
    kit.set(BATTERY, 59, {"device_class": "battery"})
    await kit.minutes(5)
    assert len(kit.faults("not_charging", "clear")) == 1
    await drain(kit, 59, 30, 30)  # 58: only 1 below the new baseline
    assert len(kit.faults("not_charging")) == 1
    await drain(kit, 58, 30, 30)  # 57: 2 below
    assert len(kit.faults("not_charging")) == 2


async def test_falling_while_the_screen_is_in_use_is_not_a_fault(kit):
    await start(kit, battery=50, idle="off", inputs={"low_level": 20})
    await plug_on(kit)
    await drain(kit, 50, 15, 90)  # 44 % after 90 min awake: expected on a slow charger
    assert kit.faults() == []
    kit.set(IDLE, "on")
    await kit.minutes(120)
    assert kit.faults() == []  # flat while idle, 6 below the start: the fall happened in use (a real 10-10 case)
    await drain(kit, 44, 20, 40)  # now it falls 2 while idle
    assert len(kit.faults("not_charging")) == 1


async def test_flat_battery_is_not_a_fault(kit):
    await start(kit, battery=55)
    await plug_on(kit)
    await kit.minutes(240)
    assert kit.faults() == []


async def test_without_an_idle_sensor_any_fall_counts(kit):
    kit.set(PLUG, "off")
    kit.set(BATTERY, 50, {"device_class": "battery"})
    await kit.setup(BP, {"charger_plug": PLUG, "battery_sensor": BATTERY})
    kit.set(PLUG, "on")
    await kit.settle()
    await drain(kit, 50, 30, 60)
    assert len(kit.faults("not_charging")) == 1
    assert "idle" not in kit.faults()[0]["message"]


async def test_plug_off_ends_the_watch_quietly(kit):
    await start(kit, battery=70)
    await plug_on(kit)
    await drain(kit, 70, 20, 40)
    kit.set(PLUG, "off")
    kit.set(POWER, "off")
    await kit.minutes(120)
    assert kit.events == []


async def test_reload_rebaselines_from_the_current_level(kit):
    await start(kit, battery=50, plug="on", power="on")  # already charging at load: the watch starts from 50
    await drain(kit, 50, 30, 30)  # 49 at 30 min
    await reload(kit)  # the old run is gone; the new watch starts from 49
    await drain(kit, 49, 30, 30)  # 48 at 60 min: 2 below the first start, 1 below the new one
    await kit.minutes(29)
    assert kit.faults() == []
    await drain(kit, 48, 1, 1)  # 47 at 90 min
    assert len(kit.faults("not_charging")) == 1


# ---- the other faults -----------------------------------------------------------------------------------


async def test_plug_unavailable_after_the_grace_period_then_clears(kit):
    await start(kit, battery=60, plug="on")
    kit.set(PLUG, "unavailable")
    await kit.minutes(4)
    kit.set(PLUG, "on", {"friendly_name": "Tablet charger"})
    await kit.minutes(10)
    assert kit.events == []  # a blip passes silently
    kit.set(PLUG, "unavailable")
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable")) == 1
    kit.set(PLUG, "on")
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable", "clear")) == 1


async def test_no_power_turns_nothing_off_and_clears(kit):
    await start(kit, battery=60, plug="on", power="on")
    kit.set(POWER, "off")
    await kit.minutes(5)
    [fault] = kit.faults("no_power")
    assert "reports no power" in fault["message"]
    kit.set(POWER, "on")
    await kit.minutes(5)
    assert len(kit.faults("no_power", "clear")) == 1


async def test_stuck_relay_is_reported_and_the_plug_left_alone(kit):
    await start(kit, battery=85, plug="off", power="off")
    kit.set(POWER, "on")
    await kit.minutes(5)
    assert len(kit.faults("power_without_plug")) == 1
    assert kit.calls == []  # switching the plug on cannot fix a relay stuck on
    await kit.minutes(30)
    assert kit.faults(status="clear") == []
    kit.set(POWER, "off")  # relay repaired
    await kit.minutes(5)
    assert len(kit.faults("power_without_plug", "clear")) == 1


async def test_turn_on_at_fault_can_be_disabled(kit):
    await start(kit, battery=40, plug="off", inputs={"turn_on_at_fault": False, "low_minutes": 15})
    kit.set(BATTERY, 30, {"device_class": "battery"})
    await kit.minutes(15)
    assert len(kit.faults("low_battery")) == 1
    assert kit.calls == []


async def test_low_battery(kit):
    await start(kit, battery=55, plug="off", inputs={"low_level": 40, "low_minutes": 60})
    kit.set(BATTERY, 39, {"device_class": "battery"})
    await kit.minutes(59)
    assert kit.faults() == []
    await kit.minutes(1)
    assert len(kit.faults("low_battery")) == 1
    assert kit.state(PLUG) == "on"
    kit.set(BATTERY, 40, {"device_class": "battery"})
    await kit.minutes(5)
    assert len(kit.faults("low_battery", "clear")) == 1


async def test_no_power_faults_without_a_power_sensor(kit):
    kit.set(PLUG, "on")
    kit.set(BATTERY, 60, {"device_class": "battery"})
    await kit.setup(BP, {"charger_plug": PLUG, "battery_sensor": BATTERY})
    kit.set(POWER, "off")
    await kit.minutes(30)
    assert kit.events == []


async def test_custom_action_receives_the_variables(kit):
    await start(kit, battery=60, plug="on", power="on", inputs={"fault_action": [
        {"event": "my_notify", "event_data": {"tag": "{{ fault_id }}", "text": "{{ status }}: {{ message }}"}}]})
    seen = []
    kit.hass.bus.async_listen("my_notify", lambda e: seen.append(dict(e.data)))
    kit.set(POWER, "off")
    await kit.minutes(5)
    assert seen and seen[0]["tag"] == "switch_tablet_charger_no_power"
    assert seen[0]["text"].startswith("fault: Tablet charger is on")
    assert kit.events == []  # the default event is replaced, not added to


# ---- no idle and no plugged-in sensor: a screenless battery board ---------------------------------------


async def bare(kit, battery, plug, inputs=None):
    """Only the plug and the battery, as on a board that reports nothing but its battery."""
    kit.set(PLUG, plug, {"friendly_name": "Tablet charger"})
    kit.set(BATTERY, battery, {"device_class": "battery"})
    await kit.setup(BP, {"charger_plug": PLUG, "battery_sensor": BATTERY, **(inputs or {})})


async def switch_plug(kit, state):
    kit.set(PLUG, state, {"friendly_name": "Tablet charger"})
    await kit.settle()


async def test_bare_board_dead_charger_is_caught_by_the_steady_fall(kit):
    await bare(kit, 60, "off")
    await switch_plug(kit, "on")
    await drain(kit, 60, 30, 60)  # 58 at 60 min
    [fault] = kit.faults("not_charging")
    assert "fell from 60% to 58%." in " ".join(fault["message"].split())
    assert kit.faults("no_power") == []  # "Expect a rise within" is off by default


async def test_expect_a_rise_flags_a_flat_battery(kit):
    await bare(kit, 60, "off", {"rise_minutes": 15})
    await switch_plug(kit, "on")
    await kit.minutes(14)
    assert kit.faults() == []
    await kit.minutes(1)
    [fault] = kit.faults("no_power")
    assert fault["fault_id"] == "switch_tablet_charger_no_power"
    assert "has not risen" in fault["message"]
    kit.set(BATTERY, 61, {"device_class": "battery"})  # power restored
    await kit.minutes(5)
    assert len(kit.faults("no_power", "clear")) == 1


async def test_expect_a_rise_is_satisfied_once_per_phase(kit):
    await bare(kit, 60, "off", {"rise_minutes": 15})
    await switch_plug(kit, "on")
    await kit.minutes(10)
    kit.set(BATTERY, 61, {"device_class": "battery"})
    await kit.minutes(180)  # flat for three hours after one rise: the charger works
    assert kit.faults() == []
    await switch_plug(kit, "off")
    await switch_plug(kit, "on")  # a new phase is checked again
    await kit.minutes(15)
    assert len(kit.faults("no_power")) == 1


async def test_expect_a_rise_waits_while_the_device_is_busy(kit):
    kit.set(IDLE, "off")
    await bare(kit, 60, "off", {"rise_minutes": 15, "idle_sensor": IDLE})
    await switch_plug(kit, "on")
    await kit.minutes(60)
    assert kit.faults() == []
    kit.set(IDLE, "on")
    await kit.minutes(15)
    assert len(kit.faults("no_power")) == 1


async def test_expect_a_rise_is_skipped_with_a_plugged_in_sensor(kit):
    await start(kit, battery=60, plug="off", inputs={"rise_minutes": 15})
    await plug_on(kit)
    await kit.minutes(60)
    assert kit.faults() == []


async def test_bare_board_stuck_relay_is_found_from_the_battery_rising(kit):
    await bare(kit, 79, "on")
    kit.set(BATTERY, 80, {"device_class": "battery"})
    await switch_plug(kit, "off")  # the window keeper's ceiling; the relay sticks
    kit.set(BATTERY, 81, {"device_class": "battery"})
    await kit.minutes(30)
    assert kit.faults() == []  # one point of rounding is not a rise
    kit.set(BATTERY, 82, {"device_class": "battery"})
    await kit.settle()
    [fault] = kit.faults("power_without_plug")
    assert "rose from 80% to 82%" in fault["message"]
    assert kit.calls == [] and kit.state(PLUG) == "off"
    kit.set(BATTERY, 81, {"device_class": "battery"})  # draining again: power is cut
    await kit.minutes(5)
    assert len(kit.faults("power_without_plug", "clear")) == 1


async def test_bare_board_normal_cycle_raises_nothing(kit):
    await bare(kit, 51, "off", {"rise_minutes": 15})
    kit.set(BATTERY, 50, {"device_class": "battery"})
    await switch_plug(kit, "on")
    level = 50
    while level < 80:  # a charger that clearly outpaces the drain: +1 % every 4 min
        await kit.minutes(4)
        level += 1
        kit.set(BATTERY, level, {"device_class": "battery"})
    await switch_plug(kit, "off")
    while level > 50:
        await kit.minutes(20)
        level -= 1
        kit.set(BATTERY, level, {"device_class": "battery"})
    await kit.minutes(5)
    assert kit.events == []


async def test_two_inferred_faults_in_one_phase_keep_their_own_kind(kit):
    """not_charging and the inferred no_power open at once in the same plug phase; each fault and each clear
    carries its own kind and fault_id (since HA 2025.4 a variable set in one parallel branch is seen by all)."""
    await bare(kit, 60, "off", {"rise_minutes": 15})
    await switch_plug(kit, "on")
    await kit.minutes(15)  # flat 15 min: no_power, raised at 60
    await drain(kit, 60, 30, 60)  # 58 at 75 min, on 75 min: not_charging, while no_power is still open
    assert [(e["status"], e["kind"], e["fault_id"]) for e in kit.events] == [
        ("fault", "no_power", "switch_tablet_charger_no_power"),
        ("fault", "not_charging", "switch_tablet_charger_not_charging"),
    ]
    assert "has not risen" in kit.events[0]["message"] and "fell from 60% to 58%" in kit.events[1]["message"]
    kit.set(BATTERY, 59, {"device_class": "battery"})  # above 58: not_charging clears; still under 60
    await kit.minutes(5)
    kit.set(BATTERY, 61, {"device_class": "battery"})  # above 60: no_power clears
    await kit.minutes(5)
    assert [(e["status"], e["kind"], e["fault_id"]) for e in kit.events[2:]] == [
        ("clear", "not_charging", "switch_tablet_charger_not_charging"),
        ("clear", "no_power", "switch_tablet_charger_no_power"),
    ]


async def test_a_relapse_inside_the_five_minutes_restarts_the_clear(kit):
    await start(kit, battery=60, plug="on", power="on")
    kit.set(POWER, "off")
    await kit.minutes(5)
    assert len(kit.faults("no_power")) == 1
    kit.set(POWER, "on")
    await kit.minutes(3)
    kit.set(POWER, "off")  # relapse
    await kit.minutes(1)
    kit.set(POWER, "on")
    await kit.minutes(4)
    assert kit.faults(status="clear") == []  # 4 quiet minutes since the relapse
    await kit.minutes(1)
    assert len(kit.faults("no_power", "clear")) == 1


async def test_unreachable_plug_is_not_commanded(kit):
    await start(kit, battery=60, plug="off")
    kit.set(PLUG, "unavailable")
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable")) == 1
    assert kit.calls == []


async def test_restart_withdraws_leftovers_and_raises_a_fault_that_still_holds(kit):
    await start(kit, battery=60, plug="on")
    kit.set(PLUG, "unavailable")
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable")) == 1
    await reload(kit)
    [reset] = [e for e in kit.events if e["status"] == "reset"]
    assert reset["kind"] == "all" and reset["fault_id"] == "switch_tablet_charger"
    assert "switch_tablet_charger_plug_unavailable" in reset["fault_ids"] and len(reset["fault_ids"]) == 5
    await kit.minutes(4)
    assert len(kit.faults("plug_unavailable")) == 1
    await kit.minutes(1)  # still unreachable a grace period after the reload: raised again, once
    assert len(kit.faults("plug_unavailable")) == 2
    await kit.minutes(30)
    assert len(kit.faults("plug_unavailable")) == 2
    kit.set(PLUG, "on", {"friendly_name": "Tablet charger"})
    await kit.minutes(5)
    assert len(kit.faults("plug_unavailable", "clear")) == 1


async def test_restart_raises_a_low_battery_that_still_holds_only_once(kit):
    await start(kit, battery=55, plug="on", inputs={"low_level": 40, "low_minutes": 30})
    kit.set(BATTERY, 39, {"device_class": "battery"})
    await kit.minutes(10)
    await reload(kit)
    await kit.minutes(29)
    assert kit.faults() == []
    await kit.minutes(1)  # held low for "Low for at least" after the reload
    assert len(kit.faults("low_battery")) == 1
    await kit.minutes(60)
    assert len(kit.faults("low_battery")) == 1


async def test_restart_raises_no_power_that_still_holds(kit):
    await start(kit, battery=60, plug="on", power="on")
    kit.set(POWER, "off")
    await kit.minutes(5)
    assert len(kit.faults("no_power")) == 1
    await reload(kit)
    await kit.minutes(5)
    assert len(kit.faults("no_power")) == 2
    await kit.minutes(30)
    assert len(kit.faults("no_power")) == 2
    kit.set(POWER, "on")
    await kit.minutes(5)
    assert len(kit.faults("no_power", "clear")) == 1


async def test_reload_that_changed_nothing_keeps_the_runs_and_adds_none(kit):
    await start(kit, battery=60)
    await plug_on(kit)  # the watch takes 60 as its base
    kit.set(POWER, "off")
    await kit.minutes(5)  # no_power, its run open
    await drain(kit, 60, 25, 25)  # 59 at 30 min
    await reload(kit, changed=False)
    await drain(kit, 59, 30, 30)  # 58 at 60 min on: the surviving watch faults, once
    assert [(e["status"], e["kind"]) for e in kit.events] == [("fault", "no_power"), ("fault", "not_charging")]
    kit.set(POWER, "on")
    await kit.minutes(5)
    assert [(e["status"], e["kind"]) for e in kit.events[2:]] == [("clear", "no_power")]


async def test_restart_with_nothing_wrong_sends_only_the_reset(kit):
    await start(kit, battery=60, plug="on", power="on")
    await reload(kit)
    await kit.minutes(30)
    assert [e["status"] for e in kit.events] == ["reset"]


# ---- the real trace -------------------------------------------------------------------------------------


def old_rule_episodes(trace):
    """The rule being replaced: charging an hour and the battery no higher than an hour ago."""
    level = {s.time: s.battery for s in trace}
    episodes, on_since, active = [], None, False
    for s in trace:
        if not s.power:
            on_since, active = None, False
            continue
        on_since = on_since or s.time
        before = level.get(s.time - timedelta(hours=1))
        hit = before is not None and s.time - on_since >= timedelta(hours=1) and s.battery <= before < 100
        if hit and not active:
            episodes.append(s.time)
        active = hit
    return episodes


async def replay(kit, trace, tamper=None, inputs=None):
    first = trace[0]
    kit.freezer.move_to(first.time)
    await start(kit, battery=first.battery, plug="on" if first.power else "off",
                idle="on" if first.idle else "off", inputs=inputs)
    for s in trace[1:]:
        gap = int((s.time - first.time).total_seconds() // 60)
        await kit.minutes(gap)
        kit.freezer.move_to(s.time)
        s = tamper(s) if tamper else s
        plug = "on" if s.power else "off"
        if kit.state(PLUG) != plug:
            kit.set(PLUG, plug, {"friendly_name": "Tablet charger"})
        kit.set(POWER, plug)
        kit.set(IDLE, "on" if s.idle else "off")
        kit.set(BATTERY, s.battery, {"device_class": "battery"})
        await kit.settle()
        first = s


async def test_real_trace_old_rule_fires_but_the_blueprint_does_not(kit):
    trace = load_trace("wall-tablet-sample.csv")
    assert trace[-1].time - trace[0].time > timedelta(days=9)
    assert len(old_rule_episodes(trace)) >= 8  # the false "not rising" pushes being replaced
    await replay(kit, trace)
    assert kit.faults() == [], kit.faults()


async def test_real_trace_without_a_plugged_in_sensor_raises_nothing(kit):
    """The same ten days with only the plug, the battery and the idle sensor: the battery never rises after
    the plug turns off, so the inferred stuck-relay check stays quiet."""
    await replay(kit, load_trace("wall-tablet-sample.csv"), inputs={"power_sensor": ""})
    assert kit.faults() == [], kit.faults()


async def test_real_trace_with_a_dead_charger_is_caught_within_75_minutes(kit):
    """The same days, but from the first charging phase on the seventh day the charger delivers nothing: the battery drains
    at the trace's own discharge rate while the plug and power still read on."""
    trace = load_trace("wall-tablet-sample.csv")
    day = [s for s in trace if s.time.date().isoformat() == "2027-01-11"]
    begin = next(s.time for s in day if s.power)
    window = [s for s in trace if begin - timedelta(hours=2) <= s.time <= begin + timedelta(hours=4)]
    start_level = next(s.battery for s in window if s.time == begin)

    def dead(s):
        if s.time < begin:
            return s
        drained = start_level - int((s.time - begin).total_seconds() / 3600 * 2.7)
        return type(s)(s.time, drained, True, s.idle)

    await replay(kit, window, tamper=dead)
    [fault] = kit.faults("not_charging")
    assert fault["at"] - begin <= timedelta(minutes=75), fault["at"] - begin
    assert kit.faults("low_battery") == kit.faults("no_power") == []
