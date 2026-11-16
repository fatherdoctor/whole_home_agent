# Keep familiar voice control while adding Home Assistant

*Guide checked against the linked official pages on 2026-11-10. Menu names may change; follow the owner's
screen and the current linked instructions. This is a plan the owner carries out, not permission for the agent
to change devices or accounts.*

The goal is to control each chosen device from Home Assistant while keeping the voice commands the household
already uses. Ask which assistant they use and what it controls. Start with one ordinary light or switch
**that no routine uses**, when a brief interruption is acceptable; agree its test and undo before changing it.
If every plug serves a routine, follow the [pilot exception below](#many-wi-fi-plugs-one-pilot-then-small-batches).
Leave safety devices out: **never expose locks, alarms or garage doors to voice**, including through a script or scene. The kit's allowed list is lights, switches and safe scene
scripts ([Alexa](../adapters/voice/alexa.md), [Google](../adapters/voice/google.md) and
[Apple](../adapters/voice/apple.md) policies).

## The default: native control, with the owner's choice first

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

## 1. Make a private inventory before removing anything

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

## 2. Check support, then choose a route for this device

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

### Before the first native plug add: check Alexa exposure

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

### Native add, including when discovery finds nothing

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

### SHARE: leave voice working

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

### A new Matter device, still in its box

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

## 3. MOVE: Home Assistant first, old voice entry second

The owner approves the device, route, subscription cost if any, and interruption first. The agent explains;
the owner signs in, clicks and tests. First inventory all affected routines and use a pilot device with none,
or follow the [pilot exception below](#many-wi-fi-plugs-one-pilot-then-small-batches).

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
   from [Coming back](../00-start-here/from-a-chat-app.md#coming-back-without-an-agent-on-the-box) when no house
   files exist. Keep private names/screenshots in private notes. Undo: hide the replacement exposure, restore
   the inventoried maker voice link/entry using its instructions, restore groups and each saved routine, then
   have the owner test original control. Keep working HA integration unless its removal is separately chosen.

For KEEP with voice unchanged, stop after adding/testing native control, retest the original voice/routines and
the maker app as a control, and record that nothing was re-exposed or unlinked. To undo the native addition, the
owner can delete its Home Assistant integration entry; check first whether it also controls other devices, since
deleting the entry removes those connections too. Retest the original voice path and routines afterward. A safe
pause is before cutover, or after the device, commands,
groups and routines have passed and the note includes undo. Do not leave a half-retired routine overnight.
For every route, also use [the exposure-preference undo](#undo-the-exposure-preference) before closing the pilot.

## Undo the exposure preference

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

## Many Wi-Fi plugs: one pilot, then small batches

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

When one safe plug works in Home Assistant, continue to [your first automation](../00-start-here/your-first-automation.md).
You need not migrate every plug before that lesson.
Its script can later become the voice control below.

## 4. A safe scene script with an Alexa phrase

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
   Read its trace together, using [the lesson's test method](../00-start-here/your-first-automation.md#6-you-try-it-the-agent-reads-the-result).
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
Revisit [the exposure-preference undo](#undo-the-exposure-preference) if this lesson changed that setting.

The Home Assistant and Nabu Casa guides were readable on 2026-11-16.
The Amazon routine guide could not be read here; the owner must open it if the app's labels differ.
No live device or account was used to test this walkthrough.

## If it does not work

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

## Siri and Apple Home

[HomeKit Bridge](https://www.home-assistant.io/integrations/homekit/) exposes selected Home Assistant entities to
Apple Home and Siri; HomeKit Device brings supported HomeKit accessories into Home Assistant. These are different
routes. Matter sharing is another choice for Matter devices. Follow `../adapters/voice/apple.md`, keep the same
narrow safe list, and avoid publishing a second copy of an accessory already in Apple Home. The owner keeps all
pairing codes private. Existing Apple Home scenes and automations need the same inventory and retest treatment.
