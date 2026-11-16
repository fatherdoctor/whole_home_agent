# Other agents

*Status: notes (O1); the first-session steps added after the O4 dry run (2026-10-14), which walked the kit as a
non-Claude agent; the mechanisms table moved to `templates/runtime/FALLBACKS.md` (KIT-RT0, 2026-10-23).*

`AGENTS.md` is the neutral entry point: any agent that reads a Markdown file at the start of a session should be able
to run the kit. **v1.0 is tested on Claude Code only; this page and the fallbacks are untested on other agents.**
OpenAI Codex has its own page, `codex.md` (lab notes, the STEP 0 line and its usage reader; not yet run through the
kit end to end). The principles do not depend on the vendor; the mechanisms do, and each has an equivalent.

The table of record is `templates/runtime/FALLBACKS.md` (KIT-RT0): one row per mechanism, keyed to the
capabilities STEP 0 records, with the path without it and who pays. This page keeps the first-session steps.

Whatever the agent: nothing reaches a person except the owner without their OK, never send to verify, verify before
claiming, report failures verbatim, secrets never in the repo. If the runtime cannot enforce read-only tools for a
sub-agent, do not run persona simulations against the live house at all; run them against an isolated clone.

## First session on a runtime that is not Claude Code
1. **Make `AGENTS.md` the file your runtime reads first.** If it reads `AGENTS.md` itself, nothing to do. Otherwise
   put one line, "Read AGENTS.md first; it is the standing brief.", in the file it does read (its rules or
   instructions file; the runtime's documentation names it).
2. **Lessons:** the memory file is `house/docs/gotchas.md`. Read it at the start of every Phase 2 session; append the
   day a lesson is learned.
3. **Reaching the box:** `install/agent-access.md`. A token in an environment variable is the common form; if your
   runtime cannot read environment variables, use `read: person-reads` and say so.
4. **No scheduler, no usage percentage:** keep `profile.agent.unattended: false` and `setup.budget.runs_per_day: 0`;
   the count gate is `setup.budget.items_per_session`.
5. **The secrets deny list:** if your runtime can deny file reads by path, deny the paths listed in
   `templates/runtime/claude-code-settings.json` before the first read of the box; if it cannot, say so in
   `house/runtime.yaml`, and the standing rule ("A secret in your output is a leak") is the only fence.
6. **The push guard:** install the hook (`templates/guard/README.md`). If your runtime pushes without git hooks,
   run the guard yourself before every push and stop on a non-zero status.
7. **No read-only sub-agents:** no persona simulations against the live house (above); single-agent reviews only.
