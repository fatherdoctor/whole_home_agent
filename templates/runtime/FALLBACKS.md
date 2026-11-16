# Fallbacks: what the kit does when a capability is missing

*Status: written (KIT-RT0, 2026-10-23). The table of record for every runtime; `adapters/agents/other-agents.md`
keeps the first-session steps and points here. One row per thing the kit relies on, keyed to the `can:` keys that
STEP 0 records, so step d is a lookup: for every key that is `no` or `unknown`, take this row's path and name it in
the one-line report.*

How to read a row: **The kit uses** is the mechanism a principle assumes; **One runtime's form** is how the runtime
the kit was first built on provides it (vendor names appear here and in `adapters/agents/`, nowhere else in the kit);
**When missing** is the path every other runtime takes, in order where there is more than one; **Who it costs** is
who does the extra work. The principles do not change with the runtime; only the mechanism does.

| Key | The kit uses | One runtime's form | When missing, the kit does this instead | Who it costs |
|---|---|---|---|---|
| (always) | A standing brief that outranks the prompt | `CLAUDE.md` pointing at `AGENTS.md` | `AGENTS.md` is already the entry point; the runtime's own instruction file (project instructions, custom instructions, a `.github/` instructions file, a system message) gets one line: "Read AGENTS.md first." | nobody |
| `schedule` | Scheduled unattended runs (the lanes) | cloud routines on a trigger | In order: the platform's own scheduler (scheduled tasks, a CI cron on the repository, a cron or systemd timer on the box or a laptop that starts the agent with the lane's brief); else the **manual lane**: the person starts the lane's brief when they want a run. The brief is the same file either way; `agent.unattended` stays `false` until a scheduler that can push exists. | the person, a minute a run |
| `persistent_memory` | Memory across sessions | the memory directory | `house/docs/gotchas.md` (lessons) and, once the "what next?" helper exists, `house/docs/what-next-log.md` (history); both read at the start of every session by rule. | nobody |
| (always) | Skills and slash commands | `.claude/skills/*` | Plain prompt files under `tools/prompts/<name>.md`; the person pastes one or names it. A skill in the kit is always also a prompt file; the prompt file is the one the kit documents. | nobody |
| `box_access` | Reading and changing the box | an MCP server, or SSH and the API from the session | `install/agent-access.md`: the API with a token in the environment (inside an app, the Supervisor's proxy and the app's own Home Assistant tools, section 0, with nothing to set up); without that, `read: person-reads` (the person pastes what the box shows) and `deploy: person-pastes`, which Phase 0 already allows. A runtime that reads the box through a tool (an MCP server) rather than `HA_URL` records `no` here and uses that tool as its fallback path. Drive and calendar connectors: the clerk lists what to file and what to add, the person does it. | the person |
| `subagents` | Helper agents with their own tool lists (read-only verifiers, persona simulations, cheaper helpers for mechanical work) | per-agent tool allowlists | Reviews by a fresh session with the reviewer prompt; **no persona simulation against the live house** (an isolated copy only); the read-only verifier is the person reading the screen; mechanical work stays in the one session. | quality, a little |
| (always) | Deny-by-default permissions for unattended runs | a permission mode | A sandbox that refuses rather than asks; or `agent.unattended: false` (every change approved by the person) and no scheduled runs. | the person's time |
| `git_push` | Git push from the agent | Git with a checked guard hook | Run the hook check from the place you push from. If this computer cannot run hooks, diagnose why first. Follow the by-hand push in `templates/guard/README.md`: pass `--guard-only`, run the guard before every push, and push only after exit 0. Record the manual method and reason in the CHANGELOG. Repair a broken hook or refused commit; never bypass it. If no push is possible, give the person a diff to guard and push. A runtime returning only a draft PR records `git_push: no` and describes that in `variant`. | the person when a push must be handed back |
| (gate) | The usage probe and the pace line | the account's usage screen read by a script | Count mode: `setup.budget.runs_per_day` counted by `pacing/preflight.py --runs-per-day`, the brief stopping after `setup.budget.items_per_session` items; with an API key also a per-run cap and `--month-usd` (`budget-and-pacing.md` rules 7, 9). A usage page copied by hand goes stale within hours and is not a gate. | nobody |
| (card) | The assistant usage card (`packages/assistant-usage.yaml`) | the account usage endpoint read by `usage_reader.py` with the login's token, never refreshing it | With no reader for the runtime (or an API-key login): the card says "Not read yet" and every figure is unknown, never a guess; the person reads the provider's usage page. Another runtime gets the card by writing the same JSON file: on Codex, `usage_reader_codex.py` reads the client's own rate limits (`adapters/agents/codex.md`). | nobody |
| `read_files` | Reading the repository's files | a file-read tool on the clone | The person attaches the files the brief names (`AGENTS.md`, `house/profile.yaml`, the open backlog rows) or pastes them; with neither, the agent says which files it needs and stops (STEP 0, step e). | the person |
| `web` | Web access | a fetch tool | The person pastes release notes and the community thread; the update review marks a page "not read" rather than guessing. | the person |
| `long_context` | Long context | 200k tokens and more | Index-first reading order: `principles/00-index.md`, the backlog's open rows only, the newest 20 run-log lines; once the board package exists, its compact export (`board-open.md`) for runtimes under about 32k. | nobody |
| `notify_owner` | Notify the owner | a push tool from the session | The brief's last line is the message and the person reads the run; or a Home Assistant notification sent by a script the person approved once, to the owner only. | the person |
| `shell`, `write_files` | Scripts and file edits | a shell in the repository | With no shell: the agent writes the file's full contents in the reply and the person saves it; with no write at all, the agent is read-only and says so (STEP 0, pairs that cannot work). | the person |
| (roles) | Reviews by another model | separate lanes on two models | A fresh session of the same model with the reviewer prompt, told it did not write the thing; or the person. `house/runtime.yaml` names which model fills the reviewer role. | quality, a little |
| (setup) | An agent that can reach the box from the first step of setup | the terminal agent on a computer, or the agent's app on the box | A chat app on a tablet guides the first evening with no shell, no files and no box (`00-start-here/from-a-chat-app.md`; the app's limits in `adapters/agents/chat-apps.md`): the owner does every step and reads the screen back; one attached file (`00-start-here/chat-app-starter.md`) when the app cannot open the kit's address; a hand-off note the owner pastes into the agent on the box carries the evening over. | the person |

## When the fallback is a person

In an interactive session, ask once, with exactly what to do and where the material is, then wait. In an unattended
run with nobody in the session, write what is needed where the brief says (the run log, the backlog, a draft pull
request) and stop that step; never leave it only in the reply.

## Adding a row

A kit file may rely on a mechanism only if this table has a row for it (`README.md`, rule 1). To add one: name the
`can:` key it depends on (or `(always)`), the one runtime's form, the path without it, and who pays; then add the
key to STEP 0's probes table if it is new.
