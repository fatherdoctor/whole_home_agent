# SMS and voice calls

*Status: notes (O1). Used in practice. Templates: `templates/`.*

## What is different
- A paid provider (a telephony API) with per-message cost, carrier registration for application traffic (an
  unregistered sender has messages accepted and then silently dropped), and legal keywords: STOP must stop
  everything at once, HELP must answer.
- No buttons, tags or replacement; one segment per message; a sender id is forgeable; the inbound webhook is
  unauthenticated unless you sign it.
- A call "answered" can be a voicemail; machine detection returns a value you must branch on.

## What the principles need from it
- **Consent is a record keyed to the number** (`notifications-and-tiers.md` rule 16): unknown → granted → revoked,
  append-only. STOP is acted on instantly; YES only records an intent until a human confirms.
- **Three gates on every outbound text** (rule 17): master send switch, number resolves to a directory contact,
  consent granted. Numbers live in the secrets file, referenced by key (rule 18).
- **Never send to verify** (rule 6). A test-send script refuses unless an arming toggle is on, and clears it
  afterwards; its test-number field is empty in the repo.
- **An id is not delivery** (rule 24): do not wait for a reply to a message the carrier dropped.
- **Text first, call a minute later**; a disarm stops the ladder; an acknowledgment stops calls and texts only, and
  only from someone on a rung.

## How this goes wrong

- A session places a second "test" call to check its own script and rings a stranger, after writing down that it
  could not verify whose number it was.
- A text is accepted with an id and then rejected by the carrier (for example, unregistered application traffic);
  the script waits for a reply nobody can send.
- An automatic reply to a keyword such as HELP answers any number, a stranger's included. Evaluate the condition
  with nothing sent.
- A phone number in a config comment is one export from the repo.
