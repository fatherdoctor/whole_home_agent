# Apple Home and Siri

*Status: notes (O1) plus setup (O4, 2026-10-14, from the official HomeKit Bridge page). Not used in practice;
general guidance, not lessons.*

## What is different
- Home Assistant appears to Apple Home through the HomeKit Bridge integration (local, no cloud subscription), or
  devices are shared into Apple's Matter fabric directly.
- Exposure is per entity in the bridge's options; Apple Home has its own rooms, scenes and automations, which can
  act on the bridged entities outside Home Assistant.
- Siri commands arrive under the bridge, not a person.

## What the principles need from it
- **Exposure is lights, switches and scene scripts only.** Do not bridge locks or the alarm, even though HomeKit
  supports them; the alarm and the locks have one controller.
- **No logic in Apple Home.** Automations live in Home Assistant so that traces, the changelog and the health
  checks see them. Apple Home automations on bridged entities are logic hidden from the system.
- **Attribution.** Keep the bridge's accessory list short so a change "by the bridge" is easy to map to a voice
  command.
- **Matter fabrics.** A device in both Apple's fabric and Home Assistant's can be driven from either side; see
  `adapters/radios/matter-thread.md`.

## Setup (the person does it; you read back)
1. **Network first:** mDNS between the box and the phones (`install/network-and-backups-first.md` section 1b).
2. **Settings > Devices & services > Add integration > HomeKit Bridge.** Choose the domains to include: `light`,
   `switch`, `script` (and `scene` if the house uses scenes). Then narrow it to the listed entities in the bridge's
   options (include mode, entity by entity): the policy is a short list, not a domain.
3. A notification in Home Assistant shows the pairing QR code. The person scans it from **Apple Home > Add
   Accessory** on their iPhone. The pairing code is a setup secret: never copied into the chat or the repository.
4. Assign the bridged accessories to Apple Home rooms that match the Home Assistant areas.
5. **A home hub** (HomePod or Apple TV) is what lets Siri, sharing and remote control work away from home. Without
   one, Siri works only on the iPhone, at home. Ask whether there is one; it is also a Thread border router
   (`adapters/radios/matter-thread.md`, step 2).
6. Record: `setup.voice: [apple]`, the exposed entities in `house/docs/policies.md`, a CHANGELOG entry with the undo
   (remove the integration; remove the bridge in Apple Home).
Limits: one bridge holds at most 150 accessories; scripts and scenes appear in Apple Home as switches.

## A spoken "Goodnight" without logic in Apple Home
Expose the house's script (for example `script.goodnight`, named "Goodnight") through the bridge. "Hey Siri, turn on
Goodnight" runs it. If the person wants the phrase "Goodnight" on its own, an Apple Home scene that contains ONLY that
switch is allowed: it is a wrapper, with no conditions and no other accessories. Never put lights into the Apple scene
directly; the script decides what goodnight means, and its trace shows it ran.

## Rooms and children
Siri is per person and per device, not per room, so `voice.per_area` stays `{}`. Home Assistant cannot limit what a
child's iPad asks Siri to do; the lever is Apple's: the child's membership in the Apple home (**Apple Home > Home
Settings > the person**, with control of accessories off, or not invited). Record `voice.child_rooms: any` with the
path in `assumed`, and the Apple-side setting in `house/docs/policies.md`.

## How this goes wrong

- None recorded.
