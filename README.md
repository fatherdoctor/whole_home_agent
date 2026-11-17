# Whole Home Agent

**Chat assistant handed this address and asked to set up Home Assistant:** open
[`00-start-here/from-a-chat-app.md`](https://raw.githubusercontent.com/fatherdoctor/whole_home_agent/main/00-start-here/from-a-chat-app.md)
and start; it carries the first evening and a "Coming back without an agent on the box" path.

## Starting from a chat app
**Chat assistant:** the page above is the one way in; its plain-text address is in the link. If you can open
nothing here, ask the person to download `00-start-here/chat-app-starter.md` and attach it: the same evening, with
every guide it needs, in one file.

**Person, starting from a chat app** (ChatGPT, Claude or another, on a phone, a tablet or a computer), whether you
have no hardware yet, a machine to install on, a virtual machine on a server, or Home Assistant already running:
paste this repository's address into the chat and say *"Set up Home Assistant using this."* The chat asks what you
have first. No shell and no GitHub account are needed; a computer only if you are installing onto a bare machine.

**Coming back, still without an agent on the box:** paste the kit address and your saved progress note into a
fresh chat and say *"Continue from this note using the kit."* Open
[Coming back without an agent on the box](00-start-here/from-a-chat-app.md#coming-back-without-an-agent-on-the-box).
The chat cannot see or change the box: it guides one step, you click and report what happened. You can keep
adding devices or learn your first automation this way; you do not need another AI subscription to continue.

Build your first Home Assistant house together with an AI agent, using practices that came from building and running
a real one: an install walkthrough for the hardware you have, a house-profile interview after your first prompt, and
platform-neutral rules for automations, health checks, notifications, naming, documentation, planning, updates,
budget pacing and tier-2 support.

It assumes nothing about your choices. Zigbee, Z-Wave, Matter or Thread; Alexa, Google, Apple or Assist; a Raspberry
Pi, an HA Green, a mini PC or a VM; your coding agent. Pick what you like; the principles stay the same and
the adapters say what changes.

## How to use it
1. Read `00-start-here/README.md` (ten minutes). It asks which way you are starting and sends you to one page: a
   chat app (above), a computer, a box already installed (with or without onboarding), or a house that
   has been running for a while.
2. Make a **private** copy of this repository that you own (`00-start-here/getting-the-kit.md` walks it, for
   someone with no git habits): your `house/` folder (the profile, the CHANGELOG, your house's documents) is
   committed there, never to the kit's own repository. From a computer you do this first; from the agent's app on
   the box the agent does it with you, and after a chat-app start it can wait until you want it.
3. Open your AI agent in that folder and say: **"Read AGENTS.md and start."** (From the agent's app on the box:
   **"Set me up with the starter kit: <the kit's address>"**.) The agent runs **Phase 0** (fifteen minutes of questions, then
   installing Home Assistant one step at a time, or marking that done if it already is) and, at your first request,
   **Phase 1** (half an hour of questions that write your own naming scheme, policies, notification tiers,
   health-check plan, operations page, manual and wiki skeletons, and a backlog with your request at the top).
4. After that you build, one backlog item at a time, with the agent following `principles/`, and climb the levels
   (`00-start-here/levels.md`) by asking "what next".

## Map
| Folder | What is in it |
|---|---|
| `AGENTS.md` | The entry point for any agent: the phases, the agent's own rules, where everything is. |
| `00-start-here/` | For the person: the two ways in, what you need, getting the kit, the choices, what to expect, the handover, the levels. |
| `install/` | Installing Home Assistant on each kind of hardware, network and backups first. |
| `interview/` | Both interview scripts (Phase 0 setup, Phase 1 house profile), the profile schema, and what Phase 1 generates. |
| `principles/` | The rules, each with why and how it goes wrong. Platform-neutral. |
| `adapters/` | What changes per choice: radios, voice assistants, notification channels, agents, hardware. |
| `templates/` | Starting files the interview copies into your house: packages, docs, the tier-2 support agent, pacing tools. |
| `examples/` | A fictional worked example house, end to end. |
| `tools/` | Tools you run from your own repository: the "what next?" helper (`tools/what-next/WHAT-NEXT.md`, levels 0-2 so far). |
| `blueprints/` | Ready-to-import automation blueprints, tested in a real Home Assistant: a battery window keeper and a charger fault watch for a wall tablet on a smart plug, and a beta update notice for testers ([`blueprints/beta-testing.md`](blueprints/beta-testing.md)). |
| `house/` | Your own files, created by the interviews: profile, docs, config mirror, export. Layout in `house/README.md`. |

## Status
Version 1.0 (November 2026). The principles, install guides, the chat-app entry point, the interviews and the
templates are written and tested; the adapter notes for radios, voice and notifications are still notes. Every file
says its status at the top. Some status lines and notes still carry our internal work codes (such as `KIT-DRY.f6`);
they point to a tracker that is not public, and you can ignore them. Nothing in this repository is specific to the
house it came from: no names, addresses, phone numbers, codes or tokens, and none should ever be added.

**v1.0 is tested on one runtime only** (`adapters/agents/claude-code.md`); a second has lab notes (`adapters/agents/codex.md`, v1.1), and `templates/runtime/FALLBACKS.md` says what the kit does without a mechanism. v1.0 supports the ladder to level 4; levels 5 to 7 are written down but not in v1.0 (`00-start-here/levels.md`).

Known issues in v1.0:
- The comment at the top of `templates/packages/health-check.yaml` says every simulated check should show a push. Only fault checks push; a notice check raises the notice count and stays quiet. `00-start-here/levels.md` (`L3-health-fired`) has it right.
- The what-next helper (`tools/what-next/`) checks levels 0 to 2 only. For levels 3 and 4, the agent reads each readiness line in `00-start-here/levels.md` and checks it by hand against the source the table at the end of that page names.
- Voice assistants: before the owner path saves the scene script or adds a native plug, it does not yet check whether an active Alexa YAML filter or Google's new-entity setting would expose it to a voice assistant. Check **Settings > Voice assistants > Expose** yourself after those steps, and turn off anything you did not mean to share.

*It covers the Home Assistant box and, more and more, the whole home around it: the equipment that is not connected, its records, manuals, maintenance and troubleshooting.*

License: MIT, see [`LICENSE`](LICENSE).
