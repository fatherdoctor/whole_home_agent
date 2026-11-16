"""Battery window keeper, against a real Home Assistant."""

from conftest import BATTERY, HEIGHTENED, PLUG

BP = "battery_window_keeper.yaml"
BASE = {"charger_plug": PLUG, "battery_sensor": BATTERY}


async def start(kit, battery, plug, inputs=None, heightened=None):
    kit.set(PLUG, plug, {"friendly_name": "Tablet charger"})
    kit.set(BATTERY, battery, {"device_class": "battery", "unit_of_measurement": "%"})
    if heightened is not None:
        kit.set(HEIGHTENED, heightened)
    await kit.setup(BP, {**BASE, **(inputs or {})})


async def test_ceiling_turns_the_plug_off_and_floor_turns_it_on(kit):
    await start(kit, 79, "on")
    kit.set(BATTERY, 80)
    await kit.settle()
    assert kit.state(PLUG) == "off"
    for level in (70, 60, 51):  # inside the window: nothing changes
        kit.set(BATTERY, level)
        await kit.settle()
        assert kit.state(PLUG) == "off"
    kit.set(BATTERY, 50)
    await kit.settle()
    assert kit.state(PLUG) == "on"
    kit.set(BATTERY, 65)  # rising through the window: stays on
    await kit.settle()
    assert kit.state(PLUG) == "on"


async def test_heightened_switch_moves_the_window(kit):
    await start(kit, 80, "on", {"heightened_switch": HEIGHTENED}, heightened="on")
    kit.set(BATTERY, 85)
    await kit.settle()
    assert kit.state(PLUG) == "on"  # Heightened ceiling is 95
    kit.set(BATTERY, 95)
    await kit.settle()
    assert kit.state(PLUG) == "off"
    kit.set(BATTERY, 70)
    await kit.settle()
    assert kit.state(PLUG) == "on"  # Heightened floor is 70


async def test_switching_back_to_normal_acts_at_once(kit):
    await start(kit, 90, "on", {"heightened_switch": HEIGHTENED}, heightened="on")
    assert kit.state(PLUG) == "on"
    kit.set(HEIGHTENED, "off")
    await kit.settle()
    assert kit.state(PLUG) == "off"  # 90 is above the Normal ceiling


async def test_no_switch_means_normal_always(kit):
    await start(kit, 85, "on")
    await kit.minutes(15)
    assert kit.state(PLUG) == "off"


async def test_custom_ranges(kit):
    await start(kit, 60, "off", {"normal_floor": 40, "normal_ceiling": 60})
    kit.set(BATTERY, 61)
    await kit.settle()
    assert kit.state(PLUG) == "off"
    kit.set(BATTERY, 40)
    await kit.settle()
    assert kit.state(PLUG) == "on"
    kit.set(BATTERY, 60)
    await kit.settle()
    assert kit.state(PLUG) == "off"


async def test_invalid_range_holds_the_plug_on(kit):
    await start(kit, 75, "off", {"normal_floor": 80, "normal_ceiling": 60})
    kit.set(BATTERY, 76)
    await kit.settle()
    assert kit.state(PLUG) == "on"
    kit.set(BATTERY, 95)
    await kit.settle()
    assert kit.state(PLUG) == "on"  # never switched off while the range is invalid


async def test_invalid_heightened_range_holds_on_only_while_heightened(kit):
    await start(kit, 85, "on", {"heightened_switch": HEIGHTENED, "heightened_floor": 90,
                                "heightened_ceiling": 90}, heightened="on")
    await kit.minutes(15)
    assert kit.state(PLUG) == "on"
    kit.set(HEIGHTENED, "off")
    await kit.settle()
    assert kit.state(PLUG) == "off"


async def test_unreachable_battery_waits_out_the_grace_period(kit):
    await start(kit, 65, "off")
    kit.set(BATTERY, "unavailable")
    await kit.minutes(4)
    assert kit.state(PLUG) == "off"  # a blip passes silently
    kit.set(BATTERY, 64)
    await kit.minutes(10)
    assert kit.state(PLUG) == "off"
    kit.set(BATTERY, "unavailable")
    await kit.minutes(5)
    assert kit.state(PLUG) == "on"  # held on, the safe side
    kit.set(BATTERY, 70)
    await kit.minutes(15)
    assert kit.state(PLUG) == "on"  # back inside the window: no change


async def test_unavailable_heightened_switch_means_normal(kit):
    await start(kit, 85, "on", {"heightened_switch": HEIGHTENED}, heightened="on")
    assert kit.state(PLUG) == "on"
    kit.set(HEIGHTENED, "unavailable")
    await kit.settle()
    assert kit.state(PLUG) == "off"  # 85 is above the Normal ceiling


async def test_a_silent_battery_is_held_on_once_set(kit):
    """A kiosk app that stops reporting leaves its last level standing; the real battery drains."""
    await start(kit, 62, "off", {"stale_minutes": 120})
    await kit.minutes(119)
    assert kit.state(PLUG) == "off"
    await kit.minutes(1)  # two hours without a report, caught by the tick
    assert kit.state(PLUG) == "on"
    kit.set(BATTERY, 63)  # it reports again, inside the window: no change
    await kit.minutes(15)
    assert kit.state(PLUG) == "on"


async def test_a_silent_battery_is_ignored_by_default(kit):
    await start(kit, 62, "off")
    await kit.minutes(240)
    assert kit.state(PLUG) == "off"


async def test_tick_repairs_a_missed_change(kit):
    await start(kit, 85, "off")
    kit.set(PLUG, "on", {"friendly_name": "Tablet charger"})  # someone switches it by hand
    await kit.settle()
    assert kit.state(PLUG) == "on"
    await kit.minutes(15)
    assert kit.state(PLUG) == "off"


async def test_plug_back_from_unavailable_is_reconciled(kit):
    await start(kit, 45, "unavailable")
    kit.set(BATTERY, 44)
    await kit.settle()
    assert kit.state(PLUG) == "unavailable"  # nothing to switch; the fault watch reports this
    kit.set(PLUG, "off", {"friendly_name": "Tablet charger"})
    await kit.settle()
    assert kit.state(PLUG) == "on"


async def test_light_domain_plug(kit):
    kit.hass.services.async_register(
        "light", "turn_off", lambda call: kit.set("light.tablet_charger", "off"))
    kit.set("light.tablet_charger", "on")
    kit.set(BATTERY, 79, {"device_class": "battery"})
    await kit.setup(BP, {"charger_plug": "light.tablet_charger", "battery_sensor": BATTERY})
    kit.set(BATTERY, 81)
    await kit.settle()
    assert kit.state("light.tablet_charger") == "off"
