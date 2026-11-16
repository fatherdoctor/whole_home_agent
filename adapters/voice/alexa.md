# Alexa

*Status: notes (O1). Used in practice. Templates: `templates/`.*

## What is different
- Home Assistant Cloud's Alexa link does not require **Remote access**. Keep the Cloud account signed in and configure Alexa separately.
  [Nabu Casa documents the separate Cloud features](https://support.nabucasa.com/hc/en-us/articles/26508882007581-Remote-access-Security-aspects).
  The [official Remote access action guide](https://www.home-assistant.io/actions/cloud.remote_disconnect/) confirms that voice assistants keep working when it is off.
- Exposure goes through Home Assistant's cloud subscription (or a self-hosted skill). Each exposed entity becomes
  a device in the Alexa app; changes need a sync, and stale devices may need deleting in the app.
- Commands from Alexa arrive in Home Assistant under the cloud system user, not under a person.
- Speaking on Echo devices needs a community integration with a real account login that the owner performs in the
  UI; its sessions expire and it is not load-bearing.

## What the principles need from it
- **Exposure is lights, switches and scene scripts only** (`safety-and-security.md` rule 2). No sensors, media
  players, locks, alarm or app switches. Do not expose the Echo devices' own media players back to Alexa.
- **Attribution.** To know what Alexa did, read the assistant's own command history; the system user tells you
  only that a cloud assistant acted.
- **Notifications (rule 23).** Speakers are the fallback voice; a wall panel, where there is one, speaks first.
  Never speak and push the same countdown on two devices at once.
- **Working with the agent.** Logging into the assistant account is the owner's act in the UI, never a session's.
- **Keeping a maker skill.** The owner can keep the existing maker skill and add supported Home Assistant control
  alongside it. Leave the existing Alexa entry and routines in place and do not expose the HA copy back to Alexa;
  test the maker app and Alexa again after the addition. See [the voice guide](../../install/voice-assistants.md).
- **A phrase for several lamps.** Follow [the worked scene-script example](../../install/voice-assistants.md#4-a-safe-scene-script-with-an-alexa-phrase).
  Home Assistant Cloud exposes the approved script; Alexa can run it directly or from a voice-triggered routine.
  The owner tests the phrase and each physical lamp. Stopping a script does not undo its completed actions.

## How this goes wrong

- "Device isn't responding" although the action happened: usually a stale device copy from an earlier discovery.
  Relink the skill and cut the exposure list in the same pass.
- Smart speakers' own media players get exposed back to Alexa, creating recursive device entries. Exclude them.
- Cloud-driven changes arrive under a system user, so a music request a moment before a lamp change can be blamed
  for it. Read the assistant's own command log before naming a cause.
- A countdown spoken by both a wall panel and an Echo is harder to follow than one voice. Let the speaker talk only
  when the panel cannot.
