# Templates

*Status: written (O3b, 2026-10-13). The starting files Phase 1 copies into `house/` and fills from the profile, per
`interview/generated-files.md` (the contract: which file, made from which answers, needed before what). Every file
says at its top where it goes and what to fill; search for `FILL`.*

## Runtime (every runtime, first)

| Template | Goes to | What it is |
|---|---|---|
| `runtime/STEP-0.md` | stays in the kit; every brief points at it | The "where am I" block each run does first: observe the runtime, probe what it can do, record it, name the fallbacks in one line. |
| `runtime/FALLBACKS.md` | stays in the kit | For each capability the kit relies on, what the kit does without it and who pays. The only place besides `adapters/agents/` that names a vendor feature. |
| `runtime/claude-code-settings.json` | merged into `.claude/settings.json` (level 0) | The secrets deny list: the agent's file tools may not read or edit `secrets.yaml`, `.storage/`, the recorder database, backups or credential files. Other runtimes deny the same paths their own way (`adapters/agents/other-agents.md`). |
| `runtime/runtime.yaml` | `house/runtime.yaml` | One entry per runtime the household uses: roles mapped to models, capabilities as yes / no / unknown, the fallbacks in use. |

`runtime/README.md` has the six rules every kit file follows so the kit stays runtime-neutral.

## Packages (Home Assistant configuration)

Copy each with its macro file. The macros hold the logic once; the packages only wire it up; the tests check the
macros offline.

| Template | Goes to | What it is |
|---|---|---|
| `packages/notification-router.yaml` | `ha/packages/notification_router.yaml` | `script.notify`, the one entry point for every phone push: classes, per-phone levels, owner-only maintainer class, life safety past every dial, tags and shared slots, Dismiss on every push, Dismiss-only for minors, critical only for alarm and life safety, a dry run that logs `notify_router_call`; `script.notify_clear`; the "notifications switched off" push. |
| `custom_templates/notify.jinja` | `ha/custom_templates/notify.jinja` | The router's decisions: class, slot, recipients, per-platform payload. |
| `packages/health-check.yaml` | `ha/packages/health_check.yaml` | One `sensor.health_<subsystem>` per subsystem (state = faults; attributes notices, severity, findings), threshold helpers, planned-restart suppression, the fault push and the all-clear that needs an alert-open flag. |
| `custom_templates/health.jinja` | `ha/custom_templates/health.jinja` | The house's check list (CHECKS) and one macro per check kind: battery, unavailable, silent, enabled, age, mesh, is_on. |

Both packages need `homeassistant: packages: !include_dir_named packages` in `configuration.yaml`, and the
router must be in place before the health checks (health pushes go through it).

## Documents

| Template | Goes to | What it is |
|---|---|---|
| `docs/CHANGELOG.md` | `house/docs/CHANGELOG.md` | Dated entries, newest first: why, authorized, changed, checks, undo. |
| `docs/gotchas.md` | `house/docs/gotchas.md` | One lesson per entry, by area: the rule, the incident, how to check. |
| `docs/backlog.md` | `house/docs/backlog.md` | Rulings, questions for the owner, and the items the generation always adds, sized. |
| `docs/board.md` | `house/docs/board.md` (level 2) | The board: one row per card with a status word, a run log with est/actual; five seed rows. Grammar: `docs/board-format.md` (both the level-2 subset and the level-6 form with the Plans, Sprints and Epics sections, tokens and the PLAN line). Chapter: `principles/board-and-lanes.md`. |
| `docs/card-names.tsv` | `house/docs/card-names.tsv` | One plain-English line per card, added in the same commit as the card. |
| `docs/board-slice-outline.md` | stays in the kit; the house's agent writes `house/docs/board_slice.py` from it | A tool outline: one command prints the few KB of the board a lane or the planner needs, with the board check's parser and one eligibility rule shared with the preflight (`principles/board-and-lanes.md` rule 20). |
| `docs/router-replay-outline.md` | stays in the kit; the house's agent writes the replay tool from it | A tool outline: rebuild the last weeks of real pushes and the settings history, run them through the old and new router side by side, report every difference before the apply (`principles/testing-and-simulation.md` rule 14). |
| `docs/review.md` | `house/docs/reviews/<CODE>-<date>.md` | A review file: verdict, findings by severity (reproduced or reasoned, each with its fix), what held, enactment, the author's response, the closure. |
| `docs/board_check.py` | stays in the kit; run from the house root | Checks a board against the grammar (cells, status words, unique codes, tokens, closers, plain names, run-log shapes); exit 0 clean, 1 faults. Its `parse_board` is the parser the board view and page share. |
| `docs/user-manual/README.md` | `house/docs/user-manual/README.md` | The household manual's skeleton: household and guest tracks, plain words, changes through `NOTES.md`. |
| `docs/wiki/SCHEMA.md` | `house/docs/wiki/SCHEMA.md` | The maintainer wiki's v1 schema and writer brief: three page kinds, one citation form, generated facts. |

## The tier-2 support agent (only when wanted, and built last)

| Template | Goes to | What it is |
|---|---|---|
| `tier2/BRIEF.md` | `house/tier2/BRIEF.md` | The agent's standing brief: levels, the never list, race rails, the playbook table, pushes, check-ins. |
| `tier2/checker.py` | `house/tier2/checker.py` | The deterministic 5-minute checker: findings by id, wakes the model with the id only, heartbeat, self-heal. `--selftest` runs offline. |
| `tier2/IDLE.md`, `tier2/OUT-OF-BAND.md` | `house/tier2/` | The agent's two run-time lists: read-only idle work the owner allows, and the jobs only an on-box session can do. |

## Assistant usage card (level 0-1, so the household sees its budget before it climbs)

| Template | Goes to | What it is |
|---|---|---|
| `runtime/usage_reader.py` | `house/usage/usage_reader.py` | Reads the assistant account's 5-hour and weekly use from its login (no model call, the token never stored or refreshed), works out today's use, writes one JSON file into Home Assistant's config folder every 15-30 minutes. Setup: `runtime/README.md`, "The usage reader". Another runtime has its own reader in `runtime/` writing the same file, copied beside this one; `runtime/README.md` lists it and its adapter page under `adapters/agents/` gives the setup. |
| `packages/assistant-usage.yaml` | `ha/packages/assistant_usage.yaml` | The file as `sensor.assistant_usage_read`; week, today, session, pace line and read-age sensors; the weekly warning level and daily budget helpers; the view picker; a stale sensor; a threshold sensor that stays off until the household turns it on. |
| `custom_templates/usage.jinja` | `ha/custom_templates/usage.jinja` | The rules once: stale or reset figures are unknown, the pace line, the threshold test, the bars and numbers views. |
| `dashboards/assistant-usage-card.yaml` | a dashboard card | One card, three views (linear bars with a two-week line chart, plain numbers, tachometer dials), built-in cards only. |

## Pacing (only when unattended runs are wanted)

| Template | Goes to | What it is |
|---|---|---|
| `pacing/usage_probe.sh` | `house/pacing/usage_probe.sh` | Reads the account's usage screen at no token cost; writes `latest.txt`. |
| `pacing/pace_gate.py` | `house/pacing/pace_gate.py` | The budget gate: pace line, model figure, stale read (over 2 h), last week's read; reads the usage reader's JSON or the probe's text; exit 0 = run, 1 = skip. |
| `pacing/preflight.py` | `house/pacing/preflight.py` | The no-model preflight every scheduled run passes before the agent starts: off switch, an eligible row (one `eligible()` shared with the board slice), the budget (percentage or count mode), an API-key monthly cap; monitoring always GO, only its idle work gated. |

## Live export

| Template | Goes to | What it is |
|---|---|---|
| `export/export_house.py` | `house/export/export_house.py` | Standard library only. Writes `entities.json` (ids with area, floor, device, labels, integration; no live states), `areas.json`, `integrations.json`, `automations.json`, `meta.json`, sorted for clean diffs. `HA_URL` and an admin `HA_TOKEN` from the environment, never the command line. Run before a plan names an entity, then run the guard. |
| `export/first_look.py` | `house/export/first_look.py` | The first look at an existing house (Phase 0E, KIT-EXIST.b2): twelve read-only checks over the export and the box, written to `house/docs/first-look.md` (and `inventory.md` with `--inventory`), each finding a fault, risk or notice with its evidence, rule and offer; a check that cannot read its source answers `unknown`. `--config <dir>` for a copy of the configuration folder, `--offline <dir>` for tests. Never prints a secret, an error text or a user's name. |
| `docs/first-look.md`, `docs/inventory.md` | `house/docs/` | The two pages' shapes; `first_look.py` fills them. |

## Guard

| Template | Goes to | What it is |
|---|---|---|
| `guard/push_guard.py` (+ `selftest.py`, `names.example.txt`) | `guard/push_guard.py`, `selftest.py`, `names.example.txt` (owner writes `names.txt` privately) + a pre-push hook | Refuses a push carrying a token, a literal password, a private key, a phone number, a word on the household's `names.txt`, `secrets.yaml`, `.storage/` or a backup; exit 0 = clean, 1 = refused. Install: `guard/README.md`. |

## Tests

`tests/test_templates.py` renders the macros in a stand-in for Home Assistant's template sandbox
(`tests/ha_stub.py`), drives the pace gate and the checker with fixtures, renders the router script's own
templates the way Home Assistant chains them, and loads every YAML file. Run it before copying a template and
after the house changes one, from the repository root:
`python3 -m venv .venv && .venv/bin/pip install jinja2 pyyaml && .venv/bin/python templates/tests/test_templates.py`
(a virtual environment, because many systems refuse a plain `pip install`). Copy
`tests/` into the house with the macros and keep adding a case per change. The stand-in is not Home Assistant:
the final check is Settings > Tools > Template on the box, and the config check.
