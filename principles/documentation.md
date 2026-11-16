# Documentation

*Status: written (O1, 2026-10-11); the wiki's delivery, archive and page rules added (KIT-SYNC-1107, 2026-11-07).
Distilled from a real install; the failure modes are written generically.*

CHANGELOG, gotchas, a user manual for the household, a maintainer wiki for the builder.

## The rule

1. [core] **CHANGELOG discipline.** One entry per change, newest first, with the authorization behind it (who, when, what
   was agreed), the time, the commit, the checks run, and the undo. When an entry needs more than a few lines, the detail goes in
   the design doc or the commit, not the log.
2. [core] **A gotchas file.** One failure mode per entry with the rule it taught. Historical narrative and lessons are
   different things: the lesson stays in the working tree, the narrative moves to an archive, and nothing moves
   until its lesson has been extracted. Write the rule, never the value.
3. [default, topic 10] **A user manual for the household**, with guest and household tracks, its own contributing standard, a writer
   that cannot see the box, and a notes file where sessions queue changes instead of editing pages.
4. [default, topic 10] **A maintainer wiki for the builder.** One page per integration, device model, package, automation, dashboard
   and subsystem. A schema fixes page types (thing, procedure, incident) and sections; a facts box is generated
   from the live export and never typed; every claim is cited; every external source is archived (a page snapshot,
   a PDF, a package at the installed commit) with a hash and license. A writer brief, and a nightly reviewer that
   writes findings but never edits a page. The bar the owner set: the owner back after a long time away, a
   contractor, or a future agent with no memory can recreate the install from the wiki alone, and the install
   means everything bought and built, the computer and its components included, not only the Home Assistant
   configuration.
5. [default, topic 10] **A document standard, applied forward-only.** A title block with a dated bold status line; sentence case; no
   reflowing of untouched paragraphs; tables not diagrams for data; strike-and-date rather than delete; "see
   section 5.2", never "see above". A linter measures; a routine judges language. No sweeps unless asked by name.
6. [default, topic 10] **Two nightly routines.** A keeper reconciles dated status claims older than three days against the changelog
   and the live export, a few edits a run, never writing under another writer's product. A checker reports what a
   script cannot see and never lints history.
7. [core] **The live export outranks any prose.** When a document and the export disagree, the export wins and the page
   records the disagreement in one line. Cite the entity id or the export filename, never a description. If the
   export does not cover a fact, say "unverifiable" and stop.
8. [core] **Generated files are never hand-edited; fix the generator.** A hand-maintained roster of registry state is a
   known failure.
9. [core] **Dates in prose carry one declared timezone**; on-box sessions convert from UTC.
10. [default, topic 10] **Serve the wiki as one small file per page.** Each page is its own HTML file; the stylesheet,
    script and search index are shared files named by a hash of their content; pictures are files (named by content,
    loaded lazily), never embedded as text; a search index of every page's headings and opening text is fetched the
    first time the search box is used. The front page keeps a small router so old deep links (`#page`, a QR code on
    a panel, bookmarks) reach the right file. Every file carries its own version and checks a no-store version file
    first thing, reloading itself when the server has a newer copy, so a phone's long cache never shows an old page.
    A rebuild rewrites only the files whose bytes changed, and a link check runs on the built site.
11. [default, topic 10] **Archived manuals are readable by every writer.** Manuals and maker documents archived on the
    box are extracted, by a model-free job, to text and to candidate pictures (line drawings, diagrams) in the repo,
    so a writer that cannot see the box can read and cite them. A page may not call a manual missing, or an interval
    unknown, when the extracted text exists; the build checks "not archived" phrases against the archive.
12. [default, topic 10] **Page rules that keep pages honest.**
    - A lessons section is optional and never padded: omit it when nothing surprised anyone.
    - Maintenance holds care tasks from the manual or the maker, each with its interval and citation (or a cited "the
      manual gives no routine maintenance"). Operating schedules (when a pump runs, when a light comes on) belong in
      the automation section, not under Maintenance.
    - Look before listing a gap: the archive text, the device ledger, then the maker's site. A gap that one of those
      answers is a page error, not an open question.
    - A layout or formatting pass never marks a page verified; only a pass that checked its facts against sources does.
    - Physical things (an appliance, a valve) and digital things (an automation, a dashboard) are different page
      shapes: a physical page has no live-house facts box and needs a maker, Maintenance and a picture.
    - Emergency "if something is wrong" help lives on one landing page (the one a panel's help link opens), not
      scattered across pages where it goes stale.

## Why

A stale map is worse than none: a reader trusts a map and stops looking, so a wrong one sends them confidently to
the wrong place. One sweep found the design docs wrong in the expensive direction eleven times, every one a prose
fact that had moved. The owner's bar for the wiki is to rebuild the house from it alone.

## How this goes wrong

- **A bot everyone thinks exists.** People believe a routine keeps the design docs current, and none does. A device
  goes into service, the doc still says it is not, the manual copies the doc, and a guest page tells a visitor the
  wrong thing. Rule 6.
- **A roster kept by hand.** A prose list of which entities carry a label goes wrong, and the script that targets
  the label does nothing, silently. Rule 8.
- **A to-do list in the README.** It is stale within a week. Keep work in the backlog (`backlog-and-planning.md`
  rule 1).
- **A sweeping auto-fix.** A terminology fix across every page needs round after round of exceptions and still
  produces sentences that use both terms. Apply standards forward only. Rule 5.
- **A checker that trusts a mirror.** A doc checker compares against a mirror file that is itself stale, and
  reports the contradiction backwards. Rule 7.
- **Two sources for one routine's rules.** A brief and a routine prompt disagree; one is edited, the other wins,
  and a reversed rule runs for days. Keep one source. Rule 6.
- **A real secret in a worked example.** A gotcha explains a lock problem with a real code, or a real phone number.
  Use placeholders. Rule 2.
- **One 25 MB page.** The whole wiki, pictures embedded as text, is one file; a phone loads all of it for one page,
  and the self-reload script inside it runs late or not at all, so the owner reads a day-old page after two rebuilds.
  Rule 10.
- **"Manual not archived" over an archived manual.** The manuals were fetched to the box, but the cloud writer could
  not see them, so pages said the manual was missing and Maintenance was empty. Rule 11.
- **A padded page.** A required lessons section gets filled with invented "lessons", and a pump's run schedule is
  filed under Maintenance, so the page passes the lint and teaches nothing. Rule 12.
- **Times in two zones.** A UTC timestamp copied into local prose puts an event hours off, and the next reader
  builds on it. Rule 9.

## How to check it

- Every status line has a date.
- The log folders for the keeper, checker and writer show one file per night.
- The wiki build's lint shows zero uncited claims and zero secret-shaped strings.
- A grep (`-l` or `-c`, never default output, so a real hit does not land in the transcript) for phone-number and token shapes over the repo returns nothing.
- The index's counts match the live export.
- The built wiki's link check reports 0 problems; no picture is a data URI, and no page file is much over about
  1 MB (a phone loads one page, not the wiki).
- A stale cached copy of a page, opened in a phone-size browser, reloads itself to the current build.
- Every manual in the box's archive has its extracted text in the repo, and the build's "not archived" check is clean.

## Adapter notes

- Hardware-neutral.
- **AI agent.** The nightly writers, keeper and checker are scheduled cloud routines reading a standing brief file.
  Another agent needs an equivalent "brief outranks prompt" file and a log-per-run convention. Lessons an on-box
  agent keeps in its persistent memory are exported into the wiki's raw notes so routines without box access can
  read them.
