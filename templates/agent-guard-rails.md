# Optional agent guard rails

When the assistant checks with you before a change is set in two places: the app's own permission setting
(its page explains the modes) and the starting set you chose in [house rules](house-rules.md), Careful start or
Direct. The lines below are extra limits you can add on top of either. For example, if you choose the lock line,
the assistant cannot lock or unlock a door for you, though it can explain how. None of these extra lines is selected
for you.

These instructions are not a lock: an assistant or another way of controlling the system may still have access.

## Choose and install

1. Pick any lines you want from the list below. Copy only those lines, with the two markers, into the file the
   assistant reads in its working folder: `/config/AGENTS.md` for the ChatGPT app or `/config/CLAUDE.md` for
   the Claude app when its working folder is `/config`. Add the lines to the existing file; do not replace it.
   If the working folder is elsewhere, use the instructions file in that folder.
2. Ask the assistant to read your chosen limits back to you without taking an action. If it cannot see them,
   check which folder it is using and which file it reads. Write down your choices where you keep your house rules.
3. To remove a limit later, remove that line from the same file. Start a new session so the assistant reads the
   updated instructions, then ask it to read the limits back again.

```markdown
<!-- BEGIN owner-selected agent guard rails -->
- Do not lock or unlock locks.
- Do not arm or disarm the alarm.
- Do not open or close covers, including garage doors.
- Do not access or control cameras.
- Do not send messages or notifications to people without my OK.
- Do not publish content or changes externally.
<!-- END owner-selected agent guard rails -->
```

You can choose just one line or make a limit narrower by writing what it covers. Keep passwords and other secrets
out of the instructions and the chat. When you change a limit, write down what changed and how to undo it.
