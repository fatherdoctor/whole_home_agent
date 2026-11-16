# Chat apps (setup and later evenings by hand)

*Status: notes (KIT-CHAT0, 2026-11-10; generic and corrected after its first dry run, KIT-CHAT0.g). For
`00-start-here/from-a-chat-app.md`: a general chat assistant app on any phone, tablet or computer (ChatGPT, the
Claude app, or another) guiding the owner through setup before any agent runs on the box. Walked once, in a
stand-in dry run (KIT-DRY.s2, 2026-11-10: a plain chat opened the README, then that page and this one, three pages
in one turn). Which real apps open a pasted address, and how many pages, is still to be tested app by app; the
table below is what the kit expects.*

## What it is for, and what it is not

A chat app guides the first evening: opening questions, choosing a start, installing or reading what is there,
onboarding, the owner account, backups, updates and the hand-off. Without an agent on the box it may keep guiding
later evenings using the kit's own device and first-automation guides. **The chat cannot see or change the box;
the owner performs every step.** It cannot run a command or keep house files. Its return path and owner-kept
progress-note format are in
[Coming back without an agent on the box](../../00-start-here/from-a-chat-app.md#coming-back-without-an-agent-on-the-box).
Once the owner hands off, the agent on the box (`claude-code.md` or `codex.md`) leads.

STEP 0 on this runtime is short, and there is nothing to write: the chat records nothing on the box. In the
`templates/runtime/STEP-0.md` names it is `claude-app` (the Claude app) or `other` with the product in `variant`:
ChatGPT is `other` with `variant: chatgpt`, and any other chat app is `other` with its own name. Its capabilities,
in the `can:` keys:

| Key | Value | So the kit does |
|---|---|---|
| `shell`, `write_files`, `git_push` | no | Every step is the owner's, on their own device; the chat drafts hand-off and progress notes, which the owner saves |
| `box_access` | no | The owner reads the screen back, or sends a screenshot |
| `read_files` | partly | Some apps open a pasted repository address and one or two pages; others open nothing. The fallback is `00-start-here/chat-app-starter.md`, one attached file |
| `web` | often | Used for the official Home Assistant documentation when a screen differs; "not read" when it cannot |
| `persistent_memory` | no | The owner pastes the saved notes into a new chat or the later agent on the box |
| `schedule`, `subagents`, `notify_owner` | no | Not needed for setup |

## Getting the kit into the chat

1. **Paste the kit's address** and ask: *"Set up Home Assistant using this."* The first lines of the kit's
   `README.md` tell a chat assistant to open `00-start-here/from-a-chat-app.md`, with that page's plain-text (raw)
   address in the link. If the app opens it, that page carries the whole evening.
2. **If the app cannot open the address** (it says so, or it answers from general knowledge without quoting the
   page), download `00-start-here/chat-app-starter.md` from the kit and attach it to the chat with
   *"Follow this file."* It is built from the kit by `tools/chat-starter/build_starter.py` and holds the page,
   this one, the Phase 0 questions, the install guides for every start (Green, Raspberry Pi, mini PC, a Proxmox
   virtual machine), network and backups, voice assistants, the first automation, and the agents' install
   sections.
3. **Screenshots work in both.** When a step says "read what is there", a screenshot is usually faster than typing.
   Crop out anything secret before sending it: the full list is rule 3 of `from-a-chat-app.md` (passwords, codes,
   the two-step login QR code and setup key, the backup key, tokens, the remote address).

## Which Phase 0 questions the chat asks

Only the page's four opening questions (the device in use, where Home Assistant is, the AI plan and any monthly
limit, the time tonight), and the two its steps need when they come up: whether the owner will log in to the router
(default no), and the Home Assistant Cloud budget if they want it. The rest of the Phase 0 interview (time zone,
radios and devices, voice, the house's first request) belongs to the agent on the box, which reads the hand-off note
first and does not ask again what the note answers. The note records "not asked" for what the chat did not ask.

## Which agent the hand-off installs

Whichever assistant subscription the owner already has, so the evening adds no new bill. The chat asks which in
the opening, so the owner knows from the start how tonight ends:
- a Claude subscription: the Claude Code app (`claude-code.md`, "Install on the box and sign in"; the kit's
  first runtime, walked end to end);
- a ChatGPT plan that includes Codex (OpenAI has included Codex in its paid ChatGPT plans, Plus and above,
  since 2025; plans change, so check OpenAI's current plan page): the Codex app (`codex.md`). It has lab notes
  only, no walked install, so for now the first evening ends at the hand-off note, written and kept for later, or continues hand-guided; say so in the
  opening. They can return for hand-guided work without buying another plan; offer the first runtime only if
  they want to add a Claude subscription (`from-a-chat-app.md`, "The hand-off");
- another plan, or none: keep the note too, with nothing to buy; the hand-guided return path remains available.

The chat app and the agent on the box do not need to come from the same vendor.

## How this goes wrong

- **The chat assumes what it was not told** (a tablet, a box someone handed over, a family helper, a particular
  plan). It asks the page's opening questions and follows the answers; a step that names a device or a person the
  owner never mentioned is a fault: the owner says so and the chat corrects course.
- **The chat answers from memory instead of the page.** Ask it to quote the step it is on; if it cannot, attach the
  starter file.
- **A password or a code goes into the chat.** The chat says so and the owner changes it in Home Assistant. A chat
  transcript is saved and searchable.
- **The chat claims it built or checked something on the box.** Coaching an owner through a device plan or
  automation is allowed; the owner approves, clicks and reports each result. Claiming to have deployed, run a
  test, seen live state or saved house files is a fault. Read the kit guide first, preserve the owner's rules,
  and record owner-observed results and undo in the progress note; unobserved results stay not checked.
- **A screen does not match.** Menus move between releases; the chat follows the screen and says which step
  changed, and the agent on the box notes it in `house/docs/gotchas.md` so the guide can be corrected.
