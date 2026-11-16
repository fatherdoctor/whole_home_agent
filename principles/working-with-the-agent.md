# Working with the agent

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

Approvals, reporting faithfully, verifying before claiming, timestamps, memory.

## The rule

1. [core] **Approvals.** Nothing that reaches a person (push, call, SMS, speech, speaker, panel) goes anywhere but the
   owner's own phone without permission for that specific send. Permission for one send is never permission for
   the recipient, the channel or a follow-up test.
2. [core] **Never send to verify your own work.** Verify everything that does not reach a person, then let the owner
   send.
3. [core] **Report faithfully, including failed tests.** A rehearsal report lists what ran, what failed verbatim, what
   was not exercised, and corrects its own earlier claims in the same log.
4. [core] **Verify before claiming.** Read the file back after every push. Run the real scripts, not inference. Vary one
   input at a time. Enumerate from the API, never derive a name from a pattern. A snapshot is not a check. A
   current value is not evidence of a historical one.
5. [core] **Timestamps.** Report filenames carry date and time in the declared local timezone. Read fire times from the
   house's own records, not the shell clock.
6. [core] **Memory.** Lessons are written the day they are learned, as a rule with a why and a how-to-apply, and exported
   where routines can read them. A new lesson goes into the CHANGELOG or the wiki queue the same day.
7. [core] **Say what is live vs what the docs say.** The live export is the truth; a mirror or prose is a claim; if the
   export does not cover a fact, say "unverifiable" rather than substituting.
8. [core] **Never deploy from a session that cannot see the box.** Cloud routines have the repo only: draft PRs and
   deploy notes, never a merge, never the live box; the merge owner named in the owner's ruling lands them
   (`board-and-lanes.md` rule 24). The line is drawn at intent, not mechanism: such a session writes
   nothing meant to be applied to the running system, edits no mirror of a live file and never proposes a live edit as
   a next step, because a commit that somebody applies by hand is exactly how a freeze gets broken.
9. [core] **Secrets never in the repo.** PINs, codes, tokens, passwords, phone numbers, addresses: name a secret, never
   quote it. A push guard that exits non-zero scans every commit for phone shapes, credential shapes and forbidden
   paths. A warning that does not stop anything is a comment, not a guard: it was read and pushed past twice.
10. [core] **Clean up behind yourself.** Removing a thing is not done until its registry entry, export files and
    references are gone, in the same session.
11. [core] **When the owner approves a build against a deadline, build it then.** Defer only if genuinely blocked, and
    say what.
12. [core] **Having written down that something cannot be verified is the moment to ask, not to proceed.**
13. [core] **Prove a file is complete before writing it back.** Compare what you hold against a manifest's byte count.
14. [core] **Commits carry a co-author line, never a session link.** A public history (a fork, a published
    component) shows the agent as a contributor through the co-author line; a link to the conversation that made the
    commit is noise to a reader and a pointer into a private account. If links slipped in, rewrite only your own
    commits above the upstream point (never a signed upstream commit), **and only with the owner's go for that
    repository** (a rewrite changes every hash that reviews and links quote; nothing else in these rules gates a
    force-push), confirm every branch's tree is unchanged, force-push with a lease, and keep a map from old to new
    hashes, because reviews and board rows quote the old ones. The coding tool adds a session link to commits and to
    PR bodies by default, so a rule in a brief is not enough: a repo-root `CLAUDE.md` (or the tool's project
    instructions) is what overrides the default, and a CI check fails any PR whose body or commits carry a session
    link (report only on the main branch, which is never rewritten).
15. [default, topic 3] **Prefer native device control, with the owner's choice first.** Suggest Matter where supported,
    otherwise Home Assistant's local maker integration; explain the cloud dependency it avoids. Keeping a maker hub
    and adding its integration (such as Hue), or retaining an app for features/firmware or lack of native support,
    is a first-class choice. Follow the owner; inventory routines and prove native control before retiring a cloud
    voice path (`../install/voice-assistants.md`).
16. [default] **A wish beyond the kit is the owner's next card, not an invented recipe.** Say plainly that no kit
    guide covers it; ask what the owner means and introduce their own board and [build lane](board-and-lanes.md),
    starting with this wish as their first card when no board exists. Offer options with costs, follow the owner's
    choice, agree tests and undo, and admit the unknowns before building. A chat without an agent on the box offers
    to keep it as an open card in the saved progress note; moving to that agent makes the build lane possible.
    The chat never claims to run a lane, create house files or start the build.

## Why

Sends are audible, outward-facing and irreversible; the cost lands on someone who did not opt in. A claim the
owner cannot check is worse than a gap. A session that cannot see the box cannot see what it broke.

## How this goes wrong

- **Verifying by sending.** An agent tests its new script end to end by calling the number again, or fires a test
  event that the router fans out to the household. Symptom: a stranger's phone ringing at night, or family members
  told about a shutdown that is not happening. Rules 1, 2, 12.
- **A placeholder over the real file.** A file is pushed with stand-in content and replaces the real automation;
  only reading it back catches it. Rule 4.
- **A stale write.** A file tool with no stale-content check overwrites a commit made a minute earlier, or an agent
  reads a truncated copy of a shared log and writes it back, reversing recorded decisions. Rule 13.
- **A guard that warns and continues.** A pre-push check prints ABORT but the push runs anyway, because the
  script's output was read instead of its exit status. Rule 9.
- **Half a removal.** Deleted automations leave registry rows behind and come back as unavailable entities after a
  restart. A "restored" flag matches many legitimate entities too, so never bulk-delete on it. Rule 10.
- **A name derived by pattern.** A notify service name is guessed from another person's working one; the real one
  differs, and nothing shows until the automation runs. Rule 4.
- **Confident and wrong.** An agent says a setting has "always" been on when it was enabled that day. Rules 4, 7.
- **A report that hides the result.** A write-up says "mostly done" where it should say what failed. List what
  ran, what failed verbatim and where the end state differs from the request. Rule 3.
- **A default that outranks the brief.** The rule says no session links, but the tool's built-in attribution adds one
  to every commit and PR body, and after a few weeks dozens of PRs carry them. Only a repo-root instruction file and
  a CI check stopped it. Rule 14.
- **A clock that is not.** A blocking call makes time read from the host look skewed by a minute. Rule 5.

## How to check it

- A test-send script with an arming toggle exists and its test-number field is empty.
- The push guard runs on exit status before every push and has fixtures.
- Every report file has the time in its name; every rehearsal or drill record has a "failures, verbatim" section.
- The cloud routines' briefs say "never deploy", and the box resets its runtime copy to the main branch on a
  schedule, so a merge is treated as a deploy.
- A search of the repo for live codes and phone numbers returns nothing.
- A repo-root `CLAUDE.md` names the attribution rule, and the attribution check runs on every PR.

## Adapter notes

- Hardware-neutral.
- **Each runtime's quirks** (memory, permission classifier, refusals in the guard) are on its adapter page,
  `adapters/agents/<runtime>.md`.
- **Another agent.** `AGENTS.md` is the neutral entry; the same four things matter regardless of vendor: a brief,
  a push guard, a log per run, the secrets rule. Without a sandbox that distinguishes read from write tools, the
  "simulation personas are read-only by construction" guarantee must be rebuilt another way. See
  `adapters/agents/other-agents.md`.
