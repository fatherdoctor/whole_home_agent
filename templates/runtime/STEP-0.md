# STEP 0 - where am I

*Status: written (KIT-RT0, 2026-10-23). Every kit prompt, brief and tool runs this block first, on every runtime.
The fallback table is `FALLBACKS.md`; the record is `house/runtime.yaml` (template: `runtime.yaml` in this folder);
the script that runs the probes for you is `probe_runtime.py` (KIT-RT0s, 2026-10-23: it runs the shell, file,
git, web and box probes itself, takes the rest and the runtime's name from the agent, and prints the step-d line;
usage in its docstring). The rules that keep the rest of the kit runtime-neutral are in `README.md`. Where you are
and what GitHub can do, told to the owner in two lines: KIT-STEP0, 2026-11-10, "Where you are" below.*

The kit runs on more than one assistant: a terminal agent on the person's computer, a cloud session with only the
repository, a chat with files attached, another vendor's agent. Each has a different set of tools, and a prompt that
assumes a tool it does not have either hangs, invents a result, or asks the person for something it should have
found out itself. So every run finds out where it is first, from evidence, says which path it chose, and then acts.
The kit names model tiers by **role** (planner, builder, reviewer, mechanical, writer), never by product; the
household maps roles to the models each runtime offers in `house/runtime.yaml`.

## The block (verbatim; a brief quotes it or says "Do STEP 0 (templates/runtime/STEP-0.md) first")

```
STEP 0 - WHERE AM I. Before anything else:
a. Observe which runtime you are (the names table). Read house/runtime.yaml if it exists. If it has an entry for
   the runtime you observe, dated under 7 days ago: an interactive session skips to d; an unattended run still runs
   the probes in b (they take seconds) and rewrites the entry only if a value changed. Otherwise detect:
b. Decide from evidence, never from assumption, and record each as yes / no / unknown:
   runtime: claude-code | claude-cloud | claude-app | other (name it in `variant`)
   can: shell | read_files | write_files | git_push | web | schedule | subagents | long_context (over 100k) |
        persistent_memory | box_access (reach Home Assistant) | notify_owner
   Probe cheaply (the probes table): run `echo ok` (shell); read AGENTS.md (read); write house/.probe, read it back,
   delete it (write); `git push --dry-run --no-verify origin HEAD` (git); fetch
   https://version.home-assistant.io/stable.json (web); look for a tool that creates a scheduled or recurring task,
   or a cron you may edit (schedule); look for a tool that starts another agent with its own tool list (subagents);
   say your context size if you know it, else unknown (long_context); look for a memory you did not write this
   session (persistent_memory); for box_access, ask the owner to confirm the box as described in
   install/agent-access.md section 2, then use the reader in section 3. With no profile yet, record unknown:
   "no profile yet; the owner confirms the box in install/agent-access.md section 2". A different address or a
   failed check stops the read before loading a token. Inside an app, the check is the owner's confirmation only.
   --no-box skips the box and token reads and records box_access unknown. Look for a tool that pushes a message to the owner (notify_owner). A probe that errors
   is "no". Never probe by sending anything to a person, and never print a token or a URL that names the house.
   Also record where you run (`where`: box | cloud | computer) and what GitHub can do from here (`github`: push |
   read-only | no-reach | none); "Where you are" below says how, and what each answer changes.
c. Write your entry in house/runtime.yaml (template: templates/runtime/runtime.yaml), with today's date when a value
   changed or the entry is over 7 days old; with no write access, state the same block in your reply and ask the
   person to save it.
d. For every capability that is no or unknown, take the path templates/runtime/FALLBACKS.md gives, and say in one
   line which runtime you found and which fallbacks apply, e.g.
   "claude-app: shell no (I write each file out in full and you save it), git push no (I hand you the diff),
   schedule no (you start each run), subagents no (single-agent reviews), box no (you read the box to me)."
   Then tell the owner the two plain lines the script prints last: where this is and what that changes, and GitHub.
e. If the brief you are running needs a capability you lack and the table gives no fallback, or its fallback is a
   person and nobody is in this session, stop and say what is needed and from whom.
```

## Where you are, and what it changes (KIT-STEP0)

The same kit is started in four kinds of place. Step 0 finds out which, from evidence, and the rest of the session
behaves for that place. The script decides the last three (`where` in `house/runtime.yaml`); `--where` overrides it
when you know better, and says so.

| Place | How you tell | What it changes |
|---|---|---|
| A chat (no shell) | you cannot run a command; files arrive as attachments | Say so in one line; record nothing (there is nowhere to write it); ask only what you must, as a question about what the owner sees ("what does the box's screen show under Settings > About?"); every step is the owner's ("A chat app before the box has an agent", below). |
| `cloud` | the runtime is a cloud session (`claude-cloud`, or the marker such a session sets); a fresh clone, no `/share`. The script knows one vendor's marker only: in another vendor's cloud container (a Codex cloud task, for example), pass `--where cloud` yourself | No box actions from here, ever: write the change package (the exact edits, the check, the undo) and hand the owner the steps, or tell them to carry on in a session on the box. The repository is the only thing you change, and nothing written here outlives the session unless it is pushed. |
| `box` | the Supervisor's token is set (an app on the box), or `/share` sits beside the config folder | Path B (`AGENTS.md`, "Already installed"): skip the install steps and read the box directly, once the owner has confirmed it is their box (`install/agent-access.md` section 2; the saved fingerprint, `box_url_sha256`, is checked before any token is read). The house folder lives in `/share/<repository name>`. |
| `computer` | a shell, and the script found no box folders and no cloud marker (which is not proof there is none) | The phase table decides; the box is reached only through `install/agent-access.md` (or the owner reads it to you). |

**GitHub (read-only, never printing a token, the account or the address).** The script checks: git present; this
folder a repository with an `origin`; a credential set up (an environment variable's name, a git credential helper,
or `gh auth status` by its exit code only); whether `origin` answers `git ls-remote`; and the push dry run above. It
says only the remote's kind, GitHub or another git server, and records `github`. What is not pushed lives where the
session is: on the box, local and in the box's backups; on a computer, on that computer only; in a cloud session,
nowhere once the session ends.

| `github` | Means | What it changes |
|---|---|---|
| `push` | the remote answers and the dry run passes | The house folder is kept on the remote as well (on the box, also in its backups); push after each change as the brief says, and in a cloud session before it ends. |
| `read-only` | the remote answers, the push would be refused (no credential, one without write access, or the branch cannot be pushed as it stands: a detached HEAD, no upstream) | Keep changes in the folder; hand the owner the push or a diff (`FALLBACKS.md`, the `git_push` row). In a cloud session, hand over the files or the diff before it ends. |
| `no-reach` | `origin` is set but did not answer (offline, a wrong address, an expired sign-in) | The folder stays where the session is until the remote answers (see above); say which, and that GitHub is optional. |
| `none` | no git, no repository, or no `origin` | The folder stays where the session is (see above); GitHub is optional (`00-start-here/getting-the-kit.md` part 2 when the owner wants it). |

**The model and the plan.** Say which model you run as when the runtime shows it, else that you cannot see it
(`AGENTS.md`, "Which model, said out loud"); never name a plan the owner has not named.

**The two lines.** The script ends with them; they are what the owner hears, e.g. "I am running in a cloud session
with a fresh copy of the repository and no way into your box: I change nothing on the box from here; I hand you the
steps, or we carry on in a session on the box." and "GitHub: I can read the repository but not push to it as it
stands, so nothing written here outlives this session: I hand you the files or the diff before it ends." On a
computer the second line says the folder is on that computer only; only on the box does it name the box's backups.
An entry written before KIT-STEP0 has no `where` or `github`; `--if-stale` probes it rather than guess either line.

## The runtime names

Pick the one that matches what you observe, not what you were told. When two fit, pick the narrower and put the
rest in `variant`.

| Name | What it is | What usually tells you |
|---|---|---|
| `claude-code` | Claude Code in a terminal or an IDE, on the person's computer or on the box | a shell in the person's own file system; `CLAUDE.md` was read for you |
| `claude-cloud` | A Claude Code cloud session or a scheduled routine: a fresh clone, no box, often no person watching | the clone is new, there is no `HA_URL`, the prompt says it is a scheduled run |
| `claude-app` | Claude chat (web, desktop, mobile) with files attached or a project | no shell, no git; files arrive as attachments |
| `other` | Anything else (another vendor's agent or chat); name it in `variant`, and say there what hands your work back (a pull request, a diff, nothing) | |

The names are labels for the fallback table, not guarantees: two sessions of the same runtime can differ (a sandbox
with network off, a chat with a web tool switched on), which is why the probes decide and the name only describes.
The list matches `probe_runtime.py`'s `RUNTIMES`; a household on another vendor's agent runs as `other` with the
product named in `variant` (vendor names belong in `adapters/agents/` and `FALLBACKS.md`, `README.md` rule 1).

## The probes

Each probe is local, cheap, and sends nothing to anyone. "Yes" needs the evidence in the last column; anything else,
including an error or a permission prompt that is refused, is "no". `unknown` is allowed only where the table says.

| Key | Probe | Yes when |
|---|---|---|
| `shell` | run `echo ok` | it prints `ok` |
| `read_files` | read `AGENTS.md` | its first line comes back |
| `write_files` | write the date into `house/.probe`, read it back, delete it (the path is git-ignored) | the round trip works and the file is gone |
| `git_push` | `git push --dry-run --no-verify origin HEAD` (pushes nothing, so skipping the pre-push hook loses no protection; a new branch with no upstream and an already-pushed branch both pass) | it exits 0, "Everything up-to-date" included; a branch behind `origin` (rejected as non-fast-forward) is `yes` too: the remote was reached, fetch before pushing; a detached HEAD, no `origin` remote or an authentication error is `no`, with the reason |
| `web` | fetch `https://version.home-assistant.io/stable.json` (small, public, says nothing about the house) | a JSON body comes back |
| `schedule` | look for a tool that creates a scheduled or recurring task, or a cron or timer on this machine you may edit | such a tool or file is present |
| `subagents` | look for a tool that starts another agent with its own tool list | such a tool is present |
| `long_context` | your context window, if the runtime states it or you know it | 100k tokens or more; `unknown` if you cannot say |
| `persistent_memory` | a memory the runtime keeps between sessions that you can read now | you read something you did not write this session; `unknown` if you cannot tell |
| `box_access` | Confirm the box with the owner (`install/agent-access.md` section 2), then use the reader in section 3. It checks the saved address before loading the private token. | A successful read returns counts only. With no profile yet, record `unknown`: "no profile yet; the owner confirms the box in install/agent-access.md section 2". Inside an app, the check is the owner's confirmation only. |
| `notify_owner` | look for a tool that pushes a message to the owner's phone or inbox | such a tool is present (never send to find out) |

The one-line report in step d is the only thing the person needs to see; the probe outputs stay in the session.

## When Step 0 runs again

- The entry for your runtime is over 7 days old.
- The runtime you observe is not the one in the entry (a new entry, not an overwrite: a household may use two).
- The same runtime name runs in more than one place (a terminal agent on a laptop and on the box differ in
  `box_access` and `schedule`): key each entry by name and place, `claude-code/box`, `claude-code/laptop` (the script's
  `--place box`), so neither session rewrites the other's entry on every run. Two vendors both named `other` need a
  `--place` each too: the vendor in `variant` is not part of the key.
- At the start of every unattended run (the probes take seconds; rewrite the entry only if a value changed, so the
  repository does not get a commit per run).
- A probe disagrees with the entry in the middle of a session (a push fails, a tool is gone): fix the entry then,
  and say so in one line.

## A chat app before the box has an agent

A chat app on any device (`claude-app`, or `other` with the product in `variant`) guiding the first evening
(`00-start-here/from-a-chat-app.md`) records nothing: there is no `house/` yet and nowhere to write it. It says in one
line that it has no shell, no files and no box, that every step is the owner's, and that the evening ends with the
hand-off note; its limits and fallbacks are in `adapters/agents/chat-apps.md`. The agent on the box runs Step 0 in
full when it starts.

## Pairs that cannot work (stop at step e)

| You are | And you lack | Then |
|---|---|---|
| an unattended run | `write_files` | you can only report: send the report through `notify_owner` when that is `yes`; otherwise your reply is the only record and the scheduler's own run history is where the person finds it. Write nothing, say what you found, stop |
| an unattended run | `git_push`, and nothing hands your work back (no pull request or diff returned by the platform: `variant` names a hand-back when there is one, `FALLBACKS.md` git row) | your work has nowhere to go; stop at the gate and say the lane needs a scheduler that can push or a manual lane (`FALLBACKS.md`, schedule) |
| a run that must change the box | `box_access`, with nobody in the session | write the change package (the exact edits, the check, the undo) where the brief says and stop; a person deploys |
| any run asked to simulate people against the live house | `subagents` with read-only tools | never against the live house; an isolated copy only (`adapters/agents/other-agents.md`) |

## What Step 0 never does

Sends anything to anyone; prints a token, a password, the box's address, the remote's address or the GitHub account; writes outside `house/.probe` and `house/runtime.yaml`; fetches
the box as its web probe (that is the box probe, and only through `HA_URL` or the Supervisor's proxy); fills a value it could not observe.
