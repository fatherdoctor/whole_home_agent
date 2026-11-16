# Telegram

*Status: notes (O1). Not tested in practice; general guidance only. Templates: `templates/`.*

## What is different
- A bot, one chat per person (or a group). Inline-keyboard buttons; a message can be edited in place if you store
  its message id.
- Anyone who finds the bot can message it; a chat id is not an identity you verified.

## What the principles need from it
- **One chat per person** if per-person levels matter; a shared group is one level for everyone.
- **Replacement** is "edit message": store the message id per tag in a helper and edit, or send a new one and
  delete the old.
- **Inbound commands** follow `safety-and-security.md` rule 12: acknowledge only, never touch alarm state, answer
  status only to a known chat id, and no keyword that helps someone decide whether to approach the house.
- **Consent**: a person who starts the bot has opted in to the bot; they have not opted in to calls or texts. Keep
  the consent record per channel.
