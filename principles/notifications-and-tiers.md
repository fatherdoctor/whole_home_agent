# Notifications and tiers

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

Routers, tiers (house / maintainer / alarm / life-safety), tags and replacement, consent, never send to verify.

## The rule

1. [core] **One router.** Every message to a person goes through one script. Callers never address a phone; a caller
   declares a class, the router decides who gets it.
2. [default, topic 6] **Classes nest, levels nest.** A working set of classes: `alarm` (needs level 1), `security` / `reminder`
   / `house` (level 2), `health` / `maintainer` (level 3). Each person's phone has a level: Nothing 0, Alarms only
   1, Security and reminders 2, Everything 3. A phone gets a push when its level ≥ the class's need. A caller that
   names no class defaults to `security`, so a forgotten field never makes a message invisible.
3. [core] **Life safety ignores the dial.** Fire and CO reach every household phone whatever its level, bypass test
   mode, and are exempt from every rate cap.
4. [core] **`maintainer` is the owner's class.** The system talking about itself (self-checks, nightly jobs, restarts,
   the support agent) goes only to the owner and is never texted to a guest. `house` (equipment such as a freezer)
   does reach guests.
5. [core] **Nothing reaches a person except the owner without the owner's OK for THAT send.** Push, call, SMS, speech into
   a room, speaker announcements, panel speech. One permission is never permission for the recipient, the channel
   or a follow-up test. Designed automated alerting and fixed-text replies to an inbound message are exempt; an
   AI session driving a console never is.
6. [core] **Never send to verify your own work.** Verify with the config check, template renders, `last_triggered`,
   listener sets and the push log; then let the owner send. If a test must leave the box, use the owner's own
   device service directly, or the router at `maintainer` class, never the router with the critical flag. The
   router is the worst thing to test with, because fanning out is its job.
7. [core] **A 200 from a notify service means accepted, not delivered.** Confirm on a real phone.
8. [core] **Tags and replacement.** Every push carries a tag; related states share one phone-side slot (alarm state,
   power, leak) so the newest replaces the oldest. Choice-less pushes get a Dismiss button. Prompts are cleared
   when resolved; clears go twice, a few seconds apart, at high priority. A flow that re-pushes on one tag is
   never cleared by tag.
9. [core] **One push per event.** When two automations react to one state change, one owns it and the other stands
   down. Zero coalescing window for alarm, escalation and life safety; seconds for security; longer for health and
   maintainer.
10. [core] **One cause, one warning.** A condition that is a consequence of an already-raised condition sits under its
    cause. Deference needs POSITIVE evidence: a cause that is unknown or unavailable suppresses nothing. A
    duplicate costs an annoyed swipe; a silence costs the event.
11. [core] **No all-clear for a problem nobody heard about** (`health-checks.md` rule 7).
12. [core] **Pushes say what happened, computed from live state**, never a literal that encodes a helper's old value, and
    they time-stamp from the event, not the send.
13. [core] **Time-critical pushes carry no expiry and high priority**, every class. The critical flag is reserved for the
    alarm's loud stage and life safety; spending it elsewhere trains everyone to swipe alarms away.
14. [default, topic 1] **Buttons never go to a minor's phone.** A child's device receives Dismiss only.
15. [core] **Push and text are separate instruments.** Household phones are push targets with a level and no consent;
    the text ladder is a few fixed numbered slots. A device does not consent; a slot has no level.
16. [core] **Consent is a record with a history, keyed to the number, never to the slot**: unknown → granted → revoked,
    append-only, kept. Refill a slot and the new number starts at no consent. STOP is authoritative and acted on
    at once; YES only records an intent until a human confirms, because the inbound webhook is unauthenticated.
17. [core] **The house texts nobody who has not subscribed.** Every outbound text clears three gates in order: master
    send switch, the number resolves to a directory contact, consent reads granted. Recording an inbound message
    is never gated.
18. [core] **Numbers live in the secrets file, referenced by key**; never in the repo, a doc, a comment, a sensor
    attribute or the recorder. A contact whose reference does not resolve is a fault, not a skip.
19. [default, topic 6] **The ladder.** When the alarm escalates, the adults and any live guest are texted and called first; later
    rungs are texted after a delay, then called. One walk per alarm, a daily cap on full walks, the first rung
    never capped; a suppressed walk pushes the owner to say so. A disarm stops the walk; every rung re-checks the
    alarm first. An acknowledgment word cancels calls and texts only, and only from someone on a rung or a live
    guest.
20. [core] **Audience is the first axis.** Household can fix it. A temporary occupant can see it and follow an
    instruction: plain wording, no system vocabulary, only things they can act on. Emergency contacts can only
    drive over, and only after the household is exhausted. The owner is told whatever a temporary person was told.
21. [default, topic 6] **Guest slots are time-boxed** and expire by themselves; a guest level gets plain-words arm and disarm, leaks,
    the armed-unlock warning and the alarm; no reminders, no health, no calls.
22. [default, topic 6] **A noise budget per hazard** (three pushes a day, then one replaceable roll-up; a new top-severity warning
    always pushes).
23. [default, topic 7] **The wall panel is the voice; speakers only when the panel cannot.** The speakers are a fallback, not a second
    voice: they depend on an internet connection, and the panel was unproven when the rule was set, so the speakers
    cover its failure. Two voices in one room are confusing. Text first, call a minute later: each step is more
    disruptive for the recipient than the last, and the minute is a starting value to tune, not a measured figure.
24. [core] **A send that returns an id is not a delivered message**, and a wait that cannot succeed is worse than no
    wait. Branch on the negative for machine detection.
25. [core] **A mute must expire by itself** and show as a problem while on.

## Why

Sends are audible, outward-facing and irreversible; the cost lands on someone who did not opt in. One router means
one place for levels, consent, tags and the test switch, and one place to grep. Classes and levels let a person
dial their own noise without anyone editing automations.

## How this goes wrong

- **Verifying by sending.** A session places a second "test" call to check its own work and rings a stranger; a
  test event makes the router fan out and family members get a push about something that is not happening. Having
  written down that a send cannot be verified is the moment to ask, not proceed. Rules 5, 6.
- **Accepted is not delivered.** A push with an unsupported option returns success and never arrives, with one
  detail-free log line. Rule 7.
- **Pushes that stack instead of replace.** A lone "clear" is lost in a burst, and a two-step flow leaves its first
  push on screen after the second arrives. Give related pushes one tag. Rule 8.
- **"Arm?" and "Armed" in the same minute.** One state change fans out to two automations. Rule 9.
- **One cause, many devices.** A power cut puts the UPS, a wall panel and a keypad on battery in the same second:
  three pushes for one event. A device on battery reports only when the power cut has not already. Rule 10.
- **Text that is out of date.** A push says "gone 15 minutes" from a literal when the helper is now 5; times are
  stamped at send, not at the event. Rule 12.
- **A push that waits in the phone.** Android doze holds a normal-priority push for minutes. Rule 13.
- **Push and text as one thing.** A contact directory that mixes the two needs a pile of helpers per person, and
  consent ends up keyed to the slot instead of the number. Rules 15, 16.
- **A reply to anyone.** An automatic reply to a keyword such as HELP answers any number, a stranger's included;
  its fix then refuses silently because it reads retired helpers. Evaluate the condition with nothing sent. Rule
  17.
- **A number in a comment.** A phone number in a config comment is one export from the repo. Rule 18.
- **A disarm that does not stop the calls.** The escalation stops on an acknowledgment but not on a disarm;
  harmless with empty rungs, serious once a neighbor is on the list. Rule 19.
- **The wrong audience.** One household member gets every countdown notice; a sitter gets `armed_away` instead of
  plain words; a filter default such as `default(true)` turns an explicit false into true and guests get household
  prompts; a guest set to Everything gets nightly-job failures; a guest slot never expires and "someone is
  expected" stays true, disabling an empty-house rule. Rules 4, 20, 21.
- **Two voices at once.** A countdown spoken by the panel and a speaker together in one room is confusing; the
  speakers exist to cover the panel's failure (they need the internet, and the panel was unproven when the rule was
  set), not to double it. A text and a call in the same moment skip the escalation: each step should be more
  disruptive than the one before. Text first, call a minute later if nobody has acknowledged; the minute is a
  starting value, tuned as the house learns. Rule 23.
- **An id is not a delivery.** A text gets an id and is then rejected by the carrier, and the script waits for a
  reply to a message nobody received. Rule 24.
- **A mute that never ends.** A notification mute set for one evening is still on a week later. Rule 25.

## How to check it

- grep automations and scripts for direct `notify.` calls outside the router and the owner's own device.
- Every call site declares a class; list sites per class and review the audience of each.
- A push-log sensor holds the last forty pushes with recipients; after any test the owner is the only recipient.
- `last_triggered` on every send-capable script after a build session that promised "nothing sent".
- "Sending switched off" shows as a FAULT on the health check, not a quiet state.
- Replay a fourteen-day push history and count bursts.
- Before a router change is applied: the replay report (`testing-and-simulation.md` rule 14) shows the same
  audience for every real push of the last weeks, or names the ruling behind each difference.
- The push log records who was actually sent to, after the sending switch and test mode, and a held push says it
  was held; a log that lists the would-be audience misleads every later replay and audit.
- Render every templated message against live state before it ships; cast numbers.
- A repo push guard blocks phone-number and code shapes; the recorder excludes inbound free text and code entities.
- A monthly rotating test to one contact, verifying ARRIVAL, written back as "last reached".

## Adapter notes

- **Companion app.** Only the legacy `notify.mobile_app_*` services accept tags and actions; look the names up.
  Android: `ttl: 0`, `priority: high`, up to three buttons, real text-to-speech, a critical channel for the alarm
  stage. iOS: critical alerts must be granted per device and degrade silently; no TTS; phones do not reliably
  return the tag on an action, so put it in the action data too. Never set `authenticationRequired` or
  `destructive`. See `adapters/notifications/companion-app.md`.
- **Pushover.** Priorities map to levels; emergency priority retries until acknowledged, so use it only for the
  alarm class. No tag replacement, no clearing; one URL action. (General knowledge, not tested.)
- **Telegram.** Inline-keyboard buttons; replacement is "edit message", which needs the message id stored; one
  chat per person if per-person levels matter. (General knowledge.)
- **SMS.** No buttons, tags or replacement; one segment per message; STOP and HELP keywords and a consent record are
  mandatory; a sender id is forgeable, so no keyword may answer "is anyone home". See
  `adapters/notifications/sms.md`.
