# The choices

*Status: written (O2, 2026-10-13). The agent asks about these in Phase 0 and Phase 1. Every one has a default;
every one can change later, some more cheaply than others (the table says which).*

| Choice | Options | The trade-off in a sentence | Default | Cost to change later |
|---|---|---|---|---|
| **Hardware** | HA Green; Raspberry Pi 5; mini PC; a VM on your server | Green just works and never grows much; a Pi is cheap and fine with an SSD; a mini PC grows for years; a VM gives you snapshots and a staging copy but ties the house to the server's upkeep | Green if you want zero fuss; mini PC if you expect to keep adding | A backup restores onto any of them in an hour; the radios move with their USB sticks |
| **Radio for new devices** | Zigbee; Z-Wave; Matter over Thread; Wi-Fi | Zigbee: cheapest and widest, needs a USB stick on a cable; Z-Wave: the lock radio, fewer and pricier devices; Matter/Thread: the new standard, fewer devices today, needs a border router; Wi-Fi: no hub, but every device is on your network and your router's mercy | Zigbee; Z-Wave if you want a lock; Matter if your devices already are | Re-pairing every device of the old radio: a weekend |
| **Voice assistant** | Alexa; Google; Apple (Siri); Assist (local); none | The cloud ones are easy and listen to a company; Assist is private and newer; none is a fine answer | What is already in the house; otherwise none | Low: voice only ever controls lights, switches and scenes |
| **How the house reaches you** | The companion app; plus Pushover, Telegram, text or a call later | The app is free and enough for a household; the others are for reaching people who do not have the app, or for when nobody answers a push | The companion app, nothing else at first | Low for a second push channel; a text or call ladder is a design in its own right (consent, numbers) |
| **Reaching the house from outside** | Not now; Nabu Casa; a VPN; a reverse proxy | Nabu Casa is paid and safe and funds the project; a VPN is free and yours to run; a proxy is for people who already run one; nothing is opened during setup | Not now | Low |
| **The agent** | The runtime you have (`adapters/agents/`, one page each; the status line on each page says what is tested) | The principles do not care; the mechanisms do (`adapters/agents/`) | The one you have | Low: the house's files are plain text |
| **Where the agent runs** | Your computer, in this folder; on the box; in the cloud with the files only | On your computer it sees the box over the network and you see what it does; on the box it can run on a schedule; in the cloud it can only draft | Your computer | Low |
| **Budget reserve** | A percentage of the week kept back | Too small and the agent runs out mid-change; too large and nothing gets done | 10 %, 20 % when you are away | Nil |
| **Budget target** | Spend the week's allowance by the reset, or by an earlier time ("95 % by Saturday 10:00") | Pacing to the reset uses every hour; an earlier target leaves the last hours free for you and makes the agent's pace steadier | The reset | Nil |
| **Backups** | Daily on the box; a copy off the box; snapshots and a staging clone on a VM | Every tier protects against a different failure (`principles/backups-and-recovery.md`); the hardware decides which are possible | Every tier the hardware allows | Nil |

You choose the agent's limits, including whether to use the optional [guard rails](../templates/agent-guard-rails.md)
for locks and alarms. These are instructions, not an access control; the agent's actual permissions still matter.
Secrets stay out of this folder, and the other safety rules on codes, consent and messages still apply.
