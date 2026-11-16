# Google Assistant

*Status: notes (O1). Used lightly in practice (scene scripts only). Templates: `templates/`.*

## What is different
- Same cloud exposure path and the same system user as Alexa; a separate per-entity exposure flag.
- Google's device model is stricter about types: a script exposed as a scene is the clean way to offer a
  multi-step action.

## What the principles need from it
- **Exposure is lights, switches and scene scripts only**; a handful of scene scripts is usually
  enough.
- **Attribution** needs the assistant's own activity log.
- If the same speakers are also used for announcements, the "one voice at a time" rule from
  `notifications-and-tiers.md` applies.

## How this goes wrong

- Nothing specific beyond the shared cloud-user attribution problem in `alexa.md`.
