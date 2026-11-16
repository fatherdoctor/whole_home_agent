# Naming

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

Entity, device, area, helper and automation naming; ids that survive renames.

## The rule

1. [default, topic 2] **Name automations and scripts `Category - Target`**: "Motion Lighting - Guest Hallway", "Notify - Freezer
   Temperature", "Switch Control - Kitchen Island". The category is what kind of thing it is; the target is the
   room, device or person it acts on. Always set `alias`, `description` and `mode`.
2. [core] **An id is decided at creation and survives every rename. Never guess an id; read it back after creating
   anything.** Home Assistant derives an entity id from the name typed at creation time, then keeps it. Two
   devices from the same box, paired a week apart, can end up with different id shapes.
3. [core] **Select things by name AND id, never by an id prefix alone.** A renamed thing keeps its old id; a prefix
   match silently misses it.
4. [core] **When you rename a value (a mode option, a select option), rename it everywhere, including the helper's own
   option list, then drive one real transition to prove it landed.**
5. [core] **Check whether a helper exists before creating one.** A second helper with the same name silently becomes
   `_2`.
6. [core] **Do not reuse a word another system already uses for a mode.** If the alarm has an "Away" arm mode, the
   house's presence mode is "Not Home", not "Away".
7. [core] **Every device gets an area.** The built-in Overview, area cards and voice assistants all key on it.
8. [default, topic 2] **A hidden companion helper carries a suffix** (`_actual`, `_pending`); the person-facing one has the plain
   name.
9. [core] **Keep a readable record of label membership.** Labels live only in the entity registry; the UI shows them
   nowhere you can diff.
10. [default, topic 10] **Keep the YAML key order stable**: alias, description, triggers, conditions, actions, mode. Diffs stay
    readable and reviewers stop hunting.

## Why

Home Assistant 2026.11 may display a device name together with its entity name, including on cards without an
explicit name. The update keeps entity IDs and preserves changed display names as voice aliases. Check what the
person sees and hears before renaming anything; an explicit card name can keep a shorter display. The
[2026.11 release notes](https://www.home-assistant.io/blog/2026/11/04/release-202611/#name-it-once-home-assistant-adds-the-context)
also describe the planned deprecation of the `friendly_name` template attribute.

Ids are the only stable handle. Automations, scripts, dashboards and templates all hold them, and the system keeps
them from creation through every later rename. Names are for people and can change freely; ids cannot without a
registry edit and a reference sweep. Almost every silent failure in this area lived in the gap between the two:
the name said one thing, the id another, and nothing complained.

## How this goes wrong

- **A value renamed everywhere but its own list.** A mode option is renamed in every automation that sets it, but
  not in the select helper's option list, so every `select_option` call is rejected with only a log line. Symptom:
  the mode freezes for days and everything keyed on it stops. A runtime fix (`input_select.set_options`) does not
  survive a restart; only the stored definition does. Rule 4.
- **Selecting by id prefix.** A check that filters by an id prefix misses a thing renamed to the right alias but
  still carrying an old id. Rule 3.
- **A guessed id.** The id a helper gets is derived from its name by rules you do not control ("Re-Arm" becomes
  `re_arm`, not `rearm`). Symptom: a "not found" error only when the automation runs. Rule 2.
- **A silent duplicate.** Creating a helper whose slug already exists produces a `_2` twin with no warning, and
  automations keep pointing at the first one. Rule 5.
- **An id derived from a neighbor's.** Two similar devices share words in their ids; an automation built by
  analogy targets the wrong hardware. Rule 2.
- **Ids that drift from their names.** After a few renames, ids no longer say what the thing does ("away" in the
  id of something that now arms Stay). Renaming an id is a registry change with references to sweep, so get the
  name right before creating. Rules 1, 2.
- **A path or key that is not what you asked for.** The UI derives a dashboard's url path, and a script's YAML key
  and its entity id can differ after a rename; some integrations call scripts by key. Re-list and use the real
  value. Rule 2.
- **One word, two systems.** The presence mode and the alarm both use "Away", so "set it to Away" means two
  different things and a fix aimed at one changes the other. Rule 6.

## How to check it

- After any create: read the id back from Settings > Tools > States or `/api/states`. Never type it from memory.
- After any rename: grep the old string across automations, scripts, template files, dashboards AND helper option
  lists; then trigger one real transition and watch it land.
- A standing audit line: "every entity reference in automations, scripts, templates and dashboards resolves live:
  0 broken references". Run it after every rename and before every trip.
- Compare the count of an id-prefix selection against a name-based selection; if they differ, something was
  renamed.
- Review question: "If this is renamed next year, what still says the old name?"

## Adapter notes

- **Radios.** Expect id shapes to differ by integration: some integrations add an area prefix to the id at
  creation and others keep the name given at pairing. Read back, do not infer.
- **Z-Wave.** Trigger on `event.*` entities, not on raw value-notification events, which double-fire and break
  when nodes are renumbered.
- **Cloud thermostats.** One vendor's service matches room sensors by NAME, not device id, and a physically
  replaced sensor keeps the old one's name in the cloud list; unpair at the thermostat, the disabled flag in Home
  Assistant does nothing.
- **Marketplace.** Two integrations can share a display name; verify by repository.
- **Voice.** The name is what the assistant hears. Keep spoken names short, unique and free of model numbers.
  Exposure policy is in `safety-and-security.md` and `adapters/voice/`.
