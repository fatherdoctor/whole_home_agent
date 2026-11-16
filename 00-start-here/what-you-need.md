# What you need

*Status: written (O2, 2026-10-13).*

## To have before you start
- **A machine for Home Assistant.** One of: the official Home Assistant Green; a Raspberry Pi 5 with an SSD; a
  small Intel or AMD mini PC; or a virtual machine on a server you already run. `choices.md` says how to pick;
  `install/` has a guide for each. If you are buying, do not buy until the agent has asked you about it.
- **A network the box can use.** Connect it by cable rather than Wi-Fi for setup. Router login is optional:
  use the box's working name or current address if you decline router changes. If you cannot use a cable, say so
  before installing so the agent can check a route for your hardware.
- **A phone** with the Home Assistant companion app (it is free, on iPhone and Android). Every household phone that
  should hear from the house needs it.
- **Somewhere off the box for a backup copy**: a cloud drive you already pay for, a computer that is usually on,
  or a network drive. The install is not done until a backup is there.
- **Somewhere for the emergency kit**: the backup encryption key and the authenticator setup key, in a password manager, on
  paper, or both. Never in this folder, never on the box.
- **An AI agent.** Either on your computer, with file and shell access to this folder (one page per runtime in
  `adapters/agents/`; each page's status line says how far it is tested), or on the box itself as its app once
  Home Assistant is installed. `README.md` in this folder says which way to start. **With only a chat app on a
  phone or tablet**, no agent is needed to begin: [`from-a-chat-app.md`](from-a-chat-app.md) walks the install, the account, the backups
  and later changes by hand. A Raspberry Pi or a mini PC still needs a computer once to write its drive.
- **An allowance for the agent**, and a sense of how much of it you want to spend a week. The agent will ask;
  `principles/budget-and-pacing.md` is the long version.
- **Time.** About two hours for the install, then half an hour of questions at your first request, then an hour
  or so per thing you build. The agent waits as long as you like between any two steps.

## What you do not need
- Any smart devices yet. The agent reads what you own and plans around it; it never asks you to buy a radio before
  the box is running.
- To know Home Assistant, YAML, networking or Linux. The agent explains each step in plain words and waits for
  "done".
- A public address, a domain, a VPN or an open port. Nothing is opened to the internet during setup.
- A voice assistant. If you have one, it is a choice (`choices.md`); if not, nothing is missing.
