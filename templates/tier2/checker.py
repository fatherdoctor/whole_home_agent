#!/usr/bin/env python3
"""checker.py - the deterministic half of a tier-2 support agent: finds problems, wakes the model, heals itself.

Status: template (O3b, 2026-10-13). Copied to tier2/checker.py only when agent.tier2_wanted is yes, and only once
the router, the health counts and the budget gate exist (interview/generated-files.md). Principle:
principles/tier-2-support-agent.md (rule numbers below are its rules). Standard library only.

Runs every 5 minutes from cron or a supervisor loop. No model, no actions on the house: it reads the Home
Assistant REST API, writes findings.json, touches a heartbeat, and for each finding not yet delivered wakes the
model with ONE line - the finding id, never free text from a state or a log line, so nothing stored in the house
can become an instruction (rule 9). The model reads findings.json itself, through its read-only wrapper.

Delivery is recorded per finding, apart from the finding itself: `woken` is set only when the wake command exits 0.
A finding still active and not yet woken is tried again every WAKE_RETRY_MIN minutes, so a failed or missing wake
is never lost when the finding outlives it. A failed wake (non-zero exit, a timeout, a command that cannot start)
is written to wake.log and on stderr, and the run exits 1 so the scheduler's own log shows it; the heartbeat is
still written, because the checks themselves ran.

Finding ids: <code>:<target>. Codes in this skeleton (add the house's own in CHECKS, each with a playbook row in
BRIEF.md - rule 6, no invented playbooks):
  C1  Home Assistant does not answer the API
  I1  a representative entity of a watched integration is unavailable for 10 min or more
  I2  a config entry of a watched domain is not loaded for 2 runs in a row (only entries seen loaded before)
  H1  a health count is above 0 for 15 min and its alert-open flag is off: the house did not announce it
  W1  a watchdog automation the agent relies on is switched off
  S1  the model's "pass done" stamp is older than AGENT_STALE_H hours: restart the agent, at most hourly (rule 13)

Settings (environment):
  HA_URL          default http://127.0.0.1:8123 (on the box); never a hostname that only one network knows
  HA_TOKEN_FILE   a file holding a long-lived token for a NON-ADMIN user where possible (I2 needs admin: skip it
                  if you will not give the checker one); never put the token itself in the environment or the repo
  TIER2_DIR       state folder: findings.json, heartbeat, pass_done, heal.log, wake.log (default ./tier2-state)
  WAKE_CMD        command that delivers one line to the model, the line appended as its last argument
                  (e.g. a tmux send-keys wrapper); unset = print only (a dry run): nothing is marked delivered,
                  so the findings are woken once it is set
  WAKE_RETRY_MIN  minutes between tries for a finding whose wake failed or was not sent (default 15)
  AGENT_RESTART   command that restarts the agent session (S1); unset = report S1, do not heal
  AGENT_STALE_H   hours before S1 (default 12)

Run `checker.py --selftest` to check the evaluation and the delivery rules offline against a fake API.
Run `checker.py --wake-test` once installed to prove a finding reaches the model: it sends the id `T0:wake-test`
through the real WAKE_CMD and exits 0 only when that command does; unset WAKE_CMD exits 2. No API call, no state
written; the model should say it got `T0:wake-test` and that it is a test.
"""
import contextlib
import io
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.request

# FILL (from house/docs/health-checks.md and the BRIEF's playbook table):
REP = {  # integration -> one entity that is only available while the integration works (I1)
    "zwave_js": "lock.front_door",
    "zha": "light.kitchen_ceiling",
}
I2_DOMAINS = {"zwave_js": "door locks", "zha": "Zigbee", "mobile_app": "phone pushes"}  # domain -> plain words
HEALTH = {  # health sensor -> its alert-open flag (packages/health_check.yaml)
    "sensor.health_security": "input_boolean.health_alert_open_security",
    "sensor.health_system": "input_boolean.health_alert_open_system",
}
WATCHDOGS = ["automation.health_fault_push", "automation.tier2_checker_silent"]  # W1

I1_MIN, H1_MIN = 10, 15
HEAL_EVERY_S = 3600
WAKE_TEST_ID = "T0:wake-test"


def api(path, ctx):
    req = urllib.request.Request(ctx["url"] + path, headers={"Authorization": "Bearer " + ctx["token"]})
    with _OPENER.open(req, timeout=20) as r:
        return json.loads(r.read())


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect: urllib would send the Authorization header on to whatever host a 3xx names."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # urllib then raises HTTPError with the 3xx code


_OPENER = urllib.request.build_opener(_NoRedirect)


def minutes_since(iso, now):
    from datetime import datetime
    return (now - datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()) / 60


def evaluate(get, now, memory, pass_done_age_h=None, stale_h=12):
    """-> (findings {id: text}, memory). `get(path)` is the API; `memory` carries I2's seen-loaded and
    previous-run state between runs. Pure apart from `get`, so --selftest can drive it."""
    found = {}
    try:
        states = {s["entity_id"]: s for s in get("/api/states")}
    except Exception as e:  # C1: nothing else can be judged without the API
        return {"C1:core": f"Home Assistant API did not answer ({type(e).__name__})"}, memory

    for integ, ent in REP.items():
        s = states.get(ent)
        if s and s["state"] == "unavailable" and minutes_since(s["last_changed"], now) >= I1_MIN:
            found[f"I1:{integ}"] = f"{ent} unavailable {int(minutes_since(s['last_changed'], now))} min"

    try:
        entries = get("/api/config/config_entries/entry")
    except Exception:
        entries = None  # no admin token: I2 is skipped, never guessed
    if entries is not None:
        seen = set(memory.get("seen_loaded", []))
        prev = set(memory.get("not_loaded", []))
        now_bad = set()
        for e in entries:
            if e.get("domain") not in I2_DOMAINS or e.get("disabled_by"):
                continue
            if e.get("state") == "loaded":
                seen.add(e["entry_id"])
            elif e["entry_id"] in seen:
                now_bad.add(e["entry_id"])
                if e["entry_id"] in prev:
                    found[f"I2:{e['entry_id']}"] = f"{I2_DOMAINS[e['domain']]} ({e.get('title', '')}) is {e.get('state')}"
        memory = dict(memory, seen_loaded=sorted(seen), not_loaded=sorted(now_bad))

    for sensor, flag in HEALTH.items():
        s, f = states.get(sensor), states.get(flag)
        if s and f and s["state"].isdigit() and int(s["state"]) > 0 and f["state"] == "off" \
                and minutes_since(s["last_changed"], now) >= H1_MIN:
            found[f"H1:{sensor}"] = f"{sensor} = {s['state']} for {int(minutes_since(s['last_changed'], now))} min, not announced"

    for a in WATCHDOGS:
        s = states.get(a)
        if s is None or s["state"] != "on":
            found[f"W1:{a}"] = f"{a} is {s['state'] if s else 'missing'}"

    if pass_done_age_h is not None and pass_done_age_h >= stale_h:
        found["S1:agent"] = f"agent pass_done stamp {pass_done_age_h:.0f} h old"
    return found, memory


def send_wake(wake_cmd, fid):
    """Run the wake command with the finding id as its last argument. -> None when it worked, else why not."""
    try:
        r = subprocess.run(shlex.split(wake_cmd) + [fid], timeout=30, check=False)
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        return f"{type(e).__name__}: {e}"
    return None if r.returncode == 0 else f"exit {r.returncode}"


def deliver(findings, now, wake_cmd, retry_s, send=send_wake):
    """Wake the model for each finding not yet delivered. Changes `findings` in place: `woken` when the command
    exits 0; `tries`, `last_try` and `wake_error` otherwise. -> (sent ids, [(id, why)] failures).
    No wake command is a dry run: printed, never marked delivered."""
    sent, failed = [], []
    for fid in sorted(findings):
        f = findings[fid]
        if f.get("woken") or now - f.get("last_try", 0) < retry_s:
            continue
        if not wake_cmd:
            print("would wake:", fid)
            continue
        f["tries"] = f.get("tries", 0) + 1
        f["last_try"] = now
        why = send(wake_cmd, fid)
        if why is None:
            f["woken"] = now
            f.pop("wake_error", None)
            sent.append(fid)
        else:
            f["wake_error"] = why
            failed.append((fid, why))
    return sent, failed


def wake_test(wake_cmd, send=send_wake):
    """--wake-test: -> exit code. 0 = the real wake command took the test id, 1 = it failed, 2 = no command."""
    if not wake_cmd:
        print("wake test: WAKE_CMD is not set, so no finding can reach the model")
        return 2
    why = send(wake_cmd, WAKE_TEST_ID)
    print("wake test: sent " + WAKE_TEST_ID if why is None else f"wake test: FAILED ({why})")
    return 0 if why is None else 1


def run():
    d = os.environ.get("TIER2_DIR", "./tier2-state")
    os.makedirs(d, exist_ok=True)
    p = lambda n: os.path.join(d, n)  # noqa: E731
    ctx = {"url": os.environ.get("HA_URL", "http://127.0.0.1:8123").rstrip("/"),
           "token": open(os.environ["HA_TOKEN_FILE"]).read().strip()}
    try:
        old = json.load(open(p("findings.json")))
    except (OSError, ValueError):
        old = {"findings": {}, "memory": {}}
    now = time.time()
    try:
        age_h = (now - os.path.getmtime(p("pass_done"))) / 3600
    except OSError:
        age_h = None  # never stamped yet: the agent's first pass has not happened; not a finding
    found, memory = evaluate(lambda path: api(path, ctx), now, old.get("memory", {}), age_h,
                             float(os.environ.get("AGENT_STALE_H", "12")))
    findings = {}
    for fid, text in found.items():
        prev = old["findings"].get(fid, {})
        findings[fid] = dict(prev, text=text, first=prev.get("first", now), last=now)  # keeps the delivery record
    _, failed = deliver(findings, now, os.environ.get("WAKE_CMD"),
                        60 * float(os.environ.get("WAKE_RETRY_MIN", "15")))
    if failed:
        with open(p("wake.log"), "a") as f:
            for fid, why in failed:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + f"wake failed for {fid}: {why}\n")
                print(f"checker: wake failed for {fid}: {why}", file=sys.stderr)
    tmp = p("findings.json.tmp")
    with open(tmp, "w") as f:
        json.dump({"updated": now, "findings": findings, "memory": memory}, f, indent=1)
    os.replace(tmp, p("findings.json"))
    if "S1:agent" in findings and os.environ.get("AGENT_RESTART"):
        try:
            last = os.path.getmtime(p("heal.log"))
        except OSError:
            last = 0
        if now - last >= HEAL_EVERY_S:
            subprocess.run(os.environ["AGENT_RESTART"].split(), timeout=120, check=False)
            with open(p("heal.log"), "a") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S restarted the agent (S1)\n"))
    with open(p("heartbeat"), "w") as f:  # the house pushes the owner when this goes silent for 2 h (rule 8)
        f.write(str(int(now)))
    return 1 if failed else 0


def selftest_cases():
    """(name, got, want) triples for templates/tests/test_templates.py."""
    now = 1_768_478_400.0  # a fixed time; ages below are relative to it
    iso = lambda m: time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(now - m * 60))  # noqa: E731
    base = [{"entity_id": "lock.front_door", "state": "locked", "last_changed": iso(600)},
            {"entity_id": "light.kitchen_ceiling", "state": "off", "last_changed": iso(600)},
            {"entity_id": "sensor.health_security", "state": "0", "last_changed": iso(600)},
            {"entity_id": "input_boolean.health_alert_open_security", "state": "off", "last_changed": iso(600)},
            {"entity_id": "sensor.health_system", "state": "0", "last_changed": iso(600)},
            {"entity_id": "input_boolean.health_alert_open_system", "state": "off", "last_changed": iso(600)},
            {"entity_id": "automation.health_fault_push", "state": "on", "last_changed": iso(600)},
            {"entity_id": "automation.tier2_checker_silent", "state": "on", "last_changed": iso(600)}]
    entries = [{"entry_id": "z1", "domain": "zwave_js", "state": "loaded", "title": "Z-Wave"},
               {"entry_id": "old", "domain": "zha", "state": "setup_error", "title": "old stick"}]

    def fake(states=None, ents=None, down=False):
        st = {s["entity_id"]: dict(s) for s in base}
        for e, v in (states or {}).items():
            st[e] = dict(st.get(e, {"entity_id": e}), **v)

        def get(path):
            if down:
                raise OSError("connection refused")
            return list(st.values()) if path == "/api/states" else (ents if ents is not None else entries)
        return get

    out = []
    f, m = evaluate(fake(), now, {})
    out.append(("healthy house -> no findings", sorted(f), []))
    out.append(("an entry never seen loaded is ignored", m["not_loaded"], []))
    f, _ = evaluate(fake(down=True), now, {})
    out.append(("API down -> C1 only", sorted(f), ["C1:core"]))
    f, _ = evaluate(fake({"lock.front_door": {"state": "unavailable", "last_changed": iso(5)}}), now, {})
    out.append(("unavailable 5 min -> nothing yet", sorted(f), []))
    f, _ = evaluate(fake({"lock.front_door": {"state": "unavailable", "last_changed": iso(12)}}), now, {})
    out.append(("unavailable 12 min -> I1", sorted(f), ["I1:zwave_js"]))
    bad = [dict(entries[0], state="setup_retry"), entries[1]]
    f1, m1 = evaluate(fake(ents=bad), now, m)
    f2, _ = evaluate(fake(ents=bad), now, m1)
    out.append(("entry down one run -> nothing; two runs -> I2", (sorted(f1), sorted(f2)), ([], ["I2:z1"])))
    f, _ = evaluate(fake({"sensor.health_security": {"state": "1", "last_changed": iso(20)}}), now, {})
    out.append(("health 1 for 20 min, flag off -> H1", sorted(f), ["H1:sensor.health_security"]))
    f, _ = evaluate(fake({"sensor.health_security": {"state": "1", "last_changed": iso(20)},
                          "input_boolean.health_alert_open_security": {"state": "on"}}), now, {})
    out.append(("health 1, announced -> nothing", sorted(f), []))
    f, _ = evaluate(fake({"automation.health_fault_push": {"state": "off"}}), now, {})
    out.append(("watchdog off -> W1", sorted(f), ["W1:automation.health_fault_push"]))
    f, _ = evaluate(fake(), now, {}, pass_done_age_h=13)
    out.append(("agent stamp 13 h old -> S1", sorted(f), ["S1:agent"]))

    # Delivery (rule 9): a finding is woken until a wake command exits 0, retried while it stays active.
    calls = []

    def fails(cmd, fid):
        calls.append(fid)
        return "exit 1"

    def works(cmd, fid):
        calls.append(fid)
        return None
    fs = {"I1:zha": {"text": "x", "first": now, "last": now}}
    sent, failed = deliver(fs, now, "wake", 900, fails)
    out.append(("a failed wake is reported, not counted as delivered",
                (sent, [i for i, _ in failed], "woken" in fs["I1:zha"], fs["I1:zha"].get("wake_error")),
                ([], ["I1:zha"], False, "exit 1")))
    deliver(fs, now + 300, "wake", 900, works)
    out.append(("...not tried again before the retry interval", list(calls), ["I1:zha"]))
    sent, _ = deliver(fs, now + 900, "wake", 900, works)
    out.append(("...and tried again once it has passed, while the finding is still active",
                (sent, bool(fs["I1:zha"].get("woken")), fs["I1:zha"]["tries"]), (["I1:zha"], True, 2)))
    sent, _ = deliver(fs, now + 3600, "wake", 900, works)
    out.append(("a delivered finding is not woken again", sent, []))
    fs = {"W1:automation.health_fault_push": {"text": "x", "first": now, "last": now}}
    with contextlib.redirect_stdout(io.StringIO()):  # the dry run's "would wake" line
        sent, _ = deliver(fs, now, None, 900, works)
    out.append(("no wake command: a dry run that marks nothing delivered",
                (sent, "woken" in fs["W1:automation.health_fault_push"]), ([], False)))
    sent, _ = deliver(fs, now + 60, "wake", 900, works)
    out.append(("...so the finding is woken once the command is set", sent, ["W1:automation.health_fault_push"]))
    with contextlib.redirect_stdout(io.StringIO()):
        codes = (wake_test(None, works), wake_test("wake", fails), wake_test("wake", works))
    out.append(("wake test: unset command exits 2, a failing one 1, a working one 0 with the test id",
                (codes, calls[-1]), ((2, 1, 0), WAKE_TEST_ID)))
    return out


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        bad = [(n, g, w) for n, g, w in selftest_cases() if g != w]
        for n, g, w in bad:
            print("FAIL", n, g, w)
        print("selftest:", "all pass" if not bad else f"{len(bad)} failing")
        sys.exit(1 if bad else 0)
    if "--wake-test" in sys.argv:
        sys.exit(wake_test(os.environ.get("WAKE_CMD")))
    sys.exit(run())
