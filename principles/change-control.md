# Change control

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

Freezes, version pins, staging clones, rehearsals, drift logs, rollback of record.

## The rule

1. [core] **Declare a freeze before any period the owner cannot attend to the house** (a trip, a cutover soak). Take a
   named snapshot or full backup at the freeze point. From then on every live change needs the owner's explicit
   go and gets a dated drift row against that snapshot.
2. [core] **Pin versions during the freeze**: Core, OS, Supervisor where you can, community packages, every app, and
   device firmware. Turn app auto-update off. Do not install a new monthly release until the freeze lifts; the
   weekly review keeps running and only a critical update is applied, with the owner's word (`updates.md` rule 8).
3. [default, topic 9] **Keep a staging clone**: a full copy of production on an isolated network with no uplink and no radios,
   neutralized (start-at-boot off, no USB passthrough) BEFORE it ever starts. Rename it so it can never be
   mistaken for the house, and guard every destructive command with a check that prints that name. Staging tools
   read the hypervisor credential, so only a session the owner has trusted with that credential runs them; a build
   lane never does.
4. [default, topic 9] **Rehearse every risky deploy on the clone first**, with a named commit, a measured rollback time, and a test
   suite run before and after.
5. [core] **The config check must be fully successful.** "Successful config (partial)" means a file failed to parse and
   is a FAILURE. Require the literal success line.
6. [core] **Every deploy has a deploy note**: what changes, file by file; a section **What makes this take effect**
   naming the mechanism, not a promise (the path the box runs it from, the step that copies or applies it, the
   reload or restart; or "repo-only: nothing runs on the box"); pre-checks; exact steps including the config check;
   a test plan that fires nothing audible or outward; a rollback; and what it costs (helpers, entities, battery,
   API calls). Whoever applies it confirms each named path on the box (`board-and-lanes.md` rule 24).
7. [core] **A rollback of record exists before the change.** For a VM, a no-RAM snapshot from the command line; for bare
   metal, an untouched original disk and a boot-order change; for YAML, git plus a count of top-level keys before
   and after.
8. [core] **Never pause the VM** (RAM-included snapshots, suspend-mode backups): time, sun and `for:` triggers run late
   by the pause length until the next restart.
9. [core] **Keep a drift log**: one dated line per live change that the design or inventory does not yet reflect. A line
   is a claim about what is wrong, not a correction.
10. [core] **Do not hand-apply a commit to a frozen box.** A commit that somebody applies by hand is exactly how a freeze
    gets broken. A merge to the branch the box deploys from IS a deploy; treat it as one.
11. [core] **Count before and after every scripted edit** of a live file, and abort on loss. A valid config check is not
    enough.
12. [default, topic 9] **Outside a freeze, updates follow the weekly review-then-update cadence** (`updates.md`): a version waits
    four or five days, a written verdict comes before the apply, the apply has a rollback of record and a
    next-day checkout, and the hypervisor host gets the same patience.

## Why

The owner is away and cannot recover; an untested change on the live box has no undo for the household. A freeze
is only real if it has a snapshot to roll to and a log of what moved after it. Staging turns "we think this
works" into "we measured it".

## How this goes wrong

- **The config check's fake pass.** A colon inside an unquoted description, or an apostrophe inside a single-quoted
  string, makes a file unparseable; the check says "Successful config (partial)" and is read as a pass. The running
  system keeps the old version in memory, so later edits silently never load, and a restart would load none of
  that file. Rule 5.
- **A paused VM.** A RAM-included snapshot or a suspend-mode backup pauses the VM; timers fire late and missed time
  triggers are simply dropped. The cause shows only in the hypervisor's task log. Rule 8.
- **A firmware batch.** One device crashes mid-update and its radio jams the mesh. Stop any batch at the first
  failure, and freeze device firmware before a trip. Rules 1, 2.
- **A scripted edit that eats a file.** A regex matching across lines swallows the rest of a helpers file; the
  config check passes and the reload deletes every helper after the match. Count before and after. Rule 11.
- **An upgrade that breaks at startup.** A new version rejects an old option shape and disables the scripts that
  use it; only the rehearsal on the clone shows it. Rule 4.
- **A clone on the house network.** It steals the boards' connections, grabs the radios and texts real people. A
  restore meant to be partial runs as full. Rule 3.
- **A change made by hand and never written down.** Someone edits the live box directly; the next deploy from the
  repo silently reverts it, or the docs describe a house that no longer exists. Rules 9, 10.

## How to check it

- A dated snapshot with a reason exists before the freeze; the drift register has a row per post-freeze change.
- Auto-update is off on every app; list them.
- The clone's config shows the isolated bridge, zero USB lines, start-at-boot off, and a ping to the gateway from
  inside it fails.
- Every deploy note contains the word "rollback" and the literal expected check output.
- The nightly live export produces no commit on a night nothing changed (content-addressed, no timestamp).

## Adapter notes

- **Proxmox or another hypervisor.** Snapshots from the command line, no RAM; clone to an isolated bridge; a
  measured rollback of a few minutes. See `adapters/hardware.md`. Host updates: `updates.md` rule 11.
- **Mini PC, bare metal.** The rollback of record is a second disk plus a boot-order change; staging means a second
  box or a VM elsewhere.
- **Raspberry Pi / HA Green.** No snapshot layer; the first tier collapses to git plus the built-in backup; a
  staging clone is a second card or box restored from a backup, isolated the same way.
- **AI agent.** A permission classifier can refuse clone-shell changes mid-rehearsal; budget for a human step. Any
  agent needs the same "print the clone's name before destroying" guard.
