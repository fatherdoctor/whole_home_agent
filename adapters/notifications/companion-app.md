# Companion app push

*Status: notes (O1), the iOS urgent-push lever added after the O4 dry run (2026-10-14). Used in practice on
Android; the iOS notes are from the companion app documentation, not experience.*

## What is different
- One notify service per phone, created when the app registers; the service name is not derivable from the
  person's name or the device's entity id. Look it up.
- Android and iOS differ in what they support. Android: real text-to-speech, a critical channel, up to three
  buttons, and doze (pushes without the timely flags arrive minutes late). iOS: critical alerts must be granted per
  device and degrade silently when they are not; no TTS; remote clears are silent pushes and can lag.

## What the principles need from it
- **Tags and replacement** (`notifications-and-tiers.md` rule 8): every push carries a tag; related states share a
  slot; clears go twice, a few seconds apart, at high priority.
- **Timely flags** (rule 13): `ttl: 0` and `priority: high` on every class that matters.
- **The critical flag is reserved** for the alarm's loud stage. On Android that is a channel at maximum volume plus
  spoken text (tones were silent when measured); on iOS a critical alert the owner has granted.
- **Urgent but not an alarm on iOS** (a water leak at 3 am, a door open while nobody is home): an ordinary push stays
  silent under a Focus such as Sleep, and critical is reserved. The lever is the interruption level:
  `data: {push: {interruption-level: time-sensitive}}`, which breaks through a Focus where the person has allowed
  Time Sensitive notifications for the app. Decide in Phase 1 topic 6 which classes carry it; the router template
  does not set it yet (a house adds it to its payload macro for those classes, with a test case).
- **A device name is a role** (`Owner phone`): the action name is made from it (`install/network-and-backups-first.md`
  section 5).
- **Buttons never go to a minor's phone** (rule 14); their devices get Dismiss only.
- **Never set `authenticationRequired` or `destructive` on an action**: the service returns 200 and the push is not
  delivered.
- iPhones do not reliably return the tag on an action; put it in the action data too.

## How this goes wrong

- A push with an unsupported action option returns 200 and never arrives.
- Android doze holds a normal-priority push for minutes; time-critical classes need high priority.
- A lone "clear" can be lost in a burst; send clears twice.
