# Start here (for the person)

*Status: rewritten for the two ways in (KIT-START0, 2026-10-27; was O2, 2026-10-13); the KIT-START0r findings
enacted (KIT-START0.f, 2026-10-28); the third way in, an existing house (KIT-EXIST.a, 2026-10-31); installed but
not onboarded, models and cost (KIT-DRY.f6, 2026-11-10). Seven short
pages, written for you, not for the agent. The full rewrite around the levels is a later item (KIT-START).*

Older guides call Home Assistant apps add-ons.

## Which way are you starting?

- **You want to start from a chat app** (on a phone, a tablet or a computer), and no agent runs on the box yet,
  wherever Home Assistant is: nothing yet, a machine to install on, a virtual machine, or already running (even a
  box someone else installed that still shows the welcome screen: the chat walks its onboarding). Take
  **path D** (`from-a-chat-app.md`): the chat app asks what you have, walks the first evening with you, and ends by
  handing over to the agent on the box, which then continues at "Already installed" step 2 in `AGENTS.md`. No
  computer is needed unless you are installing onto a bare machine.
- **Home Assistant is not installed yet, and you have a computer.** Take **path A**: the agent runs on your
  computer, walks the install with you, then moves onto the box.
- **Home Assistant is installed but not onboarded** (someone set the box up for you, and its page still shows a
  welcome screen with **Create my smart home**, or asks you to create an account). Take **path A** too, and tell the agent so: it skips the install, asks its questions first,
  and then walks onboarding with you. Do not onboard before it asks.
- **Home Assistant is already installed and onboarded (you made the owner account and named the house), and
  nothing else has been done to it.** Take **path B**: you install the agent as an app and start inside the box.
  Readable on a phone; no computer needed.
- **Home Assistant has been running for a while, with devices, automations and habits of its own.** Take
  **path C** (`existing-house.md`): the agent reads first and changes nothing, a backup comes before the looking,
  nothing of yours is renamed, and the kit's rules apply to new work only.

All three paths end at the same place: a box you can always find, by its name or its address, with a backup off
it (level 0), and the agent waiting for your first request. Changing settings on your router is optional.

## What this kit is

A set of pages and rules for building and running a Home Assistant house together with an AI agent: an install
walkthrough for the hardware you have, half an hour of questions that become your house's own rulebook, and a way of
working where every change is written down with its undo and nothing reaches a person without your OK. It came out
of a real house; nothing in it is about that house. Every rule and guard rail in it is a default you may change or
drop, and the whole path is an offer: you can stop or skip at any point, or go your own way with your agent, another,
or none. The agent tells you once what a rail protects against, then does what you chose.

## Path B: straight from Home Assistant (four steps, yours alone)

Nothing can guide you until the agent runs on the box, so these steps are the only part of the kit you do by hand.

1. **Onboard Home Assistant.** If already onboarded, confirm the owner account and skip step 1. Otherwise, when
   the welcome screen appears, open the address the install showed you, create the owner account, name the house and
   set its location. Stop there: no devices, no apps, nothing else yet.
2. **Install your runtime's app.** `adapters/agents/<runtime>.md`, "Install on the box and sign in", has the
   steps. The kit's first runtime has the full walk-through; a second has lab notes.
3. **Sign in** as the same section says. The sign-in is stored on the box and travels inside its backups, so from now
   on a backup file is a secret: keep it where you keep passwords.
4. **Say:** `Set me up with the starter kit: <the kit's address>`. From here the agent leads. It first says where it
   is running and what it can do there (below), then asks how the kit should reach it and makes your own private
   copy of it (`getting-the-kit.md`), and the "what next?" helper takes you up level 0. Inside the app it already
   sees the house, so it asks you for no Home Assistant token and installs nothing again (`install/agent-access.md`,
   section 0); it starts at the network-and-backups checklist. When a step sends you out of the chat to type a
   line at the shell, come back the way your runtime resumes a conversation (`adapters/agents/<runtime>.md`, "Resuming
   a session"), not with a fresh start; and once your private copy exists at `/share/<repository name>`, start every
   session with `cd /share/<repository name>` first (`getting-the-kit.md`, part 2, says why).

## Path A: from a computer

1. **Get the kit onto your computer and make it your own private repository.** `getting-the-kit.md`, written for
   someone with no git habits. Ten minutes.
2. **Open your agent in that folder and say: "Read AGENTS.md and start."** It asks about fifteen minutes of
   questions (hardware, network, backups, its own budget), picks the install guide for your hardware, and walks the
   install one step at a time, waiting for "done" after each. You type every password into the box yourself; it
   never asks for one.
3. **Move onto the box.** When the box is set up with a backup off it, the agent walks you through
   installing your runtime's app (path B, steps 2 and 3), and the session on your computer ends with a handover
   note that the app session reads first (`handover.md`). From then on the agent can run on the box, on a
   schedule, and see the house directly; each box session starts with `cd /share/<repository name>` and then your
   runtime's start command (`handover.md` says why).

## Path C: an existing house

`existing-house.md`, start to finish. In short: the app as in path B's steps 2 and 3; one backup downloaded
and opened by you; then `Set me up with the starter kit on my existing house: <the kit's address>`, and "lived-in"
to the one question the agent asks. The first session is read-only: an inventory, a first look at health and
risk, and a list of offers you may leave untaken.

## The first thing the agent does: say where it is

Every session opens by finding out what it can do where it is (a shell, files, git push, the web, the box, a
scheduler, a way to reach you), from evidence, and telling you in one line, with what you will have to do by hand
instead. On the box the app already sees Home Assistant; on your computer it may not until a later step. The
answer is written into `house/runtime.yaml` so the next session does not ask again.

The same file names which model fills which role. **Setup is reading and walking a guide, not building:** the
cheapest model that can follow the guide is enough, and the most expensive one is not needed before your first
build. The agent asks you to open your runtime's list of models and read it out, so it knows which ones you have;
then it says which to pick, how to switch and how to check the switch worked (`adapters/agents/<runtime>.md`,
"Changing the model"). **Does a bigger model cost more?** On a monthly plan, no extra money: it uses up the plan's
allowance faster. With a pay-as-you-go API key, yes, per use. Anything the house itself needs (a sensor, a backup
drive, Home Assistant Cloud) is a separate budget line, never taken out of the AI plan.

## Levels 0 to 2, and "what next?"

The kit is a ladder (`levels.md`). The first three levels are where everyone starts:

- **Level 0, a working house.** Installed, reachable by a stable name or address, multi-factor login, daily backups with one copy off
  the box, the emergency kit somewhere that is not this folder. Both paths above end here.
- **Level 1, the repo and the habit.** Every change in your private repository with its undo written down, a guard
  that keeps secrets out, your house profile from the Phase 1 questions.
- **Level 2, one board, one session.** The work on a board with sizes and statuses; one assistant session at a time.

Each level has a short test that says it is working. You climb by asking **"what next"**: the helper
(`tools/what-next/WHAT-NEXT.md`) runs the tests, tells you where you stand, and suggests one to three small steps,
each with how long it takes, what it costs and how to undo it. It turns nothing on by itself. Most households
should stop at level 3 or 4; `levels.md` says why.

Optional, before the agent builds: [make your first automation with it coaching](your-first-automation.md).

## The pages

1. `what-you-need.md` - the things to have before you start, and the ones you do not need.
2. `getting-the-kit.md` - how the kit reaches the agent (a public address, a private repository and a read-only
   token, or files already on the box) and how to make your own private repository from it.
3. `choices.md` - the decisions the agent will ask you about, with the trade-offs in plain words and a default
   for each. Nothing here is final; every one can change later.
4. `what-to-expect.md` - how the agent works with you: the three phases, what it asks before doing, what it
   will never do, what it will ask you to do yourself, and what the first month looks like.
5. `handover.md` - path A only: moving the agent from your computer onto the box, and the note that goes with it.
6. `existing-house.md` - path C only: what happens when the kit is adopted on a house that is already running,
   and the four steps you do by hand.
7. `from-a-chat-app.md` - path D only: the first evening from a chat app, on any device, to the hand-off.
   `chat-app-starter.md` is the same evening as one file, for a chat app that cannot open web addresses.
8. `levels.md` - the ladder: eight levels from "a working house" to "the agent acts" (levels 5 to 7 not in v1.0), three
   side tracks, and the test that says you are ready for the next one.

Ten minutes for the first four. Then path B step 4, path A step 2, or path C's four steps.
