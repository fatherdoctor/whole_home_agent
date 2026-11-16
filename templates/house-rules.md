# House rules: choose a starting set

The owner chooses how the assistant handles an ordinary request. Explain both sets in plain words and recommend
**Careful start** to a new owner. Copy only the chosen set into `/config/AGENTS.md` for the ChatGPT app or
`/config/CLAUDE.md` for the Claude app when its working folder is `/config`; otherwise use the instructions file
in its working folder. Add to the existing file; do not replace its other instructions. If the assistant cannot
install or read the instructions, help the owner do it and check them in a new session. These instructions do not
change the assistant's actual access or override stricter runtime or safety rules. Keep secrets out of the file
and chat.

## Careful start (recommended for a new owner)

```markdown
Before each change, say what you will change and wait for my yes. Back up before editing. After a configuration
change, run the Home Assistant configuration check and report the result. If a check cannot run or fails, say so.
```

This lets you see each proposed change before it happens. It takes more confirmations.

## Direct

```markdown
My direct request is the go-ahead for the change I asked for. Make it, then say in one line what changed. Ask first
when my request is unclear, a change goes beyond what I asked, or before deleting, restarting, firmware or version
changes. Back up before editing. After a configuration change, run the Home Assistant configuration check and report
the result. If a check cannot run or fails, say so.
```

This takes fewer confirmations for changes you specifically request. It still asks in the cases above. You can add
[optional guard rails](agent-guard-rails.md) to either set, and change your choice later using
[Loosening your rules](../00-start-here/loosening-your-rules.md).
