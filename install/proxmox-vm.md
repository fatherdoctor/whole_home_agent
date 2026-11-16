# Installing on: a Proxmox VM (Home Assistant OS)

*Status: written (O3a, 2026-10-13). The image, the minimum resources and the UEFI / no-Secure-Boot / guest-agent
requirements come from the official Home Assistant "Alternative" installation page (KVM/Proxmox, `.qcow2`) as of
October 2026. The official page has no Proxmox click-through, so the Proxmox steps below follow Proxmox VE 8's own
interface; if a field name differs on your version, the requirement in bold is what matters.*

**For the agent:** ask first whether Proxmox is already installed and running other VMs. If not, installing
Proxmox itself is a separate job (its own installer ISO, its own documentation); do that first, or switch to
`mini-pc-bare-metal.md` if the person only wants Home Assistant on that machine. Never run a script from the
internet on the Proxmox host on the person's behalf. One step at a time; wait for "done".

## Why a VM
The VM is the hardware that makes the backup tiers fast (`adapters/hardware.md`): a snapshot before a risky change
rolls back in about a minute, a nightly image goes to a second disk, and a clone can be a staging copy of the
house. The costs: USB radios need passthrough, the guest cannot see the host's temperatures, and a paused VM pauses
the house's clock.

## Before you start
- A Proxmox VE host with free resources. **Minimum 2 vCPUs and 2 GB of RAM** for the VM (official minimum); 4 GB is
  a better start. 32 GB of disk is the image's default; 64 GB leaves room for the database and backups.
- The host on Ethernet with a bridge (normally `vmbr0`) to the home network.
- A shell on the host (the node's **Shell** button in the web interface).

## 1. Create the VM (Proxmox web interface, **Create VM**)
- **General:** a VM ID (write it down) and a name such as `haos`. Start at boot: on.
- **OS:** **Do not use any media.** Guest OS: Linux.
- **System:** Machine **q35**. BIOS **OVMF (UEFI)**. Add an EFI disk on your VM storage, and **untick "Pre-Enroll
  keys"** (pre-enrolled keys turn Secure Boot on, and Home Assistant OS does not boot with it). **Qemu Agent: on**
  (Home Assistant OS runs the guest agent, so Proxmox can shut it down cleanly and freeze it for snapshots).
- **Disks:** delete the default disk. The Home Assistant image becomes the disk in step 2.
- **CPU:** 2 cores; type **host** is fine on a single host.
- **Memory:** 4096 MB. Turn ballooning off if you want the VM's memory to stay put.
- **Network:** bridge `vmbr0`, model **VirtIO**.
- Finish, but **do not start** the VM.

## 2. Import the Home Assistant OS disk (host shell)
1. Copy the **KVM/Proxmox (.qcow2)** link from the official "Alternative" installation page. The file is named
   `haos_ova-<version>.qcow2.xz`.
2. On the host:
   ```sh
   cd /tmp
   wget <the link you copied>
   xz -d haos_ova-<version>.qcow2.xz
   qm disk import <vmid> haos_ova-<version>.qcow2 <storage>   # e.g. local-lvm; older versions: qm importdisk
   ```
3. In the VM's **Hardware**, the imported disk shows as **Unused Disk 0**. Edit it, attach it as **SCSI** (controller
   VirtIO SCSI single), tick **Discard** if your storage is an SSD, and **Add**.
4. **Resize** the disk if you want more than 32 GB (Hardware > the disk > Disk Action > Resize). Home Assistant OS
   grows into it on the next start.
5. **Options > Boot Order:** put the new SCSI disk first and enabled; untick the network boot entries.
6. Delete the downloaded files from `/tmp`.

## 3. First start
1. **Start** the VM and open its **Console**. After a minute or two the Home Assistant banner shows the VM's
   address.
2. The console stays at the EFI shell or "no bootable device": the disk is not first in the boot order, or Secure
   Boot is on (re-create the EFI disk without pre-enrolled keys).

## Onboarding
1. **Find a working name or address.** Try `http://homeassistant.local` on the home network, or use the address
   in the VM's console. Follow `network-and-backups-first.md` section 1; router changes are optional, with no as
   the default. If you choose a reservation, match the VM's own MAC address in **Hardware > Network Device**,
   rather than the host's adapter. A host reservation is a separate optional choice.
2. On your computer, open that name or `http://<address>` (port 80), using what worked in step 1. On this new-install
   path `:8123` redirects there; an older install may still use port 8123. Keep the address that opens it.
3. A **Preparing Home Assistant** page for several minutes is normal; the first start downloads the latest Home
   Assistant.
4. Choose **Create my smart home** (or restore a backup if you are moving an existing house; see
   `network-and-backups-first.md`).
5. Create the owner account (use a password manager), set the home location, time zone, units and currency.
6. Choose what to share with the project.
7. **Skip the discovered devices for now** unless one is essential (`principles/naming.md`).
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
if the router gives the box a new address. After a restore or clone, check that the saved name or address
still reaches this VM. Its console shows its current address; a new virtual MAC can mean the router gives the
box a new address. Check a reservation only if you chose one.

## First backup, and a copy off the box
Follow `network-and-backups-first.md` section 3 first: the built-in backup with an off-box copy is still the plan
for "the whole host is dead". Then add the tiers only a VM gets (`principles/backups-and-recovery.md`):
- **Snapshots without RAM** before risky changes (VM > Snapshots > Take Snapshot, "Include RAM" OFF). A snapshot
  with RAM pauses the VM, and a paused VM stalls every timed automation; timers fire late and missed
  time triggers are dropped. Delete old snapshots; they grow.
- **A nightly Proxmox backup** (Datacenter > Backup) of the VM in **snapshot** mode, never "suspend" or "stop", to
  a disk that is not the VM's own disk.
- **Later, a staging clone** on an isolated bridge, start at boot off, with every USB passthrough line removed
  before its first start: a restored house tries to talk to its radios and push notifications at once.

## USB radios
Pass a radio stick to the VM by its **vendor and device ID** (VM Hardware > Add > USB Device > Use USB Vendor/Device
ID), not by port, so it survives being moved to another port. Put the stick on a short USB extension cable away
from the host. See `adapters/radios/`. A clone of this VM must never be given the same stick.

## Things the house must never be able to do
If you later add a Proxmox integration to Home Assistant, it creates Start, Stop and Reset buttons for the VM the
house runs in; "Stop" pressed from inside the house is pulling its own plug. Give that integration a read-only (or
read-plus-snapshot) Proxmox user, disable the button entities, and never expose them to a voice assistant
(`adapters/hardware.md`, `principles/safety-and-security.md`).

## Community helper scripts
A popular community project offers a one-line script that does steps 1 and 2 for you. It is not part of the official
documentation. If the person wants it, read the script before running it on the host (it runs as root on the
machine that runs everything), and check its result against the bold requirements above.

## Next: Phase 1
When every box in `network-and-backups-first.md` "Done when" is ticked, go back to `AGENTS.md`.
