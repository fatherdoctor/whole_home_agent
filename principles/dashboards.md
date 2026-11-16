# Dashboards

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

Design rules, a reference tab, kiosk panels, testing on the glass.

## The rule

1. [core] **The 30-day test.** A person can stop looking at a page for thirty days and still change a setting on it
   without the manual or an AI.
2. [core] **Seven kinds of thing on a page, and nothing else.** A tab answers one question. A section is one column. A
   heading is a noun phrase in Title Case. A status line is one sentence (the only place a template lives). Rows
   are an entities card of eight rows or fewer. An action is a button, always with a `confirmation` that says who
   it reaches or what it moves. Pages teach through names, not sentences: no captions, which nobody reads and
   which take up space.
3. [core] **Nothing on a first tab is settable.** The same tab order everywhere: Now, the doing tabs, Settings, Health.
4. [core] **A toggle is on a page only if a person is expected to flip it.** An automation's own enable switch is never
   a row outside a Health tab. A latch or flag is shown read-only, as a phrase.
5. [core] **No history, dates, reasons or values in card text.** History belongs in the changelog; values belong in the
   entity.
6. [default, topic 2] **Sections balanced** (the tallest at most twice the shortest), at most six per tab, three columns on a
   tablet, one on a phone; the first section is what a phone shows without scrolling.
7. [default, topic 2] **Plain words, one vocabulary.** Text, Call, Push. Sprinklers, not irrigation. Wall panel, not kiosk. Decide the
   list once and keep it in the house profile.
8. [core] **The live page is the source of truth, edited by hand, exported nightly to git.** Routine changes happen on
   the page, never in YAML; YAML is for a new kind of thing. Do not write a generator for a page people edit.
9. [core] **A reference tab is read-only and shows what settings ARE SET TO, not the settings.** Template rows or a
   markdown table, never the helper itself. "The why" is its deliverable, the one place a caption earns its
   length.
10. [default, topic 2] **Lights stay per room.** The house-operations page is not a remote.
11. [core] **A wall panel has one model tab that every other tab is measured against:** one font size and weight,
    theme-supplied card surfaces, one-page fit, every element links to its equivalent page. The panel's user is
    non-admin and local-only. Anything served from `/local` is cached by the browser for weeks and is reachable
    through remote access without login; bump a version query string after editing it.
12. [core] **Test on the glass.** Layout decisions are made at the panel with the owner watching. A screenshot judges
    layout, never rendering. A card that is empty when healthy is tested by asserting its row count against the
    health verdict in code, not by looking at it.
13. [core] **Mind the memory.** Iframes and live camera tiles are the heaviest things on a page; hidden and conditional
    cards still build and stream. A tablet's browser leaks on every reconnect after a long screensaver; schedule a
    page reload with the screen off, and a real app restart only under a free-memory threshold.

## Why

Shared pages drift into several conventions at once; an edit to one never reaches its twin; captions grow until a
tab is a phone-length essay. The rules exist so a page can be read, not decoded, by someone who was not in the
session that built it, including the owner a month later.

## How this goes wrong

- **Captions doing the names' job.** Pages full of explanatory captions and question headings ("Is anything
  wrong?") get skipped; better names ("Alarm System Status") make the captions unnecessary. Rules 2, 7.
- **The raw editor holds everything.** Pasting into the raw configuration editor replaces every view, not just the
  one you meant. Editing from a copy fetched before someone else's change loses theirs; re-fetch before each edit.
  Rule 8.
- **A feature that silently does nothing.** A card key that needs a plugin is ignored without an error when the
  plugin is missing; a button tests a state string that is not in the helper's options. Rule 12.
- **A control in the wrong place.** A tap on a page about leaks can start the sprinklers, with no confirmation.
  Rule 2.
- **Too long for a phone.** A tab with a dozen sections becomes an endless scroll. Rule 6.
- **A stray frontend resource.** One leftover custom resource breaks lazy loading and cards render blank; it takes
  a bisect to find. Rule 12.
- **A wall panel's own failures.** The screensaver timeout is shorter than the exit delay, so the panel goes dark
  mid-countdown; it drops off Wi-Fi with the screen off and does not reconnect; an origin change logs it out. Rule
  11.
- **Memory that never comes back.** A browser that runs for days accumulates detached page nodes; live camera tiles
  and frequent wakes make it worse until the panel slows or reloads. Rule 13.
- **A link the router swallows.** A same-origin markdown link to a file never opens. Use a button with a url path.
  Rule 12.

## How to check it

- A structural lint over the exported dashboards: no `input_*` on the first view; no `automation.` row outside
  Health; no digit in a row name; a regex for dates, "was ", "used to", "untested"; `confirmation` on every
  button; sections per tab ≤ 6; rows per card ≤ 8; a vocabulary word list.
- Sweep every dashboard for dangling entity references; expect 0.
- Diff the nightly export after a hand edit to see what actually changed.
- Wall panel: the user is non-admin and local-only; the "screen off in darkness" setting is off; the version
  string under `/local` was bumped.
- Wall panel memory: a new element TYPE on the panel (a new card type, resource, theme mechanism, animated or
  media element) gets a measured run before it stays: `templates/docs/wiki/measure-a-wall-panels-memory.md` (read
  the device's own screen state, force a GC and take 3 samples, cover a screensaver cycle, never improvise a screen
  toggle mid-run, record a void run as void). A row or tile of a kind already on the panel needs none.
- Review questions: "What question does this tab answer?" "Would a guest understand every word?" "Which rows are
  plumbing?" "What happens when nothing is wrong, and how do we know the card is right then?"

## Adapter notes

- **Phone vs tablet.** Sections stack on a phone; the frontend assigns sections to columns in order, so balance is
  the author's job.
- **Kiosk apps on Android tablets.** The usual kiosk app cannot reboot the tablet without owner rights; Android's
  doze kills Wi-Fi during screen-off; acoustic motion is the only way to wake a dark screen because touch does
  not; its screenshot skips map tiles and canvas graphs. Other kiosk apps: no incident recorded.
- **Custom cards.** Keep them for the wall panel only; phone pages use stock cards, so a plugin update cannot
  take the household's pages down.
- **Version-specific.** Card options change between monthly releases (map clustering, grid rows). Note the
  version a layout was built on in the page's status line.
