# house/ - the person's own files

*Status: layout declared (O2, 2026-10-13). Created by the Phase 0 interview. Everything in here is yours; the kit
writes here only through the interviews and the Phase 2 loop.*

| Path | What it is | Written by |
|---|---|---|
| `profile.yaml` | Your answers; the record every session reads first. Schema: `interview/profile-template.yaml`. | the interviews |
| `runtime.yaml` | What each assistant runtime you use can do here (shell, git push, the box, a scheduler ...) and which model fills each role. Template: `templates/runtime/runtime.yaml`. | STEP 0 of every run (`templates/runtime/STEP-0.md`) |
| `docs/CHANGELOG.md` | Every change, newest first, with the undo. | every change |
| `docs/backlog.md` | What is planned, sized, with the decisions written as questions. From level 2 only the rulings and the questions; the items move to the board. | the interview, then every idea |
| `docs/board.md`, `docs/card-names.tsv` | The board: every card with its status, the run log; and a plain name per card. Template: `templates/docs/board.md`; grammar: `templates/docs/board-format.md`. | every session and lane, the planner |
| `docs/reviews/`, `docs/asks/` | One file per review row (`templates/docs/review.md`); one page per owner card that is more than a sentence. | the reviewer; whoever needs the owner |
| `docs/gotchas.md` | Lessons, one per failure, with the rule each taught. | the day a lesson is learned |
| `docs/naming.md`, `docs/policies.md`, `docs/notifications.md`, `docs/health-checks.md`, `docs/operations.md` | Your house's own rules, generated from the profile and the principles. | Phase 1, then by hand |
| `docs/user-manual/` | For the household and sitters, in plain words. | Phase 1 skeleton, then as behavior changes |
| `docs/wiki/` | For the builder: one page per integration, device, package, automation, dashboard. | Phase 1 schema, then the writer |
| `ha/` | A mirror of the box's configuration folder: `packages/`, dashboards. Deployed from here; never the only copy of anything (the box has the live one, the backup has the rest). | Phase 2 |
| `export/` | The live export: areas, devices, entities, automations, as the box reports them. The truth when a document disagrees. | an export script, never by hand |
| `tier2/` | The support agent's brief and checker, when you want one. | after the router and the health counts |
| `pacing/` | The usage probe and its readings. | its backlog item (usage probe and budget gate); then the probe |

Never in here: `secrets.yaml` or any copy of it, codes, tokens, phone numbers, addresses, recovery keys. A push
guard should refuse the commit (`principles/working-with-the-agent.md` rule 9).
