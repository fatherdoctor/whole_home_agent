# Z-Wave

*Status: notes (O1). Templates: `templates/`. Used in practice: most of the failure modes are first-hand.*

## What is different
- One stack (Z-Wave JS, an app plus the integration). A controller stick on a USB extension. Long Range needs a
  compatible stick and devices and is star-topology, not mesh.
- Nodes have numbers; names are yours. Battery nodes sleep and read `asleep`, which is normal; `dead` is the
  fault.
- "Alive" is lazy: the stack marks a node dead only after a command to it fails. A device that nobody has talked
  to can read alive for hours after it stopped answering.

## What the principles need from it
- **Health (rule 5).** Ping a lock when its last-seen is older than about two hours; a failed ping is what marks
  the node dead. Add a *radio noise* check from the controller's statistics (jammed-channel average above a
  threshold) and a *mesh failing* check (many nodes unreachable at once).
- **Automations.** Trigger on `event.*` entities, not on raw value-notification events, which double-fire and
  break when nodes are renumbered. Scene paddles: taps need a plain state trigger, hold and release attribute
  triggers, `mode: queued`. A lock can acknowledge and not execute: wait for the state you asked for.
- **Backups T4.** Monthly controller NVM backup, kept off-box. It carries lock codes: a secret.
- **Change control (rule 2).** Device firmware is frozen during any trip. Never batch firmware updates; stop at the
  first freeze. Keep a generated dump of every device's configuration parameters as the recovery reference after
  a factory reset.
- **Safety.** Locks and the code manager depend on this radio; the health rules above are what let the alarm
  trust a lock's state.

## How this goes wrong

- A device that crashes mid-firmware-update can jam the whole radio: every node goes unreachable, but a lock still
  reads locked and available for hours because the stack marks a node dead only after a command fails. Health
  stays green. The fix that works is cutting power to the crashed device; no restart, rebuild or re-pair acts on
  radio noise.
- A lock acknowledges a command within a second or two and never moves, with no jam flag and nothing in the log.
  Wait for the state you asked for.
- A factory reset wipes configuration parameters with no record of their values. Keep a generated parameter dump.
- A radio restart can replay old door-code events with no slot name; ignore such events.
