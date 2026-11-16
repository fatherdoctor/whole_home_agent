#!/usr/bin/env python3
"""export_house.py - write what the box actually has to house/export/*.json, so docs and plans cite the truth.

Status: template (O4b, 2026-10-14; the existing-house inventory, snapshot and diff KIT-EXIST.b1, 2026-10-31).
Copied to house/export/export_house.py by the backlog item "live export script" (interview/generated-files.md), and
by Phase 0E on an existing house (AGENTS.md). Principle: principles/documentation.md rule 7 (the live export outranks
any prose). Standard library only; no pip install.

    HA_URL=http://<address>:8123 HA_TOKEN=<long-lived token> python3 house/export/export_house.py [--out house/export]
        [--config <copy of the configuration folder>] [--snapshot <name>]
    python3 house/export/export_house.py --diff <snapshot or folder> <snapshot or folder>

The token comes from the environment ONLY - never an argument (it would land in shell history) and never a file in
the repository. Make it in Home Assistant: your profile > Security > Long-lived access tokens, named for this job.
The export needs an administrator's token (the config-entries list is admin-only). Inside a runtime's app the
app sets HA_URL and HA_TOKEN itself (install/agent-access.md section 0); nothing to make.

Every read is a GET, a read-only websocket command or a file read. Nothing on the box is changed.

What it writes (each file sorted, so a git diff shows only what changed):
  entities.json      every entity that has a state: id, name, domain, area, floor, device, labels, integration,
                     and a few stable attributes (device_class, unit). No live states: they change every minute and
                     would bury the real differences. Disabled entities have no state and are not listed.
  areas.json         areas with their floor and how many entities each holds.
  integrations.json  config entries: domain, title, state (loaded, setup_retry, ...), disabled or not.
  automations.json   automations and scripts: id, name, on or off; for automations also the mode, the blueprint
                     used and a short fingerprint of the definition (config_sha), so a changed automation shows.
                     Their YAML lives in ha/, not here.
  meta.json          Home Assistant version (and OS and Supervisor, with the latest of each, when the box has
                     them), time zone, unit system, when the export ran, which way it read (app or computer) and
                     where each file came from.
  scripts_scenes.json  scripts (id, name, on or off, mode, last triggered, fingerprint) and scenes (id, name).
  helpers.json       input_* helpers, counter, timer, schedule and UI template helpers: id, name, area and their
                     definition (options, ranges); an input_text's value is never read.
  dashboards.json    each dashboard: url path, title, mode, view and card counts, the card types used (names only).
  addons.json        apps (slug, name, version, running, start on boot, auto-update, watchdog) and legacy HACS
                     repositories (category and name).
  backups.json       backups (date, size, type, locations by kind, protected or not), mounts by name and use, and
                     the backup settings: schedule, retention, where to, encrypted yes or no.
  users.json         counts only: users, administrators, multi-factor login by role (never by name), long-lived
                     tokens and the age of the oldest.
  blueprints.json    blueprint files present and which automations and scripts use them.

Where each new file reads, by path (AGENTS.md, "Phase 0E", step 3; existing-house.md, "What to expect" 3):
  inside the app  the configuration folder's .storage files (read by this script alone, by a whitelist of keys
                     per file; never copied) and the Supervisor API. The first runtime's app declares
                     hassio_api and hassio_role: manager (another runtime's page says what its app
                     declares), which reaches /addons, /backups and /mounts; with a lesser role a 403
                     answers `unknown` for that file, never "none".
  from a computer    the websocket API (lovelace/dashboards/list, lovelace/config, backup/info, backup/config/info,
                     supervisor/api with a GET, blueprint/list) with an administrator's token. What it cannot
                     read is written as `"source": "person", "status": "unknown"` with the page the person reads
                     to the agent. users.json has no computer source (the multi-factor stores are files): `unknown`
                     unless --config points at a copy of the configuration folder with its .storage/.

The .storage whitelist (existing-house.md, "What the agent never does on this path"): lovelace* (view and card
counts, card types), hacs.repositories
(name, category, installed), backup (schedule, retention, agent ids; the encryption password as present or absent
only), auth (users' admin flag and owner flag, tokens' type and creation date; never a name, hash or token),
auth_module.totp / auth_module.notify (whether an entry exists for a user id, never the entry), trace.saved_traces
(the automation and whether the trace ended in error; never the trace's variables or the error text).

--snapshot <name> also writes the export, once, to <out>/.<name>/ (Phase 0E: .phase0e-start and .phase0e-end).
--diff <a> <b> compares two exports on DEFINITIONS only - automations, scripts, scenes, helpers, areas, dashboards,
integrations - and drops on/off, last_triggered and every other runtime field: on a lived-in house automations fire
while the agent reads, and that is not a change by the agent. Exit 0 untouched, 1 a definition changed (named), 2 a
part could not be compared (a person-sourced or unknown file: two recitations are not a diff; and automations or
scripts whose definition could not be fingerprinted - YAML-only, no id, or a config GET that failed, which keeps its
status as `definition: "unreadable (403)"` - are counted per file and named, never passed).

Run it before a plan names an entity ("read back", principles/naming.md), after a change, and before each wiki
writer run. Then run the push guard: an integration's title can carry an account name or an email address; rename
the entry in Home Assistant or add a guard allow line, never commit it as it is.
"""
import argparse
import base64
import hashlib
import json
import os
import pathlib
import re
import shutil
import socket
import ssl
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# One template call returns every registry link the REST states list lacks. Rendered by Home Assistant itself, so
# the functions are the real ones (area_id, floor_id, device_id, labels, config_entry_id, config_entry_attr).
REGISTRY_TEMPLATE = """
{%- set ns = namespace(rows=[]) -%}
{%- for s in states -%}
  {%- set e = s.entity_id -%}
  {%- set entry = config_entry_id(e) -%}
  {%- set dev = device_id(e) -%}
  {%- set ns.rows = ns.rows + [{"entity_id": e, "area": area_id(e), "floor": floor_id(e), "device": dev,
      "device_name": device_attr(dev, "name_by_user") or device_attr(dev, "name") if dev else none,
      "labels": labels(e), "integration": config_entry_attr(entry, "domain") if entry else none}] -%}
{%- endfor -%}
{%- set na = namespace(rows=[]) -%}
{%- for a in areas() -%}
  {%- set na.rows = na.rows + [{"area": a, "name": area_name(a), "floor": floor_id(a),
      "entities": area_entities(a) | count}] -%}
{%- endfor -%}
{{- {"entities": ns.rows, "areas": na.rows} | to_json -}}
"""

KEEP_ATTRS = ("device_class", "unit_of_measurement", "state_class")
SUPERVISOR_URL = "http://supervisor"
ADDON_CONFIG = "/homeassistant"


class ReadError(SystemExit):
    """A read that failed. Uncaught it ends the run with its message (as before); the new files catch it and answer
    `unknown`. `status` is the HTTP code, or the websocket error code."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect: urllib would send the Authorization header on to whatever host a 3xx names."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # urllib then raises HTTPError with the 3xx code


# Every request that carries the token goes through this opener, never urllib.request.urlopen.
OPENER = urllib.request.build_opener(NoRedirect)


def http_fetch(base, token):
    """The real fetcher: fetch(method, path, body) -> parsed JSON. Raises ReadError with a plain message."""

    def fetch(method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(base.rstrip("/") + path, data=data, method=method,
                                     headers={"Authorization": "Bearer " + token,
                                              "Content-Type": "application/json"})
        try:
            with OPENER.open(req, timeout=60) as r:
                raw = r.read().decode()
        except urllib.error.HTTPError as e:
            hint = {401: "the token is wrong or expired", 403: "the token's user is not an administrator",
                    404: "this Home Assistant has no such endpoint (too old?)"}.get(e.code, e.reason)
            if 300 <= e.code < 400:
                hint = "a redirect; the token is not sent on, so use the address it points to"
            raise ReadError(f"export: {method} {path} failed: {e.code} ({hint})", e.code)
        except urllib.error.URLError as e:
            raise ReadError(f"export: cannot reach Home Assistant: {e.reason}")
        return json.loads(raw)

    return fetch


def supervisor_fetch(token, base=SUPERVISOR_URL):
    """GET on the Supervisor API (inside an app): supervisor(path) -> the reply's `data`. A 403 is a ReadError
    with status 403 (the app's hassio_role does not reach that path)."""

    def get(path):
        req = urllib.request.Request(base + path, headers={"Authorization": "Bearer " + token})
        try:
            with OPENER.open(req, timeout=60) as r:
                reply = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise ReadError(f"export: Supervisor GET {path} failed: {e.code}", e.code)
        except urllib.error.URLError as e:
            raise ReadError(f"export: cannot reach the Supervisor: {e.reason}")
        return reply.get("data", {}) if isinstance(reply, dict) else {}

    return get


# ---------------------------------------------------------------- a small websocket client (read-only commands)
def ws_frame(payload, opcode=1, mask=True):
    """One websocket frame. Clients must mask (RFC 6455 5.3)."""
    head = bytes([0x80 | opcode])
    n = len(payload)
    bit = 0x80 if mask else 0
    if n < 126:
        head += bytes([bit | n])
    elif n < 65536:
        head += bytes([bit | 126]) + struct.pack("!H", n)
    else:
        head += bytes([bit | 127]) + struct.pack("!Q", n)
    if not mask:
        return head + payload
    key = os.urandom(4)
    return head + key + bytes(b ^ key[i % 4] for i, b in enumerate(payload))


WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  # RFC 6455's fixed string for Sec-WebSocket-Accept
WS_MAX_FRAME = 64 << 20  # 64 MB: far over any dashboard or registry answer


class WSClient:
    """Home Assistant's websocket API, standard library only: call({"type": ...}) -> result, or ReadError with the
    error code. Only read commands are sent (the export's own list, WS_READS)."""

    def __init__(self, base, token, timeout=60, sock=None):
        self.next_id = 1
        self.buf = b""
        u = urllib.parse.urlparse(base)
        if sock is None:
            port = u.port or (443 if u.scheme == "https" else 80)
            try:
                sock = socket.create_connection((u.hostname, port), timeout)
                if u.scheme == "https":
                    sock = ssl.create_default_context().wrap_socket(sock, server_hostname=u.hostname)
            except OSError as e:
                raise ReadError(f"export: websocket: cannot reach {u.hostname}: {e}")
        self.sock = sock
        # The Supervisor proxies Core's websocket at /core/websocket; Core itself serves /api/websocket.
        path = "/core/websocket" if u.hostname == "supervisor" else u.path.rstrip("/") + "/api/websocket"
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {path} HTTP/1.1\r\nHost: {u.netloc}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
                           ).encode())
        while b"\r\n\r\n" not in self.buf:
            self._more()
        head, self.buf = self.buf.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n", 1)[0] + b" ":
            raise ReadError("export: websocket: the upgrade was refused")
        # RFC 6455 4.1: the server proves it read our key. A proxy or a captive page that answers 101 fails here.
        want = base64.b64encode(hashlib.sha1((key + WS_GUID).encode()).digest())
        got = [ln.split(b":", 1)[1].strip() for ln in head.split(b"\r\n")[1:]
               if ln.split(b":", 1)[0].strip().lower() == b"sec-websocket-accept"]
        if got != [want]:
            raise ReadError("export: websocket: the upgrade answer is not Home Assistant's (Sec-WebSocket-Accept "
                            "missing or wrong): check the address, or a proxy in the way")
        first = self._recv()
        if first.get("type") != "auth_required":
            raise ReadError("export: websocket: unexpected greeting")
        self._send({"type": "auth", "access_token": token})
        if self._recv().get("type") != "auth_ok":
            raise ReadError("export: websocket: the token was refused", "auth_invalid")

    def _more(self):
        chunk = self.sock.recv(65536)
        if not chunk:
            raise ReadError("export: websocket: the connection closed")
        self.buf += chunk

    def _take(self, n):
        while len(self.buf) < n:
            self._more()
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _send(self, msg):
        self.sock.sendall(ws_frame(json.dumps(msg).encode()))

    def _recv(self):
        data = b""
        while True:
            b0, b1 = self._take(2)
            op, n = b0 & 0x0F, b1 & 0x7F
            if n == 126:
                n = struct.unpack("!H", self._take(2))[0]
            elif n == 127:
                n = struct.unpack("!Q", self._take(8))[0]
            if n > WS_MAX_FRAME:
                raise ReadError(f"export: websocket: a frame of {n} bytes is over the {WS_MAX_FRAME >> 20} MB cap")
            key = self._take(4) if b1 & 0x80 else None
            payload = self._take(n)
            if key:
                payload = bytes(b ^ key[i % 4] for i, b in enumerate(payload))
            if op == 8:
                raise ReadError("export: websocket: closed by Home Assistant")
            if op == 9:
                self.sock.sendall(ws_frame(payload, opcode=10))
                continue
            if op in (0, 1, 2):
                data += payload
                if b0 & 0x80:
                    return json.loads(data.decode())

    def call(self, msg):
        if msg.get("type") not in WS_READS or (msg.get("type") == "supervisor/api"
                                               and msg.get("method", "get") != "get"):
            raise ValueError(f"export: {msg.get('type')} is not one of the export's read-only commands")
        i, self.next_id = self.next_id, self.next_id + 1
        self._send({"id": i, **msg})
        while True:
            reply = self._recv()
            if reply.get("id") == i and reply.get("type") == "result":
                if reply.get("success"):
                    return reply.get("result")
                err = reply.get("error") or {}
                raise ReadError(f"export: websocket {msg['type']}: {err.get('code')}", err.get("code"))


WS_READS = ("lovelace/dashboards/list", "lovelace/config", "backup/info", "backup/config/info", "supervisor/api",
            "trace/list",  # the first look (first_look.py check 2, from a computer)
            "blueprint/list")


def lazy_ws(base, token):
    """ws(msg) that connects on first use; a failure to connect is a ReadError for that read, as any other."""
    holder = {}

    def call(msg):
        if "client" not in holder:
            holder["client"] = WSClient(base, token)
        return holder["client"].call(msg)

    return call


# ---------------------------------------------------------------- the .storage whitelist
def storage_reader(config_dir):
    """read(name) -> the parsed .storage file, or None when it is not there. Only this module's whitelisted
    functions below call it; nothing it returns is written as it is."""
    root = pathlib.Path(config_dir) / ".storage"

    def read(name):
        f = root / name
        try:
            return json.loads(f.read_text())
        except FileNotFoundError:
            return None
        except (OSError, ValueError) as e:
            raise ReadError(f"export: cannot read .storage/{name}: {e.__class__.__name__}")

    return read


def _data(doc):
    return doc.get("data") if isinstance(doc, dict) else None


def _entry_ids(module_doc):
    """auth_module.totp / .notify: the user ids that have an entry; never the entry (it is the secret)."""
    users = (_data(module_doc) or {}).get("users")
    if isinstance(users, dict):  # Home Assistant's own shape: {user_id: secret or settings}
        return set(users)
    if isinstance(users, list):  # tolerated: [{"user_id": ...}, ...]
        return {u.get("user_id") for u in users if isinstance(u, dict)}
    return set()


def read_users(storage, now):
    auth = _data(storage("auth"))
    if auth is None:
        return None
    users = [u for u in auth.get("users") or [] if not u.get("system_generated") and u.get("is_active", True)]
    mfa = _entry_ids(storage("auth_module.totp")) | _entry_ids(storage("auth_module.notify"))
    admins = [u for u in users if "system-admin" in (u.get("group_ids") or [])]
    owner = next((u for u in users if u.get("is_owner")), None)
    others = [u for u in admins if u is not owner]
    ages = []
    for t in auth.get("refresh_tokens") or []:
        if t.get("token_type") == "long_lived_access_token" and t.get("created_at"):
            try:
                ages.append((now - _when(t["created_at"])).days)
            except ValueError:
                pass
    return {
        "users": len(users), "administrators": len(admins),
        "owner": None if owner is None else {"administrator": owner in admins, "mfa": owner.get("id") in mfa},
        "other_administrators": {"count": len(others), "with_mfa": sum(1 for u in others if u.get("id") in mfa)},
        "long_lived_tokens": {"count": len(ages), "oldest_days": max(ages) if ages else None},
    }


def backup_settings(config):
    """`.storage/backup`'s data.config, or backup/config/info's config: schedule, retention, agents by kind, and the
    encryption password as present or absent only (the file holds the key itself)."""
    config = config if isinstance(config, dict) else {}
    create = config.get("create_backup") or {}
    sched = config.get("schedule") or {}
    ret = config.get("retention") or {}
    return {
        "schedule": {k: sched.get(k) for k in ("recurrence", "days", "time") if k in sched},
        "retention": {k: ret.get(k) for k in ("copies", "days") if k in ret},
        "locations": sorted({location_kind(a) for a in create.get("agent_ids") or []}),
        "encrypted": bool(create.get("password")),
    }


def location_kind(agent):
    """A backup location by kind, never by path: local, Nabu Casa, mount:<name>, or the integration's domain."""
    if agent in (None, "", ".local", "backup.local", "hassio.local"):
        return "local"
    if agent == "cloud.cloud":
        return "Nabu Casa"
    domain, _, name = str(agent).partition(".")
    if domain == "hassio":
        return "mount:" + name
    return domain if name else "mount:" + domain


def trace_errors(storage):
    """`.storage/trace.saved_traces` read for two keys only: which automation, and whether its trace ended in error.
    The file also holds trace variables (trigger payloads, message text, names); none is read. For the first look."""
    doc = _data(storage("trace.saved_traces"))
    rows = {}
    if isinstance(doc, dict):  # Home Assistant's shape: {"automation.<id>": [trace, ...]}
        items = [(k, v) for k, v in doc.items()]
    elif isinstance(doc, list):  # tolerated: [{"key": ["automation", "<id>"], "traces": [...]}]
        items = [(".".join(map(str, x.get("key") or [])), x.get("traces")) for x in doc if isinstance(x, dict)]
    else:
        return []
    for key, traces in items:
        if not str(key).startswith("automation."):
            continue
        err = any(isinstance(t, dict) and (t.get("error") or t.get("script_execution") == "error")
                  for t in traces or [])
        rows[key] = rows.get(key, False) or err
    return [{"automation": k, "error": v} for k, v in sorted(rows.items())]


def summarize_lovelace(config):
    """View and card counts and the card types; nothing else of a dashboard's config is kept."""
    if not isinstance(config, dict):
        return {"views": None, "cards": None, "card_types": []}
    if "strategy" in config and not config.get("views"):
        return {"views": 0, "cards": 0, "card_types": [], "strategy": str((config["strategy"] or {}).get("type"))}
    types = set()

    def walk(cards):
        n = 0
        for c in cards if isinstance(cards, list) else []:
            if isinstance(c, dict):
                n += 1
                if isinstance(c.get("type"), str):
                    types.add(c["type"])
                n += walk(c.get("cards"))
                if isinstance(c.get("card"), dict):
                    n += walk([c["card"]])
        return n

    views = config.get("views") if isinstance(config.get("views"), list) else []
    count = 0
    for v in views:
        if isinstance(v, dict):
            count += walk(v.get("cards"))
            for sec in v.get("sections") or []:
                if isinstance(sec, dict):
                    count += walk(sec.get("cards"))
    return {"views": len(views), "cards": count, "card_types": sorted(types)}


# ---------------------------------------------------------------- the seven new files
def unknown(why, source="unknown", ask=None):
    out = {"source": source, "status": "unknown", "why": why}
    if ask:
        out["ask"] = ask
    return out


def _when(v):
    d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _sha(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True, default=str).encode()).hexdigest()[:16]


def read_definition(fetch, domain, item_id):
    """The UI config of one automation or script (GET, administrator): its blueprint and a fingerprint. None when it
    has no UI config (YAML-only: the GET answers 404, or no id). A GET that failed otherwise keeps its status
    (`definition: "unreadable (403)"`), so a permission problem does not look like YAML."""
    if not item_id:
        return None
    try:
        cfg = fetch("GET", f"/api/config/{domain}/config/{urllib.parse.quote(str(item_id), safe='')}")
    except ReadError as e:
        if e.status == 404:
            return None
        return {"blueprint": None, "config_sha": None, "definition": f"unreadable ({e.status or 'no answer'})"}
    if not isinstance(cfg, dict):
        return None
    return {"blueprint": (cfg.get("use_blueprint") or {}).get("path"), "config_sha": _sha(cfg)}


HELPER_FIELDS = {
    "input_boolean": (), "input_button": (), "input_text": (), "schedule": (),
    "input_select": ("options",), "input_number": ("min", "max", "step", "mode"),
    "input_datetime": ("has_date", "has_time"), "counter": ("minimum", "maximum", "step", "initial"),
    "timer": ("duration",),
}


def dashboards_file(src):
    storage, ws = src.get("storage"), src.get("ws")
    if storage:
        listed = (_data(storage("lovelace_dashboards")) or {}).get("items") or []
        rows = [{"url_path": None, "title": "Overview", "default": True,
                 **_storage_dash(storage("lovelace"), "storage")}]
        for d in listed:
            mode = d.get("mode", "storage")
            row = {"url_path": d.get("url_path"), "title": d.get("title"), "default": False}
            if mode == "yaml":
                row.update({"mode": "yaml", "views": None, "cards": None, "card_types": [],
                            "note": "a YAML dashboard: its file is not read here"})
            else:
                row.update(_storage_dash(storage("lovelace." + str(d.get("id"))), "storage"))
            rows.append(row)
        return {"source": "storage", "status": "ok", "dashboards": _sorted_dash(rows)}
    if ws:
        try:
            listed = ws({"type": "lovelace/dashboards/list"}) or []
            rows = []
            for d in [{"url_path": None, "title": "Overview", "mode": "storage"}] + list(listed):
                row = {"url_path": d.get("url_path"), "title": d.get("title"), "default": d.get("url_path") is None,
                       "mode": d.get("mode", "storage")}
                try:
                    row.update(summarize_lovelace(ws({"type": "lovelace/config", "url_path": d.get("url_path")})))
                except ReadError as e:
                    if e.status != "config_not_found":
                        raise
                    row.update({"mode": "auto-generated", "views": 0, "cards": 0, "card_types": []})
                rows.append(row)
            return {"source": "websocket", "status": "ok", "dashboards": _sorted_dash(rows)}
        except ReadError as e:
            return unknown(f"the websocket dashboard reads answered {e.status or e}", "person",
                           "Settings > Dashboards: each dashboard's title, and its views and card types")
    return unknown("no configuration folder and no websocket", "person",
                   "Settings > Dashboards: each dashboard's title, and its views and card types")


def _storage_dash(doc, mode):
    if doc is None:  # no stored config: the auto-generated dashboard (or a YAML-mode Overview)
        return {"mode": "auto-generated", "views": 0, "cards": 0, "card_types": []}
    return {"mode": mode, **summarize_lovelace((_data(doc) or {}).get("config"))}


def _sorted_dash(rows):
    return sorted(rows, key=lambda r: (r["url_path"] is not None, r["url_path"] or ""))


def addons_file(src, links):
    sup, ws, storage = src.get("supervisor"), src.get("ws"), src.get("storage")
    out = None
    if sup or ws:
        def get(path):
            return sup(path) if sup else ws({"type": "supervisor/api", "endpoint": path, "method": "get"})
        try:
            rows = []
            for a in (get("/addons") or {}).get("addons") or []:
                info = get(f"/addons/{a.get('slug')}/info") or {}
                rows.append({"slug": a.get("slug"), "name": info.get("name", a.get("name")),
                             "version": info.get("version", a.get("version")),
                             "running": info.get("state", a.get("state")) == "started",
                             "boot": info.get("boot"), "auto_update": info.get("auto_update"),
                             "watchdog": info.get("watchdog")})
            out = {"source": "supervisor" if sup else "websocket", "status": "ok",
                   "addons": sorted(rows, key=lambda r: r["slug"] or "")}
        except ReadError as e:
            why = (f"the Supervisor answered {e.status}: the app's hassio_role does not reach /addons "
                   "(it needs manager)") if e.status == 403 else (
                "this Home Assistant has no Supervisor (Container or Core install)"
                if e.status in ("unknown_command", 404) else f"the app list could not be read ({e.status or e})")
            out = unknown(why, "person" if not sup else "unknown",
                          "Settings > Apps: each app's name, and whether it is running")
    if out is None:
        out = unknown("no Supervisor access and no websocket", "person",
                      "Settings > Apps: each app's name, and whether it is running")
    if storage and storage("hacs.repositories") is not None:
        repos = _data(storage("hacs.repositories")) or {}
        items = repos.values() if isinstance(repos, dict) else repos
        hacs = {"source": "storage", "repositories": sorted(
            ({"category": r.get("category"), "name": r.get("full_name")} for r in items
             if isinstance(r, dict) and r.get("installed")), key=lambda r: (r["category"] or "", r["name"] or ""))}
    else:
        hacs = {"source": "states", "repositories": sorted(
            ({"category": None, "name": r["name"]} for r in links
             if r["integration"] == "hacs" and r["entity_id"].startswith("update.")), key=lambda r: r["name"] or "")}
    out["hacs"] = hacs
    return out


def backups_file(src):
    sup, ws, storage = src.get("supervisor"), src.get("ws"), src.get("storage")
    ask = "Settings > System > Backups: the date and place of the newest backup, and the automatic backup settings"
    if sup:
        try:
            raw = (sup("/backups") or {}).get("backups") or []
            rows = [{"date": b.get("date"), "size_mb": b.get("size"), "type": b.get("type"),
                     "locations": sorted({location_kind(x) for x in (b.get("locations") or [b.get("location")])}),
                     "protected": bool(b.get("protected"))} for b in raw]
            out = {"source": "supervisor", "status": "ok", "backups": rows}
            try:
                out["mounts"] = sorted(({"name": m.get("name"), "usage": m.get("usage"), "type": m.get("type")}
                                        for m in (sup("/mounts") or {}).get("mounts") or []),
                                       key=lambda m: m["name"] or "")
            except ReadError as e:
                out["mounts"] = unknown(f"the Supervisor answered {e.status} for /mounts (needs manager)")
        except ReadError as e:
            out = unknown(f"the Supervisor answered {e.status} for /backups (needs the backup or manager role)",
                          ask=ask)
    elif ws:
        try:
            info = ws({"type": "backup/info"}) or {}
            rows = []
            for b in info.get("backups") or []:
                agents = b.get("agents") or {a: {} for a in b.get("agent_ids") or []}
                sizes = [a.get("size") for a in agents.values() if isinstance(a, dict) and a.get("size")]
                size = max(sizes) if sizes else b.get("size")
                rows.append({"date": b.get("date"), "type": "full" if b.get("database_included", True) and
                             b.get("homeassistant_included", True) and not b.get("folders") else "partial",
                             "size_mb": round(size / 1048576, 1) if isinstance(size, (int, float)) else None,
                             "locations": sorted({location_kind(a) for a in agents}),
                             "protected": any(isinstance(a, dict) and a.get("protected") for a in agents.values())
                             or bool(b.get("protected"))})
            out = {"source": "websocket", "status": "ok", "backups": rows,
                   "mounts": unknown("mounts are read inside the app only")}
        except ReadError as e:
            out = unknown(f"backup/info answered {e.status or e}", "person", ask)
    else:
        out = unknown("no Supervisor access and no websocket", "person", ask)
    if "backups" in out:
        out["backups"] = sorted(out["backups"], key=lambda b: str(b["date"]))
    settings = None
    if storage and storage("backup") is not None:
        settings = {"source": "storage", **backup_settings((_data(storage("backup")) or {}).get("config"))}
    elif ws:
        try:
            settings = {"source": "websocket",
                        **backup_settings((ws({"type": "backup/config/info"}) or {}).get("config"))}
        except ReadError as e:
            settings = unknown(f"backup/config/info answered {e.status or e}", "person", ask)
    out["settings"] = settings or unknown("no configuration folder and no websocket", "person", ask)
    return out


def users_file(src, now):
    storage = src.get("storage")
    if storage:
        counts = read_users(storage, now)
        if counts is not None:
            return {"source": "storage", "status": "ok", **counts}
    return unknown("from a computer there is no source: Settings > People shows administrators but not another "
                   "user's multi-factor state or token ages; the app, or --config with a copy of the "
                   "configuration folder and its .storage/, would let it read", "person",
                   "Settings > People: how many users and administrators; the owner alone says whether their own "
                   "login uses a second factor")


def blueprints_file(src, definitions):
    config_dir, ws = src.get("config_dir"), src.get("ws")
    present, source, why = set(), None, "no configuration folder and no websocket: the files present are not listed"
    if config_dir and (pathlib.Path(config_dir) / "blueprints").is_dir():
        root = pathlib.Path(config_dir) / "blueprints"
        for f in root.rglob("*.y*ml"):
            rel = f.relative_to(root).parts
            if len(rel) >= 2:
                present.add((rel[0], "/".join(rel[1:])))
        source = "files"
    elif ws:
        try:
            for domain in ("automation", "script"):
                for path in (ws({"type": "blueprint/list", "domain": domain}) or {}):
                    present.add((domain, path))
            source = "websocket"
        except ReadError as e:
            source = None
            why = f"blueprint/list answered {e.status or e}"
    used = {}
    for entity_id, d in definitions.items():
        if d and d.get("blueprint"):
            used.setdefault((entity_id.split(".", 1)[0], d["blueprint"]), []).append(entity_id)
    keys = sorted(present | set(used))
    rows = [{"domain": k[0], "path": k[1], "present": (k in present) if source else None,
             "used_by": sorted(used.get(k, []))} for k in keys]
    if source is None:
        return {"source": "definitions", "status": "partial",
                "why": why,
                "blueprints": rows}
    return {"source": source, "status": "ok", "blueprints": rows}


def build(fetch, now=None, sources=None):
    """Everything the export writes, as {filename: data}. `fetch` is http_fetch(...) or a test's fake. With
    `sources` (a dict of storage, supervisor, ws, config_dir, mode - any may be missing) it adds the seven files of
    an existing house's inventory; without, the original five."""
    now = now or datetime.now(timezone.utc)
    config = fetch("GET", "/api/config")
    states = fetch("GET", "/api/states")
    entries = fetch("GET", "/api/config/config_entries/entry")
    reg = fetch("POST", "/api/template", {"template": REGISTRY_TEMPLATE})
    reg = json.loads(reg) if isinstance(reg, str) else reg
    links = {r["entity_id"]: r for r in reg["entities"]}

    entities, autos = [], []
    for s in states:
        e = s["entity_id"]
        a = s.get("attributes") or {}
        link = links.get(e, {})
        entities.append({
            "entity_id": e, "domain": e.split(".", 1)[0], "name": a.get("friendly_name", e),
            "area": link.get("area"), "floor": link.get("floor"), "device": link.get("device"),
            "device_name": link.get("device_name"), "labels": sorted(link.get("labels") or []),
            "integration": link.get("integration"),
            **{k: a[k] for k in KEEP_ATTRS if k in a},
        })
        if e.startswith(("automation.", "script.")):
            autos.append({"entity_id": e, "id": a.get("id"), "name": a.get("friendly_name", e),
                          "enabled": s.get("state") == "on" if e.startswith("automation.") else True})
    integrations = [{"entry_id": x.get("entry_id"), "domain": x.get("domain"), "title": x.get("title"),
                     "state": x.get("state"), "disabled": bool(x.get("disabled_by"))} for x in entries]
    stamp = now.isoformat(timespec="seconds")
    files = {
        "entities.json": sorted(entities, key=lambda r: r["entity_id"]),
        "areas.json": sorted(reg["areas"], key=lambda r: r["area"]),
        "integrations.json": sorted(integrations, key=lambda r: (r["domain"] or "", r["title"] or "")),
        "automations.json": sorted(autos, key=lambda r: r["entity_id"]),
        "meta.json": {"version": config.get("version"), "time_zone": config.get("time_zone"),
                      "unit_system": (config.get("unit_system") or {}).get("temperature"),
                      "exported": stamp, "entities": len(entities), "integrations": len(integrations)},
    }
    if sources is None:
        return files

    # ---- the existing-house inventory (AGENTS.md, "Phase 0E", step 3)
    by_id = {s["entity_id"]: s for s in states}
    definitions = {}
    for row in files["automations.json"]:
        e = row["entity_id"]
        attrs = by_id[e].get("attributes") or {}
        if e.startswith("automation."):
            d = read_definition(fetch, "automation", attrs.get("id"))
            row.update({"mode": attrs.get("mode"), "last_triggered": attrs.get("last_triggered"),
                        "blueprint": (d or {}).get("blueprint"), "config_sha": (d or {}).get("config_sha")})
            if (d or {}).get("definition"):
                row["definition"] = d["definition"]
        else:
            d = read_definition(fetch, "script", e.split(".", 1)[1])
        definitions[e] = d

    scripts, scenes, helpers = [], [], []
    for s in states:
        e, a = s["entity_id"], s.get("attributes") or {}
        domain = e.split(".", 1)[0]
        name = a.get("friendly_name", e)
        if domain == "script":
            d = definitions.get(e) or {}
            scripts.append({"entity_id": e, "name": name, "state": s.get("state"), "mode": a.get("mode"),
                            "last_triggered": a.get("last_triggered"), "blueprint": d.get("blueprint"),
                            "config_sha": d.get("config_sha")})
            if d.get("definition"):
                scripts[-1]["definition"] = d["definition"]
        elif domain == "scene":
            scenes.append({"entity_id": e, "id": a.get("id"), "name": name})
        elif domain in HELPER_FIELDS or (links.get(e, {}).get("integration") == "template"):
            row = {"entity_id": e, "domain": domain if domain in HELPER_FIELDS else "template", "name": name,
                   "area": links.get(e, {}).get("area")}
            row.update({k: a[k] for k in HELPER_FIELDS.get(domain, ()) if k in a})
            helpers.append(row)

    link_rows = [{"entity_id": e, "integration": r.get("integration"),
                  "name": (by_id.get(e, {}).get("attributes") or {}).get("friendly_name", e)}
                 for e, r in links.items()]
    files["scripts_scenes.json"] = {"source": "states", "status": "ok",
                                    "scripts": sorted(scripts, key=lambda r: r["entity_id"]),
                                    "scenes": sorted(scenes, key=lambda r: r["entity_id"])}
    files["helpers.json"] = {"source": "states", "status": "ok",
                             "helpers": sorted(helpers, key=lambda r: r["entity_id"])}
    files["dashboards.json"] = dashboards_file(sources)
    files["addons.json"] = addons_file(sources, link_rows)
    files["backups.json"] = backups_file(sources)
    files["users.json"] = users_file(sources, now)
    files["blueprints.json"] = blueprints_file(sources, definitions)

    versions = {}
    for key, entity in (("core", "update.home_assistant_core_update"),
                        ("os", "update.home_assistant_operating_system_update"),
                        ("supervisor", "update.home_assistant_supervisor_update")):
        a = (by_id.get(entity) or {}).get("attributes") or {}
        if a:
            versions[key] = {"installed": a.get("installed_version"), "latest": a.get("latest_version")}
    meta = files["meta.json"]
    meta.update({"mode": sources.get("mode"), "versions": versions,
                 "sources": {n: d.get("source") for n, d in files.items() if isinstance(d, dict) and "source" in d},
                 "unknown": sorted(n for n, d in files.items() if isinstance(d, dict) and d.get("status") == "unknown")})
    return files


# ---------------------------------------------------------------- snapshot and the definitions-only diff
DIFF_FILES = ("automations.json", "scripts_scenes.json", "helpers.json", "areas.json", "dashboards.json",
              "integrations.json")
RUNTIME = {"enabled", "state", "last_triggered", "last_changed", "last_updated", "last_reported", "current",
           "entities", "running"}
ROW_KEYS = ("entity_id", "entry_id", "area", "url_path")


def _rows(data):
    if isinstance(data, list):
        return [("", r) for r in data]
    out = []
    for part in ("scripts", "scenes", "helpers", "dashboards"):
        for r in (data or {}).get(part) or []:
            out.append((part, r))
    return out


def _row_key(part, row):
    for k in ROW_KEYS:
        if k in row:
            return f"{part + ' ' if part else ''}{row[k] if row[k] is not None else '(default)'}"
    return part + " " + json.dumps(row, sort_keys=True)


def _blind(rows):
    """{row key: kind} for the automations and scripts whose definition the export could not fingerprint:
    `yaml` (config_sha null and an id: no UI definition), `no id` (an automation without one) or the
    `unreadable (<status>)` the GET answered. A row without a config_sha field (the --basic export, the
    script rows of automations.json) is not a definition row."""
    out = {}
    for part, r in rows:
        if "config_sha" not in r or r["config_sha"] is not None:
            continue
        e = str(r.get("entity_id", ""))
        if r.get("definition"):
            out[_row_key(part, r)] = r["definition"]
        elif e.startswith("script.") or r.get("id"):
            out[_row_key(part, r)] = "yaml"
        else:
            out[_row_key(part, r)] = "no id"
    return out


def _blind_lines(name, blind):
    """The unknown lines for one file's unfingerprinted rows (PROC: two recitations are not a diff)."""
    out = []
    kinds = {}
    for k, kind in blind.items():
        kinds.setdefault(kind, []).append(k)
    noun = "scripts" if name == "scripts_scenes.json" else "automations"
    if kinds.get("yaml"):
        n = len(kinds["yaml"])
        out.append(f"{name}: {n} {noun if n != 1 else noun[:-1]} {'have' if n != 1 else 'has'} no UI definition to "
                   f"fingerprint (YAML); compare their files with git")
    if kinds.get("no id"):
        n = len(kinds["no id"])
        out.append(f"{name}: {n} {noun if n != 1 else noun[:-1]} {'have' if n != 1 else 'has'} no id, so no "
                   f"definition to fingerprint; compare their files with git")
    for kind in sorted(k for k in kinds if k.startswith("unreadable")):
        n = len(kinds[kind])
        out.append(f"{name}: {n} {noun if n != 1 else noun[:-1]} with the definition {kind}; check the token is an "
                   f"administrator's and export again")
    return out


def diff(a_dir, b_dir):
    """(differences, unknowns): definitions only; a file that is person-sourced or unknown on either side is an
    unknown, never a pass. So is an automation or script whose definition neither export could fingerprint
    (YAML-only, no id, or a failed read): its body is outside the comparison, so the file cannot answer `pass`."""
    differences, unknowns = [], []
    for name in DIFF_FILES:
        fa, fb = pathlib.Path(a_dir) / name, pathlib.Path(b_dir) / name
        if not fa.exists() or not fb.exists():
            unknowns.append(f"{name}: missing in {'the first' if not fa.exists() else 'the second'} export")
            continue
        a, b = json.loads(fa.read_text()), json.loads(fb.read_text())
        if any(isinstance(x, dict) and (x.get("source") == "person" or x.get("status") == "unknown")
               for x in (a, b)):
            unknowns.append(f"{name}: person-sourced or unknown, not compared")
            continue
        ra = {_row_key(p, r): {k: v for k, v in r.items() if k not in RUNTIME} for p, r in _rows(a)}
        rb = {_row_key(p, r): {k: v for k, v in r.items() if k not in RUNTIME} for p, r in _rows(b)}
        if name in ("automations.json", "scripts_scenes.json"):
            unknowns += _blind_lines(name, {**_blind(_rows(a)), **_blind(_rows(b))})
        for k in sorted(set(ra) | set(rb)):
            if k not in rb:
                differences.append(f"{name}: {k} removed")
            elif k not in ra:
                differences.append(f"{name}: {k} added")
            elif ra[k] != rb[k]:
                fields = sorted(f for f in set(ra[k]) | set(rb[k]) if ra[k].get(f) != rb[k].get(f))
                differences.append(f"{name}: {k} changed ({', '.join(fields)})")
    return differences, unknowns


def write(files, out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (out / name).write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n")


def snapshot(files, out, name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name or ""):
        raise SystemExit("export: a snapshot name is lowercase letters, digits and dashes (phase0e-start)")
    target = pathlib.Path(out) / ("." + name)
    if target.exists():
        raise SystemExit(f"export: snapshot {target} already exists and is written once; compare with --diff")
    write(files, target)
    return target


def _resolve(out, ref):
    p = pathlib.Path(ref)
    return p if p.is_dir() else pathlib.Path(out) / ("." + ref)


def gather_sources(config_dir=None, env=None):
    """Which way the export reads: inside the app (SUPERVISOR_TOKEN set and /homeassistant/.storage there) the
    configuration folder and the Supervisor; from a computer the websocket, plus --config when given."""
    env = os.environ if env is None else env
    sup_token = env.get("SUPERVISOR_TOKEN")  # guard: allow reads the environment, holds no value
    if config_dir is None and sup_token and (pathlib.Path(ADDON_CONFIG) / ".storage").is_dir():
        config_dir = ADDON_CONFIG
    src = {"mode": "addon" if sup_token else "computer", "config_dir": config_dir}
    if config_dir:
        src["storage"] = storage_reader(config_dir)
    if sup_token:
        src["supervisor"] = supervisor_fetch(sup_token)
    return src


def confirmed_access(root=".", profile_path="house/profile.yaml", url=None):
    """Shared file-first credential policy; verify the owner's target before credential lookup."""
    import importlib.util
    path = pathlib.Path(__file__).resolve().parents[1] / "tools/ha_read.py"
    if not path.is_file():
        path = pathlib.Path(root).resolve() / "templates/tools/ha_read.py"
    spec = importlib.util.spec_from_file_location("_kit_export_access", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.confirmed_access(root, profile_path, url=url)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(pathlib.Path(__file__).resolve().parent), help="folder to write (default: this one)")
    ap.add_argument("--url", default=os.environ.get("HA_URL"), help="default: $HA_URL, e.g. http://<address>:8123")
    ap.add_argument("--root", default=".", help="household repository root")
    ap.add_argument("--profile", default="house/profile.yaml", help="owner-confirmed target profile")
    ap.add_argument("--config", help="a copy of the configuration folder (with .storage/) to read from a computer")
    ap.add_argument("--snapshot", metavar="NAME", help="also write the export once to <out>/.<NAME>/")
    ap.add_argument("--diff", nargs=2, metavar=("A", "B"), help="compare two exports on definitions only; no network")
    ap.add_argument("--basic", action="store_true", help="the original five files only")
    args = ap.parse_args(argv)
    if args.diff:
        a, b = (_resolve(args.out, x) for x in args.diff)
        differences, unknowns = diff(a, b)
        for line in differences:
            print("changed  " + line)
        for line in unknowns:
            print("unknown  " + line)
        verdict = "fail" if differences else ("unknown" if unknowns else "pass")
        print(f"diff: {verdict} ({len(differences)} definition changes, {len(unknowns)} parts not compared)")
        sys.exit({"pass": 0, "fail": 1, "unknown": 2}[verdict])
    try:
        args.url, token = confirmed_access(args.root, args.profile, args.url)
    except Exception:
        sys.exit("export: confirmed profile and private credential required; see install/agent-access.md")
    sources = None
    if not args.basic:
        sources = gather_sources(args.config)
        if "storage" not in sources or "supervisor" not in sources:
            sources["ws"] = lazy_ws(args.url, token)
    files = build(http_fetch(args.url, token), sources=sources)
    run_report(files, args.out, args.snapshot)


def run_report(files, out, snapshot_name=None):
    write(files, out)
    m = files["meta.json"]
    print(f"export: {m['entities']} entities, {m['integrations']} integrations, Home Assistant {m['version']} "
          f"-> {out}")
    if "sources" in m:
        print("export: read " + ", ".join(f"{n.removesuffix('.json')} from {s}" for n, s in sorted(m["sources"].items())))
        if m["unknown"]:
            print("export: unknown (the person reads these to the agent): " + ", ".join(m["unknown"]))
    if snapshot_name:
        print(f"export: snapshot -> {snapshot(files, out, snapshot_name)}")


if __name__ == "__main__":
    main()
