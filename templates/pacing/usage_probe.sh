#!/bin/sh
# usage_probe.sh - read the AI account's usage figures without spending tokens; publish the latest for routines.
# Status: template (O3b, 2026-10-13). Copied to pacing/usage_probe.sh when setup.agent.usage_probe is true
# (interview/generated-files.md). Principle: principles/budget-and-pacing.md rule 1. The gate that reads its
# output is pace_gate.py, next to it.
#
# How it works (Claude Code): starts a throwaway interactive `claude` in its own tmux session, types /usage, saves
# the screen, exits. /usage reads account figures and makes no model call - CHECK THIS ONCE on your version: the
# session's own cost line must read zero after a probe. If your agent has no usage screen, set
# setup.agent.usage_probe: false and gate on cost per run instead (adapters/agents/).
#
# Rules: never drive any other session's tmux; run from a folder the agent already trusts (no trust prompt);
# one probe at a time. The gate wants a read under 2 h old (older reads need 10 points of margin): prefer
# templates/runtime/usage_reader.py every 15-30 minutes, and use this probe only where the reader cannot run.
#
# Output: $USAGE_DIR/usage-YYYYMMDD-HHMM.txt (the whole screen, kept) and $USAGE_DIR/latest.txt (the summary
# lines with a "read <time>" first line). Schedule it with cron or the host's scheduler, about hourly.
#
# Settings (environment): USAGE_DIR (default ./usage), PROBE_DIR (a trusted working folder, default $PWD),
# AGENT_CMD (default `claude`).
set -u
D=${USAGE_DIR:-./usage}; W=${PROBE_DIR:-$PWD}; A=${AGENT_CMD:-claude}
S=usage_probe_$$; mkdir -p "$D"; F=$D/usage-$(date +%Y%m%d-%H%M).txt
command -v tmux >/dev/null || { echo "usage_probe: tmux is required" >&2; exit 2; }
tmux new-session -d -s "$S" -x 160 -y 50 -c "$W" "$A; sleep 20" || exit 1
sleep 15; tmux send-keys -t "$S" "/usage"; sleep 2; tmux send-keys -t "$S" Enter; sleep 12
tmux capture-pane -p -t "$S" > "$F"
tmux send-keys -t "$S" Escape; sleep 1; tmux send-keys -t "$S" "/exit" Enter; sleep 3
tmux kill-session -t "$S" 2>/dev/null
# Keep only the lines the gate reads; strip the bar characters. An empty capture still writes the "read" line,
# and pace_gate.py treats a file with no figures as "do not run".
# The zone is the IANA name (pace_gate.py cannot resolve an abbreviation such as CDT); falls back to the abbreviation.
Z=${TZ:-$(timedatectl show -p Timezone --value 2>/dev/null)}; Z=${Z:-$(date +%Z)}
{ echo "read $(date '+%Y-%m-%d %H:%M') $Z"
  grep -E "Current session|Current week|% used|Resets" "$F" | sed 's/[█▌▏▎▍▋▊▉ ]\{3,\}/ /g'
} > "$D/latest.tmp" && mv "$D/latest.tmp" "$D/latest.txt"
cat "$D/latest.txt"
