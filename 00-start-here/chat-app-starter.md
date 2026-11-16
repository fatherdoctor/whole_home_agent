# Whole Home Agent - the starter file for a chat app

*Built by `tools/chat-starter/build_starter.py` from 12 kit sources; do not edit by hand, edit the sources and
rebuild. For a chat app that cannot open web addresses: attach this one file and say
"Follow this file." Start with Part 1. A path such as `install/ha-green.md` names a Part below when it is
included; anything else lives in the full kit, which the agent on the box reads after the hand-off.*

Parts: 1 `00-start-here/from-a-chat-app.md`; 2 `adapters/agents/chat-apps.md`; 3 `interview/phase-0-setup-interview.md`; 4 `install/ha-green.md`; 5 `install/raspberry-pi.md`; 6 `install/mini-pc-bare-metal.md`; 7 `install/proxmox-vm.md`; 8 `install/network-and-backups-first.md`; 9 `install/voice-assistants.md`; 10 `00-start-here/your-first-automation.md`; 11 `adapters/agents/claude-code.md` (Install on the box and sign in); 12 `adapters/agents/codex.md` (Install on the box and sign in)

---

<a id="starter-part-1"></a>
## Part 1: `00-start-here/from-a-chat-app.md`

<a id="starter-part-1--starting-from-a-chat-app"></a>
### Starting from a chat app

*Status: written (KIT-CHAT0, 2026-11-10); made generic and corrected after its first dry run (KIT-CHAT0.g,
2026-11-10). The fourth way in: a person with a general chat assistant app, and no agent running on a Home
Assistant box yet. Walked once, in a stand-in dry run of start **4** (a box someone else set up, signed in from one
device; KIT-DRY.s2): its findings are folded in below. Starts 1, 2 and 3 have not been walked from a chat app yet.
For the chat assistant and the person together. If your chat app cannot open web addresses, `chat-app-starter.md`
in this folder is this page with the guides it needs, as one file to attach.*

<a id="starter-part-1--for-the-chat-assistant-reading-this"></a>
#### For the chat assistant reading this

You were handed this kit's address, or this page, by someone who wants to set up Home Assistant. You are the guide
for the first evening and, if no agent runs on the box, later evenings by hand. You have no shell, you cannot
reach their Home Assistant, and you may be able to open only a page or two of this repository. This page carries
the first evening and the return path below. Your limits, and what each
kind of chat app can do, are in `adapters/agents/chat-apps.md` (included in the starter file).

**You know nothing about this person until they tell you.** Do not assume their device (a phone, a tablet or a
computer), their hardware (none yet, a Raspberry Pi, a mini PC, a Home Assistant Green or Yellow, a virtual machine
on a server), who set it up, who else lives with them, or which AI plan they have. The examples on this page are
examples, not the default. Ask, then pick the path.

Rules for every evening:

1. **One step at a time.** Give one numbered step, wait for "done" (or a screenshot), then the next. When a step
   needs several screens read, ask for all of them in one message. Once the owner has completed and confirmed
   a proven sequence, you may offer to bundle the same sequence for another device with their agreement. Never bundle
   a step that would show a secret or pairing code to the chat. Stop at any unexpected screen and return to one step
   at a time.
2. **Believe their screen.** Menus move between Home Assistant releases. When the screen differs from this page,
   say so, check Home Assistant's official documentation if you can open it, and follow the screen.
3. **Keep secrets out of the chat.** Never ask for, and never ask to see in a screenshot: a password (Home
   Assistant's, the Home Assistant Cloud account's, a maker-app account's, the Wi-Fi's, the router's), a six-digit
   code, the two-step login QR code or its setup key, the backup encryption key or emergency kit, an access token
   (never screenshot the **Create token** dialog), or the house's remote address (the one Home Assistant Cloud
   gives, ending in `ui.nabu.casa`). If one is pasted or shows in a screenshot, say so and ask them to change it.
   Passwords are typed into the relevant app or account, never into the chat.
4. **The goal first, then the route.** Each step below names its goal. If the owner wants another way to reach it
   (another cloud, a USB drive, no router changes), offer the routes that meet the same goal with their cost and
   effort in plain words, and follow their choice.
5. **Router changes are optional.** Ask before any step that needs the router's admin page; the default is no.
6. **Anything off-site goes through Home Assistant Cloud first** (remote access, off-site backups, voice links),
   with its price said plainly as its own budget line, separate from the chat app's subscription. A VPN or a
   tunnel is the alternative for an owner who declines it.
7. **The owner decides.** Every rule here is a default. If they want the on-box agent now, follow
   [Jumping ahead](#starter-part-1--jumping-ahead). For other changes, say once, in a sentence, what the rule protects against,
   offer a lighter alternative once if there is one, then do what they chose and write it in the hand-off note.
   For an agent later installed on the box, the owner may choose
   [optional guard rails](../templates/agent-guard-rails.md) for either assistant. A chosen restriction means the
   agent cannot perform that action, for example operating a lock. These instructions are not a technical
   permission boundary and cannot loosen the runtime's enforced policy.
   If your chat cannot open the link, attach the guard-rails template separately; it is not in the starter file.
8. **The owner builds; the chat guides.** If an agent on the box is available, hand off with the note below.
   Otherwise offer to pause or return for hand-guided work using "Coming back without an agent on the box".
   You may explain a device plan or coach an automation from the kit's guides, one step at a time; the owner
   approves and performs every change. Never claim you clicked, deployed, read live state or saved house files.

<a id="starter-part-1--jumping-ahead"></a>
#### Jumping ahead

If the owner asks to go straight to the ChatGPT or Claude app, take this route instead of completing the usual
interview and setup first. If two-step login is half done, finish it (setup key saved and fresh sign-in confirmed)
or turn it off so it remains off; never leave it half on. It needs a running Home Assistant installation that
supports apps. Starting from nothing, finish the install in "Which start is yours" and onboarding first, then
return here; if apps are not supported, say so rather than claiming the app can be installed yet.

Do only these checks and steps before the app install:

Open [First change on a box already running](#starter-part-1--first-change-on-a-box-already-running).
Start with **Before the first backup or update, save any old Cloud backup** in that section.
Confirm the download of any wanted backup before the numbered steps.
Then follow steps 1-3: one local backup, then the first update.
An off-box copy of the new local backup can wait.
Save a wanted old Cloud backup first.
Do not repeat any check or step already completed and confirmed.
Otherwise follow that section and return here before installing the app.

Two-step login helps protect the account if someone learns its password. A copy off the box protects the backup if
the box or its storage is lost or fails.
On a box someone else set up, a new password and clearing old sessions and long-lived tokens keep a former helper
out before an agent with full access goes in.

Then go to the chosen app: use steps 1 and 2 in "The hand-off to the agent on the box" for Claude. For ChatGPT,
the kit has lab notes only; open the app's own documentation at the instructions page where you found the app
(its publisher's site or store page) and follow it. Do not guess its repository address or sign-in steps. Once an
agent is installed, continue with house rules in hand-off step 3 and the note in step 4; if it cannot be installed
yet, keep the note without claiming it was installed.

In the hand-off note, list each skipped step separately as `skipped at owner's request, <date>`; include two-step
login, the off-box copy, the new password, clearing old sessions and long-lived tokens, and any other setup or
interview steps if they were skipped. The agent on the box offers those steps later, without treating them as
completed.

<a id="starter-part-1--the-opening"></a>
#### The opening

If the owner names a later goal first, explain that setup comes first.
Save that later goal in the owner's words for the next evening.
Do not silently start it during setup.

Say what tonight is, then ask the four questions in one message. If the owner's first message already answered
some (their device, their plan, where Home Assistant is), do not ask those again: say what you took from it and ask
only the rest.

*"Tonight's goal: Home Assistant running and yours, with two-step login, backed up with a copy off the box. Then
the agent that runs inside Home Assistant takes over, if your AI plan has one the kit can install; otherwise tonight
ends with a short note you keep for later, and nothing new to buy. Without an agent on the box, we can keep going
by hand on later evenings: I explain, you click. I'll go one step at a time. Four questions first:*
1. *What are you using right now: a phone, a tablet or a computer? Is there a computer you could use for an hour
   if a step needs one?*
2. *Where is Home Assistant? Nothing yet / a machine with nothing on it yet (which one?) / a virtual machine on a
   server / already running (set up by you or by someone else).*
3. *Which AI plan do you have: Claude, ChatGPT, another, or none? And is there a monthly amount you want the AI to
   stay within?* (A limit on the AI plan does not cover Home Assistant Cloud, a separate fee; if they want to
   stay under a total, add the two and say so when Cloud comes up at the backup step.)
4. *How much time do you have tonight?"*

**What the plan answer means for tonight.** The kit has a walked install for one agent on the box: Claude Code, for
a Claude subscription. A ChatGPT plan that includes Codex has a Codex page with lab notes only, so tonight ends at
the hand-off note, kept for later, unless the owner uses the app's own documentation at the hand-off or under
"Jumping ahead".
Another plan, or none, keeps the note too. That is a safe stop for tonight;
returning to this chat-guided path is also an option. Say this now, not at the end.

**Time, roughly.** Reading what is already there: 15 minutes. The account made yours: 20 minutes. Backups and a
copy off the box: 30 minutes. Updates: 10 to 30 minutes each. Installing, if needed: a Green about 30 minutes, a
Raspberry Pi about an hour, a mini PC or a virtual machine one to two hours.
**On a box already running, allow time for the local backup and full update below before other changes.**
After that, the safe place to pause is once a backup is off the box (steps 3 and 4 of "Every start, tonight");
the household's phones can wait. Letting a brand-new release settle a few days is advice for later maintenance,
not a reason to leave this first update until last. Never pause in the middle of turning on two-step login.

<a id="starter-part-1--first-change-on-a-box-already-running"></a>
#### First change on a box already running

**Goal: a local recovery copy, then a fully current Home Assistant before changing anything else.** Any start
that is not a fresh install from the newest image takes this step first, including a box somebody else set up.
Read its version and installation type from the screens in start 4; sign in or finish required onboarding only
as needed to reach Settings. Before changing accounts, network settings, integrations or apps:

**Before the first backup or update, save any old Cloud backup.** Home Assistant Cloud keeps one backup, and a new
upload replaces it. The automatic backup before an update can go to Cloud too. Ask whether the house used Home
Assistant Cloud for backups. If it did and the owner may want that backup, the owner downloads it first: log in to
the [Home Assistant Cloud account](https://account.nabucasa.com/) in a browser, open **Cloud services > Backups**
and select **Download** (the official
[download steps](https://www.home-assistant.io/common-tasks/general/backups/#downloading-a-backup-from-home-assistant-cloud)).
Confirm that the file is saved: on an iPad it shows in the Files app with its size. Keep it private, off the box
and out of the chat. Until the copy is saved, make no backup and no update. Skip this if it was saved at the
welcome screen.

1. **One local backup first:** **Settings > System > Backups**. If the page shows both **Set up backups** and
   **Back up now**, choose **Set up backups** first. If only **Back up now** shows, use it.
   On first-time setup, save the encryption key or emergency kit privately off the box before continuing the wizard.

   On an iPad, download the emergency kit and open Safari's Downloads or the Files app to find the saved file.
   Keep it privately off the box. Store the key in the password manager and keep a second secure copy, such as paper.
   The copy icon puts the encryption key on the clipboard; it does not save a protected copy.
   Paste it only into the intended private password-manager entry, never into the chat input.
   After checking the saved copy privately, copy harmless text to replace the clipboard contents.
   Never paste the key into chat or share a screenshot of it.

   Then choose **Custom** and set a daily schedule, retention of 7 where supported, and include the **Share folder** where offered.
   If backups are already configured, use **Automatic backup > Configure backup settings** to check those settings.
   Confirm the existing emergency kit is kept privately off the box.
   Select a full manual backup and the local location, create it and wait for it to finish.
   Never paste or show the key to chat.
2. **Update the operating system first**, then **Home Assistant Core and the Supervisor**, then **everything
   else**, one update at a time under **Settings > Updates**. Update only components this installation has;
   Container has no Home Assistant OS or Supervisor. In each dialog leave **Back up automatically before
   updating** on where offered; otherwise make a fresh manual local backup before that update. Read the release
   notes, wait for each restart and reconnect, and confirm the installed version before the next update.
   If the Updates list shows the updates in another order, still do the operating system first. You cannot open
   the release notes: ask the owner to skim each one and say whether it mentions anything they use.
   **If an operating system update finishes, the update card disappears, but nothing restarted and System
   information still shows the old version**, the new system is waiting for a reboot. Open **Settings > System >
   Repairs**: an item saying a reboot is required has a fix button. Use it, then wait for the reconnect (about a
   minute) and confirm the new version before the next update. Do not power the box off.
3. Once no updates remain, return to Jumping ahead if following that route. On the usual path, start 4 returns to
   **Your account, made yours**; if you postponed onboarding's optional Wi-Fi step, do it first, then continue to
   the account. Do not repeat the backup or updates once completed and confirmed. If an update fails or the box
   does not return, stop there and use the official recovery instructions with the saved backup; do not interrupt
   power or start another update.

A fresh install from the newest image that is already current normally skips this step and follows the usual path.
For Jumping ahead, first follow **Before the first backup or update, save any old Cloud backup** above.
Confirm the download of any wanted backup before continuing.
You must still make the local backup in step 1.
If the box is already current, confirm no updates remain on the screen and continue at step 3.
Return to Jumping ahead after steps 1-3; do not repeat checks or steps already completed and confirmed.
Updating first makes later steps match today's screens. Home Assistant 2026.11 includes **Settings > Marketplace**
for community integrations, dashboard cards, themes and templates.
Existing content from the former community store migrates automatically.
Check any migration repairs, especially for custom repositories or YAML dashboard resources. A separate GitHub
connection may be needed for custom repositories. Apps are managed separately under **Settings > Apps**. Follow the
screen when a label differs. The [Marketplace guide](https://www.home-assistant.io/integrations/marketplace/)
explains the migration and its limits.
The local backup is the starting safeguard; on the usual path, the encrypted copy off the box and automatic
schedule still come later tonight. When jumping ahead, offer them later. A local backup alone does not finish the
backup goal.

<a id="starter-part-1--which-start-is-yours"></a>
#### Which start is yours

From the answer to question 2:

- **(1) Nothing yet.** Choose the hardware first, then go to start 2 or 3.
- **(2) A machine with nothing on it yet:** a Raspberry Pi, a mini PC, or a Home Assistant Green or Yellow.
- **(3) A virtual machine on a server** the owner or someone in the house already runs.
- **(4) Home Assistant already running, anywhere:** on any hardware or virtual machine, set up by the owner or by
  someone else, signed in to or still asking for its first account. A box someone set up and handed over is this
  start.

All four end at the same place: Home Assistant running, the owner account theirs alone with two-step login, backups
on with a copy off the box, and the hand-off note.

<a id="starter-part-1--1-nothing-yet-choose-the-hardware"></a>
#### 1. Nothing yet: choose the hardware

**Goal: a machine that will run Home Assistant OS (the kit's main install type), chosen on purpose.**

Offer these in plain words and follow the owner's choice (`00-start-here/choices.md` in the full kit has the
trade-offs):
- **Home Assistant Green** for "just works": it comes with Home Assistant installed, needs no computer at any step,
  and stays on a network cable (it has no Wi-Fi). Sold through the official Home Assistant site's list of sellers;
  check the price there rather than trusting a number here.
- **A small Intel or AMD mini PC** for "can grow": more power and disk, but it **needs a computer once**, plus a USB
  stick of 8 GB or more and a keyboard and screen, to write Home Assistant onto it.
- **A Raspberry Pi 5 (or 4)**, only if they already own one, ideally with an SSD; an SD card is for trying it out.
  It needs a computer once to write the card or drive.
- **A virtual machine**, only if a server (Proxmox, for example) is already running at home.

Then go to start 2 (or 3 for a virtual machine) once the hardware is in hand.

<a id="starter-part-1--2-a-machine-with-nothing-on-it-yet"></a>
#### 2. A machine with nothing on it yet

**Goal: Home Assistant OS on the machine's own drive, started on the home network, then onboarded.**

- **Home Assistant Green**, or a **Yellow** that came with Home Assistant installed: plug in the network cable (to
  the router or a switch next to it), then the power. Wait several minutes: the first start downloads the latest
  Home Assistant. Guide: `install/ha-green.md` (in the starter file). For a Yellow without it installed, follow the
  official Yellow documentation; the kit has no Yellow guide.
- **Raspberry Pi:** `install/raspberry-pi.md` (in the starter file). Writing the card or drive needs a computer once.
- **Mini PC:** `install/mini-pc-bare-metal.md` (in the starter file): firmware settings, writing the image, first
  start. **This needs a computer once.** Home Assistant OS has no installer of its own: it is written onto the
  drive from another computer, and a phone or tablet cannot do that. Pick one before starting: the owner's own
  computer (Windows, Mac or Linux) for about an hour; or a helper's computer, or the helper does this part and hands
  the machine over (then it is start 4). The linked guide still needs that computer and a physical USB stick.
  The first start needs **a network cable to the router**; Wi-Fi comes after onboarding (below).

Where a guide says "your computer", any device's browser or the Home Assistant app does the same job once Home
Assistant is running. Where it says to find the address and reserve it in the router, skip that unless the owner
chose to log in to the router (rule 5): the app and `homeassistant.local` find the machine by name.

Then **Onboarding**, below.

<a id="starter-part-1--3-a-virtual-machine-on-a-server"></a>
#### 3. A virtual machine on a server

**Goal: Home Assistant OS in its own virtual machine, started, then onboarded; the owner knows who runs the server.**

The guide is `install/proxmox-vm.md` (in the starter file) for Proxmox; other hypervisors follow the official Home
Assistant "Alternative" installation page with the same requirements (UEFI, Secure Boot off, enough memory and
disk). The steps happen in the server's admin page, by whoever runs it; the chat walks them one at a time. Say
three things plainly before starting:
- Whoever controls the server controls the house's machine: its power, its snapshots and its updates. If that is
  not the owner, the owner should know who it is and how to reach them.
- A backup kept on the server's own disk is not off the box. The off-box copy below still applies.
- Home Assistant OS is the kit's main install type. A Container, Core or Supervised install still gets the account,
  two-step login and backup steps below; Container and Core have no Apps, so their hand-off is to an agent on a
  computer (path A), not an app.

Then **Onboarding**, below.

<a id="starter-part-1--4-home-assistant-already-running"></a>
#### 4. Home Assistant already running

**Goal: confirm what is already done, from the screen, and make it the owner's.**

1. **Open it.** Use the Home Assistant app (free in the app store) or a browser, at the address they have. A new
   install answers at `http://homeassistant.local` (port 80; adding `:8123` redirects there). An install made some
   time ago, or a customized one, may answer only at `:8123` on the end. Port 80 is normal, not a sign of a proxy or
   a virtual machine. A numeric address (four numbers with dots) can change; if a saved one stops working, try
   `homeassistant.local` or let the app find the box on the home network. The app may ask for notifications (allow)
   and location (fine to say "while using" or "not now"; who the house tracks is decided later).
   Ask first what the owner sees: **a welcome screen or a dashboard**. Do not assume "a friend installed it"
   means it is set up.
   - **A welcome screen** (the button is usually **Create my smart home**, with a link to restore from a backup
     beside it): onboarding was not done. A reset or replacement box shows the same screen. Before either button,
     ask: *"Is this a new house, or do you want a saved house back from a backup?"*
     - **A new house:** do not restore; go to **Onboarding** below. This is the usual answer for a box someone
       else installed.
     - **A saved house back (a recovery):** do not choose **Create my smart home**. If the house backed up to
       Home Assistant Cloud, save a private copy of that backup first: the owner logs in to the
       [Home Assistant Cloud account](https://account.nabucasa.com/), opens **Cloud services > Backups**, selects
       **Download** and confirms that the file is saved. Then follow Home Assistant's
       official [restore steps](https://www.home-assistant.io/common-tasks/general/backups/#restoring-a-backup)
       from this screen. The owner types the backup's encryption key from the emergency kit into the restore
       screen, never into the chat. Protect the saved backup until the restored house runs: set up no new backups
       and add no backup location before then. Home Assistant Cloud keeps only the latest backup, so a new upload
       replaces the saved one. After the restore, sign in with the restored house's owner account and continue
       at step 2 below.
   - **It asks to sign in:** use the login they have.
2. **Read what is there.** Ask for these three screens in one message (a screenshot each, or read aloud):
   - **Settings > System > Repairs** > the three-dot menu > **System information**: the Home Assistant version,
     installation type, hardware ("board"), and whether it is a virtual machine. A virtual machine is start 3's
     case: say its three points out loud. Home Assistant OS is the kit's main type. Container and standalone Core
     have no apps; do the account, two-step login and backups without the Apps steps, and hand off to an agent on
     a computer (path A). Supervised has been unsupported since 2025.12 but includes apps; check that Apps is
     available on this installation and keep the on-box app route if it is. If it is unavailable, use path A.
     The [installation-method notice](https://www.home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/)
     explains the support status and migration choices.
   - **Settings > System > Network**: Wi-Fi or a cable, and the address. An interface named `wlan0` is Wi-Fi; one
     named `end0`, `eth0` or starting `enp` is a cable. If it says cable and the owner thought Wi-Fi, a cable is
     fine (steadier): say what was found and go on.
   - **Settings > People**: the people and users. Whose name is on the account and who
     else has a login. The page may show no **Owner** label. Then the account made at onboarding is the owner:
     if the owner made it tonight or can say they did, that is settled. If someone else onboarded the box, open
     **Settings > People > Users** (turn on **Advanced mode** in the profile if the tab is missing) and read which
     account is marked **Owner**. Users with a check in the **System** column belong to Home Assistant itself.
     If that column is hidden on a narrow screen, open the user: its editor says **System user**.
     Leave those system users alone; examples include Supervisor, Home Assistant Content and Home Assistant Cast.

   The chat writes down what it saw and marks those install steps done "from the screen, <date>". Anything that
   differs from "installed, on the network, nothing else" is said out loud before going on.
3. **What is installed:** on a system with apps, open **Settings > Apps** (called **Add-ons** before 2026.2) and
   note the installed apps, such as a Matter server; otherwise skip that screen. On 2026.11 or later, open **Settings > Marketplace** to see community
   integrations, cards, themes and templates; leave them in place. On older releases, use HACS if it is already
   installed to see those community items; do not install it just for this check. The Marketplace is built in on
   2026.11, so do not install HACS there. Its optional GitHub device sign-in is used for custom repositories; keep
   the code out of chat. This is separate from a token for cloning a private repository. The
   [Marketplace guide](https://www.home-assistant.io/integrations/marketplace/) explains when it is needed.
4. **If a "discovered" banner offers devices, skip it for now.** Leave the cards alone; do not tap **Ignore**,
   which hides the card. If one was ignored, open **Settings > Devices & services**, use the filter menu and choose
   **Show ignored**, then re-enable it; follow the screen if the label differs. Naming devices on purpose comes later,
   with an agent on the box or the hand-guided return path below.

Then go to **First change on a box already running**, above: make the local backup and complete the updates before
**Your account, made yours**. Once confirmed, continue to the account without repeating those steps.

<a id="starter-part-1--onboarding-starts-2-3-and-4-if-it-asked-to-create-an-account"></a>
#### Onboarding (starts 2, 3, and 4 if it asked to create an account)

**Goal: the owner account, in the owner's name, and the house's location.**

1. Open the Home Assistant app and let it find the box, or open `http://homeassistant.local` in a browser (port 80;
   an older install may need `:8123`). If neither finds it after a few minutes, the address is on the machine's
   screen (a mini PC), in the server's admin page (a virtual machine), or in the router's list of connected devices
   (only if the owner is willing to log in to the router).
2. Choose **Create my smart home**, for a new house only; a recovery uses the restore link instead (start 4,
   "A welcome screen"). Create the owner account **in the owner's own name**, with a password saved in
   the password manager of the device they are using (or the one they already use). Set the home location, time
   zone, units and currency. The screens come in this order: account, home location (a map with a search box),
   then sharing. Check the country, time zone, units and currency it fills in; the defaults can be UTC, euro and
   metric.
3. Choose what to share with the project (all optional; the kit has no preference, leaving them off is fine).
4. **Skip the discovered devices for now**, unless one is essential. Leave the cards alone; do not tap **Ignore**,
   which hides the card. If one was ignored, open **Settings > Devices & services**, use the filter menu and choose
   **Show ignored**, then re-enable it; follow the screen if the label differs.
5. **Moving to Wi-Fi** (optional; a cable is steadier). Start 4: skip this Wi-Fi step until after First change;
   return here after its local backup and updates, or keep the cable. **Settings > System > Network**, open the
   Wi-Fi interface (often `wlan0`), choose **Wi-Fi**, search, pick the network, type the Wi-Fi password into Home Assistant (not the
   chat), save. Wait a minute, unplug the cable, reopen the app: it finds the box again by name. No Wi-Fi interface
   means no Wi-Fi Home Assistant can use; keep the cable. A Green has none.

For start 4, if First change is not yet complete, then go to **First change on a box already running**, above,
before the account or optional Wi-Fi changes. After the backup and updates are confirmed, return to step 5 if
wanted. If First change is already confirmed, go to **Your account, made yours**; do not repeat it. Starts 2 and 3
go directly to **Your account, made yours**.

<a id="starter-part-1--your-account-made-yours"></a>
#### Your account, made yours

**Goal: only the owner can sign in as the owner, and nobody else is locked out by surprise.** Do these in order.
Home Assistant has no button that moves the Owner role to another account, which is why a helper makes the owner
account in the owner's name. For an account the owner made themselves at onboarding tonight, skip to step 5.

1. **Others who use the owner login need their own first.** If family or a helper have been signing in as the
   owner, changing the password in step 3 locks them out. Ask now: "just me", or "they get their own login"?
   To make one: **Settings > People > Add person**, their name, turn on **Allow person to login**, a username and a
   first password, and **Administrator** only if they should be able to change everything. Give them the first
   password in person (not by text); they change it in their own profile. "Wanted later" is a fine answer: write it
   in the note. A second administrator login is also a way back in if the owner ever loses their authenticator.
2. **An owner account not in the owner's name** (the helper's name, or a generic "owner"): **Settings > People >
   Users** (turn on **Advanced mode** in the profile if the tab is missing), open that account, change the display
   name to the owner's, and the username too if the screen offers it. The username is what they type at the next
   sign-in: save it with the password.
3. **A new password.** Profile (the name at the bottom of the side bar) > **Security** > **Change password**:
   save a new password in the device's password manager, then submit it in Home Assistant.
   If it asks **Do you want to log out from all devices?**, explain the choice before answering.
   To sign out other sessions, choose **Yes**. This signs out every device, including this one.
   Sign in again with the new password.
   **No** keeps the existing sessions signed in.
   Recommend Yes for this takeover and let the owner choose.
   On Home Assistant 2026.11 it may not ask; then other sessions stay signed in.
   Either way, review sessions and long-lived tokens in step 4.
   Then delete the message or note that carried the old password.
4. **Who is still signed in.** Same page, the list of signed-in sessions (**Refresh tokens**) and **Long-lived
   access tokens**. Ask the owner to read the list back (names and last-used dates, never a token). Every session
   or token that is not the owner's own device gets deleted: a family member's browser from the hand-over, a
   helper's computer, a token someone made. Sessions can all show the same name (the box's address); then
   compare creation times: one made before the owner first signed in belongs to whoever onboarded the box.
   Leave the one this device is using (if the screen does not mark it,
   ask before deleting and delete it last). Long-lived tokens keep full access through a password change and are
   easy to forget; delete any the owner did not make.
5. **Two-step login.** Explain it first: after the password, Home Assistant asks for a six-digit code from an
   authenticator app. On the same page, open **Multi-factor authentication modules**. If Authenticator app is
   already enabled, do not disable or reconfigure it. Confirm a fresh sign-in in a private window or on another device before closing
   this session, and check that the owner has recovery material (the setup key or another administrator login); do
   not ask them to show it to chat. If it is not enabled, select **Authenticator app** > **Enable** and follow
   these steps:
   - **Save the setup key first**, before entering any code: the text shown below the QR code. It goes in the
     password manager and one other place that is not the box (paper in a drawer counts). Home Assistant gives no
     recovery codes; this key is how the authenticator is rebuilt on a new device. Keeping it in the same password
     manager as the password is convenient but makes that manager the one thing to protect: the owner's choice.
   - **The QR code and the setup key are secrets:** no screenshot of this screen for the chat.
   - **The authenticator:** the device's own password manager often makes these codes (on Apple devices the
     Passwords app; on others an authenticator app from the app store). **With only one device**, do not scan: copy
     the setup key into the authenticator on that same device. With two, scan the QR code with the other one.
   On an iPad, copy the key by pressing and holding it, keeping the Home Assistant tab open; in the Passwords app
   open the account's entry, edit it, add a verification code by entering the setup key, then return to the tab
   for the six digits. Follow the screen if a label differs.
   - Type the six digits it shows. **If the code is refused**, wait for the next one (they change every 30
     seconds) and check that the device sets its clock automatically.
   - **Confirm a fresh sign-in works before closing this session:** a private browser window or another device,
     password, then code. Losing every authenticator with no setup key and no second administrator login is
     recovered only by the agent on the box or a helper at a terminal.
6. **The helper's own account,** if they made one: remove it (**Settings > People > Users** > the account >
   **Delete user**), or keep it as a named support account. If kept, untick **Administrator** unless they should be
   able to change everything; it can be deleted at any time.

**A box on Wi-Fi is normal.** What to watch: a good signal (not in a cabinet behind the TV), and an address that may
change unless the router keeps one for it. The app and `homeassistant.local` find the box by name; reserving the
address is optional, later, only if the owner chooses to log in to the router (`install/network-and-backups-first.md`,
section 1).

<a id="starter-part-1--every-start-tonight"></a>
#### Every start, tonight

**Goal: backed up with a copy off the box and the emergency kit kept in two places.** An existing install has
already had its local backup and full update in "First change on a box already running"; a fresh install is
already current. These steps now finish the ongoing backup protection. These are the parts of
`install/network-and-backups-first.md` (in the starter file) that any device can do.
What counts tonight is that goal: the box found by a stable name or address, and a backup kept somewhere other than
the box. Two lines of that file's "Done when" list read differently on this path: the address is reserved in the
router only if the owner chose to log in to it (otherwise `homeassistant.local` is the stable name), and the
downloaded backup may be on a phone or tablet instead of a computer. The agent on the box checks the rest again.

1. **Backups.** Open **Settings > System > Backups**. For first-time setup, choose **Set up backups**, save the
   **backup encryption key** (the "emergency kit") in the password manager **and** one other place off the box,
   then choose **Custom**. Use the iPad save-and-clipboard instructions in First change step 1 above.
   Follow the screen if a label differs. **Recommended** saves immediately with three copies and excludes the Share folder.
   If setup already exists, open **Automatic backup > Configure backup settings**; the first local backup above may
   already have completed setup. Check the existing emergency kit is kept privately off the box. Without its key no
   encrypted backup can be restored. In either route, confirm daily, at a time the box is on (on a virtual machine someone else runs, ask them whether the server stays on overnight and note the time you chose); set retention to 7
   where the location supports it. What to back up: Home Assistant's
   settings and history, and the **Share folder** ticked if the wizard offers it (Home Assistant OS and Supervised do; the agent's house folder will live there, and these
   backups are its off-box copy); media off unless it is needed. Locations: this system for now; the off-box one
   comes in step 2. On a virtual machine, "this system" is the server's disk. The first local backup and updates
   on an existing install were done before this section; do not mistake them for the off-box copy.
2. **A copy off the box: Home Assistant Cloud first.** It gives encrypted off-site backups (scrambled with the key
   from step 1, so the copy is useless to anyone else), remote access from a phone without opening anything on the
   router, and voice assistant links, for a fee of its own. Its dated price is in
   `install/network-and-backups-first.md`, section 2 (in the starter file); the current one is on **Settings > Home Assistant Cloud** and at
   nabucasa.com/pricing. Say it as its own budget line: it is not part of the AI subscription. Only on the owner's
   yes:
   - **Signing up changes nothing in an existing Alexa or Google Home setup.** Their devices, routines and voice
     commands keep working as they are. Linking Home Assistant to a voice assistant is a separate, later choice
     (`install/voice-assistants.md`, in the starter file).
   - **The sign-up** (**Settings > Home Assistant Cloud**) asks for an email, a password for the Cloud account
     (different from Home Assistant's, saved separately), an emailed confirmation, and a trial or a payment as its
     page shows.
   - **Remote access is off on a new setup until the owner turns it on.** An older setup may already have it on.
     After signing in, ask the owner to read the **Remote access** toggle on the Home Assistant Cloud page. Turn
     it on only if the owner wants to reach the house from outside; for backups only, leave it off. Two-step login
     comes first either way. The remote address it shows stays out of the chat.
   - Home Assistant Cloud's Alexa link does not require **Remote access**. Keep Cloud signed in and configure Alexa separately.
     [Nabu Casa documents the separate Cloud features](https://support.nabucasa.com/hc/en-us/articles/26508882007581-Remote-access-Security-aspects).
     The [official Remote access action guide](https://www.home-assistant.io/actions/cloud.remote_disconnect/) confirms that voice assistants keep working when it is off.
   - If the Cloud account already holds a backup of a house the owner may want back, and it is not saved yet,
     download it now, before the next step: the next upload replaces it. Use **Settings > System > Backups**,
     select the Cloud backup, then under **Locations** the three-dot menu > **Download from this location**; or
     the Cloud account route in **First change on a box already running**. Keep the file private.
   - Then add **Home Assistant Cloud** as a backup location. It holds **one** backup of up to 5 GB, the latest; a
     backup larger than that needs less in it (media off, large files out of the Share folder) or another location.

   If the owner would rather not pay, the alternatives (a cloud drive, a network drive, a computer that is usually
   on) are in the same file, section 3; the goal is the same: an encrypted copy off the box, made automatically.
3. **One backup in hand.** **Backups > Backup now**, with the off-box location ticked. Wait for it, then open that
   backup in the list: its details show where it is stored. Seeing the off-box location there (for example Home
   Assistant Cloud) means the copy reached it. A hand copy to a device or computer is best kept encrypted;
   keep the emergency kit separately and privately off the box: its key is needed to restore the copy.
   **Normally the Download in a backup's menu gives a decrypted file, with no encrypted choice offered.** When the
   backup uses the key already set on the box, Home Assistant decrypts it on the fly and downloads it straight
   away (Home Assistant's
   [backup page](https://www.home-assistant.io/common-tasks/general/backups/#downloading-your-local-backups);
   the frontend code behind it,
   [download_backup.ts](https://github.com/home-assistant/frontend/blob/20261028.5/src/panels/config/backup/helper/download_backup.ts#L43)).
   The recommended copy stays encrypted: Home Assistant Cloud, or the Google Drive location (step 2's
   alternatives; `install/network-and-backups-first.md`, section 3, route B, about 20 minutes, free), neither of
   which needs a download. A decrypted file holds the house's settings and any saved logins, so warn once, in one
   plain sentence, that anyone who gets that file can read them. If the owner still wants that hand copy in iCloud
   Drive or another store they trust, that is their choice: go on without arguing, and add "off-box hand copy,
   decrypted, <date>" to the note's `Owner's choices:` line. Only when the key is missing or wrong does a dialog open, and
   its link **download the backup encrypted** gives the encrypted file; use that link only if you see that
   dialog, and never change or remove the key to make it appear. Delete a decrypted copy made only to check the
   archive. Until a route is working the off-box step stays pending (step 4).
   Confirm the copy reached the off-box location; a completed download alone does not prove it can be restored.
   **Proof on a phone or tablet alone:** the kit has no tested way to open the downloaded `.tar` file there. The
   proof needs a computer with an archive tool, or an archive app on the tablet that can list a `.tar` file's
   contents (`backup.json` and `homeassistant.tar.gz`). Until the owner opens it that way, or does a restore drill,
   the note says the proof is pending; that is fine for tonight. The first
   **scheduled** backup reaching the off-box location is checked later by the agent on the box, and the note says so.
4. **The safe pause point.** A copy is off the box. Stopping here is fine: write the hand-off note (below) now, with
   phones "pending" and the actual update outcome. If no copy is off the box tonight (the owner declined Cloud
   and no encrypted off-box route is working yet), the pause point is the one before that step: the local backup made,
   updates done, two-step login confirmed, the note saying plainly `off-box: not yet` and why. Say it is a
   stopping point for tonight, not a finished backup.
5. **Confirm the update outcome.** Record the versions checked after the first update, or that the fresh image
   was already current. If that first update is unfinished, return to that step before installing the agent;
   do not call it optional or mark it done. A backup-before-update copy on the box does not prove an off-box copy.
6. **The household's phones** (optional tonight). Each phone that should hear from the house gets the Home
   Assistant app, signed in by its own person. Name each device **for its role, not its owner's name or model**
   (`Owner phone`, `Kitchen tablet`): the name ends up in the house's automations and notes.

<a id="starter-part-1--the-hand-off-to-the-agent-on-the-box"></a>
#### The hand-off to the agent on the box

**Goal: an agent that runs inside Home Assistant, with the full kit, picks up where tonight stopped.**

With a Claude subscription: steps 1 to 5 (`adapters/agents/claude-code.md`, "Install on the box and sign in", in
the starter file). With a ChatGPT plan, another plan or none: skip steps 1 and 2, which are Claude-only. Do step 3
whenever any on-box agent is installed. For ChatGPT, the kit has lab notes only: use the ChatGPT app's own
documentation at the instructions page where you found the app, then step 3; do not guess its repository or
sign-in steps. If no on-box agent is installed yet, record the rules as not yet installed and keep the note in
step 4 (a notes app is fine): the box is installed and backed up on the box, and the account is the owner's unless
those steps were skipped. You can pause here or use "Coming back without an agent on the box" on a later evening.
No extra subscription is required for that path.
When an on-box agent becomes available, return to step 3 and give it the hand-off and latest progress notes.

1. **Add the agent's app.** **Settings > Apps > Install app** > the three-dot menu > **Repositories**. Add the
   repository (the web address of the agent's app collection) the Claude Code page names, then install and start it.
2. **Sign it in.** This one step happens in a **terminal**: a black text window inside Home Assistant, the app's
   **Open Web UI**. Type `claude` and press Enter; it shows a link. Open the link in a browser, sign in to the Claude
   account, and it gives a code. Go back to the terminal and paste the code, or type it (it is short), then press
   Enter. If paste and typing do not work in that window on a phone or tablet, do this one step from any computer's
   browser, signed in to Home Assistant. The sign-in is stored on the box and travels inside its backups, so from
   now on a backup file is a secret: keep it where passwords are kept.
3. **Choose and install house rules.** Recommend **Careful start** for a new owner: the assistant says what it will
   change and waits for yes each time. **Direct** treats an explicit request as the go-ahead and reports what changed;
   it still asks when unclear, beyond the request, or before deleting, restarting, firmware or version changes.
   Both require backup before edits and a configuration check after configuration changes. The owner chooses.
   Give the agent the kit's address in its app, then ask it to open `templates/house-rules.md` from that address.
   Add only the chosen set to its existing instructions file: `/config/AGENTS.md` for the ChatGPT app or
   `/config/CLAUDE.md` for the Claude app when its working folder is `/config`; otherwise use the instructions
   file in its working folder. Ask it to read the rules back in a new session. Confirm the read-back before treating
   the rules as installed; if the agent cannot do it, pause and help the owner follow the template. Optional extra
   limits and changing the choice later are explained in
   `00-start-here/loosening-your-rules.md`. Do not paste secrets into instructions or chat.
4. **The hand-off note.** The chat writes a short note in this shape, with what tonight actually did, and no
   passwords, codes, tokens, keys or addresses:

   ```
   Set me up with the starter kit: <the kit's address, or "no address: the kit's starter file is attached below">
   Hand-off from a chat app (<date>)
   Start: nothing yet, <hardware> installed tonight | <hardware> installed tonight | virtual machine on a server (run by <owner | someone else>) | already running (set up by <owner | someone else>)
   Done, from the screen: <version>, <installation type from System information>, <hardware or virtual machine>, on <Wi-Fi or cable>, onboarded
   Installed apps found: <none | community store | Matter server | ...>
   Owner account: in the owner's name; new password <yes/no>; old sessions and tokens reviewed <yes/no>; two-step login <on/off>, fresh sign-in checked <yes/no>
   Other logins: <none | made for <role>, administrator yes/no | wanted later>
   Helper's account: <none | removed | kept as a support account, administrator yes/no>
   Backups: automatic <yes/no>, share folder <yes/no>, off-box <Home Assistant Cloud | other | not yet>
   Off-box proof: tonight's manual backup reached <location kind | nowhere yet>; first scheduled one not yet checked
   Remote access: <off | on through Home Assistant Cloud | not set up>
   Emergency kit and setup key: <in two places | one place | not yet>
   Backup evidence: current off-box copy <Cloud confirmed | other location confirmed | not yet>; downloaded copy <yes | no | not attempted>
   Opened archive or restore proof: <owner confirmed | pending>
   Updates: <done | pending>. Phones: <done, named by role | pending>
   Router: <not asked | the owner will not log in to it | the owner will log in to it>
   Agent plan and budget: <Claude | ChatGPT | other | none>; <the owner's words, or "not discussed">
   House rules: <Careful start | Direct | not yet>; extra limits: <none | which | not yet>
   Owner's choices: <none | each best practice the owner took a weaker way on (for example a decrypted backup copy, one emergency-kit place, a forwarded port), the risk said once, <date>>
   Skipped steps: <none | each skipped step (two-step login, off-box copy, new password, clearing old sessions, clearing long-lived tokens, other): skipped at owner's request, <date>; stopped for safety: <step>, <why, and what is needed to resume>>
   Git: <none yet; the house folder lives on the box | private copy at <host>, made for a cloud session>
   What the owner wants the house to do first: <their words>
   Rules the owner changed: <none | which, in their words>
   Open questions: <anything left>
   ```

   An owner with only the attached starter file has no kit address: write the first line as shown and the agent on
   the box asks them for it. The owner copies the note and pastes it as the **hand-off message** to the agent on the box. The agent downloads the kit
   itself from the address on the first line, saves the note, checks each line against the box, and continues from
   there (`AGENTS.md`, "Arriving from a chat app").
5. **If the hand-off happened, the agent on the box leads.** Keep the conversation and latest progress note to
   look back on. Without that agent, keep the note and continue by hand below whenever you choose.

<a id="starter-part-1--coming-back-without-an-agent-on-the-box"></a>
#### Coming back without an agent on the box

You can keep going from a chat app, including with a ChatGPT-only plan. No agent installation or new subscription
is required. Start a fresh chat with this kit's address. With no address, attach the starter file to the new chat
again. Paste any first-evening hand-off and progress notes you have into it.
Say what you want to do next and how long you have. The chat says first: **"I cannot see or change your box.
You do every step; I explain and check what you read back."** A new chat may remember nothing.

1. **Resume, do not restart.** Read the notes before asking the opening questions again. Confirm what has changed
   since their date and the next unfinished step. An older note may lack a field: ask only what this step needs,
   mark the rest "not recorded", and never turn a missing answer into done. A note's pairing route is a claim to
   recheck for that device, not proof that the next device uses the same route. On a first return, having no
   progress note is fine: start one below using any hand-off and what the owner remembers, marking unknowns
   "not recorded" rather than inventing completed work.
2. **Agree one small goal, limits, test and undo.** Ask before the owner changes anything. Confirm a current
   backup first using [network and backups](#starter-part-8); keep the emergency kit
   privately off the box. Do not begin a change that cannot be left safely within tonight's time.
3. **Use a kit guide as the plan.** For devices and familiar voice commands, use
   [Keep familiar voice control](#starter-part-9): inventory first, check each device's connection
   clues, agree its route and preserve routines. For several devices of the same brand, ask for their connection
   clues together, but record and check each device separately. For a maker's supported-model list, ask the owner
   to read the list once and report whether each model appears: opening each model-support page costs a round trip.
   Do not assume a model is supported from its brand or another model; leave it unknown until checked.
   For a first small automation, use
   [Your first automation](#starter-part-10): the owner makes a safe helper, script or automation in the
   editor and tries it. Read the relevant guide before offering its next step; do not invent a new route from
   memory when the guide cannot be opened. Attach the starter or the specific guide if needed.
   **If the kit has no guide for the wish, say so plainly.** Use it to introduce the owner's own board and
   [build lane](../principles/board-and-lanes.md): an agent works one approved card at a time. Ask what outcome
   they mean and offer to keep the wish as an open card in this progress note, their first if none exists, with
   the unknowns still open. Moving to an agent on the box makes that build lane possible; the chat can explain
   and draft the proposal for the owner to save, but cannot run a lane or claim work started. The later agent
   reads the note and works the card the kit's way: clarify, offer options with costs, follow the owner's choice,
   agree tests and undo, and admit what is still unknown. No missing guide is a promise that a build will work.
4. **One instruction, then the owner's result.** The owner clicks and reports the screen and physical result;
   the chat cannot inspect the box, run actions or read a trace itself. Ask the owner to read the relevant saved
   settings and trace. Record tests as "owner observed", "failed" or "not checked", never as independently
   verified by the chat. Preserve the kit's limits on safety devices and messages. No test sends or speaks to
   another person. If a screen differs, consult the guide's current official reference or stop for that evidence.
5. **Save progress before stopping or changing devices.** Keep the note below in a private notes app or file
   under the owner's control; do not depend on chat history. If a guide asks for a house board row or CHANGELOG
   before that folder exists, the owner keeps its goal, status, checks and undo in this note for later transfer.
   This does not claim a profile, board, readiness check or house file has been created. Stop after a complete
   device/test/undo record, or before a risky step, rather than halfway through removing a working voice path.

Copy and update this short note at every safe stop. Use device roles or labels, never personal names, addresses,
passwords, keys, tokens, Matter pairing codes or QR codes. Keep the original hand-off note alongside it.

```text
Chat-guided progress (<date>; kit: <public kit address | no address: starter file attached>)
Agent on the box: none | installed but not handed off | hand-off complete
Goal and time for this or next session: <one small goal; time available>
Done: <steps completed; date; owner-observed result>
Not checked or failed: <what, and why>
Next: <guide, section and first unfinished step; safe pause state>
Device routes: <one line per device role: clue seen, route chosen, done/pending>
Device names: <one line per device role: Home Assistant name; voice name; not checked if unknown>
Rules and choices: <owner's limits and exceptions; no change implied by silence>
Backup: <date; location kind; owner confirmed completion; key kept off box yes/no>
Change list (one line per change): <date; device role or lesson; what owner changed; actual test result; undo>
Open card: <wish beyond the kit; intended outcome; owner choice pending; unknowns; not started>
Open questions: <missing facts; guide or screen needed>
```

When an agent later runs on the box, paste **both notes**, if available, as its first message with the kit's address.
Ask it to read them before doing anything, check their claims against the box, resume at the unfinished step, and
carry the change list with its undo into the house CHANGELOG and pending work into the backlog. It must not repeat work
just because the chat could not save house files, or treat a route recorded for one device as another's route.

<a id="starter-part-1--git-can-wait"></a>
#### Git can wait

During onboarding, the owner creates their own **free GitHub account**: it can hold a private copy of the
house's files and sign in to tools that use GitHub. The owner signs up themselves in GitHub, keeping their
password and recovery details out of chat. Nothing breaks without it tonight: if they defer it, record that
and continue with the local house folder and backups. GitHub's
[account creation guide](https://docs.github.com/en/account-and-profile/how-tos/account-management/creating-an-account-on-github)
walks the sign-up. No GitHub token or shell is needed for this chat path.

The agent on the box keeps the house's folder (its profile,
its change log, every file it writes) on the box under `/share`, with its history of changes kept locally. The
automatic backups include it (the **Share folder** box above), and the off-box location carries those backups off
the box. A private repository at a code host comes later, and only if the owner wants it; the agent walks it from
the box, and nothing about it needs a shell on the owner's device.

<a id="starter-part-1--where-to-start-and-when-to-move-to-the-box"></a>
#### Where to start, and when to move to the box

Three places can run the kit. Only the last one can reach the box, so the kit moves there as soon as it can.

- **A plain chat (ChatGPT, Claude or another) with the kit's address.** This page, tonight. **No GitHub account.**
  It reads and explains; the owner does every step, including on later evenings with the saved progress note.
- **A cloud coding agent** (Codex in the cloud, Claude Code on the web). **Needs a GitHub account** and the owner's
  own private copy of the kit: on the kit's GitHub page in a browser, **Use this template** > **Create a new
  repository**, set it to **Private** (if that button is missing, **Import repository** in GitHub's **+** menu makes
  the same private copy from the kit's address). It can write the house's files there, but it runs on the vendor's
  computers, **not on the home network, so it cannot reach the box** either: the owner still does and reads back
  every step on the box. Only worth it to start the house's files before the agent on the box is installed.
- **The agent's app on the box** (the hand-off above). **No GitHub account.** It reads and changes the box itself,
  keeps the house folder on the box under `/share`, the automatic backups carry that folder, and the off-box
  location carries the backups. GitHub stays optional: one more off-site copy, later.

When its agent's app is installed and signed in, hand off to the box with both notes; later evenings then
start there. Until then, use the hand-guided return path above.

If a private copy was made for a cloud session, say so on the note's **Git** line (`private copy at <host>, made
for a cloud session`). The agent on the box then offers two choices: use that copy as the
house folder (it brings the copy onto the box, with whatever the cloud session wrote), or start the house folder fresh
on the box and keep the copy only as an extra off-site copy. Either way, from then on the house's files change on the
box, not in the cloud session.

<a id="starter-part-1--what-the-chat-app-cannot-do"></a>
#### What the chat app cannot do

- See the box. It knows only what the owner tells it and what the screenshots show.
- Remember an earlier evening in a new conversation; the owner supplies the hand-off and latest progress notes.
- Open more than a page or two of this repository, in some apps. If it says it cannot read a file this page
  names, give it `chat-app-starter.md` instead (download it from this folder and attach it).
- Run anything. Every step is the owner's; the chat reads, explains and waits.

---

<a id="starter-part-2"></a>
## Part 2: `adapters/agents/chat-apps.md`

<a id="starter-part-2--chat-apps-setup-and-later-evenings-by-hand"></a>
### Chat apps (setup and later evenings by hand)

*Status: notes (KIT-CHAT0, 2026-11-10; generic and corrected after its first dry run, KIT-CHAT0.g). For
`00-start-here/from-a-chat-app.md`: a general chat assistant app on any phone, tablet or computer (ChatGPT, the
Claude app, or another) guiding the owner through setup before any agent runs on the box. Walked once, in a
stand-in dry run (KIT-DRY.s2, 2026-11-10: a plain chat opened the README, then that page and this one, three pages
in one turn). Which real apps open a pasted address, and how many pages, is still to be tested app by app; the
table below is what the kit expects.*

<a id="starter-part-2--what-it-is-for-and-what-it-is-not"></a>
#### What it is for, and what it is not

A chat app guides the first evening: opening questions, choosing a start, installing or reading what is there,
onboarding, the owner account, backups, updates and the hand-off. Without an agent on the box it may keep guiding
later evenings using the kit's own device and first-automation guides. **The chat cannot see or change the box;
the owner performs every step.** It cannot run a command or keep house files. Its return path and owner-kept
progress-note format are in
[Coming back without an agent on the box](#starter-part-1--coming-back-without-an-agent-on-the-box).
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

<a id="starter-part-2--getting-the-kit-into-the-chat"></a>
#### Getting the kit into the chat

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

<a id="starter-part-2--which-phase-0-questions-the-chat-asks"></a>
#### Which Phase 0 questions the chat asks

Only the page's four opening questions (the device in use, where Home Assistant is, the AI plan and any monthly
limit, the time tonight), and the two its steps need when they come up: whether the owner will log in to the router
(default no), and the Home Assistant Cloud budget if they want it. The rest of the Phase 0 interview (time zone,
radios and devices, voice, the house's first request) belongs to the agent on the box, which reads the hand-off note
first and does not ask again what the note answers. The note records "not asked" for what the chat did not ask.

<a id="starter-part-2--which-agent-the-hand-off-installs"></a>
#### Which agent the hand-off installs

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

<a id="starter-part-2--how-this-goes-wrong"></a>
#### How this goes wrong

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

---

<a id="starter-part-3"></a>
## Part 3: `interview/phase-0-setup-interview.md`

<a id="starter-part-3--phase-0---the-setup-interview"></a>
### Phase 0 - the setup interview

*Status: written (O2, 2026-10-13). Run by the agent before Home Assistant exists. Follow `interview/README.md`,
"How to interview". Writes the `setup:` block of `house/profile.yaml` (schema: `profile-template.yaml`).*

**Purpose.** Decide the four things the install depends on (hardware, network, backups, agent budget), record
what the house already owns so Phase 1 can start from facts, and pick the install guide. Fifteen minutes. The
person does not need to know anything about Home Assistant yet; `00-start-here/` is written for them and you may
point at it, one section at a time, never as homework.

<a id="starter-part-3--jumping-ahead-phase-0"></a>
#### Jumping ahead (Phase 0)

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

<a id="starter-part-3--topic-1---where-and-when"></a>
#### Topic 1 - where and when

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

<a id="starter-part-3--topic-2---hardware"></a>
#### Topic 2 - hardware

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

<a id="starter-part-3--topic-3---network"></a>
#### Topic 3 - network

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
[`install/network-and-backups-first.md` section 2](#starter-part-8--2-remote-access-choose-later-but-choose-on-purpose).
Explain its price and the VPN or tunnel alternative from
`install/network-and-backups-first.md` section 2, then follow the owner's choice. Offering it is not permission
to subscribe, enable remote access or change router settings.

<a id="starter-part-3--topic-4---radios-and-devices-already-owned"></a>
#### Topic 4 - radios and devices already owned

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

<a id="starter-part-3--topic-5---notifications"></a>
#### Topic 5 - notifications

*Why:* the first message the house ever sends will go to a phone; the channel has to exist before the box does.

| Ask | Default | Writes |
|---|---|---|
| Which phones will the house talk to, and are they iPhone or Android? | the companion app on every household phone; nothing else at setup | `setup.notification_channels`, `setup.phone_platforms` |
| Will anyone need to be reached by text or call rather than a push? | later, as a backlog item with consent rules; nothing now | `setup.notification_channels` (planned) |

<a id="starter-part-3--topic-6---backups-off-the-box"></a>
#### Topic 6 - backups, off the box

*Why:* the install guide ends with a backup in two places. The second place has to exist before step one.

| Ask | Default | Writes |
|---|---|---|
| Where can a copy of the backup live that is not the box? (Home Assistant Cloud, a cloud drive, a NAS, a computer that is usually on) | offer Home Assistant Cloud first with its separate cost; the owner chooses the encrypted off-box route in `install/network-and-backups-first.md` section 3 | `setup.backup_offbox` (a kind, never a path, never a credential), `setup.cloud_budget` if chosen |
| Where will you keep the emergency kit (the backup encryption key and the authenticator setup key)? | a password manager and a printed sheet | `setup.emergency_kit` (a kind, never a location that identifies the house) |

<a id="starter-part-3--topic-7---the-agent-and-its-budget"></a>
#### Topic 7 - the agent and its budget

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

<a id="starter-part-3--close-phase-0"></a>
#### Close Phase 0

1. Read the `setup:` block back in plain words. Correct. Set `setup.interviewed_on`.
2. Say which guide you will walk and how long it takes (`install/README.md`, "Hands-on time"), and that you will
   go one step at a time and wait after each.
3. Begin the guide. When its "Done when" list and the one in `install/network-and-backups-first.md` are all
   checked: first CHANGELOG entry, `setup.done: true`, `setup.installed_on`.
4. Tell the person: Phase 1 starts at their first request to build something, and takes about half an hour of
   questions before the first build. `00-start-here/what-to-expect.md` says the same.

---

<a id="starter-part-4"></a>
## Part 4: `install/ha-green.md`

<a id="starter-part-4--installing-on-home-assistant-green"></a>
### Installing on: Home Assistant Green

*Status: written (O3a, 2026-10-13; Green only from KY, 2026-10-13). Sources: the official Home Assistant
installation pages, which hand Green setup to Nabu Casa's support site (support.nabucasa.com, "Home Assistant Green
documentation"). The Nabu Casa pages could not be read when this was written: the agent should open them with the
person and correct anything here that differs.*

**For the agent:** this is the shortest guide in the kit; most of the work is in `network-and-backups-first.md`.

<a id="starter-part-4--what-it-is"></a>
#### What it is
- **Home Assistant Green** is the official ready-made box: Home Assistant OS comes installed on its internal
  storage, so there is nothing to write or flash.
- It has no Zigbee or Thread radio; a USB radio such as Home Assistant Connect ZBT-2 adds one (`adapters/radios/`).

<a id="starter-part-4--before-you-start"></a>
#### Before you start
- The box, its power supply (in the box), and an **Ethernet cable** to the router. Setup is over Ethernet, and the box
  should stay wired.
- A computer or phone on the same network. A router login is optional, only if you choose a reservation.

<a id="starter-part-4--install"></a>
#### Install
There is nothing to install.
1. Plug the Ethernet cable into the box and the router.
2. Plug in the power. The box starts on its own.
3. Wait a few minutes. The first start downloads the latest Home Assistant, so the first screen you see may say it
   is preparing; let it finish.

<a id="starter-part-4--onboarding"></a>
#### Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network. The Green has no
   screen; if the name does not work, use the no-router route in `network-and-backups-first.md` section 1 to find
   its current address. Router changes are optional, with no as the default.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. Keep the address that opens it.
3. On the welcome screen choose **Create my smart home** (or restore a backup if you are moving an existing house
   onto this box; see `network-and-backups-first.md`, and check the box has more free storage than the old house
   uses).
4. Create the owner account (use a password manager), set the home location, time zone, units and currency.
5. Choose what to share with the project.
6. **Skip the discovered devices for now** unless one is essential; Phase 1 names things on purpose
   (`principles/naming.md`).
7. **Fresh installs only:** defer offered updates until `network-and-backups-first.md` section 3 has made
   a backup and a copy off the box; then follow section 4. A box already running instead follows that guide's
   **section 0: local backup and full update first**, before other changes. A fresh image already current
   needs no update.

**Jumping ahead:** If you choose [Jumping ahead](#starter-part-1--jumping-ahead),
you may update after making a local backup first and leave the off-box copy until later. A local backup
is lost with the box if the box or its storage is lost or fails.

<a id="starter-part-4--network-a-working-name-or-address"></a>
#### Network: a working name or address
The goal is to reach the box at a stable name or address. A reservation is optional. If you decline router
changes, record that choice and the tested access kind in the profile, as section 1 of
`network-and-backups-first.md` explains. Keep any private address in your note off the repository, and record how to find it again
if the router gives the box a new address. Leave the Green using automatic addresses; it has no screen to
recover a mistyped static address. A router that cannot reserve an address does not require changing the box's
network settings.

<a id="starter-part-4--first-backup-and-a-copy-off-the-box"></a>
#### First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3. The internal storage is not replaceable by you, so the off-box copy
is the whole recovery plan: a dead box becomes "buy another box (or use any spare computer), restore the off-box
copy during onboarding". Do one restore drill onto something else in the first month so you know it works and how
long it takes.

<a id="starter-part-4--next-phase-1"></a>
#### Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.

---

<a id="starter-part-5"></a>
## Part 5: `install/raspberry-pi.md`

<a id="starter-part-5--installing-on-raspberry-pi"></a>
### Installing on: Raspberry Pi

*Status: written (O3a, 2026-10-13), from the official Home Assistant Raspberry Pi installation page as of October
2026. If a menu name below does not match what you see, the official page wins; tell the agent so it can note the
change.*

**For the agent:** one step at a time; wait for "done". Ask which Pi model and how much RAM before step 1. Never
suggest a phone charger or a computer's USB port as the power supply.

<a id="starter-part-5--before-you-start"></a>
#### Before you start
You need:
- **A Raspberry Pi 5 or Raspberry Pi 4 with at least 2 GB of RAM** (4 GB or more leaves room for apps). Older
  models are not covered by the official guide.
- **The official power supply for that model** (the Pi 5 one is 27 W). Phone chargers and computer USB ports
  cannot supply enough power, and an underpowered Pi corrupts its card in ways that look like software bugs.
- **A microSD card of 32 GB or more, labeled A2** (Application Class 2: faster at the small reads and writes
  Home Assistant does all day). A known brand; counterfeit cards are common. If you boot from an SSD, the card
  is still handy as a spare.
- **A card reader** on the computer you will write the card from.
- **An Ethernet cable to the router.** Required for the install; Wi-Fi can be set up later, but wired is more
  reliable and recommended for good.
- A case with some airflow. A Pi that throttles from heat slows everything down.

**Parts for a Pi 5 booting from NVMe** (the setup this kit recommends for a Pi): the Pi 5 (4 GB or more), the
27 W official supply, an M.2 HAT for the Pi 5, an NVMe drive in a length the HAT holds (most take 2230 and
2242; check the HAT's page before buying a 2280), the active cooler or a fan case, and a case made to fit the
board with the HAT on it (many Pi 5 cases do not). Default: use a USB enclosure compatible with the drive to write
the image from the other computer. Keep a microSD card as a spare; the card-first alternative below needs additional
Pi desktop equipment.

**About the card.** On a Pi the card is the most likely part to fail (see `adapters/hardware.md`): it wears out
from constant small writes. Plan for that from day one: the off-box backup in `network-and-backups-first.md` is
your whole recovery plan, and a spare card in a drawer turns a dead card into a 45-minute restore. Booting from an
SSD (USB, or an NVMe board on a Pi 5) avoids most card wear: see "Booting from an SSD" below.

<a id="starter-part-5--install"></a>
#### Install
On your computer:
1. Download and install **Raspberry Pi Imager** from raspberrypi.com/software.
   - If Imager does not run on your computer, download the Home Assistant OS image for your model (`haos_rpi5-64`
     or `haos_rpi4-64`, `.img.xz`, from the Home Assistant OS releases page on GitHub) and write it with
     another imaging tool such as Balena Etcher.
2. Open Imager and select **OS**.
3. Select **Other specific-purpose OS > Home automation > Home Assistant**.
4. Choose the Home Assistant OS build for your model (RPi 4 or RPi 5). They are different images.
5. Insert the card. Choose it as the storage. **Everything on the card is erased**; check you picked the card and not
   another drive.
6. Select **Next**, then **Write**, and wait for writing and verifying to finish.
7. Select **Finish** and eject the card.

<a id="starter-part-5--booting-from-an-ssd-nvme-on-a-pi-5-or-usb"></a>
##### Booting from an SSD (NVMe on a Pi 5, or USB)
The steps above write a card; an SSD takes the same image. Two ways, the official pages win if they differ:
- **Write the drive directly.** Put the drive in a USB enclosure, plug it into the computer, and in Imager choose it
  as the storage (step 5). Then fit it to the Pi (NVMe: into the board, with the Pi off) and boot with no card.
- **Through a card first.** Without an enclosure, this needs a monitor, keyboard, mouse and suitable display cable,
  plus a Raspberry Pi OS desktop on the card and a working network connection. Follow the official Raspberry Pi
  first-time desktop setup, then run Raspberry Pi Imager on that desktop to write Home Assistant OS to the NVMe.
  Check the selected destination before writing; shut down and remove the card before booting the NVMe. If those
  peripherals or a documented remote desktop route are unavailable, use an enclosure or stop until they are ready.
If the Pi does not boot from the drive with no card in, connect a screen: it shows the bootloader's boot order. A
current Pi 5 bootloader tries NVMe; an older one may need the boot order changed with the official Raspberry Pi
tools (`rpi-eeprom-config`, or Imager's "Bootloader" image). Record `setup.storage: nvme` (or `ssd`).

On the Pi:
1. Put the card in the Pi (skip this with an SSD).
2. Plug the Ethernet cable into the Pi and the router (the same network as your computer, with internet).
3. Plug in the power supply. There is no power button; it starts.

<a id="starter-part-5--onboarding"></a>
#### Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network. If it does not work,
   follow the no-router route in `network-and-backups-first.md` section 1; a connected HDMI screen can show the
   Pi's current address. Router changes are optional, with no as the default.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. On a Pi 4 or 5 the page
   should appear within a minute or two; the first start downloads the latest Home
   Assistant, so a "preparing" screen for several minutes is normal.
   - Nothing after 5 minutes: the card was probably not written correctly. Write it again, ideally with another
     card. Still nothing: connect a screen by HDMI and read the console.
3. On the welcome screen choose **Create my smart home** (or **Upload backup** / Home Assistant Cloud if you are
   moving an existing house onto this Pi; see `network-and-backups-first.md`).
4. Create the owner account. Use a password manager; the name shown is what the household sees.
5. Set the home location, time zone, units and currency. The location drives sunrise and sunset automations and
   the weather; a pin at the right house matters more than it seems.
6. Choose what to share with the Home Assistant project (your call; analytics are anonymous and help the
   developers).
7. The last screen lists devices it found on the network. **Skip them for now** unless one is essential; Phase 1
   names things on purpose (`principles/naming.md`) and renaming later is work.
8. **Fresh installs only:** defer offered updates until `network-and-backups-first.md` section 3 has made
   a backup and a copy off the box; then follow section 4. A box already running instead follows that guide's
   **section 0: local backup and full update first**, before other changes. A fresh image already current
   needs no update.

**Jumping ahead:** If you choose [Jumping ahead](#starter-part-1--jumping-ahead),
you may update after making a local backup first and leave the off-box copy until later. A local backup
is lost with the box if the box or its storage is lost or fails.

<a id="starter-part-5--network-a-working-name-or-address"></a>
#### Network: a working name or address
The goal is to reach the box at a stable name or address. A reservation is optional. If you decline router
changes, record that choice and the tested access kind in the profile, as section 1 of
`network-and-backups-first.md` explains. Keep any private address in your note off the repository, and record how to find it again
if the router gives the box a new address. A static address needs a separate choice and a recovery plan, with
a screen and keyboard ready at the Pi. It is not the fallback for declining the router.

<a id="starter-part-5--first-backup-and-a-copy-off-the-box"></a>
#### First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3. For a Pi this is not optional: the card is the likely failure, and
an off-box copy plus a spare card is the plan for it.

Worth adding in the first month:
- a **spare card or SSD**, and one timed restore onto it (restore during onboarding);
- a **system monitor** for the Pi's CPU temperature and disk use, so heat and a filling card show up as health
  checks before they show up as failures (`principles/health-checks.md`).

<a id="starter-part-5--radios"></a>
#### Radios
USB radio sticks (Zigbee, Z-Wave, Thread) go on a short USB **extension cable**, away from the Pi and its USB 3
ports, which interfere with 2.4 GHz radios. See `adapters/radios/`.

<a id="starter-part-5--next-phase-1"></a>
#### Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.

---

<a id="starter-part-6"></a>
## Part 6: `install/mini-pc-bare-metal.md`

<a id="starter-part-6--installing-on-a-mini-pc-bare-metal-home-assistant-os"></a>
### Installing on: a mini PC, bare metal (Home Assistant OS)

*Status: written (O3a, 2026-10-13), from the official Home Assistant "Generic x86-64" installation page as of
October 2026. If a menu name below does not match what you see, the official page wins; tell the agent so it can
note the change.*

**For the agent:** this guide ERASES the mini PC's drive. Before step 1, ask the person to confirm in words that
nothing on that computer needs keeping, and that the computer is dedicated to Home Assistant from now on. One step
at a time; wait for "done". If they want to run other things on the same machine, stop and switch to
`proxmox-vm.md`.

<a id="starter-part-6--before-you-start"></a>
#### Before you start
You need:
- **The mini PC.** Intel or AMD, 64-bit, able to boot in **UEFI** mode (almost anything from the last ten years).
  4 GB of RAM is enough to start; 8 GB leaves room. An SSD of 64 GB or more.
- **A drive that uses 512-byte sectors.** A few NVMe SSDs and hard disks use 4K-native sectors only ("4Kn"); Home
  Assistant OS cannot boot from those. Most drives are fine; if the drive's data sheet says 4Kn, use another.
- **A USB stick of 8 GB or more** (it is erased too) and another computer to prepare it on.
- **An Ethernet cable to the router.** The first start needs the internet: it downloads the latest Home Assistant.
- **A keyboard and a screen** for the setup (only during the install).

Why bare metal rather than a VM: simpler, nothing between Home Assistant and the hardware, and USB radios just
work. What you give up: no instant snapshots before risky changes (backup tiers T0-T2 are slower; see
`adapters/hardware.md`), and the machine runs nothing else.

<a id="starter-part-6--1-set-the-firmware-bios"></a>
#### 1. Set the firmware (BIOS)
1. Start the mini PC and press the setup key repeatedly: usually **F2**, sometimes **Del**, **F1** or **F10**.
2. Make sure **UEFI** boot mode is enabled.
3. **Disable Secure Boot.** Home Assistant OS does not boot with it on.
4. While you are here, two settings worth having (names vary by maker):
   - **Restore on AC power loss: Power On** (sometimes "After power failure: On"), so the house comes back by
     itself after a power cut. Without it, every outage ends with someone pressing the power button.
   - Wake or fan settings you do not understand: leave them.
5. Save and exit.

<a id="starter-part-6--2-write-home-assistant-os-to-the-internal-drive"></a>
#### 2. Write Home Assistant OS to the internal drive
The official recommended method boots Ubuntu from the USB stick and writes the image from there. Home Assistant OS
has no installer of its own.

On your other computer:
1. Make an Ubuntu Desktop USB stick, following Ubuntu's own "try Ubuntu Desktop" instructions.

On the mini PC:
1. Plug in the USB stick, the Ethernet cable, keyboard and screen. Start it and pick the USB stick as the boot
   device (the boot menu key is often **F10** or **F12**, or change the boot order in the firmware).
2. When asked, choose **Try Ubuntu**, NOT "Install Ubuntu".
3. In Ubuntu, open a browser, go to the official Home Assistant "Generic x86-64" installation page and download the
   Home Assistant OS image it links (`haos_generic-x86-64-<version>.img.xz`).
4. Open **Show Applications**, search for **Disks**, and open it.
5. On the left, select the mini PC's INTERNAL drive (check the size and model; the USB stick is also listed).
6. From the **⋮** menu at the top, choose **Restore Disk Image...**, select the image you downloaded, then
   **Start Restoring...** and confirm **Restore**.
   - "Error unmounting filesystem ... target is busy": you are running Ubuntu from the internal disk instead of the
     stick. Restart and choose **Try Ubuntu** from the stick.
   - A "Swap" partition is listed on the target drive: select it, press the stop button to unmount it, and try
     again.
7. When it finishes, shut Ubuntu down and remove the USB stick when told to.

(The official page also has a second method: take the drive out, write the image with Balena Etcher on another
computer, and put it back. Use it if the mini PC cannot boot from USB.)

<a id="starter-part-6--3-first-start"></a>
#### 3. First start
1. With the USB stick removed and the Ethernet cable in, power on.
2. After a minute or so the Home Assistant banner appears on the screen with the box's address.
   - "No bootable device": the firmware needs an EFI boot entry pointing at `\EFI\BOOT\bootx64.efi` on the drive.
     The official page shows how, from the firmware's boot menu or with `efibootmgr` from the Ubuntu stick.

<a id="starter-part-6--onboarding"></a>
#### Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network, or use the address
   on the box's screen. Follow `network-and-backups-first.md` section 1; router changes are optional, with no as
   the default. Reserve the address only if you choose that route.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. Bookmark the address that opens it.
3. A **Preparing Home Assistant** page for several minutes is normal.
4. Choose **Create my smart home** (or restore a backup if you are moving an existing house onto this box; see
   `network-and-backups-first.md`).
5. Create the owner account (use a password manager), set the home location, time zone, units and currency.
6. Choose what to share with the project.
7. **Skip the discovered devices for now** unless one is essential (`principles/naming.md`).
8. **Fresh installs only:** defer offered updates until `network-and-backups-first.md` section 3 has made
   a backup and a copy off the box; then follow section 4. A box already running instead follows that guide's
   **section 0: local backup and full update first**, before other changes. A fresh image already current
   needs no update.
9. Unplug the keyboard and screen.

**Jumping ahead:** If you choose [Jumping ahead](#starter-part-1--jumping-ahead),
you may update after making a local backup first and leave the off-box copy until later. A local backup
is lost with the box if the box or its storage is lost or fails.

<a id="starter-part-6--network-a-working-name-or-address"></a>
#### Network: a working name or address
The goal is to reach the box at a stable name or address. A reservation is optional. If you decline router
changes, record that choice and the tested access kind in the profile, as section 1 of
`network-and-backups-first.md` explains. Keep any private address in your note off the repository, and record how to find it again
if the router gives the box a new address. A static address on the box needs a separate choice and a recovery
plan; it is not the fallback for declining the router.

<a id="starter-part-6--first-backup-and-a-copy-off-the-box"></a>
#### First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3. On a mini PC, worth adding in the first months
(`principles/backups-and-recovery.md`):
- a **second internal drive or a network share** for a nightly copy, so a dead system drive is a reinstall plus a
  restore, not a rebuild;
- a **system monitor** for CPU temperature and disk use (`principles/health-checks.md`);
- a timed restore drill onto a spare machine or a VM.

<a id="starter-part-6--radios"></a>
#### Radios
USB radio sticks go on a short USB **extension cable**, away from the PC and its USB 3 ports. See
`adapters/radios/`.

<a id="starter-part-6--next-phase-1"></a>
#### Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.

---

<a id="starter-part-7"></a>
## Part 7: `install/proxmox-vm.md`

<a id="starter-part-7--installing-on-a-proxmox-vm-home-assistant-os"></a>
### Installing on: a Proxmox VM (Home Assistant OS)

*Status: written (O3a, 2026-10-13). The image, the minimum resources and the UEFI / no-Secure-Boot / guest-agent
requirements come from the official Home Assistant "Alternative" installation page (KVM/Proxmox, `.qcow2`) as of
October 2026. The official page has no Proxmox click-through, so the Proxmox steps below follow Proxmox VE 8's own
interface; if a field name differs on your version, the requirement in bold is what matters.*

**For the agent:** ask first whether Proxmox is already installed and running other VMs. If not, installing
Proxmox itself is a separate job (its own installer ISO, its own documentation); do that first, or switch to
`mini-pc-bare-metal.md` if the person only wants Home Assistant on that machine. Never run a script from the
internet on the Proxmox host on the person's behalf. One step at a time; wait for "done".

<a id="starter-part-7--why-a-vm"></a>
#### Why a VM
The VM is the hardware that makes the backup tiers fast (`adapters/hardware.md`): a snapshot before a risky change
rolls back in about a minute, a nightly image goes to a second disk, and a clone can be a staging copy of the
house. The costs: USB radios need passthrough, the guest cannot see the host's temperatures, and a paused VM pauses
the house's clock.

<a id="starter-part-7--before-you-start"></a>
#### Before you start
- A Proxmox VE host with free resources. **Minimum 2 vCPUs and 2 GB of RAM** for the VM (official minimum); 4 GB is
  a better start. 32 GB of disk is the image's default; 64 GB leaves room for the database and backups.
- The host on Ethernet with a bridge (normally `vmbr0`) to the home network.
- A shell on the host (the node's **Shell** button in the web interface).

<a id="starter-part-7--1-create-the-vm-proxmox-web-interface-create-vm"></a>
#### 1. Create the VM (Proxmox web interface, **Create VM**)
- **General:** a VM ID (write it down) and a name such as `haos`. Start at boot: on.
- **OS:** **Do not use any media.** Guest OS: Linux.
- **System:** Machine **q35**. BIOS **OVMF (UEFI)**. Add an EFI disk on your VM storage, and **untick "Pre-Enroll
  keys"** (pre-enrolled keys turn Secure Boot on, and Home Assistant OS does not boot with it). **Qemu Agent: on**
  (Home Assistant OS runs the guest agent, so Proxmox can shut it down cleanly and freeze it for snapshots).
- **Disks:** delete the default disk. The Home Assistant image becomes the disk in step 2.
- **CPU:** 2 cores; type **host** is fine on a single host.
- **Memory:** 4096 MB. Turn ballooning off if you want the VM's memory to stay put.
- **Network:** bridge `vmbr0`, model **VirtIO**.
- Finish, but **do not start** the VM.

<a id="starter-part-7--2-import-the-home-assistant-os-disk-host-shell"></a>
#### 2. Import the Home Assistant OS disk (host shell)
1. Copy the **KVM/Proxmox (.qcow2)** link from the official "Alternative" installation page. The file is named
   `haos_ova-<version>.qcow2.xz`.
2. On the host:
   ```sh
   cd /tmp
   wget <the link you copied>
   xz -d haos_ova-<version>.qcow2.xz
   qm disk import <vmid> haos_ova-<version>.qcow2 <storage>   # e.g. local-lvm; older versions: qm importdisk
   ```
3. In the VM's **Hardware**, the imported disk shows as **Unused Disk 0**. Edit it, attach it as **SCSI** (controller
   VirtIO SCSI single), tick **Discard** if your storage is an SSD, and **Add**.
4. **Resize** the disk if you want more than 32 GB (Hardware > the disk > Disk Action > Resize). Home Assistant OS
   grows into it on the next start.
5. **Options > Boot Order:** put the new SCSI disk first and enabled; untick the network boot entries.
6. Delete the downloaded files from `/tmp`.

<a id="starter-part-7--3-first-start"></a>
#### 3. First start
1. **Start** the VM and open its **Console**. After a minute or two the Home Assistant banner shows the VM's
   address.
2. The console stays at the EFI shell or "no bootable device": the disk is not first in the boot order, or Secure
   Boot is on (re-create the EFI disk without pre-enrolled keys).

<a id="starter-part-7--onboarding"></a>
#### Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network, or use the address
   in the VM's console. Follow `network-and-backups-first.md` section 1; router changes are optional, with no as
   the default. If you choose a reservation, match the VM's own MAC address in **Hardware > Network Device**,
   rather than the host's adapter. A host reservation is a separate optional choice.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. Keep the address that opens it.
3. A **Preparing Home Assistant** page for several minutes is normal; the first start downloads the latest Home
   Assistant.
4. Choose **Create my smart home** (or restore a backup if you are moving an existing house; see
   `network-and-backups-first.md`).
5. Create the owner account (use a password manager), set the home location, time zone, units and currency.
6. Choose what to share with the project.
7. **Skip the discovered devices for now** unless one is essential (`principles/naming.md`).
8. **Fresh installs only:** defer offered updates until `network-and-backups-first.md` section 3 has made
   a backup and a copy off the box; then follow section 4. A box already running instead follows that guide's
   **section 0: local backup and full update first**, before other changes. A fresh image already current
   needs no update.

**Jumping ahead:** If you choose [Jumping ahead](#starter-part-1--jumping-ahead),
you may update after making a local backup first and leave the off-box copy until later. A local backup
is lost with the box if the box or its storage is lost or fails.

<a id="starter-part-7--network-a-working-name-or-address"></a>
#### Network: a working name or address
The goal is to reach the box at a stable name or address. A reservation is optional. If you decline router
changes, record that choice and the tested access kind in the profile, as section 1 of
`network-and-backups-first.md` explains. Keep any private address in your note off the repository, and record how to find it again
if the router gives the box a new address. After a restore or clone, check that the saved name or address
still reaches this VM. Its console shows its current address; a new virtual MAC can mean the router gives the
box a new address. Check a reservation only if you chose one.

<a id="starter-part-7--first-backup-and-a-copy-off-the-box"></a>
#### First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3 first: the built-in backup with an off-box copy is still the plan
for "the whole host is dead". Then add the tiers only a VM gets (`principles/backups-and-recovery.md`):
- **Snapshots without RAM** before risky changes (VM > Snapshots > Take Snapshot, "Include RAM" OFF). A snapshot
  with RAM pauses the VM, and a paused VM stalls every timed automation; timers fire late and missed
  time triggers are dropped. Delete old snapshots; they grow.
- **A nightly Proxmox backup** (Datacenter > Backup) of the VM in **snapshot** mode, never "suspend" or "stop", to
  a disk that is not the VM's own disk.
- **Later, a staging clone** on an isolated bridge, start at boot off, with every USB passthrough line removed
  before its first start: a restored house tries to talk to its radios and push notifications at once.

<a id="starter-part-7--usb-radios"></a>
#### USB radios
Pass a radio stick to the VM by its **vendor and device ID** (VM Hardware > Add > USB Device > Use USB Vendor/Device
ID), not by port, so it survives being moved to another port. Put the stick on a short USB extension cable away
from the host. See `adapters/radios/`. A clone of this VM must never be given the same stick.

<a id="starter-part-7--things-the-house-must-never-be-able-to-do"></a>
#### Things the house must never be able to do
If you later add a Proxmox integration to Home Assistant, it creates Start, Stop and Reset buttons for the VM the
house runs in; "Stop" pressed from inside the house is pulling its own plug. Give that integration a read-only (or
read-plus-snapshot) Proxmox user, disable the button entities, and never expose them to a voice assistant
(`adapters/hardware.md`, `principles/safety-and-security.md`).

<a id="starter-part-7--community-helper-scripts"></a>
#### Community helper scripts
A popular community project offers a one-line script that does steps 1 and 2 for you. It is not part of the official
documentation. If the person wants it, read the script before running it on the host (it runs as root on the
machine that runs everything), and check its result against the bold requirements above.

<a id="starter-part-7--next-phase-1"></a>
#### Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.

---

<a id="starter-part-8"></a>
## Part 8: `install/network-and-backups-first.md`

<a id="starter-part-8--network-and-backups-first"></a>
### Network and backups first

*Status: written (O3a, 2026-10-13), from the official Home Assistant documentation as of October 2026 (the
installation, onboarding and backup pages). Every hardware guide ends here. Re-check the official pages when a step
does not match what you see: menus move between releases.*

**For the agent:** walk the person through this file one numbered step at a time and wait for "done" before the
next. Phase 0 is not finished until every box in "Done when" is ticked or the owner has chosen otherwise, one practice at a time, under "The owner's choice" below. You do not touch the network equipment
yourself; the person does, with you reading their router's screen back to them if they need help.

<a id="starter-part-8--why-this-comes-before-anything-else"></a>
#### Why this comes before anything else
Every later step needs two things: a working way to reach the box, and a backup somewhere other than the box.
A stable name or address avoids broken bookmarks and connections. A router reservation is optional; if you
decline it, record the working route and how to recover when a DHCP address changes. The first week's mistakes
are cheap only if you can roll them back.

<a id="starter-part-8--0-on-an-existing-install-back-up-locally-and-update-first"></a>
#### 0. On an existing install, back up locally and update first
**Goal: a recovery copy before the first change, then current screens for every later step.** Any start other
than a fresh install from the newest image takes this step before network, account, integration or app changes.
Sign in or finish required onboarding to reach Settings; read the version and installation type first.
A fresh install that is already current continues at section 1 without another update.

Before the first backup or update, save any old Home Assistant Cloud backup the owner may want. Cloud keeps one
backup, and the next upload replaces it; the automatic backup before an update can go to Cloud too. The owner
logs in to the [Home Assistant Cloud account](https://account.nabucasa.com/), opens **Cloud services > Backups**,
selects **Download**, and confirms that the file is saved privately off the box
([official steps](https://www.home-assistant.io/common-tasks/general/backups/#downloading-a-backup-from-home-assistant-cloud)).
Until it is saved, make no backup and no update.

1. **One local backup before anything else:** **Settings > System > Backups > Back up now**. If this is first-time
   setup, save the emergency kit privately off the box, choose **Custom** in the wizard, and confirm daily, retention
   of 7 where supported, and the **Share folder** where offered. If backups are already set up, use **Automatic backup >
   Configure backup settings** to verify those choices. Then select the full system and local location for a manual
   backup and wait for completion. Never put the encryption key or emergency kit in chat or the repository.
2. Under **Settings > Updates**, update **the operating system first**, then **Home Assistant Core and the
   Supervisor**, then **everything else**. Skip components the installation does not have (Container has no
   Home Assistant OS or Supervisor). Leave **Back up automatically before updating** on in each dialog where
   offered; otherwise make a fresh manual local backup before that update. Read the release notes and finish
   each update and restart before starting the next; verify each new installed version.
3. Continue only when the full update is complete. If an update fails or the box does not return, stop and use
   that component's official recovery instructions and the backup, rather than interrupting power or stacking
   more updates.

This gets the owner today's screens: **Settings > Marketplace** is built in on 2026.11 for community integrations,
cards, themes and templates; **Settings > Apps** manages apps separately.
Existing content from the former community store migrates automatically.
Check migration repairs and custom repository updates. The [Marketplace guide](https://www.home-assistant.io/integrations/marketplace/)
explains the limits and when a GitHub connection is needed. Follow the actual screen if a label moves. Letting a brand-new release settle a few days is advice for later maintenance, not a requirement to
postpone this first full update. Section 3 still sets up and proves encrypted automatic backups off the box;
this first local backup does not satisfy that goal. The official
[OS and Core update guide](https://www.home-assistant.io/common-tasks/os/#updating-home-assistant) covers
the dialogs and recovery. It recommends an outside copy before an OS update; this first-evening path starts
with the local copy above, so a failed disk could lose both the system and that copy. An outside copy is
stronger protection whenever one is already available.

<a id="starter-part-8--1-find-the-boxs-address-and-keep-it"></a>
#### 1. Find the box's address, and keep it
**Goal:** the person can reach the correct box from a computer and a phone, and knows what to try if its address
changes. A router normally assigns addresses automatically (DHCP). A reservation can keep one stable, but changing
the router is optional: **ask whether the owner wants to log in to it; the default is no**. The person operates
it, never the agent. Do not turn a declined login into a static-address change on the box.

1. **No router login:** try `http://homeassistant.local` from the home network. On some Android and Windows setups,
   .local names do not work; open the Home Assistant app and let it find the box, or read the address from the
   box's console. If the name does not resolve, use the
   current address shown by the box's console or installation screen, `http://<address>`. For a box without a
   screen, open the Home Assistant [companion app](https://companion.home-assistant.io/docs/getting_started/#step-by-step-setup)
   on a phone on the same home network, choose **Connect to my Home Assistant server**, and look for its discovered
   server. If it finds none, ask whoever set up the internet to find the box's current address in the provider
   app or router's connected-device list. That person can read the entry without asking the owner to change the
   router. If neither route identifies the box, stop and ask for that evidence; do not
   guess an address. On the kit's new-install path the address uses port 80, and `:8123` redirects there; an older
   or customized installation may still need port 8123. Keep the address that actually opens Home Assistant.
   Record `setup.network.router_control: false` and `setup.network.local_access: default-name` or `current-address`,
   as actually tested. If no choice was confirmed, list its dotted path under `assumed` rather than calling it
   verified. Bookmark the working address on both devices. In gotchas record, without a personal address:
   **DHCP addresses can change; try the default name, check the box's console, or ask the router administrator
   for the current device entry before changing anything.** If gotchas does not exist yet, keep this in the setup
   progress note and carry it forward when that file is created.
2. **Only if the owner opts in:** the router's label, provider app or manual explains its administration page.
   The owner types that page's address into the browser's address bar (not a search box), or opens the provider
   app, and enters its administrator credentials there. Those may differ from the Wi-Fi password. No password,
   router address or screenshot containing credentials goes into the agent's chat or repository.
   Find **DHCP clients**, **DHCP client list**, **Connected devices**, **Attached devices** or **Client list**.
   Confirm the entry by matching its **MAC/device-adapter address** with the active adapter's label, console or
   VM hardware screen, or match the console's current address to the client list's address column. A VM has its
   own virtual adapter; do not match the host's adapter instead. A device name alone is not proof: it may have been
   renamed. Do not select another device just because its name looks plausible.
3. **Optional reservation:** after confirming the device, reserve its current address in that page; the menu may
   say **Address reservation**, **Fixed IP** or **Static lease**. Leave the box using DHCP. Record
   `setup.network.router_control: true` and `setup.network.local_access: reserved-address` only after the person
   confirms success. If reservation is unavailable, use the no-router path, record what was checked, and leave
   reservation for a later owner decision. Static addressing needs a separate explicit choice and a recovery
   plan; it is not the default fallback.
4. **Check and save:** open the working address from the computer and phone on the same home network and keep
   bookmarks or a private note off the box. The profile records the access **kind**, never a personal address.
   Network settings that cannot be checked without a declined router login stay `assumed`, including the checks
   in section 1b. Later devices pinned to an address may benefit from reservations too, but each router change
   still needs the owner's choice.

<a id="starter-part-8--1b-what-the-network-must-allow"></a>
#### 1b. What the network must allow
Some radios and voice bridges need more from the router than an address. Check the ones the house uses
(`setup.radios`, `setup.voice`) now, with the person reading the router's settings; a provider's box usually has
them right by default.
- **Matter and Thread:** IPv6 on for the home network, and multicast (mDNS) reaching Wi-Fi from the wired side.
- **Apple Home (HomeKit Bridge), Google Cast, most "discovered" devices:** mDNS ("Bonjour") passing between the
  box and the phones.
- **Everything on Wi-Fi:** the box and the phones on the same network, not a guest network, and "client isolation"
  or "AP isolation" off on it.
- **Wi-Fi devices that are 2.4 GHz only** (most plugs and bulbs): a 2.4 GHz network they can join. A router that
  merges both bands under one name usually works; if a device will not join, the person can join their phone to
  2.4 GHz for the pairing.
Write what was checked into `setup.network`; anything not checked goes in the profile's `assumed` list.

<a id="starter-part-8--2-remote-access-choose-later-but-choose-on-purpose"></a>
#### 2. Remote access (choose later, but choose on purpose)
**Goal:** reach the house securely from outside when the owner wants that. Remote access is optional for setup.
Offer these routes in order, explain cost and effort, and follow the owner's choice:
- **Home Assistant Cloud (Nabu Casa), first:** remote access without opening a router port, encrypted off-site
  backups, Alexa/Google voice links and cloud speech services. As checked on 2026-11-10, the US price is **USD
  6.50/month or USD 65/year, plus tax**; other regions differ. Check Nabu Casa's current
  [Pricing & Benefits](https://www.nabucasa.com/pricing/) before
  subscribing. Put this on its own **off-site access/backup budget line**, separate from the AI subscription.
  In **Settings > Home Assistant Cloud**, the owner creates or signs into their account. **Remote access is off on
  a new setup until the owner turns its toggle on**; an older setup may already have it on, so read the toggle on
  that page after signing in. Complete the MFA enrollment and recovery checks below before turning it on; for
  backups only, leave it off. Signing up leaves an existing Alexa or Google Home setup as it
  is; voice links are a separate, later choice (`install/voice-assistants.md`). The backup location is selected
  separately in section 3. Account details and the remote address stay out of chat and the repository.
- **If the owner declines Cloud: a VPN to the home network**, such as WireGuard or Tailscale, or a managed tunnel.
  A VPN can have no subscription cost but takes setup and a VPN app on each phone; tunnel costs and requirements
  vary. Choose a documented route the owner can maintain, not a router change they did not agree to.
- **Not recommended for a first box: forwarding a router port to Home Assistant.** It puts the login page on the
  internet. If you ever do it, it needs HTTPS, multi-factor login on every account and a reason.

Whatever you pick, turn on **multi-factor authentication** for the owner account before any remote access is
enabled (unless the owner chose otherwise under "The owner's choice" below): **your user profile > Security >
Multi-factor authentication modules > Authenticator app > Enable**, then scan the code with an authenticator app.
Before finishing enrollment, the owner saves the **setup key shown below the QR code** with the emergency kit,
in a password manager and a second secure place off the box. This is a different key from the backup encryption
key. Home Assistant's authenticator setup does not issue a set of backup codes. Check how the authenticator app
backs up or transfers accounts and how to recover it without the current phone. Confirm a fresh login works
before closing the existing session. Never show either key to the agent or put it in chat or the repository.
The official [authenticator setup instructions](https://www.home-assistant.io/docs/authentication/multi-factor-auth/)
show where the setup key appears.

Home Assistant Cloud's Alexa link does not require **Remote access**.
Leave that toggle off unless the owner wants access to the Home Assistant UI from outside.
[Nabu Casa documents the separate Cloud features](https://support.nabucasa.com/hc/en-us/articles/26508882007581-Remote-access-Security-aspects).
The [official Remote access action guide](https://www.home-assistant.io/actions/cloud.remote_disconnect/) confirms that voice assistants keep working when it is off.

<a id="starter-part-8--3-backups-from-day-one"></a>
#### 3. Backups from day one
**Goal: a copy off the box, encrypted, automatic.** A working copy elsewhere must survive a failed Home Assistant
disk without depending on somebody remembering to copy it. The tiers are in `principles/backups-and-recovery.md`.
If the owner wants another service, or a route stalls, explain another route's cost and effort and follow their
choice. The readiness check is the goal, not a particular vendor. A hand copy for tonight is useful but partial.

**Cloud-copy check — before backup setup, including on a fresh install:** ask whether the owner used Home Assistant Cloud for backups before.
If so, or if that is unknown, check that Cloud account for a backup the owner may want.
Cloud keeps only the last uploaded backup; a new upload replaces it, including a scheduled backup.
The owner signs in to the [Home Assistant Cloud account](https://account.nabucasa.com/) in a browser.
Open **Cloud services > Backups** and select **Download** for any wanted backup.
Then confirm the saved file privately off the box; on an iPad, check its entry and size in Files.
Keep the file and its encryption key out of chat and the repository.
If there is no wanted Cloud backup, record that decision privately instead.
If the account or the download cannot be checked, pause here.
Until the wanted copy is saved, or the owner confirms no wanted Cloud backup, do not enable a backup location.
Do not create a backup or update before that decision.
Do this before the setup wizard below; a fresh install may have skipped section 0.

1. Open **Settings > System > Backups**. On first-time setup, choose **Set up backups**. If backups are already
   configured, choose **Automatic backup > Configure backup settings** instead; the first local backup in section 0
   may already have completed setup. Verify the same schedule, retention, data and locations below on either route.
2. **Download the backup emergency kit** when asked, and store it in a password manager AND one other place that
   is not the box (a printed copy in a drawer counts). It holds the encryption key; without it an encrypted backup
   cannot be restored. Never put it in the repository the agent works in. In the first-time wizard choose **Custom**:
   **Recommended** saves immediately, retains three and excludes the Share folder.
3. **Schedule: Daily.** Choose a time when every backup location is reachable (a network share that sleeps at
   night fails the backup for that location).
4. **Keep: 7** to start. With daily backups that is a week of rollback points where the location allows it;
   Home Assistant Cloud keeps only the latest backup, so it is not a seven-copy archive.
5. **Data:** include the **Share folder**: the agent keeps the house folder there, and these backups are its
   off-box copy until the owner chooses a code host (`AGENTS.md`, "Arriving from a chat app"). Leave media out
   unless you know you need it; it makes backups large and restores slow. Some apps are
   large too. Check the backup's size against each location's limit (Home Assistant Cloud: one backup, up to
   5 GB); when it nears the limit, move large files out of the share folder rather than leaving the folder out.
6. **Locations: choose a route below**, then in **Backups > Automatic backup > Configure backup settings >
   Locations** enable it, keep encryption on and check its retention. An integration must be set up before its
   location appears. Finish by creating a backup and checking that the chosen destination actually received it.

<a id="starter-part-8--route-a--home-assistant-cloud-offered-first"></a>
##### Route A — Home Assistant Cloud, offered first
First complete the Cloud-copy check at the start of this section, including a confirmed download of any wanted backup.
Do not enable this location until that check is complete, even on a fresh install.
Use the subscription described in section 2; there is no separate backup fee.
Sign in under **Settings > Home Assistant Cloud**, then enable its backup location as above.
It holds **one encrypted backup, up to 5 GB**: the latest saved there replaces the previous one.
Keep the saved copy and emergency kit privately off the box.
If the selected data exceeds the limit, reduce what is included or choose another destination.
A subscription alone is not a completed backup.

<a id="starter-part-8--route-b--google-drive-free-within-the-accounts-storage-allowance"></a>
##### Route B — Google Drive, free within the account's storage allowance
This is the hardest setup step; the agent walks you through it one screen at a time.

Allow **about 20 minutes of hands-on setup**, plus any Google activation delay. It needs a Google Cloud project
and OAuth credentials; signing into Drive alone is not enough. Use Home Assistant's official
[Google Drive prerequisites](https://www.home-assistant.io/integrations/google_drive/#prerequisites)
alongside these steps; they carry the exact domain and redirect values, not the
address of the owner's box.

1. In the Google Cloud console, create/select a project and enable **Google Drive API**.
2. Open **Google Auth Platform > Branding > Get started**. Give the app a name, fill in the owner's own contact
   details in Google, and choose an **External** audience. Complete Branding's app-domain fields with the values
   from the official instructions.
3. Under **Audience**, publish the app. Leaving it in **Testing** makes authorization expire after seven days;
   a testing user must also be added there. Do not mistake that for a reliable unattended backup.
4. Under **Clients > Create client**, choose **Web application**. Copy the official instructions' exact
   **Authorized redirect URI**, create the client, and save its client ID and client secret privately before
   closing the dialog. Neither belongs in the agent's chat or repository. Activation can take time.
5. In Home Assistant, **Settings > Devices & services > Add integration > Google Drive**. Enter those application
   credentials there, authorize the intended account, and check the instance URL before **Link Account**.
6. Return to the backup settings, enable **Google Drive**, keep encryption on, and confirm a backup arrives in
   its Drive folder. Check free space; storage beyond the account's allowance may cost money.

<a id="starter-part-8--route-c--a-share-or-a-usb-copy-with-its-limits-recorded"></a>
##### Route C — a share, or a USB copy with its limits recorded
A NAS or another computer can provide an automatic destination: **Settings > System > Storage > Add network
storage**, usage **Backup**, then select it under backup Locations. It must be awake and writable at backup time.
A share in the same building survives the box failing, but does not replace an off-site copy.

A USB drive kept away from the box is a useful hand-copy destination. It is **not automatic** unless an automatic
copy process is configured and a scheduled run is verified. A drive left beside or attached to the box is not an
off-site copy. Do not erase or repurpose a drive to make this checklist pass.

<a id="starter-part-8--make-and-check-the-first-copy"></a>
##### Make and check the first copy
1. **Backups > Backup now > Manual backup**: select the intended data and destinations, create it, and wait for
   completion and uploads. Confirm the new backup in each chosen destination, not only in the on-box list.
2. Download a copy to the owner's computer, or to a phone or tablet. A fresh install can produce a file of only a few hundred KB; there
   is no universal minimum size. Compare the download with the backup's reported size and check that it completed.
   **Size alone does not pass L0-backup-proven.** The owner opens a decrypted download with an archive tool and
   confirms it contains `backup.json` and the Home Assistant data archive, or performs a restore drill. The kit has
   no tested way to open the `.tar` file on a phone or tablet alone: it needs a computer with an archive tool, or
   an archive app on the tablet that can list a `.tar` file. Until then the proof stays pending. The agent
   never opens the backup. Keep a decrypted copy private; it holds settings and saved logins.
3. **Hand copy tonight.** The backup menu's **Download** normally gives a decrypted file with no encrypted choice:
   when the backup uses the key already set on the box, Home Assistant decrypts it on the fly and downloads it at
   once (the [backup page](https://www.home-assistant.io/common-tasks/general/backups/#downloading-your-local-backups);
   the frontend code,
   [download_backup.ts](https://github.com/home-assistant/frontend/blob/20261028.5/src/panels/config/backup/helper/download_backup.ts#L43)).
   The recommended copy stays encrypted: copy the encrypted archive from the `backup` folder (Samba share app)
   if the owner can, or use route B (Google Drive, free, section 3), or Home Assistant Cloud if chosen. A
   decrypted file holds settings and any saved logins, so warn once, in one plain sentence, that anyone who gets
   it can read them. If the owner still wants that copy in iCloud Drive or another store they trust, it is their
   choice: go on without arguing and add "off-box hand copy, decrypted, <date>" to the `Owner's choices:` line. Only if the key is
   missing or wrong does a dialog open, with a link **download the backup encrypted**; use it only when you see
   that dialog, and never change or remove the key to make it appear. Check the file's presence at the
   destination. Until one route works, the off-box copy stays pending.
4. Record the date, destination **by kind**, what was checked, and **automatic off-box backup pending**, with the
   next step, in the CHANGELOG (or the setup progress note before it exists). No keys or personal paths. A manual
   upload does not finish the automatic goal or L0-done-when; keep that line open and record any owner exception
   separately. Do not assume a pre-update backup was uploaded: **app-update backups use the default local backup
   location**, on the box or designated network storage, rather than the selected Cloud/Drive automatic locations.
   For later maintenance updates, verify a current full backup off the box; make a fresh manual copy if needed.
   The initial update in section 0 starts with its local backup, before this off-box setup exists.
5. Verify a later **scheduled** backup reaches the chosen outside location with encryption on. Only then mark
   the automatic off-box goal complete. An Apple-only household can use Cloud, Drive or a Mac share; iCloud Drive
   is not itself a Home Assistant backup location.

For tonight's note, a confirmed encrypted Cloud copy is an off-box copy, not a downloaded file.
Record its location and confirmation without claiming a download happened.
Keep the opened-archive or restore-proof check pending until the owner performs it.
A location check alone does not prove that an archive can be restored.

The official [backup guide](https://www.home-assistant.io/common-tasks/general/backups/) covers location setup,
encrypted downloads and the different destination rules for app-update backups.

A full restore drill (a spare box or a VM, restore from the off-box copy during onboarding, time it) is worth doing
in the first month. A restore of a larger install takes up to about 45 minutes; you want to know your number before
the day you need it. Restoring during onboarding also works across hardware (a Raspberry Pi backup onto a mini PC),
as long as the target has more free disk than the source had in use (**Settings > System > Repairs > ⋮ > System
information > Home Assistant Supervisor > Disk used**).

<a id="starter-part-8--4-updates-from-day-one"></a>
#### 4. Updates, from day one
- **The first full update was section 0**, after a local backup and before the other changes. A fresh install
  already current had nothing to update. Do not put that initial update last or leave it optional tonight.
- For later maintenance, first verify section 3's backup and outside copy. Read the release notes, especially
  "Backward-incompatible changes". Let a brand-new release settle for a few days as advice; find its publication
  date on its release page, not the version-only stable-version feed. If the date cannot be checked, say so.
- Open **Settings > Updates**. Work one layer at a time: **OS, then Core and Supervisor, then everything else**.
  In each update's dialog leave **Back up automatically before updating** selected where offered. This is not
  a switch in the backup setup wizard; otherwise make a manual backup and outside copy before that update.
- Expect a backup stage, installation, then a restart for Core/OS updates. The page may say **Connection lost**
  or temporarily stop loading; reconnect at the saved address and log in with MFA if asked. Timing varies: do
  not interrupt power or start another update just because the page disconnects. If it does not return, use the
  component's official recovery instructions and the saved backup rather than repeatedly restarting it.
- Check that the new version is shown and the needed integrations work before starting the next update.
- For ongoing maintenance before a trip or a busy week, freeze updates until you are back
  (`principles/change-control.md`).

<a id="starter-part-8--5-the-households-phones"></a>
#### 5. The household's phones
Every adult who should get notifications or control the house from a phone needs the companion app now; Phase 1
reads the phones from the box.
1. Install **Home Assistant** from the App Store or Google Play, open it, and connect to
   the saved working address, normally `http://<address>` on the new-install path (on the home network). Each
   person logs in as themselves; a child's device only if
   the person wants it.
2. **Name the device for its role before anything uses it.** The field is called **Device name**: Android asks
   for it while connecting; on an iPhone it is in the app's settings (the menu moves between versions; the official
   companion app docs say where). Use a role, for example `Owner phone`. Renaming after the app has registered may
   not rename the action; if it does not, remove the device in Home Assistant and connect the app again. The
   notification action is made from this name (`notify.mobile_app_owner_phone`), and it ends up in
   automations, the CHANGELOG and the wiki: a role keeps a person's name and phone model out of all of them.
3. Allow notifications. On an iPhone also allow **Time Sensitive** notifications (an urgent push can then reach the
   person through a Focus such as Sleep; `adapters/notifications/companion-app.md`). Location: "Always" only for
   people whose presence the house uses (Phase 1 asks).
4. Read the action names back from **Settings > Tools > Actions** (type `notify.mobile_app`), and send nothing:
   the first push is the owner's to send.

<a id="starter-part-8--6-giving-the-agent-access"></a>
#### 6. Giving the agent access
`install/agent-access.md`: a user and a token for the agent, a read check, and (at the first build) a deploy path.

<a id="starter-part-8--the-owners-choice"></a>
#### The owner's choice
Each practice above is the default and the recommendation. Where a weaker way still works, the owner may take it
after one plain sentence about the risk; then go on without arguing and do not ask again. Record it in one form:
an entry `<practice>, <date>` on the `Owner's choices:` line of the hand-off note, and, once the house has a
profile, in `adoption.opted_out`.

| Practice | The weaker way that still works | The one sentence to say |
|---|---|---|
| Encrypted backups | A plain (decrypted) copy in a store the owner trusts, such as iCloud Drive or a NAS | Anyone who gets that file can read the house's settings and saved logins. |
| Where the off-box copy lives | Any store the owner trusts and can reach, not only Home Assistant Cloud or Google Drive | A copy that is not automatic or not tested may be missing on the day it is needed. |
| One emergency kit in two places | One place, or the same password manager as the password | If that one place is lost, an encrypted backup or the authenticator cannot be rebuilt. |
| Two-step login | Off, or on for the owner account only | If someone learns the password, nothing else stands in the way; this matters most before remote access. |
| Remote access | A VPN, a managed tunnel, or a forwarded port instead of Home Assistant Cloud | A forwarded port puts the login page on the internet, so it needs HTTPS and two-step login on every account. |
| The router | The owner never logs in; a working name or address is recorded instead | A changed address can break bookmarks and connections until the new one is found. |

Hard stops stay only where the choice would harm someone else or leave the owner with no way back: a secret
(a key, a token, a password, a setup key) put into chat or the repository; two-step login left half on (enrollment
started but the setup key not saved, or the new login not confirmed before the old session is closed, which can lock
the owner out); changing
or removing the backup key so a dialog appears; a message to a person who has not agreed to it; exposing locks,
alarm or sensors to a voice assistant. Say which one it is and why, in one sentence.

<a id="starter-part-8--done-when"></a>
#### Done when
- [ ] The box can be reached at a stable name or address: either its address is reserved, or the owner has
      declined router changes and confirmed a working name or current address. The choice and tested access
      kind are recorded in the profile; any private address is kept in a note off the repository. The recovery
      steps for a changed DHCP address are recorded. A reservation is not required for this check.
- [ ] The working address, normally `http://<address>` (port 80 on the new-install path), opens from a computer
      and a phone on the home network, and is bookmarked on both; any older port is recorded.
- [ ] The owner account has multi-factor login on, with its setup key and authenticator recovery checked.
- [ ] Automatic daily backups are configured, kept 7 where supported (Cloud keeps one); the backup-before-update
      option is checked in each update dialog, not claimed from the backup wizard.
- [ ] A scheduled backup has reached at least one encrypted location off the box. A hand copy alone leaves this open.
- [ ] The emergency kit is in two places, neither of them the box nor the repository.
- [ ] One backup has been downloaded and opened by the owner, or a restore drill has proved it; size alone is not proof.
- [ ] Each household phone that will get pushes has the companion app, named for its role, notifications allowed.
- [ ] The network checks in 1b for the house's radios and voice are done, or listed as `assumed`.
- [ ] `install/agent-access.md` "Done when" is ticked (or `setup.agent_access.read: person-reads` is recorded).

Then go to Phase 1 (`AGENTS.md`).

---

<a id="starter-part-9"></a>
## Part 9: `install/voice-assistants.md`

<a id="starter-part-9--keep-familiar-voice-control-while-adding-home-assistant"></a>
### Keep familiar voice control while adding Home Assistant

*Guide checked against the linked official pages on 2026-11-10. Menu names may change; follow the owner's
screen and the current linked instructions. This is a plan the owner carries out, not permission for the agent
to change devices or accounts.*

The goal is to control each chosen device from Home Assistant while keeping the voice commands the household
already uses. Ask which assistant they use and what it controls. Start with one ordinary light or switch
**that no routine uses**, when a brief interruption is acceptable; agree its test and undo before changing it.
If every plug serves a routine, follow the [pilot exception below](#starter-part-9--many-wi-fi-plugs-one-pilot-then-small-batches).
Leave safety devices out: **never expose locks, alarms or garage doors to voice**, including through a script or scene. The kit's allowed list is lights, switches and safe scene
scripts ([Alexa](../adapters/voice/alexa.md), [Google](../adapters/voice/google.md) and
[Apple](../adapters/voice/apple.md) policies).

<a id="starter-part-9--the-default-native-control-with-the-owners-choice-first"></a>
#### The default: native control, with the owner's choice first

Prefer bringing each device under Home Assistant through **Matter where the exact device supports it**, otherwise
Home Assistant's own **local integration for that maker**. This reduces dependence on a maker's cloud for everyday
control. Once native control works, the default MOVE route retires the maker's voice skill/account link and brings
voice back through Home Assistant Cloud's Alexa or Google link, with the same names and rooms. Cloud voice still
depends on that cloud and the Home Assistant box; native device control does not make cloud voice independent.

This is a **preference, never a hard rule**. Explain why you suggest the change, what it costs (including routines
to rebuild), and follow the owner's choice. Good reasons to keep a maker's hub or app include a local bridge that
keeps lights working when Home Assistant is down, no supported native integration, an app-only feature, or firmware
updates. **Keep the maker's hub, add it to Home Assistant** is a first-class route: for example, keep bulbs paired
to their Hue bridge and add the bridge through [Philips Hue](https://www.home-assistant.io/integrations/hue/).
The [Matter guide's bridge comparison](https://www.home-assistant.io/integrations/matter/#when-not-to-use-a-bridge)
notes that Hue's local integration exposes more features than its Matter bridge. Test which retained controls
actually work without Home Assistant; do not promise that every voice command or automation survives an outage.
Removing a cloud voice link is different from deleting an app, account or hub; keep anything the chosen integration
needs. The owner can also keep Alexa/Google exactly as it is and add native control alongside it, with no new
exposure back to that assistant.

<a id="starter-part-9--1-make-a-private-inventory-before-removing-anything"></a>
#### 1. Make a private inventory before removing anything

The owner opens Alexa or Google Home and, for every device being considered, notes its voice name, room,
groups, how it was connected, and every routine that uses it. Keep screenshots of the device and each routine
in the owner's private notes, outside the repository and chat; they may show personal details. Record the
trigger, conditions and actions well enough to rebuild the routine. Removing or replacing its device entry
can leave a routine pointing at the old entry even if the replacement has the same name.

**Required for every device, before selecting its route or changing anything:** the agent walks these clues
with the owner, even if another device of the same brand was just checked. An enabled skill is not proof of
this device's connection, and a previous session's route note must be checked against this device's screen.

- In Alexa, open the device's settings. A sharing setting, which may be labeled **Other Assistants and Apps**,
  is a clue that this entry uses Matter. The enabled-skills list may be labeled **Skills & Games > Your Skills**;
  check it for the maker too. A maker's skill can supply a separate cloud copy of the same physical device.
- In Google Home, inspect the device's settings for a sharing page, which may be labeled
  **Linked Matter apps & services**, and the list of linked maker services. Ask which service supplies this entry.
- In the maker's app, open **this device's** settings and identity page (it may be labeled **Device Info**).
  Read its exact model, hardware version and current firmware, then its Matter setup or connected-services page.
  For Tapo, the [maker's sharing guide](https://www.tp-link.com/us/support/faq/3573/) shows the Matter Setup Code
  option; absence needs a model-support check, not a guess. A Matter logo means capability, not proof that this
  particular Alexa/Google entry uses Matter. If skill and Matter copies both exist, inspect each entry's source
  and record them separately.
  If a version is missing, check the device label and maker's app or instructions without sharing identifiers.
  Record a version still missing as unknown. A listed model alone does not prove an unknown hardware or firmware
  version is supported; check the list's version requirements with the maker. If unclear, support stays unknown.
- Record `Matter`, `maker cloud`, `both` or `unknown` **per device**, with the clue used, current routines and the
  owner's chosen route. Keep addresses, serials, account details, Matter pairing codes and QR codes out of chat
  and the repository; the owner reads/enters private setup information directly in the apps.

[TP-Link's sharing walkthrough](https://www.tp-link.com/us/support/faq/3573/) illustrates the Alexa and Google
menus. [Google's Matter guide](https://support.google.com/googlehome/answer/13127223?hl=en) distinguishes Matter
from maker-linked devices. If the source is still unknown, stop before removing it and consult its maker's
instructions together. Never guess a pairing route or ask for account passwords or setup codes in chat.
If the label differs, open that device's settings and look for sharing with another assistant, or find the maker
in the enabled skills or linked-services list. Ask the owner to read the options, then check the linked official
guide. If none matches, stop and record the route as unknown; do not guess or remove the device.

<a id="starter-part-9--2-check-support-then-choose-a-route-for-this-device"></a>
#### 2. Check support, then choose a route for this device

A chat can check the exact model in the maker's official support page and Home Assistant's
[integration directory](https://www.home-assistant.io/integrations/). For Tapo/Kasa, use
[TP-Link Smart Home's supported-device guidance](https://www.home-assistant.io/integrations/tplink/#supported-devices),
including its linked hardware/firmware list; do not infer support from the brand or the name of the last lamp.
For Matter, check the maker's model/variant documentation and the
[Home Assistant Matter requirements](https://www.home-assistant.io/integrations/matter/). A Thread logo alone
is not Matter support. If a page cannot be read, ask the owner to open it and read the relevant compatibility
line; otherwise record support as unknown and stop before changing the working connection.

The TP-Link page lists models only. Its linked python-kasa list names the hardware and firmware versions that
were tested, not the only ones that work. A model on Home Assistant's list with a version missing from python-kasa
is unknown, not unsupported. The owner may still try the native add with KEEP (voice unchanged): it changes
nothing in Alexa, the maker app or the routines. The on and off test at the plug is the proof. If it fails, the
undo deletes only the new integration entry. Record the result as "unknown, tested by trying".

| Route | When it fits | What changes |
|---|---|---|
| **MOVE — default preference** | A supported native route exists and the owner wants voice through Home Assistant. | Add/test Matter first where supported, otherwise the local maker integration; retire the old maker voice path, expose one HA replacement, rebuild routines. |
| **SHARE** | This voice entry is already paired by Matter and another controller is supported. | Add Home Assistant as another controller, preserving the existing voice entry and routines. Do not expose a duplicate back. |
| **KEEP — hub or app retained** | The owner chooses independent local bridge control, needed app features/firmware, or a route without native support. | Keep the maker hub/app; add its supported HA integration if available. Hue bulbs can stay on their bridge. With no supported route, leave the device working as it is. |
| **KEEP — voice unchanged, native alongside** | The owner wants Alexa/Google and its routines left exactly as they are. | Add/test the supported native HA control but leave the maker skill/service and voice entries alone. Expose nothing back to that assistant. |

A maker cloud skill cannot be shared as a Matter connection; a compatible device may have a separate supported
Matter setup. SHARE and KEEP need no Home Assistant Cloud voice link. Keep existing routines in their current
system unless the owner separately chooses to move their logic. Record the choice, not a rule that the next
device must use it too.

If a Matter device is also on the maker integration's local support list, either supported route may be an option:
check the exact model and version and choose with the owner. Adding both can create duplicate Home Assistant
entries. Choose one route for the pilot, and check for duplicates before adding another.

Allow roughly 10–20 minutes per device for clues, setup and tests, or 15–30 minutes for a SHARE pilot. These are
planning estimates; support checks, account setup and routines can take longer. Stop at a safe boundary if there
is not enough time to test and record the undo.

<a id="starter-part-9--before-the-first-native-plug-add-check-alexa-exposure"></a>
##### Before the first native plug add: check Alexa exposure

If Home Assistant already has an Alexa link, open **Settings > Voice assistants** and inspect Alexa's
**Expose new entities** setting before adding a plug by either the native integration or Matter sharing.
First record the old setting privately, in the house CHANGELOG or your saved progress note.
It is off by default for Alexa, but an owner may have turned it on. If it is on, turn it off for this pilot
and the later batches. This preference affects future additions; it does not hide entities already exposed.

In **Settings > Voice assistants > Expose**, check the actual Alexa exposed list too, not just that preference.
Keep only the agreed safe entities exposed.

Also check whether Cloud Alexa uses a **YAML filter**; grayed out exposure controls are a clue.
The [official manual configuration guide](https://support.nabucasa.com/hc/en-us/articles/25619363899677-Configuring-Amazon-Alexa-to-work-with-Home-Assistant)
explains that a filter decides exposure instead of the UI setting.
Ask the person who maintains that configuration whether its rules include `switch` or otherwise expose a new plug.
Check the effective exposed list with them; an approved list today does not prove the next plug stays hidden.
Record whether exposure is controlled by the UI or a filter, without copying configuration or secrets into chat.

If a filter can expose it, pause before adding the plug until its effective exposure can be restricted.
The owner and configuration maintainer must agree that restriction and its undo first.
Do not guess a YAML edit or try to override the filter with the UI toggle.
If the filter or its effect cannot be checked, pause before adding the plug too.

If the Alexa link or exposure controls cannot be identified,
pause before adding the plug and follow the [official Alexa setup](https://www.nabucasa.com/config/amazon_alexa/).
If Alexa has no Home Assistant link, leave it unlinked while proving the native route.

After each add, before adding another plug, check the actual exposed list and the Alexa device list again.
For SHARE or KEEP with voice unchanged, the new HA plug copy must remain unexposed: keep the working
maker-skill entry (or original Matter entry), its name, room and groups, and retest its saved routines.
With UI-managed exposure, if a duplicate appeared, hide only the new HA copy from Alexa first.
If a filter controls it, stop the batch and use the configuration maintainer's restriction above instead.
Follow the official guide to remove its unwanted Alexa entry if it remains.
Do not remove the working maker entry or unlink its skill.

Retest original voice control and routines before continuing. MOVE also waits for section 3's deliberate
cutover; adding the plug is not permission to expose it.
The [official exposure guide](https://www.home-assistant.io/voice_control/voice_remote_expose_devices/)
explains the separate assistant preferences and the per-entity list.

Before adding the plug, check **Assist** too: its **Expose new entities** setting is on by default.
It can expose a new ordinary lamp plug even when Alexa's preference is off.
The owner chooses whether this pilot should be available to Assist.
Open **Settings > Voice assistants**, read the Assist setting and its exposed list, and record the original setting.
If the owner wants to choose each new entity, agree the undo and turn that preference off before the add.
Otherwise record the choice to keep automatic exposure on.
After each add, verify Assist's actual exposed list against that choice.
Ask before changing an existing entity's assistant selections.
Use the shared exposure-preference undo below for Assist as well as Alexa.
The [official exposure guide](https://www.home-assistant.io/voice_control/voice_remote_expose_devices/) describes these independent defaults.

Home Assistant Cloud's Alexa link does not require **Remote access**.
Keep the Cloud account signed in and set up the Alexa link separately.
[Nabu Casa documents the separate Cloud features](https://support.nabucasa.com/hc/en-us/articles/26508882007581-Remote-access-Security-aspects).
The [official Remote access action guide](https://www.home-assistant.io/actions/cloud.remote_disconnect/) confirms that voice assistants keep working when it is off.

<a id="starter-part-9--native-add-including-when-discovery-finds-nothing"></a>
##### Native add, including when discovery finds nothing

Use the chosen integration's current official setup. For a supported Tapo/Kasa light, plug or switch, open
**Settings > Devices & services > Add integration > TP-Link Smart Home** even when no discovery card appears.
Its [configuration guide](https://www.home-assistant.io/integrations/tplink/#configuration) describes the Host
and account fields: the owner enters the device's current local address and credentials in Home Assistant,
never in chat. Check the maker's device-information screen privately; do not guess an address.

Home Assistant stores a supplied maker login in its integration configuration on the box; that configuration is
included in backups. Encryption depends on the backup settings, so check rather than assume it. The owner enters
passwords only in the official form, never in chat or notes. Follow the maker's current two-step sign-in flow;
changing account security can require an existing voice skill to authenticate again. Do not assume it unlinked:
check the maker's instructions and retest voice. A second device may reuse the saved maker login; if offered,
the owner confirms it rather than entering or sharing the password again.

The integration controls supported devices locally, but newer devices still require maker-account authentication.
If access is refused, check the guide's Third-Party Compatibility requirement; the Tapo setting is documented
under **Tapo Lab > Third-Party Compatibility**. The owner approves and makes that change. Different subnets or
a guest network can prevent discovery/access; follow the integration's troubleshooting and the kit's optional
router-change rule. No discovery is not proof of no support. Do not reset a working device or install a community
driver just to get past an unknown result. For a retained Hue bridge, choose **Philips Hue** and follow its
[manual integration steps](https://www.home-assistant.io/integrations/hue/#configuration).

On either native route, confirm the exact entity, name and area, then have the owner switch it on **and off**
and report the physical result. If that fails, retain the working maker/voice connection and stop to diagnose.
A maker app may still be needed for initial setup, authentication, a feature or firmware; do not delete it or
its account because everyday switching now works locally.

The Home Assistant copy may have a different name from the voice entry: record both privately and follow the
[naming principle](../principles/naming.md) for the HA name. If the area does not exist, the owner can
create it in **Settings > Areas, labels & zones** and assign the device; phase 1 need not be complete. Keep the
voice name and room unchanged on KEEP.

Choose a suitable time for voice tests in a shared home, especially at night. For a wall switch, ask someone in
the room to check its own button and physical result too; do not operate it unexpectedly.

<a id="starter-part-9--share-leave-voice-working"></a>
##### SHARE: leave voice working

Use the [Home Assistant Matter guide](https://www.home-assistant.io/integrations/matter/) with the current
**Home Assistant Companion app**, not a browser. Confirm the Matter integration and server are ready; on normal
Home Assistant OS, adding that integration offers the official Matter server app. Installing it is a change
for the owner to approve. The phone/tablet needs the guide's supported OS, Bluetooth permissions and local
network access; Thread devices also need an appropriate border router.

From the existing controller, request a fresh sharing code for **this one device**. Alexa's setting may be
labeled **Other Assistants and Apps > Add Another**; Google has its linked-Matter setting. In the Companion app,
use **Settings > Connectivity > Matter > Add device** and the option for an already-used device, which may be
labeled **Yes. It's already in use.** Follow the current guide if the screen differs. With two devices, display
the code privately on one and scan/enter it on the HA Companion device; on one device, switch apps and paste it
privately. Sharing codes expire; request a fresh one if needed, never paste it or a QR into chat. Do not
factory-reset a working device or substitute the original box code for a fresh sharing code.

Test on and off in Home Assistant, the original assistant and the maker app where retained; check the physical
result and every saved routine. **Do not expose the HA copy back to the same assistant**. Undo SHARE by removing
only the Home Assistant controller/connection using the Matter guide's removal instructions, keeping the original
controller and device intact, then test its original controls/routines again. Do not factory-reset it to undo.

<a id="starter-part-9--a-new-matter-device-still-in-its-box"></a>
##### A new Matter device, still in its box

SHARE above starts from a device already working in Alexa or Google. A new device can start in either place, and
the first pairing decides which app holds it. Offer the owner these routes with their cost, then follow the choice:

- **Alexa first, then SHARE:** pair it in the Alexa app as a Matter device, test it there, then follow SHARE above.
  Alexa keeps its own entry; do not expose the Home Assistant copy back to Alexa.
- **Home Assistant first:** in the Home Assistant Companion app, **Settings > Connectivity > Matter > Add device**.
  Select the option for a new device (it may say **No, it's new**).
  If the screens differ, follow the current Matter guide. Bluetooth on, the phone or
  tablet close to the device; for a Wi-Fi device it must be on the 2.4 GHz network the device will use. Then set
  its name and area and test it. For Alexa voice, expose only that light through Home Assistant Cloud, as in
  section 4 step 3. The full kit's `adapters/radios/matter-thread.md` has the details.
- **The maker's app first:** set it up like a Wi-Fi plug, then use KEEP or MOVE above.

The pairing code on the box is a secret for the device's life: keep it in the password manager or the box, never
in chat or a screenshot. Thread devices also need a border router.

<a id="starter-part-9--3-move-home-assistant-first-old-voice-entry-second"></a>
#### 3. MOVE: Home Assistant first, old voice entry second

The owner approves the device, route, subscription cost if any, and interruption first. The agent explains;
the owner signs in, clicks and tests. First inventory all affected routines and use a pilot device with none,
or follow the [pilot exception below](#starter-part-9--many-wi-fi-plugs-one-pilot-then-small-batches).

1. **Add and prove native Home Assistant control**, using section 2: Matter where supported, otherwise its local
   maker integration. Confirm on/off physically before removing anything. If it fails, stop with the old voice
   path intact. Keep a needed maker app, account and hub.
2. **Prepare the Cloud voice route with the owner.** Show the separate subscription cost and current-pricing link
   in `network-and-backups-first.md` section 2. Use the official
   [Alexa link](https://www.nabucasa.com/config/amazon_alexa/) or
   [Google link](https://www.nabucasa.com/config/google_assistant/). Agree a narrow exposure list. Declining Cloud
   means choose KEEP or pause this cutover; do not subscribe or open a router port. Linking Cloud alone is not
   permission to expose devices, and the voice-skill linking below needs at least one exposed entity.
3. **Retire the confirmed old maker voice path.** Remove the old voice copy or unlink its maker skill/service,
   as its current screen permits. Read the confirmation first: unlinking an account may affect all its devices.
   Do not delete the maker account or remove a device from its app if native access still needs it. Disable the
   maker's Alexa skill or Google account link only after **all devices it supplies have tested native control**.
   If individual removal is unavailable or discovery brings it back, stop the pilot cutover and agree batch
   preparation: keep familiar voice working while testing the remaining native controls, then unlink once.
   Do not invent a per-device exclusion setting or call a duplicate a completed MOVE.
4. **Expose one Home Assistant replacement per device**, with the original voice name, room and groups. Follow
   the linked Cloud guide: select the approved entity, link the Home Assistant Smart Home skill in Alexa or
   Home Assistant Cloud in Google Home, then discover/sync. Activation may discover automatically; check the
   resulting sources/list too. Keep SHARE/voice-unchanged KEEP devices unexposed. Exactly one entry should
   control each physical device. Restore names and groups explicitly rather than relying on discovery.
5. **Rebuild and test each inventoried routine against the replacement entry.** Reusing a name does not repair
   a reference or restore a silently deleted action. The owner tries every saved voice command, on and off, and
   each routine, checking the physical results. For multiple devices, finish the pilot, then routine devices
   with their routines checked after each change; leave a sunset/time routine for last when practical. Agree
   how to observe its real trigger/off time; running actions alone is not trigger proof. Never speak or send
   a message as the agent to test the work.
6. **Record actual results, the chosen route and undo** in the house CHANGELOG, or the owner's saved progress note
   from [Coming back](#starter-part-1--coming-back-without-an-agent-on-the-box) when no house
   files exist. Keep private names/screenshots in private notes. Undo: hide the replacement exposure, restore
   the inventoried maker voice link/entry using its instructions, restore groups and each saved routine, then
   have the owner test original control. Keep working HA integration unless its removal is separately chosen.

For KEEP with voice unchanged, stop after adding/testing native control, retest the original voice/routines and
the maker app as a control, and record that nothing was re-exposed or unlinked. To undo the native addition, the
owner can delete its Home Assistant integration entry; check first whether it also controls other devices, since
deleting the entry removes those connections too. Retest the original voice path and routines afterward. A safe
pause is before cutover, or after the device, commands,
groups and routines have passed and the note includes undo. Do not leave a half-retired routine overnight.
For every route, also use [the exposure-preference undo](#starter-part-9--undo-the-exposure-preference) before closing the pilot.

<a id="starter-part-9--undo-the-exposure-preference"></a>
#### Undo the exposure preference

This preference undo applies to SHARE, KEEP, MOVE and the scene-script lesson.
Repeat the recorded-setting and undo decision for Assist if its preference changed.

At an undo or a pause, revisit the old automatic-exposure setting you recorded before the pilot.
Ask the owner whether to keep it off or restore the earlier value.
Explain that turning it back on can expose future entities; it does not remove copies already exposed.
Do not restore it automatically. Record the owner's choice privately and apply only that choice.

If a filter controls exposure, its agreed restriction and undo need the configuration maintainer too.
Recheck the actual exposed list, Alexa entries and original routines after any change.

The Alexa and Google Cloud pages above document account linking, entity exposure and discovery/sync. The
inventory, staged order and routine checks are the kit's migration procedure; no live migration was tested here.

<a id="starter-part-9--many-wi-fi-plugs-one-pilot-then-small-batches"></a>
#### Many Wi-Fi plugs: one pilot, then small batches

For Tapo or another maker, check each plug's exact model and versions as section 1 describes.
Do not assume every plug in a multipack has the same support.
Choose SHARE when the existing Alexa entry uses Matter and preserving its routines is the goal.
Choose KEEP (voice unchanged), with the supported maker integration alongside Alexa, when Matter is absent
or a needed feature is missing there.
Both routes can leave Alexa unchanged, with no duplicate Home Assistant exposure.
MOVE stays the kit's default preference for voice through Home Assistant Cloud; when the owner wants existing
Alexa routines left unchanged, choose SHARE or KEEP for that plug instead.

Prove one lamp plug first, including its physical button, maker app, Home Assistant, Alexa and any existing routine.

If every plug has a routine, choose the least disruptive one.
Require the owner's saved complete routine and agreed interruption before the pilot.
After each change, test every action in that routine and check the physical result.
If a result fails, restore the original controls and routine before continuing.
Retest its original voice commands, groups and routine triggers before declaring it restored.
If the interruption or restoration cannot be agreed, pause before the pilot.

Finish its checks before another plug changes.
Then agree a small batch, such as three plugs, and repeat the per-device checks from sections 1 and 2.
The batch size is a plan, not proof that the network or models support it.

Keep a private checklist with one row per physical plug:

| Record | What closes the row |
|---|---|
| Model, versions and connection source | Support checked; SHARE, KEEP or MOVE chosen for this plug. |
| Home Assistant and original Alexa entry | On and off observed at the plug; one Alexa entry controls it. |
| Every saved routine, room and group | Targets confirmed; physical results checked, including the real scheduled trigger when applicable. |
| Undo and next step | Results saved; any unchecked step remains open. |

Keep private names and screenshots outside the repository and chat.
Stop the batch at the first failure and use section 3's undo for that route.
Leave untouched plugs on their original controls.
For MOVE, an account-wide skill removal still waits until every device it supplies has proven native control.
Preparing three plugs does not permit unlinking the maker skill for all the others.
Check for duplicate Alexa entries again after discovery.

When one safe plug works in Home Assistant, continue to [your first automation](#starter-part-10).
You need not migrate every plug before that lesson.
Its script can later become the voice control below.

<a id="starter-part-9--4-a-safe-scene-script-with-an-alexa-phrase"></a>
#### 4. A safe scene script with an Alexa phrase

The goal is one phrase that sets chosen lamps, without exposing unrelated controls.
This example uses two harmless lamp plugs already proven in Home Assistant.
If you have only one, use that one throughout.
You make the changes on the iPad; the chat explains one step and waits for done.
Use the Home Assistant Companion app for Matter setup and the Alexa app for Alexa settings.
Keep sign-ins and sharing codes in those apps, never in chat.

1. In **Settings > Automations & scenes > Scripts**, create a script named **Reading lamps**.
   Add **Switch: Turn on** for the two exact lamp switches selected from your device list.
   Use **Light: Turn on** instead for a light entity; never copy a made-up entity id.
   Check every action and target before saving.
   Do not include locks, alarms, garage doors, messages, speakers or a call to an unchecked script.
2. Run the saved script yourself and observe both lamps.
   Read its trace together, using [the lesson's test method](#starter-part-10--6-you-try-it-the-agent-reads-the-result).
   Agree how you will restore each lamp's previous state.
   Running this script skips any condition in an automation that might otherwise call it.
3. If Cloud is not linked, review its price and follow the [official Alexa setup](https://www.nabucasa.com/config/amazon_alexa/).
   Open **Settings > Home Assistant Cloud** for the Cloud account and Alexa setup.
   Follow its Alexa link; the current official guide uses **Settings > Voice assistants** to enable Alexa.
   Open **Settings > Voice assistants**.
   On the **Amazon Alexa** card, select its **entities exposed** button, which includes the current count.
   This opens the Alexa-only Expose view. A new script may not appear in this table yet.
   Then choose **Expose entities** and select the individual script **Reading lamps**.
   The dialog title must be **Expose entities**, with the subtitle **to Amazon Alexa**.
   If the subtitle names more than Alexa, cancel and return to the Amazon Alexa card.
   Confirm only after the dialog limits exposure to Alexa only and the selected entity is the intended script.
   Avoid the unfiltered add dialog and the script's master exposure switch; both can enable other assistants.
   If the script already has other assistants selected, record those choices and ask before changing them.
   Check the assistant icons afterward against the owner's choices.
   If a YAML filter disables these controls, use the pre-add check above and pause until exposure can be restricted.
   Keep **Expose new entities** off for Alexa. Do not expose the individual plugs as well.
   Keep SHARE and KEEP plug copies unexposed while Alexa retains their original entries.
   The kit permits only lights, switches and safe scene scripts, even though Cloud supports more types.
4. In the Alexa app, link the **Home Assistant Smart Home** skill with your Cloud account if needed.
   Discover devices, then find the script by its name; Alexa can present it as a scene.
   Confirm that the chosen entry comes from Home Assistant, not a similarly named maker device.
   If it is missing, check exposure, account linking and discovery before changing anything else.
5. Say **Alexa, turn on Reading lamps** yourself and observe both lamps.
   The [official script instructions](https://www.home-assistant.io/integrations/alexa.smart_home/#script) describe this direct command.
   Use short, distinct names without competing device or group names.
   If Alexa hears another name, check its command history and choose a clearer one.
   If the history shows the right words but Alexa gave its own reply, the phrase clashes with a built-in
   command. A single word or a greeting, such as "evening", does this; choose two or three words instead.
   Do not rename existing devices just to fit this example.
6. For a custom phrase, create a new routine in the Alexa app.
   Choose a voice trigger such as **Time to read**.
   Add a Smart Home scene action for **Reading lamps** where your app offers it, then save.
   Follow [Amazon's routine guide](https://www.amazon.com/gp/help/customer/display.html?nodeId=G2PYLKJN3XVZ55EQ) if labels differ.
   If the script is not available there, keep the proven direct command; do not substitute an unrelated action.
7. Return the lamps to their agreed starting states, then say **Alexa, time to read** yourself.
   Confirm the phrase, the selected routine, the script trace and both physical lamps.
   The routine's play button alone does not prove its voice trigger.
   Do not mark this route complete when only the direct command works.

Turning off a running script stops its remaining steps; it does not reverse lamp changes already made.
For a separate lights-off phrase, create and test a safe script with explicit off actions.
The script is the list of actions; an automation or Alexa routine supplies the trigger.
See [the automation rules](../principles/automations.md#reusing-a-script-for-voice-and-automations) before adding a schedule.

Record actual results and undo in the house CHANGELOG, or the saved chat progress note when no house files exist.
Undo this example by disabling its new Alexa routine and hiding only this script's Alexa exposure.
Restore the lamps manually to their agreed previous states.
Keep existing maker routines and the working Home Assistant device connections.
Before deleting the new script, check whether another automation or dashboard uses it.
Revisit [the exposure-preference undo](#starter-part-9--undo-the-exposure-preference) if this lesson changed that setting.

The Home Assistant and Nabu Casa guides were readable on 2026-11-16.
The Amazon routine guide could not be read here; the owner must open it if the app's labels differ.
No live device or account was used to test this walkthrough.

<a id="starter-part-9--if-it-does-not-work"></a>
#### If it does not work

- **The voice app shows a stale state:** check the physical device and maker app first, then refresh the voice app
  and retry. If it remains stale, consult the assistant's troubleshooting; keep the working connection and do not
  delete an entry merely to refresh its display.
- **Two copies answer:** check which connection supplies each. On SHARE, turn off the extra Cloud exposure.
  On MOVE, finish retiring the old maker copy only after Home Assistant control works. Do not delete at random.
- **A routine stopped after a rename or move:** open the saved routine and compare it with the private inventory.
  If an action still names the old device, choose the current device entry. If the action is gone, add it again
  in the routine (the assistant's app has an add-action step), or recreate the routine. With no record of the
  original action, mark it unknown and ask the owner; do not guess. Restore its room and group. The owner tests the saved trigger and the physical result.
- **Matter sharing fails:** keep the existing connection. Check the current app, Bluetooth permissions and that
  the phone, box and device can communicate on the home network rather than an isolated guest network. Matter
  needs local IPv6; Thread devices also need a suitable border router. Use the official troubleshooting steps;
  ask before changing router settings, and do not factory-reset a working device just to retry sharing.
- **A skill brings devices back:** the maker link still supplies them. Revisit the remaining-device plan before
  unlinking it. Recheck duplicates after the next discovery too.

<a id="starter-part-9--siri-and-apple-home"></a>
#### Siri and Apple Home

[HomeKit Bridge](https://www.home-assistant.io/integrations/homekit/) exposes selected Home Assistant entities to
Apple Home and Siri; HomeKit Device brings supported HomeKit accessories into Home Assistant. These are different
routes. Matter sharing is another choice for Matter devices. Follow `../adapters/voice/apple.md`, keep the same
narrow safe list, and avoid publishing a second copy of an accessory already in Apple Home. The owner keeps all
pairing codes private. Existing Apple Home scenes and automations need the same inventory and retest treatment.

---

<a id="starter-part-10"></a>
## Part 10: `00-start-here/your-first-automation.md`

<a id="starter-part-10--your-first-automation-with-the-agent-beside-you"></a>
### Your first automation, with the agent beside you

You can make one small thing yourself before the agent starts building for you. Once Home Assistant has at
least one device, the agent offers this lesson once, before its first build. It explains one step, waits while
you click, then checks what happened. A tablet or computer works. There is no quiz, and no YAML unless you ask.
You can pause or say skip; the agent records that answer in `house/docs/backlog.md` and keeps helping.

The normal interview and your limits still apply. Choose a small light or a plug with a harmless lamp attached,
not a heater, lock, alarm, garage door, message or speaker. The agent reads the devices you actually have and
asks what you would like. These are suggestions, not devices to buy:

| If it fits your devices and wishes | What it teaches |
|---|---|
| A lamp plug that turns on at a chosen time | A clock can start an automation; choose an off time too. |
| A light that comes on at sunset | A trigger can follow the sun rather than a fixed clock time. |
| A Guest mode toggle that changes one light's behavior | A helper stores your choice, and a condition checks it. |
| A Good night button for one safe light | A script gives a list of steps a name, and a dashboard can run it. |

Pick one, change it, or suggest your own. The agent adapts the steps to that choice and says which exact device
will change before you save anything. If you have no suitable safe device, leave the offer for later.

<a id="starter-part-10--1-write-your-own-small-board-row-first"></a>
#### 1. Write your own small board row first

In `house/docs/board.md`, write one row with the agent coaching: a new unique code, your plain name for the
lesson, lane `owner`, a small point estimate, status BACKLOG, a link and any decision still needed. Follow
`../templates/docs/board-format.md`; add its plain-name entry in `house/docs/card-names.tsv` too. If the board
has not been introduced, the agent explains the six columns and helps you start it from the template; do not
leave its sample work as real work. You type your row and choose its size. Before clicking to build, mark it
IN PROGRESS with the time. This can count toward `L2-own-row`; doing the lesson does not pass all of level 2.

Agree the intended behavior, a quick test and an undo. The following worked example uses one ordinary light:
turning on a new lesson toggle runs a script that turns the light on, but only when the light is off. The other
suggestions use the same pieces with a different trigger or condition.

<a id="starter-part-10--2-make-a-helper-a-choice-on-the-screen"></a>
#### 2. Make a helper: a choice on the screen

A helper is a value you can change without touching a physical device. In **Settings > Devices & services >
Helpers > Create helper**, choose **Toggle** and give it a clear name, such as **Try the light**. Create it and
leave it off for now. Choose the actual helper from the list in later steps; do not copy an invented identifier.
For the Guest mode option, call it **Guest mode** and decide together what on should mean.

The agent explains each screen and waits for done. The [official toggle guide](https://www.home-assistant.io/integrations/input_boolean/)
shows the current screens. It stores on or off; it is not a real light switch.

<a id="starter-part-10--3-make-a-script-a-named-list-of-steps"></a>
#### 3. Make a script: a named list of steps

Open **Settings > Automations & scenes > Scripts**, create a new script and add one action: turn on the exact
light you chose. Give the script a clear name such as **Lesson light on**, then save. The agent points out the
target before you confirm it; do not choose a whole area for this first try. For Good night, choose a safe light
off instead. You can add steps later, one at a time.

A script runs its steps when something calls it, including you pressing a dashboard button. An automation can
call the same script. The [official scripts guide](https://www.home-assistant.io/docs/script/)
shows how the steps run. Ask the agent to explain an unfamiliar action before selecting it.

<a id="starter-part-10--4-make-an-automation-when-only-if-then-do"></a>
#### 4. Make an automation: when, only if, then do

Open **Settings > Automations & scenes > Automations > Create automation > Create new automation**. In the
visual editor, add these parts for the worked example:

- **When**: a state change of your new lesson helper from off to on. This is the **trigger**, the event that
  starts a run. Use the helper's actual entry, not the physical light.
- **And if**: your chosen light is off. This is the **condition**, a question checked when the trigger happens.
  If it is false, the automation stops. It does not wait for the light to become off.
- **Then do**: run your saved **Lesson light on** script. This is the **action**, what happens after the check.

Save with a name you recognize and check whether it is enabled. For a scheduled plug or sunset choice, the
agent substitutes that trigger, and uses the helper as an optional allow/skip condition. Do not silently add
an off time or other behavior you have not chosen. The [visual editor](https://www.home-assistant.io/docs/automation/editor/)
and [trigger guide](https://www.home-assistant.io/docs/automation/trigger/) explain these parts in the current UI.

<a id="starter-part-10--5-put-your-controls-on-a-dashboard"></a>
#### 5. Put your controls on a dashboard

Use a dashboard you already edit, or make a small practice dashboard. Keep the automatic Overview dashboard
as it is: taking control changes how it updates. In the dashboard's edit screen, add an **Entities** card with
your helper and script selected from the real entity list. The helper's row shows its state and lets you
change it; the script's row offers a run control. Save the card and leave edit mode. If the script row does not
offer a run control on your screen, use the card editor to add a button with a **Perform action** tap action
that runs that exact script; the agent walks the current screen rather than inventing a menu.

[Entities cards](https://www.home-assistant.io/dashboards/entities/) can show states and buttons, and
[dashboard actions](https://www.home-assistant.io/dashboards/actions/) define what a tap does. Check the target
before you tap: running the script bypasses the automation's condition.

<a id="starter-part-10--6-you-try-it-the-agent-reads-the-result"></a>
#### 6. You try it; the agent reads the result

The agent uses read access only: it may inspect the saved settings, states, last-run time and trace, but it
creates, edits, reloads and triggers nothing. If that access is missing, you read the screen back; the result
stays unverified until it can be checked. Neither path grants broader permissions.

1. You run the script once from the dashboard, and watch the chosen light. This checks the script and button.
2. For the worked example, you turn the light off, set the helper off, then turn the helper on. Watch the light
   turn on. This is a real trigger test. Leaving the helper on does not trigger it again.
3. Open the automation's trace together. Check that the helper change started it, the condition passed, and the
   saved script ran. The agent compares the read state and last-run time with what you saw physically.
4. With the light already on, you set the helper off and on again. The trace should stop at the false condition.
   That is the intended result. For other choices, the agent proposes an equally small test of the chosen event;
   a temporary near-future test time must be restored and recorded before calling a sunset schedule finished.

**Run actions** is not proof that a trigger or condition works. If something fails, say what you saw, check the
selected helper, target, enabled state and trace, then change one thing yourself and retry. A failed or unread
trace is reported as failed or not checked, not passed. Nothing sends a message or speaks for a lesson test.

<a id="starter-part-10--7-write-down-what-you-made-and-its-undo"></a>
#### 7. Write down what you made, and its undo

You write a short dated CHANGELOG entry with the agent coaching, using `../templates/docs/CHANGELOG.md`: why,
your go, the new helper/script/automation/card, what each test actually showed, and undo. A useful first undo is:
disable the lesson automation, remove only its new dashboard card, and return the light to its previous state.
Disabling an automation does not stop a script it already started. An adapted lesson can start a script with a
delay through `script.turn_on`, and that script runs on its own. Read the automation's actions to find that exact
script. Open **Settings > Tools > Actions**, choose `script.turn_off`, select that script only, and select
**Perform action**. Do not stop other scripts. Then check the light again after the delay has passed. ([Scripts](https://www.home-assistant.io/integrations/script/#waiting-for-a-script-to-complete);
[Turn off script](https://www.home-assistant.io/actions/script.turn_off/).)
If you later delete the lesson script/helper, check that nothing else uses them first. Do not delete a preexisting
control or restore the whole house just to remove the lesson.

Put the lesson's code in the entry, link your board row to it, and record the outcome. Mark DONE only when the
chosen behavior and checks passed; otherwise use PARTIAL or BLOCKED with what remains. If you stopped early,
that is a valid stopping point. The record helps the next session resume rather than offer the lesson again.

<a id="starter-part-10--next-let-alexa-run-your-safe-script"></a>
#### Next: let Alexa run your safe script

If your plugs already work in Home Assistant, you can reuse the script before migrating every other plug.
Follow [the voice guide's scene-script example](#starter-part-9--4-a-safe-scene-script-with-an-alexa-phrase) for Cloud exposure, a phrase, tests and undo.
Expose only the approved safe script; leave original Alexa plug entries alone on SHARE or KEEP.
Check the script's own actions and targets first: Alexa does not run the condition in your lesson automation.
The agent still explains while you sign in, save and speak the test phrase.

What you just learned: a **helper** keeps a choice, a **script** names some steps, an **automation** connects an
event and a check to those steps, and a **dashboard** puts the controls in reach. You built it. The agent starts
its normal build loop only after this lesson, or after you say skip, and still asks for your go on the next item.

*UI references checked on 2026-11-10; no live device was used to validate this lesson. The kit's board and
CHANGELOG formats above supply the record rules. If a menu differs, follow the current official page and your
screen rather than guessing.*

---

<a id="starter-part-11"></a>
## Part 11: `adapters/agents/claude-code.md`, section "Install on the box and sign in"

<a id="starter-part-11--install-on-the-box-and-sign-in"></a>
#### Install on the box and sign in

*Moved here from `00-start-here/README.md`, path B, steps 2 and 3 (CX-SWEEP).*

1. **Install the Claude Code app.** Settings > Apps > Install app > the three dots (top right) >
   Repositories > paste `https://github.com/robsonfelix/robsonfelix-hass-addons` > Add. Back in the store, find
   **Claude Code**, Install, Start, then **Open Web UI** (it also appears in the sidebar). This is an app from the
   app store, not the Marketplace. The Marketplace is built in and is not needed for this app.
2. **Sign in.** The web UI is a terminal. Type `claude` and press Enter. It shows a link: open it in a browser (your
   phone is fine), sign in to your Claude account there, copy the code it gives you, and paste it back into the
   terminal. The terminal's paste keys are a computer's (`Shift+Insert` or `Ctrl+Shift+V`); if paste does nothing
   on a phone, type the code (it is short), or do this one step from a computer's browser. Untested on a phone until
   a lab run says otherwise. The sign-in is stored on the box and travels inside its backups, so from now on a backup
   file is a secret: keep it where you keep passwords.

---

<a id="starter-part-12"></a>
## Part 12: `adapters/agents/codex.md`, section "Install on the box and sign in"

<a id="starter-part-12--install-on-the-box-and-sign-in"></a>
#### Install on the box and sign in
*Lab notes, not yet walked end to end (CX-SWEEP).* The app route: a Home Assistant app wraps the client and
gives it a chat page (see "What is different"); which app repository and which steps the kit recommends is not
decided, so this page has no click-by-click walk-through. Not verified: the app's install steps on a fresh box.
Sign-in is the device code described under "What is different": `codex login --device-auth`, then enter the code on
any phone or computer. The sign-in lives in the client's home folder, so on the box treat a backup as a secret, as on
the first runtime.
