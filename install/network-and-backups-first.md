# Network and backups first

*Status: written (O3a, 2026-10-13), from the official Home Assistant documentation as of October 2026 (the
installation, onboarding and backup pages). Every hardware guide ends here. Re-check the official pages when a step
does not match what you see: menus move between releases.*

**For the agent:** walk the person through this file one numbered step at a time and wait for "done" before the
next. Phase 0 is not finished until every box in "Done when" is ticked or the owner has chosen otherwise, one practice at a time, under "The owner's choice" below. You do not touch the network equipment
yourself; the person does, with you reading their router's screen back to them if they need help.

## Why this comes before anything else
Every later step needs two things: a working way to reach the box, and a backup somewhere other than the box.
A stable name or address avoids broken bookmarks and connections. A router reservation is optional; if you
decline it, record the working route and how to recover when a DHCP address changes. The first week's mistakes
are cheap only if you can roll them back.

## 0. On an existing install, back up locally and update first
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

## 1. Find the box's address, and keep it
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

## 1b. What the network must allow
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

## 2. Remote access (choose later, but choose on purpose)
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

## 3. Backups from day one
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

### Route A — Home Assistant Cloud, offered first
First complete the Cloud-copy check at the start of this section, including a confirmed download of any wanted backup.
Do not enable this location until that check is complete, even on a fresh install.
Use the subscription described in section 2; there is no separate backup fee.
Sign in under **Settings > Home Assistant Cloud**, then enable its backup location as above.
It holds **one encrypted backup, up to 5 GB**: the latest saved there replaces the previous one.
Keep the saved copy and emergency kit privately off the box.
If the selected data exceeds the limit, reduce what is included or choose another destination.
A subscription alone is not a completed backup.

### Route B — Google Drive, free within the account's storage allowance
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

### Route C — a share, or a USB copy with its limits recorded
A NAS or another computer can provide an automatic destination: **Settings > System > Storage > Add network
storage**, usage **Backup**, then select it under backup Locations. It must be awake and writable at backup time.
A share in the same building survives the box failing, but does not replace an off-site copy.

A USB drive kept away from the box is a useful hand-copy destination. It is **not automatic** unless an automatic
copy process is configured and a scheduled run is verified. A drive left beside or attached to the box is not an
off-site copy. Do not erase or repurpose a drive to make this checklist pass.

### Make and check the first copy
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

## 4. Updates, from day one
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

## 5. The household's phones
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

## 6. Giving the agent access
`install/agent-access.md`: a user and a token for the agent, a read check, and (at the first build) a deploy path.

## The owner's choice
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

## Done when
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
