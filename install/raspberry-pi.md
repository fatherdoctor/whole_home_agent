# Installing on: Raspberry Pi

*Status: written (O3a, 2026-10-13), from the official Home Assistant Raspberry Pi installation page as of October
2026. If a menu name below does not match what you see, the official page wins; tell the agent so it can note the
change.*

**For the agent:** one step at a time; wait for "done". Ask which Pi model and how much RAM before step 1. Never
suggest a phone charger or a computer's USB port as the power supply.

## Before you start
You need:
- **A Raspberry Pi 5 or Raspberry Pi 4 with at least 2 GB of RAM** (4 GB or more leaves room for apps). Older
  models are not covered by the official guide.
- **The official power supply for that model** (the Pi 5 one is 27 W). Phone chargers and computer USB ports
  cannot supply enough power, and an underpowered Pi corrupts its card in ways that look like software bugs.
- **A microSD card of 32 GB or more, labeled A2** (Application Class 2: faster at the small reads and writes
  Home Assistant does all day). A known brand; counterfeit cards are common. If you boot from an SSD, the card
  is still handy as a spare.
- **A card reader** on the computer you will write the card from.
- **An Ethernet cable to the router.** Required for the install; Wi-Fi can be set up later, but wired is more
  reliable and recommended for good.
- A case with some airflow. A Pi that throttles from heat slows everything down.

**Parts for a Pi 5 booting from NVMe** (the setup this kit recommends for a Pi): the Pi 5 (4 GB or more), the
27 W official supply, an M.2 HAT for the Pi 5, an NVMe drive in a length the HAT holds (most take 2230 and
2242; check the HAT's page before buying a 2280), the active cooler or a fan case, and a case made to fit the
board with the HAT on it (many Pi 5 cases do not). Default: use a USB enclosure compatible with the drive to write
the image from the other computer. Keep a microSD card as a spare; the card-first alternative below needs additional
Pi desktop equipment.

**About the card.** On a Pi the card is the most likely part to fail (see `adapters/hardware.md`): it wears out
from constant small writes. Plan for that from day one: the off-box backup in `network-and-backups-first.md` is
your whole recovery plan, and a spare card in a drawer turns a dead card into a 45-minute restore. Booting from an
SSD (USB, or an NVMe board on a Pi 5) avoids most card wear: see "Booting from an SSD" below.

## Install
On your computer:
1. Download and install **Raspberry Pi Imager** from raspberrypi.com/software.
   - If Imager does not run on your computer, download the Home Assistant OS image for your model (`haos_rpi5-64`
     or `haos_rpi4-64`, `.img.xz`, from the Home Assistant OS releases page on GitHub) and write it with
     another imaging tool such as Balena Etcher.
2. Open Imager and select **OS**.
3. Select **Other specific-purpose OS > Home automation > Home Assistant**.
4. Choose the Home Assistant OS build for your model (RPi 4 or RPi 5). They are different images.
5. Insert the card. Choose it as the storage. **Everything on the card is erased**; check you picked the card and not
   another drive.
6. Select **Next**, then **Write**, and wait for writing and verifying to finish.
7. Select **Finish** and eject the card.

### Booting from an SSD (NVMe on a Pi 5, or USB)
The steps above write a card; an SSD takes the same image. Two ways, the official pages win if they differ:
- **Write the drive directly.** Put the drive in a USB enclosure, plug it into the computer, and in Imager choose it
  as the storage (step 5). Then fit it to the Pi (NVMe: into the board, with the Pi off) and boot with no card.
- **Through a card first.** Without an enclosure, this needs a monitor, keyboard, mouse and suitable display cable,
  plus a Raspberry Pi OS desktop on the card and a working network connection. Follow the official Raspberry Pi
  first-time desktop setup, then run Raspberry Pi Imager on that desktop to write Home Assistant OS to the NVMe.
  Check the selected destination before writing; shut down and remove the card before booting the NVMe. If those
  peripherals or a documented remote desktop route are unavailable, use an enclosure or stop until they are ready.
If the Pi does not boot from the drive with no card in, connect a screen: it shows the bootloader's boot order. A
current Pi 5 bootloader tries NVMe; an older one may need the boot order changed with the official Raspberry Pi
tools (`rpi-eeprom-config`, or Imager's "Bootloader" image). Record `setup.storage: nvme` (or `ssd`).

On the Pi:
1. Put the card in the Pi (skip this with an SSD).
2. Plug the Ethernet cable into the Pi and the router (the same network as your computer, with internet).
3. Plug in the power supply. There is no power button; it starts.

## Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network. If it does not work,
   follow the no-router route in `network-and-backups-first.md` section 1; a connected HDMI screen can show the
   Pi's current address. Router changes are optional, with no as the default.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. On a Pi 4 or 5 the page
   should appear within a minute or two; the first start downloads the latest Home
   Assistant, so a "preparing" screen for several minutes is normal.
   - Nothing after 5 minutes: the card was probably not written correctly. Write it again, ideally with another
     card. Still nothing: connect a screen by HDMI and read the console.
3. On the welcome screen choose **Create my smart home** (or **Upload backup** / Home Assistant Cloud if you are
   moving an existing house onto this Pi; see `network-and-backups-first.md`).
4. Create the owner account. Use a password manager; the name shown is what the household sees.
5. Set the home location, time zone, units and currency. The location drives sunrise and sunset automations and
   the weather; a pin at the right house matters more than it seems.
6. Choose what to share with the Home Assistant project (your call; analytics are anonymous and help the
   developers).
7. The last screen lists devices it found on the network. **Skip them for now** unless one is essential; Phase 1
   names things on purpose (`principles/naming.md`) and renaming later is work.
8. **Fresh installs only:** defer offered updates until `network-and-backups-first.md` section 3 has made
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
if the router gives the box a new address. A static address needs a separate choice and a recovery plan, with
a screen and keyboard ready at the Pi. It is not the fallback for declining the router.

## First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3. For a Pi this is not optional: the card is the likely failure, and
an off-box copy plus a spare card is the plan for it.

Worth adding in the first month:
- a **spare card or SSD**, and one timed restore onto it (restore during onboarding);
- a **system monitor** for the Pi's CPU temperature and disk use, so heat and a filling card show up as health
  checks before they show up as failures (`principles/health-checks.md`).

## Radios
USB radio sticks (Zigbee, Z-Wave, Thread) go on a short USB **extension cable**, away from the Pi and its USB 3
ports, which interfere with 2.4 GHz radios. See `adapters/radios/`.

## Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.
