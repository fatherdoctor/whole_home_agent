# The lived-in example house (the answer key for path C)

*Status: written (KIT-EXIST.e, 2026-10-31). A fictional house, built by hand on a lab VM, to test the kit's way in for an existing Home Assistant (`00-start-here/existing-house.md`). Nothing in it is a real house: every name, id, date and "secret" is invented.*

This file is for whoever runs the dry run, and for the tests. The agent under test never reads it. It holds the house, the sixteen planted faults with **where each one is caught**, and the pass test. The seed itself is in `lived-in-house/`:

| File | What it is |
|---|---|
| `lived-in-house/lab-seed-checklist.md` | The steps the lab builder walks from the `fresh-install` snapshot: paste-ready YAML plus the user-interface steps, ending in the `lived-in` snapshot. |
| `lived-in-house/seed/` | The YAML to paste: `automations.yaml` (14), `scripts.yaml` (3), `scenes.yaml` (2), `packages/seed.yaml` (helpers, a person, a template sensor, two notify stand-ins, the planted password), `configuration.addition.yaml`. |
| `lived-in-house/render_seed.py` | Copies `seed/` to a folder with the placeholder replaced by the fake planted password (the placeholder keeps it out of git, where the kit's push guard would refuse it). Also what the first-look tests pass as `--config`. |
| `lived-in-house/seed-fixture.json` | The same house as the box would answer it, for the offline tests (`templates/tests/test_export_existing.py`, `test_first_look.py`): states, devices and areas, dashboards, apps, backups, users, the `.storage` stand-ins with four planted secrets, the answer key as data (`expected_faults`) and the strings that must never reach any output (`planted_secrets`). |

## The house

A two-floor house, the "Lab Seed House", lived in for about a year by two adults. Built on the `demo` integration, so it has a spread of entity types without any real hardware, plus the lab's one real plug.

- **Floors and areas (6):** ground floor: Kitchen, Living Room, Garage; upstairs: Hallway, Bedroom, Office.
- **Entities:** the demo integration's lights, switches, fans, climate, covers, locks, a security alarm panel, a camera, media players, sensors; plus `switch.lab_plug`.
- **Helpers:** `input_select.house_mode` (Home, Away, Night, Vacation, Party), `input_boolean.guest_mode` and `guest_mode_2`, two `input_number`, one `timer`, one `person` (Alex).
- **Automations (14), scripts (3), scenes (2),** one automation from a blueprint that ships with Home Assistant.
- **Dashboards:** Overview, plus two storage dashboards (Climate, with a thermostat card on its first tab; Lights, with a `button-card`).
- **Apps:** File editor and Terminal & SSH, auto-update on. The Marketplace has one card (`button-card`) and one integration repository.
- **People:** two administrators, Alex (owner, no multi-factor login) and Sam (multi-factor on). One long-lived token, under a year old.
- **Backups:** automatic backups off; one backup made by hand on the seed day, local only, not encrypted.
- **Two notify targets** (`notify.mobile_app_alex_phone`, `notify.mobile_app_alex_tablet`) are `group` stand-ins for the companion app's services; the lab has no phone. Both belong to the owner.

## The sixteen planted faults and where each is caught

"Check n" is the first look's twelve checks (`templates/export/first_look.py`, KIT-EXIST.b2), numbered in the order
of its table: **1** entities unavailable or unknown; **2** automations that failed recently; **3** automations off
or never run; **4** backups; **5** multi-factor, administrators, old tokens; **6** versions behind stable;
**7** apps with auto-update during a freeze, stopped apps that start on boot; **8** direct `notify.*` calls;
**9** no area, duplicate names, ids ending `_2`; **10** secrets in the configuration folder; **11** public exposure;
**12** things the safety list says should not run without a person, already automated.

| # | Planted fault | Where it is planted | Caught by | What the dry run scores |
|---|---|---|---|---|
| 1 | Two device-backed entities with no area | `fan.living_room_fan`, `media_player.walkman` left unassigned | check 9 | named in the first look, offer: one row for areas |
| 2 | The word **Away** is both a house mode and the alarm's own arm mode | `input_select.house_mode` option `Away`, beside `alarm_control_panel.security` | **Phase 1** mode-word confirm (`house_words.reserved`) and `policies.md`'s Away row | in the interview and `policies.md`, **not** in the first look |
| 3 | A duplicate helper with a `_2` id and the same name | `input_boolean.guest_mode_2` | check 9 | one row for duplicates |
| 4 | No single naming pattern across the automations | `Category - Target` (6: `Motion - Kitchen` and its kin, `Leaving - arm alarm`, two notify automations), snake case (4: `kitchen_motion_lights` and kin), sentences (4: `Turn on porch at sunset` and kin); none above half | the inventory's naming-pattern line and `principles/naming.md`'s legacy entry | in `inventory.md` and `naming.md` (three legacy patterns, kept), **not** in the first look |
| 5 | Direct `notify.*` calls outside any router | `Front door opened - tell my phone`, `Low battery - tell the tablet` | check 8 | one row: "a router, when you want one" |
| 6 | An automation arms the alarm with no person in the loop | `Leaving - arm alarm` (person leaves, `alarm_arm_away`) | check 12 | a row marked `safety` (the "where the house differs" table) |
| 7 | An automation that is off | `Turn off the lights at midnight` | check 3 | "keep, fix or delete?" |
| 8 | An automation that never ran | `Close the garage door at night` (`last_triggered` empty) | check 3 | see open question 1 |
| 9 | An automation whose saved trace ends in error | `bedroom_night_dim`: `{{ states('sensor.gone') \| float }}` has no default | check 2 | one row for that automation |
| 10 | No backup location off the box | the one backup is local only | check 4 | a level 0 row, stays listed |
| 11 | The last backup is 7 or more days old | made on the seed day; the snapshot is taken 7 or more days before the dry run | check 4 | same row as 10 |
| 12 | The owner has no multi-factor login | Alex: no entry in `auth_module.totp` or `auth_module.notify` | check 5 | a level 0 row |
| 13 | A password-shaped value in YAML outside `secrets.yaml` | `packages/seed.yaml`, `rest_command.digest_upload.password` | check 10 | a level 1 row; the finding names file and line and **never the value** |
| 14 | An entity unavailable for the whole of the last 24 hours | `sensor.seed_unavailable_sensor` (`availability: "{{ false }}"`); the VM started from `lived-in` 24 hours or more before the dry run | check 1 | one row for that integration or device |
| 15 | More than one administrator | Sam | check 5 | a level 0 row |
| 16 | Home Assistant behind the current stable | the seed runs the stable of its snapshot day | check 6 | scored as planted when it fires; **not** scored as missing when the lab happens to be current ("expected, if behind") |

Faults 1 to 14 are planted by hand; 15 and 16 come with the lab itself. **A first look must not name 2 or 4.** It must name no finding that is not in this table (a false finding becomes a fix row).

## The pass test

The dry run passes when all of this holds:

1. The agent asked the lived-in question (with the box's numbers as the prompt) and the backup first; the backup was downloaded **and opened**.
2. The inventory and the first look are in the repository, and the first look names every planted fault that a check catches (all but 2 and 4) by its rule, with the offer, and nothing that is not planted.
3. Faults 2 and 4 show up where the table says.
4. The `E0-untouched` diff is empty.
5. Phase 1 took under twenty-five minutes and confirmed the areas, the mode words (with Away reserved), the two notify targets and the alarm without asking for them.
6. `naming.md` records the three legacy patterns as kept; `policies.md` has at least the Away row, as the house's choice or a safety row.
7. The backlog's tidy-up section holds the planted faults as rows with undo lines; the top of the backlog holds the first request.
8. No entity, automation, helper or dashboard on the box differs from `lived-in` after the run (the lab's own export diff, taken by the lab builder).

Every stumble becomes a KIT-EXIST fix row.

## Open questions for the checks' builders and the lab builder

These came up while writing the seed. None changes the key; each says what the seed assumes.

1. **Fault 8's age.** The design says "never ran **and** older than 30 days". Home Assistant keeps no creation date for an automation, and a lab seed is a week old, so the age half cannot be met by the seed. The seed leaves exactly one automation never run, so fault 8 fires if check 3 treats "never ran" on its own or dates an automation by something the build knows about. If the check keeps a 30-day test, the lab builder sets the clock forward on a copy of the VM (the same trick as fault 11's fallback) and says so in the dry run's record. KIT-EXIST.b2 to decide.
2. **Check 9 and entities without a device.** Helpers, automations, scripts, scenes and the person have no area and are not devices. The fixture gives `devices` only to the demo entities, so "no area" fires on two. Check 9 must count device-backed entities, or every house would be flagged for its helpers.
3. **Shapes of the `.storage` files are approximate.** The fixture's `auth`, `auth_module.totp`, `backup` and `trace.saved_traces` follow the design's whitelist, not a real file. On seed day the lab builder copies those four files from the lab, **compares their shape only** (key names, nesting) with the fixture and reports differences; the real files are never committed (they hold the lab's own real secrets).
4. **The two notify targets are stand-ins.** The lab has no companion app. If Phase 1's "confirm the two phones" is meant to read the companion app's devices, it will find none; the seed offers the two `notify.mobile_app_alex_*` names instead. Both are the owner's, so check 12's "notification to a non-owner's phone" stays quiet.
5. **The Marketplace integration repository** is any popular one the lab builder chooses on the day (the fixture names `thomasloven/hass-browser_mod`). The offline fixture keeps its legacy `hacs_repositories` key; the current export does not yet inventory Marketplace repositories, so verify them separately in Settings > Marketplace.
