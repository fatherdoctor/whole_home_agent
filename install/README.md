# Install

*Status: written (O3a, 2026-10-13), from the official Home Assistant installation, onboarding and backup
documentation as of October 2026. Official pages win when they disagree with these guides; update the guide when
that happens.*

Pick the guide for your hardware. Every guide ends the same way: onboarded, updated, reachable at a stable name or
address, backed up, with a copy off the box (`network-and-backups-first.md`, "Done when"). Router changes are optional.

| Guide | For | Hands-on time | Backup tiers it allows |
|---|---|---|---|
| `ha-green.md` | The official ready-made box, Home Assistant Green | ~30 min | off-box copy only |
| `raspberry-pi.md` | Raspberry Pi 5 or 4, 2 GB RAM or more | ~1 h | off-box copy; a spare card |
| `mini-pc-bare-metal.md` | An Intel or AMD mini PC dedicated to Home Assistant | ~1-2 h | off-box copy; a second disk |
| `proxmox-vm.md` | A VM on a Proxmox host that may run other things | ~1-2 h, plus Proxmox itself | snapshots, nightly images, staging clones |

Then, for everyone: `network-and-backups-first.md`, which ends with `agent-access.md` (how the agent reads the box
and, at the first build, deploys to it).

On the kit's new-install path, open `http://<address>` (port 80); `:8123` redirects there. An older or customized
install may still use port 8123: keep the address that actually opens it. Try `http://homeassistant.local` first;
if it does not work, section 1 of `network-and-backups-first.md` walks the address options. A reservation is one
route. The owner's recorded choice to decline router changes and a tested name or current address is another.
**Back up and get a copy off the box before accepting offered updates**, then follow section 4 of that guide.

Not covered: Home Assistant Container or Core installs (no apps, formerly add-ons, and no built-in OS updates;
the official documentation covers them), and VirtualBox, VMware or Hyper-V (the official "Windows", "macOS",
"Linux" and "Alternative" pages have click-throughs; the requirements in `proxmox-vm.md` still apply: UEFI, Secure
Boot off, 2 vCPUs, 2 GB RAM or more).

**For the agent:** the person may be reading these guides for the first time. Go one numbered step at a time and
wait for "done". If what they see differs from the guide, believe their screen, check the official page, and say
which step changed so the guide can be updated after Phase 0.

Already use voice control? [Keep it working while adding Home Assistant](voice-assistants.md).
Need a YAML secret? [Enter and rotate it privately with the File editor app](secrets.md).
