# Lab seed checklist: building `lived-in` from `fresh-install`

*Status: written (KIT-EXIST.e, 2026-10-31). For whoever builds the lab, on a test virtual machine (never the house's own). The answer key is `../lived-in-house.md`. About an hour with the YAML ready. Never run any of this on a real house.*

**Timing, first:** snapshot `lived-in` **at least 7 days before** the dry run (so the one backup is 7 or more days old on the day, fault 11), and **start the VM from that snapshot at least 24 hours before** the dry run (so the unavailable sensor has been unavailable for the whole window, fault 14). If the dry run has to come sooner, set the clock forward on a **copy** of the VM and say so in the dry run's record. Write the seed day here: ______

## 1. Start

1. Restore the test virtual machine to `fresh-install`, a snapshot taken right after a fresh Home Assistant install and onboarding. Log in as the owner. Write down the owner's name for step 6; the YAML calls the person Alex, so name the owner Alex or change `person.alex` in `seed/automations.yaml` and `seed/packages/seed.yaml` together.
2. On a computer: `python3 render_seed.py ~/lab-seed` (from this folder). The result is the YAML below with the fake planted password filled in.

## 2. Integrations, floors and areas (user interface)

1. Settings > Devices & services > Add integration > **Demo**. Accept the defaults.
2. Keep the lab's one real plug (any integration); rename its switch `switch.lab_plug`.
3. Settings > Areas > Floors: create **Ground** and **Upstairs**. Create six areas and give each its floor: Kitchen, Living Room, Garage (Ground); Hallway, Bedroom, Office (Upstairs).
4. Assign each demo device to the area in `seed-fixture.json`'s `devices` list (its `area_id`). **Leave the two with `area_id: null` unassigned** (`fan.living_room_fan`, `media_player.walkman`): that is fault 1.

## 3. The YAML (paste-ready)

In the File editor app (install it first, step 5) or any way you copy files into `/homeassistant`:

1. Add the two lines of `seed/configuration.addition.yaml` to `configuration.yaml` (the `homeassistant:` block; merge with an existing one).
2. Copy `~/lab-seed/automations.yaml`, `scripts.yaml`, `scenes.yaml` over the lab's (they are empty or default on `fresh-install`; look first, and if they are not empty, add instead of replacing).
3. Copy `~/lab-seed/packages/seed.yaml` to `/homeassistant/packages/seed.yaml` (make the folder).
4. Settings > Tools > YAML > **Check configuration**, then restart Home Assistant. The restart must show no error.
5. Settings > Automations: confirm **14** automations, **3** scripts, **2** scenes; Helpers: `House mode`, two `Guest mode`, two numbers, one timer; the `person` Alex; the sensor "Seed unavailable sensor" shows **Unavailable**.

## 4. What the YAML plants

Faults 2, 3, 4, 5, 6, 7 (after step 8 below), 8, 9, 13 and 14 come from the files; the comments in them say which. Do not tidy any of it.

## 5. Apps

Install **File editor** and **Terminal & SSH**; start both; turn **Auto update on** for both. Leave watchdog off.

## 6. People

1. Create **Sam**, an administrator (Settings > People > Users). Sam is the second administrator (fault 15).
2. Log in once as Sam and turn on multi-factor (Profile > Multi-factor authentication modules > TOTP) with any authenticator app. The secret is the lab's own: never write it down or commit it.
3. **Do not** turn multi-factor on for the owner (fault 12).
4. As the owner: Profile > Security > Long-lived access tokens > create one named `lab agent` (under a year old is not a finding).

## 7. Marketplace and the dashboards

1. Open **Settings > Marketplace**. It is built in on 2026.11; accept its community-content notice before installing.
2. Install one card, `custom-cards/button-card`, and one integration repository of your choice (the fixture names `thomasloven/hass-browser_mod`). If a custom repository needs a GitHub connection, follow the Marketplace prompt without putting its code in chat. The offline fixture retains its legacy `hacs_repositories` key; the current export does not yet inventory Marketplace repositories, so record them separately. If you choose another, change that fixture key in the same commit.
3. Dashboards: keep **Overview** the default. Create two storage dashboards: **Climate** (url `dashboard-climate`; first tab holds a thermostat card for `climate.hvac`) and **Lights** (url `dashboard-lights`; light cards plus one `custom:button-card`).

## 8. Make it look lived-in

1. Settings > Tools > Actions: for each automation except **Close the garage door at night**, run `automation.trigger` with `skip_condition: true`. This sets `last_triggered` (so only fault 8's automation has never run) and leaves a saved trace for each; `bedroom_night_dim` ends in error, which is fault 9.
2. The run of **Leaving - arm alarm** arms the demo alarm: disarm it afterward (Overview, the security panel).
3. Run each script once. Turn the automation **Turn off the lights at midnight** **off** (fault 7).
4. Put the demo entities back as they were (lights off, doors locked).

## 9. The backup (faults 10 and 11)

1. Settings > System > Backups > Backup settings: automatic backups **Off**, no extra locations, no encryption.
2. Create **one** backup by hand now: full, local only. Write the date above; this is the date that must be 7 or more days old on the dry run.

## 10. Check the seed, then snapshot

- [ ] 14 automations, 3 scripts, 2 scenes, one blueprint-based automation, one `Guest mode` duplicate, no area on exactly two device-backed entities.
- [ ] One backup, local, unencrypted, automatic backups off.
- [ ] Two administrators; the owner without multi-factor; one long-lived token.
- [ ] The password-shaped line is in `packages/seed.yaml` (search for `digest_upload`).
- [ ] Copy `.storage/auth`, `auth_module.totp`, `backup`, `trace.saved_traces` to your computer and compare **shape only** (key names, nesting) with `seed-fixture.json`'s `storage` block; note any differences in the dry run's record. **Do not commit those files or paste their contents anywhere.**
- [ ] Shut down cleanly, take the snapshot `lived-in`, write the seed day above.
- [ ] 24 or more hours before the dry run: start the VM from `lived-in`, and write down Home Assistant's version (fault 16 is scored from it).
