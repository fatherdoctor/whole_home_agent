# The maintenance calendar

*Status: written (2026-10-17). The design pattern from a real install; its build is in progress there.*

Filters, flushes, coil rinses, lubrication, seasonal yard applications, contractor visits. A shared calendar holds
the schedule; Home Assistant turns it into alerts the household can act on.

## The rule

1. [default, topic 9] **A dedicated calendar is the schedule of record.** One calendar ("Home Maintenance"), owned by the owner,
   visible to Home Assistant through its calendar integration. Recurring tasks are recurring events whose
   description holds the window, the how-to (or a link to the approved procedure) and the source of the rule.
   Contractor visits go on it too.
2. [core] **HA triggers on the calendar, not on its own copies of dates.** A calendar trigger at event start opens a task;
   the alert goes through the notification router on a maintenance track, household only, never to guests.
3. [core] **Every task can be acknowledged, deferred or closed.** Acknowledge stops the repeats and leaves it open;
   Defer (a day, a week, a date) writes a new event and marks the old one; Done records the date and who, into a
   service-history log the wiki reads. Open tasks survive a restart and show on a maintenance card with the same
   three actions; a weekly digest replaces nagging. Done on one occurrence never ends the series.
4. [core] **Seasonal tasks are windows with gates, not due dates.** The event opens a window; inside it HA watches the
   conditions the task depends on and says "now is a good time": a decent rain in the forecast for anything that
   must be watered in (fertilizer, pre-emergent where irrigation will not do it), soil temperature for
   pre-emergents (a modeled forecast is enough; no probe needed), a dry spell for sealing. A "window closing"
   nudge comes near the end. Thresholds come from an extension service, stated in the event.
5. [core] **History is recorded even when it predates the system.** A task the owner already did is entered as a
   one-off done event, so the first reminder knows the last date.
6. [core] **The agent writes to the calendar only with the owner's request or approval**, and never sends invitations or
   emails when it creates or edits an event.

## Why

People already live in their calendar; a parallel list in HA is one more place to forget. Weather and soil gates
turn a fixed date into the right day, which is the difference between a reminder that helps and one that gets
dismissed.

## How this goes wrong

- **The integration does not see a new calendar** until it reloads; a trigger on it never fires. Reload the
  calendar integration once after the calendar is created and confirm the entity.
- **A deferred task fires twice**: the original event and the new one. Rule 3 marks the original.
- **Recurring events closed as a series** by a Done on one instance; the next year's reminder never comes.
- **A date in a message disagrees with the calendar** (one date in the message, another on the calendar). The calendar is the record; ask.

## How to check it

- The calendar entity exists and its next event matches the calendar app.
- A test event (no notification sent) opens a task in a dry run, and Defer creates exactly one new event.
- Every recurring event has a window and a source in its description.

## Adapter notes

- **Calendar:** Google, Microsoft 365/Outlook, CalDAV or a local calendar all work with HA's calendar trigger;
  writing events back (Defer) needs an integration that supports creating events.
- **Weather:** any forecast integration with daily precipitation amount and probability; soil temperature from a
  modeled source (for example Open-Meteo) through a REST sensor.
