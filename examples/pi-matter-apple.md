# Worked example: a Pi 5 house with Matter, Thread and Siri

*Status: written (O4, 2026-10-14). A fictional house (a couple, a nine-year-old, a dog and a weekday dog walker; a
Raspberry Pi 5 on NVMe; Matter over Thread and Wi-Fi; Apple Home; the companion app on two iPhones; an agent other than
the kit's first runtime) taken from Phase 0 to the plans for its first five backlog items. Deliberately different from the
install the kit came from. Everything here is invented: names, times, ids.*

This is the walk **as it went on the kit before the dry run's fixes**: each `[GAP n]` is a place the agent had to
guess or found the kit wrong, numbered as in `dry-run-2026-10-14.md`, which says what was fixed and what is still
open. Read it for the shape of a real session: what the agent asked, what it wrote, and how a plan is laid out.
Where a gap is now fixed, the current kit gives the answer the agent lacked; "After the fixes" at the end lists
what would go differently today.

Opening line (AGENTS.md "Open every session with one line"): "Phase 0 (no `house/profile.yaml`); I read AGENTS.md; I propose to run the setup interview, then walk `install/raspberry-pi.md`."

Agent-side setup before question 1: no rules-file convention for my tool, so I was told by the person to "read AGENTS.md" [GAP 10]. Created `house/` in the cloned kit; the kit's remote is the public one, so I asked where the house is committed and had to invent an answer (a new private repo, kit copied in) [GAP 1]. Created `house/docs/`, `house/ha/packages/`, `house/ha/custom_templates/`, `house/export/` [GAP 2]. Copied `interview/profile-template.yaml` to `house/profile.yaml`.

---

## Phase 0 - setup interview (about 15 minutes)

The person's first message: "I just bought a Raspberry Pi 5 with an NVMe hat and want to run Home Assistant for my family. Read AGENTS.md and start." Taken from the message: Pi 5, NVMe, new (hardware, storage).

**Topic 1 - where and when.** Timezone: the computer reports America/Denver -> `timezone: America/Denver`. Language: en-US. Time today: "two hours, stop at 4 pm" (writes nothing).

**Topic 2 - hardware.** Already bought (so the "if buying" rows do not apply; the default text says a Pi only if "already own one with an SSD", which fits only by luck) [GAP 3]. Pi 5, 8 GB, NVMe on an M.2 HAT, "I think there is a power supply, a case with a fan". -> `hardware: raspberry-pi`, `install_guide: install/raspberry-pi.md`, `storage: nvme`.

**Topic 3 - network.** Router is the ISP's unit; they have its app and never reserved anything. Router control: "maybe; there is a Devices screen" -> default "find out together" -> `router_control: null` first, set `true` after step 1 of the guide succeeded (see below) [GAP 4: where does `assumed` go for a scalar?]. Wired: yes, the Pi sits next to the router -> `wired: true`. Remote access: not now -> `none`. 2.4 GHz: assume yes (assumed) -> `wifi_24ghz: true` [GAP 6: ISP routers with one SSID for both bands/band steering, mDNS/IPv6 not asked].

**Topic 4 - radios and devices owned.** Owned: "five Matter plugs that work over Wi-Fi, a Home Assistant Connect ZBT-1 stick, a HomePod mini". Radio for new devices: Matter over Thread (matches the default row), plus the Wi-Fi plugs [GAP 5: no value for Matter-over-Wi-Fi]. Voice: Apple. -> `radios: [matter-thread, wifi]`, `voice: [apple]`.

**Topic 5 - notifications.** Two iPhones; the child has an iPad and no companion app. -> `notification_channels: [companion-app]`, `phone_platforms: [ios, ios]` (an iPad is not a "phone") [GAP 21]. Text/call: later.

**Topic 6 - backups off the box.** They pay for iCloud, nothing else. The default "a cloud drive the person already pays for" leads nowhere: Home Assistant has no iCloud backup location. I had to look at the network guide's list (Google Drive, OneDrive, Home Assistant Cloud, a share) and propose a free Google account used only for this [GAP 8]. -> `backup_offbox: cloud-drive`. Emergency kit: Apple Passwords app plus a printed sheet -> `emergency_kit: both`.

**Topic 7 - the agent and its budget.** Agent: "other", runs on the laptop in this folder. Plan: a pay-as-you-go API key with a monthly spend cap; no usage screen -> `usage_probe: false`. Reserve 10 %/20 % kept as defaults though there is no weekly percentage to apply them to [GAP 9]. Review: daily. Agent access to the box was not asked here or anywhere in Phase 0 [GAP 11].

**Close Phase 0 (step 1).** Read the `setup:` block back in plain words; `setup.interviewed_on: 2026-10-14`. Guide: `install/raspberry-pi.md`, about an hour.

### Walking `install/raspberry-pi.md` then `install/network-and-backups-first.md`

- "Ask which Pi model and how much RAM before step 1": asked; Pi 5, 8 GB.
- "Before you start" requires a microSD A2 card; the person has none and an NVMe drive. The guide's NVMe sentence gives no steps. I improvised: image to the NVMe through a USB enclosure the person borrowed, then into the HAT, no SD, HDMI cable ready [GAP 7]. Imager menu path as in the guide ("Other specific-purpose OS > Home automation > Home Assistant"): matched on the person's screen; choose "Raspberry Pi 5".
- Power supply: the official 27 W unit; fan case with the HAT clearance checked by the person.
- Onboarding step 1 (find the address and reserve it): the ISP app lists "homeassistant" under Devices with a "Fixed IP" toggle. The guide said "log in to the router's admin page"; nothing covers an app-only router, nor what to do if there is no toggle (guide contradiction on a static fallback) [GAP 6]. Reserved.
- Onboarding steps 2 to 8: owner "Alex", location, time zone, units; skipped discovered devices; updates installed one at a time.
- Network-and-backups-first section 1: address written in the Apple Passwords note; bookmarked on laptop and both iPhones.
- Section 2 remote access: none chosen. MFA: the section says "your user profile, Multi-factor authentication modules"; the person did not see it until Advanced mode was on [GAP 15].
- Section 3 backups: Set up backups; emergency kit downloaded to Apple Passwords and printed; daily 03:00; before-update on; keep 7; media off; location: Google Drive integration, encrypted (the person signed in themselves; the agent never saw it). Manual backup appears in both places. One backup downloaded to the laptop (size sensible).
- Section 4 updates: read, noted.
- Section 5 giving the agent access: **not in "Done when"**; the person asked "how does the agent see the house?" and the kit has no steps; fell back to "person reads Settings pages to the agent" (manual mode) [GAP 11, 12]. The companion apps were not part of Phase 0 either; the person installed them when asked and I had no steps for device names or permissions [GAP 14].

**"Done when" check (all 7 boxes ticked, one at a time with the person):**
- [x] address reserved and written down off the box
- [x] `http://<address>:8123` opens on a computer and a phone, bookmarked on both
- [x] MFA on for the owner account
- [x] automatic daily backups, keep 7, before-update on
- [x] one off-box location (Google Drive), encrypted, holding a backup
- [x] emergency kit in two places (Apple Passwords, printed), neither the box nor the repo
- [x] one backup downloaded to the computer

**Close (AGENTS.md Phase 0 step 4).** First CHANGELOG entry (the template has three sample entries; kept the Phase 0 one, five lines, not "three-line" as AGENTS.md says) [GAP 16]; `setup.done: true`, `setup.installed_on: 2026-10-14`. Told the person that Phase 1 starts at their first request and takes about half an hour.

---

## Phase 1 - the house profile

**Trigger.** "Turn the porch light on at sunset and off at 11 pm." Recorded word for word in `profile.first_request`. Said: before I build that, about half an hour of questions; your request becomes backlog item 1.

**Topic 0 - read the box (no questions).** No API access, so the person read Settings pages to me [GAP 11]. Found: areas Living Room, Kitchen, Bedroom (the defaults); integrations Sun, Weather (Met.no), Backup, Google Drive, Mobile App x2 (after the person installed the apps; services `notify.mobile_app_alexs_iphone` and `notify.mobile_app_sams_iphone`, derived from the iPhone names; I asked them to rename the devices to `Owner phone` and `Adult phone` in the app and re-read) [GAP 14]; persons Alex, Sam; zone Home; no devices; no apps beyond Backup/Google Drive. Said in four lines. No export script to run [GAP 12].

**Topic 1 - people and roles.** Alex owner, Sam adult, Robin child (9) with an iPad and no app, a dog walker who comes weekdays. The dog is not a person and the profile has no place for it [GAP 18]. Robin: `minor: true`, `phone_platform: none`, `notify_level: 1` (default for minors; no effect without a phone) [GAP 21], `may_control: [voice]`, `counts_for_presence: false` [GAP 20]. Dog walker: forced into role `sitter` with `frequency: weekdays 11:00-13:00` and `notify_level: 0`; entry method is by a key lockbox (the kit never asks how a visitor gets in) [GAP 19]. Emergency contact: nobody yet.

**Topic 2 - rooms and words.** Box areas kept, renamed "Bedroom" -> "Primary Bedroom"; added Robin Room (child), Spare Room (shared), Hallway, Laundry Room (utility), Front Porch and Back Yard (outdoor); all on floor "Main". Words: defaults. Reserved: "Away" (Apple Home's own presence word; there is no alarm, so no alarm mode is reserved). Nicknames none.

**Topic 3 - devices and what is dangerous.** Box sees nothing yet. Planned: porch light on a Matter plug, two Thread leak sensors (laundry, kitchen sink), a Thread door contact on the front door. Safety list: none controlled by the house (existing smoke/CO detectors are stand-alone, a gas furnace with its own thermostat). Must work without Home Assistant: switches at the wall, the stand-alone smoke/CO alarms, the key lockbox, the furnace thermostat. Never automate: indoor cameras (none), anything addressed to Robin or the dog walker.

**Topic 4 - priorities.** Order: security, comfort, convenience, energy. Never: a push that wakes Robin; a light flickering on at night; a message to the dog walker; Siri touching anything but lights/switches/scenes. Silence is worse than noise for safety (default). Failed before: "the old smart plug app turned the porch light off while we were arriving" -> first gotchas entry (rule: schedule off-times need a presence/arrival exception: left as a note in gotchas, not built).

**Topic 5 - rhythm.** Wake 06:30 weekday / 08:00 weekend; bed 22:30 / 23:00; quiet hours 22:30 to 06:30. Home in the day: Sam on Wednesdays. Trips: two a year (next: Thanksgiving week, 2026-11-24 to 11-29, freeze from 11-23). Modes: defaults.

**Topic 6 - notifications.** Six classes as they are (the seventh, `life_safety`, is in the router but not in the profile list) [GAP 22]. Levels: Alex 3, Sam 2 (until Sam sets the dial the router treats the phone as 3) [GAP 21]. Maintainer: owner only. Life safety everyone: yes (no smoke/CO integrated; Robin cannot receive any) [GAP 21]. Second channel: none. Sitter gets: nothing; the visitor has no phone [GAP 38]. Speech surfaces: none (the HomePod mini is a Siri device only). Which class does a leak use? The kit says nothing; I chose `security` as the owner's answer to "wake us when the sink leaks" is unanswered: Question Q1 in the backlog [GAP 29, 28]. Told once: the agent never sends to anyone but the owner and never to verify.

**Topic 7 - voice.** Assistant: Apple (Siri on both iPhones and Robin's iPad, one HomePod mini as the home hub). `per_area`: Siri is not tied to rooms -> `{}` [GAP 23]. Exposure: lights, switches, scene scripts. Child rooms: the question assumes a per-room device; recorded `own-device-only` with `assumed: true`, but the kit does not say how Apple would enforce it [GAP 23]. Wake word: not applicable.

**Topic 8 - agent permissions.** Keep the defaults; add `cameras` to never. `unattended: false` (no scheduler, no usage reading); `tier2_wanted: later`.

**Topic 9 - budget, pacing, operations.** Reserve 10/20 confirmed (meaningless without a usage read [GAP 9]). Freeze: 2026-11-23 to 2026-11-29. Backup tiers for a Pi per `install/README.md` ("off-box copy; a spare card") do not fit NVMe; recorded `[T1-builtin-before-update, T3-offbox, T2-spare-boot-media]` as free text [GAP 33]. Restore drill: monthly is unachievable with one Pi and no spare; recorded `quarterly` assumed [GAP 32]. Staging: `drill-only` assumed.

**Topic 10 - documentation.** Manual yes; the sitter track set to `now` because the dog walker is a regular visitor [GAP 19]; wiki schema now, pages from the fifth integration; manual language the house's.

**Topic 11 - generate (below). Close Phase 1:** read the block back; topics all `done` except `voice` and `operations` `assumed`; `profile.done: true`; showed the backlog; asked for the go on item 1 (agent access first).

### Resulting `house/profile.yaml` (full)

```yaml
kit_version: 1
timezone: America/Denver
language: en-US
assumed:                       # EXTENSION, not in the schema [GAP 4]
  - setup.network.wifi_24ghz
  - profile.voice.child_rooms
  - profile.operations.restore_drill
  - profile.operations.staging

setup:
  done: true
  interviewed_on: 2026-10-14
  installed_on: 2026-10-14
  hardware: raspberry-pi
  install_guide: install/raspberry-pi.md
  storage: nvme
  network:
    router_control: true       # an ISP app with a "Fixed IP" toggle [GAP 6]
    wired: true
    wifi_24ghz: true           # assumed
    remote_access: none
  owned_devices:
    - "five Matter plugs that join over Wi-Fi"
    - "one Home Assistant Connect ZBT-1 USB dongle, for Thread, not yet set up"
    - "Apple devices: two iPhones, one iPad (child), one HomePod mini"
  radios: [matter-thread, wifi]            # wifi here means Matter-over-Wi-Fi plugs [GAP 5]
  voice: [apple]
  notification_channels: [companion-app]
  phone_platforms: [ios, ios]              # the child's iPad has no app
  backup_offbox: cloud-drive               # a free Google account used only for this [GAP 8]
  emergency_kit: both
  agent:
    name: other
    runs: laptop
    usage_probe: false
    # how the agent reaches the box: manual (person reads the screens); no schema field [GAP 11]
  budget:
    plan: "pay-as-you-go API key with a monthly spend cap"
    buffer_pct: 10                         # no weekly percentage to apply it to [GAP 9]
    away_buffer_pct: 20
  review_cadence: daily

profile:
  done: true
  first_request: "Turn the porch light on at sunset and off at 11 pm."
  completed_on: 2026-10-14
  topics:
    people: done
    areas: done
    devices: done
    priorities: done
    rhythm: done
    notifications: done
    voice: assumed
    agent: done
    operations: assumed
    documentation: done

  people:
    - label: Alex
      role: owner
      minor: false
      phone_platform: ios
      notify_level: 3
      may_control: [app, voice]
      counts_for_presence: true
      frequency: null
      assumed: false
    - label: Sam
      role: adult
      minor: false
      phone_platform: ios
      notify_level: 2
      may_control: [app, voice]
      counts_for_presence: true
      frequency: null
      assumed: false
    - label: Robin
      role: child
      minor: true
      phone_platform: none                 # an iPad, no companion app
      notify_level: 1                      # no effect without a phone [GAP 21]
      may_control: [voice]
      counts_for_presence: false           # nothing tracks Robin [GAP 20]
      frequency: null
      assumed: true
    - label: Dog walker
      role: sitter                         # closest enum value; really a regular visitor [GAP 19]
      minor: false
      phone_platform: none
      notify_level: 0
      may_control: [none]
      counts_for_presence: false
      frequency: "weekdays, about 11:00 to 13:00; enters with a key from a lockbox"
      assumed: false
    # the dog: no field exists [GAP 18]

  areas:
    - {name: Living Room, floor: Main, kind: shared}
    - {name: Kitchen, floor: Main, kind: shared}
    - {name: Hallway, floor: Main, kind: shared}
    - {name: Primary Bedroom, floor: Main, kind: private}
    - {name: Robin Room, floor: Main, kind: child}
    - {name: Spare Room, floor: Main, kind: shared}
    - {name: Laundry Room, floor: Main, kind: utility}
    - {name: Front Porch, floor: Main, kind: outdoor}
    - {name: Back Yard, floor: Main, kind: outdoor}

  house_words:
    presence_modes: [Home, Not Home]
    guest_mode: Guest staying
    modes: [Home, Not Home, Night, Guest staying]
    reserved: ["Away: Apple Home's own presence word"]
    nicknames: {}

  devices:
    integrations: [Sun, Weather, Backup, Google Drive, Mobile App]
    owned: ["Mobile App: 2 phones"]
    planned: ["Matter plug on the porch light (Matter over Wi-Fi)", "4 more Matter plugs (lamps)",
              "2 Thread leak sensors (laundry, kitchen sink)", "1 Thread door contact (front door)",
              "OpenThread Border Router on the ZBT-1", "HomeKit Bridge"]
    safety_relevant: []                    # nothing controlled; leak sensors only read
  priorities:
    order: [security, comfort, convenience, energy]
    never:
      - "a push that wakes Robin"
      - "a light that comes on by itself at night without a reason in the schedule"
      - "any message to the dog walker"
      - "Siri reaching anything but lights, switches and scene scripts"
    must_work_without_ha:
      - "wall switches"
      - "stand-alone smoke and CO alarms"
      - "the key lockbox and the front door key"
      - "the furnace's own thermostat"
    noise_vs_silence: silence-worse-for-safety

  rhythm:
    wake: {weekday: "06:30", weekend: "08:00"}
    bed: {weekday: "22:30", weekend: "23:00"}
    quiet_hours: {start: "22:30", end: "06:30"}
    home_in_the_day: [Sam on Wednesdays]
    trips_per_year: 2

  notifications:
    classes: [alarm, security, reminder, house, health, maintainer]   # life_safety is the router's seventh [GAP 22]
    default_class: security
    maintainer_to: owner
    life_safety_everyone: true
    second_channel: none
    sitter_gets: []                       # [GAP 38]
    speech_surfaces: []

  voice:
    assistants: [apple]
    per_area: {}                          # Siri is per device, not per room [GAP 23]
    exposure: [lights, switches, scene-scripts]
    child_rooms: own-device-only          # assumed; Apple cannot gate this [GAP 23]
    wake_word: null

  agent:
    may: [lights, switches, read-all-but-secrets]
    ask_first: [delete, restart, firmware, version-change, safety-list, anything-that-reaches-a-person]
    never: [arm, disarm, lock, unlock, codes, contacts, consent, cameras]
    unattended: false
    tier2_wanted: later

  operations:
    freezes:
      - {from: 2026-11-23, to: 2026-11-29, why: trip}
    backup_tiers: [T1-builtin-before-update, T3-offbox, T2-spare-boot-media]   # [GAP 33]
    restore_drill: quarterly              # assumed; needs a drill target [GAP 32]
    staging: drill-only                   # assumed

  documentation:
    manual: true
    sitter_track: now
    wiki: schema-now-pages-from-fifth-integration
    manual_language: null
```

Not in the profile on purpose: phone numbers, addresses, the Google account, the HomeKit pairing code.

---

## Files generated (per `interview/generated-files.md`)

Written to `house/` (all with a status line naming the source fields and 2026-10-14):

| File | What it holds for this house |
|---|---|
| `profile.yaml` | the block above |
| `docs/naming.md` | the 9 areas with kinds; words Home/Not Home/Night/Guest staying, "Away" reserved for Apple; `Category - Target` list (Lighting, Notify, Health, Presence, Scene); device names typed at creation `<Area> <Thing>` e.g. "Front Porch Light"; ids read back; label record; YAML key order [GAP 30] |
| `docs/policies.md` | agent may/asks/never (cameras added); design-only list (nothing on the safety list yet, plus the standing: alarm, locks and codes, consent, firmware, versions); voice: Siri via HomeKit Bridge, lights/switches/scene scripts only, no locks; presence: Alex and Sam count, Robin and the visitor do not; priorities; "nothing unattended" |
| `docs/notifications.md` | two phones (Alex 3, Sam 2; "treated as 3 until Sam sets the dial"), Robin has no phone, the visitor none; life safety to everyone with a phone; quiet hours 22:30-06:30; maintainer = Alex only; no second channel; tags/slots: leak, door/arrival, battery, backup; the test rule; the event-to-class table I added by hand (leak=security, arrival=house, battery digest=maintainer) [GAP 29] |
| `docs/health-checks.md` | subsystems security (door contact), plumbing (2 leak sensors), system (backup age, notifications switch, Pi CPU/disk), network (Thread devices x of y); thresholds 15/30; not monitored on purpose: the plugs' lamps; off-box copy age marked "no source sensor" [GAP 34] |
| `docs/operations.md` | tiers T1/T2(spare media)/T3; restore time "to be measured"; freeze 2026-11-23 to 11-29 (fixes only); staging = drill-only; pacing: no probe, per-run cap, 3 items per session [GAP 9]; push guard "does not exist yet" [GAP 13] |
| `docs/user-manual/README.md` | household chapters filled with the house's words; guests chapter is the dog walker/visitor track (now) |
| `docs/wiki/SCHEMA.md` | schema v1; first page list = the 5 integrations |
| `docs/gotchas.md` | the template with one seeded entry (schedule off-time during arrival) |
| `docs/CHANGELOG.md` | Phase 0 entry, plus "House profile written (Phase 1)" |
| `docs/backlog.md` | below |
| `tests/` (copied from `templates/tests/`) | offline macro tests |

Not copied now: `ha/packages/*` and `custom_templates/*` (the backlog items copy them) [GAP 40]; `tier2/` (`tier2_wanted: later`); `pacing/` (no usage probe; `unattended: false`). No `push_guard.py` could be copied [GAP 13]. No export script [GAP 12].

---

## The backlog (house/docs/backlog.md), sized

The kit gives no rule for placing the person's four extra ideas or the setup items the kit does not know to add [GAP 31]; this order follows dependencies.

| # | Item | Points | Needs first |
|---|---|---|---|
| A | Agent access to the box and `packages:` enabled | 2 | nothing (person creates a user and token) [GAP 11] |
| B | Companion apps: device names, permissions, notify-level helpers set | 1 | nothing [GAP 14] |
| 1 | **Turn the porch light on at sunset and off at 11 pm** (first request) | 2 | A; the porch plug commissioned in Home Assistant, named "Front Porch Light", area Front Porch |
| 2 | Notification router | 3 | topic 6 done (yes); A, B |
| 3 | Thread bring-up (ZBT-1 firmware, border router, Matter server, credentials) | 3 | A; the person at the console [GAP 25] |
| 4 | Water leak alert | 3 | 2, 3; two sensors bought; Q1 |
| 5 | HomeKit Bridge and the Goodnight scene via Siri | 3 | A; the owner present to pair; Q4 |
| 6 | Dog-walker arrival notice to the owners | 3 | 2, 3; a door contact; Q2, Q3 |
| 7 | First health count | 3 | 2 |
| 8 | Weekly low-battery report | 2 | 7; battery devices from 4 and 6 |
| 9 | Backup restore drill | 1 | a drill target (spare NVMe/SD, second Pi or a VM) [GAP 32] |
| 10 | Manual, first chapter | 2 | item 1 built |
| 11 | The visitor track (dog walker) | 2 | Q3; moved up from last because a visitor is expected now [GAP 19] |
| 12 | Wiki pages | 3 | the fifth integration |

Questions for the owner (with audience and class):
- Q1. Should a leak at night wake the house? Audience: household (Alex, Sam); class: security. (a) normal push, silenced by Focus; (b) time-sensitive push; (c) critical, which the kit reserves for alarms. Recommended: (b) [GAP 28].
- Q2. A door opening while both of you are away outside the dog-walker window: say so? Audience: Alex and Sam; class: security. (a) yes, same push; (b) no. Recommended: (a).
- Q3. Are you OK with the house noticing the dog walker's door opening and telling only you? Audience: household. Recommended yes; the walker is told by you [GAP 19].
- Q4. Does "Goodnight" include the porch light (it goes off at 11 pm by itself)? Audience: household; class: none. Recommended: no.

The first five I planned: **1 porch, 4 leak, 5 goodnight, 6 dog walker, 8 low-battery report** (plus the gating items A, B, 2, 3, 7 in brief). The kit's own rule would make the first five the generated items [GAP 31].

---

## Phase 2 plans (plan only; there is no box)

All plans end with: Approve (wait for the owner's go), Build, Test, Record (CHANGELOG entry with the undo; a note line in the manual's `NOTES.md`; a gotcha if something taught a lesson), Report. Ids below are intended names; every id is `(read back)` after creation [GAP 30]. Files are written in `house/ha/` and deployed by a method the kit does not define [GAP 11].

### Gate A. Agent access and packages (2)
Person creates a non-admin user `agent`, a long-lived token stored as `HA_TOKEN` on the laptop (never in chat), installs a file/SSH app or Samba; I add `homeassistant: packages: !include_dir_named packages` to `configuration.yaml` with the person; check = `ha core check` / the Developer tools check, literal success line. Template: none. Test: read `/api/states` count before and after. Undo: remove the line, restart.

### Item 1. Porch light, on at sunset, off at 23:00 (2 points)
1. Entities: `switch.front_porch_light` (Matter plug, area Front Porch, id read back), `automation.lighting_front_porch_light` (alias "Lighting - Front Porch Light", key order alias, description, triggers, conditions, actions, mode).
2. File: `house/ha/packages/lighting.yaml` (new; no template exists for a plain automation).
3. Triggers with ids: `sun` event sunset (id `dusk`), `time` 23:00:00 (id `late`), and `homeassistant` start (id `boot`) so a restart between the two times lands in the right state (automations.md rules 7-8). Conditions per branch with native `sun` and `time` conditions, no templates. Actions: `choose` on trigger id -> `switch.turn_on` / `switch.turn_off`; `mode: single`.
4. Coverage: Matter plug unavailable -> `unavailable` check later in item 7; no message is sent by this item.
5. Test without sending: config check (literal success); `automation.trigger` for each branch with the owner present (a switch is on the agent's allowed list), read the state back, check the trace and `last_triggered`; confirm the next sunset from `sun.sun.next_setting` in America/Denver. No push anywhere.
6. Record: CHANGELOG with undo (`git revert <sha>`, reload automations); a `NOTES.md` line "porch light on at sunset, off at 11 pm". Gotcha candidate: the earlier "off while arriving" lesson.

### Item 2 gate. Notification router (3), brief
Copy `templates/packages/notification-router.yaml` + `templates/custom_templates/notify.jinja` to `house/ha/`; fill `phones` (Alex ios owner, Sam ios), the two `input_select.notify_level_*`, `notify_clear.services` (the same two services, kept in sync by hand [GAP 36]), SLOTS with `leak`, `dog_walker`, `battery`. Add `input_boolean.notify_test_mode` which the template lacks [GAP 39]. Test: `dry_run: true`, read `notify_router_call` events for each class; the offline tests; the owner sends the first real push. Sam's dial stays at "Everything" until Sam sets it [GAP 21].

### Gate 3. Thread bring-up (3), brief
ZBT-1 on an extension cable; firmware to Thread; OpenThread Border Router app; Matter integration; sync Thread credentials from each iPhone; record whether the HomePod mini's network is also present [GAP 25]. No kit procedure to quote: steps taken from the official pages and noted in gotchas. Template: none. Test: Settings > Thread shows one preferred network; no message.

### Item 4. Water leak alert (3 points)
1. Entities: `binary_sensor.laundry_room_leak`, `binary_sensor.kitchen_sink_leak` (Thread sensors named at commissioning; Matter often derives longer ids such as `..._water_leak`, read back), batteries `sensor.laundry_room_leak_battery`, `sensor.kitchen_sink_leak_battery`.
2. Automations: "Notify - Leak Detected" (two state triggers with ids, `from: 'off'`, `not_from: unavailable` guards, `mode: queued`) and "Notify - Leak Cleared" (clears the `leak` slot via `script.notify_clear`, no "all clear" text for a problem nobody heard).
3. Template: `notification-router.yaml` + `notify.jinja`; call `script.notify` with `class: security` [GAP 29] (Q1 may make it time-sensitive [GAP 28]), `tag: leak_detected`, title "Water leak", message built from the trigger's area name and event time (not a literal).
4. Health: the kit's own sample CHECKS already include a kitchen sink leak sensor (`unavailable` 60 min, `silent` 24 h); add laundry too (item 7).
5. Test: `notify_test_mode` on (owner's OK); set a simulated "on" state in Settings > Tools > States for each sensor; read `notify_router_call` (to: Alex, Sam; slot `leak`); then verify nothing audible happened; trace both branches; the owner puts a wet finger on the real sensor and says what arrived on both phones (the owner sends and reports, I never trigger a live push).
6. Risk: iPhone Focus/Sleep mutes it at 3 am until Q1 is decided; battery of the sensors reports in steps (gotchas).

### Item 5. HomeKit Bridge and Goodnight via Siri (3 points)
1. Entities: `script.scene_goodnight` (alias "Scene - Goodnight"; turns off `switch.living_room_lamp`, `switch.kitchen_counter_light`, `switch.hallway_lamp`; does not include the porch light unless Q4 says so), the HomeKit Bridge entry "House Bridge" with an explicit include list of exactly those three switches plus the script (4 accessories) [GAP 24].
2. File: script in `house/ha/packages/scenes.yaml`; the bridge is created in the UI by the owner (the pairing code appears in a Home Assistant notification; the owner scans it; I never see it).
3. Apple side: in Apple Home one scene named "Good Night" containing only the bridged "Goodnight" switch, so Siri's "Good night" runs it; no conditions or automations in Apple Home (apple.md:15) [GAP 24]. Needs the HomePod mini as the home hub for remote use.
4. Robin's iPad: its Siri works only if Robin is a Home member with Control; left to the owner [GAP 23].
5. Template: none.
6. Test without sending: config check, `script.turn_on` once with the owner present (lights are allowed), read each switch state back, trace; count the bridge's accessories (4); the owner says the phrase to Siri and reports.

### Item 6. Dog-walker arrival notice to the owners (3 points)
1. Entities: `binary_sensor.front_door_contact` (Thread contact, area Front Porch), battery `sensor.front_door_contact_battery`, helper `schedule.dog_walker_window` (Mon-Fri 11:00-13:00 — the person-facing name is plain; no suffix), `input_boolean.dog_walker_arrival_sent` (hidden companion, `_sent`), `person.alex`, `person.sam`.
2. Automation: "Presence - Dog Walker Arrival" (trigger contact `off` -> `on`; conditions: schedule on, both persons `not_home`, arrival-sent flag off; actions: set flag, `script.notify` class `house`, tag `dog_walker_arrived`, title "Dog walker", message "Front door opened at <event time>"; `mode: single`), plus a reset automation at window end. Positive evidence only; restart-safe because the flag is a helper.
3. Template: router (class `house`, level 2, so Sam receives it); no template exists for a presence/arrival pattern.
4. Audience: Alex and Sam only. The walker is never messaged and `sitter_gets: []` holds [GAP 19, 38]. Nothing else about the walker is stored.
5. Needs: Q2 (outside the window), Q3 (consent of the household to sense the door).
6. Test: `notify_test_mode` on; simulate contact `on` with persons set to `not_home` in Settings > Tools; read the router event; vary one input at a time (schedule off, one person home, flag on) and show nothing fires; the owner sends the first real push on the next weekday by opening the door in the window.

### Item 8. Weekly low-battery report (2 points; follows item 7)
1. Entities: `sensor.laundry_room_leak_battery`, `sensor.kitchen_sink_leak_battery`, `sensor.front_door_contact_battery`, the thresholds `input_number.health_battery_fault_pct` (15) and `health_battery_notice_pct` (30), the `sensor.health_security` and `sensor.health_plumbing` attributes `notices`.
2. Template: `health-check.yaml` + `health.jinja` (`battery` kind; the checks are written once there). The weekly digest itself has no template [GAP 34]; I write "Health - Weekly Battery Report" (Sunday 09:00 `time` trigger, `choose` on whether any battery notice exists, `script.notify` class `maintainer`, tag `battery_report`, owner only). A report that only sends when something is low cannot be shown to work on a quiet week, so the plan includes a test from a simulated state.
3. Faults (below 15 %) page through the health fault push; notices (below 30 %) appear only in the report.
4. Test: `notify_test_mode` on; set a battery sensor to 12 and 25 in Settings > Tools > States; confirm the count, notices and the event the report would send; render the digest template in Developer tools; run the offline tests (all pass today); the owner sends the first real report (changing the Sunday trigger is the owner's call).
5. Risk: Matter battery reports are coarse; the replay of 7 days of history decides thresholds (testing rule 4), which does not exist yet on a new box — start at the defaults.

---

## Where the kit helped and where it did not
- Helped: the strict order, the approval loop, the "never send to verify" rule, the backlog template, the offline tests (65 cases, all pass on an interpreter with jinja2), and Phase 0's emphasis on a reserved address and an off-box backup.
- Did not: anything about Thread/Matter, NVMe boot, Apple setup, reaching the box from a different agent, a push guard, an export script, the dog and the visitor.

## After the fixes (what the same walk does on today's kit)
- **Phase 0** adds two sections: the phones (role names such as `Owner phone` before the app registers, Time
  Sensitive allowed) and `install/agent-access.md` (an agent user, a token in an environment variable, a read
  check). The walk's "person reads Settings pages" fallback becomes `setup.agent_access.read: api`.
- **The Pi guide** has an NVMe path (write the drive through a USB enclosure; boot order if it does not start), and
  the network guide covers a provider's router with no reservation and the IPv6/mDNS checks Matter and HomeKit need.
- **Backups** name the Apple-only case: iCloud is not a location; Home Assistant Cloud, a dedicated Google or
  Microsoft account, or a Mac share.
- **The profile** has an `assumed` list, `matter-wifi`, `agent_access`, a count-based budget, `pets`, the
  `visitor` role with `entry`, and `notifications.events` (leak -> security, urgent). The dog walker is a
  `visitor`, not a forced `sitter`.
- **Thread bring-up** follows `adapters/radios/matter-thread.md` step by step (the HomePod mini is an existing
  Apple network: import its credentials and join it rather than start a second one), and the Goodnight item
  follows `adapters/voice/apple.md` ("Goodnight" script exposed; an Apple scene that wraps only that switch).
- **The backlog** puts the small gating items (agent access, packages, Thread bring-up, the HomeKit Bridge) ahead
  of the first request, and adds the live export and the push guard (`templates/guard/`).
- The four items the first report left open (naming of entity ids in plans, a test-mode switch in the router,
  health-check kinds for numeric thresholds and app status, the export script) were closed by O4b on 2026-10-14;
  see `dry-run-2026-10-14.md` "Open items".
