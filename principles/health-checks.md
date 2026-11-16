# Health checks

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

A health count per subsystem, faults vs notices, what makes a good check, watching the watchers, and timing the
preventive reboot of a device that slides with uptime.

## The rule

1. [core] **One integer health count per subsystem** (security, plumbing, system, network), each the sum of per-check
   macros written exactly once. Every tile and push reads the same sensor; nothing re-implements the logic.
2. [core] **Faults page someone; notices are visible and never page.** Severity is an attribute of the sensor, not a
   color chosen by the card. Three notices must not paint red.
3. [core] **A fault is a thing a working system never produces.** "No rise in an hour" is not a fault; "fell while idle
   on the charger" is. Replay history before choosing a threshold (`testing-and-simulation.md`).
4. [core] **Stale is a state.** Distinguish *unavailable* (the integration dropped it), *silent* (no report for N hours)
   and *not reporting* (a cloud entry failed). Unavailable is not "disconnected". Silence on a battery sensor is a
   notice at 24 h, not a fault at 6 h.
5. [default, topic 3] **"Alive" is only alive if something has talked to it.** Ping a lock when its last-seen is older than about
   two hours; a failed ping is what marks the node dead. Radio noise is a separate check.
6. [core] **Watch the watchers.** The health sensor faults when any automation in its own family, including the
   self-check alert, is disabled. The match is by id OR alias, never an id prefix. The health page on a shared
   panel is read-only.
7. [core] **The all-clear may only follow a problem push that was actually delivered.** Set an "alert open" flag when the
   problem push goes out, and only if notifications were on; the all-clear requires the flag.
8. [core] **Every check must be able to fire.** Prove it from a simulated state, not by looking at a healthy page. A
   fallback like `unavailable | float(-1)` makes both sides of a threshold unreachable. Remove checks whose
   source entity no longer exists. When a measurement's unit changes, re-derive every threshold.
9. [default, topic 3] **Thresholds per device class** (battery fault under 15 %, notice under 30 % for locks and motion sensors),
   kept in helpers shown on a page. Mesh health is "x of y online" with an explicit *not monitored* label for
   things offline on purpose; 0 of N is a coordinator fault with a short delay.
10. [core] **A device you reboot on purpose gets a planned-restart suppression**, so a planned outage never pages. The
    flag is **short-lived, with an expiry**: set it only when the restart is about to happen (a flag set hours
    early relabels a real crash as planned), and give it an expiry so a forgotten one cannot hide a crash later.
    Two shapes are sound: a window that covers every restart until it expires (the kit's
    `templates/packages/health-check.yaml`), or a single-use flag that clears on the restart it covers; if yours
    clears, set it again before each reboot in a series. Every watcher that can page honors it, the support
    agent's boot path included (`tier-2-support-agent.md` rule 10).
11. [core] **Backups are a health check**: house backup age, off-box copy age, backup disk fill, stale hand-made
    snapshots, radio backup age.
12. [core] **Health pushes go to the owner only**, at high priority with no expiry, through the one router
    (`notifications-and-tiers.md`). "Notifications switched off" is itself a fault, and produces one push.
13. [default, topic 6] **A daily reminder for anything offline since before today**, with a per-device toggle.
14. [core] **Find and trim long-unavailable entities on a schedule.** Inventory everything unavailable or unknown for
    more than a day (states plus history), grouped by device and integration, excluding disabled entities and
    ignored discoveries, and sort each row into **FIX** (a real device that dropped: reload, re-pair, battery,
    routing), **TRIM** (an entity the integration exposes that this house never uses or that no longer exists:
    disable it in the entity registry, never delete, after checking that nothing references it: automations,
    scripts, templates, dashboards, the health macros) or **KNOWN** (an accepted gap with its reason written
    down). Apply TRIM only for rows the owner approved, with the undo (re-enable) in the CHANGELOG, never during
    a freeze; repeat the inventory as part of the weekly update review (`updates.md`).

15. [default, topic 6] **Watch a slowly degrading device, then time its preventive reboot.** Some devices (a
    Wi-Fi camera, a streaming stick, a cheap hub) do not fail; they slide over days of uptime until a reboot fixes
    them, and nothing in the house sees it because every entity stays available. When a reboot is what fixed a
    device, do not guess an interval:
    - **Measure what the person noticed, read-only, on a schedule.** An hourly read of a few numbers that show the
      slide (frame rate from a short read of the main feed, time to a snapshot, the device's own CPU or memory,
      the longest stall), with **one login and one logout per read** (a read-only account where the device has one,
      its password in the secrets store), appended to a log file. It sends no
      notifications and changes nothing on the device; record the last reboot time beside it. Write down the
      healthy and the degraded numbers from the day it was fixed; each limit sits between the two, on the healthy
      side of degraded, so the watch calls the slide before it is as bad as the day it was noticed.
    - **Separate a slide from a normal cycle.** Compare like with like (day reads with day reads; a camera's night
      mode can halve its frame rate on a clock) and call it a slide only after several consecutive degraded reads
      on the same metric, so one busy hour is not a slide.
    - **A trend report recommends; a person decides.** On a set date the report gives the trend per day and part
      of day and, if it slid, a scheduled reboot **at half the uptime at which it slid** (so it never gets
      there). If it did not slide, it says so and names the uptime at which the last slide was seen: no slide in a
      short window is not a clean bill.
    - **Time the reboot around the house's calendar.** Before an away week or guests, reboot early enough that the
      next expected slide (last reboot + the slide's uptime) falls after it. Use a restart the house already
      exposes (an integration's restart button, enabled on purpose), set the planned-restart flag (rule 10), and
      confirm afterwards with one hand read that the numbers are back at or better than the healthy ones. A
      restart button reports nothing back: before a second press, read the button's last-pressed time or the
      device's uptime, or one reboot becomes two.
    - **Keep the watch running past the next expected slide**, then re-run the report; stop it with its own
      rollback when the question is answered, and write the reboot times in the change log.

## Why

A count is cheap to glance at, cheap to push and cheap for an agent to compare; the issue list under it explains
the number. Faults vs notices keeps red meaning something. Watching the watchers is the only defense against a
one-tap silent disable or a self-check that stopped rendering. Stale detection matters because most failures in a
home install are *silence that looked healthy*, not errors.

## How this goes wrong

- **A sensor that never listens.** A refactor moves a template's entity references somewhere the template engine
  does not track them (for example into `variables:`); the sensor registers no listeners, renders once and latches.
  Symptom: a health count that does not move even when you break something on purpose. Rules 1, 8.
- **Selecting by id prefix.** A "disabled automation" check filters by an id prefix, and a renamed automation keeps
  its old id. Symptom: disabling that one automation is never reported. Rule 6, and `naming.md` rule 3.
- **A dead check that looks alive.** After a migration or a restore, an entity comes back `unavailable`, and a
  default such as `float(-1)` makes neither branch able to fire. Symptom: a green check that cannot go red. Rules 4,
  8.
- **Silence mistaken for death.** Many battery devices check in with the radio stack without touching any entity,
  so their entities can be quiet for half a day while the device is fine. Symptom: a "not heard from" fault every
  day for a healthy sensor. Make long silence a notice with a per-class window. Rules 4, 9.
- **Alive because nobody asked.** Some radio stacks (Z-Wave among them) mark a node dead only after a command to it
  fails. When the mesh is jammed, a lock can read locked and available for hours. Symptom: green health through an
  outage. Rule 5.
- **An all-clear nobody needed.** "Self-check clear" goes out after any return to zero, including debounced blips
  and problems whose push was muted. Symptom: an all-clear for a problem the person never heard about. Rule 7.
- **Notices dressed as faults.** Harmless notices paint a tile the same red as a dead device. Symptom: people learn
  that red means nothing. Rule 2.
- **Numbers that are each reasonable and together impossible.** A page designed to be empty when healthy has
  filter bugs that only an assertion in code finds; a threshold set on one scale (entities) is compared against a
  count on another (devices), so its guard can never be satisfied. Rule 8.
- **A threshold that fires on normal behavior.** "Charging but not rising" fires every time a battery is already
  full. Replay history before choosing (`testing-and-simulation.md` rule 4). Rule 3.
- **An address that moved.** A device takes a new DHCP lease and the integration pinned to the old address sits
  unavailable until something checks it. Rule 4; reserve addresses as `install/network-and-backups-first.md` says.
- **Disabling an automation to silence it.** Turning off an automation's own switch raises the standing
  "automation disabled" fault and pages someone. Use a feature toggle instead. Rule 6, and `dashboards.md` rule 4.
- **A planned reboot that pages.** A nightly restart of a board or an app raises the same fault as a crash.
  Rule 10.
- **A planned-restart flag set early, left open, or not set again.** Set hours ahead, it labels a genuine crash
  as planned; a window left open for a day hides a real crash tomorrow; a single-use flag nobody set again makes
  the second reboot of a host-update evening page like a crash; a watcher written later that never reads it (a
  boot-time push path beside the restart path) pages anyway. Rule 10.
- **Unavailable entities that pile up.** Hundreds of option entities a lock integration exposes, scene events a
  dimmer never sends, a seasonal outlet unplugged for the winter: harmless alone, together they bury the one
  unavailable entity that is a dead device, and every health page grows an exclusion list. Rule 14.
- **A push that arrives late.** Phone power saving (Android doze) holds a normal-priority push for minutes. Rule
  12.
- **A device that slides with uptime.** A camera's stream gets choppy and its snapshots slow over a week or two
  while every entity stays available; a reboot fixes it and the cycle starts again. Symptom: the person notices a
  frozen feed, and the next slide lands, unseen, in the middle of a trip. A reboot interval picked by guess is
  either too often or too late. Rule 15.

## How to check it

- Both counts read 0 on a known-good day and every line of a non-zero count is explained. Record "N/N clear"
  before any freeze snapshot.
- grep every threshold check for `float(-1)` and `unavailable` fallbacks; prove each branch reachable with a
  simulated state.
- Toggle any health-family automation off: the count must rise within the debounce window.
- Pause notifications, break something, resume: no all-clear may appear.
- For each watchdog, run the "kill it" test once (stop the panel heartbeat, expect a fault; stop the support
  agent, expect the silent-agent push).
- Dashboards show the sensor's first issue verbatim: no local wording, no local severity.
- The long-unavailable inventory has a dated row per entity marked FIX, TRIM or KNOWN; TRIM rows are disabled in
  the registry, not deleted, and each has a CHANGELOG undo.
- For a device on a degradation watch: the log has one read an hour with a login and logout each, nothing was
  sent, the report says slide or no slide with the uptime it is judged against, and the next expected slide
  (last reboot + that uptime) is not inside the next away week.

## Adapter notes

- **VM vs bare metal vs Pi.** A VM guest cannot read host thermals or the BIOS "restore on AC loss" setting;
  re-check after any BIOS reset. A VM pause stalls every timed trigger: add a clock-jump sensor and a safe-moment
  automation reload. Distinguish a box reboot from a session restart (an uptime file). A Pi has no hypervisor, so
  the "VM backup age" row disappears; keep house-backup and off-box ages.
- **Radios.** Z-Wave "alive" is lazy: use last-seen plus pings and controller noise statistics. Zigbee drops
  battery devices after about six hours and mains relays after about two, so a five-minute "no power" fault must
  come from a second signal. With two radios you can cross-check mains loss: both mostly unavailable means a power
  cut; one means a stick fault; neither means the network.
- **No wall panel.** Drop the panel checks; keep the planned-restart pattern for anything you reboot on purpose.
- **Companion app.** `ttl: 0` and `priority: high` on health pushes, or doze delays them.
