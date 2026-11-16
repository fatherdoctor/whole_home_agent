# The interviews

*Status: written (O2, 2026-10-13).*

Two scripts, one schema, one contract:

| File | When | Writes |
|---|---|---|
| `phase-0-setup-interview.md` | Before Home Assistant exists. About fifteen minutes. | `house/profile.yaml`, the `setup:` block; picks the install guide |
| `phase-1-house-profile-interview.md` | At the person's first request to build something. About half an hour; can stop early. | `house/profile.yaml`, the `profile:` block; then the generated files |
| `profile-template.yaml` | The schema of `house/profile.yaml`, with every field explained and its default. | copied to `house/profile.yaml` the first time |
| `generated-files.md` | What Phase 1 produces from the profile, from which principle, from which template, and what each build item needs answered first. The contract between the interview and `templates/`. | |

## How to interview (both phases)

1. **One topic at a time; offer a small batch when it helps.** Start with one question and say why the topic
   matters. Ask whether the person prefers one at a time or a short group of related questions with clearly
   labeled recommended defaults. Batching can fit an evening; it never turns silence into agreement. Wait for
   the answers, read them back, and record unanswered choices as pending or assumed, not confirmed. Keep
   consent to a destructive change, a paid service or a live action separate; never batch secret entry into chat.
2. **Never ask what you can read.** In Phase 1 the box already knows its areas, devices, integrations and
   people; read them and confirm, never re-ask. In Phase 0 the person's first message often answers two or three
   questions; take those and move on. Read `setup.standing_rules` at the start of either phase: those rules apply
   immediately. Phase 1 topic 8 carries them into the agent limits and generated policies; pending questions
   never erase a rule the owner already gave.
3. **Offer the default.** Every question has a recommended answer. Say it. "I don't know" means the default,
   recorded with `assumed: true` so a later session revisits it.
4. **Write before moving on.** Each topic's answers go into `house/profile.yaml` before the next topic starts.
   A session that dies mid-interview loses nothing.
5. **Plain words.** No entity ids, domains or integration names in a question unless the person used them first.
   "Which rooms have a motion sensor" rather than "which binary_sensors of device_class motion".
6. **Secrets never.** No question asks for a code, PIN, password, token, phone number or street address. The
   profile records that a thing exists and where its secret lives, never the value.
7. **The person may stop.** After any topic: "stop here or go on?" Mark unanswered topics `pending` in
   `profile.topics` and say what can and cannot be built until they are answered. Stopping does not skip
   generation: Phase 1's topic 11 still runs with the answered topics, writes `(pending: topic N)` for the rest and
   sets `profile.generated_on`; the next session that answers a pending topic regenerates only what it feeds.
8. **Read it back.** At the end of each phase, show the profile block in plain words, ask for corrections, then
   set the phase's `done` flag.
