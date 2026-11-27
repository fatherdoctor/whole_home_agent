# Contributing

Bug reports, corrections and ideas are welcome. Every change starts from an issue, so we can agree on the approach before a pull request shows up.

## Making a change

1. **Open an issue first.** Say what you want to change and why. If an issue for it already exists, use that one.
2. **Work on a branch** and open a pull request into `main`. Put one change in each pull request. Never push to
   `main`.
3. **Link the issue.** The pull request description says `Closes #n`, so the issue closes when the pull request
   merges.
4. **Keep later work open.** If a change is wanted but not now, its issue stays open with the `backlog` label.
   Don't close it just because nobody is working on it.

Before you push, run the checks CI runs: `python3 tools/chat-starter/build_starter.py --check` and `python3 tools/chat-starter/test_build_starter.py`. `AGENTS.md` has the rules for an agent working in the kit.

## Reporting a bug

Use the **Bug report** form when you open an issue. It asks for:

- The kit page and step where it went wrong.
- Which assistant you were using (ChatGPT, Claude, or another).
- Your Home Assistant version, if you have one running.
- What the assistant said, pasted, and what you expected instead.

Remove names, addresses, phone numbers, passwords, codes, tokens, and your Home Assistant address from everything you paste. This repository must never hold details about a real house.
