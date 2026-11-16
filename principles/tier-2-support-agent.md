# Tier-2 support agent

*Status: written (O1, 2026-10-11). Distilled from a real install; the failure modes are written generically.*

An always-on watcher with fenced actions, race rails, ask-before-act, and its own health.

## The rule

1. [core] **The agent is a back-stop behind the automated back-stops.** The house must keep working with the agent dead.
   Nothing in the house depends on it except the one watchdog that reports its silence.
2. [core] **Authority lives in enforced levels, not in the prompt.** L1: act and journal (reads, wake or reload a page,
   reload a stuck integration entry from a short list). L2: act, then push the owner at once, at most three an
   hour (turn off a misbehaving automation, cancel a timer, undo its own actions). L3: ask, act after a long
   timeout with no Hold or at once on Go (restart Core, an app, the panel, the VM). L3 ask-only with no
   timeout: any config edit. L4: never.
3. [default, topic 8] **The never list.** Disarm, unlock, open the garage, read or change codes; silence a real alarm, smoke or CO
   event; message anyone but the owner; edit config, dashboards, helpers or secrets; touch the hypervisor beyond
   reading; push to the main branch; any firmware, re-pair, route rebuild or radio reload; act during an alarm
   incident; act on anything it has never seen working.
4. [core] **No raw shell.** Every read and every act goes through two wrappers that hold the rules, the protected list,
   the sensitive-id filter and the rate counters. The model cannot write the wrappers, its own journal, status or
   counters. A refusal is final, not a puzzle to solve.
5. [core] **Race rails on every act.** Nothing while the alarm is arming, pending or triggered, while a life-safety
   incident is open, during the doorbell minute, while an announcement plays, or on a target with a pending ask.
6. [core] **No invented playbooks.** A symptom not in the table gets one push per cause per six hours, then waiting. A
   radio finding is reported, never prescribed unprompted: the push carries the readings and what fixed it last
   time, and a recommendation (a power cycle included) goes out only when the person asks for one through Suggest
   (rule 16). The agent never proposes air-gapping a device on its own.
7. [core] **Asks are bound** to one verb and one target with their own Hold and Go buttons. A stale tap cannot answer a
   later ask; an ask whose condition has gone away is withdrawn, never left live.
8. [core] **Two liveness watchdogs for two failure modes.** A deterministic checker (plain code, no model) runs every five
   minutes and touches a heartbeat; the model stamps "pass done". The house pushes the owner if the checker is
   silent for two hours or the agent for about half a day.
9. [core] **The checker finds; the model decides.** The checker injects only a finding id, never free text from a state
   or a log line, so nothing stored in the house can become an instruction.
10. [core] **Pushes are problems and resolutions only**, one cause per push, in plain words, never "all is well". A
    planned reboot (the marker is set, `health-checks.md` rule 10) is journaled, not pushed, on the boot path as
    well as the session-restart path; a marker older than a few hours is stale and ignored, so a forgotten one
    cannot silence a real crash. The wrapper's push IS the push; the agent never duplicates it.
11. [default, topic 9] **Check-ins are a fixed list of numbered OK / CHECK lines** (panel, keypad, boards, radios, network, box,
    power, integrations, health counts, budget) plus only what is new. Never a finding code without its meaning.
12. [default, topic 9] **Cost is context × turns.** One read-only verb returns everything a pass needs; two check-ins a day; a fresh
    session every morning; the checks themselves are never budget-blocked, and idle work runs only when the
    preflight says `idle work: yes` (`templates/pacing/preflight.py --role monitor`, `budget-and-pacing.md` rule 3);
    idle work is read-only and never delays a finding.
13. [core] **Self-heal its own login** (restart on a stale token, at most hourly; one push a day if it stays dead); wait
    ten minutes after boot for the house to settle; a launcher guard prevents two agents.
14. [core] **An out-of-band queue** for anything only the on-box session can do: a counted row with a due date; a struck
    row names the measurement that proves it, not the artifact that suggests it.
15. [core] **Every alert gets its "back" push.** When a finding the model was woken for clears, the checker wakes it
    with the finding id and the model sends one push on the same cause, replacing the alert on the phone: what is
    back, since when, and how long it was out. A resolution carries no advice and no Suggest button.
16. [core] **Suggest is on demand and report-only.** Problem pushes carry a Suggest button; resolutions never do. A tap
    is acknowledged at once by the house itself, on the same tag so the answer replaces it ("looking into it");
    the checker wakes the model, which answers with one push: one sentence, about two hundred characters, the
    suggestion only (the title already names the problem). The answer never acts and never schedules an act.
    Taps are capped per day, a tap on an unknown push is journaled once, and the button writes to its own helper
    and automation so a tap can never answer a Hold or a Go.

## Why

A model with a shell and an API token can disarm the alarm in one crafted call; levels in a prompt are advice,
levels in a wrapper are a fence. Unattended permission prompts hang rather than refuse, so the session must run
deny-by-default. The owner reads pushes on a phone during a trip: one cause, plain words, a button that cannot
misfire.

## How this goes wrong

- **A shell allowlist.** An allowlist of commands cannot stop a crafted service call, and a device helper that
  allows `reboot` is a reboot verb. Database access lets a joined query read code helpers. A naive local time turns
  an hour's log window into several. Hence wrappers only, no recorder access and timezone-aware timestamps. Rules 2,
  4.
- **One unfenced verb.** A reload verb accepts any integration in any state; reloading one that is waiting for a
  sign-in wipes the re-auth prompt. Fence each verb to named targets and conditions. Rule 2.
- **Two voices for one event.** The wrapper and the agent both push "app restarted", or the agent and the
  health system both push the same rise. Symptom: two pushes, one cause. Rule 10.
- **Answering a different question.** With only a whole-house read, the agent answers a question about one thing
  with a tour of everything. Give it narrow verbs and tell it to name another subsystem only when it is a fault now.
  Rule 10.
- **Text nobody can read.** Check-ins in generic prose, with finding codes that mean nothing to the person reading
  them on a phone. Rule 11.
- **Cost from context.** A frequent pass on a large context, or duplicate schedules after a crash, spend millions of
  tokens a day on nothing. Rule 12.
- **A shared, stale login.** Several sessions share one credentials file; a long session keeps a token after it is
  rotated and fails until restarted. Rule 13.
- **An ask answered by an old reply.** Text replies cannot say which ask they answer, so a day-old push still in a
  phone's notification shade answers a newer one. Bind Hold and Go buttons to an ask id. Rule 7.
- **A failure the agent cannot see, and a remedy it invents.** The agent cannot see radio noise, so a jammed mesh
  goes unnoticed; once it can, the tempting playbook (restart, rebuild, re-pair) does nothing for noise. Push the
  readings and the known fix, and invent nothing; a recommendation waits for the person to ask through Suggest.
  Rules 6, 16.
- **A failure that takes the agent with it.** When the VM is unreachable, the agent and every on-box watchdog are
  down too. Do not pretend to cover it; say so. Rule 1.
- **A reboot the agent was told about, reported as a crash.** The session-restart path honors the planned-restart
  marker; the boot path, written later, does not, so every planned host reboot pushes "reboot complete" and
  journals an unplanned outage. One marker, read by every path that can push, with an expiry. Rule 10.
- **An alert with no ending.** A device goes offline during electrical work and the owner hears about it; it
  comes back and nobody says so, so the alert stays open on the phone and in the owner's head. Rule 15.
- **A suggestion that is an essay, or an action.** An answer too long to read on a phone, or a "suggestion" that
  executes itself, which is an act outside the levels. One sentence, report-only. Rule 16.

## How to check it

- The pre-deployment list: a dry start acts on nothing; a STOP file holds every action; four forbidden calls
  (disarm, a free shell, read a code cache, rewrite its status) come back as logged refusals with no hang and no
  action; Hold stops a fake ask; the fourth L2 in an hour becomes a push; a planned reboot brings the agent back
  within fifteen minutes; a second launcher run finds the existing session; the token expires after the trip.
- Weekly: usage numbers in the check-in; one schedule only; the journal has an undo line for every L2.
- Tap Suggest on a test push: the acknowledgement arrives at once on the same tag, one answer follows within
  minutes, a second tap on the same push is refused, nothing acted. A resolution push shows Dismiss only.
- Set the planned-restart marker and reboot: the journal gains a line and the phone nothing. Let a marker go
  stale and reboot: the push arrives.

## Adapter notes

- **Per runtime.** How to run it headless with a fixed model and a deny-by-default permission mode is on the
  adapter page, `adapters/agents/<runtime>.md`. Scheduled tasks created in a session die with it, and cron is UTC
  (daylight-saving shifts it).
- **Other agents.** Reproduce deny-by-default and the two-wrapper fence. If the runtime cannot auto-deny, do not
  run it unattended. See `adapters/agents/other-agents.md`.
- **Pi / HA Green.** No hypervisor: L3 "reboot the VM" becomes "reboot the host" with no snapshot before it. The
  app model (an SSH app with protection mode off, a terminal multiplexer) assumes the Supervisor.
- **Mini PC or VM.** The hypervisor token stays L4 (read-only, never stop or reset).
- **Radios.** The noise and mesh findings are Z-Wave diagnostics; Zigbee has its own "x of y online" and label
  exclusion.
- **No wall panel.** Drop the panel findings and the tablet wrapper entirely.

## Beyond the house: a portable starter prompt

The same shape (scripted checks first, the model woken only on findings, authority levels enforced in wrappers,
bound asks, two watchdogs, a budget gate, Suggest on demand, planned-work markers with an expiry) has been
written as a portable starter prompt that turns a general-purpose coding agent into an engineering agent for any
system you name: it interrogates the system, asks a short fixed set of questions, proposes a monitor catalog,
builds the checker and the wrappers, and touches a control system only through a per-point ladder the operator
writes (report-only by default, a shadow period before any live write). It names no industry; a domain profile
is appended. It is a sibling document of this kit, kept to the same rules (generic, no incident detail); a
portable version is planned for the kit, and this chapter will point at it when it lands. Nothing in it changes
the rules above for a house: a house agent's never list stays as written.
