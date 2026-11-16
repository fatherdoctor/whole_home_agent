# An existing house: adopting the kit where Home Assistant already lives (path C)

*Status: written (KIT-EXIST.a, 2026-10-31) from the design for the third way in. For you, not for the agent; the
agent's side is `AGENTS.md`, "Phase 0E". The export and first-look scripts this page describes are
`templates/export/export_house.py` and `first_look.py` (KIT-EXIST.b1 and .b2, 2026-10-31).*

You have been living with Home Assistant for a while: devices you paired, automations you wrote, dashboards the
household knows, habits nobody wrote down. This page is for you. Paths A and B (`README.md`) assume an empty
house; this path is **adoption, not replacement**.

## What will happen

- **The agent reads first and changes nothing.** Its first session on your house is read-only end to end: it
  looks, it writes down what it saw, it asks. No rename, no new helper, no automation touched, nothing written on
  the box except its own folder. It proves this to itself with a before-and-after comparison, and the comparison
  is one of the lines in the level 0 test.
- **A backup comes before the looking.** You download one backup off the box, to your phone or a computer, before
  the agent runs anything; opening it, when you are at a computer, is what proves it usable (level 0's own line,
  and it may come later). An existing house has more to lose than a new one.
- **Nothing you have is renamed, moved or rewritten to fit the kit.** The kit's naming scheme, its documents and
  its rules apply to new work from the day you adopt it. What exists stays as it is.
- **Your habits win.** Where your setup and a kit principle disagree (your own way of naming automations, a
  presence mode that shares a word with the alarm, a notification sent straight from each automation), your way
  stands, and the agent writes that down once so it never argues it again. For the few things on the kit's safety
  list (an automation that arms, unlocks or changes a code with nobody in the loop; a message reaching a person
  you never said may be messaged; a secret in a configuration file; no backup off the box; no second factor on an
  administrator's login) it says so once, plainly, with the fix on offer; after that it is your choice like any
  other. The ladder's own tests (level 0's backup lines, level 1's guard) still say what they say.
- **The old is a tidy-up list you may never take.** Everything the first look finds, and every kit piece you
  already have an equivalent for, goes into one optional section of the backlog, one item per row with its undo.
  A full tidy-up section is not a failing of your house, and no test counts its rows.

## What you need

- Home Assistant running and onboarded, with you as an administrator.
- The agent either **inside the box** (your runtime's app, path B's steps 2 and 3 in `README.md`; the most it
  can see, which makes the first look the most complete) or **on a computer** with an administrator's token
  (`install/agent-access.md`). From a computer, two things cannot be read at all: whether each administrator's
  login has a second factor, and whether a configuration file holds a secret. The agent says so and asks you the
  first one; the second waits for the app, or for a copy of the configuration folder you give it.
- About thirty minutes for the first session, at a computer or a phone; about twenty more later, at your first
  request, for the shorter interview. A phone is enough for every step; only opening the backup file (the second
  half of step 2 below, the level 0 line "proven usable") wants a computer or a tablet archive app that can list a
  `.tar` file, and that half may wait.
- **No agent yet, only a chat app?** [`from-a-chat-app.md`](from-a-chat-app.md) (start 4, "Home Assistant already running") guides the
  account, two-step login, backups and later changes by hand. The automatic inventory and first look below need
  an agent; the chat cannot read the box.
- `what-you-need.md` for the rest; `getting-the-kit.md` for how the kit reaches the agent and your own private
  copy of it. If your configuration already lives in a git repository, keep it: the agent asks where it is and
  records it as your configuration mirror; the kit goes into a fresh private repository of its own. Folding the two
  into one is a tidy-up row for later, if you ever want it.

## What to expect

### If Alexa already controls your plugs

This path is for a house that already runs Home Assistant.
If only Alexa runs your devices, start with [the setup paths](README.md) instead.
Keep those devices and routines working while you prepare Home Assistant.

After the read-only adoption and the interview, choose one ordinary lamp plug for the first change.
Follow [the voice guide](../install/voice-assistants.md#many-wi-fi-plugs-one-pilot-then-small-batches) for Matter or maker integration, then small batches.
It preserves familiar Alexa controls and records an undo for each plug.
Next, [the first automation lesson](your-first-automation.md) introduces a reusable script.
The voice guide then shows [how Alexa can run that script](../install/voice-assistants.md#4-a-safe-scene-script-with-an-alexa-phrase).
None of these changes belongs in the read-only adoption session.

### The adoption session

1. **One question.** The agent finds a running Home Assistant and no house profile, and asks whether this is a
   house you have been living with or a fresh install. It says the numbers it sees ("41 automations, 3
   dashboards, so I assume lived-in") as the prompt, not as the decision. Your word wins.
2. **The backup, by you** (step 2 below).
3. **The inventory**, read-only, written into your repository under `house/export/` as sorted files and
   `house/docs/inventory.md` as something you can read: areas and what is in them, integrations, automations and
   scripts with the naming pattern you use most, dashboards, apps, backups and users as counts. Facts only:
   names, ids, counts and whether a thing is on, off or unavailable; never a token, a password, a phone number,
   an address, or the inside of a `.storage` file. The agent says what it found in six lines and asks nothing yet.
4. **The first look**, also read-only, in `house/docs/first-look.md`: a short list of what is wrong, what is risky
   and what is only worth a notice, each with its evidence, the rule it comes from, and an offer. Things like:
   entities that have been unavailable for a day; automations that failed recently, or never ran; no backup this
   week, or none off the box; a second factor missing on an administrator; a long-lived token older than a year;
   a version behind stable; a secret in a YAML file; a port forwarded to the box; an automation that arms or
   unlocks with nobody in the loop. It ends with one paragraph said aloud: how many of each, the two or three that
   matter most, and that nothing was changed. **Each line is an offer.** "Leave it" is an answer to any of them.
5. **The setup block from evidence.** What the setup interview would have asked, the box has answered: version,
   hardware, address, backups. You are asked only what it cannot tell: who can log in to the router, where the
   off-box backup copy goes, the agent's budget. Then the network-and-backups checklist
   (`install/network-and-backups-first.md`), whose "Done when" list is still the gate; the lines the first look
   already proves are ticked from evidence and say so.
6. **Phase 0E closes.** The first CHANGELOG entry reads "Kit adopted on an existing house", with the dates and the
   line "nothing changed on the box". The agent tells you Phase 1 begins with your first request.
7. **The shorter interview, at your first request** (about twenty minutes instead of thirty). Every topic opens
   with what the box already told the agent, in one line for you to confirm ("you have 14 areas on two floors,
   named as on the box: right?"), and asks only what the box cannot know: who the people are, what must never
   break, when the house sleeps, who may be told what, what the agent may do by itself. Your house's own rulebook
   is written from the answers, as on the other paths, with two differences: `naming.md` records your existing
   scheme as kept beside the kit's scheme for new work, and the kit's build items (a notification router, health
   counts) are generated only where you have nothing equivalent; where you do, they are tidy-up rows.
8. **The ladder is the same ladder** (`levels.md`, "An existing house"). Nothing is skipped, but most of level 0
   and much of level 1 passes from evidence on the first day, and a check that reads for one of the kit's own
   pieces accepts your own equivalent once it is written down. A house that is years old can still be at level 0
   on day one; that is the honest reading, and it reaches level 1 in its first week of new work.

## The four steps you do by hand

These are yours until the agent runs. A chat app can walk them with you (`from-a-chat-app.md`). If the agent
will run on a computer instead of the box, do step 1 and then follow `install/agent-access.md`; the backup step is
the same.

1. **Install your runtime's app and sign in**: path B's steps 2 and 3 in `README.md`, exactly as written. Your
   house is already onboarded, so path B's step 1 is done.
2. **One backup, downloaded off the box.** Settings > System > Backups > make a backup (or pick the newest) >
   download it, to your phone or to a computer. That copy, made before the agent looks, is the level 0 line
   `E0-backup-first`; the agent records the date, never the file's path. **Then open it with an archive tool:**
   on a computer, or with an archive app on a tablet that can list a `.tar` file (the kit has not tested one). It
   is a `.tar` archive, and inside it you will see `backup.json` and `homeassistant.tar.gz`. Say to the agent one thing
   you saw inside. That minute is what the level 0 line "proven usable" (`L0-backup-proven`) means, and it may
   come later: if you downloaded the backup but have not opened it, say so. The agent records the download and
   leaves the proven line open until a backup is opened or a restore is rehearsed. It never marks done a step that
   did not happen.
3. **Say:** `Set me up with the starter kit on my existing house: <the kit's address>`. The agent says where it is
   running and what it can do there, asks how the kit should reach it and makes your private copy
   (`getting-the-kit.md`), then asks the one question above. Answer "lived-in".
4. **Answer the first session's questions and read the first look.** Say "leave it" to anything you do not want
   touched. When a step sends you out of the chat to type a line at the shell, come back the way your runtime
   resumes a conversation (`adapters/agents/<runtime>.md`, "Resuming a session"); once your private copy exists at `/share/<repository name>`, start every session with
   `cd /share/<repository name>` first.

## What the agent never does on this path

- Change, rename, move, delete or reload anything on the box during the first session; it reads.
- Read the contents of `.storage` files, or show them to you "to check": the export script parses the few it
  needs for counts and names, and the agent never sees inside. A file it cannot read that way is `unknown`.
- Treat your setup as wrong because it differs from the kit, or re-raise a difference you said stands.
- Mark a backup proven, or any other step done, from anything but what happened.
- Take a backup itself, or restore one: those are acts on the box, and they are yours.

## If it goes wrong

The first session changed nothing, so there is nothing to undo on the box. If the before-and-after comparison
reports a difference, the agent names it and the level 0 test does not pass until the CHANGELOG says what changed
and why. The repository the agent wrote is yours to keep or delete; your existing repository, if you had one, was
never touched.
