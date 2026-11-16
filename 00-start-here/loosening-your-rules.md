# Loosening your rules

Start with Careful start if you want to approve each change. Once you understand what the assistant can reach and are
comfortable with its changes and recovery steps, you can choose Direct: an explicit request becomes permission for
that request, with a one-line report afterward. It still asks when unclear, beyond your request, or before deleting,
restarting, firmware or version changes, and still backs up before editing and checks configuration changes. You can
return to Careful start at any time. Neither set overrides stricter runtime or safety rules.

The [optional guard rails](../templates/agent-guard-rails.md) are separate limits you may add to either set:

- **Locks:** the assistant does not lock or unlock locks.
- **Alarm:** it does not arm or disarm the alarm.
- **Covers:** it does not open or close covers, including garage doors.
- **Cameras:** it does not access or control cameras.
- **Messages:** it does not send messages or notifications to people without your OK.
- **Publishing:** it does not publish content or changes externally.

These are instructions, not an access control. The guard-rails template explains how to add or remove individual
lines, start a new session and have the assistant read them back. To change starting sets, replace only your chosen
set in the assistant's instructions file with the other set from [house rules](../templates/house-rules.md), then
start a new session and ask it to read the rules back. Record what changed and how to undo it; keep secrets out.
