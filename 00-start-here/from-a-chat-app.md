# Starting from a chat app

*Status: written (KIT-CHAT0, 2026-11-10); made generic and corrected after its first dry run (KIT-CHAT0.g,
2026-11-10). The fourth way in: a person with a general chat assistant app, and no agent running on a Home
Assistant box yet. Walked once, in a stand-in dry run of start **4** (a box someone else set up, signed in from one
device; KIT-DRY.s2): its findings are folded in below. Starts 1, 2 and 3 have not been walked from a chat app yet.
For the chat assistant and the person together. If your chat app cannot open web addresses, `chat-app-starter.md`
in this folder is this page with the guides it needs, as one file to attach.*

## For the chat assistant reading this

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
   [Jumping ahead](#jumping-ahead). For other changes, say once, in a sentence, what the rule protects against,
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

## Jumping ahead

If the owner asks to go straight to the ChatGPT or Claude app, take this route instead of completing the usual
interview and setup first. If two-step login is half done, finish it (setup key saved and fresh sign-in confirmed)
or turn it off so it remains off; never leave it half on. It needs a running Home Assistant installation that
supports apps. Starting from nothing, finish the install in "Which start is yours" and onboarding first, then
return here; if apps are not supported, say so rather than claiming the app can be installed yet.

Do only these checks and steps before the app install:

Open [First change on a box already running](#first-change-on-a-box-already-running).
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

## The opening

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

## First change on a box already running

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

## Which start is yours

From the answer to question 2:

- **(1) Nothing yet.** Choose the hardware first, then go to start 2 or 3.
- **(2) A machine with nothing on it yet:** a Raspberry Pi, a mini PC, or a Home Assistant Green or Yellow.
- **(3) A virtual machine on a server** the owner or someone in the house already runs.
- **(4) Home Assistant already running, anywhere:** on any hardware or virtual machine, set up by the owner or by
  someone else, signed in to or still asking for its first account. A box someone set up and handed over is this
  start.

All four end at the same place: Home Assistant running, the owner account theirs alone with two-step login, backups
on with a copy off the box, and the hand-off note.

## 1. Nothing yet: choose the hardware

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

## 2. A machine with nothing on it yet

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

## 3. A virtual machine on a server

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

## 4. Home Assistant already running

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

## Onboarding (starts 2, 3, and 4 if it asked to create an account)

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

## Your account, made yours

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

## Every start, tonight

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

## The hand-off to the agent on the box

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

## Coming back without an agent on the box

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
   backup first using [network and backups](../install/network-and-backups-first.md); keep the emergency kit
   privately off the box. Do not begin a change that cannot be left safely within tonight's time.
3. **Use a kit guide as the plan.** For devices and familiar voice commands, use
   [Keep familiar voice control](../install/voice-assistants.md): inventory first, check each device's connection
   clues, agree its route and preserve routines. For several devices of the same brand, ask for their connection
   clues together, but record and check each device separately. For a maker's supported-model list, ask the owner
   to read the list once and report whether each model appears: opening each model-support page costs a round trip.
   Do not assume a model is supported from its brand or another model; leave it unknown until checked.
   For a first small automation, use
   [Your first automation](your-first-automation.md): the owner makes a safe helper, script or automation in the
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

## Git can wait

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

## Where to start, and when to move to the box

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

## What the chat app cannot do

- See the box. It knows only what the owner tells it and what the screenshots show.
- Remember an earlier evening in a new conversation; the owner supplies the hand-off and latest progress notes.
- Open more than a page or two of this repository, in some apps. If it says it cannot read a file this page
  names, give it `chat-app-starter.md` instead (download it from this folder and attach it).
- Run anything. Every step is the owner's; the chat reads, explains and waits.
