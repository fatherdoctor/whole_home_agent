# Changelog

*The kit's own changes, newest first. A house that adopts the kit keeps its own log in `house/docs/CHANGELOG.md`
(from `templates/docs/CHANGELOG.md`).*

## 2026-11-16 - clarify first-evening controls and backup records

- Use the documented Connectivity path for Matter in the voice guide and radio adapter.
- Check Assist's default exposure before a plug add, with the owner's choice and an undo.
- Explain that the Cloud Alexa link works with Remote access off, with official documentation links.
- Separate a confirmed Cloud backup, a downloaded file and archive or restore proof in the note.
- Put the iPad emergency-kit steps before the first backup and explain the copy icon's clipboard behavior.
- Keep a later owner goal for after setup and correct the System and password-dialog labels.
- Drop the unsupported subscription claim, name the backup check consistently and align the community-store wording.
- Rebuild the starter. No live system or account changes are part of this text change.
- Undo: restore the previous guide text and rebuild the starter.

## 2026-11-16 - preserve the old Cloud backup before backup setup

- Put the Cloud account check and confirmed download before the backup wizard, locations and first backup, including on a fresh install.
- Repeat that requirement before the direct Cloud route enables its location.
- Make both Jumping ahead references name the Cloud-copy check before the numbered backup and update steps.
- Distinguish the wanted old Cloud copy from an off-box copy of the new local backup, and rebuild the starter.

## 2026-11-16 - a path from existing Alexa plugs to scene scripts

- Connect the adoption page, plug migration guide and first automation lesson.
- Add a pilot and small-batch checklist for Wi-Fi plugs, with original Alexa routines kept and tested.
- Check Alexa's automatic exposure preference and actual exposed list before the first plug add, then check
  both lists and original routines after each add. Clarify route choices and the separate Cloud and exposure pages.
- Check for an Alexa YAML filter before any plug add; pause when the UI cannot restrict effective exposure.
- Open the Alexa-only exposure view from the Amazon Alexa card before adding a new scene script.
- Match the dialog title and subtitle to the screen, and verify the subtitle names Alexa only.
- Keep the exposure-preference undo at the shared route level, with the owner's saved setting and explicit choice.
- Use one pilot exception, with saved routines, an agreed interruption and complete restoration checks.
- Walk through a safe lamp script, narrow Cloud exposure, a custom Alexa phrase, tests and undo.
- Explain why a direct script call skips an automation's conditions and why stopping a script does not reverse its actions.
- Rebuild the single-file chat starter from its sources. No device or account changes are part of this documentation change.

## 2026-11-14 - best practice by default, the owner's informed choice (KIT-OWNER-CHOICE)

- `install/network-and-backups-first.md` gains "The owner's choice": six practices (encrypted backups, where the
  off-box copy lives, the emergency kit's two places, two-step login, the remote access route, the router's role),
  the weaker way that still works, and the one sentence of risk to say once. The hard stops that remain are listed
  with their reason (a secret in chat or the repository, two-step login left half on, a changed backup key, a
  message to someone who has not agreed, locks or alarm exposed to a voice assistant).
- The hand-off note has an `Owner's choices:` line; `AGENTS.md` reads it with `Skipped steps:`; the principle is a
  short section in `principles/safety-and-security.md`. The starter file is rebuilt. Undo: revert this change.

## 2026-11-10 - step one everywhere: where am I, and what can I reach (KIT-STEP0)

- Step 0 now also finds out where it runs and behaves for that place: a plain chat (no shell: says so, records
  nothing, asks only what it must), a cloud session (a fresh clone, no box: no box actions, the owner gets the
  steps), the box itself (path B: skip the install steps, read the box once the owner has confirmed it), or a
  computer with a shell. `templates/runtime/STEP-0.md`, "Where you are", has the table; `AGENTS.md` Step 0 says it
  in one paragraph.
- `templates/runtime/probe_runtime.py` gains `where` (box | cloud | computer, from evidence; `--where` overrides)
  and a read-only GitHub check, `github` (push | read-only | no-reach | none): git present, a repository with an
  `origin`, a credential set up (named by kind only), `git ls-remote`, and the existing push dry run. It never prints
  a token, the account or the remote's address, only "GitHub" or "a git server". Both are recorded in
  `house/runtime.yaml` (template updated; an older entry without them is probed on the next run, `--if-stale`
  included), and the script ends with two plain lines for the owner. Without a push, the second line says where the
  house folder lives from here: on the box, local and in the box's backups; on a computer, on that computer only; in
  a cloud session, nowhere once it ends, so the owner is handed the files or the diff first. The script knows one
  cloud vendor's marker; in another vendor's cloud container the agent passes `--where cloud`.
- Tests: 38 new cases in `templates/tests/test_templates.py` with fake environments for each place and scratch
  repositories for each GitHub state.
- Undo: revert this commit; a `where:` or `github:` line left in `house/runtime.yaml` is kept as a hand-added key.

## 2026-11-10 - a generic chat-app start, and the second dry run's fixes (KIT-CHAT0.g)

- `00-start-here/from-a-chat-app.md` rewritten as generic: the chat knows nothing about the person until told (no
  assumed device, hardware, household or plan); it opens with tonight's goal and four questions (the device in use,
  where Home Assistant is, the AI plan and any limit, the time tonight), then picks one of four starts: nothing yet
  (choose hardware), a machine with nothing on it (Green or Yellow, Raspberry Pi, mini PC), a virtual machine on a
  server, or Home Assistant already running anywhere (a handed-over box is a case of this).
- Security: "make the account yours" now reviews signed-in sessions and long-lived tokens (Profile > Security) after
  the password change, which does not sign other devices out; the false "the old one is now useless" is gone;
  others who used the owner login get their own login first (with the route to make one).
- Also from KIT-DRY.s2: the plan answer and how tonight ends are said up front; Home Assistant Cloud leaves an
  existing Alexa or Google setup alone (link to `install/voice-assistants.md`) and its sign-in turns remote access
  on (two-step login first; how to keep backups only); a hardware and virtual-machine check; time estimates and a
  safe pause point once a copy is off the box; two-step login fixes (setup key saved first, a one-device route, QR
  and key are secrets, a refused code, a fresh sign-in check); rule 3's keep-out list; devices named by role; more
  hand-off note lines; port 80 explained; the unsourced marketplace claim removed.
- `install/network-and-backups-first.md` agrees with the chat page: the Share folder is included in backups (the
  house folder lives there), with the Cloud 5 GB limit; Cloud sign-in turns remote access on.
- `adapters/agents/chat-apps.md`: generic, ChatGPT's STEP-0 name, which Phase 0 questions the chat asks, the plan
  question up front. README and `00-start-here/README.md` chat entry lines made generic.
- The starter file now also carries `install/raspberry-pi.md` and `install/proxmox-vm.md` (twelve parts, about
  120,000 characters); its test looks for the new start and the account review.
- Undo: revert this commit, then rebuild the starter (`python3 tools/chat-starter/build_starter.py`).

## 2026-11-10 - the chat starter file carries the voice and first-automation pages, and CI catches a stale one (KIT-STARTER-REGEN)

- `tools/chat-starter/build_starter.py` adds `install/voice-assistants.md` and `00-start-here/your-first-automation.md`;
  the starter file is rebuilt (about 91,000 characters, ten parts).
- A workflow, `.github/workflows/starter-check.yml`, runs `build_starter.py --check` and its tests on every pull
  request and push to main, so a change to a source without a rebuild fails.
- `AGENTS.md` path C step 3: from a computer, the inventory runs only after `install/agent-access.md` section 2 has
  confirmed the box (the export and first look refuse an unconfirmed box).
- Undo: remove the two lines from `SOURCES` and rebuild; delete the workflow file; restore the step 3 sentence.

## 2026-11-10 - adapter lines and small fixes from the review of the dry-run fixes (KIT-DRY.f6f)

- `adapters/agents/claude-code.md`: `/model <name>` also becomes the default for new sessions; how to switch for
  this session only. The secrets deny list also stops `cat`, `head`, `tail`, `sed`, `tee` and redirections on those
  paths, not `grep -r` or a script; a token file is read by the kit's reader, never by a shell `cat`. Inside the
  box, the read check waits for the owner's confirmation of the box in the profile.
- `AGENTS.md`: the first phase row no longer rests on `box_access: yes` with no profile (a session with no profile
  records `unknown` and goes by what it sees inside the box or what the person says); the installed-but-not-
  onboarded row rests on what the person says; Phase 0's goal is "reachable at a stable name or address"; Phase 0
  and 0E close name the request recorded in Phase 0.
- `templates/runtime/runtime.yaml`: the `box_access` comment matches the check. `interview/profile-template.yaml`:
  `first_request` may be set in Phase 0. `templates/tests/test_templates.py`: the deny-list case checks the three
  token-file rules.
- Undo: revert this commit.

## 2026-11-10 - starting from a chat app on a tablet (KIT-CHAT0)

- `00-start-here/from-a-chat-app.md`: path D, the first evening from a tablet and a chat app, for three starts (a
  box a helper set up and handed over, no hardware yet, a bare mini PC that needs a computer once); onboarding from
  the tablet; the owner account made the owner's own with two-step login; Wi-Fi as normal; updates and backups with
  Home Assistant Cloud first; the hand-off note to the agent on the box; git optional at first.
- `00-start-here/chat-app-starter.md`, built by `tools/chat-starter/build_starter.py` (test beside it): the same
  evening and every guide it names, as one file to attach when a chat app cannot open the kit's address.
- `adapters/agents/chat-apps.md`: what a chat app can and cannot do during setup, and which agent the hand-off
  installs. `README.md`: a first-screen pointer for a chat assistant handed the address.
- `AGENTS.md`: "Arriving from a chat app" (save and check the hand-off note, no code host until the owner wants one,
  never install the community store), and Phase 2 offers the owner a first automation built by hand before the
  first build. `templates/runtime/STEP-0.md` and `FALLBACKS.md`: the chat-app runtime and its `(setup)` row.
- Review fixes: the Claude Code sign-in is named as a terminal step with a computer as the fallback; Settings >
  Apps leads (Add-ons before 2026.2); no two-step "recovery codes" (keep the authenticator's setup key); the
  router reservation in the embedded install guides is skipped unless the owner chose the router; the setup gate
  reads as its goal on a tablet; the Cloud price lives in the interview only; a ChatGPT-plan owner's evening ends
  at the hand-off note until the Codex install is walked; the note carries the agent budget.
- Second review fixes: "Where to start, and when to move to the box" (a plain chat needs no GitHub; a cloud coding
  agent needs GitHub and a private copy and still cannot reach the box; the agent's app on the box needs neither),
  the note's Git line can name a private copy made for a cloud session and `AGENTS.md` "Arriving from a chat app"
  step 4 says what to do with it; "Every start" backs up and copies off the box before any update; the address
  without `:8123` first; "app" for the agents in the new lines; the README's first lines are the chat entry and
  name every way in; `build_starter.py` reports characters and bytes. Starter rebuilt on main.

## 2026-11-10 - the owner can change or drop any guard rail (KIT-OWNER)

- `AGENTS.md`: "The kit serves the owner" near the top: every guard rail (the push guard, the secrets deny list,
  ask-first, the phase gates, the levels, the board, the CHANGELOG habit, the agent's own secrets conduct) is a
  default the owner may change or drop, and the path is an offer. On the owner's ask the agent warns once, scaled to
  the ask, offers one lighter option, does it, records it with an undo, and keeps helping; it never refuses.
- `00-start-here/README.md`, `00-start-here/levels.md`, `templates/guard/README.md`: one line each saying so; the
  needs-first rule is what the helper suggests, not a lock on the owner.
- `adoption.opted_out` in the profile (`interview/profile-template.yaml`, the levels block): what was dropped, when,
  why, the undo and the checks it turns off. `tools/what-next/what_next.py` reports it and leaves those checks out
  of the standing failures, so the helper never suggests restoring a dropped rail; `WHAT-NEXT.md` gives the words.
- Review fixes: the owner's choice outranks the principles too (a `[core]` principle is the strongest default, not
  a lock); the yield covers "must" and "do not" as well as "never" and "always"; one phrase for the record
  (`adoption.opted_out` or the rail's own setting) in `AGENTS.md`, `levels.md` and the guard README.
- Undo: revert this pull request.

## 2026-11-10 - fixes from a stand-in newcomer dry run: AGENTS.md and the Claude adapter (KIT-DRY.f6)

- `AGENTS.md`: Phase 0 allows one unfinished "Done when" line on every path, accepted by the owner in writing in
  the first CHANGELOG entry (level 0 stays unpassed until it is done); a phase row for a box installed but not
  onboarded; where mid-guide progress lives (comment lines in `setup:`); a build request during Phase 0 recorded
  word for word in `profile.first_request`, so the Phase 1 and Phase 2 rows now key on `profile.generated_on`;
  `house/docs/gotchas.md` created at the first Phase 0 lesson; `model_roles` filled from the runtime's own model
  list; the setup-note check marked box-side; two new standing rules (goal first, then the route, the owner picks
  the route; one-line batched asks for harmless, one-click-undo changes); a fallback when the official page cannot
  be read; the git identity pointer; the two attribution rules merged; the status line shortened.
- `adapters/agents/claude-code.md`: "Changing the model" (see the list, switch, confirm with `/status`, a model per
  role, cost); a Home Assistant token kept in a file outside the repository, and where; the setup note is box-side.
- `templates/runtime/claude-code-settings.json`: denies reads of `ha_token*` files anywhere and of
  `~/.config/home-assistant/`.
- `principles/budget-and-pacing.md` rule 10: plain cost answers (monthly plan vs API key) and a separate hardware
  and services budget line. One failure mode and one check.
- `00-start-here/README.md`: the installed-but-not-onboarded way in; a router change is optional; models and cost
  in plain words. `00-start-here/getting-the-kit.md`: a repository and a commit in plain words; set the git name
  and email per repository. `templates/docs/gotchas.md`: its header says Phase 0 may create it.
- Undo: revert this commit.

## 2026-11-07 - wiki process, backup size management, attribution (KIT-SYNC-1107)

- `principles/documentation.md`: rules 10-12 - the wiki as one small file per page with content-named assets,
  picture files, a search index and a per-file version check; archived manuals extracted to text and pictures the
  writers can read; page rules (lessons optional, cited Maintenance, look before listing a gap, a layout pass never
  verifies, physical vs digital pages, emergency help on one landing page). Three failure modes and their checks.
- `principles/board-and-lanes.md` rule 24: the merge owner may be a model-free job that merges only a reviewed PR
  carrying a merge token, at the reviewed commit, once its condition is met, and checks the merged diff. The
  install this comes from has built that job and not yet run it (its workflow waits for the owner's go), so this is
  a design that passed review, not a measured result. One failure mode and one check.
- `principles/backups-and-recovery.md`: rules 10-12 - each destination's cap, re-downloadable copies out of the
  backed-up folders, a size warning under the cap, a failed upload to any destination is a health fault. One
  failure mode and its checks.
- `principles/working-with-the-agent.md` rule 14: the tool's default session link, overridden by a repo-root
  `CLAUDE.md` and caught by a CI check.
- `AGENTS.md` "Your standing rules": the attribution and shallow-clone lines (`CLAUDE.md` stays a pointer to
  `AGENTS.md`). `principles/00-index.md`: summaries updated.
- Undo: revert this commit.
