# Wi-Fi devices and ESPHome

*Status: notes (O1). Templates: `templates/`.*

## What is different
- No mesh and no coordinator; every device is a client of your access points. Signal, DHCP and the access point's
  client limit are the failure modes.
- ESPHome boards are yours to build: firmware is a YAML file you compile, so "firmware" is also "config".
- Cloud-dependent Wi-Fi devices (some bulbs, plugs, thermostats) go away with the vendor's service or your WAN.

## What the principles need from it
- **Health.** An unreachable Wi-Fi device reads `unavailable` promptly; use that as the dead-device fault. Add a
  WAN check so a cloud outage shows as one cause, not forty. A cloud-polled device has minutes of lag: never a
  five-minute fault on its last update.
- **Change control.** Reserve DHCP addresses for anything an integration is pinned to by IP. ESPHome firmware is
  device firmware: frozen during a trip, and an ESPHome version bump is a version change (design only, after the
  trip).
- **Automations.** A Wi-Fi light may drop whichever of color and brightness arrives second when it has to switch
  modes: split the calls and delay half a second. A boolean attribute from an ESPHome board arrives as the string
  `on` / `off`.
- **Testing.** ESPHome boards that hold alarm zones or door contacts are part of the security subsystem; their
  firmware changes get the staging and rehearsal treatment.

## How this goes wrong

- A device takes a new DHCP lease and the integration pinned to the old address sits unavailable until something
  checks it. Reserve addresses.
- A light that drops its color when sent with brightness can pass every test if the harness adds a gap production
  does not have.
- A brief cloud DNS failure makes every gateway entity unavailable at once; treat unavailable as a notice and only
  a real disconnected state as the fault.
