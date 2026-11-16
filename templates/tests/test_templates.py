#!/usr/bin/env python3
"""test_templates.py - offline checks for the kit's templates. Run: python3 templates/tests/test_templates.py

Status: template (O3b, 2026-10-13). Exit 0 = every case passes. Needs jinja2 and PyYAML.

Covers: the router's decisions (notify.jinja), every health-check kind (health.jinja), the pace gate
(pacing/pace_gate.py), the checker's evaluation (tier2/checker.py with a fake API), the live export
(export/export_house.py with a fake Home Assistant), the runtime probe (runtime/probe_runtime.py with fake probes
and scratch git repositories), the usage reader (runtime/usage_reader.py with a fake endpoint) and the usage card's
macros and package (usage.jinja, packages/assistant-usage.yaml), the board checker (docs/board_check.py on the
seed board, the level-6 fragment and broken boards), the what-next facts (tools/what-next/what_next.py on scratch
house repositories at levels 0-2), and that every YAML template loads. After the house edits a macro, add a case here for the change (principles/testing-and-simulation.md).
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

import yaml

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATES = HERE.parent
sys.path.insert(0, str(HERE))
from ha_stub import env_for, render  # noqa: E402

FAILS = []


def case(name, got, want):
    ok = got == want
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"\n     got  {got!r}\n     want {want!r}"))
    if not ok:
        FAILS.append(name)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- router
PHONES = [
    {"label": "Owner", "service": "notify.mobile_app_owner_phone", "level_helper": "input_select.notify_level_owner",
     "platform": "ios", "owner": True},
    {"label": "Adult", "service": "notify.mobile_app_adult_phone", "level_helper": "input_select.notify_level_adult",
     "platform": "android"},
    {"label": "Child", "service": "notify.mobile_app_child_tablet", "level_helper": "input_select.notify_level_child",
     "platform": "android", "minor": True},
]
BASE = {"input_boolean.notifications_enabled": "on", "input_select.notify_level_owner": "Everything",
        "input_select.notify_level_adult": "Security and reminders", "input_select.notify_level_child": "Alarms only"}


def recipients(cls, states=None, tag=""):
    st = dict(BASE, **(states or {}))
    src = ("{% from 'notify.jinja' import notify_recipients %}"
           "{{ notify_recipients(phones, cls, tag, 'input_boolean.notifications_enabled') }}")
    out = json.loads(render(src, st, phones=json.dumps(PHONES), cls=cls, tag=tag))
    return [p["label"] for p in out]


case("router: alarm reaches level >= 1", recipients("alarm"), ["Owner", "Adult", "Child"])
case("router: security skips Alarms-only", recipients("security"), ["Owner", "Adult"])
case("router: no class defaults to security", recipients(""), ["Owner", "Adult"])
case("router: unknown class defaults to security", recipients("freezer"), ["Owner", "Adult"])
case("router: health needs Everything", recipients("health"), ["Owner"])
case("router: maintainer is owner only", recipients("maintainer", {"input_select.notify_level_adult": "Everything"}),
     ["Owner"])
case("router: switch off silences security", recipients("alarm", {"input_boolean.notifications_enabled": "off"}), [])
case("router: life safety ignores switch and levels",
     recipients("life_safety", {"input_boolean.notifications_enabled": "off",
                                "input_select.notify_level_child": "Nothing"}), ["Owner", "Adult", "Child"])
case("router: missing level helper counts as Everything",
     recipients("health", {"input_select.notify_level_owner": "unknown"}), ["Owner"])
case("router: Nothing gets nothing but life safety",
     recipients("alarm", {"input_select.notify_level_adult": "Nothing"}), ["Owner", "Child"])
case("router: the switched-off notice passes for 60 s",
     recipients("maintainer", {"input_boolean.notifications_enabled": {"state": "off", "changed_min_ago": 0.5}},
                tag="notifications_off"), ["Owner"])
case("router: ...and not after",
     recipients("maintainer", {"input_boolean.notifications_enabled": {"state": "off", "changed_min_ago": 2}},
                tag="notifications_off"), [])


def payload(phone, cls, actions, critical, tag="alarm_armed"):
    src = ("{% from 'notify.jinja' import notify_payload, notify_slot %}"
           "{{ notify_payload(phone, cls, notify_slot(tag, 1), actions, critical) }}")
    return json.loads(render(src, BASE, phone=json.dumps(phone), cls=cls, tag=tag,
                             actions=json.dumps(actions), critical=critical))


ARM = [{"action": "ARM_AWAY", "title": "Arm"}]
DISMISS = [{"action": "DISMISS", "title": "Dismiss"}]
p = payload(PHONES[1], "security", ARM, False)
case("router: slot shared by related tags", p["tag"], "alarm_state")
case("router: android high priority, no expiry", (p["ttl"], p["priority"], "channel" in p), (0, "high", False))
case("router: caller's buttons kept for an adult", p["actions"], ARM)
case("router: a minor gets Dismiss only", payload(PHONES[2], "security", ARM, False)["actions"], DISMISS)
case("router: no buttons -> Dismiss", payload(PHONES[1], "reminder", [], False)["actions"], DISMISS)
case("router: critical honored for alarm (android)", payload(PHONES[1], "alarm", [], True)["channel"], "alarm_stream")
case("router: critical refused for security",
     payload(PHONES[0], "security", [], True)["push"]["interruption-level"], "time-sensitive")
case("router: critical honored for life safety (ios)",
     payload(PHONES[0], "life_safety", [], True)["push"]["interruption-level"], "critical")


def dry(dry_run, cls, test_on):
    st = {"input_boolean.notify_test_mode": "on" if test_on else "off"}
    src = ("{% from 'notify.jinja' import notify_dry %}"
           "{{ notify_dry(dry_run, cls, 'input_boolean.notify_test_mode') }}")
    return render(src, st, dry_run=dry_run, cls=cls)


case("router: test mode off, no dry run -> delivers", dry(False, "security", False), "False")
case("router: caller's dry run -> nothing delivered", dry(True, "security", False), "True")
case("router: test mode on -> every class is a dry run", [dry(False, c, True) for c in ("alarm", "health", "")],
     ["True", "True", "True"])
case("router: test mode never holds back life safety", dry(False, "life_safety", True), "False")
case("router: a caller's dry run still holds back life safety", dry(True, "life_safety", False), "True")
case("router: dry_run as the string HA may pass", dry("true", "house", False), "True")
case("router: no tag -> unique slot", payload(PHONES[1], "reminder", [], False, tag="")["tag"], "note_1")

# ---------------------------------------------------------------- health
HEALTHY = {
    "sensor.front_door_lock_battery": "80", "lock.front_door": "locked",
    "input_number.health_battery_fault_pct": "15", "input_number.health_battery_notice_pct": "30",
    "automation.health_fault_push": "on", "automation.health_all_clear_push": "on",
    "binary_sensor.kitchen_sink_leak": {"state": "off", "changed_min_ago": 600, "reported_min_ago": 60},
    "input_boolean.notifications_enabled": "on",
    "sensor.backup_last_successful_automatic_backup": "2026-01-15T03:00:00+00:00",
    "light.kitchen_ceiling": "off", "light.hall_ceiling": "on", "switch.porch_light": "off",
    "input_datetime.health_planned_restart_until": "unknown",
    "input_boolean.notify_test_mode": "off",
    "sensor.system_monitor_disk_usage": {"state": "41.3", "attributes": {"unit_of_measurement": "%"}},
    "sensor.system_monitor_processor_temperature": {"state": "52", "attributes": {"unit_of_measurement": "°C"}},
}
HEALTHY["light.kitchen_ceiling"] = {"state": "off", "entry_state": "loaded"}


def health(sub, changes=None):
    st = dict(HEALTHY, **(changes or {}))
    for k, v in list(st.items()):
        if v is None:
            del st[k]
    return json.loads(render("{% from 'health.jinja' import health %}{{ health('" + sub + "') }}", st))


def summary(h):
    return (h["faults"], h["notices"], h["severity"], [f["why"] for f in h["findings"]])


for sub in ("security", "plumbing", "system", "network"):
    case(f"health: {sub} healthy", summary(health(sub)), (0, 0, "ok", []))
case("health: battery fault", summary(health("security", {"sensor.front_door_lock_battery": "12"})),
     (1, 0, "fault", ["battery 12 %"]))
case("health: battery notice", summary(health("security", {"sensor.front_door_lock_battery": "22"})),
     (0, 1, "notice", ["battery 22 %"]))
case("health: battery threshold read from the helper",
     summary(health("security", {"sensor.front_door_lock_battery": "22",
                                 "input_number.health_battery_fault_pct": "25"})), (1, 0, "fault", ["battery 22 %"]))
case("health: a battery unavailable for a day, with no unavailable check of its own, is a fault",
     summary(health("security", {"sensor.front_door_lock_battery": "unavailable"})),
     (1, 0, "fault", ["unavailable since"]))
case("health: a battery reading unknown for 45 min is a fault, as unavailable is",
     summary(health("security", {"sensor.front_door_lock_battery": {"state": "unknown", "changed_min_ago": 45}})),
     (1, 0, "fault", ["reading unknown since"]))
case("health: ...but not in its first 30 min (a restart is not an alarm)",
     summary(health("security", {"sensor.front_door_lock_battery": {"state": "unknown", "changed_min_ago": 10}})),
     (0, 0, "ok", []))
case("health: lock unavailable 10 min is not yet a fault",
     summary(health("security", {"lock.front_door": {"state": "unavailable", "changed_min_ago": 10}})), (0, 0, "ok", []))
case("health: lock unavailable 45 min is a fault",
     summary(health("security", {"lock.front_door": {"state": "unavailable", "changed_min_ago": 45}})),
     (1, 0, "fault", ["unavailable since"]))
case("health: a watcher switched off is a fault",
     summary(health("security", {"automation.health_fault_push": "off"})), (1, 0, "fault", ["automation is off"]))
case("health: silent 30 h is a notice, never a fault",
     summary(health("plumbing", {"binary_sensor.kitchen_sink_leak": {"state": "off", "reported_min_ago": 1800}})),
     (0, 1, "notice", ["no report since"]))
case("health: notifications off is a fault",
     summary(health("system", {"input_boolean.notifications_enabled": "off"})), (1, 0, "fault", ["is off"]))
case("health: backup 40 h old is a notice",
     summary(health("system", {"sensor.backup_last_successful_automatic_backup": "2026-01-13T20:00:00+00:00"})),
     (0, 1, "notice", ["last updated"]))
case("health: backup 3 days old is a fault",
     summary(health("system", {"sensor.backup_last_successful_automatic_backup": "2026-01-12T12:00:00+00:00"})),
     (1, 0, "fault", ["last updated"]))
case("health: 2 of 3 online is a notice",
     summary(health("network", {"light.hall_ceiling": "unavailable"})), (0, 1, "notice", ["2 of 3 online"]))
case("health: 0 of 3 online is a fault",
     summary(health("network", {**{e: "unavailable" for e in ("light.hall_ceiling", "switch.porch_light")},
                                        "light.kitchen_ceiling": {"state": "unavailable", "entry_state": "loaded"}})), (1, 0, "fault", ["0 of 3 online"]))
case("health: planned restart suppresses the mesh check",
     summary(health("network", {**{e: "unavailable" for e in ("light.hall_ceiling", "switch.porch_light")},
                                "light.kitchen_ceiling": {"state": "unavailable", "entry_state": "loaded"},
                                "input_datetime.health_planned_restart_until": "2026-01-15T12:20:00+00:00"})),
     (0, 0, "ok", []))
case("health: a check whose entity is gone is a notice, not a pass",
     summary(health("security", {"sensor.front_door_lock_battery": None})),
     (0, 1, "notice", ["check source gone: sensor.front_door_lock_battery"]))
case("health: test mode left on is a notice",
     summary(health("system", {"input_boolean.notify_test_mode": {"state": "on", "changed_min_ago": 30}})),
     (0, 1, "notice", ["is on since 11:30 AM"]))
case("health: disk use over the notice line",
     summary(health("system", {"sensor.system_monitor_disk_usage": {"state": "84.6",
                                                                     "attributes": {"unit_of_measurement": "%"}}})),
     (0, 1, "notice", ["at 85 %"]))
case("health: processor temperature over the fault line",
     summary(health("system", {"sensor.system_monitor_processor_temperature": "88"})), (1, 0, "fault", ["at 88"]))
case("health: an above reading that cannot be read is a fault, not a pass",
     [summary(health("system", {"sensor.system_monitor_disk_usage": v})) for v in ("unavailable", "unknown", "n/a")],
     [(1, 0, "fault", ["unavailable since"])] + [(1, 0, "fault", ["reading unknown since"])] * 2)
case("health: an age reading unknown is a fault, not a pass",
     summary(health("system", {"sensor.backup_last_successful_automatic_backup": "unknown"})),
     (1, 0, "fault", ["reading unknown since"]))
case("health: an age source unavailable is reported once, by its own unavailable check",
     summary(health("system", {"sensor.backup_last_successful_automatic_backup": "unavailable"})),
     (1, 0, "fault", ["unavailable since"]))
case("health: integration in setup retry is a fault",
     summary(health("network", {"light.kitchen_ceiling": {"state": "unavailable", "entry_state": "setup_retry",
                                                          "changed_min_ago": 1}})),
     (1, 1, "fault", ["2 of 3 online", "integration setup retry"]))
case("health: integration still starting is not a finding",
     summary(health("network", {"light.kitchen_ceiling": {"state": "on", "entry_state": "setup_in_progress"}})),
     (0, 0, "ok", []))
case("health: integration check on an entity no integration owns is a notice, not a crash",
     summary(health("network", {"light.kitchen_ceiling": "on"})),
     (0, 1, "notice", ["check source gone: light.kitchen_ceiling has no integration entry"]))
case("health: unknown subsystem is empty", summary(health("garden")), (0, 0, "ok", []))

# ---------------------------------------------------------------- pace gate
gate = load(TEMPLATES / "pacing" / "pace_gate.py", "pace_gate")
READ = """read 2026-01-14 23:45 UTC
 Current week (all models)
 25% used
 Resets Jan 17, 9:59pm (UTC)
 Current week (Opus)
 30% used
 Resets Jan 17, 9:59pm (UTC)
"""
from datetime import datetime, timezone  # noqa: E402
NOW = datetime(2026, 1, 14, 22, 0, tzinfo=timezone.utc)  # 4 of 7 days into the week
r = gate.decide(READ, now=NOW.replace(day=15, hour=0), buffer=10, model="Opus")
case("pace: line = 90 x fraction elapsed", round(r["line"], 1), 52.5)
case("pace: under the line runs", r["run"], True)
r = gate.decide(READ.replace("30% used", "60% used"), now=NOW.replace(day=15, hour=0), buffer=10, model="Opus")
case("pace: the model figure over the line skips", (r["run"], "Opus" in r["why"]), (False, True))
r = gate.decide(READ, now=datetime(2026, 1, 11, 0, 0, tzinfo=timezone.utc), buffer=10, model="Opus")
case("pace: no floor by default (early week, 25 % used, skips)", (round(r["line"], 1) < 15.0, r["run"]), (True, False))
r15 = gate.decide(READ, now=datetime(2026, 1, 11, 0, 0, tzinfo=timezone.utc), buffer=10, model="Opus", floor=15)
case("pace: --floor 15 sets a floor", round(r15["line"], 1), 15.0)
r = gate.decide(READ, now=datetime(2026, 1, 15, 2, 0, tzinfo=timezone.utc), buffer=10, model="Opus")
case("pace: a read over 2 h old needs 10 points of margin", (r["stale"], r["run"]), (True, True))
r = gate.decide(READ.replace("30% used", "47% used"), now=datetime(2026, 1, 15, 2, 0, tzinfo=timezone.utc),
                buffer=10, model="Opus")
case("pace: ...and skips inside the margin", r["run"], False)
r = gate.decide(READ.replace("30% used", "47% used"), now=datetime(2026, 1, 15, 1, 0, tzinfo=timezone.utc),
                buffer=10, model="Opus")
case("pace: a read 75 minutes old is fresh", (r["stale"], r["run"]), (False, True))
LAST_WEEK = READ.replace("25% used", "95% used").replace("read 2026-01-14 23:45", "read 2026-01-17 21:45")
r = gate.decide(LAST_WEEK, now=datetime(2026, 1, 18, 1, 0, tzinfo=timezone.utc), buffer=10)
case("pace: a read from last week counts as 0 %, stale: early in the new week it waits for a fresh read",
     (r["week_pct"], r["stale"], r["run"]), (0.0, True, False))
r = gate.decide(LAST_WEEK, now=datetime(2026, 1, 18, 18, 0, tzinfo=timezone.utc), buffer=10)
case("pace: ...and under the age limit, past the margin, it runs", (r["week_pct"], r["run"]), (0.0, True))
r = gate.decide(LAST_WEEK, now=datetime(2026, 1, 18, 22, 0, tzinfo=timezone.utc), buffer=10)
case("pace: KIT-GATE.r F1 - a read over 24 h old never runs, last week's or not",
     (r["run"], "usage read too old" in r["why"]), (False, True))
r = gate.decide(READ.replace("25% used", "80% used"), now=datetime(2026, 1, 20, 1, 0, tzinfo=timezone.utc), buffer=10)
case("pace: ...a dead reader is a stop, not a margin (80 % read on Jan 14, now Jan 20: was RUN)", r["run"], False)
r = gate.decide(READ, now=datetime(2026, 1, 15, 22, 0, tzinfo=timezone.utc), buffer=10, max_age_hours=12)
case("pace: --max-age-hours sets the limit", (r["run"], "limit 12 h" in r["why"]), (False, True))
r = gate.decide("garbage", now=NOW, buffer=10)
case("pace: an unreadable file never runs", r["run"], False)
import json as _json  # noqa: E402
READ_JSON = _json.dumps({"schema": 1, "status": "ok", "read_at": "2026-01-14T23:45:00+00:00",
                         "week": {"pct": 25.0, "resets_at": "2026-01-17T21:59:00+00:00"},
                         "models": {"opus": {"pct": 30.0, "resets_at": "2026-01-17T21:59:00+00:00"}}})
r = gate.decide(READ_JSON, now=NOW.replace(day=15, hour=0), buffer=10, model="Opus")
case("pace: reads usage_reader.py's JSON the same as the probe text", (round(r["line"], 1), r["run"], r["stale"]),
     (52.5, True, False))
r = gate.decide(READ_JSON.replace('"pct": 30.0', '"pct": 60.0'), now=NOW.replace(day=15, hour=0), buffer=10, model="Opus")
case("pace: JSON model figure over the line skips", r["run"], False)
r = gate.decide(_json.dumps({"schema": 1, "status": "error", "read_at": None}), now=NOW, buffer=10)
case("pace: a reader file with no figures never runs", r["run"], False)
for _bad in ("NaN", "-5.0", "Infinity"):  # KIT-GUARD-FIX (from KAN-2cr F5): not a reading, so never a run
    r = gate.decide(READ_JSON.replace('"pct": 30.0', '"pct": ' + _bad), now=NOW.replace(day=15, hour=0), buffer=10,
                    model="Opus")
    case(f"pace: a JSON model figure of {_bad} is missing, never a run", r["run"], False)
r = gate.decide(READ_JSON.replace('"read_at": "2026-01-14T23:45:00+00:00", ', ''), now=NOW.replace(day=15, hour=0),
                buffer=10)
case("pace: figures with no read time never run", (r["run"], "read time is unknown" in r["why"]), (False, True))
import contextlib as _cl  # noqa: E402
import io as _io  # noqa: E402
with _cl.redirect_stdout(_io.StringIO()):
    case("pace: a bad --target is exit 2 (bad arguments)", gate.main(["--file", "/nonexistent", "--target", "x"]), 2)
    case("pace: a missing reading is a skip, exit 1", gate.main(["--file", "/nonexistent"]), 1)

# ---------------------------------------------------------------- preflight (no-model GO/SKIP)
pf = load(TEMPLATES / "pacing" / "preflight.py", "preflight")
PF_BOARD = """# Board

## Items

| Item | Lane | Pts | Status | Link | Decisions needed |
|---|---|---|---|---|---|
| **A1 Build the porch light** | builder | 2 | BACKLOG [P3] | | none |
| **A2 Wire the porch sensor** | builder | 1 | BACKLOG (after A3) [P1] | | none |
| **A3 Pick the porch sensor** | owner | 0.5 | BACKLOG (owner) [P1] | | none |
| **A4 Read the box log [BOX]** | builder | 1 | BACKLOG [P1] | | none |
| **A5 Review A6** | reviewer | 1 | BACKLOG (after A6 in review) [P2] | | none |
| **A6 Build the garage check** | builder | 2 | READY FOR REVIEW [P2] | | none |
| **A7 Blocked thing** | builder | 1 | BLOCKED by A3 [P1] | | none |
| **A8 Old thing** | builder | 1 | BACKLOG (after A0: met 2026-01-01) [P2] | | none |
| **A9 Check the box disk** Needs the box: [BOX] | builder | 1 | BACKLOG [P1] | | none |
| **A10 Wait for the export** | builder | 1 | BACKLOG (after Tue export) [P1] | | none |

## Run log
"""
import argparse as _ap  # noqa: E402
import tempfile as _tf  # noqa: E402


def pf_args(**kw):
    d = dict(lane="builder", role="lane", cannot=["BOX"], usage=None, buffer=10.0, model=None, target=None, floor=0.0,
             stale_hours=2.0, runs_per_day=None, runs_log="/nonexistent/runs.log", month_usd=None,
             spend_ledger="/nonexistent/spend.log", stop="/nonexistent/STOP")
    d.update(kw)
    return _ap.Namespace(**d)


bc = load(TEMPLATES / "docs" / "board_check.py", "board_check_pf")
rows = bc.parse_board(PF_BOARD)["items"]
case("preflight: eligible order (P2 met-after before P3; unmet after, [BOX], blocked, review rows out)",
     [r["code"] for r in pf.ordered(rows, "builder")], ["A8", "A1"])
case("preflight: an 'after X in review' row is eligible once X is in review",
     [r["code"] for r in pf.ordered(rows, "reviewer")], ["A5"])
by = {r["code"]: r for r in rows}
case("preflight: an unmet after says which", pf.eligible(by["A2"], "builder", by), (False, "after A3 not met"))
case("preflight: KIT-GATE.r F3 - a runtime tag in the Item cell's free text is read", pf.eligible(by["A9"], "builder", by),
     (False, "[BOX] row"))
case("preflight: KIT-GATE.r F6 - an 'after' word that is no code says so",
     [c for c, w in pf.why_not(rows, "builder") if "no row Tue on the board" in w], ["A10"])
case("preflight: ...and why_not lists the lane's open, ineligible rows only",
     [c for c, _ in pf.why_not(rows, "builder")], ["A2", "A4", "A9", "A10"])
go, line = pf.decide(pf_args(runs_per_day=5), NOW, PF_BOARD, None, gate, bc)
case("preflight: work and budget -> GO naming the first row", (go, line.startswith("GO builder: 2 eligible, first A8")),
     (True, True))
go, line = pf.decide(pf_args(), NOW, PF_BOARD, None, gate, bc)
case("preflight: no budget mode set is no unattended run", (go, "no budget mode" in line), (False, True))
go, line = pf.decide(pf_args(lane="writer"), NOW, PF_BOARD, None, gate, bc)
case("preflight: nothing eligible is a SKIP before any budget read", (go, "nothing eligible" in line), (False, True))
go, line = pf.decide(pf_args(usage="u.json", model="Opus"), NOW.replace(day=15, hour=0),
                     PF_BOARD, READ_JSON.replace('"pct": 30.0', '"pct": 60.0'), gate, bc)
case("preflight: a budget SKIP has the board's skip-line shape", (go, bool(bc.SKIP_RE.match(line))), (False, True))
go, line = pf.decide(pf_args(usage="u.json", model="Opus"), datetime(2026, 1, 16, 2, 0, tzinfo=timezone.utc),
                     PF_BOARD, READ_JSON, gate, bc)
case("preflight: KIT-GATE.r F2 - a too-old read's SKIP has a board skip shape",
     (go, "no usable read" in line, bool(bc.SKIP_RE.match(line))), (False, True, True))
go, line = pf.decide(pf_args(usage="u.json"), NOW.replace(day=15, hour=0), PF_BOARD,
                     READ_JSON.replace('"read_at": "2026-01-14T23:45:00+00:00", ', ''), gate, bc)
case("preflight: ...and one with no read time", (go, bool(bc.SKIP_RE.match(line))), (False, True))
case("board_check: the percentage skip shape with a month suffix matches",
     bool(bc.SKIP_RE.match("2026-01-14 22:00 UTC builder skipped: budget (week 60 %, Opus 70 %, line 52.5 %, "
                           "read 2026-01-14 21:45 UTC; month $60.00 of $50.00)")), True)
case("board_check: a skip line in no known shape does not match",
     bool(bc.SKIP_RE.match("2026-01-14 22:00 UTC builder skipped: budget (it felt like a lot)")), False)
case("board_check: a skip line with a month suffix that is not dollars does not match",
     bool(bc.SKIP_RE.match("2026-01-14 22:00 UTC builder skipped: budget (count mode: 2 of 2 runs today; month 60)")),
     False)
_wb = bc.parse_board(PF_BOARD.replace("| **A1 Build the porch light** |", "| **A1 Build the porch light** after A6 |"))
case("board_check: KIT-GATE.r F3 - 'after <CODE>' in an open row's Item cell is a warning, not a fault",
     ([(c, "Item cell" in m) for _, c, m in _wb["warnings"]], _wb["faults"] == bc.parse_board(PF_BOARD)["faults"]),
     ([("A1", True)], True))
go, line = pf.decide(pf_args(role="monitor", usage="u.json", model="Opus"), NOW.replace(day=15, hour=0),
                     None, READ_JSON.replace('"pct": 30.0', '"pct": 99.0'), gate, bc)
case("preflight: monitoring is never budget-blocked; only its idle work is", (go, "idle work: no" in line), (True, True))
with _tf.TemporaryDirectory() as _d:
    stop = pathlib.Path(_d) / "STOP"
    stop.write_text("")
    go, line = pf.decide(pf_args(role="monitor", stop=str(stop)), NOW, None, None, gate, bc)
    case("preflight: the off switch stops every role, monitoring included", (go, "off switch" in line), (False, True))
    log = pathlib.Path(_d) / "runs.log"
    log.write_text("2026-01-14 08:00 builder GO\n2026-01-14 12:00 builder GO\n2026-01-13 08:00 builder GO\n")
    go, line = pf.decide(pf_args(runs_per_day=2, runs_log=str(log)), NOW, PF_BOARD, None, gate, bc)
    case("preflight: count mode stops at runs_per_day for today", (go, "2 of 2" in line), (False, True))
    case("preflight: KIT-GATE.r F2 - the count-mode SKIP matches the board's skip shape", bool(bc.SKIP_RE.match(line)),
         True)
    go, _ = pf.decide(pf_args(runs_per_day=3, runs_log=str(log)), NOW, PF_BOARD, None, gate, bc)
    case("preflight: ...and runs under it", go, True)
    led = pathlib.Path(_d) / "spend.log"
    led.write_text("2026-01-02 builder 30.50\n2026-01-10 builder 19.60\n2025-12-30 builder 99\n")
    go, line = pf.decide(pf_args(runs_per_day=5, month_usd=50, spend_ledger=str(led)), NOW, PF_BOARD, None, gate, bc)
    case("preflight: the month's API spend at the cap is a SKIP", (go, "$50.10 of $50.00" in line), (False, True))
    case("preflight: KIT-GATE.r F2 - ...and its line matches the board's skip shape", bool(bc.SKIP_RE.match(line)),
         True)
    go, _ = pf.decide(pf_args(runs_per_day=5, month_usd=60, spend_ledger=str(led)), NOW, PF_BOARD, None, gate, bc)
    case("preflight: ...and under it runs", go, True)

    import contextlib as _cl  # noqa: E402
    import io as _io  # noqa: E402

    def pf_main(*argv):
        out = _io.StringIO()
        with _cl.redirect_stdout(out):
            rc = pf.main(list(argv))
        return rc, out.getvalue().strip()

    mlog = pathlib.Path(_d) / "monitor-runs.log"
    mon = ("checker", "--role", "monitor", "--runs-per-day", "1", "--runs-log", str(mlog),
           "--stop", str(pathlib.Path(_d) / "no-stop"), "--now", "2026-01-15T09:00:00+00:00")
    first, second = pf_main(*mon), pf_main(*mon)
    case("preflight: count mode records a monitor's idle start, so a one-run ceiling allows one idle start a day",
         (first[0], "idle work: yes (count mode: 0 of 1" in first[1], second[0], "idle work: no (count mode: 1 of 1"
          in second[1], mlog.read_text() if mlog.exists() else "no log"), (0, True, 0, True, "2026-01-15 09:00 checker GO idle\n"))
    case("preflight: ...and the claim takes the last place only once, under the lock",
         (pf.claim_run(mlog, "other", NOW, 1), pf.claim_run(mlog, "other", NOW, 1)), ((True, 0), (False, 1)))

    # A runs log that cannot be written (here a directory) must not stop monitoring: the checker runs only on exit 0.
    bad = pathlib.Path(_d) / "runs-log-is-a-directory"
    bad.mkdir()
    base = ("--runs-per-day", "1", "--runs-log", str(bad), "--stop", str(pathlib.Path(_d) / "no-stop"),
            "--now", "2026-01-15T09:00:00+00:00")
    _err = _io.StringIO()
    with _cl.redirect_stderr(_err):
        mon_bad = pf_main("checker", "--role", "monitor", *base)
    case("preflight: an unwritable runs log keeps the monitor GO with exit 0, denies idle work and reports the error",
         (mon_bad[0], mon_bad[1].startswith("GO monitor"), "idle work: no (count mode: runs log not writable"
          in mon_bad[1], "preflight: runs log:" in _err.getvalue()), (0, True, True, True))
    pf_board = pathlib.Path(_d) / "board.md"
    pf_board.write_text(PF_BOARD, encoding="utf-8")
    with _cl.redirect_stderr(_io.StringIO()):
        lane_bad = pf_main("builder", "--board", str(pf_board), *base)
    case("preflight: ...and lane work fails closed on the same log",
         (lane_bad[0], "builder skipped: budget (count mode: runs log not writable" in lane_bad[1]), (1, True))

# ---------------------------------------------------------------- checker
ck = load(TEMPLATES / "tier2" / "checker.py", "checker")
ck_cases = ck.selftest_cases()
for name, got, want in ck_cases:
    case("checker: " + name, got, want)


def ck_run(d, env, states):
    """One real checker run (run()) against a fake API: findings.json, the wake command and wake.log are real."""
    keep_env, keep_api = dict(os.environ), ck.api
    os.environ.update(TIER2_DIR=str(d), HA_TOKEN_FILE=str(d / "token"), **env)
    ck.api = lambda path, ctx: states if path == "/api/states" else []
    try:
        return ck.run()
    finally:
        os.environ.clear()
        os.environ.update(keep_env)
        ck.api = keep_api


with tempfile.TemporaryDirectory() as _d:
    d = pathlib.Path(_d)
    (d / "token").write_text("not-a-real-token\n")
    got = d / "got.txt"
    capture = d / "capture.py"
    capture.write_text("import sys\nopen(sys.argv[1], 'a').write(sys.argv[-1] + '\\n')\n")
    good = f"{sys.executable} {capture} {got}"
    bad = f"{sys.executable} -c 'import sys; sys.exit(3)'"
    off = [{"entity_id": "automation.health_fault_push", "state": "off", "last_changed": "2026-01-15T00:00:00+00:00"},
           {"entity_id": "automation.tier2_checker_silent", "state": "on", "last_changed": "2026-01-15T00:00:00+00:00"}]
    rc1 = ck_run(d, {"WAKE_CMD": bad, "WAKE_RETRY_MIN": "0"}, off)
    log1 = (d / "wake.log").read_text() if (d / "wake.log").exists() else ""
    rc2 = ck_run(d, {"WAKE_CMD": good, "WAKE_RETRY_MIN": "0"}, off)
    rc3 = ck_run(d, {"WAKE_CMD": good, "WAKE_RETRY_MIN": "0"}, off)
    case("checker run: a failed wake exits 1 and is logged; the still-active finding is woken on the next run, once",
         (rc1, "wake failed for W1:automation.health_fault_push: exit 3" in log1, rc2, rc3,
          got.read_text() if got.exists() else "nothing received"),
         (1, True, 0, 0, "W1:automation.health_fault_push\n"))
    env = {k: v for k, v in os.environ.items() if k != "WAKE_CMD"}
    r_unset = subprocess.run([sys.executable, str(TEMPLATES / "tier2" / "checker.py"), "--wake-test"],
                             env=env, capture_output=True, text=True, timeout=60)
    r_set = subprocess.run([sys.executable, str(TEMPLATES / "tier2" / "checker.py"), "--wake-test"],
                           env=dict(env, WAKE_CMD=good), capture_output=True, text=True, timeout=60)
    case("checker --wake-test: no WAKE_CMD exits 2; a harmless capture command receives the test id and exits 0",
         (r_unset.returncode, r_set.returncode, (got.read_text().splitlines() if got.exists() else ["none"])[-1]),
         (2, 0, "T0:wake-test"))


# ---------------------------------------------------------------- level 4 readiness text (00-start-here/levels.md)
LEVELS = (TEMPLATES.parent / "00-start-here" / "levels.md").read_text(encoding="utf-8")
L4 = LEVELS[LEVELS.index("### Level 4"):LEVELS.index("### Level 5")]
case("levels: L4 readiness proves a finding wakes the agent with the real wake command, and unset is a fail",
     ("`L4-wake`" in L4, "--wake-test" in L4, "T0:wake-test" in L4, "An unset `WAKE_CMD` (exit 2) is `fail`" in L4,
      "| L4-wake |" in LEVELS), (True, True, True, True, True))
case("levels: L4-act-denied no longer passes on a missing wrapper alone; other write paths must be refused",
     ("no wrapper installed = pass" in LEVELS, "A missing wrapper\n    proves nothing on its own" in L4,
      "give `unknown`, never `pass`" in L4), (False, True, True))
case("levels: the monitor's 'always GO' names the owner's off switch",
     "while `pacing/STOP` exists the preflight answers SKIP for monitoring too" in L4, True)

# L3-update-applied (F3 of the level 3 review): no helper reads it yet, so the contract is the text itself.
L3 = " ".join(LEVELS[LEVELS.index("### Level 3"):LEVELS.index("### Level 4")].split())
L3_UPDATE = L3[L3.index("`L3-update-applied`"):L3.index("`L3-restore-drill`")]
L3_ROW = " ".join(next(ln for ln in LEVELS.splitlines() if "L3-update-applied" in ln and ln.startswith("|")).split())
case("levels: L3-update-applied needs a verdict, a CHANGELOG entry with the undo, and a later-day check",
     ("ALL CLEAR or CLEAR WITH ACTIONS" in L3_UPDATE, "a HOLD is a review, not an application" in L3_UPDATE,
      "a CHANGELOG entry with the undo" in L3_UPDATE, "dated a later day than the entry" in L3_UPDATE),
     (True, True, True, True))
case("levels: ...the three are tied by the update row's code, so evidence of three different updates does not pass",
     ("tied by the update row's code" in L3_UPDATE, "the CHANGELOG entry names it" in L3_UPDATE,
      "the review file the row links" in L3_UPDATE), (True, True, True))
case("levels: ...a missing piece is fail and unreadable evidence is unknown, in the text and in the sources table",
     ("Any of the three not found is `fail`" in L3_UPDATE, "cannot be read is `unknown`" in L3_UPDATE,
      "the board row whose code the entry names" in L3_ROW, "`unknown` (unreadable)" in L3_ROW,
      "no row, verdict or later-day check to match" in L3_ROW), (True, True, True, True, True))


# ---------------------------------------------------------------- router script wiring
# Render the script's OWN templates from the YAML, the way Home Assistant chains script variables: each rendered
# string goes through native-type parsing (literal_eval) before the next template sees it.
import ast  # noqa: E402


def native(text):
    try:
        v = ast.literal_eval(text.strip())
        return v if isinstance(v, (list, dict, bool, int, float)) else text.strip()
    except (ValueError, SyntaxError):
        return text.strip()


class _L(yaml.SafeLoader):
    pass


router = yaml.load((TEMPLATES / "packages" / "notification-router.yaml").read_text(), Loader=_L)["script"]["notify"]
v = {"phones": router["variables"]["phones"], "class": "security", "message": "m", "actions": None,
     "critical": None, "dry_run": None, "title": None, "tag": "alarm_armed"}
for step in router["sequence"]:
    if "variables" in step:
        for k, tpl in step["variables"].items():
            v[k] = native(render(tpl, BASE, **v))
case("wiring: recipients is a native list", [p["label"] for p in v["recipients"]], ["Owner", "Adult"])
case("wiring: slot", v["n_slot"], "alarm_state")
case("wiring: test mode off -> not a dry run", (v["n_dry"], v["n_test"]), (False, False))
vt = dict(v, **{"class": "security"})
for step in router["sequence"]:
    if "variables" in step:
        for k, tpl in step["variables"].items():
            vt[k] = native(render(tpl, dict(BASE, **{"input_boolean.notify_test_mode": "on"}), **vt))
case("wiring: test mode on -> a dry run, logged as test mode", (vt["n_dry"], vt["n_test"]), (True, True))
event = [s for s in router["sequence"] if "event" in s][0]["event_data"]
case("wiring: the call event records dry_run and test_mode", sorted(k for k in event if k in ("dry_run", "test_mode")),
     ["dry_run", "test_mode"])
clear = yaml.load((TEMPLATES / "packages" / "notification-router.yaml").read_text(),
                  Loader=_L)["script"]["notify_clear"]["variables"]["services"]
case("wiring: notify_clear's services match PHONES (FILL both together)", clear,
     [p["service"] for p in router["variables"]["phones"]])
loop = [s for s in router["sequence"] if "repeat" in s][0]["repeat"]["sequence"][0]
payload_tpl = loop["data"]["data"]
v["repeat"] = {"item": v["recipients"][1]}
got = native(render(payload_tpl, BASE, **v))
case("wiring: per-phone payload renders to a dict with Dismiss", (got["tag"], got["actions"][0]["action"]),
     ("alarm_state", "DISMISS"))
case("wiring: the loop's target is the phone's service", render(loop["action"], BASE, **v),
     "notify.mobile_app_adult_phone")

# ---------------------------------------------------------------- push guard
guard = load(TEMPLATES / "guard" / "push_guard.py", "push_guard")
GUARD_CASES = [
    ("clean yaml", ("ha/packages/x.yaml", "  alias: Porch light on at sunset"), []),
    ("!secret reference passes", ("ha/secrets_ref.yaml", "  token: !secret porch_api_token"), []),
    ("null value passes", ("house/profile.yaml", "  pin: null"), []),
    ("literal password refused", ("ha/x.yaml", "password: hunter22"), ["literal secret"]),  # guard: allow test fixture
    ("bearer refused", ("tools/a.sh", "curl -H 'Authorization: Bearer abcdefghijklmnopqrstuvwxyz123'"), ["bearer"]),  # guard: allow test fixture
    ("jwt refused", ("notes.md", "eyJhbGciOiJIUzI1.eyJpc3MiOiIxMjM0NTY3.abcdefghijklmnop"), ["jwt"]),  # guard: allow test fixture
    ("phone refused", ("docs/contacts.md", "call 555-201-4477"), ["phone"]),  # guard: allow test fixture
    ("allow marker passes", ("docs/x.md", "call 555-201-4477  guard: allow fictional example"), []),
    ("prose mention passes", ("docs/x.md", "   The pairing code is a setup secret: never copied."), []),
    ("indented key refused", ("ha/x.yaml", "    wifi_password: s3cretvalue"), ["literal secret"]),  # guard: allow test fixture
    ("env export refused", ("x.sh", "export HA_TOKEN=abcd1234efgh"), ["literal secret"]),  # guard: allow test fixture
    ("version number passes", ("docs/x.md", "HA 2026.10.1 on 192.168.1.20"), []),  # guard: allow test fixture
    # KIT-SAFE (sweep 2026-10-31, F2): shapes that went through before.
    ("json password refused", ("c.json", '{"user": "x", "password": "hunter22"}'), ["literal secret"]),  # guard: allow test fixture
    ("flow map password refused", ("c.yaml", "  wifi: {ssid: home, password: hunter22}"), ["literal secret"]),  # guard: allow test fixture
    ("url password refused", ("d.md", "rtsp://admin:hunter22@cam.local/s"), ["literal secret"]),  # guard: allow test fixture
    ("prose password refused", ("d.md", "the password is hunter22"), ["literal secret"]),  # guard: allow test fixture
    ("prose door code refused", ("d.md", "The door code is 4821."), ["literal secret"]),  # guard: allow test fixture
    ("PIN with colon refused", ("d.md", "Keypad PIN: 0000"), ["literal secret"]),  # guard: allow test fixture
    ("github classic token refused", ("x.sh", "T=ghp_" + "A1b2C3x4" * 5), ["api key"]),
    ("github fine-grained token refused", ("x.sh", "T=github_pat_" + "A1b2C3x4y5" * 6), ["api key"]),
    ("anthropic key refused", ("d.md", "sk-ant-api03-" + "x9Y8z7W6" * 4), ["api key"]),
    ("long hex refused", ("d.md", "webhook " + "0123456789abcdef" * 3), ["long hex"]),
    ("e164 phone refused", ("d.md", "call +12055550147"), ["phone"]),  # guard: allow test fixture
    ("ten-digit phone refused", ("d.md", "call 2055550147"), ["phone"]),  # guard: allow test fixture
    ("commit link passes", ("d.md", "https://github.com/o/r/commit/" + "0a1b2c3d4e" * 4), []),
    ("action pin passes", (".github/workflows/w.yml", "  - uses: actions/checkout@" + "0a1b2c3d4e" * 4), []),
    ("password by its key passes", ("d.md", "The password is in secrets.yaml under wifi_password."), []),
    ("templated password passes", ("c.yaml", "  password: \"{{ states('input_text.x') }}\""), []),
    ("secret ref in flow map passes", ("c.yaml", "  wifi: {ssid: home, password: !secret wifi}"), []),
    ("env var in url passes", ("x.sh", "curl https://user:${PASS}@host/x"), []),
    ("date after code passes", ("d.md", "error code 2026-10-31 in the log"), []),
    ("epoch seconds pass", ("d.md", "last_changed 1730000000"), []),
    ("entity id with digits passes", ("c.yaml", "sensor.zone_2055550147_temp"), []),
    # KIT-SAFE.f (review KIT-SAFE.r F2): token and key values the password-only shape let through.
    ("json token refused", ("c.json", '{"token": "abcdefghij1234567890"}'), ["literal secret"]),  # guard: allow test fixture
    ("json api_key mid-line refused", ("c.json", '{"a": 1, "api_key": "Zx81kQ02mN44pL97"}'), ["literal secret"]),  # guard: allow test fixture
    ("32-hex auth token refused", ("d.md", "twilio auth_token: " + "0123456789abcdef" * 2), ["literal secret"]),
    ("yaml token mid-line refused", ("c.yaml", "  porch: {url: x, token: Zx81kQ02mN44pL97Zx81}"), ["literal secret"]),  # guard: allow test fixture
    ("token variable passes", ("x.py", 'token = os.environ["HA_TOKEN"]'), []),
    ("token from a file passes", ("x.py", '           "token": open(os.environ["HA_TOKEN_FILE"]).read().strip()}'), []),
    ("aws key id refused", ("d.md", "id AKIA" + "ABCDEFGH12345678"), ["api key"]),
    ("basic auth header refused", ("x.sh", "-H 'Authorization: Basic dXNlcjpodW50ZXIyMg=='"), ["literal secret"]),  # guard: allow test fixture
    # F3: ordinary config and code that the guard refused on a real tree.
    ("esphome GPIO pin passes", ("k.yaml", "    i2s_bclk_pin: GPIO44"), []),
    ("esphome bare GPIO pin passes", ("k.yaml", "    pin: GPIO18"), []),
    ("yaml tag value passes", ("k.yaml", "      pin: !lambda 'return id(x);'"), []),
    ("python code from a call passes", ("x.py", "        code = m.group(1)"), []),
    ("python constant from a call passes", ("x.py", "TOKEN = subprocess.run(['ssh', 'box'])"), []),
    ("python name to name passes", ("x.py", "        has_pin = PIN_SUBMIT in blob"), []),
    ("json key to a name passes", ("x.py", '            "code": code,'), []),
    ("prose after Code: passes", ("d.md", "- Code: revert the PR's commit"), []),
    ("bare pin with digits refused", ("c.yaml", "  pin: 4821"), ["literal secret"]),  # guard: allow test fixture
    ("bare code quoted refused", ("x.py", 'CODE = "4821"'), ["literal secret"]),  # guard: allow test fixture
    ("commit id under a commit key passes", ("r.json", '  "repo_commit": "' + "0a1b2c3d4e" * 4 + '",'), []),
    ("commit id under an export key passes", ("r.json", '  "live_export": "' + "0a1b2c3d4e" * 4 + '",'), []),
    ("sha256 digest passes", ("r.json", '{"path": "a.html","sha256":"' + "0a1b2c3d" * 8 + '","bytes": 5}'), []),
    # KIT-SAFE.f2 (closure KIT-SAFE.fc R1): a key that only contains a commit or digest word is not masked.
    ("refresh_token 40 hex refused", ("c.yaml", "refresh_token: " + "0a1b2c3d4e" * 4), ["literal secret", "long hex"]),
    ("shared_secret 40 hex refused", ("c.yaml", 'shared_secret: "' + "0a1b2c3d4e" * 4 + '"'), ["literal secret", "long hex"]),
    ("api_key_ref 40 hex refused", ("c.yaml", 'api_key_ref: "' + "0a1b2c3d4e" * 4 + '"'), ["literal secret", "long hex"]),
    ("export_token 40 hex refused", ("c.yaml", "export_token: " + "0a1b2c3d4e" * 4), ["literal secret", "long hex"]),
    ("commit_token 40 hex refused", ("x.sh", "commit_token=" + "0a1b2c3d4e" * 4), ["literal secret", "long hex"]),
    ("hashed_password 64 hex refused", ("c.yaml", "hashed_password: " + "0a1b2c3d" * 8), ["literal secret", "long hex"]),
    ("commit_sha passes", ("r.json", '  "commit_sha": "' + "0a1b2c3d4e" * 4 + '",'), []),
    ("bare sha passes", ("r.json", '  "sha": "' + "0a1b2c3d4e" * 4 + '",'), []),
    ("git_ref passes", ("r.yaml", "  git_ref: " + "0a1b2c3d4e" * 4), []),
    ("checksum passes", ("r.json", '  "checksum": "' + "0a1b2c3d" * 8 + '",'), []),
    ("json wifi_password mid-line refused", ("c.json", '{"ssid": "home", "wifi_password": "hunter22"}'), ["literal secret"]),  # guard: allow test fixture
    ("flow map mqtt_password refused", ("c.yaml", "  mqtt: {host: x, mqtt_password: hunter22}"), ["literal secret"]),  # guard: allow test fixture
    ("password key named in prose passes", ("d.md", "Set wifi_password in secrets.yaml."), []),
    ("64 hex under another key refused", ("r.json", '  "webhook": "' + "0a1b2c3d" * 8 + '"'), ["long hex"]),
    ("url placeholder password passes", ("d.md", "icecast://source:<password>@127.0.0.1:8000/x"), []),
    ("prose after password: passes", ("d.md", "These archives hold the NUT password: they stay on the box."), []),
    ("password name as a value passes", ("x.py", '    body = {"userName": user, "password": password}})'), []),
    ("password with a digit mid-line refused", ("c.yaml", "  ups: {user: x, password: hunter22}"), ["literal secret"]),  # guard: allow test fixture
    # F5: ten bare digits need a phone word in front.
    ("datestamp passes", ("d.md", "build 2026110200 finished"), []),
    ("firmware number passes", ("r.json", '"sw_version": "9295801220",'), []),
    ("ten digits after phone refused", ("c.json", '{"phone": "5125550199"}'), ["phone"]),  # guard: allow test fixture
]
for name, (path, line), want in GUARD_CASES:
    case(f"guard: {name}", [k for _, _, k in guard.scan([(path, 1, line)])], want)
# KIT-PUBr.f.pr2: a character that prints as nothing does not hide a key; a YAML tag or anchor before a block
# indicator does not hide the value; a changed key over an old value is judged (block_values gives the key's line).
_PIN = "alarm_" + "pin: " + '"48' + '21"'  # guard: allow invented fixture value
case("guard: a PIN after a byte-order mark refused", [k for _, _, k in guard.scan([("n.yaml", 1, "\ufeff" + _PIN)])],
     ["literal secret"])
case("guard: a PIN after a zero-width space refused", [k for _, _, k in guard.scan([("n.yaml", 1, "\u200b" + _PIN)])],
     ["literal secret"])
_V = "Zq7x" + "9Wp2Lm4k"
for _props in ("! ", "!!str ", "&a ", "&a !!str ", "!<tag:yaml.org,2002:str> "):
    case(f"guard: a block value after {_props.strip()} is read with its key",
         [j for _, j, _ in guard.block_values(f"wifi_password: {_props}|\n  {_V}\n")], [f"wifi_password: {_V}"])
case("guard: a named tag stays with the block value", [j for _, j, _ in guard.block_values("api_key: !secret |\n  name\n")],
     ["api_key: !secret name"])
case("guard: !secret before a block passes", guard.scan([("n.yaml", 2, "api_key: !secret name")]), [])
case("guard: block_values gives the key's line", guard.block_values(f"a: 1\nwifi_password: |\n\n  {_V}\n"),
     [(4, f"wifi_password: {_V}", 2)])
case("guard: a tag message is read", [x[0] for x in guard.scan(
     [("tag 0123456789ab message", 1, "wifi_" + "password: " + _V)])], ["tag 0123456789ab message"])
case("guard: secrets.yaml path refused", [k for _, _, k in guard.scan([("ha/secrets.yaml", None, None)])], ["forbidden path"])
case("guard: .storage path refused", [k for _, _, k in guard.scan([("ha/.storage/auth", None, None)])], ["forbidden path"])
case("guard: package path passes", guard.scan([("ha/packages/porch.yaml", None, None)]), [])
for bad in ("home-assistant_v2.db", "home-assistant_v2.db-wal", ".git-credentials", "x/.credentials.json",
            ".claudecode/git-credentials"):
    case(f"guard: {bad} path refused", [k for _, _, k in guard.scan([(bad, None, None)])], ["forbidden path"])
guard_st = load(TEMPLATES / "guard" / "selftest.py", "guard_selftest")
case("guard: photo with GPS refused", [k for _, _, k in guard.scan([("p/a.jpg", None, None)], read=lambda p: guard_st.jpeg(True))],
     ["photo location (GPS in EXIF)"])
case("guard: photo without GPS passes", guard.scan([("p/a.jpg", None, None)], read=lambda p: guard_st.jpeg(False)), [])
case("guard: GPS in a PNG eXIf chunk refused", guard.has_gps(b"\x89PNG....eXIf" + guard_st.jpeg(True)[12:-2]), True)
case("guard: GPS in a WebP EXIF chunk refused",
     guard.has_gps(b"RIFF\x00\x00\x00\x00WEBPVP8X" + b"\x00" * 14 + b"EXIF\x00\x00\x00\x00" + guard_st.jpeg(True)[12:-2]),
     True)
case("guard: long line scanned in pieces finds a token past the cut, and fast",
     (lambda t0: ([k for _, _, k in guard.scan([("m.js", 1, "sk-" * 20000 + "z" * 60000 + " ghp_" + "A1b2C3x4" * 5)])],
                  time.time() - t0 < 5))(time.time()),
     (["api key"], True))
case("guard: damaged EXIF is no GPS", guard.has_gps(b"Exif\x00\x00II*\x00\xff\xff\xff\x7f"), False)
DENY = json.loads((TEMPLATES / "runtime" / "claude-code-settings.json").read_text())["permissions"]["deny"]
case("deny list: secrets.yaml, .storage, the database, backups and the token file are denied",
     all(any(k in d for d in DENY) for k in ("secrets.yaml", ".storage/**", "home-assistant_v2.db", "//backup/**")) and
     all(r in DENY for r in ("Read(**/ha_token*)", "Read(//**/ha_token*)", "Read(~/.config/home-assistant/**)")), True)
case("guard: range ends", (guard.range_ends("a..b"), guard.range_ends("a...b"), guard.range_ends("HEAD")),
     (("a", "b"), ("a", "b"), (None, "HEAD")))

NAMES = guard.load_names(TEMPLATES / "guard" / "names.example.txt")
case("guard: example names file loads", len(NAMES), 3)
case("guard: missing names file is off", guard.load_names(TEMPLATES / "guard" / "no-such-file.txt"), None)
NAME_CASES = [
    ("name refused", ("docs/x.md", "Ask Sample Person about it"), ["household name"]),
    ("name is case-insensitive", ("docs/x.md", "ask SAMPLE person"), ["household name"]),
    ("street refused", ("docs/x.md", "lives on Sampleton Lane"), ["household name"]),
    ("name inside a longer word passes", ("docs/x.md", "Exampleville2 is not it"), []),
    ("comment line in the file is not a name", ("docs/x.md", "# names.txt"), []),
    ("allow marker passes a name", ("docs/x.md", "Sample Person  guard: allow fictional example"), []),
    ("names file itself is not scanned", ("guard/names.txt", "Sample Person"), []),
    ("another file called names.txt is scanned", ("docs/guard/names.txt", "Sample Person"), ["household name"]),
]
for name, (path, line), want in NAME_CASES:
    case(f"guard: {name}", [k for _, _, k in guard.scan([(path, 1, line)], NAMES, "guard/names.txt")], want)
case("guard: the file --names points at is not scanned",
     guard.scan([("private/list.txt", 1, "Sample Person")], NAMES, "private/list.txt"), [])
with tempfile.TemporaryDirectory() as td:
    inline = pathlib.Path(td) / "names.txt"
    inline.write_text("Sam  # brother\n# whole line\nAvery   #nick\nApt#5\n")
    INLINE = guard.load_names(inline)
case("guard: inline comment keeps the name and drops the comment",
     [bool(INLINE[0].search("ask Sam about it")), bool(INLINE[0].search("brother")), bool(INLINE[1].search("Avery"))],
     [True, False, True])
case("guard: a # with no space before it stays in the name", [bool(INLINE[2].search("Apt#5"))], [True])
case("guard: whole-line comment is not a name", len(INLINE), 3)
case("guard: no names given, no name check", guard.scan([("docs/x.md", 1, "Sample Person")]), [])

def hook_execution_denied(repo):
    checked = subprocess.run([sys.executable, str(repo / "guard/selftest.py"), "--check-hook", "--repo",
                              str(repo), "--remote", "origin"], capture_output=True, text=True)
    try:
        result = json.loads(checked.stdout)
    except ValueError:
        return False
    return checked.returncode == 2 and result == {
        "status": "unavailable", "method": "unverified", "reason": "hook_execution_denied"}


# Ask the real checker before expecting executable-hook cases to pass.
import shutil
with tempfile.TemporaryDirectory() as td:
    probe = pathlib.Path(td)
    subprocess.run(["git", "init", "-q", str(probe)], check=True)
    subprocess.run(["git", "-C", str(probe), "remote", "add", "origin", "fixture-remote"], check=True)
    shutil.copytree(TEMPLATES / "guard", probe / "guard")
    (probe / ".git/hooks/pre-push").write_bytes(guard_st.HOOK_STUB)
    (probe / ".git/hooks/pre-push").chmod(0o755)
    restricted_hooks = hook_execution_denied(probe)
if restricted_hooks:
    print("SKIP guard: planted-secret self-test passes (this computer or sandbox will not run hook files)")
else:
    selftest = subprocess.run([sys.executable, str(TEMPLATES / "guard" / "selftest.py")], capture_output=True, text=True)
    case("guard: planted-secret self-test passes", selftest.returncode, 0)

# KIT-GUARD-FIX (from the lanewright review KAN-2cr): every pushed commit is scanned, not only the end-to-end diff;
# a bare allow marker counts for nothing; a listed file deleted at any size is a shrink finding.
case("guard: a bare allow marker counts for nothing (N1)",
     [k for _, _, k in guard.scan([("d.md", 1, "call 555-201-4477  guard: allow")])], ["phone"])  # guard: allow test fixture
case("guard: an allow marker with a reason still passes (N1)",
     guard.scan([("d.md", 1, "call 555-201-4477  # guard: allow no literal")]), [])
with tempfile.TemporaryDirectory() as td:
    gr = pathlib.Path(td)

    def _g(*a):
        return subprocess.run(["git", "-C", td, "-c", "user.name=t", "-c", "user.email=t@example.invalid", *a],
                              check=True, capture_output=True, text=True).stdout

    def _commit(path, text, msg="c"):
        f = gr / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
        _g("add", "-A")
        _g("commit", "-qm", msg)

    _g("init", "-q", "-b", "main")
    _commit("README.md", "scratch\n")
    _commit("docs/short.md", "one\ntwo\n")
    _g("tag", "base")
    _commit("ha/x.yaml", "wifi_" + "password: hunter22\n")  # guard: allow test fixture
    _commit("ha/x.yaml", "wifi_password: !secret wifi\n")
    case("guard: a secret added in one pushed commit and removed in the next is refused (F1)",
         [k for _, _, k in guard.scan(guard.changes(td, "base..HEAD"))], ["literal secret"])
    _g("rm", "-q", "docs/short.md")
    _g("commit", "-qm", "delete")
    case("guard: a listed file under 20 lines deleted is a shrink finding",
         [k for _, _, k in guard.shrink_findings(td, "base..HEAD", ["docs/short.md"])],
         ["shrink (deleted; a listed file may not be deleted)"])
    case("guard: no upstream scans every commit in the history too (F1)",
         [k for _, _, k in guard.scan(guard.changes(td, None))], ["literal secret"])
    case("guard: the same line in several commits is reported once",
         len([1 for p_, n_, l_ in guard.changes(td, "base..HEAD") if l_ and "hunter22" in l_]), 1)

# KIT-XR-GUARD (review 2026-11-11) F2 F4 on a first push (no upstream): the working tree is read as bytes, so a UTF-16
# file is decoded and a renamed photo is known by its bytes; F1 a YAML block value is joined to its key there too.
with tempfile.TemporaryDirectory() as td:
    for path, data in (("README.md", b"scratch\n"),
                       ("cfg/u16.json", ('{"pass' + 'word": "hunter22"}\n').encode("utf-16")),
                       ("media/photo.dat", guard_st.jpeg(True)),
                       ("ha/wifi.yaml", ("wifi_" + "password: |-\n  hunter22\n").encode())):
        f = pathlib.Path(td) / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    subprocess.run(["git", "-C", td, "init", "-q"], check=True)
    subprocess.run(["git", "-C", td, "add", "-A"], check=True)
    case("guard: a first push reads a UTF-16 file, a renamed photo and a YAML block from the working tree",
         sorted((p_, k) for p_, _, k in guard.scan(guard.changes(td, None), read=guard.reader(td, None))),
         [("cfg/u16.json", "literal secret"), ("ha/wifi.yaml", "literal secret"),
          ("media/photo.dat", "photo location (GPS in EXIF)")])
case("guard: decode_text reads UTF-16 without a mark and refuses bytes that are not text",
     (guard.decode_text("porch light".encode("utf-16-le")), guard.decode_text(bytes(range(256)) * 2)),
     ("porch light", None))
case("guard: an escaped JSON key is scanned as its characters",
     [k for _, _, k in guard.scan([("c.json", 1, '{"\\u0070assword": "hunter22"}')])], ["literal secret"])  # guard: allow test fixture

# KIT-GUARD-FIX2 (review-kit-guard-fix 2026-11-10): F1 a new branch scans only what no remote has, F2 a merge adds only
# what is new against every parent, F3 a photo is read as the commit that touched it left it.
with tempfile.TemporaryDirectory() as td2:
    origin, one, two = (str(pathlib.Path(td2) / n) for n in ("origin.git", "one", "two"))

    def _h(cwd, *a):
        return subprocess.run(["git", "-C", cwd, "-c", "user.name=t", "-c", "user.email=t@example.invalid", *a],
                              check=True, capture_output=True, text=True).stdout

    def _put(cwd, path, data, msg="c"):
        f = pathlib.Path(cwd) / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data) if isinstance(data, bytes) else f.write_text(data)
        _h(cwd, "add", "-A")
        _h(cwd, "commit", "-qm", msg)

    def _kinds(cwd, rng="auto"):
        r = guard.resolve_range(cwd, None) if rng == "auto" else rng
        return [k for _, _, k in guard.scan(guard.changes(cwd, r), read=guard.reader(cwd, r))]

    old = "wifi_" + "password: hunter22\n"  # guard: allow test fixture
    _h(td2, "init", "-q", "--bare", "-b", "main", origin)
    _h(td2, "init", "-q", "-b", "main", one)
    _h(one, "remote", "add", "origin", origin)
    _put(one, "README.md", "scratch\n")
    _put(one, "ha/x.yaml", old)
    _put(one, "ha/x.yaml", "wifi_password: !secret wifi\n")
    _h(one, "push", "-q", "-u", "origin", "main")
    _h(one, "checkout", "-q", "-b", "topic")
    _put(one, "docs/a.md", "a harmless line\n")
    case("guard: a new branch is not refused for old lines its remote already has (KIT-GUARD-FIX2 F1)",
         (guard.resolve_range(one, None), _kinds(one)), (guard.NOT_ON_A_REMOTE, []))
    _put(one, "ha/y.yaml", "api_" + "key: abcdefgh12345678\n")
    _put(one, "ha/y.yaml", "api_key: !secret api\n")
    case("guard: a new branch still refuses a secret its own commits added and removed (F1)",
         _kinds(one), ["literal secret"])
    case("guard: with no remote-tracking branch every line is reported once across tree and history (F1)",
         len([1 for p_, n_, l_ in guard.changes(one, None) if l_ == "a harmless line"]), 1)

    _h(td2, "clone", "-q", origin, two)
    _put(two, "ha/z.yaml", "wifi_" + "password: other22\n", "from another machine")  # guard: allow test fixture
    _h(two, "push", "-q", "origin", "main")
    _h(one, "checkout", "-q", "main")
    _put(one, "docs/b.md", "mine\n")
    _h(one, "pull", "-q", "--no-rebase", "--no-edit", "origin", "main")
    case("guard: a pull that merges is not refused for lines already upstream (F2)",
         _kinds(one, "@{u}..HEAD"), [])
    _put(one, "ha/w.yaml", "wifi_" + "password: mine22\n")  # guard: allow test fixture
    case("guard: a line the pusher adds after the merge is still refused (F2)",
         _kinds(one, "@{u}..HEAD"), ["literal secret"])
    _h(one, "reset", "-q", "--hard", "HEAD~1")
    _h(one, "push", "-q", "origin", "main")

    _put(one, "p/a.jpg", guard_st.jpeg(True), "photo")
    _put(one, "p/a.jpg", guard_st.jpeg(False), "stripped")
    case("guard: a photo with its location, stripped in the next commit, is still refused (F3)",
         _kinds(one, "@{u}..HEAD"), ["photo location (GPS in EXIF)"])

    # KIT-GUARD-FIX3 (1): an added line starting `++ ` is not a file header; the lines after it are still scanned,
    # under their own file's name.
    _put(one, "docs/c.md", "++ a line\n++ b/decoy.md\nwifi_" + "password: hunter33\n", "plus lines")  # guard: allow test fixture
    _r = "HEAD~1..HEAD"
    case("guard: a line starting ++ does not hide the rest of its file (KIT-GUARD-FIX3)",
         [(p_, k) for p_, _, k in guard.scan(guard.changes(one, _r))], [("docs/c.md", "literal secret")])
    _h(one, "reset", "-q", "--hard", "HEAD~1")

    # KIT-GUARD-FIX3 (2): only the remote being pushed to counts. A flagged commit pushed to remote B only, then a
    # new branch on top for remote A: the flagged commit is still new to A.
    other = str(pathlib.Path(td2) / "other.git")
    _h(td2, "init", "-q", "--bare", "-b", "main", other)
    _h(one, "remote", "add", "b", other)
    _h(one, "checkout", "-q", "-b", "side")
    _put(one, "ha/v.yaml", "wifi_" + "password: onb44\n", "only on b")  # guard: allow test fixture
    _h(one, "push", "-q", "-u", "b", "side")
    _h(one, "checkout", "-q", "-b", "feature")
    _put(one, "docs/d.md", "harmless\n")
    _kr = lambda remote: [k for _, _, k in guard.scan(guard.changes(one, guard.resolve_range(one, None, remote)))]
    case("guard: a commit only another remote holds is scanned on its way to this one (KIT-GUARD-FIX3)",
         (guard.resolve_range(one, None, "origin"), _kr("origin")), (guard.NOT_ON_A_REMOTE + "=origin", ["literal secret"]))
    case("guard: with no remote named the old rule holds (any remote counts)", _kr(None), [])
    case("guard: pushing to the remote that holds it is clean", _kr("b"), [])
    _h(one, "branch", "-q", "--set-upstream-to", "b/side")
    case("guard: an upstream on another remote does not count for this one (KIT-GUARD-FIX3)",
         (guard.resolve_range(one, None, "origin"), _kr("origin")), (guard.NOT_ON_A_REMOTE + "=origin", ["literal secret"]))
    case("guard: an upstream on the remote being pushed to is used", guard.resolve_range(one, None, "b"), "@{u}..HEAD")
    case("guard: a remote with no branch yet scans the whole history",
         "literal secret" in _kr("https://example.invalid/new.git"), True)

    # KIT-GUARD-FIX4 N3: git quotes a name with a non-ASCII letter, a double quote, a backslash or a control character
    # (`+++ "b/caf\303\251.md"`) and puts a tab after one with a space; each is still read, under its real name.
    _pw = "wifi_" + "password: hunter55\n"  # guard: allow test fixture
    for _name in ("docs/caf\u00e9.md", 'docs/say "hi".md', "docs/back\\slash.md", "docs/two words.md",
                  'docs/a "quoted" name.md', "docs/tab\there.md"):
        _put(one, _name, _pw, "odd name")
        case(f"guard: a secret in a file named {_name!r} is refused under that name (KIT-GUARD-FIX4)",
             [(p_, k) for p_, _, k in guard.scan(guard.changes(one, "HEAD~1..HEAD"))], [(_name, "literal secret")])
    _put(one, "caf\u00e9/secrets.yaml", "x: 1\n", "odd folder")
    case("guard: a forbidden path under an accented folder is refused (KIT-GUARD-FIX4)",
         [(p_, k) for p_, _, k in guard.scan(guard.changes(one, "HEAD~1..HEAD"))],
         [("caf\u00e9/secrets.yaml", "forbidden path")])
    _put(one, "f\u00f6tos/a.jpg", guard_st.jpeg(True), "odd photo")
    case("guard: a photo with its location under an accented folder is refused (KIT-GUARD-FIX4)",
         _kinds(one, "HEAD~1..HEAD"), ["photo location (GPS in EXIF)"])
    _h(one, "reset", "-q", "--hard", "HEAD~8")

    # KIT-GUARD-FIX4 N2: a destination with a space (the hook's $1 is a path or URL when the remote has no name) is one
    # argument: the whole history is read, not "ambiguous argument".
    _sp = str(pathlib.Path(td2) / "with space.git")
    _h(td2, "init", "-q", "--bare", "-b", "main", _sp)
    case("guard: a remote path with a space reads the whole history (KIT-GUARD-FIX4)",
         (guard.resolve_range(one, None, _sp), "literal secret" in _kr(_sp)), (guard.NOT_ON_A_REMOTE + "=" + _sp, True))
    _h(one, "checkout", "-q", "main")
    _clean = str(pathlib.Path(td2) / "clean repo")
    _h(td2, "init", "-q", "-b", "main", _clean)
    _put(_clean, "README.md", "scratch\n")
    _r = guard.resolve_range(_clean, None, _sp)
    case("guard: a clean history pushed to a remote path with a space passes (KIT-GUARD-FIX4)",
         [k for _, _, k in guard.scan(guard.changes(_clean, _r), read=guard.reader(_clean, _r))], [])
    case("guard: the whole guard on a remote path with a space exits 0 on a clean repo (KIT-GUARD-FIX4)",
         guard.main(["--repo", _clean, "--remote", _sp, "--names", "/nonexistent", "--shrink", "/nonexistent"]), 0)


# ---------------------------------------------------------------- live export
exp = load(TEMPLATES / "export" / "export_house.py", "export_house")


class _S:
    def __init__(self, entity_id):
        self.entity_id = entity_id


REG = {"light.kitchen_ceiling": ("kitchen", "ground", "dev1", ["downstairs"], "zha"),
       "automation.porch_on": (None, None, None, [], None)}
reg_out = json.loads(env_for({}, "2026-01-15T12:00:00+00:00").from_string(exp.REGISTRY_TEMPLATE).render(
    states=[_S(e) for e in REG],
    area_id=lambda e: REG.get(e, (None,))[0], floor_id=lambda x: "ground" if x in ("kitchen",) or REG.get(x, [0, 0])[1]
    else None, device_id=lambda e: REG[e][2], labels=lambda e: REG[e][3],
    config_entry_id=lambda e: "E" + e if REG[e][4] else None, config_entry_attr=lambda i, a: REG[i[1:]][4],
    device_attr=lambda d, a: "Kitchen ceiling" if a == "name" else None, areas=lambda: ["kitchen"],
    area_name=lambda a: "Kitchen", area_entities=lambda a: ["light.kitchen_ceiling"]))
case("export: the registry template renders to entities + areas",
     (reg_out["entities"][0]["integration"], reg_out["entities"][0]["device_name"], reg_out["entities"][1]["area"],
      reg_out["areas"]), ("zha", "Kitchen ceiling", None,
                          [{"area": "kitchen", "name": "Kitchen", "floor": "ground", "entities": 1}]))


def fake_fetch(method, path, body=None):
    return {
        ("GET", "/api/config"): {"version": "2026.1.0", "time_zone": "UTC", "unit_system": {"temperature": "°F"}},
        ("GET", "/api/states"): [
            {"entity_id": "light.kitchen_ceiling", "state": "on",
             "attributes": {"friendly_name": "Kitchen ceiling", "brightness": 200}},
            {"entity_id": "automation.porch_on", "state": "off",
             "attributes": {"friendly_name": "Lighting - Porch On", "id": "1700000000001"}}],
        ("GET", "/api/config/config_entries/entry"): [
            {"entry_id": "E1", "domain": "zha", "title": "Zigbee", "state": "loaded", "disabled_by": None,
             "pref_disable_polling": False}],
        ("POST", "/api/template"): json.dumps(reg_out),
    }[(method, path)]


files = exp.build(fake_fetch, now=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc))
case("export: writes the five files", sorted(files), ["areas.json", "automations.json", "entities.json",
                                                      "integrations.json", "meta.json"])
case("export: entities carry registry links, never live state",
     files["entities.json"][1], {"entity_id": "light.kitchen_ceiling", "domain": "light", "name": "Kitchen ceiling",
                                 "area": "kitchen", "floor": "ground", "device": "dev1",
                                 "device_name": "Kitchen ceiling", "labels": ["downstairs"], "integration": "zha"})
case("export: an automation switched off shows as disabled",
     files["automations.json"], [{"entity_id": "automation.porch_on", "id": "1700000000001",
                                  "name": "Lighting - Porch On", "enabled": False}])
case("export: integrations keep only the safe fields", files["integrations.json"],
     [{"entry_id": "E1", "domain": "zha", "title": "Zigbee", "state": "loaded", "disabled": False}])
# KIT-DRY.f3f: an inherited token alone cannot bypass the owner-confirmed profile.
with tempfile.TemporaryDirectory() as missing_root:
    try:
        exp.main(["--root", missing_root, "--url", "http://example.invalid:8123"])
        case("export: refuses an unconfirmed target before credential lookup", "ran", "refused")
    except SystemExit as e:
        case("export: refuses an unconfirmed target before credential lookup",
             str(e), "export: confirmed profile and private credential required; see install/agent-access.md")



# ---------------------------------------------------------------- runtime probe (KIT-RT0s)
import contextlib  # noqa: E402
import io  # noqa: E402
import tempfile  # noqa: E402

rt = load(TEMPLATES / "runtime" / "probe_runtime.py", "probe_runtime")

case("runtime: yes/no read as booleans or strings",
     [rt.norm(v) for v in (True, False, "yes", "No", "TRUE", "false", "unknown", "", "maybe")],
     ["yes", "no", "yes", "no", "yes", "no", "unknown", "unknown", None])
case("runtime: the template reads, its FILL entry is the only one",
     list(rt.parse_record((TEMPLATES / "runtime" / "runtime.yaml").read_text())), ["FILL-runtime-name"])
for bad, why in (("runtimes:\n  a:\n    can:\n      - shell\n", "block list"),
                 ("runtimes:\n  a: &x\n    variant: v\n", "anchor"),
                 ("runtimes:\n  a:\n    variant: v\n    variant: w\n", "duplicate key"),
                 ("other: 1\n", "top level not runtimes")):
    try:
        rt.parse_record(bad)
        case(f"runtime: refuses a record with a {why}", "parsed", "RecordError")
    except rt.RecordError:
        case(f"runtime: refuses a record with a {why}", "RecordError", "RecordError")
try:  # KIT-RT0sr M1: a nested mapping a rewrite would drop is refused, not read
    rt.parse_record("runtimes:\n  a:\n    variant: v\n    notes:\n      owner: a person\n")
    case("runtime: refuses a hand-added nested mapping in an entry", "parsed", "RecordError")
except rt.RecordError as e:
    case("runtime: refuses a hand-added nested mapping in an entry", ("RecordError", "notes" in str(e)),
         ("RecordError", True))
garble = rt.parse_record("runtimes:\n  a:\n    variant:\n    owner: Dad's laptop  # the gray one\n"
                         "    can:\n      shell: yes\n")["a"]
case("runtime: an empty value is empty text, not a mapping (L3a)", garble["variant"], "")
case("runtime: a quote mid-word is plain text, the comment still drops (L3b)", garble["owner"], "Dad's laptop")
case("runtime: an empty can stays a mapping",
     rt.parse_record("runtimes:\n  a:\n    can:\n    variant: v\n")["a"]["can"], {})

ALL_YES = {k: "yes" for k in rt.PROBED}
e1, ch1 = rt.merge(None, ALL_YES, {"schedule": "yes"}, "cloud", {"builder": "model-b"}, "2026-01-10")
case("runtime: a new entry is a change dated today", (ch1, e1["detected_on"]), (True, "2026-01-10"))
case("runtime: fallbacks are every key not yes",
     e1["fallbacks_in_use"], ["subagents", "long_context", "persistent_memory", "notify_owner"])
case("runtime: a role mapping is kept, the rest stay FILL",
     e1["model_roles"], {"planner": "FILL", "builder": "model-b", "reviewer": "FILL", "mechanical": "FILL",
                         "writer": "FILL"})
round_trip = rt.parse_record(rt.dump_record({"claude-cloud": e1}))["claude-cloud"]
e2, ch2 = rt.merge(round_trip, ALL_YES, {}, None, {}, "2026-01-15")
case("runtime: same values under 7 days old is no change, date kept", (ch2, e2["detected_on"]), (False, "2026-01-10"))
case("runtime: an untold key keeps the entry's value", e2["can"]["schedule"], "yes")
e3, ch3 = rt.merge(round_trip, ALL_YES, {}, None, {}, "2026-01-17")
case("runtime: same values 7 days old is refreshed", (ch3, e3["detected_on"]), (True, "2026-01-17"))
e4, ch4 = rt.merge(round_trip, dict(ALL_YES, git_push="no"), {}, None, {}, "2026-01-11")
case("runtime: a changed probe is a change", (ch4, e4["detected_on"], "git_push" in e4["fallbacks_in_use"]),
     (True, "2026-01-11", True))
booled = rt.parse_record("runtimes:\n  claude-code:\n    detected_on: 2026-01-10\n    can:\n      shell: true\n"
                         "      web: false\n")["claude-code"]
case("runtime: YAML booleans in the record read as yes/no",
     [rt.merge(booled, {}, {}, None, {}, "2026-01-11")[0]["can"][k] for k in ("shell", "web")], ["yes", "no"])
odd = rt.dump_record({"claude-app": dict(e1, variant="yes", model_roles={"planner": "on", "writer": "a: b"})})
case("runtime: text that YAML would read as a boolean is quoted",
     (yaml.safe_load(odd)["runtimes"]["claude-app"]["variant"],
      yaml.safe_load(odd)["runtimes"]["claude-app"]["model_roles"]["planner"],
      yaml.safe_load(odd)["runtimes"]["claude-app"]["model_roles"]["writer"]), ("yes", "on", "a: b"))
typed = ["- dash", "? key", "123", "1e3", "null", "~", "+1", ".5", "2026-01-10"]
back = yaml.safe_load(rt.dump_record({"x": dict(e1, variant="- dash", model_roles=dict(zip(rt.ROLES, typed[1:6])),
                                               note=typed[6], other=typed[7], when=typed[8])}))["runtimes"]["x"]
case("runtime: values YAML would type or refuse are quoted (L4)",
     [back["variant"]] + [back["model_roles"][r] for r in rt.ROLES] + [back["note"], back["other"], back["when"]],
     typed)
case("runtime: PyYAML reads what the script writes the same way",
     {k: ("yes" if v is True else "no" if v is False else v)
      for k, v in yaml.safe_load(rt.dump_record({"x": e1}))["runtimes"]["x"]["can"].items()}, e1["can"])


def rt_main(args, probes):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            rc = rt.main(args, probes=probes)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue()


def fake(**over):
    vals = dict(ALL_YES, **over)
    return {k: (lambda v=v: (v, "fake")) for k, v in vals.items()}


with tempfile.TemporaryDirectory() as td:
    rec = pathlib.Path(td) / "house" / "runtime.yaml"
    base = ["--runtime", "claude-code", "--root", td, "--today", "2026-01-10"]
    rc, out = rt_main(base + ["--set", "subagents=yes"], fake())
    case("runtime main: first run writes the entry", (rc, rec.exists(), "written" in out), (0, True, True))
    first = rec.read_text()
    rc, out = rt_main(base[:-1] + ["2026-01-12"], fake())
    case("runtime main: an unchanged re-run leaves the file alone", (rc, rec.read_text() == first, "unchanged" in out),
         (0, True, True))
    rc, out = rt_main(base[:-1] + ["2026-01-12", "--runtime", "claude-cloud"], fake(git_push="no"))
    case("runtime main: a second runtime is a new entry, the first kept",
         list(yaml.safe_load(rec.read_text())["runtimes"]), ["claude-code", "claude-cloud"])
    case("runtime main: the one-line report names the fallbacks",
         out.strip().splitlines()[-3].startswith("claude-cloud: shell yes") and "git_push" in out.splitlines()[-3],
         True)
    before = rec.read_text()
    rc, out = rt_main(base[:-1] + ["2026-01-13"], fake(write_files="no", web="no"))
    case("runtime main: without write_files the entry is printed, not written",
         (rc, rec.read_text() == before, "save this entry" in out), (0, True, True))
    rc, out = rt_main(base[:-1] + ["2026-01-13", "--dry-run"], fake(web="no"))
    case("runtime main: --dry-run writes nothing", (rc, rec.read_text() == before, "would be" in out),
         (0, True, True))
    rc, out = rt_main(base + ["--if-stale"], {k: (lambda: 1 / 0) for k in rt.PROBED})
    case("runtime main: --if-stale on a fresh entry probes nothing", (rc, "nothing probed" in out), (0, True))
    rc, out = rt_main(base + ["--set", "git_push=yes"], fake())
    case("runtime main: a probed key is never taken on trust", rc, 2)
    rc, out = rt_main(["--runtime", "chatgpt-agent", "--root", td], fake())
    case("runtime main: an unknown runtime name is refused", rc, 2)
    rc, out = rt_main(base[:-1] + ["2026-01-12", "--no-web"], fake(web="no"))
    case("runtime main: --no-web keeps the entry's web value and forces no rewrite (L1)",
         (rc, "unchanged" in out, yaml.safe_load(rec.read_text())["runtimes"]["claude-code"]["can"]["web"]),
         (0, True, True))
    rc, out = rt_main(base[:-1] + ["2026-01-12", "--place", "box"], fake(box_access="yes"))
    rc2, out2 = rt_main(base[:-1] + ["2026-01-12", "--place", "laptop"], fake(box_access="no"))
    boxed = rec.read_text()
    case("runtime main: two places leave two entries (M2)",
         [k for k in yaml.safe_load(boxed)["runtimes"] if "/" in k], ["claude-code/box", "claude-code/laptop"])
    rc, out = rt_main(base[:-1] + ["2026-01-13", "--place", "box"], fake(box_access="yes"))
    case("runtime main: a run for one place leaves the other untouched",
         (rc, rec.read_text() == boxed, out.strip().splitlines()[-3].startswith("claude-code/box: ")), (0, True, True))
    rc, out = rt_main(base + ["--place", "my box"], fake())
    case("runtime main: a --place with a space is refused", rc, 2)
    os.chmod(rec, 0o640)
    rt_main(base[:-1] + ["2026-01-14"], fake(git_push="no"))
    case("runtime main: a rewrite keeps the file's mode (L5)", oct(rec.stat().st_mode & 0o777), oct(0o640))
    real_replace = pathlib.Path.replace
    pathlib.Path.replace = lambda self, target: (_ for _ in ()).throw(PermissionError("ro"))
    try:
        rc, out = rt_main(base[:-1] + ["2026-01-15"], fake(git_push="no", shell="no"))
    finally:
        pathlib.Path.replace = real_replace
    case("runtime main: a failed replace leaves no .tmp behind (L5)",
         (rc, "not written" in out, (rec.parent / "runtime.yaml.tmp").exists()), (0, True, False))
    rec.write_text("runtimes:\n  claude-code:\n    can:\n      - shell\n")
    rc, out = rt_main(base, fake())
    case("runtime main: refuses to overwrite a record it cannot read",
         (rc, rec.read_text().endswith("- shell\n")), (2, True))


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *a], cwd=cwd,
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as td:
    origin, work = pathlib.Path(td) / "origin.git", pathlib.Path(td) / "work"
    git(td, "init", "-q", "--bare", str(origin))
    git(td, "init", "-q", str(work))
    case("runtime git: no origin remote is no", rt.probe_git(work)[0], "no")
    git(work, "remote", "add", "origin", str(origin))
    (work / "a.txt").write_text("a\n")
    git(work, "add", "a.txt")
    git(work, "commit", "-qm", "a")
    case("runtime git: a branch with no upstream is yes (KIT-RT0r M3a)", rt.probe_git(work)[0], "yes")
    git(work, "push", "-q", "origin", "HEAD")
    case("runtime git: an up-to-date branch is yes (M3c)", rt.probe_git(work)[0], "yes")
    hook = work / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    case("runtime git: a refusing pre-push hook does not turn it no (M3b)", rt.probe_git(work)[0], "yes")
    case("runtime git: the dry run pushed nothing", git(origin, "rev-list", "--all", "--count").stdout.strip(), "1")
    other = pathlib.Path(td) / "other"
    git(td, "clone", "-q", str(origin), str(other))
    (other / "b.txt").write_text("b\n")
    git(other, "add", "b.txt")
    git(other, "commit", "-qm", "b")
    git(other, "push", "-q", "origin", "HEAD")
    case("runtime git: a branch behind origin is yes, with the reason (L2)", rt.probe_git(work),
         ("yes", "dry run reached the remote; branch behind origin (fetch before pushing)"))
    git(work, "checkout", "-q", "--detach")
    case("runtime git: detached HEAD is no", rt.probe_git(work), ("no", "detached HEAD"))


# ---------------------------------------------------------------- step one everywhere (KIT-STEP0)
on_disk = lambda *paths: (lambda p: p in paths)  # noqa: E731
case("step0 where: an app on the box (the Supervisor's token)",
     rt.detect_where({"SUPERVISOR_TOKEN": "t"}, on_disk())[0], "box")
case("step0 where: a shell on the box (/share beside the config folder)",
     rt.detect_where({}, on_disk("/share", "/homeassistant/configuration.yaml"))[0], "box")
case("step0 where: /share alone is not the box", rt.detect_where({}, on_disk("/share"))[0], "computer")
case("step0 where: a cloud runtime is cloud", rt.detect_where({}, on_disk(), runtime="claude-cloud")[0], "cloud")
case("step0 where: a cloud session's marker is cloud",
     rt.detect_where({"CLAUDE_CODE_REMOTE": "true"}, on_disk())[0], "cloud")
case("step0 where: the box wins over a cloud marker",
     rt.detect_where({"SUPERVISOR_TOKEN": "t", "CLAUDE_CODE_REMOTE": "true"}, on_disk(), "claude-cloud")[0], "box")
case("step0 where: anything else with a shell is a computer, and says no marker was found (F3)",
     (rt.detect_where({}, on_disk())[0], "no cloud marker found" in rt.detect_where({}, on_disk())[1],
      "--where cloud" in rt.detect_where({}, on_disk())[1]), ("computer", True, True))
case("step0 github: the remote's kind, never its address",
     [rt._remote_kind(u) for u in ("https://x-access-token:abc@github.com/someone/house.git",
                                   "git@github.com:someone/house.git", "ssh://git@ssh.github.com:443/a/b",
                                   "https://git.example.invalid/a/b.git", "/srv/git/house.git")],
     ["GitHub", "GitHub", "GitHub", "a git server (not GitHub)", "a git server (not GitHub)"])
case("step0 github: push, read-only, no-reach, none",
     [rt.github_state(r, p) for r, p in (("reach", "yes"), ("reach", "no"), ("reach", "unknown"),
                                         ("no-reach", "yes"), ("none", "no"))],
     ["push", "read-only", "read-only", "no-reach", "none"])

with tempfile.TemporaryDirectory() as td:
    case("step0 github: no git installed is none",
         rt.probe_github(pathlib.Path(td), {}, which=lambda n: None)[::2], ("none", "git is not installed"))
    case("step0 github: a folder that is not a repository is none", rt.probe_github(pathlib.Path(td), {})[0], "none")
    origin, work = pathlib.Path(td) / "origin.git", pathlib.Path(td) / "work"
    git(td, "init", "-q", "--bare", str(origin))
    git(td, "init", "-q", str(work))
    case("step0 github: a repository with no origin is none", rt.probe_github(work, {})[::2],
         ("none", "a repository with no origin remote"))
    git(work, "remote", "add", "origin", str(origin))
    no_gh = lambda n: shutil.which(n) if n == "git" else None  # noqa: E731 - no gh on this fake machine
    state, kind, ev = rt.probe_github(work, {"GH_TOKEN": "tok-SECRET-123"}, which=no_gh)
    case("step0 github: an empty remote that answers is reached (exit 2)", (state, kind), (
         "reach", "a git server (not GitHub)"))
    case("step0 github: a credential is named by kind, never by value",
         ("GH_TOKEN" in ev, "SECRET" in ev, str(origin) in ev), (True, False, False))
    (work / "a.txt").write_text("a\n")
    git(work, "add", "a.txt")
    git(work, "commit", "-qm", "a")
    git(work, "push", "-q", "origin", "HEAD")
    case("step0 github: a remote with a branch is reached", rt.probe_github(work, {}, which=no_gh)[0], "reach")
    git(work, "remote", "set-url", "origin", str(pathlib.Path(td) / "gone.git"))
    state, kind, ev = rt.probe_github(work, {}, which=no_gh)
    case("step0 github: a remote that does not answer is no-reach, with no address",
         (state, "did not answer" in ev, "gone.git" in ev), ("no-reach", True, False))

lines = {}
for where in rt.WHERE:
    for gh in rt.GITHUB:
        for box in ("yes", "unknown"):
            lines[where, gh, box] = rt.owner_lines({"where": where, "github": gh, "can": {"box_access": box}})
case("step0 owner: always two lines, plain, naming no address or token",
     {len(v) == 2 and all("http" not in x and "token" not in x.lower() and len(x) < 230 for x in v)
      for v in lines.values()}, {True})
case("step0 owner: on the box it skips the install steps and reads the box",
     "skip the install steps" in lines["box", "push", "yes"][0] and "agent-access.md" in lines["box", "push", "unknown"][0],
     True)
case("step0 owner: a cloud session changes nothing on the box and hands the steps over",
     ("change nothing on the box" in lines["cloud", "push", "unknown"][0], "hand you the steps" in lines["cloud", "none", "yes"][0]),
     (True, True))
case("step0 owner: a computer says whether it reads the box",
     ("can read your box" in lines["computer", "push", "yes"][0], "cannot read your box" in lines["computer", "push", "unknown"][0]),
     (True, True))
case("step0 owner: no GitHub on the box keeps the house folder local and in the backups, GitHub optional",
     ["local and in the box's backups" in lines["box", g, "yes"][1] and "optional" in lines["box", g, "yes"][1]
      for g in ("none", "no-reach")], [True, True])
case("step0 owner: the box's backups are named only on the box (F2)",
     sorted({k[0] for k, v in lines.items() if "box's backups" in v[1]}), ["box"])
case("step0 owner: on a computer the folder is on this computer only (F2)",
     ["on this computer only" in lines["computer", g, "yes"][1] for g in ("read-only", "no-reach", "none")],
     [True, True, True])
case("step0 owner: a cloud session that cannot push says nothing outlives it and hands the files over (F2)",
     ["outlives this session" in lines["cloud", g, "yes"][1] and "files or the diff" in lines["cloud", g, "yes"][1]
      for g in ("read-only", "no-reach", "none")], [True, True, True])
case("step0 owner: a cloud session that can push pushes before it ends (F2)",
     "before this session ends" in lines["cloud", "push", "yes"][1], True)
case("step0 owner: read-only hands the push over, push keeps it on GitHub",
     ("hand you" in lines["computer", "read-only", "yes"][1], "push to it" in lines["computer", "push", "yes"][1]),
     (True, True))
case("step0 owner: a cloud session with a way into the box still changes nothing on it (N4)",
     ("no way into your box" in lines["cloud", "push", "yes"][0], "change nothing on it" in lines["cloud", "push", "yes"][0],
      "no way into your box" in lines["cloud", "push", "unknown"][0]), (False, True, True))
case("step0 owner: a value the entry does not hold is left out, never defaulted (F1)",
     (rt.owner_lines({"can": {"box_access": "unknown"}}), len(rt.owner_lines({"where": "box", "can": {}}))), ((), 1))

with tempfile.TemporaryDirectory() as td:
    rec = pathlib.Path(td) / "house" / "runtime.yaml"
    base = ["--runtime", "claude-code", "--root", td, "--today", "2026-01-10"]
    place = lambda w, g: {"where": lambda: (w, "fake"), "github": lambda: (g, "GitHub", "fake")}  # noqa: E731
    rc, out = rt_main(base, dict(fake(), **place("box", "reach")))
    got = yaml.safe_load(rec.read_text())["runtimes"]["claude-code"]
    case("step0 main: where and github are recorded beside can",
         (rc, got["where"], got["github"]), (0, "box", "push"))
    case("step0 main: the report ends with the owner's two lines",
         out.strip().splitlines()[-2:], list(rt.owner_lines(dict(got, can={"box_access": "yes"}), "GitHub")))
    first = rec.read_text()
    rc, out = rt_main(base[:-1] + ["2026-01-12"], dict(fake(), **place("box", "reach")))
    case("step0 main: the same place again is no rewrite", (rc, rec.read_text() == first), (0, True))
    rc, out = rt_main(base[:-1] + ["2026-01-12"], dict(fake(git_push="no"), **place("box", "reach")))
    case("step0 main: a push that stops working turns github read-only",
         yaml.safe_load(rec.read_text())["runtimes"]["claude-code"]["github"], "read-only")
    rc, out = rt_main(base[:-1] + ["2026-01-12", "--where", "computer"], dict(fake(), **place("box", "none")))
    got = yaml.safe_load(rec.read_text())["runtimes"]["claude-code"]
    case("step0 main: --where overrides the evidence and says so",
         (got["where"], got["github"], "told (--where)" in out), ("computer", "none", True))
    rc, out = rt_main(base + ["--where", "chat"], fake())
    case("step0 main: a chat is not a --where (no shell, nothing recorded)", rc, 2)
    rc, out = rt_main(base[:-1] + ["2026-01-13", "--if-stale"], {k: (lambda: 1 / 0) for k in rt.PROBED})
    case("step0 main: --if-stale still tells the owner the two lines",
         out.strip().splitlines()[-2].startswith("I am running on a computer"), True)
    rec.write_text("runtimes:\n  claude-code:\n    detected_on: 2026-01-12\n    can:\n      shell: yes\n")
    rc, out = rt_main(base[:-1] + ["2026-01-13", "--if-stale"], dict(fake(), **place("cloud", "reach")))
    got = yaml.safe_load(rec.read_text())["runtimes"]["claude-code"]
    case("step0 main: --if-stale probes an entry with no where or github, never reads it as a computer (F1)",
         ("nothing probed" in out, "on a computer" in out, "not connected" in out, got["where"], got["github"]),
         (False, False, False, "cloud", "push"))
    git(td, "init", "-q")
    git(td, "remote", "add", "origin", "https://git.example.invalid/someone/house.git")
    rc, out = rt_main(base[:-1] + ["2026-01-14", "--if-stale"], {k: (lambda: 1 / 0) for k in rt.PROBED})
    case("step0 main: --if-stale names the remote's kind, not GitHub, for another git server (F1)",
         ("nothing probed" in out, out.strip().splitlines()[-1].startswith("a git server (not GitHub):"),
          "example.invalid" in out), (True, True, False))
    rec.write_text("runtimes:\n  claude-code:\n    detected_on: 2026-01-10\n    owner: Dad\n    can:\n      shell: yes\n")
    rt_main(base[:-1] + ["2026-01-11"], dict(fake(), **place("cloud", "none")))
    got = yaml.safe_load(rec.read_text())["runtimes"]["claude-code"]
    case("step0 main: an entry from before KIT-STEP0 gains where and github, its own keys kept",
         (got["where"], got["github"], got["owner"]), ("cloud", "none", "Dad"))


def box_fetch(answers):
    def f(url, headers):
        a = answers[url.rsplit("/api", 1)[1]]
        if isinstance(a, Exception):
            raise a
        return a
    return f


ENV = {"HA_URL": "http://box.example.invalid:8123", "HA_TOKEN": "t0k"}  # guard: allow test fixture

def bound_box(env, fetch):
    reader = rt._read_tool("ha_read")
    url = reader.selected_url(env)
    pinned = {"setup": {"agent_access": {"box_url_sha256": reader.fingerprint_url(url)}}}
    return rt.probe_box(env, fetch, profile=pinned)

case("runtime box: no token is no", bound_box({"HA_URL": ENV["HA_URL"]}, box_fetch({}))[0], "no")
case("runtime box: 401 is no", bound_box(ENV, box_fetch({"/": (401, "")})), ("no", "/api/ returned 401"))
case("runtime box: 200 and a count is yes, count only",
     bound_box(ENV, box_fetch({"/": (200, json.dumps({"message": "API running."})), "/states": (200, json.dumps([{}, {}, {}]))})),
     ("yes", "200, 3 entities, via HA_URL"))
# KIT-BASE: inside an add-on there is no HA_URL; the Supervisor's token and its Core proxy are the way in
sup_calls = []
def sup_fetch(url, headers):
    sup_calls.append((url, headers.get("Authorization")))
    return (200, json.dumps([{}, {}])) if url.endswith("/states") else (200, json.dumps({"message": "API running."}))
case("runtime box: SUPERVISOR_TOKEN alone is yes through the Supervisor proxy",
     bound_box({"SUPERVISOR_TOKEN": "sup-t0k"}, sup_fetch), ("yes", "200, 2 entities, via the Supervisor (inside an add-on)"))  # guard: allow test fixture
case("runtime box: the Supervisor path uses its proxy URL and token",
     sup_calls[1], (rt.SUPERVISOR_CORE + "/api/", "Bearer sup-t0k"))  # guard: allow test fixture
case("runtime box: HA_URL wins over SUPERVISOR_TOKEN when both are set",
     bound_box(dict(ENV, SUPERVISOR_TOKEN="sup-t0k"), box_fetch({"/": (200, json.dumps({"message": "API running."})), "/states": (200, "[]")}))[1],  # guard: allow test fixture
     "200, 0 entities, via HA_URL")
# KIT-BASEr M1: the add-on exports HA_URL=http://supervisor/core and HA_TOKEN=$SUPERVISOR_TOKEN itself, so inside it
# both are set; the path is named by where it goes, so the section 0 tell still fires
addon_calls = []
def addon_fetch(url, headers):
    addon_calls.append((url, headers.get("Authorization")))
    return (200, json.dumps([{}])) if url.endswith("/states") else (200, json.dumps({"message": "API running."}))
case("runtime box: HA_URL at the Supervisor proxy (the add-on's own export) is the Supervisor path",
     bound_box({"HA_URL": rt.SUPERVISOR_CORE + "/", "HA_TOKEN": "sup-t0k", "SUPERVISOR_TOKEN": "sup-t0k"}, addon_fetch),  # guard: allow test fixture
     ("yes", "200, 1 entities, via the Supervisor (inside an add-on)"))
case("runtime box: that path uses the proxy URL once, with HA_TOKEN",
     addon_calls[1], (rt.SUPERVISOR_CORE + "/api/", "Bearer sup-t0k"))  # guard: allow test fixture
leak = bound_box(ENV, box_fetch({"/": OSError("cannot reach http://box.example.invalid:8123 with t0k")}))
case("runtime box: an error never echoes the URL or token", ("example" in leak[1] or "t0k" in leak[1], leak[0]),
     (False, "no"))
case("runtime box: initial endpoint response carries no credential", sup_calls[0][1], None)
case("runtime box: inherited credentials without a profile target are not used",
     rt.probe_box(ENV, lambda *_: (_ for _ in ()).throw(AssertionError("must not request")))[0], "no")
case("runtime web: a JSON body is yes", rt.probe_web(lambda u, h: (200, '{"hassio": 1}'))[0], "yes")
case("runtime web: an error is no", rt.probe_web(lambda u, h: (_ for _ in ()).throw(OSError("x")))[0], "no")


# ---------------------------------------------------------------- usage reader and card (KIT-USE)
ur = load(TEMPLATES / "runtime" / "usage_reader.py", "usage_reader")
from datetime import datetime as _dt, timezone as _tz, timedelta as _td  # noqa: E402

UTC = _tz.utc
TOK = "sk-ant-oat01-NOT-A-REAL-TOKEN"  # guard: allow test fixture
REPLY = {"five_hour": {"utilization": 3.0, "resets_at": "2026-01-15T14:00:00.123+00:00"},
         "seven_day": {"utilization": 41, "resets_at": "2026-01-17T04:00:00Z"},
         "seven_day_opus": {"utilization": 20.5, "resets_at": "2026-01-17T04:00:00Z"},
         "seven_day_sonnet": None, "seven_day_oauth_apps": {"utilization": 0, "resets_at": None},
         "extra_usage": {"is_enabled": False}}
NOW = _dt(2026, 1, 15, 12, 0, tzinfo=UTC)


def login(tmp, expires_ms=None, name="creds.json", **over):
    oauth = {"accessToken": TOK, "refreshToken": "r-NOT-REAL", "subscriptionType": "pro",
             "expiresAt": expires_ms if expires_ms is not None else int((NOW + _td(days=30)).timestamp() * 1000)}
    oauth.update(over)
    p = pathlib.Path(tmp) / name
    p.write_text(json.dumps({"claudeAiOauth": oauth}))
    return str(p)


CALLS = []


def ufetch(code=200, reply=REPLY, exc=None):
    def f(token):
        CALLS.append(token)
        if exc:
            raise exc
        return code, json.loads(json.dumps(reply))
    return f


with tempfile.TemporaryDirectory() as t:
    cp = login(t)
    o = ur.build({}, cp, UTC, now=NOW, fetch=ufetch())
    case("usage reader: a good reply is ok with week, session and plan",
         (o["status"], o["week"]["pct"], o["session"]["pct"], o["plan"], o["read_at"]),
         ("ok", 41.0, 3.0, "pro", "2026-01-15T12:00:00+00:00"))
    case("usage reader: per-model weekly figures, never oauth_apps or a null limit", sorted(o["models"]), ["opus"])
    case("usage reader: reset times normalized to UTC ISO", o["session"]["resets_at"], "2026-01-15T14:00:00+00:00")
    case("usage reader: first read of the day counts today from this read (a lower bound)",
         (o["today"]["pct"], o["today"]["since"]), (0.0, "2026-01-15T12:00:00+00:00"))
    case("usage reader: the token is never in the file", TOK in json.dumps(o) or "r-NOT-REAL" in json.dumps(o),
         False)

    # KIT-GUARD-FIX (from KAN-2cr F4, F5): the token echoed in any field is masked; NaN, infinity or a negative
    # is not a fresh read.
    echo = dict(REPLY, five_hour={"utilization": 3.0, "resets_at": None, "severity": TOK},
                **{"seven_day_" + TOK: {"utilization": 1.0, "resets_at": None}})
    eo = ur.build({}, cp, UTC, now=NOW, fetch=ufetch(reply=echo))
    case("usage reader: a token echoed in a key or a severity never reaches the file (F4)",
         (eo["status"], TOK in json.dumps(eo)), ("ok", False))
    eo2 = ur._scrub_all({"models": {TOK: {"severity": "x" + TOK}}}, TOK)
    case("usage reader: the scrub covers keys and nested values (F4)", TOK in json.dumps(eo2), False)
    for bad in (float("nan"), float("inf"), -1):
        bo = ur.build(o, cp, UTC, now=NOW + _td(hours=1), fetch=ufetch(reply=dict(REPLY, seven_day={
            "utilization": bad, "resets_at": "2026-01-17T04:00:00Z"})))
        case(f"usage reader: a weekly figure of {bad} is not a fresh read; the last good figure is kept (F5)",
             (bo["status"], bo["week"]["pct"], bo["read_at"]), ("unknown", 41.0, o["read_at"]))
    case("usage reader: a negative model figure is dropped (F5)",
         sorted(ur.parse_reply(dict(REPLY, seven_day_opus={"utilization": -5, "resets_at": None}))["models"]), [])

    later = ur.build(o, cp, UTC, now=NOW + _td(hours=2), fetch=ufetch(reply=dict(REPLY, seven_day={
        "utilization": 45, "resets_at": "2026-01-17T04:00:00Z"})))
    case("usage reader: today = the rise since the day's base", later["today"]["pct"], 4.0)

    # A read shortly before midnight is the day's base; `since` names that read (KIT-USEr L2: never padded unlabeled).
    night = dict(o, read_at="2026-01-15T23:40:00+00:00", week={"pct": 50.0, "resets_at": "2026-01-17T04:00:00+00:00"})
    morn = ur.build(night, cp, UTC, now=_dt(2026, 1, 16, 1, 0, tzinfo=UTC), fetch=ufetch(reply=dict(REPLY, seven_day={
        "utilization": 53, "resets_at": "2026-01-17T04:00:00Z"})))
    case("usage reader: new day from a recent pre-midnight read", (morn["today"]["pct"], morn["today"]["since"]),
         (3.0, "2026-01-15T23:40:00+00:00"))
    far = dict(night, read_at="2026-01-15T22:30:00+00:00")
    case("usage reader: a read over an hour before midnight is not the base (L2)",
         ur.build(far, cp, UTC, now=_dt(2026, 1, 16, 1, 0, tzinfo=UTC), fetch=ufetch(reply=dict(REPLY, seven_day={
             "utilization": 53, "resets_at": "2026-01-17T04:00:00Z"})))["today"],
         {"pct": 0.0, "date": "2026-01-16", "since": "2026-01-16T01:00:00+00:00"})

    # KIT-USEr M1: a read at the reset minute that still carries the old window waits; the roll is the reply's.
    wk = lambda pct, reset: dict(REPLY, seven_day={"utilization": pct, "resets_at": reset})  # noqa: E731
    d0 = {"date": "2026-01-15", "base": 80.0, "carried": 0.0, "since": "2026-01-15T00:00:00+00:00"}
    eve = dict(o, read_at="2026-01-15T21:40:00+00:00", week={"pct": 94.0, "resets_at": "2026-01-15T22:00:00+00:00"},
               day=d0, today={"pct": 14.0, "date": "2026-01-15", "since": d0["since"]})
    edge = ur.build(eve, cp, UTC, now=_dt(2026, 1, 15, 22, 0, 5, tzinfo=UTC),
                    fetch=ufetch(reply=wk(94, "2026-01-15T22:00:00Z")))
    case("usage reader: the reset-minute read with the old window is stale, today kept (M1)",
         (edge["status"], edge["today"]["pct"], edge["week"]["pct"], edge["read_at"]),
         ("stale", 14.0, 94.0, eve["read_at"]))
    rolled = ur.build(edge, cp, UTC, now=_dt(2026, 1, 15, 22, 20, tzinfo=UTC),
                      fetch=ufetch(reply=wk(1, "2026-01-22T22:00:00Z")))
    again = ur.build(rolled, cp, UTC, now=_dt(2026, 1, 15, 22, 40, tzinfo=UTC),
                     fetch=ufetch(reply=wk(2, "2026-01-22T22:00:00Z")))
    case("usage reader: then the roll counts once, and only once (M1)",
         (rolled["status"], rolled["today"]["pct"], again["today"]["pct"]), ("ok", 15.0, 16.0))
    # KIT-USEr L3: no resets_at at all; the drop is the roll.
    nul = dict(eve, week={"pct": 90.0, "resets_at": None}, day=dict(d0, base=85.0))
    dropped = ur.build(nul, cp, UTC, now=_dt(2026, 1, 15, 23, 0, tzinfo=UTC), fetch=ufetch(reply=wk(2, None)))
    case("usage reader: a weekly figure that drops is a roll even with no reset time (L3)",
         (dropped["status"], dropped["today"]["pct"], dropped["day"]["base"]), ("ok", 7.0, 0.0))
    # KIT-USEr L1: a reset before midnight and the day's first read after it: `since` is the reset.
    late = dict(eve, read_at="2026-01-15T21:50:00+00:00")
    first = ur.build(late, cp, UTC, now=_dt(2026, 1, 16, 1, 0, tzinfo=UTC),
                     fetch=ufetch(reply=wk(3, "2026-01-22T22:00:00Z")))
    case("usage reader: since names a pre-midnight reset (L1)", (first["today"]["pct"], first["today"]["since"]),
         (3.0, "2026-01-15T22:00:00+00:00"))
    # Same day, the week resets between two reads: what today used before the reset is carried.
    pre = dict(morn, week={"pct": 60.0, "resets_at": "2026-01-16T04:00:00+00:00"},
               day={"date": "2026-01-16", "base": 50.0, "carried": 0.0, "since": "2026-01-16T00:00:00+00:00"})
    post = ur.build(pre, cp, UTC, now=_dt(2026, 1, 16, 5, 0, tzinfo=UTC), fetch=ufetch(reply=dict(REPLY, seven_day={
        "utilization": 2, "resets_at": "2026-01-23T04:00:00Z"})))
    case("usage reader: today carries across the weekly reset", (post["today"]["pct"], post["day"]["base"]),
         (12.0, 0.0))
    case("usage reader: the household's time zone decides the day",
         ur.build({}, cp, ur._zone("America/Denver"), now=_dt(2026, 1, 16, 3, 0, tzinfo=UTC),
                  fetch=ufetch())["today"]["date"], "2026-01-15")

    CALLS.clear()
    old = login(t, expires_ms=int((NOW - _td(minutes=1)).timestamp() * 1000), name="old.json")
    exp = ur.build(o, old, UTC, now=NOW, fetch=ufetch())
    case("usage reader: an expired token is stale, never refreshed, no call made",
         (exp["status"], CALLS, exp["read_at"], exp["week"]["pct"]), ("stale", [], o["read_at"], 41.0))
    r401 = ur.build(o, cp, UTC, now=NOW + _td(hours=1), fetch=ufetch(code=401, reply=None))
    case("usage reader: a refused login is stale and keeps the last good read",
         (r401["status"], r401["read_at"]), ("stale", o["read_at"]))
    case("usage reader: a server error is error", ur.build(o, cp, UTC, now=NOW, fetch=ufetch(code=500))["status"],
         "error")
    shape = ur.build(o, cp, UTC, now=NOW, fetch=ufetch(reply={"weekly": {"used": 40}}))
    case("usage reader: a changed reply shape is unknown, figures not guessed",
         (shape["status"], shape["reason"], shape["week"]["pct"], shape["read_at"]),
         ("unknown", "reply shape changed: no seven_day.utilization", 41.0, o["read_at"]))
    leak = ur.build(o, cp, UTC, now=NOW, fetch=ufetch(exc=OSError("boom Bearer " + TOK)))
    case("usage reader: an error message never carries the token", (leak["status"], TOK in leak["reason"]),
         ("error", False))
    apikey = pathlib.Path(t) / "apikey.json"  # guard: allow a file name, no secret
    apikey.write_text(json.dumps({"primaryApiKey": "x"}))
    case("usage reader: an API-key login has no account usage",
         ur.build({}, str(apikey), UTC, now=NOW, fetch=ufetch())["status"], "error")
    case("usage reader: no login file is an error",
         ur.build({}, str(pathlib.Path(t) / "none.json"), UTC, now=NOW, fetch=ufetch())["status"], "error")

    # The real HTTP call, with a fake opener: headers, and an HTTP error answers its code.
    seen = {}

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        body = json.dumps(REPLY).encode()

        def read(self, n=-1):
            return self.body

    def opener(req, timeout):
        seen.update(url=req.full_url, beta=req.get_header("Anthropic-beta"),
                    auth=req.get_header("Authorization") == "Bearer " + TOK)
        return _Resp()

    case("usage reader: calls the usage endpoint with the beta header and the bearer token",
         (ur.fetch_usage(TOK, opener)[0], seen),
         (200, {"url": "https://api.anthropic.com/api/oauth/usage", "beta": "oauth-2025-04-20", "auth": True}))

    def opener401(req, timeout):
        raise ur.urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)

    case("usage reader: an HTTP error answers its status", ur.fetch_usage(TOK, opener401), (401, None))

    class _Html(_Resp):
        body = b"<html>proxy login</html>"

    case("usage reader: a 200 that is not JSON is an error, not a changed shape (N3)",
         ur.build(o, cp, UTC, now=NOW, fetch=lambda tok: ur.fetch_usage(tok, lambda req, timeout: _Html()))["status"],
         "error")
    case("usage reader: redirects are refused, so the token never follows one (L6)",
         (any(isinstance(h, ur._NoRedirect) for h in ur._OPENER.handlers),
          ur._NoRedirect().redirect_request(ur.urllib.request.Request(ur.URL), None, 302, "Found", {},
                                            "https://elsewhere.example.invalid/")), (True, None))

    # main(): writes the file atomically, prints no token; --reply works offline; a bad zone is exit 2.
    out = pathlib.Path(t) / "ha" / "usage.json"
    import contextlib  # noqa: E402
    import io  # noqa: E402
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ur.main(["--out", str(out), "--credentials", cp, "--tz", "UTC"], now=NOW, fetch=ufetch())
    case("usage reader main: exit 0, file written, no temp file left, no token printed",
         (rc, json.loads(out.read_text())["week"]["pct"], list(out.parent.glob("*.tmp")),
          TOK in buf.getvalue()), (0, 41.0, [], False))
    # KIT-GUARD-FIX (from KAN-2cr F6 and the closer's note N-a): a fresh temporary file, never a fixed name that a
    # planted link could redirect; the file stays readable by Home Assistant; --out may not be the login file.
    case("usage reader main: a new reading file is 0644, not mkstemp's 0600 (N-a)", oct(out.stat().st_mode & 0o777),
         "0o644")
    os.chmod(out, 0o640)
    trap = pathlib.Path(t) / "trap.txt"
    trap.write_text("keep\n")
    os.symlink(trap, out.parent / "usage.json.tmp")
    with contextlib.redirect_stdout(io.StringIO()):
        ur.main(["--out", str(out), "--credentials", cp, "--tz", "UTC"], now=NOW, fetch=ufetch())
    case("usage reader main: an old fixed-name temp link is never followed, and the file keeps its mode (F6)",
         (trap.read_text(), oct(out.stat().st_mode & 0o777), json.loads(out.read_text())["status"]),
         ("keep\n", "0o640", "ok"))
    login_before = pathlib.Path(cp).read_text()
    os.symlink(cp, pathlib.Path(t) / "alias.json")
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        rcs = [ur.main(["--out", o_, "--credentials", cp, "--tz", "UTC"], now=NOW, fetch=ufetch())
               for o_ in (cp, str(pathlib.Path(t) / "alias.json"))]
    case("usage reader main: --out naming the login file, or a link to it, is refused and the login kept (F6)",
         (rcs, pathlib.Path(cp).read_text() == login_before), ([2, 2], True))
    saved = pathlib.Path(t) / "reply.json"
    saved.write_text(json.dumps(REPLY))
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        rc = ur.main(["--out", str(out), "--reply", str(saved), "--dry-run"], now=NOW, fetch=ufetch(code=500))
    case("usage reader main: --reply reads a saved reply, --dry-run is exit 0 on ok", rc, 0)
    case("usage reader main: no --tz warns that it must be Home Assistant's zone (L4)",
         "warning: no --tz" in err.getvalue(), True)
    with contextlib.redirect_stderr(io.StringIO()):
        case("usage reader main: an unknown time zone is exit 2",
             ur.main(["--out", str(out), "--tz", "Nowhere/Place"]), 2)


def usage_state(age_min=10, week=41.0, today=4.0, today_date="2026-01-15", week_reset="2026-01-17T04:00:00+00:00",
                extra=None):
    read = (_dt(2026, 1, 15, 12, 0, tzinfo=UTC) - _td(minutes=age_min)).isoformat()
    a = {"read_at": read, "status": "ok", "week": {"pct": week, "resets_at": week_reset},
         "session": {"pct": 3.0, "resets_at": "2026-01-15T14:00:00+00:00"},
         "today": {"pct": today, "date": today_date}, "models": {"opus": {"pct": 20.5, "resets_at": week_reset}}}
    a.update(extra or {})
    return {"sensor.assistant_usage_read": {"state": read, "attributes": a},
            "input_number.assistant_usage_weekly_warning": "80", "input_number.assistant_usage_daily_budget": "14.3",
            "input_boolean.assistant_usage_alerts": "off"}


def um(expr, states):
    names = "usage_pct, usage_pace, usage_over, usage_age_min, usage_bars_md, usage_numbers_md"
    return render("{% from 'usage.jinja' import " + names + " %}" + expr, states).strip()


case("usage card: fresh figures", um("{{ usage_pct('week') }} {{ usage_pct('today') }} {{ usage_pct('model:opus') }}",
                                     usage_state()), "41.0 4.0 20.5")
case("usage card: a read older than two hours is unknown", um("{{ usage_pct('week') }}", usage_state(age_min=121)),
     "unknown")
case("usage card: a window that has reset since the read is unknown",
     um("{{ usage_pct('week') }}", usage_state(week_reset="2026-01-15T11:59:00+00:00")), "unknown")
case("usage card: yesterday's today is unknown", um("{{ usage_pct('today') }}", usage_state(today_date="2026-01-14")),
     "unknown")
case("usage card: no sensor at all is unknown and 'Not read yet'",
     (um("{{ usage_pct('week') }}", {}), "Not read yet" in um("{{ usage_bars_md(80, 14.3) }}", {})),
     ("unknown", True))
case("usage card: pace line 2 days into the week", um("{{ usage_pace() }}",
                                                       usage_state(week_reset="2026-01-20T12:00:00+00:00")), "28.6")
case("usage card: no pace line once the week has reset", um("{{ usage_pace() }}",
                                                            usage_state(week_reset="2026-01-15T11:00:00+00:00")),
     "unknown")
case("usage card: over on the weekly level (helper ids)",
     um("{{ usage_over('input_number.assistant_usage_weekly_warning', 'input_number.assistant_usage_daily_budget') }}",
        usage_state(week=80.0)), "on")
case("usage card: over on the daily budget", um("{{ usage_over(80, 14.3) }}", usage_state(today=14.3)), "on")
case("usage card: under both is off", um("{{ usage_over(80, 14.3) }}", usage_state()), "off")
case("usage card: unknown is never over", um("{{ usage_over(10, 1) }}", usage_state(age_min=500)), "off")
bars = um("{{ usage_bars_md(80, 14.3) }}", usage_state())
case("usage card: bars show the value, limit mark and pace mark",
     ("41%" in bars, bars.count("┃") >= 3, "▲" in bars, "Read 10 min ago" in bars), (True, True, True, True))
case("usage card: stale bars say unknown", um("{{ usage_bars_md(80, 14.3) }}", usage_state(age_min=200)).count(
    "unknown") >= 3, True)
nums = um("{{ usage_numbers_md(80, 14.3) }}", usage_state(extra={"status": "stale", "reason": "token expired"}))
unset = dict(usage_state(), **{"input_number.assistant_usage_weekly_warning": {"state": "10", "attributes": {"min": 10}},
                               "input_number.assistant_usage_daily_budget": {"state": "14.3",
                                                                             "attributes": {"min": 1}}})
H = "'input_number.assistant_usage_weekly_warning', 'input_number.assistant_usage_daily_budget'"
case("usage card: a helper at its minimum says thresholds not set, in both views (L5)",
     ["Thresholds not set" in um("{{ usage_" + v + "_md(" + H + ") }}", unset) for v in ("bars", "numbers")],
     [True, True])
case("usage card: thresholds set, no note",
     "Thresholds not set" in um("{{ usage_numbers_md(" + H + ") }}", usage_state()), False)
sev = usage_state(extra={"week": {"pct": 41.0, "resets_at": "2026-01-17T04:00:00+00:00", "severity": "warning"}})
case("usage card: the numbers view shows the provider's severity (N2)",
     "provider: week warning" in um("{{ usage_numbers_md(80, 14.3) }}", sev), True)
case("usage card: numbers show headroom, model rows and the last try",
     ("| Week | 41% | 80% | 39 |" in nums, "| Week, opus | 20.5% |" in nums, "last try: stale - token expired" in nums),
     (True, True, True))

# The package's own templates, rendered the way Home Assistant would.
up = yaml.load((TEMPLATES / "packages" / "assistant-usage.yaml").read_text(), Loader=_L)
tsens = {s["unique_id"]: s for blk in up["template"] for kind in ("sensor", "binary_sensor") for s in blk.get(kind, [])}
case("usage package: the week sensor renders a number", render(tsens["assistant_usage_week"]["state"],
                                                              usage_state()).strip(), "41.0")
case("usage package: a stale week renders None (Home Assistant shows unknown)",
     render(tsens["assistant_usage_week"]["state"], usage_state(age_min=300)).strip(), "None")
case("usage package: stale binary sensor", [render(tsens["assistant_usage_stale"]["state"], usage_state(age_min=a))
                                            .strip() for a in (10, 300)], ["False", "True"])
over_on = usage_state(week=90.0)
case("usage package: the threshold sensor stays off until the household turns it on",
     [render(tsens["assistant_usage_over_threshold"]["state"],
             dict(over_on, **{"input_boolean.assistant_usage_alerts": s})).strip() for s in ("off", "on")],
     ["False", "True"])
case("usage package: the reader's file keys are the sensor's attributes",
     set(up["command_line"][0]["sensor"]["json_attributes"]) >= set(o) - {"day"}, True)
card = yaml.load((TEMPLATES / "dashboards" / "assistant-usage-card.yaml").read_text(), Loader=_L)
views = [c["conditions"][0]["state"] for c in card["cards"] if c["type"] == "conditional"
         and c["conditions"][0]["entity"] == "input_select.assistant_usage_view"]
case("usage card: one conditional card per view option", views, up["input_select"]["assistant_usage_view"]["options"])
tacho = [c for c in card["cards"] if c["type"] == "conditional" and c["conditions"][0]["state"] == "Tachometer"][0]
foot = [c["content"] for c in tacho["card"]["cards"] if c["type"] == "markdown"][0]
case("usage card: the Tachometer footer says unknown, never 'unknown%' (N1)",
     [render(foot, dict(usage_state(), **{"sensor.assistant_usage_pace_line": v})).split("·")[0].strip()
      for v in ("unknown", "28.6")], ["Pace line unknown", "Pace line 28.6%"])


# ---------------------------------------------------------------- board check (docs/board_check.py)
import re  # noqa: E402

bc = load(TEMPLATES / "docs" / "board_check.py", "board_check")
board_text = (TEMPLATES / "docs" / "board.md").read_text()
seed = bc.parse_board(board_text)
case("board: the level-2 seed parses clean", (seed["level"], len(seed["items"]), len(seed["runlog"]), seed["faults"]),
     (2, 5, 1, []))
case("board: one seed row per status kind", sorted(r["word"] for r in seed["items"]),
     ["BACKLOG", "BLOCKED", "DONE", "NEEDS OWNER", "READY FOR REVIEW"])
case("board: the seed's closer is read", [r["closer"] for r in seed["items"] if r["code"] == "ROUTER-1"],
     [("owner", "read")])
case("board: every seed code has a plain name",
     bc.check_names(seed, (TEMPLATES / "docs" / "card-names.tsv").read_text()), [])
case("board: the run-log line is read with est and actual",
     (seed["runlog"][0]["lane"], seed["runlog"][0]["code"], seed["runlog"][0]["est"], seed["runlog"][0]["actual"],
      seed["runlog"][0]["helpers"]), ("agent", "ROUTER-1", 3.0, 2.0, "none"))
spec = (TEMPLATES / "docs" / "board-format.md").read_text()
# KIT-DRY.f5: one point scale and honest missing usage, without losing numeric actuals.
point_docs = [(TEMPLATES / "docs" / name).read_text()
              for name in ("backlog.md", "board.md", "board-format.md")]
case("board KIT-DRY.f5: backlog and board share the format's weekly point scale",
     [bool(re.search(r"1 point = 0\.1\s*% of the weekly assistant limit", text)) for text in point_docs],
     [True, True, True])
unknown_line = ("2026-03-02 09:00-09:20 CST agent ROUTER-1 est 3 / actual unknown "
                "(PARTIAL: no usable usage read) helpers: none")
run_head = board_text.rsplit("## Run log", 1)[0] + "## Run log\n"
for helpers in ("none", "mechanical counted the rows"):
    unknown_board = bc.parse_board(run_head + unknown_line.replace("helpers: none", "helpers: " + helpers) + "\n")
    case("board KIT-DRY.f5: actual unknown is an unmeasured run with helpers " + helpers,
         (unknown_board["faults"], [(r["est"], r["actual"], r["helpers"], r.get("skipped", False))
                                   for r in unknown_board["runlog"]]),
         ([], [(3.0, None, helpers, False)]))
mixed_board = bc.parse_board(run_head + "\n".join(unknown_line.replace("actual unknown", "actual " + actual)
                                                for actual in ("0", "0.5", "unknown")) + "\n")
case("board KIT-DRY.f5: measured zero, half a point and unknown stay distinct",
     (mixed_board["faults"], [r["actual"] for r in mixed_board["runlog"]]), ([], [0.0, 0.5, None]))
for actual in ("UNKNOWN", "unknown%", "unknown0", "n/a"):
    malformed = bc.parse_board(run_head + unknown_line.replace("actual unknown", "actual " + actual) + "\n")
    case("board KIT-DRY.f5: malformed actual is still a fault: " + actual,
         (len(malformed["faults"]), malformed["runlog"]), (1, []))
unknown_est = bc.parse_board(run_head + unknown_line.replace("est 3", "est unknown") + "\n")
case("board KIT-DRY.f5: the estimate still needs a number",
     (len(unknown_est["faults"]), unknown_est["runlog"]), (1, []))
documented_unknown = [line for line in spec.splitlines() if re.match(r"^\d{4}-\d{2}-\d{2} .* / actual unknown ", line)]
case("board KIT-DRY.f5: the format ships a valid actual unknown example",
     (len(documented_unknown), all(bc.RUN_RE.fullmatch(line) for line in documented_unknown)), (1, True))
with tempfile.TemporaryDirectory() as td:
    unknown_path = pathlib.Path(td) / "board.md"
    unknown_path.write_text(run_head + unknown_line + "\n")
    import io, contextlib
    report = io.StringIO()
    with contextlib.redirect_stdout(report):
        unknown_exit = bc.main([str(unknown_path), "--names", str(TEMPLATES / "docs" / "card-names.tsv")])
    case("board KIT-DRY.f5: actual unknown passes the CLI with names checked",
         (unknown_exit, "5 rows, 1 run-log lines, 0 faults" in report.getvalue()), (0, True))
# End KIT-DRY.f5 regression cases.
frag = re.search(r"```markdown\n(.*?)```", spec, re.S).group(1)
l6 = bc.parse_board("# x board\n\n" + frag + "\n## Run log\n")
case("board: the level-6 fragment in board-format.md parses clean",
     (l6["level"], len(l6["items"]), sorted(l6["sprints"]), sorted(l6["epics"]), l6["faults"]),
     (6, 6, ["S1", "S2", "S3", "S4", "S5"], ["EP-GUEST"], []))
case("board: a queued row with its BACKLOG word dropped reads as BACKLOG",
     [(r["word"], r["queued"]) for r in l6["items"] if r["code"] == "N3r"], [("BACKLOG", "QUEUED (12h)")])
case("board: tokens are read by shape", [r["tokens"] for r in l6["items"] if r["code"] == "UPD-S2"],
     [{"priority": "3", "sprint": "S2", "epic": "UPKEEP"}])


def faults_of(rows, level6=False, runlog=""):
    head = "# t board\n\n"
    if level6:
        head += ("## Plans\nPLAN 2026-01-01 05:30 CST (planner): none\n## Sprints\n| Sprint | Dates | Allows | Capacity |\n"
                 "|---|---|---|---|\n| S1 | a..b | anything | 10 |\n## Epics\n| Epic | Name | Goal | Done when | Target | Owner |\n"
                 "|---|---|---|---|---|---|\n| EP-A | A | g | d | 2026-02-01 | lead |\n")
    body = head + "## Items\n\n" + bc.ITEMS_HEADER + "\n|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n## Run log\n" + runlog
    return sorted(m for _, _, m in bc.parse_board(body)["faults"])


# KIT-BRD.f: reproduce the two rejected status shapes and preserve the parsed apply date.
dated = bc.parse_board("# x board\n\n" + frag.replace(
    "-> closer: reviewer [review]", "-> closer: lead 2026-03-04 [apply]") + "\n## Run log\n")
case("board M1: dated apply closer parses clean and keeps its date",
     (dated["faults"], [(r["closer"], r.get("closer_date")) for r in dated["items"] if r["code"] == "N3"]),
     ([], [(("lead", "apply"), "2026-03-04")]))
case("board M1: undated closer keeps the existing tuple and has no date",
     [(r["closer"], r.get("closer_date")) for r in seed["items"] if r["code"] == "ROUTER-1"],
     [(("owner", "read"), None)])
for prefix in ("QUEUED (12h)", "QUEUED (12-24h)"):
    detailed = bc.parse_board("# x board\n\n" + frag.replace(
        "QUEUED (12h) [P1]", prefix + " (after N3: met) [P1]") + "\n## Run log\n")
    case("board M2: queued dependency detail reads as BACKLOG: " + prefix,
         (detailed["faults"], [(r["word"], r["queued"], "(after N3: met)" in r["status"])
                              for r in detailed["items"] if r["code"] == "N3r"]),
         ([], [("BACKLOG", prefix, True)]))
case("board L1: queued BLOCKED is not runnable",
     faults_of(["| **X-1 a** | builder | 1 | QUEUED (12h) BLOCKED by input [P1] [S1] [EP-A] | | |"],
               level6=True), ["finished row keeps a queue prefix (QUEUED (12h) BLOCKED)"])
for status in ("PARTIAL next step", "IN PROGRESS builder 2026-03-04 09:00"):
    case("board L1: unfinished work may stay queued: " + status,
         faults_of(["| **X-1 a** | builder | 1 | QUEUED (12h) " + status + " [P1] [S1] [EP-A] | | |"],
                   level6=True), [])
case("board KIT-LAND: PASSED - MERGE with date, what lands it and who merges is clean",
     faults_of(["| **X-1 a** | builder | 1 | PASSED - MERGE 2026-03-04 (review PASS) waits on PR #12 merge -> lead "
                "[P1] [S1] [EP-A] | PR #12 | |"], level6=True), [])
case("board KIT-LAND: PASSED - MERGE without its merge owner is a fault",
     faults_of(["| **X-1 a** | builder | 1 | PASSED - MERGE 2026-03-04 (review PASS) [P1] [S1] [EP-A] | | |"],
               level6=True), ["PASSED - MERGE must say '<date> ... waits on <what lands it> -> <who merges>'"])
case("board KIT-LAND: PASSED - MERGE is finished: a queue prefix on it is a fault",
     faults_of(["| **X-1 a** | builder | 1 | QUEUED (12h) PASSED - MERGE 2026-03-04 waits on PR #1 -> lead "
                "[P1] [S1] [EP-A] | | |"], level6=True),
     ["finished row keeps a queue prefix (QUEUED (12h) PASSED - MERGE)"])
_land = {"A6": {"code": "A6", "word": "PASSED - MERGE", "status": "PASSED - MERGE 2026-03-04 waits on PR #1 -> lead"}}
case("preflight KIT-LAND: a passed, unmerged row meets 'after X in review' but not 'after X'",
     (pf.after_met("A6", "in review", _land), pf.after_met("A6", "", _land), pf.after_met("A6", "merged", _land)),
     (True, False, False))
case("board M1: a date cannot substitute for a closer lane",
     faults_of(["| **X-1 a** | builder | 1 | READY FOR REVIEW -> closer: 2026-03-04 [apply] [P1] [S1] [EP-A] | | |"],
               level6=True), ["closer lane '2026-03-04' is not a role"])


case("board check: a duplicate code is a fault",
     faults_of(["| **X-1 a** | agent | 1 | BACKLOG | | |", "| **X-1 b** | agent | 1 | BACKLOG | | |"]),
     ["duplicate code (first at line 7)"])
case("board check: a finished row keeping its queue prefix is a fault (level 6)",
     faults_of(["| **X-1 a** | builder | 1 | QUEUED (12h) READY FOR REVIEW -> closer: reviewer [review] [P1] [S1] [EP-A] | | |"],
               level6=True), ["finished row keeps a queue prefix (QUEUED (12h) READY FOR REVIEW)"])
case("board check: a queue prefix on a level-2 board is a fault",
     faults_of(["| **X-1 a** | agent | 1 | QUEUED (12h) BACKLOG | | |"]), ["queue prefix on a level-2 board (no planner)"])
case("board check: level 6 wants every token, a known sprint and epic, and a closer in review",
     faults_of(["| **X-1 a** | builder | 1 | READY FOR REVIEW [P1] [S9] [EP-Z] | | |",
                "| **X-2 b** | builder | 1 | BACKLOG [P1] | | |"], level6=True),
     ["epic EP-Z is not in the Epics table", "in review without a closer (-> closer: <lane> [<what>])",
      "open row without a epic token ([Pn] [Sn] [EP-x] or [UPKEEP])",
      "open row without a sprint token ([Pn] [Sn] [EP-x] or [UPKEEP])", "sprint S9 is not in the Sprints table"])
case("board check: closed rows need no tokens at level 6",
     faults_of(["| **X-1 a** | builder | 1 | DONE 2026-01-02 (PASS) | | |"], level6=True), [])
case("board check: the row shape faults",
     faults_of(["| X-1 a | agent | 1 | BACKLOG | | |", "| **X-2 b** | agent | 1 | BACKLOG |",
                "| **X-3 c** | model-x | many | WAITING | | |", "| **X-4 d** | agent | 25 | BACKLOG | | |",
                "| **D-X5 e** | agent | 1 | BACKLOG (owner) | | |", "| **X-6 f** | agent | 1 | NEEDS OWNER | | |",
                "| **X-7 g** | agent | 1 | IN PROGRESS | | |", "| **X-8 h** | agent | 1 | DONE | | |",
                "| **X-9 i** | agent | 1 | BLOCKED on x | | |"]),
     ["25 points: split first (cap 20)", "4 cells, expected 6", "BLOCKED must say 'BLOCKED by <what>'",
      "DONE needs its date", "IN PROGRESS must say '<lane> YYYY-MM-DD HH:MM'",
      "Item cell must start with **CODE Title** (code: capital letter, then letters, digits, hyphens, dots)",
      "NEEDS OWNER with an empty Decisions cell (say what, or 'see D-CODE')",
      "Pts 'many' is not a number (halves allowed; a note may follow in parentheses)",
      "an owner card (D-) must be in the owner lane",
      "status must start with one of: BACKLOG, IN PROGRESS, READY FOR REVIEW, PASSED - MERGE, NEEDS OWNER, BLOCKED, PARTIAL, DONE, DROPPED, RETIRED",
      "unknown lane 'model-x' (roles: agent, builder, lead, mechanical, owner, planner, reviewer, writer)"])
case("board check: an escaped pipe stays inside its cell",
     [r["title"] for r in bc.parse_board("# b\n## Items\n" + bc.ITEMS_HEADER + "\n|---|---|---|---|---|---|\n"
                                         "| **X-1 a \\| b** | agent | 1 | BACKLOG | | |\n## Run log\n")["items"]], ["a | b"])
case("board check: run-log shapes",
     faults_of(["| **X-1 a** | agent | 1 | BACKLOG | | |"],
               runlog="2026-01-02 09:00-09:20 CST agent X-1 est 1 / actual 1 (DONE) helpers: none\n"
                      "2026-01-02 10:00-10:20 CST builder X-1 est 1 / actual 0.5 (PARTIAL) helpers: mechanical counted the rows\n"
                      "2026-01-02 11:00 CST builder skipped: budget (week 40 %, reviewer 38 %, line 35 %, read 2026-01-02 10:15 CST)\n"
                      "2026-01-02 12:00 CST builder X-1 did a thing\n"
                      "2026-01-02 13:00-13:10 CST builder X-1 est 1 / actual 1 (DONE)\n"),
     ["run-log line matches neither shape (board-format.md section 7)"] * 2)
case("board check: missing plain names are reported per code",
     [c for _, c, _ in bc.check_names(seed, "# only one\nPORCH-1\tPorch light\nbad line\n")],
     ["-", "ROUTER-1", "HEALTH-1", "DRILL-1", "MANUAL-1"])
with tempfile.TemporaryDirectory() as td:
    bp = pathlib.Path(td) / "board.md"
    bp.write_text(board_text)
    (pathlib.Path(td) / "card-names.tsv").write_text((TEMPLATES / "docs" / "card-names.tsv").read_text())
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc_clean = bc.main([str(bp)])
        rc_nonames = bc.main([str(bp), "--names", str(pathlib.Path(td) / "none.tsv")])
        rc_skip = bc.main([str(bp), "--names", "-"])
        rc_missing = bc.main([str(pathlib.Path(td) / "missing.md")])
    case("board check: exit codes (clean 0, faults 1, skip names 0, unreadable 2)",
         (rc_clean, rc_nonames, rc_skip, rc_missing), (0, 1, 0, 2))
    case("board check: the report is a table with the fault's line", "no names file at" in buf.getvalue(), True)


# ---------------------------------------------------------------- what-next facts (tools/what-next, KIT-NEXT0)

import shutil  # noqa: E402

KIT = TEMPLATES.parent
wn = load(KIT / "tools/what-next/what_next.py", "what_next")
case("what-next: the built-in YAML reader reads the profile template as PyYAML does",
     wn.mini_yaml((KIT / "interview/profile-template.yaml").read_text()),
     yaml.safe_load((KIT / "interview/profile-template.yaml").read_text()))
case("what-next: the built-in reader takes flow maps in block lists and comments",
     wn.mini_yaml("adoption:\n  level: 1  # one\n  skipped:\n    - {piece: H6, on: 2026-12-01, why: no panel}\n"
                  "  once_done: []\n"),
     {"adoption": {"level": 1, "skipped": [{"piece": "H6", "on": "2026-12-01", "why": "no panel"}], "once_done": []}})

WN_DAY = wn.datetime.date(2026, 3, 1)
WN_LOG_ENTRY = "## {d} 10:00 - {t}\n- **Why:** w\n- **Authorized:** owner\n- **Changed:** f\n- **Checks:** c\n- **Undo:** {u}\n\n"
WN_ROW = "| **{c} {t}** detail | agent | 1 | {s} | | |\n"
WN_RUN = "2026-02-{d:02d} 10:00-11:00 CST agent {c} est 1 / actual 1 (DONE) helpers: none\n"


def wn_git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)


def wn_write(repo, path, text):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def wn_profile(adoption="", topics="done", setup=True):
    tl = "".join(f"    {t}: {topics}\n" for t in ("people", "areas", "devices", "priorities", "rhythm", "agent"))
    return (f"kit_version: 2\n{adoption}setup:\n  done: {'true' if setup else 'false'}\n"
            f"  installed_on: {'2026-01-05' if setup else 'null'}\nprofile:\n  done: false\n  topics:\n{tl}")


def wn_facts(repo, **kw):
    return wn.gather(repo, WN_DAY, **kw)


def wn_res(facts):
    return {c["id"]: c["result"] for c in facts["checks"]}


with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    repo, remote = td / "house-repo", td / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    repo.mkdir()
    wn_git(repo, "init", "-q", "-b", "main")
    wn_git(repo, "remote", "add", "origin", str(remote))
    wn_write(repo, "AGENTS.md", "# agents\n")
    for src in ("docs/board_check.py", "runtime/probe_runtime.py"):
        wn_write(repo, f"templates/{src}", (TEMPLATES / src).read_text())
    wn_git(repo, "add", "-A")
    wn_git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "start")

    f = wn_facts(repo)
    case("what-next: an empty house passes no level", (f["auto_pass_through"], f["schema"]), (None, None))
    case("what-next: every check of levels 0-2 is reported, asks as ask",
         sorted({c["level"] for c in f["checks"]}) + [wn_res(f)["L1-private"], wn_res(f)["L0-backup-proven"]],
         [0, 1, 2, "ask", "ask"])

    # Level 0: the profile and the first CHANGELOG entry.
    wn_write(repo, "house/profile.yaml", wn_profile(topics="pending"))
    log = WN_LOG_ENTRY.format(d="2026-01-05", t="Home Assistant installed (Phase 0)", u="<the steps>")
    wn_write(repo, "house/docs/CHANGELOG.md", "# Changelog\n\n" + log)
    f = wn_facts(repo)
    case("what-next: level 0 passes on the profile and the first entry; schema v1 named",
         (f["auto_pass_through"], wn_res(f)["L0-profile"], f["schema"].startswith("v1")), (0, "pass", True))
    wn_write(repo, "house/profile.yaml", wn_profile(topics="pending", setup=False))
    case("what-next: setup not done fails L0-profile", wn_res(wn_facts(repo))["L0-profile"], "fail")

    # Level 1: hook, guard selftest, ignore rules, topics, three undone changes, a gotcha.
    shutil.copytree(TEMPLATES / "guard", repo / "guard")
    (repo / "guard/names.txt").write_text("# names\nSamplename\n")
    wn_write(repo, ".gitignore", "guard/names.txt\nsecrets.yaml\n")
    wn_write(repo, ".git/hooks/pre-push", guard_st.HOOK_STUB.decode())
    (repo / ".git/hooks/pre-push").chmod(0o755)
    wn_write(repo, "house/profile.yaml", wn_profile())
    entries = "".join(WN_LOG_ENTRY.format(d=f"2026-02-0{i}", t=f"change {i}", u="git revert abc") for i in (3, 2))
    wn_write(repo, "house/docs/CHANGELOG.md", "# Changelog\n\n" + entries + log.replace("<the steps>", "reinstall"))
    wn_write(repo, "house/docs/gotchas.md", "# Gotchas\n<!-- ### <the rule> -->\n## How an entry looks\n"
                                            "### <the rule, as one sentence>\n## Lights\n### Dimmers round to ten\n"
                                            "- **Incident:** 2026-02-01 - the kitchen read 40 %\n")
    wn_git(repo, "add", "-A")
    wn_git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "level 1")
    f = wn_facts(repo)
    r = wn_res(f)
    if hook_execution_denied(repo):
        print("SKIP what-next: level 1 passes (this computer or sandbox will not run hook files)")
    else:
        case("what-next: level 1 passes (dry-run push to a local remote, real guard selftest)",
             (f["auto_pass_through"], r["L1-remote"], r["L1-guard"], r["L1-ignored"], r["L1-gotchas"]),
             (1, "pass", "pass", "pass", "pass"))
    wn_write(repo, "house/docs/CHANGELOG.md", "# Changelog\n\n" + entries + log)
    case("what-next: an entry whose undo is still the template's placeholder does not count",
         wn_res(wn_facts(repo, network=False))["L1-changelog-3"], "fail")
    wn_write(repo, "house/docs/CHANGELOG.md", "# Changelog\n\n" + entries + log.replace("<the steps>", "reinstall"))
    case("what-next: offline flags make their checks unknown, never pass",
         [wn_res(wn_facts(repo, network=False, selftest=False))[k] for k in ("L1-remote", "L1-guard")],
         ["unknown", "unknown"])
    (repo / "guard/names.txt").write_text("# names only\n")
    wn_write(repo, ".gitignore", "guard/names.txt\n/secrets.yaml\n")
    r = wn_res(wn_facts(repo, network=False))
    ev = next(c["evidence"] for c in wn_facts(repo, network=False)["checks"] if c["id"] == "L1-ignored")
    case("what-next: an empty names list and an unignored ha/secrets.yaml fail L1-ignored",
         (r["L1-ignored"], "has no names" in ev, "ha/secrets.yaml not ignored" in ev), ("fail", True, True))
    (repo / "guard/names.txt").write_text("Samplename\n")
    wn_write(repo, ".gitignore", "guard/names.txt\nsecrets.yaml\n")
    wn_write(repo, ".git/hooks/pre-push", "#!/bin/sh\nexit 0\n")
    case("what-next: a hook that does not call the guard fails L1-guard",
         wn_res(wn_facts(repo, network=False))["L1-guard"], "fail")
    wn_write(repo, ".git/hooks/pre-push", guard_st.HOOK_STUB.decode())
    (repo / ".git/hooks/pre-push").chmod(0o755)

    # Level 2: the board, the backlog moved, three DONE rows in the CHANGELOG, three runs, nothing stale.
    rows = "".join(WN_ROW.format(c=c, t="t", s="DONE 2026-02-0" + str(i)) for i, c in enumerate(("LAMP-1", "FAN-1", "TV-1"), 1))
    board = ("# Board\n\n## Items\n\n| Item | Lane | Pts | Status | Link | Decisions needed |\n|---|---|---|---|---|---|\n"
             + rows + "\n## Run log\n\n" + "".join(WN_RUN.format(d=d, c=c) for d, c in ((3, "TV-1"), (2, "FAN-1"), (1, "LAMP-1"))))
    wn_write(repo, "house/docs/board.md", board)
    wn_write(repo, "house/docs/card-names.tsv", "LAMP-1\tlamp\nFAN-1\tfan\nTV-1\ttv\nNEW-1\tnew\n")
    wn_write(repo, "house/docs/backlog.md", "# Backlog\n\n**Status: the items moved to the board (docs/board.md).**\n"
                                           "<!-- ### 1. an example in a comment -->\n## Rulings\n")
    named = "".join(WN_LOG_ENTRY.format(d="2026-02-1" + str(i), t=f"{c} done", u="git revert abc")
                    for i, c in enumerate(("LAMP-1", "FAN-1", "TV-1"), 1))
    wn_write(repo, "house/docs/CHANGELOG.md", "# Changelog\n\n" + named + entries + log)
    f = wn_facts(repo, network=False)
    r = wn_res(f)
    case("what-next: level 2's auto checks pass on a clean board",
         [r[k] for k in ("L2-board", "L2-backlog-moved", "L2-done-3", "L2-runlog-3", "L2-in-progress-age")],
         ["pass"] * 5)
    case("what-next: pass-through stops at an unknown check (offline)", f["auto_pass_through"], 0)
    if hook_execution_denied(repo):
        print("SKIP what-next: online, level 2 passes through (this computer or sandbox will not run hook files)")
    else:
        case("what-next: online, level 2 passes through", wn_facts(repo)["auto_pass_through"], 2)
    stale = board.replace(rows, rows + WN_ROW.format(c="NEW-1", t="t", s="IN PROGRESS agent 2026-02-10 09:00"))
    wn_write(repo, "house/docs/board.md", stale)
    f = wn_facts(repo, network=False)
    case("what-next: a row IN PROGRESS for over seven days fails, and counts as busy",
         (wn_res(f)["L2-in-progress-age"], f["busy"]["board_rows"]["in_progress"]), ("fail", ["NEW-1"]))
    wn_write(repo, "house/docs/board.md", board.replace("LAMP-1", "PORCH-1"))
    wn_write(repo, "house/docs/card-names.tsv", "PORCH-1\tp\nFAN-1\tfan\nTV-1\ttv\n")
    f = wn_facts(repo, network=False)
    case("what-next: a template seed row left on the board fails L2-board; an unnamed DONE row is not counted",
         (wn_res(f)["L2-board"], wn_res(f)["L2-done-3"]), ("fail", "fail"))
    wn_write(repo, "house/docs/board.md", board)
    wn_write(repo, "house/docs/card-names.tsv", "LAMP-1\tlamp\nFAN-1\tfan\nTV-1\ttv\n")
    wn_write(repo, "house/docs/backlog.md", "# Backlog\n\n**Status: the items moved to the board.**\n\n"
                                           "## From the interview\n\n### 1. Porch light\n")
    case("what-next: a backlog still listing items fails L2-backlog-moved",
         wn_res(wn_facts(repo, network=False))["L2-backlog-moved"], "fail")

    # The adoption block: standing failures, pace, pause, skips, once checks.
    adoption = ("adoption:\n  level: 1\n  pace: monthly\n  paused_until: 2026-03-10\n  last_new_piece: 2026-02-10\n"
                "  skipped:\n    - {piece: D2, on: 2026-02-01, why: no guests}\n    - {piece: R3, on: 2025-11-01, why: no car}\n"
                "  once_done:\n    - {check: L0-backup-proven, on: 2026-01-06}\n")
    wn_write(repo, "house/profile.yaml", wn_profile(adoption=adoption))
    (repo / "house/docs/gotchas.md").write_text("# Gotchas\n")
    f = wn_facts(repo, network=False)
    a = f["adoption"]
    case("what-next: a failing check at or below the recorded level is a standing failure; above it is not",
         ("L1-gotchas" in f["standing_failures"], "L2-backlog-moved" in f["standing_failures"]), (True, False))
    case("what-next: pace, pause and next-piece date from the block",
         (a["level"], a["pace"], a["paused"], a["next_piece_due"], f["schema"]), (1, "monthly", True, "2026-03-12", "v2"))
    case("what-next: a skip inside 60 days is active, an older one is not",
         [(s["piece"], s["active"]) for s in a["skipped"]], [("D2", True), ("R3", False)])
    case("what-next: a recorded once check passes with its date", wn_res(f)["L0-backup-proven"], "pass")
    wn_write(repo, "house/profile.yaml", wn_profile(adoption=adoption + (
        "  opted_out:\n    - {what: gotchas habit, on: 2026-02-20, why: not for us, checks: [L1-gotchas]}\n")))
    f2 = wn_facts(repo, network=False)
    case("what-next: a check the owner opted out of still runs but is no standing failure (KIT-OWNER)",
         (wn_res(f2)["L1-gotchas"], "L1-gotchas" in f2["standing_failures"],
          [(o["what"], o["on"], o["checks"]) for o in f2["adoption"]["opted_out"]]),
         ("fail", False, [("gotchas habit", "2026-02-20", ["L1-gotchas"])]))
    wn_write(repo, "house/profile.yaml", wn_profile(adoption=adoption))

    # KIT-NEXT0r findings (M1-M4, L1-L4).
    tmpl = (TEMPLATES / "docs/gotchas.md").read_text()
    real = tmpl + "\n### Dimmers round to ten\n- **Incident:** 2026-02-01 - the kitchen read 40 %\n"
    case("what-next: the gotchas template has no entries; a real one under an area heading counts (M1)",
         (wn.gotcha_entries(tmpl), wn.gotcha_entries(real)), ([], ["Dimmers round to ten"]))
    (repo / "house/docs/gotchas.md").write_text(tmpl)
    case("what-next: the untouched gotchas template fails L1-gotchas (M1)",
         wn_res(wn_facts(repo, network=False))["L1-gotchas"], "fail")
    wn_write(repo, "secrets.yaml", "x: y\n")
    wn_git(repo, "add", "-f", "secrets.yaml")
    wn_git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "oops")
    ev = next(c for c in wn_facts(repo, network=False)["checks"] if c["id"] == "L1-ignored")
    case("what-next: a secrets.yaml tracked before its ignore rule fails L1-ignored (M2)",
         (ev["result"], "secrets.yaml tracked by git" in ev["evidence"]), ("fail", True))
    wn_git(repo, "rm", "-q", "--cached", "secrets.yaml")
    wn_git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "untrack")
    (repo / "secrets.yaml").unlink()
    wn_write(repo, "house/profile.yaml", wn_profile(adoption="adoption:\n  level: 1\n  levels_passed:\n"
                                                           "    - {level: 0, on: 2026-01-06}\n"))
    f = wn_facts(repo, network=False)
    case("what-next: levels_passed is reported and sets the standing levels (M3)",
         (f["adoption"]["levels_passed"], f["levels_held"], "L1-gotchas" in f["standing_failures"]),
         ([{"level": 0, "on": "2026-01-06"}], [0], False))
    wn_write(repo, "house/profile.yaml", wn_profile(adoption="adoption:\n  level: 5\n"))
    f = wn_facts(repo, network=False)
    case("what-next: a profile without levels_passed reads 0 through level, at most 3 (M3)",
         (f["levels_held"], f["levels_held_from"].startswith("level")), ([0, 1, 2, 3], True))
    case("what-next: offline, L1-remote is unreadable, not a standing failure (M4)",
         ("L1-remote" in f["standing_failures"], "L1-remote" in [u["id"] for u in f["unreadable"]]), (False, True))
    (repo / "house/docs/gotchas.md").unlink()
    case("what-next: a gotchas file not written yet fails (L1)", wn_res(wn_facts(repo, network=False))["L1-gotchas"],
         "fail")
    (repo / "house/docs/gotchas.md").mkdir()
    case("what-next: a gotchas path that cannot be read is unknown (L1)",
         wn_res(wn_facts(repo, network=False))["L1-gotchas"], "unknown")
    (repo / "house/docs/gotchas.md").rmdir()
    (repo / "house/docs/gotchas.md").write_text(real)
    wn_write(repo, "house/profile.yaml", "kit_version: 2\nsetup: [unclosed\n")
    case("what-next: a profile that is not valid YAML is unknown, not fail (L1)",
         [wn_res(wn_facts(repo, network=False))[k] for k in ("L0-profile", "L1-topics")], ["unknown", "unknown"])
    wn_write(repo, "house/profile.yaml", wn_profile())

    def wn_remote(why):
        rows = wn.level1(repo, {}, "read", True, False, lambda _root: ("no", why))
        return next(c["result"] for c in rows if c["id"] == "L1-remote")
    case("what-next: an unreachable remote, a timeout or a git failure is unknown; refused auth fails (L2)",
         [wn_remote(w) for w in ("git push --dry-run: remote not reachable", "git push --dry-run timed out",
                                 "git failed (OSError)", "git push --dry-run: authentication refused",
                                 "no origin remote")], ["unknown", "unknown", "unknown", "fail", "fail"])
    wn_write(repo, "house/docs/board.md", board.replace(rows, rows + WN_ROW.format(c="NEW-1", t="t", s="IN PROGRESS")))
    case("what-next: an IN PROGRESS row with no date is unknown, naming it (L3)",
         next((c["result"], "NEW-1" in c["evidence"]) for c in wn_facts(repo, network=False)["checks"]
              if c["id"] == "L2-in-progress-age"), ("unknown", True))
    wn_write(repo, "house/docs/board.md", board)
    wn_write(repo, "house/docs/CHANGELOG.md", "# Changelog\n<!-- LAMP-1 FAN-1 TV-1 -->\nLAMP-1, FAN-1 and TV-1 "
                                             "are done.\n\n" + entries + log)
    case("what-next: codes in a comment or outside the dated entries do not count for L2-done-3 (L4)",
         wn_res(wn_facts(repo, network=False))["L2-done-3"], "fail")
    wn_write(repo, "house/docs/CHANGELOG.md", "# Changelog\n\n" + named + entries + log)

    # The log, the output and the read-only promise.
    wn_write(repo, "house/docs/what-next-log.md", "# What next log\n2026-02-01 10:00 | level 1 | write a gotcha | "
                                                 "answer: later\n2026-02-20 10:00 | level 1 | the board | answer: took\n")
    case("what-next: the last log line is read", wn_facts(repo, network=False)["last_log"].endswith("answer: took"), True)
    status = wn_git(repo, "status", "--porcelain", "--ignored").stdout
    import io, contextlib  # noqa: E401,E402
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = wn.main(["--root", str(repo), "--today", "2026-03-01", "--no-network"])
        rc_none = wn.main(["--root", str(td)])
    out = buf.getvalue()
    blob = out.split("--- facts (json) ---\n", 1)[1].split("\n--- end ---", 1)[0] if "--- end ---" in out else "{}"
    case("what-next: main prints the table and a parseable JSON block; exit 0, or 2 outside a house repo",
         (rc, rc_none, "L2-board" in out.split("--- facts")[0], json.loads(blob)["today"]), (0, 2, True, "2026-03-01"))
    case("what-next: the script writes nothing", wn_git(repo, "status", "--porcelain", "--ignored").stdout, status)

    # Path C: the five E0 lines and the tidy-up facts (KIT-EXIST.d; levels.md level 0 and "An existing house",
    # backlog.md's tidy-up section).
    WN_NOW = wn.datetime.date.today().isoformat()

    def e0(f):
        return {c["id"]: c for c in f["checks"] if c["id"].startswith("E0-")}
    f = wn_facts(repo, network=False)
    case("what-next: a house not on path C gets no E0 line and no tidy-up facts",
         (e0(f), f["existing_house"], f["tidy_up"]), ({}, False, None))
    wn_write(repo, "house/profile.yaml", wn_profile(adoption="adoption:\n  level: null\n").replace(
        "  installed_on: 2026-01-05\n", "  installed_on: 2026-01-05\n  existing_house: true\n"
                                         "  inventoried_on: 2026-01-05\n  first_look_on: 2026-01-05\n"))
    f = wn_facts(repo, network=False)
    case("what-next: an existing house gets the five E0 lines at level 0, none written yet",
         sorted((c["id"], c["level"], c["kind"], c["result"]) for c in e0(f).values()),
         [("E0-backup-first", 0, "once", "ask"), ("E0-differs-written", 0, "auto", "fail"),
          ("E0-first-look", 0, "auto", "fail"), ("E0-inventory", 0, "auto", "fail"),
          ("E0-untouched", 0, "auto", "fail")])
    case("what-next: schema v3 is named, and failing E0 lines stop level 0",
         (f["schema"], f["auto_pass_through"]), ("v3", None))
    wn_write(repo, "templates/export/export_house.py", (TEMPLATES / "export/export_house.py").read_text())
    defs = {"automations.json": [{"entity_id": "automation.porch_at_dusk", "id": "1", "name": "Porch at dusk",
                                  "enabled": True, "mode": "single", "config_sha": "aa", "last_triggered": "t1"}],
            "scripts_scenes.json": {"scripts": [], "scenes": [], "status": "ok"},
            "helpers.json": {"helpers": [], "status": "ok"}, "areas.json": [{"area": "Kitchen", "floor": None}],
            "dashboards.json": {"dashboards": [], "status": "ok"},
            "integrations.json": [{"entry_id": "e1", "domain": "hue", "title": "Hue", "state": "loaded"}]}
    for n in wn.INVENTORY_FILES:
        # The profile's last edit is its last commit (wall-clock date here), so the export is stamped today.
        wn_write(repo, f"house/export/{n}", json.dumps(defs.get(n, {"exported": WN_NOW + "T23:59:00"}
                                                          if n == "meta.json" else {})))
    for snap in (".phase0e-start", ".phase0e-end"):
        for n, d in defs.items():
            wn_write(repo, f"house/export/{snap}/{n}", json.dumps(d))
    fired = json.loads(json.dumps(defs["automations.json"]))
    fired[0].update(enabled=False, last_triggered="t2")
    wn_write(repo, "house/export/.phase0e-end/automations.json", json.dumps(fired))
    wn_write(repo, "house/docs/inventory.md", "# Inventory (2026-01-05)\n\nHome Assistant 2026.1\n")
    fl = ("<!-- template comment: | 4. Backups | nothing found | -->\n# First look (2026-01-05)\n\n## The twelve checks\n\n"
          "| Check | Result | Note |\n|---|---|---|\n| 4. Backups: none in 7 days | 1 finding(s) | - |\n"
          "| 5. Logins: multi-factor | unknown | from a computer: ask the owner |\n"
          "| 10. Secrets in YAML | nothing found | - |\n")
    wn_write(repo, "house/docs/first-look.md", fl)
    wn_write(repo, "house/docs/policies.md", "# Policies\n\n## Where this house differs from the kit\n\n"
                                            "| Rule | The house | Why |\n|---|---|---|\n\n## Voice\n\nnone yet\n")
    f = wn_facts(repo, network=False)
    r = {k: c["result"] for k, c in e0(f).items()}
    case("what-next: written inventory, first look and a run automation pass E0; an empty differs table fails",
         [r[k] for k in ("E0-inventory", "E0-first-look", "E0-untouched", "E0-differs-written")],
         ["pass", "pass", "pass", "fail"])
    case("what-next: the export newer than the profile's last edit is not stale",
         ("stale" in e0(f)["E0-inventory"]["evidence"], f"; export {WN_NOW}, profile last edited" in
          e0(f)["E0-inventory"]["evidence"]), (False, True))
    # KIT-EXIST.dr N1: a committed profile is dated by its commit; an uncommitted edit by the file's own date.
    wn_git(repo, "add", "house/profile.yaml")
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm",
                    "profile", "--", "house/profile.yaml"], capture_output=True, text=True, check=True,
                   env={**os.environ, "GIT_COMMITTER_DATE": "2026-01-02T12:00:00+00:00"})
    case("what-next: a committed profile's last edit is its commit date",
         "profile last edited 2026-01-02" in e0(wn_facts(repo, network=False))["E0-inventory"]["evidence"], True)
    wn_write(repo, "house/profile.yaml", (repo / "house/profile.yaml").read_text() + "# an edit not committed yet\n")
    case("what-next: an uncommitted profile edit is dated by the file, not the last commit",
         f"profile last edited {WN_NOW}" in e0(wn_facts(repo, network=False))["E0-inventory"]["evidence"], True)
    wn_write(repo, "house/docs/policies.md", "# Policies\n\n## Where this house differs from the kit\n\nnone yet\n")
    case("what-next: 'none yet' passes E0-differs-written",
         e0(wn_facts(repo, network=False))["E0-differs-written"]["result"], "pass")
    wn_write(repo, "house/docs/policies.md", "# Policies\n\n## Where this house differs from the kit\n\n"
                                            "| Rule | The house | Why |\n|---|---|---|\n| naming | Room - Thing | ten years |\n")
    case("what-next: a row passes E0-differs-written",
         e0(wn_facts(repo, network=False))["E0-differs-written"]["evidence"], "1 row(s)")
    wn_write(repo, "house/docs/policies.md", "# Policies\n\n## 7. Where this house differs from the kit\n\nnone yet\n")
    case("what-next: a numbered 'Where this house differs' heading is the section (KIT-EXIST.dr L1)",
         e0(wn_facts(repo, network=False))["E0-differs-written"]["result"], "pass")
    changed = json.loads(json.dumps(defs["automations.json"]))
    changed[0]["config_sha"] = "bb"
    wn_write(repo, "house/export/.phase0e-end/automations.json", json.dumps(changed))
    c = e0(wn_facts(repo, network=False))["E0-untouched"]
    case("what-next: a changed definition fails E0-untouched and is named",
         (c["result"], "automation.porch_at_dusk changed (config_sha)" in c["evidence"]), ("fail", True))
    wn_write(repo, "house/export/.phase0e-end/automations.json", json.dumps({"source": "person", "status": "unknown"}))
    case("what-next: a person-sourced snapshot file is unknown, never untouched",
         e0(wn_facts(repo, network=False))["E0-untouched"]["result"], "unknown")
    wn_write(repo, "house/export/.phase0e-end/automations.json", json.dumps(fired))
    wn_write(repo, "house/docs/first-look.md", fl.replace("| 5. Logins: multi-factor | unknown | from a computer: ask the owner |\n", ""))
    c = e0(wn_facts(repo, network=False))["E0-first-look"]
    case("what-next: a first look without its login line fails, naming it (and a commented line does not count)",
         (c["result"], "login (5)" in c["evidence"]), ("fail", True))
    wn_write(repo, "house/docs/first-look.md", fl)
    (repo / "house/export/users.json").unlink()
    c = e0(wn_facts(repo, network=False))["E0-inventory"]
    case("what-next: eleven of the twelve inventory files fail E0-inventory, naming the missing one",
         (c["result"], "users.json" in c["evidence"]), ("fail", True))
    wn_write(repo, "house/export/users.json", "{}")
    wn_write(repo, "house/export/meta.json", json.dumps({"exported": "2025-12-01T09:00:00"}))
    c = e0(wn_facts(repo, network=False))["E0-inventory"]
    case("what-next: an export older than the profile's last edit passes but says stale",
         (c["result"], "; stale: export 2025-12-01" in c["evidence"]), ("pass", True))
    wn_write(repo, "house/profile.yaml", wn_profile(adoption="adoption:\n  once_done:\n"
                                                           "    - {check: E0-backup-first, on: 2026-01-05}\n").replace(
        "  installed_on: 2026-01-05\n", "  installed_on: 2026-01-05\n  existing_house: true\n"
                                         "  inventoried_on: 2026-01-05\n"))
    f = wn_facts(repo, network=False)
    case("what-next: a recorded E0-backup-first passes; it does not pass L0-backup-proven",
         (wn_res(f)["E0-backup-first"], wn_res(f)["L0-backup-proven"]), ("pass", "ask"))
    case("what-next: with every E0 line passing, level 0 passes through on an existing house",
         f["auto_pass_through"], 0)
    tidy = ("# Backlog\n\n**Status: the items moved to the board.**\n\n## Tidy-up (optional; the house's old work, one "
            "item at a time)\n\n| Item | From | Change | Undo | Pts | Needs first |\n|---|---|---|---|---|---|\n"
            "| Areas for 12 things | first look 9 | assign | clear | 1 | - |\n| Rename x_2 | first look 9 | rename | "
            "rename back | 1 | - |\n\n### 3. Encrypt backups\n\n## Rulings\n")
    wn_write(repo, "house/docs/backlog.md", tidy)
    f = wn_facts(repo, network=False)
    case("what-next: tidy-up rows are counted for the person, and L2-backlog-moved does not count them",
         (f["tidy_up"]["section"], f["tidy_up"]["rows"], wn_res(f)["L2-backlog-moved"]), ("present", 3, "pass"))
    case("what-next: tidy-up is never a check, and first_ask follows the log",
         ([c["id"] for c in f["checks"] if "tidy" in c["id"].lower()], f["tidy_up"]["first_ask"]), ([], False))
    (repo / "house/docs/what-next-log.md").unlink()
    case("what-next: with no log line yet, the first what-next names the tidy-up section once",
         wn_facts(repo, network=False)["tidy_up"]["first_ask"], True)


# ---------------------------------------------------------------- the second runtime's usage reader (CX-KIT)
# The reply below is the shape a real client (codex-cli 0.166.0) gave on a lab box on 2026-11-08, ids and account
# fields removed; the reader writes the same file as usage_reader.py, so the card and the pace gate read it unchanged.
urc = load(TEMPLATES / "runtime" / "usage_reader_codex.py", "usage_reader_codex")
CX_RESULT = {"ordinaryUsageAllowed": True, "rateLimits": {
    "limitId": "codex", "primary": {"usedPercent": 0, "windowDurationMins": 10080, "resetsAt": 1794771099},
    "secondary": None, "credits": {"hasCredits": False, "unlimited": False, "balance": "0"},
    "spendControlReached": False, "planType": "prolite", "rateLimitReachedType": None}, "rateLimitUpsell": None}
CX_LINES = [{"id": 1, "result": {"userAgent": "x/0.166.0", "platformOs": "linux"}},
            {"method": "account/updated", "params": {"authMode": "chatgpt", "planType": "prolite"}},
            {"id": 2, "result": CX_RESULT}]
CX_NOW = _dt(2026, 11, 9, 16, 0, tzinfo=UTC)


def cx_read(result=CX_RESULT, notices=(), exc=None):
    def f():
        if exc:
            raise exc
        return json.loads(json.dumps(result)), list(notices)
    return f


def cx_with(primary=None, secondary=None, **over):
    r = json.loads(json.dumps(CX_RESULT))
    r["rateLimits"].update(primary=primary, secondary=secondary, **over)
    return r


cx = urc.build({}, UTC, now=CX_NOW, read=cx_read())
case("second reader: the lab reply is ok, weekly window placed, plan read, no models",
     (cx["status"], cx["provider"], cx["week"], cx["session"], cx["models"], cx["plan"]),
     ("ok", "codex", {"pct": 0.0, "resets_at": "2026-11-15T19:31:39+00:00", "severity": None}, None, {}, "prolite"))
case("second reader: the reset is the one the client's status screen showed (13:31 CST on 15 Nov)",
     _dt.fromisoformat(cx["week"]["resets_at"]).astimezone(urc.base._zone("America/Chicago")).strftime("%H:%M %d %b"),
     "13:31 15 Nov")
two = urc.build({}, UTC, now=CX_NOW, read=cx_read(cx_with(
    primary={"usedPercent": 12.5, "windowDurationMins": 300, "resetsAt": 1794240000},
    secondary={"usedPercent": 41, "windowDurationMins": 10080, "resetsAt": 1794771099})))
case("second reader: windows are placed by length, not slot (5-hour and weekly)",
     (two["session"]["pct"], two["week"]["pct"]), (12.5, 41.0))
swapped = urc.build({}, UTC, now=CX_NOW, read=cx_read(cx_with(
    primary={"usedPercent": 41, "windowDurationMins": 10080, "resetsAt": 1794771099},
    secondary={"usedPercent": 12.5, "windowDurationMins": 300, "resetsAt": 1794240000})))
case("second reader: the same with the slots swapped", (swapped["session"]["pct"], swapped["week"]["pct"]),
     (12.5, 41.0))
case("second reader: the plan comes from the account notice when the limits do not name it",
     urc.build({}, UTC, now=CX_NOW, read=cx_read(cx_with(primary=CX_RESULT["rateLimits"]["primary"], planType=None),
                                                 notices=[CX_LINES[1]]))["plan"], "prolite")
later = urc.build(two, UTC, now=CX_NOW + _td(hours=3), read=cx_read(cx_with(
    primary={"usedPercent": 46, "windowDurationMins": 10080, "resetsAt": 1794771099})))
case("second reader: today is the rise since the day's base (usage_reader.py's bookkeeping)",
     (later["today"]["pct"], later["session"]), (5.0, None))
rolled_cx = urc.build(dict(later, week={"pct": 90.0, "resets_at": "2026-11-09T17:00:00+00:00"}), UTC,
                      now=CX_NOW + _td(hours=4), read=cx_read(cx_with(
                          primary={"usedPercent": 1, "windowDurationMins": 10080, "resetsAt": 1795375899})))
case("second reader: a new weekly window is a roll; today carries", (rolled_cx["status"], rolled_cx["day"]["base"]),
     ("ok", 0.0))
only5 = urc.build(cx, UTC, now=CX_NOW + _td(hours=1), read=cx_read(cx_with(
    primary={"usedPercent": 3, "windowDurationMins": 300, "resetsAt": 1794240000})))
case("second reader: no weekly window is unknown, the last good figures kept, nothing guessed",
     (only5["status"], only5["reason"], only5["week"]["pct"], only5["read_at"]),
     ("unknown", "reply shape changed: no weekly window in rateLimits", 0.0, cx["read_at"]))
case("second reader: a reply with no rateLimits is unknown",
     urc.build(cx, UTC, now=CX_NOW, read=cx_read({"accountId": "x"}))["status"], "unknown")
refused = urc.build(cx, UTC, now=CX_NOW, read=cx_read(exc=LookupError("not signed in")))
case("second reader: a JSON-RPC error is error with the client's words, last read kept",
     (refused["status"], refused["reason"], refused["read_at"]),
     ("error", "the Codex client refused the usage read: not signed in", cx["read_at"]))
# CX-KIT.f F2: figures that cannot be true are "unknown", never a fresh read; the last good figures are kept.
for label, prim in (("a negative percentage", {"usedPercent": -1}), ("a percentage over 100", {"usedPercent": 150}),
                    ("a NaN percentage", {"usedPercent": float("nan")}),
                    ("a true/false percentage", {"usedPercent": True}),
                    ("no weekly reset time", {"resetsAt": None}), ("a reset time of 0", {"resetsAt": 0}),
                    ("a reset time past year 9999", {"resetsAt": 1e15}),
                    ("a zero window length", {"windowDurationMins": 0}),
                    ("a fractional window length", {"windowDurationMins": 10080.5})):
    bad = urc.build(cx, UTC, now=CX_NOW + _td(hours=1),
                    read=cx_read(cx_with(primary=dict(CX_RESULT["rateLimits"]["primary"], **prim))))
    case(f"second reader: {label} is unknown, the last good week and read time kept",
         (bad["status"], (bad["reason"] or "").startswith("reply shape changed"), bad["week"], bad["read_at"]),
         ("unknown", True, cx["week"], cx["read_at"]))
bad5 = urc.build(cx, UTC, now=CX_NOW, read=cx_read(cx_with(
    primary=CX_RESULT["rateLimits"]["primary"], secondary={"usedPercent": 101, "windowDurationMins": 300})))
case("second reader: a bad 5-hour figure beside a good weekly one is unknown too",
     (bad5["status"], bad5["reason"]), ("unknown", "reply shape changed: secondary usedPercent is not a percentage"))
case("second reader: a slot that is not an object is unknown",
     urc.build(cx, UTC, now=CX_NOW, read=cx_read(cx_with(primary="10080")))["status"], "unknown")
no5reset = urc.build({}, UTC, now=CX_NOW, read=cx_read(cx_with(
    primary=CX_RESULT["rateLimits"]["primary"], secondary={"usedPercent": 4, "windowDurationMins": 300})))
case("second reader: a 5-hour window may come without a reset time", (no5reset["status"], no5reset["session"]),
     ("ok", {"pct": 4.0, "resets_at": None, "severity": None}))
# CX-KIT.f N2: only the lengths the reader knows are named; a one-day or two-week window is not called anything.
oddlen = urc.build(cx, UTC, now=CX_NOW, read=cx_read(cx_with(
    primary={"usedPercent": 9, "windowDurationMins": 1440, "resetsAt": 1794240000},
    secondary={"usedPercent": 30, "windowDurationMins": 20160, "resetsAt": 1795375899})))
case("second reader: a 1-day and a 2-week window are neither the 5-hour nor the weekly figure",
     (oddlen["status"], oddlen["reason"], oddlen["week"]),
     ("unknown", "reply shape changed: no weekly window in rateLimits", cx["week"]))
withday = urc.build({}, UTC, now=CX_NOW, read=cx_read(cx_with(
    primary={"usedPercent": 9, "windowDurationMins": 1440, "resetsAt": 1794240000},
    secondary=CX_RESULT["rateLimits"]["primary"])))
case("second reader: a 1-day window beside the weekly one is left out, not called the 5-hour figure",
     (withday["status"], withday["session"], withday["week"]["pct"]), ("ok", None, 0.0))
# CX-KIT.f F3: another reader's file is never carried over as this account's figures or day.
other = {"schema": urc.SCHEMA, "provider": "claude", "status": "ok", "plan": "max", "read_at": "2026-11-09T15:40:00+00:00",
         "week": {"pct": 80.0, "resets_at": "2026-11-12T10:00:00+00:00", "severity": None},
         "session": {"pct": 20.0, "resets_at": None, "severity": None}, "models": {"primary": {"pct": 70.0}},
         "today": {"pct": 6.0, "date": "2026-11-09", "since": "2026-11-09T00:00:00+00:00"},
         "day": {"date": "2026-11-09", "base": 74.0, "carried": 0.0, "since": "2026-11-09T00:00:00+00:00"}}
fail_other = urc.build(other, UTC, now=CX_NOW, read=cx_read(exc=OSError("Codex did not answer the usage read in time")))
case("second reader: a failed first read over another reader's file keeps none of its figures",
     (fail_other["provider"], fail_other["status"], fail_other["week"], fail_other["models"], fail_other["plan"],
      fail_other["read_at"], fail_other["day"]),
     ("codex", "error", None, None, None, None, None))
ok_other = urc.build(other, UTC, now=CX_NOW, read=cx_read(cx_with(
    primary={"usedPercent": 10, "windowDurationMins": 10080, "resetsAt": 1794771099})))
case("second reader: a good first read over another reader's file starts the day afresh (no roll, nothing carried)",
     (ok_other["status"], ok_other["models"], ok_other["today"]["pct"], ok_other["day"]["base"],
      ok_other["day"].get("carried")),
     ("ok", {}, 0.0, 10.0, 0.0))
case("second reader: no provider in the previous file is not this reader's either",
     urc.build({k: v for k, v in other.items() if k != "provider"}, UTC, now=CX_NOW,
               read=cx_read(exc=OSError("x")))["week"], None)
case("second reader: its own previous file is still carried",
     urc.build(cx, UTC, now=CX_NOW, read=cx_read(exc=OSError("x")))["week"], cx["week"])

with tempfile.TemporaryDirectory() as t:
    tp = pathlib.Path(t)
    # A fake client: answers initialize, waits for `initialized` and the read, then answers it; logs what it got.
    fake_cx = tp / "codex"
    fake_cx.write_text("#!" + sys.executable + "\n" + """import json, os, sys, time
mode = os.environ.get("FAKE_CX", "ok")
log = open(os.environ["FAKE_CX_LOG"], "a")
log.write(json.dumps({"argv": sys.argv[1:], "home": os.environ.get("CODEX_HOME")}) + "\\n")
for line in sys.stdin:
    msg = json.loads(line)
    log.write(json.dumps(msg.get("method")) + "\\n"); log.flush()
    if mode == "silent":
        time.sleep(30)
    if msg.get("id") == 1:
        print("not json at all" if mode == "garbage" else json.dumps(%s)); sys.stdout.flush()
    if msg.get("method") == "account/rateLimits/read":
        print(json.dumps(%s)); sys.stdout.flush()
        print(json.dumps(%s if mode == "error" else %s)); sys.stdout.flush()
""" % (repr(CX_LINES[0]), repr(CX_LINES[1]), repr({"id": 2, "error": {"code": -32600, "message": "not logged in"}}),
       repr(CX_LINES[2])))
    fake_cx.chmod(0o755)
    flog = tp / "log.txt"
    os.environ["FAKE_CX_LOG"] = str(flog)
    os.environ["FAKE_CX"] = "ok"
    res, notes = urc.read_app_server(str(fake_cx), codex_home=str(tp / "home"), timeout=10)
    sent = [json.loads(x) for x in flog.read_text().splitlines()]
    case("second reader: the real exchange - initialize, initialized, the read; the notice kept; CODEX_HOME passed",
         (res["rateLimits"]["planType"], [n["method"] for n in notes], sent[1:],
          sent[0]["argv"][:1], sent[0]["home"]),
         ("prolite", ["account/updated"], ["initialize", "initialized", "account/rateLimits/read"], ["app-server"],
          str(tp / "home")))
    os.environ["FAKE_CX"] = "error"
    case("second reader: an error reply from the client is error",
         urc.build({}, UTC, now=CX_NOW, read=lambda: urc.read_app_server(str(fake_cx), timeout=10))["status"],
         "error")
    os.environ["FAKE_CX"] = "garbage"
    case("second reader: a line that is not JSON is error",
         urc.build({}, UTC, now=CX_NOW, read=lambda: urc.read_app_server(str(fake_cx), timeout=10))["reason"],
         "Codex answered with a line that is not JSON")
    os.environ["FAKE_CX"] = "silent"
    t0 = time.monotonic()
    slow = urc.build({}, UTC, now=CX_NOW, read=lambda: urc.read_app_server(str(fake_cx), timeout=1))
    case("second reader: a client that never answers is error within the deadline",
         (slow["status"], slow["reason"], time.monotonic() - t0 < 8),
         ("error", "Codex did not answer the usage read in time", True))
    case("second reader: no client at the path is error",
         urc.build({}, UTC, now=CX_NOW, read=lambda: urc.read_app_server(str(tp / "none")))["reason"],
         "cannot start the Codex client (FileNotFoundError); check --codex")
    # main(): --reply takes the transcript or a bare result; writes the file the card reads.
    nd = tp / "08.ndjson"
    nd.write_text("\n".join(json.dumps(x) for x in CX_LINES) + "\n")
    bare = tp / "result.json"
    bare.write_text(json.dumps(CX_RESULT))
    outp = tp / "ha" / "usage.json"
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc1 = urc.main(["--out", str(outp), "--reply", str(nd), "--tz", "UTC"], now=CX_NOW)
        f1 = json.loads(outp.read_text())
        rc2 = urc.main(["--out", str(outp), "--reply", str(bare), "--tz", "UTC"], now=CX_NOW + _td(minutes=20))
        rc3 = urc.main(["--out", str(outp), "--reply", str(tp / "missing.json")], now=CX_NOW)
    case("second reader: main replays a transcript and a bare result, writes the file; a missing file is exit 2",
         (rc1, f1["status"], f1["plan"], rc2, rc3), (0, "ok", "prolite", 0, 2))
    pg = load(TEMPLATES / "pacing" / "pace_gate.py", "pace_gate_cx")
    case("second reader: the pace gate reads the Codex file as it reads the Claude one",
         pg.parse_json(outp.read_text())["sections"]["all models"][0], 0.0)


# ---------------------------------------------------------------- no redirect with the token (KIT-PUBr F4)
def redirect_probe(call):
    """Serve a 302 that points to a second local server, run call(first_url), and return (what the call raised or
    returned, the Authorization header the second server received, or None)."""
    import http.server
    import threading
    seen = []

    class Second(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.headers.get("Authorization"))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *a):
            pass

    second = http.server.HTTPServer(("127.0.0.1", 0), Second)

    class First(Second):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", f"http://localhost:{second.server_port}/elsewhere")
            self.end_headers()

    first = http.server.HTTPServer(("127.0.0.1", 0), First)
    for server in (first, second):
        threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        try:
            result = call(f"http://127.0.0.1:{first.server_port}")
        except (Exception, SystemExit) as e:  # noqa: BLE001 - the export's ReadError is a SystemExit
            result = e
    finally:
        first.shutdown()
        second.shutdown()
    return result, (seen[0] if seen else None)


PLANTED_TOKEN = "planted-token-for-the-redirect-case"  # guard: allow invented fixture value
exr = load(TEMPLATES / "export" / "export_house.py", "export_house_redirect")
got, header = redirect_probe(lambda url: exr.http_fetch(url, PLANTED_TOKEN)("GET", "/api/config"))
case("export: a redirect is refused, names its status only, and the token is not sent on",
     (type(got).__name__, getattr(got, "status", None), "302" in str(got), "127.0.0.1" in str(got), header),
     ("ReadError", 302, True, False, None))
chk = load(TEMPLATES / "tier2" / "checker.py", "checker_redirect")
got, header = redirect_probe(lambda url: chk.api("/api/states", {"url": url, "token": PLANTED_TOKEN}))
case("checker: a redirect is refused and the token is not sent on",
     (getattr(got, "code", None), header), (302, None))
# first_look reads the error log inside its live run; every request there and in the other two files that carries the
# token goes through the no-redirect opener, never urllib.request.urlopen.
for rel in ("export/export_house.py", "export/first_look.py", "tier2/checker.py"):
    source = (TEMPLATES / rel).read_text()
    token_opens = [line for line in source.splitlines() if "urlopen(req" in line]
    case(f"{rel}: no request with the token is opened with urllib.request.urlopen", token_opens, [])
case("first_look: the error log is read through the export's no-redirect opener",
     "exp.OPENER.open(req" in (TEMPLATES / "export" / "first_look.py").read_text(), True)


# ---------------------------------------------------------------- YAML loads


class Loader(yaml.SafeLoader):
    pass


for tag in ("!secret", "!input", "!include", "!include_dir_named", "!env_var"):
    Loader.add_constructor(tag, lambda loader, node: f"<{node.tag} {node.value}>")
for y in sorted(TEMPLATES.rglob("*.yaml")):
    try:
        yaml.load(y.read_text(), Loader=Loader)
        case(f"yaml loads: {y.relative_to(TEMPLATES)}", True, True)
    except yaml.YAMLError as e:
        case(f"yaml loads: {y.relative_to(TEMPLATES)}", str(e), True)

print(f"\n{len(FAILS)} failing" if FAILS else "\nall pass")
sys.exit(1 if FAILS else 0)
