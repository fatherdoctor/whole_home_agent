# Phase 0 - the setup interview

*Status: written (O2, 2026-10-13). Run by the agent before Home Assistant exists. Follow `interview/README.md`,
"How to interview". Writes the `setup:` block of `house/profile.yaml` (schema: `profile-template.yaml`).*

**Purpose.** Decide the four things the install depends on (hardware, network, backups, agent budget), record
what the house already owns so Phase 1 can start from facts, and pick the install guide. Fifteen minutes. The
person does not need to know anything about Home Assistant yet; `00-start-here/` is written for them and you may
point at it, one section at a time, never as homework.

## Jumping ahead (Phase 0)

When the owner asks to go straight to installing the ChatGPT or Claude app, follow this route before the usual
interview or folder creation. If two-step login is half done, finish it (setup key saved and fresh sign-in
confirmed) or turn it off so it remains off; never leave it half on. It needs a running Home Assistant installation
that supports apps. Starting from nothing, finish the install in "Which start is yours" in
`00-start-here/from-a-chat-app.md` and onboarding first, then return here; if apps are not supported, say the
app cannot be installed yet.

Do only two things first: follow "First change on a box already running" steps 1-3 in
`00-start-here/from-a-chat-app.md`: one local backup, then the first update. An off-box copy is not needed yet.
Do not repeat any step already completed and confirmed; otherwise follow those steps and return here.

Two-step login helps protect the account if someone learns its password. A copy off the box protects the backup if
the box or its storage is lost or fails.
On a box someone else set up, a new password and clearing old sessions and long-lived tokens keep a former helper
out before an agent with full access goes in.

Then use the Claude install in `00-start-here/from-a-chat-app.md`, or, for ChatGPT, say the kit has lab notes only
and point to the app's own documentation at the instructions page where you found the app (its publisher's
site or store page). Do not guess its repository address or sign-in steps. In the hand-off note, record each skipped
step separately as
`skipped at owner's request, <date>`, including two-step login, the off-box copy, a new password, clearing old
sessions and long-lived tokens, and other setup or interview steps if skipped; the on-box agent offers them later.
Do not claim an app or skipped step was completed if it was not.

**Before the first question.** Create `house/` if it is not there, with these folders now: `house/docs/`,
`house/ha/packages/`, `house/ha/custom_templates/`, `house/export/` (the rest of `house/README.md`'s layout is
created when its first file is written; no empty folders), copy
`interview/profile-template.yaml` to `house/profile.yaml`, and read the person's first message for answers it
already holds (many say "I have a Pi and some Hue bulbs"). Record those, say what you took from the message, and
start with the first topic they have not answered.

**Rules stated early apply now.** If the person says "ask before any change" or "only message me", record their
words in `setup.standing_rules` immediately and follow them throughout setup. Keep recipients as roles and omit
private details. At Phase 1 topics 6 and 8, read these rules back and carry them into the notification choices,
`profile.agent` permissions and `house/docs/policies.md`; generating the profile must not reset them. Only the
owner may relax a rule, and the kit's safety limits still apply.

## Topic 1 - where and when

*Why:* every timestamp, schedule and backup window the house will ever have keys on this.

| Ask | Default | Writes |
|---|---|---|
| Which timezone is the house in? | the computer's timezone only if it reports a full IANA name; confirm it | `timezone` (IANA name) |
| Which language should the house's own documents use? | the language of the conversation | `language` |
| Roughly how much time do you have today, and when do you want to stop? | one sitting of two hours | nothing; sets the stop point for the walk-through |

If the computer reports only an abbreviation or a UTC offset, do not turn it into a guessed IANA name. Ask the
person to check the timezone selector on their computer, phone or Home Assistant and confirm the full timezone.
If it is still unclear, ask about UTC offset and daylight-saving changes, offer the matching IANA choices, and
wait for their choice. Leave `timezone: null` until resolved; explain that schedules need this answer.

## Topic 2 - hardware

*Why:* the install guide, the backup tiers that are possible, and how much the house can grow all follow from
this one choice. The trade-offs in plain words are in `00-start-here/choices.md`.

| Ask | Default | Writes |
|---|---|---|
| Do you already have a machine for this, or are you buying one? | - | `setup.hardware` |
| If buying: do you want the box that just works, or one that can grow? | HA Green for "just works"; a small Intel or AMD mini PC for "can grow"; a Raspberry Pi 5 only if they already own one with an SSD (if they bought one new, take the parts row below and go on) | `setup.hardware`, `setup.install_guide` |
| If you already run a server at home (Proxmox, a NAS, a homelab): is Home Assistant going on it as a VM? | yes if Proxmox, with the caveat that the server's own maintenance now touches the house | `setup.hardware: proxmox-vm` |
| What will it boot from? | SSD or NVMe; an SD card is for trying it out only | `setup.storage` |
| Already bought: which parts do you have? (board and its RAM, boot drive and its size, power supply, case and cooling, any USB radio) | - | `setup.hardware_parts` (free text; the install guide's "Before you start" list is checked against it) |

**Check the answer against read-only evidence before selecting the guide.** On a running box, read the hardware
and virtualization type in **Settings > System > Repairs > ⋮ > System information**, or have the person read
it from the console or the VM host's settings. For a machine not installed yet, use its system-information screen
or the person's check of its label. Record the hardware kind and source in `setup.hardware_evidence`, without
serial numbers, network identifiers or addresses. A manufacturer hint alone is not proof of a physical machine
or VM. If the answer and evidence disagree, say what differs and resolve it with the person before choosing a
guide or any disk-writing step. If evidence is unavailable, say "unverifiable" and leave the guide unchosen until
the person can check; never send a VM through a bare-metal installation on a guess. A running installation is
checked from evidence, not reinstalled to fit a guide.

Rules: Home Assistant OS always; Container and Core installs are outside this kit (`install/README.md`). A
Raspberry Pi 4 or older with an SD card: say plainly that it works for a trial and that the card will be the first
thing to fail; record it and go on. Pick the guide from the table in `install/README.md` and write `setup.install_guide`
explicitly: `raspberry-pi` -> `install/raspberry-pi.md`, `ha-green` -> `install/ha-green.md`, `mini-pc` ->
`install/mini-pc-bare-metal.md`, `proxmox-vm` -> `install/proxmox-vm.md`. `other` running Home Assistant OS on a
generic x86 machine takes the mini PC guide; anything else is outside this kit: say so plainly and stop at Phase 0.

## Topic 3 - network

*Why:* a box that changes address breaks every phone, voice assistant and radio bridge that talks to it; a box the
person cannot reach when the internet is down is a box they cannot fix.

| Ask | Default | Writes |
|---|---|---|
| Are you comfortable logging in to the router to reserve the box's address, and do you want to do that? | no; router changes are optional | `setup.network.router_control` |
| Can the box be on a network cable rather than Wi-Fi? | wired (the HA Green has no Wi-Fi; it is always wired); Wi-Fi only when there is no other way | `setup.network.wired` |
| Do you want to reach the house from outside the home now? | not now; if yes, offer Home Assistant Cloud first, then a VPN or tunnel if preferred | `setup.network.remote_access` |
| If you choose Home Assistant Cloud, what separate subscription budget do you approve? | none until the owner chooses; show the checked price under "Home Assistant Cloud" below first | `setup.cloud_budget` |
| Do your Wi-Fi devices get a 2.4 GHz network they can join? | assume yes; check when the first Wi-Fi device joins | `setup.network.wifi_24ghz` |

With `router_control: false`, skip the reservation. Use `homeassistant.local` if it works, or the current address
shown on the box's console; section 1 of `install/network-and-backups-first.md` walks both routes. Record only the
route kind in `setup.network.local_access`, keep the actual address in the owner's private note, and add the
address-change recovery line to `house/docs/gotchas.md`. Choosing no is complete, not a task to keep asking about.

Home Assistant Cloud is a separate paid subscription from the AI plan: it covers remote access, encrypted
off-site backups and voice links. Read the dated price and current-pricing link in
[`install/network-and-backups-first.md` section 2](../install/network-and-backups-first.md#2-remote-access-choose-later-but-choose-on-purpose).
Explain its price and the VPN or tunnel alternative from
`install/network-and-backups-first.md` section 2, then follow the owner's choice. Offering it is not permission
to subscribe, enable remote access or change router settings.

## Topic 4 - radios and devices already owned

*Why:* what the house already owns decides the first radio, and a radio decided late means a second hub or a
re-pairing week. `adapters/radios/` has the detail per choice; do not read it to the person.

| Ask | Default | Writes |
|---|---|---|
| What smart devices do you already own? (bulbs, plugs, locks, thermostats, cameras, speakers, a hub) | - | `setup.owned_devices` (free text, one line per kind, no serials) |
| Which of them came with their own hub or bridge? | prefer Matter where supported, otherwise a local maker integration; keeping the hub and adding it to HA is a first-class option, chosen by the owner | `setup.owned_devices` |
| Which radio for new devices? | Zigbee with a USB coordinator on an extension cable; Z-Wave for locks when they want a lock; Matter over Thread when their devices are Matter already | `setup.radios` |
| Which voice assistant is in the house, and what does it already control? For every device, check its own connection clues in `install/voice-assistants.md` before choosing a route or changing anything, even if the maker skill is enabled. | none; inventory/clues per device first; prefer native MOVE, or SHARE/KEEP by owner choice; preserve routines | `setup.voice`; private device/routine inventory outside the repository |

Rules: record what is owned as kinds and ecosystems ("six Hue bulbs on a bridge", "a Z-Wave lock"), never a model
number list; Phase 1 reads the real list from the box. Never recommend buying a radio before the box is up.

**Who answers "do I need to buy sensors?"** The agent does, after the box is up: Phase 1 topic 0 reads what is
already connected, and topics 3 and 4 match it to the owner's first request and priorities. Explain what can be
done with what is owned and propose only the missing sensors or radio, with cost, before the owner decides what
to buy. The owner buys; the agent does not place an order. If asked during setup, explain this next step now.

**Explain discovery when onboarding ends.** The sidebar bell opens Home Assistant's notifications, including
setup notices; it is separate from phone pushes. **Settings > Devices & services > Discovered** lists devices
and services Home Assistant noticed on the network. A discovery is an offer, not proof that the device belongs
to this household: shared networks can show other people's devices. Some integrations add themselves and create
devices or entities without a separate Add click. Leave discoveries alone during setup, identify ownership in
Phase 1, and ask the owner before configuring anything. The agent enables nothing from this list and sends
nothing to test it.

## Topic 5 - notifications

*Why:* the first message the house ever sends will go to a phone; the channel has to exist before the box does.

| Ask | Default | Writes |
|---|---|---|
| Which phones will the house talk to, and are they iPhone or Android? | the companion app on every household phone; nothing else at setup | `setup.notification_channels`, `setup.phone_platforms` |
| Will anyone need to be reached by text or call rather than a push? | later, as a backlog item with consent rules; nothing now | `setup.notification_channels` (planned) |

## Topic 6 - backups, off the box

*Why:* the install guide ends with a backup in two places. The second place has to exist before step one.

| Ask | Default | Writes |
|---|---|---|
| Where can a copy of the backup live that is not the box? (Home Assistant Cloud, a cloud drive, a NAS, a computer that is usually on) | offer Home Assistant Cloud first with its separate cost; the owner chooses the encrypted off-box route in `install/network-and-backups-first.md` section 3 | `setup.backup_offbox` (a kind, never a path, never a credential), `setup.cloud_budget` if chosen |
| Where will you keep the emergency kit (the backup encryption key and the authenticator setup key)? | a password manager and a printed sheet | `setup.emergency_kit` (a kind, never a location that identifies the house) |

## Topic 7 - the agent and its budget

*Why:* a run that does not know its budget runs out of it mid-change; an agent that does not know where it runs
does not know what it may touch.

| Ask | Default | Writes |
|---|---|---|
| Which agent am I, and where do I run? (a laptop in this folder; later maybe on the box) | laptop in the repository folder; on-box later, as a backlog item | `setup.agent.name`, `setup.agent.runs` |
| What plan or allowance pays for me, and does it show usage somewhere? | whatever the person has; if the provider shows a weekly percentage, the usage probe can read it (`templates/pacing/usage_probe.sh`) | `setup.agent.usage_probe`, `setup.budget.plan` |
| How much of the week's allowance should stay in reserve? | 10 %; 20 % whenever the owner is away | `setup.budget.buffer_pct`, `setup.budget.away_buffer_pct` |
| Should the week's allowance be spent by the reset, or by an earlier time so the last hours stay free for you? (optional) | the reset | `setup.budget.target` (null = the reset; else a percent by a time, "95 % by Saturday 10:00"; `principles/budget-and-pacing.md` rule 2) |
| How often will you look at what I have done? | once a day during setup; the backlog waits otherwise | `setup.review_cadence` |
| Which house-rule set is installed: Careful start or Direct? | Careful start recommended; not yet if no set is installed and read back | `setup.house_rules` (`Careful start`, `Direct`, or `not yet`) |

Rules (`principles/budget-and-pacing.md`): no unattended runs until a usage reading exists; a session that cannot
read usage stops at a fixed count of items.

After installing and signing in to an agent on the box, install the owner's chosen
[house rules](../templates/house-rules.md) before the hand-off. Recommend Careful start to a new owner; explain
Direct as the lower-confirmation alternative. Both keep backup before editing and the configuration check. Add the
chosen set to `/config/AGENTS.md` for the ChatGPT app or `/config/CLAUDE.md` for the Claude app when the
working folder is `/config`; otherwise use the instructions file in the agent's working folder. Have the agent read
the installed rules back in a new session. Record `not yet` in `setup.house_rules` and the hand-off note until the
set is installed and read back; keep any chosen-but-pending set in the note's open questions. If there is no on-box
agent yet, keep the note and make this choice when one is installed; do not claim it is already installed.

## Close Phase 0

1. Read the `setup:` block back in plain words. Correct. Set `setup.interviewed_on`.
2. Say which guide you will walk and how long it takes (`install/README.md`, "Hands-on time"), and that you will
   go one step at a time and wait after each.
3. Begin the guide. When its "Done when" list and the one in `install/network-and-backups-first.md` are all
   checked: first CHANGELOG entry, `setup.done: true`, `setup.installed_on`.
4. Tell the person: Phase 1 starts at their first request to build something, and takes about half an hour of
   questions before the first build. `00-start-here/what-to-expect.md` says the same.
