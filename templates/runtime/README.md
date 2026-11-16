# Runtime: the kit on any assistant

*Status: written (KIT-RT0, 2026-10-23). The contract every kit prompt, brief and tool follows so the kit runs on
more than one vendor's assistant. Six files here, and six rules for every other file in the kit. The probe script
(`probe_runtime.py`) is KIT-RT0s; the sweep that brings the existing kit files under rule 1 is KIT-RT1; the gate
that reads any provider's usage figure is KIT-PRB.*

| File | What it is | Goes to |
|---|---|---|
| `STEP-0.md` | The "where am I" block every run does first: observe the runtime, probe its capabilities, record them, name the fallbacks in one line | stays in the kit; briefs point at it |
| `FALLBACKS.md` | The table of record: for each capability the kit relies on, what the kit does without it and who pays | stays in the kit |
| `runtime.yaml` | The record's template: one entry per runtime the household uses, roles mapped to models, capabilities as yes / no / unknown | `house/runtime.yaml` |
| `probe_runtime.py` | Runs the probes a script can observe (shell, files, git, web, box), takes the rest from the agent (`--set`), writes or updates one entry in `house/runtime.yaml` only when a value changed or it is 7 days old, prints the step-d line | stays in the kit; run from the house repository's root |
| `usage_reader.py` | The Claude usage reader for the usage card (KIT-USE): reads the login's 5-hour and weekly use from the account usage endpoint (no model call), works out today's use, writes one JSON file Home Assistant reads; never refreshes, stores or prints the token | `house/usage/usage_reader.py`, run where the login lives |
| `usage_reader_codex.py` | The Codex usage reader (CX-KIT): asks the Codex client's app server for the account's rate limits (no model call, never touches the sign-in), writes the same file with `usage_reader.py`'s day bookkeeping; setup in `adapters/agents/codex.md`, "The usage card" | `house/usage/usage_reader_codex.py`, next to `usage_reader.py`, run where Codex is signed in |

## Rules for every kit file

1. **No vendor feature without its fallback.** A prompt, brief or tool that relies on a mechanism names the
   `FALLBACKS.md` row (or the `can:` key) in the same sentence, or does not rely on it. Vendor names and vendor
   feature names (an instruction file such as `CLAUDE.md`, a `.claude/` folder, "memory directory", a trigger or
   routine product, "skill", "MCP", a tool's name) appear only in `adapters/agents/<runtime>.md` and in
   `FALLBACKS.md`. Everywhere else the kit uses its own words:

   | Instead of | Say |
   |---|---|
   | `CLAUDE.md`, the instructions file | the runtime's instruction file (it points at `AGENTS.md`) |
   | a routine, a trigger | a scheduled run, a lane |
   | the memory directory | `house/docs/gotchas.md` |
   | a skill, a slash command | a prompt file (`tools/prompts/<name>.md`) |
   | an MCP server, a connector | the box read (`install/agent-access.md`), the clerk's list for the person |
   | a sub-agent | a helper agent (with its own tool list) |
   | a model's product name | its role: planner, builder, reviewer, mechanical, writer |

2. **Every brief starts with STEP 0.** A brief is any file an agent is told to read at the start of a session or a
   run (`AGENTS.md`, `house/tier2/BRIEF.md`, a lane's brief). Its first line after the title and status is
   "Do STEP 0 (templates/runtime/STEP-0.md) first." A brief whose runtime is fixed by construction (the tier-2 agent
   behind its two wrappers) still says it, and says that its entry is written for it and it probes nothing.
3. **Scripts are plain.** Python 3 with the standard library (or POSIX sh), printing a table a model can read; never
   a vendor SDK. A script that must call a model takes the model's name from `house/runtime.yaml` (`model_roles`),
   never from its own code.
4. **Model tiers by role.** A rule says "the reviewer" or "the mechanical lane", never a product. The household maps
   roles to models per runtime in `house/runtime.yaml`; a role may map to the same model as another when a household
   has only one.
5. **Detection is re-run** when an entry is over 7 days old, when the observed runtime is not the entry's, at the start
   of every unattended run, and when a probe fails mid-session (`STEP-0.md`, "When Step 0 runs again").
6. **A file that needs a capability says which.** A template, a prompt or a chapter that only works with a capability
   carries one line, `Needs: <can keys>` (for example `Needs: schedule, git_push`), so STEP 0's one-line report tells a
   run at once whether the file applies, and the dry run (KIT-DRY, once on each of two runtimes) can find every
   place a hidden assumption breaks; each break becomes a fix row before the release candidate.

## The usage reader

`usage_reader.py` feeds the assistant usage card (`packages/assistant-usage.yaml`, `custom_templates/usage.jinja`,
`dashboards/assistant-usage-card.yaml`). It is the one vendor-specific piece; the package, macros and card read only
its file, so another runtime gets the card by writing the same file (FALLBACKS.md row "(card)"); the Codex reader,
`usage_reader_codex.py`, does (`adapters/agents/codex.md`, "The usage card"). This section is the Claude reader.

- **Where it runs:** where the assistant's login lives (the assistant app on the box, or the machine Claude Code is
  signed in on), and where it can write into Home Assistant's config folder. Default login file
  `~/.claude/.credentials.json`; `--credentials` for another path. A login by API key has no account usage: the
  card stays unknown.
- **Schedule:** every 15-30 minutes with the host's scheduler, e.g. cron
  `*/20 * * * * python3 house/usage/usage_reader.py --out /config/assistant_usage/usage.json --tz Area/City`.
  The package reads `/config/assistant_usage/usage.json`; change both together. `--tz` is Home Assistant's own time
  zone (Settings > System > General), not the host's: most containers run in UTC, and a different zone leaves today
  unknown between the two midnights. The reader warns when `--tz` is omitted.
- **After the first restart:** set the weekly warning level and the daily budget helpers (usually 80 % and 14.3 %);
  until then they sit at their minimums and the card says "Thresholds not set".
- **The token:** read into memory for the one call, never written, logged, printed or put on a command line, and
  never refreshed (a refresh rotates the login and can sign the assistant out). An expired or refused token is
  `status: stale` until Claude Code refreshes it on its own next use.
- **What the file holds:** `read_at` (the last good read), `status` (`ok`, `stale`, `error`, `unknown`) and
  `reason`, `plan`, `session` and `week` (`pct`, `resets_at`, `severity` when the provider sends one), `models`
  (per-model weekly figures where the plan has them), `today` (`pct`, `date`, `since`) and the reader's own `day`
  bookkeeping. A failed read keeps the last good figures and their `read_at`; the card turns them unknown after two
  hours.
- **Today:** the rise in the weekly % since local midnight, carried across the weekly reset. The reset is read from
  the provider's reply (a later `resets_at`, or the weekly figure dropping), not the clock: a read after the reset
  time that still carries the old window is `stale` ("waiting for the weekly window to roll") until the provider
  rolls. `since` says what is counted: midnight, the last read before midnight (up to an hour before) when that is
  the base, the reset when the week rolled before the day's first read, or the first read of the day when the
  reader was down over midnight (a lower bound, never padded).
- **Redirects are refused** (urllib would forward the token to the host a redirect names): a 3xx is
  `status: error`, "the usage endpoint answered 30x". A 200 that is not JSON is an error too, not a changed shape.
- **The endpoint is unofficial** (the one the client uses for its own usage screen). A reply without the weekly
  figure is `status: unknown` with reason "reply shape changed": open a fix row; the card shows unknown meanwhile.
- **Check it once by hand:** `python3 house/usage/usage_reader.py --out /tmp/usage.json --dry-run` prints the file;
  its week % must match the assistant's own usage screen. `--reply saved.json` replays a saved reply offline (a
  reply carries no token, so a saved one is safe to keep as a test fixture).

## Checking rule 1

From the kit's root; the result should be empty but for lines that only name a file by its path (below). Case-insensitive, with the product names rules 1 and 4 forbid.
Exempt, each for a reason: `adapters/agents/` and `templates/runtime/` (and the `templates/README.md` rows that
name them): the one place vendor names may appear; `.github/workflows/attribution.yml`: a check that needs the literal patterns of
one tool's session link and trailer; `interview/profile-template.yaml`: the runtime enum is data that STEP 0 probes;
`examples/dry-run`: history; the root `CLAUDE.md`: the one vendor file the kit ships, and it only points at
`AGENTS.md`; `templates/tests/` and `templates/pacing/`: test fixtures and a usage-screen sample that need a model
name as data; `adapters/voice/alexa.md`: "skill" is the voice platform's own noun; `00-start-here/chat-app-starter.md`: built
from `adapters/agents/` pages by `tools/chat-starter/build_starter.py`, never edited by hand. At `1b37be8` the sweep found 36
files and 112 lines (44 of them the word "routine"); the CX-SWEEP pass (2026-11-10) leaves four lines outside the exempt
list (in `README.md`, `AGENTS.md` and `adapters/README.md`), each of which only names an adapter page or a
`templates/runtime/` file by its path. "Routine" is the kit's own word for a scheduled lane job or ordinary English, so the regex no longer carries it.

```sh
grep -rniE 'CLAUDE\.md|\.claude/|memory directory|RemoteTrigger|\bskills?\b|\bMCP\b|\bmcp__|sub-?agents?|\bClaude\b|\bChatGPT\b|\bCodex\b|\bOpenAI\b|\bOpus\b|\bSonnet\b|\bHaiku\b|\bFable\b|\bGemini\b|\bCopilot\b' \
  --exclude-dir=.git --exclude-dir=__pycache__ . \
  | grep -vE '^\./(adapters/agents/|templates/runtime/|examples/dry-run|templates/tests/|templates/pacing/|CLAUDE\.md:|.github/workflows/attribution\.yml:|interview/profile-template\.yaml:|adapters/voice/alexa\.md:|00-start-here/chat-app-starter\.md:|templates/README\.md:[0-9]+:.*runtime/)'
```

A hit is either a vendor word to replace with the table's word, a product name to replace with its role, or a real
dependency that needs a `FALLBACKS.md` row and a `Needs:` line. A hit that is only an adapter page or a `templates/runtime/` file named by its path (`adapters/agents/claude-code.md`, `codex.md`, `templates/runtime/claude-code-settings.json`) is a pointer, not a vendor word. Kit tests may carry the same check as a case once the sweep is done.
