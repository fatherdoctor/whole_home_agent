"""ha_stub.py - a small stand-in for Home Assistant's template engine, for offline tests of the kit's macros.

Status: template (O3b, 2026-10-13). Copied with the macros so the house can keep testing them after it edits them.

Renders the SAME custom_templates/*.jinja files Home Assistant loads, in the same immutable sandbox, with stand-ins
for the template functions the macros use (now, states, is_state, state_attr, expand, as_timestamp, timestamp_custom,
is_number, from_json, to_json, config_entry_id, config_entry_attr).
It is not Home Assistant: render the real thing in Settings > Tools > Template on the box before you trust a change.
A function the stand-in lacks fails loudly (StrictUndefined), so a macro cannot silently pass on a missing name.

Needs jinja2 (pip install jinja2).
"""
import json
import pathlib
from datetime import datetime, timedelta, timezone

import jinja2
from jinja2.sandbox import ImmutableSandboxedEnvironment

MACROS = pathlib.Path(__file__).resolve().parents[1] / "custom_templates"


def parse(s):
    d = s if isinstance(s, datetime) else datetime.fromisoformat(str(s))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


class State:
    """spec: a bare state, or {state, attributes, changed_min_ago, reported_min_ago, entry_state}.
    entry_state: the state of the config entry that owns the entity ("loaded", "setup_retry", ...); leave it out
    for an entity no integration entry owns (a helper)."""

    def __init__(self, entity_id, spec, now):
        spec = spec if isinstance(spec, dict) else {"state": spec}
        self.entity_id = entity_id
        self.domain, self.object_id = entity_id.split(".", 1)
        self.state = str(spec.get("state"))
        self.attributes = spec.get("attributes") or {}
        self.last_changed = now - timedelta(minutes=spec.get("changed_min_ago", 24 * 60))
        self.last_updated = self.last_changed
        self.last_reported = now - timedelta(minutes=spec.get("reported_min_ago", spec.get("changed_min_ago", 24 * 60)))
        self.name = self.attributes.get("friendly_name", entity_id)
        self.entry_state = spec.get("entry_state")


class States:
    def __init__(self, store):
        self._store = store

    def __call__(self, entity_id):
        s = self._store.get(entity_id)
        return s.state if s else "unknown"

    def __getattr__(self, name):
        if name.startswith("_") or name in ("unsafe_callable", "alters_data"):
            raise AttributeError(name)
        raise AttributeError(f"stub: use states('<id>') or expand('<id>'), not states.{name}")


def env_for(states, now):
    now = parse(now)
    store = {e: State(e, spec, now) for e, spec in (states or {}).items()}

    def as_timestamp(v, default=None):
        try:
            if v in (None, "", "unknown", "unavailable"):
                return default
            return parse(v).timestamp()
        except (TypeError, ValueError):
            return default

    def is_number(v):
        try:
            float(v)
            return str(v).strip().lower() not in ("nan", "inf", "-inf", "")
        except (TypeError, ValueError):
            return False

    def expand(*ids):
        out = []
        for i in ids:
            for x in (i if isinstance(i, (list, tuple)) else [i]):
                if x in store:
                    out.append(store[x])
        return out

    def timestamp_custom(ts, fmt="%Y-%m-%d %H:%M:%S", local=True, default=None):
        try:
            return datetime.fromtimestamp(float(ts), timezone.utc).strftime(fmt)
        except (TypeError, ValueError):
            return default

    def config_entry_id(entity_id):
        s = store.get(entity_id)
        return "entry_" + entity_id if s is not None and s.entry_state is not None else None

    def config_entry_attr(entry_id, attr):
        # Home Assistant raises on a non-string id and on any attribute outside its list; so does the stand-in.
        if not isinstance(entry_id, str):
            raise jinja2.TemplateError("Must provide a config entry ID")
        if attr not in ("domain", "title", "state", "source", "disabled_by", "pref_disable_polling"):
            raise jinja2.TemplateError("Invalid config entry attribute")
        s = store.get(entry_id[len("entry_"):])
        return s.entry_state if (s is not None and attr == "state") else None

    env = ImmutableSandboxedEnvironment(loader=jinja2.FileSystemLoader(str(MACROS)), undefined=jinja2.StrictUndefined)
    env.globals.update(now=lambda: now, states=States(store), expand=expand, as_timestamp=as_timestamp,
                       is_state=lambda e, v: e in store and store[e].state == v,
                       state_attr=lambda e, a: store[e].attributes.get(a) if e in store else None,
                       config_entry_id=config_entry_id, config_entry_attr=config_entry_attr)
    env.filters.update(as_timestamp=as_timestamp, is_number=is_number, to_json=json.dumps, from_json=json.loads,
                       timestamp_custom=timestamp_custom)
    env.tests.update(is_number=is_number)
    return env


def render(source, states=None, now="2026-01-15T12:00:00+00:00", **context):
    """Render `source` against `states` at `now`; `context` becomes template variables (as a script's fields do)."""
    return env_for(states, now).from_string(source).render(**context)
