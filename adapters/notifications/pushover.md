# Pushover

*Status: notes (O1). Not tested in practice; general guidance only. Templates: `templates/`.*

## What is different
- One application token for the house, one user or group key per recipient. Priorities from lowest to emergency;
  emergency retries until acknowledged.
- No tag replacement and no remote clearing. One URL action per message, no multi-button prompts.

## What the principles need from it
- **Classes and levels** map onto per-recipient keys: the router picks the keys, not the caller.
- **Emergency priority is the critical flag**: reserve it for the alarm's loud stage, and set its retry and expiry so
  a missed alarm does not retry for an hour after the all-clear.
- **No replacement** means the roll-up rule (three pushes per hazard, then one replaceable notification) needs a
  different shape: send the roll-up as one message and suppress the rest, since you cannot edit in place.
- **Prompts with buttons** (Hold / Go, Arm / Don't) are not available; use the companion app or a phone-side
  dashboard for anything that needs a bound button, and never let a text reply act on the alarm.
