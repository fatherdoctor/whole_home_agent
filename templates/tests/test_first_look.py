#!/usr/bin/env python3
"""test_first_look.py - offline checks of export/first_look.py on the fictional lived-in house.

Status: template (KIT-EXIST.b2, 2026-10-31). Run: python3 templates/tests/test_first_look.py (exit 0 = every case
passes). Standard library only.

The house is examples/lived-in-house.md, from its seed fixture and its paste-ready seed (rendered with the fake
planted password). The export is built with the fakes of test_export_existing.py (KIT-EXIST.b1), inside the add-on
and from a computer, then the first look runs offline on it. The cases (KIT-EXIST design section 8): every planted
fault a check catches is found by its check (section 10's key), nothing that is not planted fires, faults 2 and 4
are left to the interview and the inventory, checks 5 and 10 answer `unknown` from a computer, and no planted
secret, error text or user's name reaches first-look.md, inventory.md or stdout. Then the parts one by one: a script
followed one level, a blueprint followed, a recovered entity not reported, a Supervisor 403, a freeze, the stable
probe; an automation outside automations.yaml (read by the config GET, or a partial note), the history
read in chunks, a hand-indented automations.yaml.
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE.parents[1]
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


tx = load(HERE / "test_export_existing.py", "test_export_existing")  # the b1 fakes; its cases run only as a script
exp = tx.exp
fl = load(HERE.parent / "export" / "first_look.py", "first_look")
seed = load(KIT / "examples" / "lived-in-house" / "render_seed.py", "render_seed")
FX = tx.FX
SECRETS = tx.SECRETS + tx.EXTRA_SECRETS
TRACE_TEXT = "fake-trace-variable-4417"  # guard: allow a planted fake, also in the fixture

# The b1 fakes add a second "House mode" helper for the export's own cases; it is not part of the seeded house.
_states = tx.fake_states
tx.fake_states = lambda fired=None: [s for s in _states(fired) if s["entity_id"] != "input_select.export_test_mode"]

EXPECTED = {  # check: the items it must name on the fixture (section 10's key, faults 1-16 but 2 and 4)
    1: ["sensor.seed_unavailable_sensor"],                                              # fault 14
    2: ["automation.seed_bedroom_night_dim"],                                           # fault 9
    3: ["automation.seed_garage_close_night", "automation.seed_midnight_off"],          # faults 7, 8
    4: ["No backup in the last 7 days", "No backup off the box"],                       # faults 11, 10
    5: ["More than one administrator", "Multi-factor login off for the owner"],         # faults 15, 12
    6: ["core"],                                                                        # fault 16
    8: ["automation.seed_battery_tell_tablet", "automation.seed_door_tell_phone"],      # fault 5
    9: ["Duplicate names and ids ending in _2", "Things with no area"],                 # faults 3, 1
    10: ["packages/seed.yaml"],                                                         # fault 13
    12: ["automation.seed_leaving_arm_away"],                                           # fault 6
}


def named(results):
    """check -> what its findings name: titles for 4, 5, 9; files for 10; items otherwise."""
    out = {}
    for r in results:
        for f in r["findings"]:
            if r["check"] in (4, 5, 9):
                out.setdefault(r["check"], []).append(f["title"])
            elif r["check"] == 10:
                out.setdefault(10, []).extend(sorted({i.split(":")[0] for i in f["items"]}))
            else:
                out.setdefault(r["check"], []).extend(f["items"])
    return {k: sorted(v) for k, v in out.items()}


def history():
    """The fixture's 24 hours, in the shape GET /api/history/period answers (minimal_response)."""
    return [[{"entity_id": e, "state": r["state"], "last_changed": r["start"]} for r in rows]
            for e, rows in FX["history_24h"].items()]


ERROR_LOG = "\n".join([
    "2026-11-10 06:00:00.000 INFO (MainThread) [homeassistant.components.automation.seed_porch_sunset] "
    "Running automation actions",
    "2026-11-10 06:00:01.000 ERROR (MainThread) [homeassistant.components.automation.seed_bedroom_night_dim] "
    f"Error while executing automation automation.seed_bedroom_night_dim: ValueError {TRACE_TEXT}",
])


def api_configs():
    """GET /api/config/automation/config/<id> for each automation, with the seed's real actions where it matters."""
    cfgs = tx.automation_configs()
    cfgs["seed_door_tell_phone"]["actions"] = [{"action": "notify.mobile_app_alex_phone", "data": {"message": "x"}}]
    cfgs["seed_battery_tell_tablet"]["actions"] = [{"action": "notify.mobile_app_alex_tablet"}]
    cfgs["seed_leaving_arm_away"]["actions"] = [{"action": "alarm_control_panel.alarm_arm_away",
                                                 "target": {"entity_id": "alarm_control_panel.security"}}]
    cfgs["seed_good_night_button"]["actions"] = [{"action": "script.turn_on",
                                                  "target": {"entity_id": "script.good_night"}}]
    return cfgs


def first_look(folder, config=None, live=None, extra=()):
    (pathlib.Path(folder) / "live.json").write_text(json.dumps(live or {}))
    out = pathlib.Path(folder).parent / "docs"
    args = ["--offline", str(folder), "--out", str(out), "--inventory"] + (["--config", str(config)] if config else [])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fl.main(args + list(extra))
    export = fl.load_export(folder)
    ctx = fl.context(export, json.loads((pathlib.Path(folder) / "live.json").read_text()), config and str(config))
    return rc, fl.run_checks(ctx), (out / "first-look.md").read_text(), (out / "inventory.md").read_text(), \
        buf.getvalue()


def leaked(*texts):
    blob = "\n".join(texts)
    return sorted(s for s in SECRETS + [TRACE_TEXT, "Sam", "Alex", "Error while executing", "ValueError"]
                  if s in blob)


with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)

    # ---- inside the add-on: the configuration folder (with .storage and the rendered seed) and the Supervisor
    root = tx.make_config_dir(tmp / "addon")
    seed.render(root)
    (root / "configuration.yaml").write_text((root / "configuration.addition.yaml").read_text())
    sources = {"mode": "addon", "config_dir": str(root), "storage": exp.storage_reader(root),
               "supervisor": tx.make_supervisor()}
    a_dir = tmp / "addon" / "house" / "export"
    tx.run(sources, out=a_dir)
    live = {"now": FX["now"], "mode": "addon", "states": tx.fake_states(), "history": history(),
            "error_log": ERROR_LOG}
    code, res, page, inv, out = first_look(a_dir, root, live)
    case("add-on: exit 0 and the page written", code, 0)
    case("add-on: every planted fault a check catches, by its check (faults 1, 3, 5-16)", named(res), EXPECTED)
    case("add-on: nothing unplanted - check 7 and check 11 find nothing",
         [r["status"] for r in res if r["check"] in (7, 11)], ["clean", "ask"])
    case("add-on: no check unknown", [r["check"] for r in res if r["status"] == "unknown"], [])
    case("add-on: check 12's finding is marked safety", [f["safety"] for r in res for f in r["findings"]
                                                          if r["check"] == 12], [True])
    case("add-on: kinds - faults 1 and 2, risks 4 5 10 12, notices 3 6 8 9",
         sorted({(r["check"], f["kind"]) for r in res for f in r["findings"]}),
         [(1, "fault"), (2, "fault"), (3, "notice"), (4, "risk"), (5, "risk"), (6, "notice"), (8, "notice"),
          (9, "notice"), (10, "risk"), (12, "risk")])
    case("add-on: fault 2 (the Away word) is not a first-look finding", "house_mode" in page, False)
    case("add-on: fault 4 is the inventory's: no single naming pattern", "no single pattern" in inv, True)
    case("inventory uses current app labels", "## Dashboards, apps, backups, users" in inv and "- Apps:" in inv, True)
    case("inventory does not claim Marketplace repository coverage", "Marketplace repositories not inventoried" in inv, True)
    case("add-on: the first look does not name the naming pattern", "pattern" in page.lower(), False)
    case("add-on: the secrets line names file and line, never the value",
         [i for r in res if r["check"] == 10 for f in r["findings"] for i in f["items"]],
         [f"packages/seed.yaml:{n} (literal secret)" for n, ln in enumerate(
             (root / "packages" / "seed.yaml").read_text().splitlines(), 1) if "password:" in ln])
    case("add-on: no planted secret, error text or name in first-look.md, inventory.md or stdout",
         leaked(page, inv, out), [])
    case("add-on: the page holds the backup, login and secrets lines (E0-first-look)",
         all(f"| {n}. " in page for n in (4, 5, 10)), True)
    case("add-on: the page says nothing was changed", "Nothing on the box was changed" in page, True)
    case("add-on: stdout counts", out.split(" -> ")[0], "first look: 2 faults, 6 risks, 5 notices")
    case("add-on: the template's comment is dropped", "<!--" in page or "<!--" in inv, False)

    # ---- from a computer: the websocket, no configuration folder; definitions from the API
    sources = {"mode": "computer", "ws": tx.make_ws()}
    c_dir = tmp / "computer" / "house" / "export"
    tx.run(sources, configs=api_configs(), out=c_dir)
    traces = [{"automation": f"automation.{k}", "error": k == "seed_bedroom_night_dim"} for k in api_configs()]
    live = {"now": FX["now"], "mode": "computer", "states": tx.fake_states(), "history": history(),
            "error_log": ERROR_LOG, "traces": traces, "automation_configs": api_configs(), "script_configs": {}}
    code, res, page, inv, out = first_look(c_dir, None, live)
    status = {r["check"]: r["status"] for r in res}
    case("computer: checks 5 and 10 answer unknown, 11 asks", (status[5], status[10], status[11]),
         ("unknown", "unknown", "ask"))
    case("computer: the unknowns say what would let them read",
         all("--config" in (r["why"] or "") for r in res if r["check"] in (5, 10)), True)
    case("computer: check 5 offers the owner-only question", "owner alone" in (res[4]["ask"] or ""), True)
    want = {k: v for k, v in EXPECTED.items() if k not in (5, 10)}
    case("computer: the other planted faults, by the same checks", named(res), want)
    case("computer: no planted secret, error text or name anywhere", leaked(page, inv, out), [])
    case("computer: stdout names the unknown checks", "unknown: checks 5, 10" in out, True)

    # ---- the parts
    a = fl.parse_automations_yaml((root / "automations.yaml").read_text())
    case("parse: 14 automations from the seed", len(a), 14)
    case("parse: the blueprint automation's path", a["seed_blueprint_hall_motion"]["blueprint"],
         "homeassistant/motion_light.yaml")
    case("parse: a script.turn_on target is a script run", a["seed_good_night_button"]["scripts"], ["good_night"])
    s = fl.parse_scripts_yaml((root / "scripts.yaml").read_text())
    case("parse: 3 scripts", sorted(s), ["good_night", "movie_time", "porch_blink"])

    def safety_with(auto_yaml, scripts_yaml="", blueprint=None):
        d = tmp / f"cfg{len(list(tmp.iterdir()))}"
        d.mkdir()
        (d / "automations.yaml").write_text(auto_yaml)
        (d / "scripts.yaml").write_text(scripts_yaml)
        if blueprint:
            bp = d / "blueprints" / "automation" / "someone"
            bp.mkdir(parents=True)
            (bp / "arm.yaml").write_text(blueprint)
        ctx = {"config_dir": str(d), "definitions": fl.definitions({"automations.json": []}, str(d))}
        r = fl.check_safety(ctx)
        return [f["evidence"] for f in r["findings"]], r["note"]

    ev, _ = safety_with("- id: leave\n  alias: Leave\n  actions:\n    - action: script.leave_house\n",
                        "leave_house:\n  sequence:\n    - action: alarm_control_panel.alarm_disarm\n"
                        "      target: {entity_id: alarm_control_panel.x}\n")
    case("check 12 follows a script.* call one level",
         ev, ["automation.leave: alarm_control_panel.alarm_disarm via script.leave_house, "
              "automated (no confirmation step read)"])
    ev, _ = safety_with("- id: bp\n  use_blueprint:\n    path: someone/arm.yaml\n    input: {}\n",
                        blueprint="blueprint:\n  name: Arm\naction:\n  - service: lock.unlock\n")
    case("check 12 follows a blueprint into its actions",
         ev, ["automation.bp: lock.unlock via blueprint someone/arm.yaml, automated (no confirmation step read)"])
    ev, note = safety_with("- id: bp\n  use_blueprint:\n    path: other/missing.yaml\n")
    case("check 12 says when a blueprint could not be read", (ev, "other/missing.yaml" in note), ([], True))
    ev, note = safety_with("- id: t\n  alias: Lock code\n  actions:\n    - action: zwave_js.set_lock_usercode\n")
    case("check 12 finds a code change", len(ev), 1)
    case("check 12 asks about a person-set code window", "code window" in note and "person" in note, True)
    ev, note = safety_with("- id: t\n  actions:\n    - action: script.window\n",
                           "window:\n  sequence:\n    - action: zwave_js.clear_code\n")
    case("check 12 asks about a code window via a script", len(ev) == 1 and "code window" in note, True)

    # ---- KIT-EXIST.b2r M1: an automation outside automations.yaml (a package) that arms the alarm
    p_dir = tmp / "package" / "house" / "export"
    p_dir.mkdir(parents=True)
    for f in a_dir.glob("*.json"):
        (p_dir / f.name).write_text(f.read_text())
    rows = json.loads((p_dir / "automations.json").read_text())
    rows.append({"entity_id": "automation.seed_package_leaving_arm", "id": "seed_package_leaving_arm",
                 "name": "Package leaving arm", "enabled": True})
    (p_dir / "automations.json").write_text(json.dumps(rows))
    live = {"now": FX["now"], "mode": "addon", "states": tx.fake_states(), "history": history(),
            "error_log": ERROR_LOG}
    _, res, page, _, _ = first_look(p_dir, root, live)
    r8, r12 = res[7], res[11]
    case("package, not read: checks 8 and 12 carry a partial note, not \"nothing found\"",
         ("partial: 1 automation(s) outside automations.yaml not read" in (r8["note"] or ""),
          "partial: 1 automation(s) outside automations.yaml not read" in (r12["note"] or ""),
          r12["findings"][0]["items"]), (True, True, ["automation.seed_leaving_arm_away"]))
    case("package, not read: the note reaches the page", "outside automations.yaml not read" in page, True)
    live["automation_configs"] = {"seed_package_leaving_arm": {
        "actions": [{"action": "alarm_control_panel.alarm_arm_away",
                     "target": {"entity_id": "alarm_control_panel.house"}}]}}
    _, res, _, _, _ = first_look(p_dir, root, live)
    case("package, read by the config GET: check 12 catches it, no partial note",
         ([i for f in res[11]["findings"] for i in f["items"]], "partial" in (res[11]["note"] or "")),
         (["automation.seed_leaving_arm_away", "automation.seed_package_leaving_arm"], False))
    case("package, read: the definitions say files+api", fl.context(fl.load_export(p_dir), live, str(root))
         ["definitions"]["source"], "files+api")

    # ---- the live reads (a fake export_house): only what the files lack is fetched; history in chunks of fifty
    calls = []

    class FakeExp:
        ReadError = type("ReadError", (Exception,), {})

        @staticmethod
        def http_fetch(base, token):
            def fetch(method, path, body=None):
                calls.append(path)
                if path == "/api/states":
                    return [{"entity_id": f"sensor.dead_{i}", "state": "unavailable"} for i in range(120)]
                if path.startswith("/api/history/period/"):
                    ids = path.split("filter_entity_id=", 1)[1].split("&", 1)[0].split(",")
                    return [[{"entity_id": e, "state": "unavailable"}] for e in ids]
                if path == "/api/config/automation/config/seed_package_leaving_arm":
                    return live["automation_configs"]["seed_package_leaving_arm"]
                raise OSError("404")
            return fetch

        @staticmethod
        def trace_errors(reader):
            return []

        @staticmethod
        def storage_reader(d):
            return None

        class OPENER:  # the export's no-redirect opener, offline here as urlopen is below
            @staticmethod
            def open(*a, **k):
                raise OSError("offline")

    real_load, real_open = fl.load_module, fl.urllib.request.urlopen
    fl.load_module = lambda path, name: FakeExp
    fl.urllib.request.urlopen = lambda *a, **k: (_ for _ in ()).throw(OSError("offline"))
    try:
        got = fl.gather_live(fl.load_export(p_dir), "http://ha.invalid", "x", str(root), "addon",
                             fl.when(FX["now"]))
    finally:
        fl.load_module, fl.urllib.request.urlopen = real_load, real_open
    hist_calls = [c for c in calls if c.startswith("/api/history/period/")]
    case("L1: 120 down entities read in three history queries of at most fifty",
         ([c.count(",") + 1 for c in hist_calls], len(got["history"])), ([50, 50, 20], 120))
    case("M1: the config GET only for the automation automations.yaml does not hold",
         [c for c in calls if c.startswith("/api/config/automation/")],
         ["/api/config/automation/config/seed_package_leaving_arm"])
    case("M1: no script GET when scripts.yaml holds every script",
         [c for c in calls if c.startswith("/api/config/script/")], [])

    # ---- KIT-EXIST.b2r L2: a hand-indented automations.yaml parses as one block -> the API reads
    d = tmp / "indented"
    d.mkdir()
    (d / "automations.yaml").write_text("  - id: a1\n    actions:\n      - action: light.turn_on\n"
                                        "  - id: a2\n    actions:\n      - action: lock.unlock\n")
    two = {"automations.json": [{"entity_id": "automation.a1", "id": "a1"}, {"entity_id": "automation.a2", "id": "a2"}]}
    defs = fl.definitions(two, str(d))
    case("L2: one block for two automations is not trusted; both unread, with why",
         (defs["automations"], defs["unread"]["automations"], "one block" in fl.unread_note(defs)),
         ({}, ["automation.a1", "automation.a2"], True))
    defs = fl.definitions(two, str(d), {"a1": {"actions": [{"action": "light.turn_on"}]},
                                        "a2": {"actions": [{"action": "lock.unlock"}]}})
    case("L2: the API reads put each call on its own automation",
         [f["items"] for f in fl.check_safety({"definitions": defs})["findings"]], [["automation.a2"]])

    base = {"export": {"entities.json": [{"entity_id": "sensor.a", "integration": "x", "device_name": "A"}]},
            "now": fl.when(FX["now"])}
    recovered = dict(base, states=[{"entity_id": "sensor.a", "state": "unavailable",
                                    "last_changed": "2026-11-10T09:30:00+00:00"}],
                     history={"sensor.a": [{"state": "on", "last_changed": "2026-11-09T09:00:00+00:00"},
                                           {"state": "unavailable", "last_changed": "2026-11-10T09:30:00+00:00"}]})
    case("check 1: down for half an hour is not a finding", fl.check_down(recovered)["findings"], [])
    old = dict(base, states=[{"entity_id": "sensor.a", "state": "unavailable",
                              "last_changed": "2026-11-08T00:00:00+00:00"}], history=None)
    case("check 1: without history, last_changed over a day old", len(fl.check_down(old)["findings"]), 1)
    case("check 1: no states read answers unknown", fl.check_down(dict(base, states=None))["status"], "unknown")

    sources = {"mode": "addon", "config_dir": str(root), "storage": exp.storage_reader(root),
               "supervisor": tx.make_supervisor(forbid=("/backups", "/addons"))}
    f_dir = tmp / "forbid" / "house" / "export"
    tx.run(sources, out=f_dir)
    ctx = fl.context(fl.load_export(f_dir), {"now": FX["now"]}, str(root))
    case("a Supervisor 403: checks 4 and 7 answer unknown, not clean",
         (fl.check_backups(ctx)["status"], fl.check_addons(ctx)["status"]), ("unknown", "unknown"))

    prof = tmp / "profile.yaml"
    prof.write_text("operations:\n  freezes:\n    - {from: 2026-11-05, to: 2026-11-15, why: trip}\n  staging: null\n")
    ctx = fl.context(fl.load_export(a_dir), {"now": FX["now"]}, str(root), str(prof))
    case("check 7: auto-update during a declared freeze", fl.check_addons(ctx)["findings"][0]["items"],
         ["core_configurator", "core_ssh"])
    prof.write_text("operations:\n  freezes: []\n")
    case("check 7: no freeze, nothing", fl.check_addons(dict(ctx, profile=str(prof)))["findings"], [])

    meta = {"version": "2026.10.3", "versions": {}}
    ctx = {"export": {"meta.json": meta}, "now": fl.when(FX["now"]),
           "stable": {"homeassistant": {"default": "2026.11.1"}, "supervisor": "2026.11.0", "hassos": {"ova": "17.0"}}}
    case("check 6: the stable probe when the update entities are missing",
         fl.check_versions(ctx)["findings"][0]["items"], ["core"])
    case("check 6: neither source answers unknown", fl.check_versions(dict(ctx, stable=None))["status"], "unknown")

    case("check 4: encryption off is a finding", [f["title"] for f in fl.check_backups(
        {"export": {"backups.json": {"status": "ok", "backups": [{"date": FX["now"], "locations": ["Nabu Casa"]}],
                                     "settings": {"source": "storage", "encrypted": False, "locations": []}}},
         "now": fl.when(FX["now"])})["findings"]], ["Backups not encrypted"])

    case("naming: two in three is the house's pattern",
         fl.naming_pattern(["Motion - A", "Motion - B", "x_y"])[0].startswith("most names follow `Category - Target`"),
         True)

    rc = fl.main(["--offline", str(tmp / "empty")])
    case("no export: exit 2", rc, 2)

print("all pass" if not FAILS else f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
