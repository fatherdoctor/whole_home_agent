# Installing on: a mini PC, bare metal (Home Assistant OS)

*Status: written (O3a, 2026-10-13), from the official Home Assistant "Generic x86-64" installation page as of
October 2026. If a menu name below does not match what you see, the official page wins; tell the agent so it can
note the change.*

**For the agent:** this guide ERASES the mini PC's drive. Before step 1, ask the person to confirm in words that
nothing on that computer needs keeping, and that the computer is dedicated to Home Assistant from now on. One step
at a time; wait for "done". If they want to run other things on the same machine, stop and switch to
`proxmox-vm.md`.

## Before you start
You need:
- **The mini PC.** Intel or AMD, 64-bit, able to boot in **UEFI** mode (almost anything from the last ten years).
  4 GB of RAM is enough to start; 8 GB leaves room. An SSD of 64 GB or more.
- **A drive that uses 512-byte sectors.** A few NVMe SSDs and hard disks use 4K-native sectors only ("4Kn"); Home
  Assistant OS cannot boot from those. Most drives are fine; if the drive's data sheet says 4Kn, use another.
- **A USB stick of 8 GB or more** (it is erased too) and another computer to prepare it on.
- **An Ethernet cable to the router.** The first start needs the internet: it downloads the latest Home Assistant.
- **A keyboard and a screen** for the setup (only during the install).

Why bare metal rather than a VM: simpler, nothing between Home Assistant and the hardware, and USB radios just
work. What you give up: no instant snapshots before risky changes (backup tiers T0-T2 are slower; see
`adapters/hardware.md`), and the machine runs nothing else.

## 1. Set the firmware (BIOS)
1. Start the mini PC and press the setup key repeatedly: usually **F2**, sometimes **Del**, **F1** or **F10**.
2. Make sure **UEFI** boot mode is enabled.
3. **Disable Secure Boot.** Home Assistant OS does not boot with it on.
4. While you are here, two settings worth having (names vary by maker):
   - **Restore on AC power loss: Power On** (sometimes "After power failure: On"), so the house comes back by
     itself after a power cut. Without it, every outage ends with someone pressing the power button.
   - Wake or fan settings you do not understand: leave them.
5. Save and exit.

## 2. Write Home Assistant OS to the internal drive
The official recommended method boots Ubuntu from the USB stick and writes the image from there. Home Assistant OS
has no installer of its own.

On your other computer:
1. Make an Ubuntu Desktop USB stick, following Ubuntu's own "try Ubuntu Desktop" instructions.

On the mini PC:
1. Plug in the USB stick, the Ethernet cable, keyboard and screen. Start it and pick the USB stick as the boot
   device (the boot menu key is often **F10** or **F12**, or change the boot order in the firmware).
2. When asked, choose **Try Ubuntu**, NOT "Install Ubuntu".
3. In Ubuntu, open a browser, go to the official Home Assistant "Generic x86-64" installation page and download the
   Home Assistant OS image it links (`haos_generic-x86-64-<version>.img.xz`).
4. Open **Show Applications**, search for **Disks**, and open it.
5. On the left, select the mini PC's INTERNAL drive (check the size and model; the USB stick is also listed).
6. From the **⋮** menu at the top, choose **Restore Disk Image...**, select the image you downloaded, then
   **Start Restoring...** and confirm **Restore**.
   - "Error unmounting filesystem ... target is busy": you are running Ubuntu from the internal disk instead of the
     stick. Restart and choose **Try Ubuntu** from the stick.
   - A "Swap" partition is listed on the target drive: select it, press the stop button to unmount it, and try
     again.
7. When it finishes, shut Ubuntu down and remove the USB stick when told to.

(The official page also has a second method: take the drive out, write the image with Balena Etcher on another
computer, and put it back. Use it if the mini PC cannot boot from USB.)

## 3. First start
1. With the USB stick removed and the Ethernet cable in, power on.
2. After a minute or so the Home Assistant banner appears on the screen with the box's address.
   - "No bootable device": the firmware needs an EFI boot entry pointing at `\EFI\BOOT\bootx64.efi` on the drive.
     The official page shows how, from the firmware's boot menu or with `efibootmgr` from the Ubuntu stick.

## Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network, or use the address
   on the box's screen. Follow `network-and-backups-first.md` section 1; router changes are optional, with no as
   the default. Reserve the address only if you choose that route.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. Bookmark the address that opens it.
3. A **Preparing Home Assistant** page for several minutes is normal.
4. Choose **Create my smart home** (or restore a backup if you are moving an existing house onto this box; see
   `network-and-backups-first.md`).
5. Create the owner account (use a password manager), set the home location, time zone, units and currency.
6. Choose what to share with the project.
7. **Skip the discovered devices for now** unless one is essential (`principles/naming.md`).
8. **Fresh installs only:** defer offered updates until `network-and-backups-first.md` section 3 has made
   a backup and a copy off the box; then follow section 4. A box already running instead follows that guide's
   **section 0: local backup and full update first**, before other changes. A fresh image already current
   needs no update.
9. Unplug the keyboard and screen.

**Jumping ahead:** If you choose [Jumping ahead](../00-start-here/from-a-chat-app.md#jumping-ahead),
you may update after making a local backup first and leave the off-box copy until later. A local backup
is lost with the box if the box or its storage is lost or fails.

## Network: a working name or address
The goal is to reach the box at a stable name or address. A reservation is optional. If you decline router
changes, record that choice and the tested access kind in the profile, as section 1 of
`network-and-backups-first.md` explains. Keep any private address in your note off the repository, and record how to find it again
if the router gives the box a new address. A static address on the box needs a separate choice and a recovery
plan; it is not the fallback for declining the router.

## First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3. On a mini PC, worth adding in the first months
(`principles/backups-and-recovery.md`):
- a **second internal drive or a network share** for a nightly copy, so a dead system drive is a reinstall plus a
  restore, not a rebuild;
- a **system monitor** for CPU temperature and disk use (`principles/health-checks.md`);
- a timed restore drill onto a spare machine or a VM.

## Radios
USB radio sticks go on a short USB **extension cable**, away from the PC and its USB 3 ports. See
`adapters/radios/`.

## Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.
