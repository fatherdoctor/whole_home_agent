# Worked examples and dry runs

*Status: written (O4, 2026-10-14).*

| File | What it is |
|---|---|
| `pi-matter-apple.md` | A fictional house (Raspberry Pi 5 on NVMe, Matter over Thread and Wi-Fi, Apple Home, an agent other than the kit's first runtime) from Phase 0 to the plans for its first five backlog items, as the dry run walked it. |
| `dry-run-2026-10-14.md` | That dry run's 40 gaps, what was fixed, and what is still open, sized. |
| `lived-in-house.md` | The answer key for path C (an existing, lived-in Home Assistant): a fictional two-floor house on the `demo` integration, its sixteen planted faults with where each is caught, and the dry run's pass test. The seed (paste-ready YAML, a lab checklist, an offline test fixture with four planted fake secrets) is in `lived-in-house/`. Not for the agent under test. |

A dry run is the kit's acceptance test: a fresh agent, a deliberately different house, every guess recorded.
Run one after any large change to `AGENTS.md`, `interview/` or `install/`, with a stack the last run did not use.
