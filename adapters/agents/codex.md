# Codex (OpenAI's coding agent)

*Status: notes (CX-KIT, 2026-11-09). Written from lab captures of the Codex CLI (0.165.0 to 0.167.0) on a Home
Assistant OS test box, 2026-11-04 to 11-08: one sign-in, one task, the usage read, the sandbox inside an app. Not
yet run through the kit end to end (KIT-DRY ran on the first runtime only), so treat every line below as a lab
finding, and every `can:` value as something STEP 0 still probes. The mechanisms table is
`templates/runtime/FALLBACKS.md`; the first-session steps for any runtime other than the first are in
`other-agents.md`, and this page adds what is particular to Codex.*

## What is different
- **Reads `AGENTS.md` itself.** The kit's entry point needs no pointer file on this runtime (`other-agents.md`,
  step 1, has nothing to do).
- **Two ways to run it:** the terminal client (`codex`) on a computer or on the box, or a Home Assistant app that
  wraps the client and gives it a chat page. The app drives the client's app server (`codex app-server`, JSON lines
  over stdin and stdout), not the one-shot `codex exec`; that matters for the usage card below.
- **Permissions are a sandbox plus an approval policy,** set in the client's config (`$CODEX_HOME/config.toml`,
  `~/.codex` by default) or on the command line: the sandbox (`read-only`, `workspace-write`) limits what a command
  can touch, and the approval policy (`on-request` in the lab) decides when it asks the person. There is no separate
  per-tool allow and deny list of the kind the first runtime has.
- **Sign-in is the person's account, by a device code:** `codex login --device-auth` prints a short code and a web
  address; the person enters the code on any phone or computer. The sign-in lives in the client's home folder.

## STEP 0 on this runtime
Run the probes as `STEP-0.md` says; record the runtime as `other` with the product in `variant`, and a place when it
runs in more than one:

```
python3 templates/runtime/probe_runtime.py --runtime other --variant "Codex CLI <version>" --place box \
  --set schedule=no --set subagents=unknown --set persistent_memory=no --set notify_owner=no
```

What the lab saw for the keys the script takes on trust (`--set`); re-check each on your version, and change the line
when the evidence differs:

| Key | What to look for on Codex | Lab result |
|---|---|---|
| `schedule` | The client has no scheduler of its own; a cron or systemd timer that starts `codex exec` with a lane's brief is the platform's scheduler (`FALLBACKS.md`, schedule row) | `no` until you add such a timer |
| `subagents` | A tool in this session that starts another agent with its own tool list | not checked: `unknown`, which takes the fallback (single-agent reviews, no persona simulation against the live house) |
| `persistent_memory` | Something the client kept from an earlier session that you can read now | `no`: lessons go in `house/docs/gotchas.md` |
| `notify_owner` | A tool that pushes to the owner's phone | `no`: the run's last line is the message |
| `long_context` | Your context size, if the client states it | say it, or `unknown` |

In a Codex cloud task (a container with a fresh clone, no box), add `--where cloud`: the script does not recognize
that container's markers and would otherwise record a computer, and the cloud rules (no box actions, hand over the
files or the diff before the task ends) would not be applied.

The probes the script runs itself (shell, files, git, web, box) need no special handling. Inside the app, the
box probe goes through the Supervisor's proxy (`install/agent-access.md`, section 0) and says so.

## What the principles need from it
- **Permissions.** For unattended runs, a sandbox that refuses rather than asks (`FALLBACKS.md`, the
  deny-by-default row): with nobody to answer, an approval request is a hang. Until a household has tried that on
  its own version, keep `profile.agent.unattended: false`.
- **The secrets deny list.** The kit has not found a per-path read deny on Codex: record that in `house/runtime.yaml`
  and keep `other-agents.md` step 5's fallback (the standing rule "A secret in your output is a leak" is the only
  fence). The sandbox limits writes and commands, not which files the agent reads.
- **The push guard.** Install the git hook (`templates/guard/README.md`); a push from inside the sandbox needs the
  network, which `workspace-write` leaves off by default, so expect `git_push: no` there and hand back a branch or a
  diff (`FALLBACKS.md`, git row).
- **Memory.** No memory of the kit's kind: `house/docs/gotchas.md` and the what-next log, read at the start of
  every session by rule.

## The usage card
`templates/runtime/usage_reader_codex.py` writes the same file as the first runtime's reader, so the package, the
card and the pace gate need no change (`FALLBACKS.md`, the "(card)" row). It asks the client's app server for the
account's rate limits (`account/rateLimits/read`): no model call, and it never opens the sign-in file or sees a
token, so there is nothing of the sign-in for it to leak or rotate.

- **Install:** copy it next to `usage_reader.py` in `house/usage/` (it uses that file's day and weekly-reset
  bookkeeping), on the machine where Codex is signed in, and schedule it every 15-30 minutes:
  `*/20 * * * * python3 house/usage/usage_reader_codex.py --out /config/assistant_usage/usage.json --tz Area/City`.
  `--codex` names the client when it is not on the PATH; `--codex-home` the client's home folder when it is not the
  default.
- **What it reads:** each window by its length: exactly a week (10080 minutes) is the weekly figure, exactly 300
  minutes the 5-hour one; a window of any other length is left out, not renamed. Only a weekly window has been seen
  in a real reply (the lab's plan has no other), so the 5-hour placement is unverified; a plan with only a weekly
  window leaves the 5-hour figure unknown. A percentage outside 0-100, a window length that is not whole minutes, or
  a weekly window without a reset time is `unknown` ("reply shape changed"). Codex gives no per-model weekly
  figures. The plan name comes from the reply.
- **Check it once by hand:** `--dry-run` prints the file. The client's own `/status` screen shows the percentage
  **left**; the file holds the percentage **used** (the same as the first runtime), so 100 % left is 0 here.
- **Offline:** `--reply` replays a saved reply: a bare result, or a whole app-server transcript (JSON lines). A saved
  reply carries no token; account ids in it are better removed before it is kept as a test fixture.
- **When it fails:** signed out, or the client refuses the read, is `status: error` with the client's own words; a
  reply without a usable weekly window is `unknown` ("reply shape changed"). Either way the last good figures stay
  and age out on the card. Only figures this reader wrote stay: when the file was last written by another runtime's
  reader (a household switching runtimes), the first read starts afresh and never shows that account's figures. The app-server methods are the client's interface, not a published web API: a new client version
  can change them, so check the card after each update.

## Install on the box and sign in
*Lab notes, not yet walked end to end (CX-SWEEP).* The app route: a Home Assistant app wraps the client and
gives it a chat page (see "What is different"); which app repository and which steps the kit recommends is not
decided, so this page has no click-by-click walk-through. Not verified: the app's install steps on a fresh box.
Sign-in is the device code described under "What is different": `codex login --device-auth`, then enter the code on
any phone or computer. The sign-in lives in the client's home folder, so on the box treat a backup as a secret, as on
the first runtime.

## Access on the box
*Lab notes, not yet walked end to end.* What this runtime's app declares for the Supervisor (role and API
flags), and which folders it can write, has not been read for the kit: check the app's own configuration before
you rely on the first runtime's page (`claude-code.md`, "Access on the box") for anything. Inside an app the
sandbox needs the app's own wrapper (see "How this goes wrong").

## Resuming a session
*Gap: not captured in the lab.* The terminal client is started with `codex` from the repository folder; whether and
how it continues an earlier conversation after the person leaves the chat for a shell line was not tested. Until a
lab run says otherwise, write where you are to `/share/kit-setup-note.md` before sending the person to the shell and
start the new session by telling it to read that note.

## Changing the model
*Gap: not captured in the lab.* Say which model you are running as, or that you cannot see it, and ask the person how
this client changes it (its config file, `$CODEX_HOME/config.toml`, or a command-line option).

## Scheduled jobs
Covered under STEP 0 above (the `schedule` row): the client has no scheduler, so a cron or systemd timer that starts
`codex exec` with a lane's brief is the platform's scheduler. Not yet run unattended in the lab.

## How this goes wrong
- **A forced re-sign-in throws away the working one.** In the lab, starting a new device sign-in on a client that was
  already signed in, and restarting before the new code was entered, left it signed out. Do not start a sign-in "to
  check"; check with the usage read or the client's own status instead.
- **The sandbox inside a Home Assistant app.** Codex's Linux sandbox uses bubblewrap. Inside an app container
  plain bubblewrap fails ("Permission denied", or "No permissions to create a new namespace"); the app's own
  wrapper made it work for the app's own server process. Unverified: whether that wrapper also works for a
  command the agent runs. The lab's two in-task probes called the plain system bubblewrap, not the wrapper, and both
  failed; a side-by-side test with the wrapper has not been run, so do not rely on a task starting its own sandbox
  until it has.
- **Approved commands may run in a login shell.** In the lab, the commands one app's agent ran after approval
  went through `/bin/sh -lc`, which resets the PATH, so a tool the app put on the PATH was not always found. That
  was one install's approved-command path, not a documented rule for every client or setup; check the PATH an
  approved command sees before relying on it.
- **A slash command typed into a chat page is not a command.** Through an app's chat page, `/status` reached the
  model as ordinary text and was answered as a question; only the terminal client runs its slash commands.
- **The client version can change under you.** One lab install reported 0.166.0 one day and 0.167.0 the next with
  no update run by hand; no update event was captured, so how it changed (the client's own updater, or the app
  or image around it) is unverified. Pin the version where the household cares, and re-run STEP 0 and the usage
  check after any version change.
