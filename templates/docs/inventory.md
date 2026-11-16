<!-- Template: templates/docs/inventory.md (kit KIT-EXIST.b2, 2026-10-31). Written by
     `house/export/first_look.py --inventory` to house/docs/inventory.md in Phase 0E, step 3 (AGENTS.md), from the
     export's twelve files: the human read of the same, by area, by integration, the naming pattern the house uses
     most, and dashboards, apps, backups and users as counts. The script replaces each {{name}}; the comments
     are dropped. The agent then says what it found in six lines and asks nothing yet. Names of users are never
     written here; the export does not hold them. -->
# Inventory ({{date}})

Home Assistant {{version}}, read from: {{mode}}. {{counts}}.

## By area

{{areas}}

Device-backed entities with no area: {{no_area}}

## By integration

{{integrations}}

## Automations and scripts

Naming: {{naming}}. The house's own pattern is kept (`principles/naming.md`, legacy names); Phase 1 confirms it.

## Dashboards, apps, backups, users

- Dashboards: {{dashboards}}
- Apps: {{addons}}
- Backups: {{backups}}
- Users: {{users}}
