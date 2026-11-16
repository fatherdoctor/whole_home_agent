# Assist and conversation agents

*Status: notes (O1). Templates: `templates/`.*

## What is different
- Assist is Home Assistant's own voice pipeline: local speech-to-text and text-to-speech, or cloud ones, with
  satellites (a voice puck, an ESPHome board, the companion app).
- A conversation agent can be the built-in intent matcher or an LLM (a cloud model, or a local one). An LLM agent
  is a network call with a cost and a latency; it cannot be load-bearing.
- Exposure is Settings → Voice assistants → Expose, per entity, separate from the cloud assistants' flags.

## What the principles need from it
- **Exposure follows `safety-and-security.md` rule 2.** The default is lights, switches and scene scripts only:
  no locks or alarm, sensors, media players or app switches. The owner may change the default after hearing what
  it protects against; record the choice. The control is Settings → Voice assistants → Expose, not the building
  agent's guard-rails file. Never change codes, slots or consent, or expose secrets. Exclude paddle relays in
  smart-bulb mode (toggling the relay cuts power to the bulb).
- **Secrets.** The sensitive set (code helpers, token helpers) is never exposed to an agent, and never appears in
  the entity names or attributes it can read.
- **Budget.** An LLM agent's calls count against the same budget as the building agent; meter them.
- **Notifications.** A satellite that announces is a speaker under the "one voice at a time" rule.

## How this goes wrong

- A conversation agent with full reach can unlock a door on a misheard sentence. Limit exposure as rule 2 sets it,
  with any owner-chosen changes recorded; keep codes, guest slots and consent protected. The agent's cloud tier
  matters too: on a free tier the vendor may train on submitted content, which rules out camera images and guests'
  messages.
