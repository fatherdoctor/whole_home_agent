# Safety and security

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

Alarm, locks, codes, guests; what should not run without a person.

## The rule

1. [core] **The owner chooses what an AI agent may control** (topic 8). An owner may choose a lights-and-switches-only
   limit, so the agent cannot arm, disarm, lock, unlock or help with other restricted devices. This is an option,
   not an assumed default; it reduces accidental changes but also keeps the agent from helping with those devices.
   Choose and record any limits with the owner; [optional guard rails](../templates/agent-guard-rails.md) offers
   a list to install. Never change codes, slots, ladder rungs, consent or the contact directory. Reading secrets
   (PINs, codes, tokens and passwords) remains outside the agent's access; ask before anything hard to undo.
   The choice cannot override a runtime's enforced permissions or higher-priority
   instructions: check those before promising an action.
2. [default, topic 7] **Voice-assistant exposure is lights, switches and scene scripts only.** No sensors, media players, locks,
   alarm or app switches. The assistant tells the house what was said; it never decides.
3. [core] **Assistant and cloud logins are done by the owner in the UI**, never by a chat or API session.
4. [default, topic 5] **Location auto-arm is Stay only.** Arming Away is an intentional human act: panel, app, or a button on a push.
5. [default, topic 1] **Who counts for presence is a per-person toggle, derived live; a missing toggle counts as monitored.** The
   failure direction is "the house does not arm itself" (visible), never "the house arms around someone"
   (invisible).
6. [default, topic 3] **Ignore thermostat occupancy sensors** for presence, arming and dashboards.
7. [default, topic 3] **One switch per code.** Any code the locks accept also disarms; there is no "unlocks but does not disarm". The
   lock-code manager is the single source of codes; the alarm's own user list stays empty.
8. [default, topic 6] **A temporary code is a notice on the self-check**, never a fault, never a push. Naming the slot is how a code
   opts in.
9. [core] **Codes never reach the repo, a doc, the logbook or the recorder.** Code entities, caches and buffers are
   recorder-excluded; the wall panel's user is non-admin and local-only; a read-only panel twin carries no live
   controls.
10. [core] **A lock's reported state is only what it last said.** Wait for the state you asked for and push on a miss.
11. [default, topic 4] **An unlock through any dashboard never disarms.** A manual unlock while armed speaks a warning at the panel
    and texts any sitter.
12. [core] **An inbound message may acknowledge and may never touch alarm state.** An acknowledgment stops calls and
    texts only; siren, pushes and announcements continue. No keyword answers anything that helps someone decide
    whether to approach the house; no TEST keyword.
13. [core] **A stale tap does nothing.** An already-armed alarm is never disarmed by a push button; a late tap gets a
    one-line "too late" reply.
14. [default, topic 5] **"A guest is staying" is a human toggle that no automation writes.** While on, departure auto-arm and re-arms
    do nothing; night Stay and morning disarm continue. The auto-arm master means "the house never arms itself"
    and gates every re-arm.
15. [core] **Life safety inverts the burglary rules**: no entry delay, no first tier, runs whatever the alarm state,
    critical push to every phone ignoring levels, speakers. Any surface can acknowledge; the detectors themselves
    are untouchable; only the detectors clearing ends it.
16. [default, topic 4] **Unlocking the doors and disarming on a smoke or CO trip is a choice with a cost, not a given.** Egress
    unlocking helps an occupied house get out; it also means a false trip, a detector fault or a deliberately
    triggered detector leaves the house unlocked and disarmed, possibly with nobody home. The interview asks it
    (topic 4). A house that chooses it scopes it: only while someone is home, only the egress-side locks, re-lock or
    push the owner when the detectors clear, and log a fault if it ever happens with the house empty. A house that
    does not chooses "disarm only" or "neither", and says so in its policies file.
17. [core] **No firmware to radios, locks or boards during a trip or a soak.** The freeze covers the time away, not
    forever: new firmware is looked for and assessed monthly (one dated page per family: what is new, what it fixes,
    what it risks) and taken after the trip and its soak, one family at a time, on a test device first. When a build
    does go on: one device, one build, its free memory and loop time watched for an hour, the previous image kept to
    flash back, the owner's own acceptance tests before the next build - and a build that feels laggy loses to one
    that is merely tighter on memory.
18. [core] **One warning per cause, scoped to when it matters** (a dog-door back door open while armed is a fault only
    when the house is truly empty or after bedtime).
19. [default, topic 4] **Automations for arming, disarming, locking, unlocking and code changes should not run
    without a person in the loop.** A code window a person set counts as that person's act. The owner may choose
    the exceptions: location auto-arm to Stay (rule 4) and life-safety unlocking and disarming on a smoke or CO
    trip (rule 16).

## Best practice by default, the owner's informed choice

Every practice in the kit is a default and a recommendation, never a lock. Where a weaker way still works (a plain
backup copy in a store the owner trusts, a VPN or forwarded port instead of Cloud, one place for the emergency
kit, two-step login off), say the risk in one plain sentence, let the owner choose it, and record it on the
`Owner's choices:` line of the hand-off note and in `adoption.opted_out`. Do not ask twice. Hard stops stay only where a choice
would harm someone else or leave the owner with no way back: a secret in chat or the repository, two-step login
left half on (enrollment unfinished or unconfirmed, so the owner can be locked out), a lost backup key, a message to someone who has not agreed, locks or alarm exposed to a voice
assistant. See `install/network-and-backups-first.md`, "The owner's choice".

## Why

The alarm, the locks and the people who can be called are the parts of the house where a wrong action has a cost
that no rollback recovers. The owner chooses the agent's limits; other rules here keep sensitive information out
of records or make the failure direction visible.

## How this goes wrong

- **Exposing everything to the voice assistant.** Sensors, cameras, media players and app switches all become
  voice targets; replies say "device isn't responding" when the action happened, and smart speakers get exposed
  back to themselves as devices. Cloud-driven changes arrive under a system user, so the wrong command gets blamed
  unless you read the assistant's own log. Rule 2.
- **Location arming Away.** The house auto-arms Away on departure and the pets trip a motion sensor. A disarm on
  arrival that does not cover the mode actually used never fires, and one that is not guarded by an empty house can
  disarm a house full of sleeping people when a phone's zone flaps at 3 a.m. Rule 4.
- **A device that makes someone always home.** A tablet attached to a child's person entity reads home
  permanently, so the house can never be empty: it stops auto-arming and stops prompting, and nothing reports it.
  Rule 5.
- **Thermostat occupancy.** A thermostat's room sensor reads occupied for hours with nobody there and blocks every
  automatic arm. Rule 6.
- **A code that opens but does not disarm.** Whoever holds it opens the door, starts the entry delay and has no way
  to stop it, so every use ends in a siren and an escalation. There is no case where that is wanted. Rule 7.
- **Codes in the history.** Code entities are written to history and the logbook by default; a code pasted into a
  description is one export from the repo; a "read-only" panel copy turns out to carry live controls. Rule 9.
- **A lock that said yes.** A lock acknowledges a command and never moves, with no jam flag and nothing in the log;
  its state shows what was asked for until someone looks. Rule 10.
- **A guest rule that ignores its own switch.** An automation's description says it respects "a guest is staying",
  but its conditions do not, so a sitter is armed in on. Rule 14.
- **Fire with the alarm armed.** Without an explicit rule, the first person out during a fire starts the entry
  delay, the siren and the burglary escalation on top of the fire one. A detector's test flag that can latch on
  would turn a real fire into a test. Rule 15.
- **A false trip unlocks an empty house.** A detector fault or a burned dinner trips the life-safety path while the
  family is out; a house that unlocks every door on any trip is now open and disarmed with nobody home, and nothing
  tells the owner until the detectors clear. Scope the unlock, or do not unlock. Rule 16.
- **A firmware batch.** One switch crashes mid-update and its radio jams the whole mesh, a lock included. Rule 17.
- **A warning that is right only sometimes.** A pet door left open is normal during the day and a fault only when
  the house is armed at night; without scope it pages on every arm, from two systems. Rule 18.

## How to check it

- The exposure list per assistant: every exposed entity is a light, a switch or a scene script; the speakers' own
  players are not exposed.
- grep automations for any arm-away call triggered by presence; location-driven arms land on armed-home.
- Presence toggles: one per person entity, derived live; a new person entity shows up as a row, not silently.
- grep automations, templates and dashboards for thermostat occupancy entities.
- Self-check faults: a code slot with override on; sending switched off; an automatic-arm automation disabled; a
  lock state not reached after a command. Notices: an active temporary code; "not monitored" people.
- Recorder excludes cover code entities; a search of git history for any live code is empty; the push guard's selftest passes, and it
  refuses a code or PIN written as digits after the word, phone shapes and tokens (`templates/guard/README.md`); it
  does not catch a bare number with nothing around it, so the rule against writing codes still stands.
- Panel user non-admin and local-only after every re-onboarding; the read-only twin regenerated with no controls.
- The life-safety path is verified by rendering and traces, never by firing a detector in the house.

## Adapter notes

- **Alexa.** Exposure is per entity through the cloud integration, synced after changes; stale devices may need
  deleting in the app. Zigbee devices can answer before state settles (a latent "not responding"). Changes arrive
  under the cloud system user. Speaker text-to-speech uses a community integration with a real account login the
  owner performs. See `adapters/voice/alexa.md`.
- **Google.** Same cloud path and system user; expose scene scripts only, or nothing.
- **Apple / HomeKit.** The same exposure policy applies.
- **Assist / a conversation agent.** Exposure is Settings → Voice assistants → Expose; an LLM conversation agent is
  a cloud call and cannot be load-bearing; start narrow and exclude paddle relays in smart-bulb mode. Rule 1
  makes the control limit an owner choice for any such agent.
- **Lock-code managers.** Keymaster-style integrations call scripts by YAML key, and the alarm's own user list must
  stay empty; with a different manager, keep the one-switch-per-code rule however it is expressed.
