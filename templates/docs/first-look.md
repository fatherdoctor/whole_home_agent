<!-- Template: templates/docs/first-look.md (kit KIT-EXIST.b2, 2026-10-31). Written by house/export/first_look.py
     to house/docs/first-look.md in Phase 0E, step 4 (AGENTS.md); the agent does not fill it by hand. The script
     replaces each {{name}}; the comments are dropped. Kinds are the words of principles/health-checks.md: a fault
     is a thing a working system never produces, a risk is a gap that has not hurt yet, a notice is visible and
     never pages. Each finding is an offer; the person may answer "leave it" to any line. A risk on the level 0
     or level 1 list that is left is recorded as left and comes back only when the readiness test names it (KIT-EXIST
     rule 7). An `unknown` check is never "nothing found": its note says what would let it read. Nothing here holds
     a secret: files, lines, ids and counts only. Levels: E0-first-look reads this page's date and the backup
     (4), login (5) and secrets (10) lines. -->
# First look ({{date}})

Read-only, read from: {{mode}}. **Nothing on the box was changed.**

{{summary}}

## Findings

{{findings}}

The offers become rows in the backlog's tidy-up section (`templates/docs/backlog.md`) only when the person says
so; a level 0 or level 1 row stays listed until done or recorded as left.

## The twelve checks

{{checks}}
