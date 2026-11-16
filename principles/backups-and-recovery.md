# Backups and recovery

*Status: written (O1, 2026-10-11); backup size management added (KIT-SYNC-1107, 2026-11-07). Distilled from a real
install; the failure modes are written generically.*

Tiers T0-T4, off-box copies, restore drills, a recovery chapter in the manual.

## The rule

1. [default, topic 9] **Design tiers by failure**, each with its own mechanism, retention and MEASURED rollback time:
   - **T0** a config experiment: a snapshot plus git, about a minute.
   - **T1** a bad Core or OS update: "snapshot, then update"; about a minute, or thirty with the built-in backup.
   - **T2** the system disk dies: a nightly machine image to a second disk, about an hour.
   - **T3** the whole box is dead: the built-in backup copied off-box to cloud storage, two to three hours on any
     replacement x86 box.
   - **T4** a radio stick dies: Z-Wave controller NVM and Zigbee coordinator backups, monthly, kept off-box, about
     half an hour and no re-pairing.
2. [core] **Nothing in T0-T2 leaves the house; T3 must.** Keep the backup encryption key outside any backup: a password
   manager plus an off-box encrypted copy.
3. [default, topic 9] **Run a restore drill, timed, into the isolated clone, monthly.** Record what came back, what was missing and
   why.
4. [core] **The thing being rolled back must not be the thing deciding to roll back.** The house may take and list
   snapshots through a narrow API token; rollback, restore and delete stay with a person at the console.
5. [core] **Backups run in snapshot mode, never suspend or stop.** Expect the Supervisor to refuse work for a few seconds
   during a snapshot; wait before chaining an update.
6. [core] **Radio and house backups carry codes and tokens**: treat them as secrets, never in the repo.
7. [core] **The manual gets a recovery chapter written from the drill, not from the design.**
8. [core] **Backup age is a health check** (`health-checks.md` rule 11), with one cause, one warning.
9. [core] **Keep a generated record of every device's configuration parameters** as the recovery reference after a
   factory reset.
10. [core] **Know each backup destination's size cap and stay well under it.** Home Assistant Cloud keeps one backup
    of at most 5 GB; other destinations have their own limits. Home Assistant backs up a folder such as `/share`
    whole and cannot skip a subfolder, so keep what can be downloaded again (git clones, build output, caches, an
    agent's work copies) out of the backed-up folders, or shallow when it must live there.
11. [core] **Warn on size before the cap, not after.** A health warning when the newest backup passes about 90 % of
    the smallest destination's cap (4.5 GB for a 5 GB cap), one cause, one warning.
12. [core] **A failed upload to any destination is a health fault.** A backup that completed locally but failed to
    reach one destination is not a success. After any change to what is backed up, check that the next night's
    backup reached every destination.

## Why

A backup that has never been restored is a hypothesis; a backup without its key is a brick. The tiers exist because
a bad config change, a bad software update, a dead drive and a dead box are different failures with different
clocks, and the owner asked for one plan that covers all of them, with a redeployment guide a person can follow.

## How this goes wrong

- **What a restore drill teaches.** A restored house brings its own name, so guards must key on network isolation,
  not the instance name. An offline restore (or one during an ISP outage) needs the "internet reachable" checks
  skipped for that call. Custom integrations that install packages on first start fail offline. Entities created
  after the backup are missing, as they should be. Rules 3, 7.
- **A restore that rolls back more than the house.** A shared directory (a git checkout, an export folder) goes
  back with it, and the next scheduled push is rejected. After any restore, fetch and compare before trusting it.
  Rule 3.
- **A backup refused mid-snapshot.** "Back up before update" fails because the Supervisor is still busy with the
  last job. Wait and retry. Rule 5.
- **A rotation that races its own lock.** A cleanup deletes old VM snapshots while the hypervisor still holds a
  lock, the delete fails quietly, and snapshots pile up until the disk is full. Poll the lock. Rule 1.
- **A key kept inside the thing it unlocks.** The backup encryption key lives only on the box; when the box dies,
  every off-box copy is unreadable. Rule 2.
- **A backup that outgrew its cap.** Several full git clones in the backed-up folder repacked overnight, the backup
  grew past the cloud cap, and the cloud upload failed while the local and other copies succeeded. The backup
  health check stayed green: it read neither delivery nor size, and the failed upload showed only in the
  integration's own repair list. Age caught it hours late, because the platform moves "last successful" only when
  every destination took the upload. Rules 10-12.
- **A reset with no record.** A factory reset wipes a device's configuration parameters, and nobody wrote down what
  they were. Rule 9.

## How to check it

- A table of tiers with a measured, not estimated, rollback time.
- A drill record dated within a month, with entity counts live vs restored.
- The key is retrievable from two places, neither of which is a backup.
- The API token's attempt to stop the VM returns 403.
- A health sensor faults if the nightly image is more than thirty hours old or did not end OK.
- The newest backup's size is under 90 % of the smallest destination's cap, and a size warning exists.
- The last automatic backup reached every destination; a forced failed upload turns the backup health check red.
- No git clone, build folder or cache sits in a backed-up folder unless it is shallow.

## Adapter notes

- **Hypervisor (Proxmox).** A tested shape: nightly image to a second disk, snapshots triggered
  from the house through a read-plus-snapshot token.
- **Mini PC, bare metal.** No T0 or T2 as such; T1 is the built-in backup before an update; T2 becomes "reinstall
  the OS, restore T3".
- **Raspberry Pi / HA Green.** The card or eMMC is the likely failure, so T3 off-box copies are the whole plan.
  Keep the official import/export path documented for the device.
- **Radios.** T4 applies to Z-Wave and Zigbee sticks. Matter and Thread credentials are held by the border router
  and fabric; find the vendor's export path before you need it.
- **AI agent.** Any agent may snapshot; only a human rolls back.
