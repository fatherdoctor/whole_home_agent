# Adapters

*Status: notes written (O1, 2026-10-11); O3b adds the detailed setup per choice.*

What changes per choice. The principles never change; an adapter says which rules need a different mechanism and
which failure modes are specific to one choice. Each note has three parts: **what is different**, **what the
principles need from it** (the mechanisms a rule assumes), and **how this goes wrong** with that choice where
there is anything specific. Choices not tested in practice are marked as such and carry general guidance only.

- `radios/zigbee.md` - ZHA vs Zigbee2MQTT, coordinators, mesh health, not-monitored devices.
- `radios/zwave.md` - Controllers, Long Range, firmware cautions, radio noise as a failure mode.
- `radios/matter-thread.md` - Border routers, fabrics, what changes vs Zigbee.
- `radios/wifi.md` - ESPHome and Wi-Fi devices, reconnects, signal.
- `voice/alexa.md` - Exposure policy, attribution of voice commands.
- `voice/google.md` - Exposure policy.
- `voice/apple.md` - HomeKit bridge, Siri.
- `voice/assist.md` - Local voice, satellites, conversation agents.
- `notifications/companion-app.md` - Tags, actions, tap targets, critical alerts.
- `notifications/pushover.md`
- `notifications/telegram.md`
- `notifications/sms.md` - Consent, costs, never send to verify.
- `agents/claude-code.md` - Settings, permissions, memory, routines.
- `agents/other-agents.md` - What the kit needs from any agent.
- `kiosk-wall-panel.md` - Wall panel watchdog: an on-device supervisor, a heartbeat webhook, a read-only view, the
  on-battery watch and how it pairs with the Battery Optimizer blueprint.
- `hardware.md` - Pi vs HA Green vs mini PC vs VM: storage, backups, staging, radios on USB.
