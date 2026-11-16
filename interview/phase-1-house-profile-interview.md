# Phase 1 - the house-profile interview

*Status: written (O2, 2026-10-13); the "From the box" column and the one-line-confirm rule for an existing house
(KIT-EXIST.c, 2026-10-31). Run by the agent at the person's first request to build something. Follow
`interview/README.md`, "How to interview". Writes the `profile:` block of `house/profile.yaml` (schema:
`profile-template.yaml`), then generates the house's files (`generated-files.md`).*

**Purpose.** Turn the principles into this house's own rules before the first thing is built: who lives here and
what each of them may see and do, what the house calls its rooms and modes, what must never break, how and when
people are told things, what voice and the agent may touch, and how the work is paced. About half an hour. The
person may stop after any topic; the "needed before" column in `generated-files.md` says what each stop allows.

**Opening.** Record the request that triggered the interview in `profile.first_request`, word for word. Say that it
becomes backlog item 1 and that the questions make sure it is built the way this house works.

## Topic 0 - read the box (no questions)

*Why:* the box already holds areas, devices, integrations, people and phones that the person typed during
onboarding. Asking again is slow and gets a different spelling. Names are for people; ids are the handle; read
them back, never guess (`principles/naming.md`).

**The one-line-confirm rule (an existing house, `setup.existing_house: true`; `AGENTS.md` "Phase 0E" rule 4):**
*confirm what the box can tell, in one line per topic; ask only what it cannot.* Each topic below opens with one
sentence built from the inventory ("you have 14 areas on two floors, named as on the box: right?"), the person says
yes or corrects it, and the topic's questions are then only the ones in the "Still asked" column of the table
"From the box". A confirmed line is written as if answered (`topics.<name>: done`), never as `assumed`. The script
does not fork: the same topics, the same files; about twenty minutes instead of thirty. On the other two paths the
reads below are the whole of this topic, as before.

Read, however your runtime reaches the box (its API, a live export the person triggers, or the person reading the
Settings pages to you if you have no access):

| Read | For | Record in |
|---|---|---|
| Areas and floors | topic 2 | `profile.areas` (names as typed) |
| Devices grouped by integration; entity counts by domain | topics 3 and 7 | `profile.devices.owned` |
| Integrations and apps installed; Home Assistant version | topic 3; the wiki skeleton | `profile.devices.integrations` |
| Persons and zones | topic 1 | `profile.people` (labels only) |
| Phones with the companion app | topics 1 and 6 | `profile.people[].phone_platform` |
| Backup settings and the last backup time | topic 9; a health check | nothing; confirm Phase 0 held |

Say what you found in four lines. Everything below starts from it.

**From the box, on an existing house.** Phase 0E already wrote the inventory (`house/export/*.json`,
`house/docs/inventory.md`) and the first look (`house/docs/first-look.md`); read those, and take a fresh export
only when the helper says `E0-inventory` is stale. The column says, per topic, what you propose from them before
you ask, and what the box cannot tell:

| Topic | From the box (propose, confirm in one line) | Still asked |
|---|---|---|
| 1 people | persons and zones (`entities.json`), the phones with the companion app, the user count by role (`users.json`: counts only, never a name from `.storage`) | roles, who is a minor, each phone's level, who counts for presence, sitters and visitors, pets, the emergency contact |
| 2 areas and the house's words | areas and floors as typed (`areas.json`); `input_select` options that look like modes (`helpers.json`: a `house_mode`, `presence`, `guest` select); the words another system already uses go straight into `house_words.reserved` with why (the alarm's arm modes from the `alarm_control_panel` attributes: "Away: the alarm's arm mode") | which of those words to keep as the house's modes; nicknames; which rooms are a child's |
| 3 devices | integrations and devices by integration (`integrations.json`, `inventory.md`); the safety-relevant domains present (`lock`, `alarm_control_panel`, a `cover` with the garage class, smoke, CO and moisture binary sensors, cameras, climate) proposed as `devices.safety_relevant` | what is dangerous that the box cannot see, what is planned, what must keep working without Home Assistant, what must never be automated |
| 4 priorities | nothing | all |
| 5 rhythm | nothing; the schedules and sun automations (`automations.json`) are a hint you may say aloud ("your night automations run at 22:30: is that bedtime?"), never an answer | all |
| 6 notifications | the notify services that exist and the phones they reach, by role; an existing router or tag scheme when the first look's check 8 found one (then "one router" is a tidy-up row, not a build item) | the classes, who gets what, the second channel, the sitter, the speech surfaces |
| 7 voice | the voice integrations present (Alexa through the cloud or a media integration, Google, HomeKit, Assist pipelines) and the count of exposed entities | per-area assistants, children's rooms, the wake word |
| 8 the agent's permissions | the automations that already act on locks, the alarm or the garage, by name (the first look's check 12), so the "never" list is read against what already runs: say that the kit's agent will not add to them | all; the house widens the list in `policies.md`, as today |
| 9 operations | the backups and their locations by kind (`backups.json`), the apps and which auto-update (`addons.json`), the existing repository (`setup.existing_repo`) | freezes, the restore drill, staging |
| 10 documentation | an existing manual or notes folder, when the person named one in Phase 0E | the choices, as today |

A pre-filled value the person corrects is written as corrected, and the inventory is not edited to match: the
export is the box's reading, the profile is the house's answer. Where the pre-fill and the kit's rule disagree (an
existing presence mode called "Away" beside an alarm that arms Away), record the clash in `house_words.reserved`
now and the difference in `policies.md` at topic 11 ("Where this house differs from the kit"); do not propose a
rename here.

## Topic 1 - people and roles

*Why:* the audience is the first axis of every message and every permission (`principles/notifications-and-tiers.md` rule
20): household can fix things, a temporary occupant can follow an instruction, an emergency contact can only
drive over. Children's phones get no buttons (rule 14).

For each person the box lists, and anyone it does not:

| Ask | Default | Writes |
|---|---|---|
| Who lives here, and how should the house refer to each of you? | first name or role, the person's choice | `people[].label`, `people[].role` (owner, adult, child, guest, sitter, visitor, emergency-contact) |
| Who is a minor? | - | `people[].minor` |
| Which phone does each have, and should the house be able to reach it? | companion app on every adult's phone | `people[].phone_platform`, `people[].notify_level` (0 nothing, 1 alarms only, 2 security and reminders, 3 everything; owner 3, adults 2, minors 1; a minor's dial must exist and be set by the owner, because a missing dial counts as Everything) |
| Who may control the house from the app, from voice, from a wall panel? | adults: app and voice; minors: voice for their own room; guests: a time-boxed guest level, set up later | `people[].may_control` |
| Whose presence counts when deciding the house is empty? | every adult; a missing answer means "counts" (`principles/safety-and-security.md` rule 5). A child with no tracked phone: `false`, and the house's "Not Home" then means "no adult is home", never "nobody is home": say so in `house_words` | `people[].counts_for_presence` |
| Who stays here sometimes without you: a sitter, family? Who comes in regularly without staying: a dog walker, a cleaner? | record the role and how often; the guest and sitter mechanisms are a later backlog item | `people[]` with role guest, sitter or visitor, `people[].frequency` |
| How does each sitter or visitor get in (a key, a lockbox, a code, let in), and may the house notice the door during their usual window? | key or let-in; noticing the door is told to the owners only, never to the visitor; a code makes it a design-only item | `people[].entry`, `people[].door_notice` (topic 11 writes the policies line from them; nothing is written to `house/docs/policies.md` before it exists) |
| Any pets: what kind, do they roam the house, who looks after them when you are out? | none | `pets[]` (topic 3 then prefers pet-immune motion sensors) |
| Who should be called if nobody in the house answers? | nobody until the alarm exists; recorded as a role, never a number | `people[]` with role emergency-contact |

Never record a phone number, an email or an address. A person who must be reachable by text later gets a secrets
key name, decided when that item is built.

## Topic 2 - rooms, floors and the house's words

*Why:* every device gets an area (`principles/naming.md` rule 7); voice assistants, the overview and the manual all key on
area names; a word that two systems use for different things causes a wrong arm or a wrong light (rule 6).
*On an existing house:* the areas are confirmed in one line, not listed one by one, and the modes the house already
has (a select the people use) are offered as `house_words.modes` as they are; nothing is renamed.

| Ask | Default | Writes |
|---|---|---|
| Here are the areas the box has: `<list>`. Anything to rename, merge or add? Outdoors, garage, utility? | keep what is typed; add outdoor and utility if missing | `areas[].name`, `areas[].floor` |
| Which rooms are shared, which are one person's, which are a child's? | - | `areas[].kind` (shared, private, child, outdoor, utility) |
| What do you say for "nobody is home" and for "we have guests staying"? | "Not Home" and "Guest staying"; if an alarm will exist, its modes (Away, Home, Night) are reserved and the house's mode never reuses them | `house_words.presence_modes`, `house_words.guest_mode`, `house_words.reserved` |
| Is there a word you use for the whole place, or for a floor, that the house should use too? | none | `house_words.nicknames` |

## Topic 3 - devices, ecosystems, and what is dangerous

*Why:* the design-only list (`principles/backlog-and-planning.md` rule 9, `principles/safety-and-security.md`) is written per house:
anything that can lock someone out, let someone in, flood, burn, or leave a family in the dark is designed first
and built only with the owner present.

| Ask | Default | Writes |
|---|---|---|
| Here is what the box sees: `<integrations and device kinds>`. What else is in the house that it does not see yet? | - | `devices.owned`, `devices.planned` |
| Which route should each device use: Matter, a local maker integration, or a retained hub/app? Explain the preference and reasons to keep the maker route using `install/voice-assistants.md`; confirm the owner's choice. | Matter where supported, otherwise HA's local maker integration; keep a Hue bridge for independent local control, app-only features/firmware, or lack of native support when the owner prefers | `devices.owned` (chosen route and reason, no private details) |
| Which of these matter for safety: locks, alarm, garage door, water shut-off, smoke or CO, cameras, heating, a medical device? | every one the box has or the person names | `devices.safety_relevant` |
| Which of them must keep working when Home Assistant is down? | locks open with a key or code; heating keeps its own thermostat; the garage keeps its wall button | `priorities.must_work_without_ha` |
| Are there things you want the house not to automate? (a bedroom camera, a child's door lock, a medical device) | Ask the owner; the owner may change these limits later | `priorities.never` (add the owner's choices; note a design-only device) |

Rule: a device on the safety list gets a design document with a build plan before any automation; the agent never
builds it unattended. Say this now, once. *On an existing house* add the second half: what already automates a
device on that list stays as it is (the first look said it once, with its offer); the rule binds new work.

## Topic 4 - priorities and what must never break

*Why:* when two rules collide (comfort versus energy, convenience versus security) the house needs one ranking
that was decided in daylight, not by whichever automation ran last.

| Ask | Default | Writes |
|---|---|---|
| Rank these for this house: security, comfort, energy, convenience. | security, comfort, energy, convenience | `priorities.order` |
| What must never happen? (locked out, lights off mid-bath, a false alarm at 3 am, a camera recording the wrong room, a push waking a child) | - | `priorities.never` |
| What failed before, in this house or the last one, that you do not want again? | - | `priorities.never`; a first `house/docs/gotchas.md` entry if it is a lesson |
| Which is worse: a message you did not need, or a silence about something real? | silence is worse for security and safety; noise is worse for comfort and energy | `priorities.noise_vs_silence` |
| When a smoke or CO detector trips, should the house unlock the doors and disarm by itself? (`principles/safety-and-security.md` rule 16: egress helps an occupied house get out; a false trip leaves an empty house unlocked) | disarm only; unlock the egress-side locks only while someone is home, re-lock when the detectors clear | `priorities.life_safety_unlock` (`none` / `disarm` / `disarm_and_unlock_when_home` / `disarm_and_unlock`); a line in `house/docs/policies.md` |

## Topic 5 - rhythm and modes

*Why:* "one warning per cause, scoped to when it matters" (`principles/safety-and-security.md` rule 18) needs the house's
hours; quiet hours decide which classes may wake someone; a trip is a freeze (`principles/change-control.md`).

| Ask | Default | Writes |
|---|---|---|
| When does the house usually wake and go to bed, weekdays and weekends? | - | `rhythm.wake`, `rhythm.bed` |
| Quiet hours: when should nothing but an alarm or a life-safety alert make a sound or a push? | bed to wake | `rhythm.quiet_hours` |
| Who is home in the day? Does anyone work from home? | - | `rhythm.home_in_the_day` |
| How often is the house empty for days at a time? | - | `rhythm.trips_per_year` (a freeze before each; the away buffer applies) |
| Which modes do you want the house to know? | Home, Not Home, Night, Guest staying; the alarm's own modes stay the alarm's | `house_words.modes` |

## Topic 6 - notifications

Read `setup.standing_rules` first and confirm them with the owner; no default below overrides those rules, and carry them into `notifications` and `policies.md`.

*Why:* one router, classes that nest, levels per phone, life safety ignores the dial, the owner alone hears the
system talk about itself (`principles/notifications-and-tiers.md` rules 1 to 5).

| Ask | Default | Writes |
|---|---|---|
| The house groups messages as: alarm; security, reminders and house (equipment); health and maintainer (the system about itself). Does that fit, or do you want another class? | the six classes as they are | `notifications.classes` |
| For each phone: everything, security and reminders only, alarms only, or nothing? (from topic 1; confirm) | as topic 1 | `people[].notify_level` |
| Who should hear about the system itself: backups, a sensor gone silent, a failed check? | the owner only, always | `notifications.maintainer_to` (owner) |
| Smoke and CO: every phone, every time, ignoring quiet hours and levels? | yes; this is the one class that ignores everything | `notifications.life_safety_everyone` |
| A second channel for when nobody answers a push: a call, a text, a speaker? | none now; the text and call ladder is a design-only item with consent rules | `notifications.second_channel` |
| Which events should use which class, and should any wake you through Do Not Disturb (iPhone: Time Sensitive)? Read the person's ideas so far: a leak, a door open while nobody is home, a visitor arriving, a weekly battery list. | leak and door-while-away: security, urgent; a visitor arriving: house; batteries and backups: maintainer; smoke and CO: life safety | `notifications.events` |
| Which of the children's devices run the companion app? (a tablet without it gets nothing, not even smoke and CO) | the owner tells a child with no app in person; written into `docs/notifications.md` section 2 | `people[].phone_platform` (none for no app) |
| What may a sitter or guest be told? | plain-words arm and disarm, leaks, the alarm, nothing about the system | `notifications.sitter_gets` |
| Is there a wall panel or a speaker the house may speak through, and in which rooms? | none; when there is one, the panel is the voice and speakers only when the panel cannot | `notifications.speech_surfaces` |

Rule, said once now: the agent never sends a message to anyone but the owner, and never to verify its own work;
the owner sends the first test of every new message. *On an existing house* the paths that already reach people
are confirmed, not rebuilt: `notifications.md` records them, and the router is a tidy-up row ("one router, when you
want one") unless the house has none.

## Topic 7 - voice

*Why:* exposure is lights, switches and scene scripts only (`principles/safety-and-security.md` rule 2); the assistant
tells the house what was said, it never decides.

| Ask | Default | Writes |
|---|---|---|
| Which assistant in which rooms, and what does it already control? Confirm Phase 0 and the box; for devices still outside Home Assistant, inventory their connection and routines with `install/voice-assistants.md`, check each device's own clues and choose native MOVE, SHARE or KEEP with the owner. | prefer native control; keep the maker hub/app or voice path when the owner chooses; nothing removed before inventory, tests and approval | `voice.assistants`, `voice.per_area`; private inventory outside the repository |
| Voice may control lights, switches and scenes. Anything to remove from that? Nothing is added without a design. | as stated | `voice.exposure` |
| Should a child's room respond only to that child's device? | yes where the assistant supports it | `voice.child_rooms` |
| If local voice (Assist): a wake word and a name for the house? | the assistant's default wake word; no house name | `voice.wake_word` (the word, not a secret) |

Logins to assistant and cloud accounts are done by the owner in the UI; the agent never asks for them.

## Topic 8 - the agent's permissions

Read `setup.standing_rules` first and confirm them with the owner; no default below overrides those rules, and carry them into `agent` and `policies.md`.

*Why:* the owner chooses optional limits on the agent's actions (`principles/safety-and-security.md` rule 1).
The [guard-rails template](../templates/agent-guard-rails.md) offers individual choices, including not locking
or unlocking locks and not arming or disarming the alarm. Choosing a device limit means the agent cannot operate
that device for the owner. Existing standing instructions and enforced runtime permissions still apply; the agent
does not widen its own access.

| Ask | Default | Writes |
|---|---|---|
| Which optional guard rails would you like to install, such as not locking or unlocking locks or not arming or disarming the alarm? | no optional line selected; existing standing instructions and permissions still apply | `agent.may`, `agent.never` |
| What do you want me always to ask before? | delete, restart, firmware, version changes, anything on the safety list, anything that reaches a person | `agent.ask_first` |
| Is there anything I may never touch, beyond topic 3? | - | `agent.never` |
| May I work while you are not watching (a scheduled run)? | not until the usage probe and the push guard exist; then yes, under the budget gate, drafts only | `agent.unattended` |
| Do you want an always-on watcher later (the tier-2 support agent)? | later; it is the last thing to build (`principles/00-index.md`) | `agent.tier2_wanted` |

## Topic 9 - budget, pacing and operations

*Why:* the pace line and the buffer (`principles/budget-and-pacing.md`), the freeze before a trip and the backup tiers the
hardware allows (`principles/change-control.md`, `principles/backups-and-recovery.md`) are decided here and written once.

| Ask | Default | Writes |
|---|---|---|
| The reserve from Phase 0 was `<buffer>` %, `<away>` % when away. Still right? | 10 and 20 | `setup.budget` (confirm) |
| (An existing house) Your configuration already lives in a repository at `<host kind>`; keep it as the mirror of record, beside the kit's? | keep it; folding it in is a tidy-up row | `setup.existing_repo` (confirm), a line in `docs/operations.md` section 1 |
| When is the next trip or busy stretch? A freeze starts the day before and nothing but a fix lands during it. | - | `operations.freezes` (dates only) |
| Backups: daily on the box, a copy off the box; with this hardware the tiers possible are `<from install/README.md>`. Which do you want? | all the hardware allows; a restore drill monthly | `operations.backup_tiers`, `operations.restore_drill` |
| A staging copy for risky changes? | yes on a VM (a clone); on a Pi or Green, a second card or the official "restore to a spare" drill instead | `operations.staging` |

## Topic 10 - documentation

*Why:* a household manual for the people, a maintainer wiki for the builder, a CHANGELOG and a gotchas file for
every session that follows (`principles/documentation.md`).

| Ask | Default | Writes |
|---|---|---|
| A manual for the household, in plain words, with a sitter track? | yes, both tracks; the sitter track is written when a sitter is first expected | `documentation.manual`, `documentation.sitter_track` |
| A maintainer wiki: start the schema now and write pages as integrations arrive? | schema now, pages from the fifth integration | `documentation.wiki` |
| Which language for the manual, if not the house's? | the house's language | `documentation.manual_language` |

## Topic 11 - generate

Follow `generated-files.md`. In order: `house/docs/naming.md`, `house/docs/policies.md`, `house/docs/notifications.md`,
`house/docs/health-checks.md`, `house/docs/operations.md`, the manual skeleton, the wiki schema, `house/docs/gotchas.md` (empty, with the
standard), the CHANGELOG (an entry for the profile), and last `house/docs/backlog.md` with the first request at the top.
Every generated file carries a status line naming the profile fields it was made from and the date. **An early stop
still generates** (README rule 7): run this topic with the answered topics, write `(pending: topic N)` where an
answer is missing (generation rule 3), and set `profile.generated_on`. A later session that answers a pending topic
regenerates only the files that topic feeds, and never over a file a person has edited since (diff first; say so).

## Close Phase 1

1. Read the whole `profile:` block back in plain words, topic by topic. Correct. Set `profile.completed_on` and
   `profile.generated_on`; mark each topic `done`, `pending` or `assumed`.
2. Set `profile.done: true` only when no topic is `pending`. Otherwise say what each pending topic blocks.
3. Show the backlog: the first request at the top, sized in points, with its "Needs first" line, followed by
   the setup items the generated files call for (on an existing house, only those the house has no equivalent
   of; the rest sit in the tidy-up section, which you name once and do not sell). Ask for the go on item 1.
4. Say what comes next, in one line: one item at a time; plan, approve, build, test, record, report.
