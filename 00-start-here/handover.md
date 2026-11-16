# From your computer to the box: the handover

*Status: written (KIT-START0, 2026-10-27); the KIT-START0r findings enacted (KIT-START0.f, 2026-10-28). Path A
only: the agent began on your computer and now moves onto the box as its app. The app's own access to the box is `install/agent-access.md`, section 0.*

## When

All three, in this order:

1. The "Done when" list in `install/network-and-backups-first.md` passes: a stable name or address, multi-factor login, daily
   backups with one copy off the box.
2. The app is installed, started and signed in (`adapters/agents/<runtime>.md`, "Install on the box and sign in"). The agent on
   your computer walks you through it; you type the sign-in code into the app's terminal, never into the chat.
3. Your private repository is cloned on the box, at `/share/<repository name>` (`getting-the-kit.md`, part 2):
   the agent gives you the line to type in the app's terminal. From then on, every box session starts with
   `cd /share/<repository name>` and then your runtime's start command (`adapters/agents/<runtime>.md`, "Resuming a session"): the app opens
   in the configuration folder unless its `working_directory` setting says otherwise, and there it finds neither
   `AGENTS.md` nor the note below. Setting `working_directory` to `/share/<repository name>` once (the app's
   Configuration tab) is the alternative; `adapters/agents/<runtime>.md`, "Access on the box", lists it as a choice to record.

## What moves, and what does not

| Thing | Moves how |
|---|---|
| Your household repository | Nothing to copy. The computer session commits and pushes everything as its last act; the box clones it from your git host. |
| `house/profile.yaml` | Inside the repository. |
| `house/runtime.yaml` | Inside the repository. The box session adds its own entry beside the computer's (`<runtime>/box` next to `<runtime>/laptop`); neither overwrites the other, and both may be used later, one session at a time. |
| The handover note | `house/docs/handover.md`, written by the computer session, read first by the box session (below). |
| Secrets | **Nothing moves.** A token or address the computer's session used stays on the computer, or is revoked there. The box session already reads the box from inside the app (`install/agent-access.md`, section 0) and asks before anything more. |
| The emergency kit, the backup password | Stay where you keep passwords. Not in the repository, not on the box. |

## The handover note

The last thing the computer session writes, the first thing the box session reads (`AGENTS.md` says so). It lives
in the repository at `house/docs/handover.md` and stays there as a record; the box session appends one line when it
has read it. Plain words, no values of anything secret, named by key only.

```markdown
# Handover: computer -> box

Written: <date> by <runtime, place>          (from house/runtime.yaml)

## Done
- Install guide: <which>, walked to step <n> of <n>.
- Done-when list (install/network-and-backups-first.md): <every line, checked by whom, on what date>.
- App installed and signed in: <date>.
- Repository cloned on the box at /share/<name>: <date>.

## Still open
- <anything from the Done-when list that is not checked, and why>
- <any question the person has not answered yet>

## Where secrets are named (keys only, never values)
- <secrets.yaml keys that exist, the emergency kit's place, the computer-side token and whether it was revoked>

## First thing to do on the box
- <one line: usually "run STEP 0, then what next">
```

The template ends there. The box session, when it has read the note, appends one more line below it,
`Read on: <date> by <runtime, place>`, and commits; a note that already carries a filled `Read on:` line is never
read again. So the computer session must not write that line itself: a note with it is a note the box skips.

## After the handover

The box session opens like every session: STEP 0 (where am I), then the note, then the phase table in `AGENTS.md`.
The computer session may keep being used for things the box cannot do well (reading a long page back to you, a
second opinion), but the rule from level 2 holds: one session works at a time, and the one that changes something
is the one that writes the changelog line.
