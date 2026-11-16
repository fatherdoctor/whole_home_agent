# Hardware

*Status: notes (O1). Templates: `templates/`; install: `install/`.*

Pi vs HA Green vs mini PC vs VM. The principles that change shape with the hardware are change control, backups
and testing; everything else is the same on every box.

| | Raspberry Pi / HA Green | Mini PC, bare metal (HAOS) | VM on a hypervisor (Proxmox) |
|---|---|---|---|
| **T0 experiment rollback** | git + built-in backup (~30 min) | git + built-in backup | CLI snapshot, no RAM (~1 min) |
| **T1 bad update** | built-in backup before update | built-in backup before update | snapshot, then update |
| **T2 disk dies** | the card IS the likely failure: T3 is the plan | reinstall the OS, restore T3 | nightly image to a second disk (~1 h) |
| **T3 box dies** | off-box copy of the built-in backup; the whole plan | off-box copy | off-box copy |
| **Staging clone** | a second card or box restored from backup on an isolated VLAN | a second box or a VM elsewhere | a clone on an isolated bridge, start-at-boot off, USB lines deleted before first boot |
| **Rollback of record** | the previous card | a second disk + boot order | the snapshot |
| **Radios** | USB sticks on an extension; a re-plug needs an integration reload | same | USB passthrough; the clone must never see the sticks |
| **Host health** | CPU temperature and throttling are visible | thermals visible | a guest cannot read host thermals or the BIOS "restore on AC loss" setting; add a hypervisor read-only integration for the host |
| **Updates** | the OS update is the riskiest step: a second card or box restored from backup first (`principles/updates.md`) | built-in backup plus the second-disk image first | snapshot, then update; host updates: wait a week, forum check for a new kernel, house VM backed up to a separate disk, a watched window, the flag before each reboot (`principles/updates.md` rule 11) |
| **Clock** | - | - | a VM pause stalls every timed trigger: a clock-jump sensor and a safe-moment reload |
| **Tier-2 agent** | app model works (Supervisor); "reboot VM" becomes "reboot host" with no snapshot first | same | the hypervisor token is read-plus-snapshot only; stop/reset stays with a person |

## How this goes wrong

- A paused VM runs its timers late and drops the time triggers it missed; a GUI snapshot "with RAM" is the same
  hazard.
- The hypervisor integration creates Start/Stop/Reset buttons for the VM that runs the house; "Stop" from inside
  the house is pulling your own plug. Disable every button entity, never expose them to a voice assistant, and use
  an audit-only token so they fail anyway.
- A restored house tries to push the moment it boots. The clone's isolation probe must fail to connect.
- An integration pinned to an IP address dies when the DHCP lease moves. Reserve addresses for anything pinned by IP.
- A host update taken the day it appears, or started right before bed. The host runs the whole house; follow
  `principles/updates.md` rule 11, and keep the previous kernel as the fallback boot entry.
- A host-side resize or restore that names the wrong VM id. Read the id back from the host's own list before any
  command that takes one.
- The house's hypervisor token cannot list the host's pending packages without a broader privilege. Keep the
  token narrow; a person, or a read-only host-side job that writes the list to a file, supplies it.
