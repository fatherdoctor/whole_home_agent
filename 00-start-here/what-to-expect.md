# What to expect

*Status: written (O2, 2026-10-13); the ladder and the points scale updated (KIT-LEVELS, 2026-10-26); the existing-house
paragraph (KIT-EXIST.a, 2026-10-31).*

## Three phases
1. **Setup** (one sitting, about two hours). The agent asks about fifteen minutes of questions (hardware, network,
   backups, its own budget), then walks you through installing Home Assistant one step at a time, waiting for
   "done" after each. It ends when the box is reachable by a stable name or address, backed up, with a copy off the
   box. Router changes are optional. The agent never asks you for a password; you type those into the box yourself. If Home Assistant is
   already installed and onboarded when the agent arrives (the app way in, `README.md`), the install steps are
   marked done from what it can see and the sitting is shorter.
   **If the house is one you have lived with** (path C, `existing-house.md`), setup is adoption: the first session
   is read-only, after a backup you download and open. The agent writes an inventory of what exists and a first
   look at what is wrong or risky, each line an offer you may leave; it asks only what the box cannot tell it; and
   nothing of yours is renamed, moved or rewritten to fit the kit. Where your way and a kit rule differ, your way
   stands, written down once. The old is a tidy-up list you may never take; the kit's rules apply to new work from
   that day. The interview at your first request is shorter, pre-filled from what the box already said.
2. **The house profile** (half an hour, at your first request). When you first ask for something ("make the porch
   light come on at dusk"), the agent does not build it yet. It asks about the people in the house, the rooms,
   what is dangerous, what must never break, when the house sleeps, who should be told what, what voice may touch,
   and what it may do by itself. Then it writes your house's own rulebook from the answers: a naming scheme, a
   policy page, a notifications page, a health-check plan, an operations page, a manual skeleton, a backlog with
   your request at the top. You can stop after any topic and finish later.
3. **Building** (the rest). One item at a time, always in the same loop: the agent plans (what changes, how long,
   what could go wrong, how it will be tested), you say go, it builds, tests without sending or sounding
   anything, records what it did and how to undo it, and reports what ran and what failed.

## What it asks before doing
Anything hard to undo: deleting, restarting, firmware, version changes. Anything on your safety list (locks,
alarm, garage, water, heating, cameras). Anything that reaches a person. A new item that is not on the backlog.

## What it will never do
- Send a message to anyone but you without your OK for that message. Never to a child's phone with buttons on
  it. Never "to test"; you send the first test of every new message.
- Change a code or a contact, or touch anything you have put on the never list.
- Store a code, a password, a token, a phone number or an address in this folder, or quote one back to you.
- Build anything from a session that cannot see the box; such a session writes a design and a draft, nothing live.
- Claim something works that it has not seen work. Failed tests are reported word for word.

You can choose [optional guard rails](../templates/agent-guard-rails.md) for locks and alarms, including putting
them on your never list. Your safety list and the requirement to ask before hard-to-undo actions still apply.

## What you will do yourself
- Type logins and passwords into the box, your phone and your voice assistant.
  Keep the backup encryption key and the authenticator setup key in your private emergency kit.
- Plug things in, press pairing buttons, read what a screen says.
- Send the first test of every message, and say what arrived.
- Say go, or not, on each item; answer the questions the agent writes into the backlog.
- Keep the emergency kit somewhere that is not this folder.

## How changes are recorded
Every change gets a dated entry in your CHANGELOG with how to undo it. Every lesson gets a line in your gotchas
file. Everything that changes what a person in the house sees gets a note for the manual. Work waits on a backlog
with sizes (points: one point is 0.1 % of your weekly assistant allowance, the scale the board uses), and nothing is
built that is not on it.

## How far to take it
The kit is a ladder (`levels.md`): level 0 is a working, backed-up house; level 1 puts every change in a private
repository with its undo; level 2 puts the work on a board; level 3 adds health counts, a weekly update review and a
digest; level 4 a monitoring agent that reports and never acts. Levels 5 to 7 are a planner, builder lanes that work
unattended, and an agent that fixes small things at night; they are not in v1.0 (`levels.md`, "Not in v1.0").
**Most households should stop at level 3 or 4.** Each level has a test that says it is working before the next is
offered, and the agent suggests the next step only when you ask "what next"; nothing is turned on that you did not
choose.

## The first month
Week one: the install, the profile, your first item, the notification router, the first health check, a backup
restore drill. Then one or two items a week at the pace you set. Before a trip, a freeze: nothing changes but
fixes, and the agent keeps a bigger reserve. After a month you will have a house that tells you when something is
wrong, a manual a sitter can follow, and a folder that records every decision and how to reverse it.
