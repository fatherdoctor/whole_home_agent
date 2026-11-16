# Screenshots needed

*Status: list (RD, 2026-10-16). Nothing here is captured yet. Rules: `docs/readme-style.md` "Screenshots" (light
theme, one window cropped to the subject, no personal data, alt text, GIFs under 2 MB). When a file exists, add its
image line to the README section named below; until then the README carries no image and no link for it.*

| File | What screen | State to show | README section |
|---|---|---|---|
| `blueprints-import.png` | Settings > Automations & scenes > Blueprints, the Import blueprint dialog | A gist URL pasted, preview showing the blueprint title | `blueprints/README.md` Installation |
| `battery-optimizer-inputs.png` | Create automation from Battery Optimizer, the five sections (Device, Ranges, Timing, Faults, Notifications) | Demo entities (`switch.demo_charger`, `sensor.demo_battery`) filled in, defaults visible | `blueprints/README.md` Preview (after Features) and Battery Optimizer |
| `charger-fault-notification.png` | A phone notification from the example action | A `not_charging` fault with its message; a second shot with the same tag replaced by the clear | `blueprints/README.md` The action |
| `battery-window-cycle.gif` | The battery history graph of the demo device over a few cycles with the plug state under it | Battery sawtooth between the floor and the ceiling | `blueprints/README.md` Preview |
| `usage-card-bars.png` | The assistant usage card, Linear bars view | Demo figures (week about 40 %, today under budget), the limit and pace marks, the two-week chart with a few days of history | `templates/README.md` Assistant usage card |
| `usage-card-numbers.png` | The same card, Numbers view | The same demo figures, a per-model row, "Read N min ago" | `templates/README.md` Assistant usage card |
| `usage-card-dials.png` | The same card, Tachometer view | The same demo figures; a second shot with the reader stopped, showing "Usage unknown" | `templates/README.md` Assistant usage card |

Capture on a demo instance (demo entities), not a real home.
