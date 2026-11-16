# Zigbee

*Status: notes (O1). Templates: `templates/`.*

## What is different
- Two stacks: ZHA (built in, simpler) or Zigbee2MQTT (an app plus MQTT, wider device support, its own UI).
  Pick one at the start; moving later means re-pairing everything.
- The coordinator is a USB stick or a network coordinator. Keep it on a USB extension away from USB 3 ports and
  the box's own radios; interference is the first thing to suspect for a flaky mesh.
- Mains-powered devices route; battery devices sleep. A mesh with few routers is a mesh with dead corners.

## What the principles need from it
- **Health (rule 4, stale is a state).** The stack drops a battery device after about six hours of silence and a
  mains relay after about two; a device whose check-ins touch no entity never drops at all. So "no report for N
  hours" needs a *last heard* sensor per device, and silence is a notice at 24 h, not a fault at 6 h.
  `unavailable` stays the dead-device fault.
- **Health (rule 9, mesh).** "x of y online" with an explicit *not monitored* label for devices offline on
  purpose (a seasonal plug, a spare sensor). 0 of N is a coordinator fault with a short delay.
- **Backups T4.** Back up the coordinator (ZHA: the network backup in the integration; Zigbee2MQTT: the data
  folder plus the coordinator backup) monthly, off-box. A new stick restored from it keeps every pairing.
- **Change control.** Reload the integration after any USB re-plug. Coordinator firmware counts as device firmware:
  frozen during a trip.
- **Naming.** Devices named at pairing time keep that name's id; read it back.

## How this goes wrong

- Battery devices check in with the stack without touching any entity, so a healthy sensor can look silent for half
  a day. Make silence a notice with a long window, not a fault.
- Zigbee devices can answer a voice assistant before their state settles, producing a "device isn't responding"
  that is not a device problem.
- With a second radio in the house, both stacks mostly unavailable at once means a power cut; one means a stick
  fault; neither means the network.
