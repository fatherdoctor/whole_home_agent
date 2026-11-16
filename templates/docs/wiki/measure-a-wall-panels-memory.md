---
title: Measure a wall panel's memory
slug: measure-a-wall-panels-memory
type: procedure
summary: How to tell whether a new element on the wall panel frees the memory it used once it leaves the screen, measured on the device itself, without the mistakes that void a run.
status: Template from the kit (KIT-WPM, 2026-10-30); fill the "For this house" lines from the box
categories: [Wall panel, Procedures]
see_also: [wall-panel]
verified: YYYY-MM-DD
---
# Measure a wall panel's memory without fooling yourself

*Status: written (KIT-WPM, 2026-10-30). A procedure page for the household's maintainer wiki (`type: procedure` in
`SCHEMA.md`): copy it into the wiki, keep the steps, and fill the "For this house" lines with the panel's own
entity ids, pixel coordinates and normal timer values, read from the box. Why it exists: a tablet that runs a
dashboard for weeks shows two kinds of memory growth, the kind a garbage collection reclaims and the kind it does
not, and a measurement that does not separate them says nothing. The two voided runs that taught every rule below
are in the "How this goes wrong" list; the method has been run end to end and passed since.*

## When to use this

Before trusting that a new element on the wall panel leaves no memory behind. The standing rule is an element
TYPE the panel does not already use: a new custom card or card type, a new frontend resource, a new theme
mechanism, an animated or media element (a live camera tile, a canvas background, a GIF). Another row, tile or
button of a kind already on the panel needs no run. The run answers one question, "does this element free what it
used once it leaves the screen?", not whether it looks right.

## Before you start

1. **Read this page to the end first.** Both voided runs below skipped a method that was already written down.
2. **Tools.** A shell on the tablet (ADB over the network for an Android kiosk) and a DevTools connection into the
   kiosk app's WebView. You read three numbers from the device: the kiosk process's graphics memory (on Android,
   `dumpsys meminfo`'s Graphics / GL line), its total PSS, and the WebView renderer's own PSS; plus the device's
   free memory and a DOM node count from DevTools.
3. **A page-local safety guard.** Before you read anything, install a guard in the page that blocks any service
   call that would reach a person or a device (a find-my-phone call, a notify, a lock), and self-test it with a
   dummy service name. During the run you may open and cancel a confirmation dialog to test it; you never let a real
   call go out. Nothing reaches a person to verify a measurement.
4. **Decide the screen state the run needs, before you touch anything.** A screen that is off or behind a
   screensaver renders nothing, and three identical flat samples of nothing look like a perfect pass. If the run
   spans a time when the screen would normally go dark, change exactly the two things that control it (the
   automation that turns the screen off at night; the screensaver timer), write down both current values, and
   restore both at the end. Never improvise a screen or screensaver toggle in the middle of a run to "see the
   dashboard for a moment": it corrupts the baseline you already took.
   *For this house:* the night screen-off automation is `automation.<...>`; the screensaver timer is
   `number.<...>` (normal value: `<...>` seconds).
5. **Never send keep-awake key events.** A kiosk app's idle timer ignores injected key events, so a keep-awake loop
   over ADB does not keep anything awake; it queues up behind the screensaver, and when the screen goes off the
   queued events have no window to go to, the input dispatcher times out, and the OS kills the kiosk app as an
   "application not responding". Keep the panel awake only with a real tap on a point you have checked hits no
   card, and only while the dashboard has the focus (the kiosk app is the resumed activity and the device reports
   awake). *For this house:* the two safe tap points are `(<x>, <y>)` and `(<x>, <y>)` screen pixels, checked on
   every view of the panel.
6. **Confirm the real screen state on the device before every reading, never from a Home Assistant switch alone.**
   A switch entity for the screen or the screensaver describes what Home Assistant last told the panel to do, not
   what is on the glass now; a screensaver that is in front of the dashboard while the switch says "off" was a whole
   voided run. Read the device's own state (the resumed activity and the wakefulness) each time.

## Steps

1. Connect to the tablet. **Do not restart the kiosk app.** A restart clears the graphics residue that has built up
   since the last one, so a run that includes a restart measures a fresh process, not the element under test, and
   its readings cannot be compared with a baseline taken before the restart. Note the kiosk process id; it must be
   the same at the end.
2. Reload the page in place (a DevTools page reload, never an app restart) for a clean page baseline inside the
   same process.
3. Install and self-test the safety guard from "Before you start".
4. **Baseline on the home view:** force a garbage collection, then take 3 samples 10 seconds apart: graphics
   memory, total PSS, the renderer's PSS, free memory, the node count.
5. **The element "on":** open, trigger or visit it, and take the same reading while it is showing.
6. **After leaving:** return to the home view, force a garbage collection, take 3 samples 10 seconds apart. Visit
   and leave the element at least 3 times before judging; one visit cannot show whether a cost repeats.
7. **Wait before calling anything a residue.** Take one more sample about 20 seconds after the "after leave +
   GC" samples. Some elements free their graphics memory a moment after the DOM and canvas side is already clean;
   a sample taken too early looks like a leak that is not one.
8. **If the element sits under a screensaver in normal use,** run one screensaver cycle over it (screensaver on for
   about a minute, then off) and read again the same way. Expect graphics memory to rise some tens of megabytes
   while the screensaver runs and mostly return once it stops.
9. **Compare with the baseline.** A small set of leftover detached nodes or canvases that stays the same size across
   repeated visits is not a leak: note the count and move on. Growth that repeats with every visit is. The pass line
   is yours to set once and keep (a residue of about ten megabytes per visit is a common threshold); write it on
   this page so the next run uses the same one. *For this house:* the pass line is `<...>` MB per visit.
10. **Restore every setup change** from "Before you start" and read both values back to confirm. A restore you did
    not re-read is a restore you assumed.

## Check it worked

- Every element tested has a baseline, an "on" reading and an "after leave + GC" reading (plus a screensaver-cycle
  reading where one applies), each with graphics memory, PSS and a node count, with times.
- No verdict was written before the late-release sample of step 7.
- The kiosk process id is the same at the end as at the start. If it changed at any point, the run is void.
- Every setup change was restored and re-read.
- The device's own screen state, not a Home Assistant switch, was checked before every reading taken anywhere a
  screensaver or a dark screen could have been in front of the dashboard.
- The run is written into the panel's wiki page the same day, with the times, the process id, the numbers and the
  verdict. **A run that broke one of the rules above is recorded as VOID, with the rule it broke**, not as
  "inconclusive" and not left out: a void run is a lesson for the next person, a missing one is the same mistake
  made twice. An unplanned kiosk restart during a run is an incident of its own (the planned-restart marker was not
  set; the panel's watchdogs saw it) and goes in the CHANGELOG.
- Undo: nothing on the panel changes in a correct run; step 10 undoes the two setup changes.

## How this goes wrong (kit note: the household copy moves these to the panel's thing page as lessons)

- **Measuring the dark.** The night screen-off had already run; three samples on the home view and three on
  another view were identical and flat, because the screen showed nothing. Rule: step 4 of "Before you start".
- **The improvised toggle.** To see the dashboard for a moment, a screensaver switch was flipped mid-run and
  flipped back four minutes later. The one reading that looked real could not be compared with anything, and the
  run was void. Rule: change only the two documented things, before the run, and restore them after.
- **Trusting the switch.** A daytime re-run read the panel while the tablet's own screensaver activity was in
  front of the dashboard, a state the house's switch entities reported as off. Void. Rule: step 6 of "Before you
  start".
- **The keep-awake loop that killed the app.** Injected key events queued behind the screensaver and, when the
  screen went off, the OS killed the kiosk app as not responding; the baseline then described a process that no
  longer existed. Rule: step 5 of "Before you start", and the process id check.
- **Calling it a leak too soon.** Canvas backgrounds still held most of their graphics memory on the first two
  post-GC samples and released it on a third taken 20 seconds later. Rule: step 7.

## References

`principles/dashboards.md` rule 13 (mind the memory) and its "How to check it"; `principles/testing-and-simulation.md`
(nothing audible or sent while testing); `principles/documentation.md` (lessons are written the day they are
learned).
