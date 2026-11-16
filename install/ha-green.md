# Installing on: Home Assistant Green

*Status: written (O3a, 2026-10-13; Green only from KY, 2026-10-13). Sources: the official Home Assistant
installation pages, which hand Green setup to Nabu Casa's support site (support.nabucasa.com, "Home Assistant Green
documentation"). The Nabu Casa pages could not be read when this was written: the agent should open them with the
person and correct anything here that differs.*

**For the agent:** this is the shortest guide in the kit; most of the work is in `network-and-backups-first.md`.

## What it is
- **Home Assistant Green** is the official ready-made box: Home Assistant OS comes installed on its internal
  storage, so there is nothing to write or flash.
- It has no Zigbee or Thread radio; a USB radio such as Home Assistant Connect ZBT-2 adds one (`adapters/radios/`).

## Before you start
- The box, its power supply (in the box), and an **Ethernet cable** to the router. Setup is over Ethernet, and the box
  should stay wired.
- A computer or phone on the same network. A router login is optional, only if you choose a reservation.

## Install
There is nothing to install.
1. Plug the Ethernet cable into the box and the router.
2. Plug in the power. The box starts on its own.
3. Wait a few minutes. The first start downloads the latest Home Assistant, so the first screen you see may say it
   is preparing; let it finish.

## Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network. The Green has no
   screen; if the name does not work, use the no-router route in `network-and-backups-first.md` section 1 to find
   its current address. Router changes are optional, with no as the default.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. Keep the address that opens it.
3. On the welcome screen choose **Create my smart home** (or restore a backup if you are moving an existing house
   onto this box; see `network-and-backups-first.md`, and check the box has more free storage than the old house
   uses).
4. Create the owner account (use a password manager), set the home location, time zone, units and currency.
5. Choose what to share with the project.
6. **Skip the discovered devices for now** unless one is essential; Phase 1 names things on purpose
   (`principles/naming.md`).
7. **Fresh installs only:** defer offered updates until `network-and-backups-first.md` section 3 has made
   a backup and a copy off the box; then follow section 4. A box already running instead follows that guide's
   **section 0: local backup and full update first**, before other changes. A fresh image already current
   needs no update.

**Jumping ahead:** If you choose [Jumping ahead](../00-start-here/from-a-chat-app.md#jumping-ahead),
you may update after making a local backup first and leave the off-box copy until later. A local backup
is lost with the box if the box or its storage is lost or fails.

## Network: a working name or address
The goal is to reach the box at a stable name or address. A reservation is optional. If you decline router
changes, record that choice and the tested access kind in the profile, as section 1 of
`network-and-backups-first.md` explains. Keep any private address in your note off the repository, and record how to find it again
if the router gives the box a new address. Leave the Green using automatic addresses; it has no screen to
recover a mistyped static address. A router that cannot reserve an address does not require changing the box's
network settings.

## First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3. The internal storage is not replaceable by you, so the off-box copy
is the whole recovery plan: a dead box becomes "buy another box (or use any spare computer), restore the off-box
copy during onboarding". Do one restore drill onto something else in the first month so you know it works and how
long it takes.

## Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.
