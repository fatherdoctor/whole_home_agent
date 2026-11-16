#!/usr/bin/env python3
"""test_export_existing.py - offline checks of the existing-house inventory in export/export_house.py.

Status: template (KIT-EXIST.b1, 2026-10-31). Run: python3 templates/tests/test_export_existing.py (exit 0 = every
case passes). Standard library only.

The house is the fictional lived-in house of examples/lived-in-house.md, read from its seed fixture
(examples/lived-in-house/seed-fixture.json): its states, registry, dashboards, add-ons, backups and the four planted
fake secrets in .storage (a password hash, a TOTP secret, a backup password, a trace variable, plus fake refresh
tokens). The fakes below give those back in the shapes Home Assistant, the Supervisor and the websocket API use, and
the cases check (KIT-EXIST design section 8): the twelve files; identical snapshots diff empty; one fired automation
diffs empty; one changed automation does not; a person-sourced file answers unknown; no planted secret reaches any
file or stdout, inside the add-on or from a computer; a Supervisor 403 answers unknown, not "none"; the trace
reader keeps the automation and the error flag only; the websocket client speaks the protocol.
"""
import base64
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import pathlib
import socket
import struct
import sys
import tempfile
import threading
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE.parents[1]
FIXTURE = KIT / "examples" / "lived-in-house" / "seed-fixture.json"

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


exp = load(HERE.parent / "export" / "export_house.py", "export_house")
FX = json.loads(FIXTURE.read_text())
NOW = datetime.fromisoformat(FX["now"])
SECRETS = FX["planted_secrets"]
EXTRA_SECRETS = ["fake-card-api-key-5501", "fake-mount-password-7781"]  # guard: allow fake planted secrets


# ---------------------------------------------------------------- the fake box, from the fixture
def automation_configs():
    """One UI config per automation (the shape GET /api/config/automation/config/<id> returns)."""
    out = {}
    for s in FX["states"]:
        e = s["entity_id"]
        if e.startswith("automation."):
            oid = e.split(".", 1)[1]
            cfg = {"id": oid, "alias": s["attributes"].get("friendly_name"), "mode": "single",
                   "triggers": [{"trigger": "state", "entity_id": "binary_sensor.x"}], "actions": []}
            for bp in FX["blueprints"]:
                if e in bp["used_by"]:
                    cfg = {"id": oid, "alias": cfg["alias"],
                           "use_blueprint": {"path": bp["path"], "input": {"motion": "binary_sensor.x"}}}
            out[oid] = cfg
    return out


def fake_states(fired=None):
    rows = []
    for s in copy.deepcopy(FX["states"]):
        e = s["entity_id"]
        if e.startswith("automation."):
            s["attributes"].update({"id": e.split(".", 1)[1], "mode": "single",  # the fixture's last run, kept
                                    "last_triggered": s["attributes"].get("last_triggered",
                                                                          "2026-10-30T15:10:00+00:00")})
            if e == fired:
                s["attributes"]["last_triggered"] = "2026-11-09T09:20:00+00:00"
                s["state"] = "on"
                s["last_changed"] = "2026-11-09T09:20:00+00:00"
        if e.startswith("script."):
            s["attributes"].update({"mode": "single", "last_triggered": None})
            if fired == e:
                s["state"] = "on"
        rows.append(s)
    rows.append({"entity_id": "input_select.export_test_mode", "state": "Home",
                 "attributes": {"friendly_name": "House mode", "options": ["Home", "Away"]}})
    rows.append({"entity_id": "input_text.gate_note", "state": "Plant3d-Pass-2026",  # guard: allow fake secret
                 "attributes": {"friendly_name": "Gate note", "mode": "password", "max": 100}})
    rows.append({"entity_id": "update.home_assistant_core_update", "state": "on",
                 "attributes": {"friendly_name": "Core update", "installed_version": FX["meta"]["core_version"],
                                "latest_version": FX["meta"]["stable_core_version"]}})
    return rows


def fake_registry():
    dev = {d["entity_id"]: d for d in FX["devices"]}
    area_floor = {a["area_id"]: a.get("floor") for a in FX["areas"]}
    ents = []
    for s in fake_states():
        d = dev.get(s["entity_id"])
        ents.append({"entity_id": s["entity_id"], "area": d and d["area_id"],
                     "floor": d and area_floor.get(d["area_id"]), "device": d and d["device_id"],
                     "device_name": d and d["name"], "labels": [],
                     "integration": "demo" if d else ("hacs" if s["entity_id"].startswith("update.hacs") else None)})
    areas = [{"area": a["area_id"], "name": a["name"], "floor": a.get("floor"),
              "entities": sum(1 for d in FX["devices"] if d["area_id"] == a["area_id"])} for a in FX["areas"]]
    return {"entities": ents, "areas": areas}


def script_configs():
    """One UI config per script (GET /api/config/script/config/<object id>): the fixture's scripts are UI scripts."""
    return {s["entity_id"].split(".", 1)[1]: {"alias": s["attributes"].get("friendly_name"), "sequence": []}
            for s in FX["states"] if s["entity_id"].startswith("script.")}


def make_fetch(fired=None, configs=None, entry_state="loaded", scripts=None, forbid_config=False):
    configs = configs if configs is not None else automation_configs()
    scripts = scripts if scripts is not None else script_configs()
    entries = [{"entry_id": f"E{i}", "domain": c["domain"], "title": c.get("title", c["domain"]),
                "state": entry_state, "disabled_by": None} for i, c in enumerate(FX["config_entries"])]

    def fetch(method, path, body=None):
        if (method, path) == ("GET", "/api/config"):
            return {"version": FX["meta"]["core_version"], "time_zone": FX["meta"]["time_zone"],
                    "unit_system": {"temperature": "°C"}}
        if (method, path) == ("GET", "/api/states"):
            return fake_states(fired)
        if (method, path) == ("GET", "/api/config/config_entries/entry"):
            return entries
        if (method, path) == ("POST", "/api/template"):
            return json.dumps(fake_registry())
        if method == "GET" and path.startswith("/api/config/") and forbid_config:
            raise exp.ReadError("403", 403)  # a token that is not an administrator's
        if method == "GET" and path.startswith("/api/config/automation/config/"):
            oid = path.rsplit("/", 1)[1]
            if oid in configs:
                return configs[oid]
            raise exp.ReadError("404", 404)
        if method == "GET" and path.startswith("/api/config/script/config/"):
            oid = path.rsplit("/", 1)[1]
            if oid in scripts:
                return scripts[oid]
            raise exp.ReadError("404", 404)
        raise AssertionError(f"the export asked for something not read-only or unexpected: {method} {path}")

    return fetch


def lovelace_storage(summary):
    """A stored dashboard config with the fixture's counts; one card carries a planted key a card config can hold."""
    views, types = [], list(summary["card_types"])
    per = [summary["cards"] // summary["views"]] * summary["views"]
    per[0] += summary["cards"] - sum(per)
    for n in per:
        views.append({"title": "v", "cards": [{"type": types[i % len(types)]} for i in range(n)]})
    views[0]["cards"][0]["api_key"] = EXTRA_SECRETS[0]
    return {"version": 1, "key": "lovelace", "data": {"config": {"views": views}}}


def make_config_dir(tmp, totp_as_dict=False):
    root = pathlib.Path(tmp) / "config"
    st = root / ".storage"
    st.mkdir(parents=True)
    storage = copy.deepcopy(FX["storage"])
    if totp_as_dict:  # Home Assistant's real shape: {user_id: secret}
        storage["auth_module.totp"]["data"]["users"] = {
            u["user_id"]: u["secret"] for u in storage["auth_module.totp"]["data"]["users"]}
    for name, doc in storage.items():
        (st / name).write_text(json.dumps(doc))
    dashes = FX["lovelace"]["dashboards"]
    items = []
    for d in dashes:
        if d["url_path"] is None:
            (st / "lovelace").write_text(json.dumps(lovelace_storage(d)))
        else:
            did = d["url_path"].replace("-", "_")
            items.append({"id": did, "url_path": d["url_path"], "title": d["title"], "mode": d["mode"]})
            (st / ("lovelace." + did)).write_text(json.dumps(lovelace_storage(d)))
    (st / "lovelace_dashboards").write_text(json.dumps({"data": {"items": items}}))
    hacs = {str(i): {"full_name": r["full_name"], "category": r["category"], "installed": r["installed"],
                     "authors": ["someone"], "etag_repository": "x"} for i, r in enumerate(FX["hacs_repositories"])}
    (st / "hacs.repositories").write_text(json.dumps({"data": hacs}))
    bp = root / "blueprints" / "automation" / "homeassistant"
    bp.mkdir(parents=True)
    (bp / "motion_light.yaml").write_text("blueprint:\n  name: Motion light\n")
    return root


def make_supervisor(forbid=()):
    sup = FX["supervisor"]

    def get(path):
        if any(path.startswith(p) for p in forbid):
            raise exp.ReadError("403", 403)
        if path == "/addons":
            return {"addons": [{"slug": a["slug"], "name": a["name"], "version": a["version"],
                                "state": a["state"]} for a in sup["addons"]]}
        if path.startswith("/addons/") and path.endswith("/info"):
            slug = path.split("/")[2]
            a = next(x for x in sup["addons"] if x["slug"] == slug)
            return {**a, "options": {"password": EXTRA_SECRETS[1]}}  # guard: allow test fixture, not a value
        if path == "/backups":
            return {"backups": [{"slug": b["slug"], "name": "seed", "date": b["date"], "type": b["type"],
                                 "size": b["size_mb"], "locations": [None], "protected": b["protected"]}
                                for b in sup["backups"]]}
        if path == "/mounts":
            return {"mounts": [{"name": "nas", "usage": "backup", "type": "cifs", "username": "x",
                                "password": EXTRA_SECRETS[1]}]}  # guard: allow a planted fake, by name
        raise AssertionError("unexpected Supervisor path " + path)

    return get


def make_ws(admin=True):
    stored = {d["url_path"]: lovelace_storage(d)["data"]["config"] for d in FX["lovelace"]["dashboards"]}
    backup_cfg = copy.deepcopy(FX["storage"]["backup"]["data"])

    def ws(msg):
        t = msg["type"]
        assert t in exp.WS_READS, t
        if not admin:
            raise exp.ReadError("unauthorized", "unauthorized")
        if t == "lovelace/dashboards/list":
            return [{"id": d["url_path"].replace("-", "_"), "url_path": d["url_path"], "title": d["title"],
                     "mode": "storage"} for d in FX["lovelace"]["dashboards"] if d["url_path"]]
        if t == "lovelace/config":
            return stored[msg.get("url_path")]
        if t == "backup/info":
            return {"backups": [{"backup_id": "b1", "date": b["date"], "name": "seed",
                                 "agents": {"hassio.local": {"protected": False, "size": 117440512}}}
                                for b in FX["supervisor"]["backups"]]}
        if t == "backup/config/info":
            return backup_cfg  # holds create_backup.password, as the real command does
        if t == "supervisor/api":
            return make_supervisor()(msg["endpoint"])
        if t == "blueprint/list":
            return {"homeassistant/motion_light.yaml": {"metadata": {"name": "Motion light"}}} \
                if msg["domain"] == "automation" else {}
        raise AssertionError(t)

    return ws


def run(sources, fired=None, configs=None, out=None, snap=None, **fetch_kw):
    files = exp.build(make_fetch(fired, configs, **fetch_kw), now=NOW, sources=sources)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exp.run_report(files, out, snap)
    return files, buf.getvalue()


def leaks(texts):
    blob = "\n".join(texts)
    return sorted(s for s in SECRETS + EXTRA_SECRETS if s in blob)


def all_text(folder):
    return [p.read_text() for p in pathlib.Path(folder).rglob("*.json")]


NEW = ["addons.json", "backups.json", "blueprints.json", "dashboards.json", "helpers.json", "scripts_scenes.json",
       "users.json"]
OLD = ["areas.json", "automations.json", "entities.json", "integrations.json", "meta.json"]

def main():
    """The cases; run as a script. test_first_look.py imports this module for its fakes only."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        cfg = make_config_dir(tmp)
        addon = {"mode": "addon", "config_dir": str(cfg), "storage": exp.storage_reader(cfg),
                 "supervisor": make_supervisor()}

        # ---- inside the add-on
        files, stdout = run(addon, out=tmp / "export", snap="phase0e-start")
        case("add-on: the twelve inventory files", sorted(files), sorted(NEW + OLD))
        case("add-on: no planted secret in any file or stdout", leaks(all_text(tmp / "export") + [stdout]), [])
        case("add-on: no input_text value in helpers.json",
             [h for h in files["helpers.json"]["helpers"] if h["entity_id"] == "input_text.gate_note"],
             [{"entity_id": "input_text.gate_note", "domain": "input_text", "name": "Gate note", "area": None}])
        case("add-on: an input_select keeps its options as its definition",
             [h.get("options") for h in files["helpers.json"]["helpers"] if h["entity_id"] == "input_select.export_test_mode"],
             [["Home", "Away"]])
        u = files["users.json"]
        case("add-on: users are counts and booleans by role, never names",
             {k: u[k] for k in ("users", "administrators", "owner", "other_administrators")},
             {"users": 2, "administrators": 2, "owner": {"administrator": True, "mfa": False},
              "other_administrators": {"count": 1, "with_mfa": 1}})
        case("add-on: the administrators' names are never written", [n for n in ("Alex", "Sam", "alex")
                                                                    if n in json.dumps(u)], [])
        case("add-on: long-lived tokens counted with the oldest's age",
             u["long_lived_tokens"], {"count": 1, "oldest_days": (NOW - datetime.fromisoformat(
                 "2026-08-15T12:00:00+00:00")).days})
        b = files["backups.json"]
        case("add-on: backups by date, size, type, locations by kind",
             b["backups"], [{"date": "2026-10-30T14:00:00+00:00", "size_mb": 112, "type": "full",
                             "locations": ["local"], "protected": False}])
        case("add-on: backup settings from .storage/backup, the password as a boolean only",
             b["settings"], {"source": "storage", "schedule": {"recurrence": "never"},
                             "retention": {"copies": None, "days": None}, "locations": ["local"], "encrypted": True})
        case("add-on: mounts by name, use and type only", b["mounts"], [{"name": "nas", "usage": "backup",
                                                                         "type": "cifs"}])
        d = {r["title"]: r for r in files["dashboards.json"]["dashboards"]}
        case("add-on: dashboards with view and card counts and card types (names only)",
             {t: (r["mode"], r["views"], r["cards"], r["card_types"], r["default"]) for t, r in d.items()},
             {x["title"]: (x["mode"], x["views"], x["cards"], sorted(x["card_types"]), x["default"])
              for x in FX["lovelace"]["dashboards"]})
        a = files["addons.json"]
        case("add-on: add-ons with running, start on boot, auto-update, watchdog",
             a["addons"][0], {"slug": "core_configurator", "name": "File editor", "version": "5.8.0", "running": True,
                              "boot": "auto", "auto_update": True, "watchdog": False})
        case("add-on: HACS repositories by category and name only",
             a["hacs"], {"source": "storage", "repositories": [
                 {"category": "integration", "name": "thomasloven/hass-browser_mod"},
                 {"category": "plugin", "name": "custom-cards/button-card"}]})
        case("add-on: blueprints present and who uses them",
             files["blueprints.json"]["blueprints"], [{"domain": "automation", "path": "homeassistant/motion_light.yaml",
                                                       "present": True,
                                                       "used_by": ["automation.seed_blueprint_hall_motion"]}])
        case("add-on: meta carries the mode, the core versions and no unknown file",
             (files["meta.json"]["mode"], files["meta.json"]["versions"]["core"], files["meta.json"]["unknown"]),
             ("addon", {"installed": FX["meta"]["core_version"], "latest": FX["meta"]["stable_core_version"]}, []))
        case("add-on: stdout names where each file came from, and nothing else",
             [ln.split(":")[0] for ln in stdout.splitlines()], ["export", "export", "export"])

        # ---- the definitions-only diff
        same = tmp / "same"
        run(addon, out=same)
        case("diff: identical exports are untouched", exp.diff(tmp / "export" / ".phase0e-start", same), ([], []))
        fired_dir = tmp / "fired"
        run(addon, fired="automation.seed_motion_kitchen", out=fired_dir)
        raw_a = json.loads((same / "automations.json").read_text())
        raw_b = json.loads((fired_dir / "automations.json").read_text())
        case("diff: one fired automation differs in the raw files (state, last_triggered)", raw_a != raw_b, True)
        case("diff: ... and is untouched on definitions", exp.diff(same, fired_dir), ([], []))
        configs = automation_configs()
        configs["seed_motion_kitchen"]["actions"] = [{"action": "light.turn_on", "target": {"entity_id": "light.x"}}]
        changed = tmp / "changed"
        run(addon, configs=configs, out=changed)
        case("diff: one changed automation is named, by field",
             exp.diff(same, changed), (["automations.json: automation.seed_motion_kitchen changed (config_sha)"], []))
        # KIT-EXIST.b1r M1: an automation with no UI definition (YAML) is outside the fingerprint, so it is named as
        # unknown and the verdict is unknown, never pass; a failed config GET keeps its status.
        yaml_cfg = automation_configs()
        del yaml_cfg["seed_motion_kitchen"]
        yaml_a, yaml_b = tmp / "yaml-a", tmp / "yaml-b"
        run(addon, configs=yaml_cfg, out=yaml_a)
        run(addon, configs=yaml_cfg, out=yaml_b)
        case("diff: a YAML-only automation is reported, not passed",
             exp.diff(yaml_a, yaml_b),
             ([], ["automations.json: 1 automation has no UI definition to fingerprint (YAML); compare their files "
                   "with git"]))
        yaml_row = [r for r in json.loads((yaml_a / "automations.json").read_text())
                    if r["entity_id"] == "automation.seed_motion_kitchen"][0]
        case("diff: ... its row has an id, a null config_sha and no definition note",
             (yaml_row["id"], yaml_row["config_sha"], "definition" in yaml_row), ("seed_motion_kitchen", None, False))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                exp.main(["--diff", str(yaml_a), str(yaml_b)])
            except SystemExit as e:
                exit_status = e.code
        case("diff: ... and the command line exits 2 (unknown)",
             (exit_status, buf.getvalue().splitlines()[-1]), (2, "diff: unknown (0 definition changes, 1 parts not "
                                                                 "compared)"))
        no_scripts = tmp / "no-scripts"
        run(addon, scripts={}, out=no_scripts)
        n_scripts = sum(1 for s in FX["states"] if s["entity_id"].startswith("script."))
        case("diff: YAML-only scripts on one side only are reported too",
             exp.diff(same, no_scripts)[1],
             [f"scripts_scenes.json: {n_scripts} scripts have no UI definition to fingerprint (YAML); compare their "
              f"files with git"])
        e403 = tmp / "cfg403"
        f403, _ = run(addon, out=e403, forbid_config=True)
        case("diff: a 403 on the config GET keeps its status in the row",
             {r.get("definition") for r in f403["automations.json"] if r["entity_id"].startswith("automation.")},
             {"unreadable (403)"})
        n_autos = sum(1 for s in FX["states"] if s["entity_id"].startswith("automation."))
        case("diff: ... and is reported as unreadable, not as YAML",
             exp.diff(e403, e403)[1],
             [f"automations.json: {n_autos} automations with the definition unreadable (403); check the token is an "
              f"administrator's and export again",
              f"scripts_scenes.json: {n_scripts} scripts with the definition unreadable (403); check the token is an "
              f"administrator's and export again"])
        try:
            exp.snapshot(files, tmp / "export", "phase0e-start")
            case("snapshot: written once", "overwrote", "refused")
        except SystemExit as e:
            case("snapshot: written once", "written once" in str(e), True)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                exp.main(["--out", str(tmp / "export"), "--diff", "phase0e-start", str(changed)])
            except SystemExit as e:
                exit_status = e.code
        case("diff: the command line exits 1 and names the change",
             (exit_status, buf.getvalue().splitlines()[0]),
             (1, "changed  automations.json: automation.seed_motion_kitchen changed (config_sha)"))

        # ---- a Supervisor 403 (a lesser hassio_role)
        files403, _ = run({**addon, "supervisor": make_supervisor(forbid=("/addons", "/backups"))}, out=tmp / "e403")
        case("403: addons.json answers unknown, not an empty list",
             (files403["addons.json"]["status"], "addons" in files403["addons.json"]), ("unknown", False))
        case("403: backups.json answers unknown, the settings still read from .storage",
             (files403["backups.json"]["status"], "backups" in files403["backups.json"],
              files403["backups.json"]["settings"]["source"]), ("unknown", False, "storage"))
        case("403: meta lists both as unknown", files403["meta.json"]["unknown"], ["addons.json", "backups.json"])

        # ---- from a computer: the websocket, no .storage
        comp, cout = run({"mode": "computer", "ws": make_ws()}, out=tmp / "computer")
        case("computer: no planted secret in any file or stdout (backup/config/info holds the password)",
             leaks(all_text(tmp / "computer") + [cout]), [])
        case("computer: dashboards and add-ons from the websocket",
             (comp["dashboards.json"]["source"], comp["addons.json"]["source"], comp["backups.json"]["source"],
              comp["backups.json"]["settings"]["source"], comp["blueprints.json"]["source"]),
             ("websocket", "websocket", "websocket", "websocket", "websocket"))
        case("computer: the same dashboards as inside the add-on",
             comp["dashboards.json"]["dashboards"], files["dashboards.json"]["dashboards"])
        case("computer: backups by kind, size in MB", comp["backups.json"]["backups"],
             [{"date": "2026-10-30T14:00:00+00:00", "type": "full", "size_mb": 112.0, "locations": ["local"],
               "protected": False}])
        case("computer: users.json answers unknown with what would let it read",
             (comp["users.json"]["status"], comp["users.json"]["source"], "--config" in comp["users.json"]["why"]),
             ("unknown", "person", True))
        person, _ = run({"mode": "computer", "ws": make_ws(admin=False)}, out=tmp / "person")
        case("computer, not an administrator: dashboards fall back to the person",
             (person["dashboards.json"]["source"], person["dashboards.json"]["status"],
              bool(person["dashboards.json"].get("ask"))), ("person", "unknown", True))
        case("diff: a person-sourced dashboards file answers unknown, never pass",
             exp.diff(tmp / "computer", tmp / "person"), ([], ["dashboards.json: person-sourced or unknown, not compared"]))
        with_cfg, _ = run({"mode": "computer", "ws": make_ws(), "config_dir": str(cfg),
                           "storage": exp.storage_reader(cfg)}, out=tmp / "withcfg")
        case("computer with --config: users read from the copy", with_cfg["users.json"]["status"], "ok")

        # ---- the real totp shape, and the trace reader
        cfg2 = make_config_dir(tmp / "dict", totp_as_dict=True)
        case("users: Home Assistant's own totp shape ({user_id: secret}) reads the same",
             exp.read_users(exp.storage_reader(cfg2), NOW)["other_administrators"], {"count": 1, "with_mfa": 1})
        traces = exp.trace_errors(exp.storage_reader(cfg))
        case("traces: automation and error flag only", sorted(traces[0]), ["automation", "error"])
        case("traces: the failing automation is flagged, the others are not",
             [t["automation"] for t in traces if t["error"]], ["automation.seed_bedroom_night_dim"])
        case("traces: no trace variable or error text reaches the result", leaks([json.dumps(traces)]) + [
            t for t in traces if "Template error" in json.dumps(t)], [])
        real = {"data": {"automation.1700000000001": [{"state": "stopped", "script_execution": "error",
                                                       "error": "x", "variables": {"v": SECRETS[3]}}],
                         "script.y": [{"error": "x"}]}}
        case("traces: Home Assistant's own shape ({'automation.<id>': [...]}), scripts skipped",
             exp.trace_errors(lambda n: real), [{"automation": "automation.1700000000001", "error": True}])

    # ---------------------------------------------------------------- the websocket client against a scripted server
    def accept_for(request):
        key = [ln.split(b":", 1)[1].strip() for ln in request.split(b"\r\n") if ln.lower().startswith(b"sec-websocket-key:")]
        return base64.b64encode(hashlib.sha1(key[0] + exp.WS_GUID.encode()).digest())

    def server(conn, log):
        f = b""
        while b"\r\n\r\n" not in f:
            f += conn.recv(4096)
        log.append(f.split(b"\r\n", 1)[0].decode())
        conn.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                     b"Sec-WebSocket-Accept: " + accept_for(f) + b"\r\n\r\n")

        def send(obj):
            conn.sendall(exp.ws_frame(json.dumps(obj).encode(), mask=False))

        def recv():
            b0, b1 = conn.recv(1)[0], conn.recv(1)[0]
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack("!H", conn.recv(2))[0]
            key = conn.recv(4)
            data = b""
            while len(data) < n:
                data += conn.recv(n - len(data))
            log.append(("masked" if b1 & 0x80 else "unmasked"))
            return json.loads(bytes(c ^ key[i % 4] for i, c in enumerate(data)))

        send({"type": "auth_required"})
        log.append(recv()["type"])
        send({"type": "auth_ok"})
        m = recv()
        send({"type": "event", "id": 99})
        big = {"views": [{"cards": [{"type": "tile"}] * 2000}]}  # a frame over 64 KB
        send({"id": m["id"], "type": "result", "success": True, "result": big})
        m = recv()
        send({"id": m["id"], "type": "result", "success": False, "error": {"code": "config_not_found"}})
        conn.close()


    a_sock, b_sock = socket.socketpair()
    log = []
    t = threading.Thread(target=server, args=(b_sock, log))
    t.start()
    cli = exp.WSClient("http://supervisor/core", "tok", sock=a_sock)
    res = cli.call({"type": "lovelace/config", "url_path": None})
    try:
        cli.call({"type": "lovelace/config", "url_path": "x"})
        err = None
    except exp.ReadError as e:
        err = e.status
    t.join(5)
    case("websocket: the Supervisor's proxy path, masked client frames, auth first",
         log[:4], ["GET /core/websocket HTTP/1.1", "masked", "auth", "masked"])
    case("websocket: a large result arrives whole, an unrelated message is skipped",
         len(res["views"][0]["cards"]), 2000)
    case("websocket: an error answers its code", err, "config_not_found")
    try:
        cli.call({"type": "config/entity_registry/update"})
        case("websocket: only the export's read commands are sent", "sent", "refused")
    except ValueError:
        case("websocket: only the export's read commands are sent", "refused", "refused")
    try:
        cli.call({"type": "supervisor/api", "endpoint": "/addons/x/restart", "method": "post"})
        case("websocket: supervisor/api only with GET", "sent", "refused")
    except ValueError:
        case("websocket: supervisor/api only with GET", "refused", "refused")

    # KIT-EXIST.b1r L1: a 101 without the right Sec-WebSocket-Accept (a proxy, a captive page) is refused
    def bad_server(conn, accept, frame=None):
        f = b""
        while b"\r\n\r\n" not in f:
            f += conn.recv(4096)
        hdr = b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
        conn.sendall(hdr + (b"Sec-WebSocket-Accept: " + (accept or accept_for(f)) + b"\r\n" if accept != b"-" else b"")
                     + b"\r\n" + (frame or b""))
        try:
            conn.recv(1)
        except OSError:
            pass
        conn.close()

    for label, accept, frame, want in (
            ("websocket: a wrong Sec-WebSocket-Accept is refused", b"bm90IHRoZSByaWdodCBvbmU=", None,
             "Sec-WebSocket-Accept"),
            ("websocket: a missing Sec-WebSocket-Accept is refused", b"-", None, "Sec-WebSocket-Accept"),
            # KIT-EXIST.b1r L2: a 64-bit length over the cap is refused before reading it
            ("websocket: a frame length over 64 MB is refused", None, bytes([0x81, 127]) + struct.pack("!Q", 1 << 40),
             "over the 64 MB cap")):
        a_sock, b_sock = socket.socketpair()
        t = threading.Thread(target=bad_server, args=(b_sock, accept, frame))
        t.start()
        try:
            exp.WSClient("http://supervisor/core", "tok", sock=a_sock)
            got = "connected"
        except exp.ReadError as e:
            got = str(e)
        a_sock.close()
        t.join(5)
        case(label, want in got, True)

    print("all pass" if not FAILS else f"{len(FAILS)} failed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
