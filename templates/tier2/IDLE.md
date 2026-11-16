# IDLE.md - read-only work the support agent may do when nothing is wrong

*Status: template (O4b, 2026-10-14). Copied to `house/tier2/IDLE.md` with the brief. The OWNER adds items; the
agent only works them, and only when `pacing/preflight.py --role monitor` says `idle work: yes` (BRIEF.md section 7).*

Rules: read-only (reports, counts, drafts of a backlog item), never an action on the house; one item per idle
pass; a finding always comes first. When an item is done, the agent moves it to "Done" with the date and where
the result is.

## Items
| # | What to look at | Write the result to | Added |
|---|---|---|---|
| 1 | Entities unavailable for more than a day that no health check covers | a proposed `docs/health-checks.md` change | (owner fills) |

## Done
| # | Date | Result |
|---|---|---|
