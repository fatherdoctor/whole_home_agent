"""Beta update notice, against a real Home Assistant: one notice per new version, the right kind of build, and the
pre-release switches turned on at start."""

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, ServiceCall

BP = "beta_update_notice.yaml"
UPDATE = "update.severe_weather"
OTHER = "update.codex_cli"
SWITCH = "switch.severe_weather_pre_release"
INPUTS = {"update_entities": [UPDATE, OTHER], "notify_action": "notify.mobile_app_test_phone",
          "pre_release_switches": [SWITCH]}


def update(kit, entity, state, installed, latest, url="https://example.invalid/releases/tag/x"):
    kit.set(entity, state, {"friendly_name": "Severe Weather" if entity == UPDATE else "Codex CLI",
                            "installed_version": installed, "latest_version": latest, "release_url": url,
                            "title": None})


async def start(kit, switch="off"):
    notices: list[dict] = []

    async def notify(call: ServiceCall) -> None:
        notices.append(dict(call.data))

    kit.hass.services.async_register("notify", "mobile_app_test_phone", notify)
    update(kit, UPDATE, "off", "v1.0.0", "v1.0.0")
    update(kit, OTHER, "off", "0.1.81", "0.1.81")
    kit.set(SWITCH, switch)
    await kit.setup(BP, INPUTS)
    return notices


async def test_a_pre_release_is_named_as_one_with_versions_and_link(kit):
    notices = await start(kit)
    update(kit, UPDATE, "on", "v1.0.0", "v1.1.0-beta.1", "https://example.invalid/releases/tag/v1.1.0-beta.1")
    await kit.settle()
    assert len(notices) == 1
    n = notices[0]
    assert n["title"] == "Update ready: Severe Weather"
    assert n["message"] == "v1.0.0 -> v1.1.0-beta.1, pre-release."
    assert n["data"]["url"] == "https://example.invalid/releases/tag/v1.1.0-beta.1"
    assert n["data"]["tag"] == f"beta-update-{UPDATE}"


async def test_a_stable_release_is_named_stable(kit):
    notices = await start(kit)
    update(kit, UPDATE, "on", "v1.0.0", "v1.1.0")
    await kit.settle()
    assert [n["message"] for n in notices] == ["v1.0.0 -> v1.1.0, stable release."]


async def test_pep440_beta_marker_counts_as_pre_release(kit):
    notices = await start(kit)
    update(kit, OTHER, "on", "0.1.81", "0.1.82b2")
    await kit.settle()
    assert notices[0]["message"].endswith("pre-release.")


async def test_a_commit_hash_is_a_commit_build_even_when_it_looks_like_a_beta_marker(kit):
    notices = await start(kit)
    # "e0b2" ends like PEP 440 "0b2"; a hex hash must never read as a beta.
    update(kit, UPDATE, "on", "faad594", "abc1e0b2")
    await kit.settle()
    assert [n["message"] for n in notices] == ["faad594 -> abc1e0b2, commit build (no release yet)."]


async def test_a_newer_version_while_on_sends_a_second_notice(kit):
    notices = await start(kit)
    update(kit, UPDATE, "on", "v1.0.0", "v1.1.0-beta.1")
    await kit.settle()
    update(kit, UPDATE, "on", "v1.0.0", "v1.1.0-beta.2")
    await kit.settle()
    assert [n["message"] for n in notices] == ["v1.0.0 -> v1.1.0-beta.1, pre-release.",
                                               "v1.0.0 -> v1.1.0-beta.2, pre-release."]


async def test_other_attribute_changes_and_turning_off_send_nothing(kit):
    notices = await start(kit)
    update(kit, UPDATE, "on", "v1.0.0", "v1.1.0")
    await kit.settle()
    kit.set(UPDATE, "on", {**kit.hass.states.get(UPDATE).attributes, "in_progress": True})
    await kit.settle()
    update(kit, UPDATE, "off", "v1.1.0", "v1.1.0")
    await kit.settle()
    assert len(notices) == 1


async def test_coming_back_from_unavailable_sends_nothing(kit):
    notices = await start(kit)
    kit.set(UPDATE, "unavailable")
    await kit.settle()
    update(kit, UPDATE, "on", "v1.0.0", "v1.1.0")
    await kit.settle()
    assert notices == []


async def test_pre_release_switch_is_turned_on_at_start(kit):
    # The start trigger arms only while Home Assistant is starting, as on a real box.
    kit.hass.set_state(CoreState.not_running)
    await start(kit, switch="off")
    kit.hass.set_state(CoreState.running)
    kit.hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await kit.settle()
    assert kit.calls == [("turn_on", SWITCH)]


async def test_pre_release_switch_is_turned_on_at_reload_and_left_alone_when_on(kit):
    await start(kit, switch="off")
    kit.hass.bus.async_fire("automation_reloaded")
    await kit.settle()
    assert kit.calls == [("turn_on", SWITCH)]
    kit.calls.clear()
    kit.hass.bus.async_fire("automation_reloaded")
    await kit.settle()
    assert kit.calls == []  # already on: nothing to do


async def test_a_disabled_switch_with_no_state_is_skipped(kit):
    await start(kit, switch="off")
    kit.hass.states.async_remove(SWITCH)
    kit.hass.bus.async_fire("automation_reloaded")
    await kit.settle()
    assert kit.calls == []
