"""Shared fixtures: a real Home Assistant instance (pytest-homeassistant-custom-component) with the kit's
blueprints copied into its config directory, plugs that change state when switched, and a minute clock."""

import asyncio
import csv
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

BLUEPRINTS = Path(__file__).resolve().parent.parent / "automation"
TRACES = Path(__file__).resolve().parent / "traces"

PLUG = "switch.tablet_charger"
BATTERY = "sensor.tablet_battery"
IDLE = "binary_sensor.tablet_screen_idle"
POWER = "binary_sensor.tablet_plugged_in"
HEIGHTENED = "input_boolean.keep_more_charge"


@dataclass
class Sample:
    time: datetime
    battery: int
    power: bool
    idle: bool


def load_trace(name: str) -> list[Sample]:
    with open(TRACES / name, newline="") as f:
        return [
            Sample(
                datetime.fromisoformat(r["time"]).replace(tzinfo=dt_util.UTC),
                int(r["battery"]),
                r["power"] == "1",
                r["idle"] == "1",
            )
            for r in csv.DictReader(f)
        ]


@pytest.fixture
async def kit(hass: HomeAssistant, tmp_path: Path, freezer):
    """HA with the blueprints installed under blueprints/automation/kit/ and a working plug."""
    freezer.move_to("2026-10-01 00:00:00+00:00")
    hass.config.config_dir = str(tmp_path)
    await hass.config.async_set_time_zone("UTC")
    dest = tmp_path / "blueprints" / "automation" / "kit"
    dest.mkdir(parents=True)
    for f in BLUEPRINTS.glob("*.yaml"):
        shutil.copy(f, dest / f.name)
    assert await async_setup_component(hass, "homeassistant", {})

    calls: list[tuple[str, str]] = []

    async def switch_service(call: ServiceCall) -> None:
        state = "on" if call.service == "turn_on" else "off"
        ids = call.data["entity_id"]
        for entity_id in [ids] if isinstance(ids, str) else ids:
            calls.append((call.service, entity_id))
            if hass.states.get(entity_id) and hass.states.get(entity_id).state == "unavailable":
                continue  # an unreachable plug does not switch
            hass.states.async_set(entity_id, state, {"friendly_name": "Tablet charger"})

    hass.services.async_register("switch", "turn_on", switch_service)
    hass.services.async_register("switch", "turn_off", switch_service)
    return Kit(hass, freezer, calls)


class Kit:
    def __init__(self, hass: HomeAssistant, freezer, calls) -> None:
        self.hass = hass
        self.freezer = freezer
        self.calls = calls
        self.events = []
        hass.bus.async_listen("charger_fault_watch", lambda e: self.events.append({**e.data, "at": dt_util.utcnow()}))

    async def setup(self, blueprint: str, inputs: dict, extra: list | None = None) -> None:
        autos = [{"id": "under_test", "alias": "under test",
                  "use_blueprint": {"path": f"kit/{blueprint}", "input": inputs}}] + (extra or [])
        # also on disk, so automation.reload (which reads configuration.yaml) finds the same automations
        with open(self.hass.config.path("configuration.yaml"), "w") as f:
            yaml.safe_dump({"automation": autos}, f)
        assert await async_setup_component(self.hass, "automation", {"automation": autos})
        await self.settle()

    def set(self, entity_id: str, state, attrs: dict | None = None) -> None:
        self.hass.states.async_set(entity_id, str(state), attrs or {})

    def state(self, entity_id: str) -> str:
        return self.hass.states.get(entity_id).state

    async def minutes(self, n: float) -> None:
        """Advance the clock one minute at a time, as HA's own time listeners see it."""
        await self.settle()  # a state set just before counts from now, not from the first tick
        for _ in range(int(n)):
            self.freezer.tick(timedelta(minutes=1))
            # one second of margin: a `for:` timer due exactly at this minute fires at it, not a minute late
            async_fire_time_changed(self.hass, dt_util.utcnow() + timedelta(seconds=1))
            await self.settle()

    async def settle(self) -> None:
        """Let everything that is ready run. Not async_block_till_done: that also waits for the fault watch's
        runs, which by design wait for hours."""
        last, stable = None, 0
        while stable < 3:
            for _ in range(20):  # callbacks queued with call_soon (event listeners) are not tasks
                await asyncio.sleep(0)
            pending = {t for t in (*self.hass._tasks, *self.hass._background_tasks) if not t.done()}
            # the loop's clock is frozen, so a real-time pause comes from the executor
            pause = asyncio.ensure_future(self.hass.loop.run_in_executor(None, time.sleep, 0.002))
            await asyncio.wait(pending | {pause}, return_when=asyncio.FIRST_COMPLETED)
            await pause
            stable = stable + 1 if pending == last else 0
            last = pending

    def faults(self, kind: str | None = None, status: str = "fault") -> list[dict]:
        return [e for e in self.events if e["status"] == status and (kind is None or e["kind"] == kind)]
