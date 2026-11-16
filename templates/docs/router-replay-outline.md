# Router replay: a tool outline

*Status: written (KIT-RPLAY, 2026-10-31). An outline, not code: the house's agent writes the tool against its own
router, from these steps, when the first change to the router is planned. The rule is
`principles/testing-and-simulation.md` rule 14. Lived once on a real install: a month of real pushes, old and new
router side by side, no difference in who heard what, and one finding against the push log itself.*

## What it answers

"If the new router had been live for the last few weeks, would anyone have heard something different?" It is
read-only: it sends nothing, touches no helper and runs offline against an export.

## Inputs (an export from the box, read-only)

1. **The messages.** Every call the router logged in the window: time, title, message, class, tag, and the
   recipients it recorded. The kit router fires `notify_router_call` on every decision; the recorder keeps those
   events. A log sensor that holds only the last N entries must be unpacked from every recorded copy and
   de-duplicated by time + title + message.
2. **The settings history.** One row per state change (entity, time in UTC, state) for everything the router
   reads: each phone's `input_select.notify_level_*`, `input_boolean.notifications_enabled`,
   `input_boolean.notify_test_mode`, the guest slots and their levels and windows, who is home (reduced to home /
   not home, no zone names), the alarm's state, and any mode the router checks.
3. **Leave out** the contact directory and anything else that holds numbers or addresses; rebuild who is who
   from the slot and phone labels only.
4. **Retention sets the window.** Home Assistant's recorder keeps 10 days unless told otherwise. Raise
   `purge_keep_days` (30 is enough) well before a router change, or keep a daily export of the router's events.

## Steps

1. **Load** both files; sort the settings history so "the state of X at time T" is one lookup.
2. **For each message**, rebuild the call (class, tag, title, message, and any flag the log keeps) and the
   house's state at that moment.
3. **Render it through both routers** with the same offline harness the router's tests use (the kit's
   `templates/tests/ha_stub.py` stand-in, or the house's own), with "now" set to the message's own time. The old
   router is the live one as exported, pinned to a file; the new one is the branch under review.
4. **Compare**, per message: phones that got it, guests texted, merged or held, and the words (title, body, text
   version). Classify each difference: audience, held/merged, wording only.
5. **Check the check.** Compare the old router's rendered audience with the audience the log recorded. Every
   mismatch is explained one by one (a switch that was off, a log written before a check) or the model is wrong
   and the replay stops until it is fixed.
6. **Report** `house/docs/reviews/<CODE>-replay-<date>.md`: the window and count; a table of differences by kind;
   every audience difference listed with the ruling that explains it, or marked as a finding; a few wording
   samples; the old-model agreement count with the explanation of each miss; and what the replay cannot see.
   Keep the machine-readable result beside it so the next run can diff against it.
7. **Re-run** after every later change to the router; expect the same counts unless a ruling moved them.

## What a replay cannot see (say so in every report)

- Messages the old router never sent: the log holds only sends.
- Flags the log does not keep (buttons, critical, time-to-live) and which automation called.
- Senders that bypass the router, phone calls and texts from a separate escalation, and speech.
- Consent: a replay names who would be texted; whether that person agreed is checked where the text is sent.

## Tests for the tool

- A fixture of three messages and a short settings history: one where both routers agree, one with an audience
  difference, one sent while sending was switched off (the old model must send nothing).
- The report's counts add up to the number of messages read; a harness error is counted, never dropped.
- Nothing in the tool can call a service: run it with no network and no token.

## Cost

No helpers or entities on the box; one export (a few MB for a month) and a longer recorder window. A run is a
few minutes on any computer.
