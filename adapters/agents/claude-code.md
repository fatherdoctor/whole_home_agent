# Claude Code

*Status: notes (O1); the token file and changing the model (KIT-DRY.f6, 2026-11-10). Used in practice. Templates:
`templates/`.*

## What is different
- Reads `CLAUDE.md`, which in this kit only points at `AGENTS.md`. Has a permission system (ask, allow, deny per
  tool and command), a per-project memory directory, sub-agents with their own tool allowlists, skills, and
  scheduled routines that run in the cloud against the repository.
- Can run on the box inside an SSH or terminal app, or in the cloud with the repository only.

## What the principles need from it
- **Permissions.** Unattended runs use a deny-by-default mode so a prompt refuses rather than hangs. The tier-2
  agent never has a raw shell; it has two wrappers (`tier-2-support-agent.md` rule 4).
- **The secrets deny list, from level 0** (interactive sessions too): merge the `deny` entries of
  `templates/runtime/claude-code-settings.json` into the project's `.claude/settings.json` (or the user settings on
  the box) before the agent first reads the box. They stop the file tools reading `secrets.yaml`, `.storage/`, the
  recorder database, backups and credential files. The same rules also stop `cat`, `head`, `tail`, `sed`, `tee` and
  `<` or `>` on those paths in a shell command. They do not stop `grep -r` or a script that opens the file itself:
  the standing rule in `AGENTS.md` ("A secret in your output is a leak") is what keeps those reads by file and count.
  **A Home Assistant token kept in a file** (an option for an owner who does not use a terminal): the list denies
  any file whose name starts `ha_token`, anywhere, and the folder `~/.config/home-assistant/`; so name the file
  `ha_token`, keep it outside the repository (`~/.config/home-assistant/ha_token` is the suggestion), readable by
  its owner only (`chmod 600`). The deny list refuses `cat` on that file too, so the token is read by the kit's
  reader, a script that opens the file itself (`install/agent-access.md`, section 2), never by a shell `cat` in the
  chat; it is never printed.
- **Sub-agents** are how persona simulations and the read-only verifier are made structurally safe: a persona's
  agent file lists read-only tools; only the verifier lists the house's read tools.
- **Memory.** Lessons go into the memory directory the day they are learned and are exported into the wiki's raw
  notes so cloud routines can read them (`working-with-the-agent.md` rule 6).
- **Routines.** Scheduled cloud runs read a standing brief file from the repository (the brief outranks the
  prompt), commit through the push guard, and start behind the no-model preflight (`templates/pacing/preflight.py`;
  `budget-and-pacing.md` rule 3): the scheduler runs it and starts `claude` only on GO. They have the repo only:
  draft PRs and design docs, never a deploy. They never subscribe to pull-request activity (`board-and-lanes.md`
  rule 21). With an API key, pass `--max-budget-usd` on every print-mode run (`budget-and-pacing.md` rule 7).
- **The usage probe** reads the account's usage screen at no token cost; `templates/pacing/usage_probe.sh`.
- **Scheduled jobs** (`board-and-lanes.md` rule 23). Cron is UTC for scheduled tasks created inside a session; those
  die with the session and expire after about seven days even while it lives, so a job that must survive lives in
  the cloud scheduler or a cron on the box. **A resumed conversation can run twice:** `claude --continue` or
  `--resume` in a second terminal opens the same conversation again, and its session crons then fire once per copy
  (one real install had one conversation open in three panes, with each cron due three times). Before resuming,
  check no other terminal holds that conversation; to spot a duplicate, look for two run-log lines for the same job
  within a minute, or list the session's scheduled tasks in each open copy.

## How this goes wrong

- A permission check can refuse a shell change in the middle of a rehearsal; plan for a human step rather than a
  workaround.
- A session that re-creates its own scheduled task after a crash leaves two schedules running the same job. Keep
  one schedule and check the list weekly.
- Several sessions sharing one credentials file: a long session keeps a token after it is rotated and fails until
  restarted.
- A file-push tool with no stale-content check overwrites a commit made a minute earlier. Use git with a rebase,
  through a guard that exits non-zero.

## Access on the box: what the app grants

*Moved here from `install/agent-access.md`, section 0 (CX-SWEEP); the text is unchanged except for its pointers.*

What the app already grants (from its own README; re-check it when a name does not match):
- **Reading the house.** With its `enable_mcp` option on (the default) you have Home Assistant tools that read
  states, list services and act on entities. Underneath, the Supervisor proxies the same API at
  `http://supervisor/core/api/` with `SUPERVISOR_TOKEN` (handed to the app at each start, and since app
  1.2.65 not written to disk by it - an older add-on wrote it into a file inside the configuration folder, so
  inside backups: update first; never print it). The app exports that address and token as `HA_URL` and
  `HA_TOKEN` for you. The read check in `install/agent-access.md`, section 3, uses them once the owner has
  confirmed this is the right box (section 2) and that confirmation is in `house/profile.yaml`; with no profile
  yet, Step 0 records `box_access: unknown`. After that, `templates/runtime/probe_runtime.py`
  reports `via the Supervisor (inside an add-on)` for it (also with `SUPERVISOR_TOKEN` alone, if a future app
  stops exporting them).
- **The Supervisor role.** The app declares `hassio_api: true` and `hassio_role: manager` (its `config.yaml`,
  version 1.2.65, read 2026-10-31). The role is what the Supervisor checks: `manager` reaches `/addons`, `/backups`
  and `/mounts`, which the existing-house inventory reads (`templates/export/export_house.py`, `addons.json` and
  `backups.json`); the default role reads only the `/*/info` paths. If a later version lowers the role, those two
  files answer `unknown` with the 403 named, never "no add-ons" or "no backups". `manager` can also start, stop and
  update apps: the export only reads, and that is your brief's rule, not the Supervisor's.
- **Files.** `/homeassistant` (the configuration folder, read-write), `/share` and `/media` (read-write), `/ssl`
  and `/backup` (read-only). The household repository lives at `/share/<repository name>`
  (`00-start-here/getting-the-kit.md`, part 2): a durable folder inside the box's backups, never the scratchpad
  or `/tmp` (a restart wipes it) and never `/homeassistant` itself. The app's own sign-in lives in
  `/homeassistant/.claudecode/` and travels inside every backup: a backup file is a secret. Read-write on
  `/homeassistant` includes `secrets.yaml` and `.storage/`: install the deny list
  (the secrets deny list, under "What the principles need from it", above) before the agent's first read.
- **Deploying** is a file copy inside the box, `house/ha/packages/` to `/homeassistant/packages/`, after the
  person's go. The check: the app's README does not say it ships the `ha` command, so until you have seen it
  run, the check is **Settings > Tools > YAML > Check configuration**, pressed by the person and read back, or the
  Supervisor's own check (`POST http://supervisor/core/check`, same token); an error is a failure and a partial
  success is a failure. Reload rather than restart, as `install/agent-access.md`, section 4, says; a restart stays an "ask first" action.
- **Be honest about the limit, sharper here than in `install/agent-access.md`, section 1.** The app runs as root with full access to
  the box and the Supervisor API: it can restart Home Assistant, change any file and act on any entity. The
  owner's [optional guard rails](../../templates/agent-guard-rails.md) are instructions, not access controls
  enforced by Home Assistant. Say that to the person in one line.

Options of the app that need a decision (ask, write the answer into `house/profile.yaml` and the CHANGELOG):
- **`auto_update_claude`** (on by default): the app updates Claude Code at each start, and rolls the update
  back by itself when the new version cannot run. So turning it off is a change-control choice, not a safety one:
  a household in a freeze (`principles/change-control.md`) turns it off in the app's configuration.
- **`working_directory`** (default `/homeassistant`): the person sets it to `/share/<repository name>` once the
  repository exists, so every session opens inside it and its `CLAUDE.md` is read for you. The household's rules
  belong in that repository `CLAUDE.md`, never in `/homeassistant/.claudecode/CLAUDE.md`: the app rewrites that
  file at every start.

## Install on the box and sign in

*Moved here from `00-start-here/README.md`, path B, steps 2 and 3 (CX-SWEEP).*

1. **Install the Claude Code app.** Settings > Apps > Install app > the three dots (top right) >
   Repositories > paste `https://github.com/robsonfelix/robsonfelix-hass-addons` > Add. Back in the store, find
   **Claude Code**, Install, Start, then **Open Web UI** (it also appears in the sidebar). This is an app from the
   app store, not the Marketplace. The Marketplace is built in and is not needed for this app.
2. **Sign in.** The web UI is a terminal. Type `claude` and press Enter. It shows a link: open it in a browser (your
   phone is fine), sign in to your Claude account there, copy the code it gives you, and paste it back into the
   terminal. The terminal's paste keys are a computer's (`Shift+Insert` or `Ctrl+Shift+V`); if paste does nothing
   on a phone, type the code (it is short), or do this one step from a computer's browser. Untested on a phone until
   a lab run says otherwise. The sign-in is stored on the box and travels inside its backups, so from now on a backup
   file is a secret: keep it where you keep passwords.

## Resuming a session

*Moved here from `00-start-here/README.md` (path B, step 4), `existing-house.md`, `getting-the-kit.md` and `AGENTS.md` (CX-SWEEP).*

- When a step sends you out of the chat to type a line at the shell (in the app, leave the chat with `/exit`),
  come back with `claude --continue` (`cc` for short), not `claude`: plain `claude` starts a new conversation that
  remembers nothing of the old one. On the box, a fresh session told to read `/share/kit-setup-note.md` continues
  from it (the note exists only there; a computer session resumes from the repository).
- Once your private copy exists at `/share/<repository name>`, start every session with
  `cd /share/<repository name>` and then `claude` (or `cc`, which picks up the last conversation): the app opens
  in the configuration folder unless told otherwise, and there it finds neither `AGENTS.md` nor your notes. The
  one-time alternative is the app's `working_directory` setting (its Configuration tab) set to
  `/share/<repository name>`, after which plain `claude` opens there.

## Changing the model

- **See the list.** `/model` with nothing after it shows the models your plan offers, the current one marked.
  That list, read back by the person, is how the agent fills `model_roles` in `house/runtime.yaml`: a model not on
  it is not available to this household, whatever the agent remembers.
- **Switch.** `/model <name>`, for example `/model sonnet`; the short names `opus`, `sonnet` and `haiku` point at the
  current model of each family, so they do not go stale. The choice also becomes the default for new sessions. For
  this session only, open `/model`, move to the row and press `s`; or switch back when the plan is done.
- **Confirm.** `/status` shows the model in use. The agent may not see a switch made after its session began, so
  after a switch the person reads that line back rather than the agent guessing.
- **Which one for which role** (a starting point; the household's list decides): `planner` and `reviewer`,
  `opus`; `builder` and `writer`, `sonnet`; `mechanical` (setup, sweeps, counts), `sonnet`, or `haiku` for plain
  counts and extractions. A plan without `opus` maps its roles to `sonnet`. The agent says which role it is using.
- **Cost.** On a monthly plan a bigger model costs no extra money; it uses the allowance faster. With an API key it
  costs more per token (`principles/budget-and-pacing.md` rule 10).

## Running the tier-2 agent

Run with a deny-by-default permission mode, an explicit model, the brief as an appended system prompt file, and a
session name a panel's terminal will not attach to by accident (`principles/tier-2-support-agent.md`). Per-run cap
on an API key: `--max-budget-usd` in print mode (`principles/budget-and-pacing.md` rule 7).

## Per-runtime quirks

Runs as an app on the box with a memory directory; its permission classifier can refuse persistence-shaped
actions mid-run, so plan for a human step; scheduled cloud routines read a standing brief and commit through the guard.
