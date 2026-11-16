# Gotchas

**Status (YYYY-MM-DD): created in Phase 0 at the first lesson or install-guide correction (`AGENTS.md`, Phase 0),
else by the Phase 1 interview. Owned by the house; one entry per lesson, added the day the lesson is learned.**

<!-- Template: templates/docs/gotchas.md (kit O3b). Principle: principles/documentation.md rule 2.
     How to use it:
     - ONE failure mode per entry, filed under its area. Read the area's section before touching that area.
     - Write the RULE, not the value: "the lock reports battery in steps of 10, so a threshold of 15 % behaves like
       10 %", not "the front lock is at 40 %". Values go stale; rules do not.
     - Every entry has the incident that taught it (date, what happened, how it was noticed) and how to check it.
     - Lessons stay here. Long narrative moves to an archive file, and only AFTER its lesson is extracted here.
     - The Phase 1 interview seeds this file from `priorities.never` answers that are lessons (things that went
       wrong before); otherwise the areas start empty, which is fine.
     Delete this comment when the first real entry is written. -->

## How an entry looks

### <the rule, as one sentence a newcomer can follow>
- **Incident:** YYYY-MM-DD - <what happened, and how it was noticed>
- **Why it happens:** <the mechanism, in two or three sentences>
- **How to check:** <a template, a command, a page to look at>
- **See also:** <CHANGELOG entry, design doc, principle>

## Areas
<!-- Keep this list in the house's own words (docs/naming.md); add an area the first time it has a lesson. -->

### Home Assistant core and configuration

- **Put back what a test toggled.** A helper, switch or scene you flip to test something is returned to its prior value
  in the same run, and the run says so.
- **Config API deletes strip YAML comments.** Delete a block by editing the file, not through the config API, or the
  comments around it are lost.
- **Success with an empty `affected_entities` is a no-op.** A service call that reports success but names nothing it
  touched did nothing; check the entity afterward.
- **The history API defaults to one day.** A replay or a "last seen" check that needs more asks for its window.
- **A time older than today names its day.** Notification text for an event that is not from today says "yesterday at
  9:10 PM" or the weekday, never a bare clock time.

### Notifications

### Health checks

### Lights and switches

### Climate

### Doors, locks and the alarm

### Radios (Zigbee, Z-Wave, Matter, Wi-Fi)

### Dashboards and the wall panel

### Voice assistants

### Backups and recovery

### The agent and its routines
