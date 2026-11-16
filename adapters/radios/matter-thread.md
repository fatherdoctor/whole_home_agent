# Matter and Thread

*Status: written (O4, 2026-10-14), from the official Home Assistant Thread and Matter integration pages as of
October 2026; the O1 notes are kept below. Not used in the install the kit came from: these are the documented
steps, not lessons. The official page wins when a menu differs.*

## What is different
- Matter is the application layer; Thread is one of its radios (Wi-Fi and Ethernet are the others). Thread needs a
  border router (a hub, a speaker, a dedicated dongle); a device joins a *fabric*, and the same device can be shared
  into several fabrics (Home Assistant plus a phone ecosystem).
- Commissioning is done with the companion app on a phone, over the phone's Bluetooth, with the device's QR or
  pairing code. Home Assistant does not use the box's own Bluetooth for it.
- Everything is IPv6 and mDNS on the home network. A router or access point that blocks either breaks Matter in
  ways that look like device faults (`install/network-and-backups-first.md`, "What the network must allow").

## Setup on Home Assistant (Thread, with a Home Assistant dongle as the border router)
The person does each step on their screen; you read it back. Needs Home Assistant OS (any of the kit's install
guides) and a 64-bit system.

1. **Plug the dongle in on a USB extension cable**, away from the box's USB 3 ports. A Connect ZBT-1 or ZBT-2 runs
   either Zigbee or Thread firmware, not both; this kit uses one radio per dongle.
2. **Check for Thread networks you already have.** **Settings > Connectivity > Thread** (add the Thread
   integration first if it is not listed). An Apple home hub (HomePod mini, recent Apple TV) or a Google/Nest hub
   is a border router with its own network, and shows here as "Other networks".
3. **Switch the dongle to Thread** with the official procedure for that dongle (linked from the Thread integration
   page: "Enable Thread on Home Assistant Connect ZBT-1 / ZBT-2"). It flashes the firmware and installs the
   **OpenThread Border Router** app. Wait for the app to start.
4. **Preferred network.**
   - No other network (step 2): Home Assistant creates `ha-thread-xxxx` and makes it preferred. Check the Home
     Assistant logo is under **Preferred network**.
   - An Apple or Google network exists: follow the official page's "existing network" case: import that network's
     credentials from a phone in that ecosystem, make it preferred, then enable the border router so it JOINS that
     network instead of starting a second one. One network for the house is the goal; two networks split the
     devices and the mesh.
5. **Give the phones the credentials.** iPhone: in the companion app, **Settings > Connectivity > Thread**, then
   **Send credentials to phone** under the preferred network. Android: companion app **Settings > Companion app >
   Troubleshooting > Sync Thread credentials**. Each phone that will commission devices needs this once.
6. **Add the Matter integration** (**Settings > Devices & services > Add integration > Matter**). It installs the
   **Matter Server** app. Wait until the integration shows as loaded.
7. **Record it:** `setup.radios` gets `matter-thread`; the CHANGELOG entry names the dongle's firmware choice, the
   preferred network (by its network name, which is not a secret; never the network key) and the undo (switch the
   firmware back from the hardware page; remove the apps).

The Thread network key and the Matter fabric live in the box (the apps' data), so **the Home Assistant backup
carries them**: a restore onto new hardware with the same dongle brings the network back. Check that the apps are
included in the backup (`install/network-and-backups-first.md` section 3, "Data").

## Commissioning a Matter device (Thread or Wi-Fi)
1. **Name and area first.** Decide the device's name in the house's scheme (`house/docs/naming.md`) before
   pairing: Matter devices arrive with vendor names.
2. On the phone: companion app, **Settings > Connectivity > Matter > Add device**.
   Turn Bluetooth on and keep the phone close to the device.
3. **Wi-Fi devices:** the phone must be on the 2.4 GHz network the device will use (many Matter Wi-Fi devices are
   2.4 GHz only). **Thread devices:** the phone must have the credentials (setup step 5).
4. Scan the code. "No, it's new" for a device out of the box. A device already in Apple Home or Google Home is
   shared instead: from that app, "Turn on pairing mode" / "Linked Matter apps", then Home Assistant uses the new
   code it shows.
5. Rename the device and its entities, set the area, and **read the ids back** for the plan.
6. **The pairing code is a secret for the device's life**: it re-adds the device after a reset. Keep it in the
   password manager (or the box it came in), never in the repository.

**One fabric or two.** Default: the device is in Home Assistant's fabric only, and phones reach it through Home
Assistant (and Siri through the HomeKit Bridge, `adapters/voice/apple.md`). Share it into a second fabric only when
the person wants that ecosystem to control it without Home Assistant (for example a light that must work when Home
Assistant is down; `profile.priorities.must_work_without_ha`). A second fabric controls the device outside the
exposure policy; record the choice per device in the device's wiki page or the CHANGELOG.

## Known problems worth knowing up front
- **Firmware updates through Home Assistant fail on a Thread network that has an Apple border router** (it does
  not forward the mDNS the update needs; "Target node did not process the update file"). Update those devices from
  the Apple Home side, or not at all; firmware is an ask-first action either way.
- **A Wi-Fi Matter device that will not commission** is usually the network: the phone on 5 GHz or a guest network,
  client isolation, or IPv6 off on the router.

## Health
- "x of y online" works the same; a Thread device that is unavailable shows as `unavailable`.
- **Border-router loss takes down every Thread device at once.** Add one check for the OpenThread Border Router and
  Matter Server apps (each app's "running" binary sensor, enabled from the app's device page under **Settings >
  Devices & services > Home Assistant Supervisor**), as a fault with a short delay, and make the "x of y" check
  defer to it (one cause, one warning: `principles/health-checks.md`).

## What the principles need from it (O1 notes)
- **Backups T4.** There is no coordinator backup to take separately when the border router runs on the box (above).
  When a vendor hub is the border router, its credentials live in that hub: record which hub, and keep every
  device's pairing code off-box; a lost fabric means re-commissioning each device by its code.
- **Naming.** Rename at commissioning and read the id back.
- **Change control.** A vendor hub updates itself; you cannot pin it. Note the version in the drift log when it
  changes. The two apps on the box update like any app: one at a time, with a backup first.
- **Voice.** A device shared into a phone ecosystem's fabric is controlled directly by that ecosystem, outside the
  exposure policy in `principles/safety-and-security.md`. Decide per device (above).

## How this goes wrong

- None recorded. The policy rules (exposure, auto-arm Stay only, one switch per code) apply by principle.
