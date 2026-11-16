# Wall panel watchdog (an Android tablet running a kiosk app)

*Status: written (H1-3, 2026-10-27). A how-to page, not code: the YAML below is a pattern to adapt, not a package to
install. Pairs with the [charger blueprints](../blueprints/README.md). Tested in practice on one real install (an
Android tablet running Fully Kiosk Browser, supervised by Automate); other kiosk apps and supervisors: general
guidance only.*

A wall panel fails in a way nothing in Home Assistant can repair: the kiosk app's screen goes away (a crash, a stray
Home press, an update), the launcher sits on the wall, and every remote path into the app is dead at that moment.
The fix has two halves. A small **supervisor on the tablet** brings the kiosk app back and sends Home Assistant a
**heartbeat**; Home Assistant **watches the heartbeat**, so the supervisor's own death is noticed too. A watchdog
nobody watches is the same bug one level up.

If the panel lives on a smart plug that cycles its battery, a third piece matters: **while the plug is off, the
panel is on its own**. An **on-battery watch** turns the charger back on the moment anything looks wrong, so a
wounded panel never runs flat.

- [What is different](#what-is-different)
- [What the principles need from it](#what-the-principles-need-from-it)
- [1. The supervisor on the tablet](#1-the-supervisor-on-the-tablet)
- [2. The heartbeat webhook](#2-the-heartbeat-webhook)
- [3. A read-only view of the heartbeat](#3-a-read-only-view-of-the-heartbeat)
- [4. The on-battery watch](#4-the-on-battery-watch)
- [5. With the Battery Optimizer blueprint](#5-with-the-battery-optimizer-blueprint)
- [6. Tests](#6-tests)
- [How this goes wrong](#how-this-goes-wrong)

## What is different

- The kiosk app is both the screen and Home Assistant's only window into the tablet (battery, screen, foreground
  app all come through the app's own integration). When the app is wounded, the tablet looks `unavailable` even
  though it is fine. The heartbeat is the one signal that does not pass through the kiosk app, so it tells the two
  apart: **heartbeat alive + app unavailable** = the app needs a restart; **both silent** = the tablet is gone
  (power, Wi-Fi).
- The usual kiosk app cannot restart itself into the foreground once its main screen is gone, and Android's own
  "restart on crash" does not bring the screen back. Something else on the device has to start it again: an
  automation app (Automate, Tasker, MacroDroid) running as a foreground service and exempt from battery
  optimization.
- A tablet on a cycling charger spends hours on battery. A failure in those hours drains it; a failure on mains
  power only looks bad.

## What the principles need from it

- **Health** ([`principles/health-checks.md`](../principles/health-checks.md)). One fault for a silent heartbeat
  (three missed beats: 15 minutes at a 5-minute beat). The restart count is on a dashboard, so a supervisor that
  is busy recovering every hour is seen before it fails. The panel gets a planned-restart flag, so a restart you
  do on purpose never pages.
- **Notifications** ([`principles/notifications-and-tiers.md`](../principles/notifications-and-tiers.md)). One
  cause, one warning: if an offline alert already reports "the kiosk app is unreachable", the on-battery watch
  turns the charger on for it but does not push it again. It pushes what nothing else reports: a stale heartbeat,
  another app in front, a battery under the floor.
- **Dashboards** ([`principles/dashboards.md`](../principles/dashboards.md)). Status rows read template sensors,
  never the helpers themselves: a helper renders as a date picker or a text box, and one tap overwrites the
  watchdog's own record.
- **Safety and security.** A webhook needs no token, so the heartbeat path holds no secret; keep it
  `local_only: true` and give it an id nobody would guess. The one token the supervisor may hold (to read the
  stand-down switch, below) and the kiosk app's remote-admin password live on the tablet only, outside the flow
  (section 1), and are never written to your repository. The token belongs to a dedicated non-admin user, so
  revoking it costs nothing if it ever leaks.

## 1. The supervisor on the tablet

The shape, in any automation app that can check the foreground app, make an HTTP request and start an app. Three
loops, all running at once:

| Loop | Every | Checks | Acts after | Does |
|---|---|---|---|---|
| A. Foreground | 30 s | the kiosk app is the foreground app (ask the OS, not the kiosk app) | 2 misses in a row (60 s) | start the kiosk app's main screen |
| B. Listener | 60 s | while the kiosk app *is* in front: its local API answers (for Fully, `http://127.0.0.1:2323/?cmd=deviceInfo&password=<its password, from a variable>`, 5 s timeout) | 3 failures in a row | the same restart |
| C. Heartbeat | 5 min | - | - | `POST` to the webhook (section 2) |

- **Recovery is one action:** start the kiosk app's main screen. Find the exact component name once with
  `adb shell cmd package resolve-activity --brief <package>` and test it with `adb shell am start -n <component>`
  while you have a cable in: a wrong activity name fails silently, and the supervisor then "recovers" every minute
  while nothing changes. Count each recovery and send the count in the heartbeat.
- **Stand down for maintenance.** Before each restart, read an `input_boolean` (here
  `input_boolean.wall_tablet_maintenance`) through the REST API; when it is on, log and skip. Without this the
  supervisor fights anyone who closes the kiosk app on purpose, including you in the supervisor's own editor.
- **The heartbeat body** is small JSON: `{"fg": "<foreground package>", "listener": true, "recoveries": 0}`. A fixed
  body is a fine first version; the webhook automation below accepts either.
- **Start on boot.** In Automate, resuming flows after a reboot is an app-wide setting (Settings, Safety, "Run on
  system startup"), not part of the flow, so it does not travel in an exported flow: tick it again by hand on every
  fresh install. Check the equivalent in other apps. A supervisor that dies at every reboot looks fine until the
  first power cut.
- Run the supervisor as a foreground service and confirm it is still exempt from battery optimization after an OS
  update. Free tiers can cap how many blocks run at once; three small loops fit, a fourth may not.
- **Keep the secrets out of the flow body.** The token (stand-down read) and the kiosk app's password (loop B) are
  read at start from the app's own variables or from a small file on the tablet the flow reads (Automate, Tasker
  and MacroDroid all have one), never typed into a block. An exported flow then carries neither.
- Build and export the flow on a phone (whose screen is not screwed to a wall), with the token and the password
  empty. Before you commit the export to your repository, search it for both (and for `Bearer`, `password=`); keep
  it there so it can be re-imported, and install it on the tablet over ADB.

## 2. The heartbeat webhook

Two helpers hold what the beat says: `input_datetime.wall_tablet_heartbeat` (date and time) and
`input_text.wall_tablet_watchdog` (max 255). Create them in the UI, and the automation in the UI's YAML view:

```yaml
alias: Wall tablet - watchdog heartbeat
description: Records each heartbeat from the supervisor on the wall tablet.
triggers:
  - trigger: webhook
    webhook_id: wall_tablet_heartbeat_<random suffix>
    allowed_methods: [POST]
    local_only: true
actions:
  - action: input_datetime.set_datetime
    target:
      entity_id: input_datetime.wall_tablet_heartbeat
    data:
      timestamp: "{{ now().timestamp() }}"
  - variables:
      body: "{{ trigger.json if trigger.json is defined and trigger.json is mapping else {} }}"
  - action: input_text.set_value
    target:
      entity_id: input_text.wall_tablet_watchdog
    data:
      value: >-
        fg={{ body.get('fg', 'unknown') }} listener={{ body.get('listener', 'unknown') | lower }}
        recoveries={{ body.get('recoveries', 0) }}
mode: queued
max: 10
```

The supervisor posts to `http://<home-assistant-address>:8123/api/webhook/wall_tablet_heartbeat_<random suffix>`
with content type `application/json`. Use the address the tablet can always reach (a reserved IP, per
[`install/network-and-backups-first.md`](../install/network-and-backups-first.md)), not a cloud URL.

## 3. A read-only view of the heartbeat

Template sensors give the dashboard and the health checks the same data with no controls on it. In
`configuration.yaml` or a package:

```yaml
template:
  - sensor:
      - name: Wall tablet watchdog
        unique_id: wall_tablet_watchdog_status
        icon: >-
          {% set hb = state_attr('input_datetime.wall_tablet_heartbeat', 'timestamp') | float(0) %}
          {{ 'mdi:heart-off-outline' if hb == 0 else 'mdi:heart-broken'
             if now().timestamp() - hb > 900 else 'mdi:heart-pulse' }}
        state: >-
          {% set hb = state_attr('input_datetime.wall_tablet_heartbeat', 'timestamp') | float(0) %}
          {% set age = ((now().timestamp() - hb) / 60) | round | int %}
          {{ 'Never seen' if hb == 0 else ('Silent ' ~ age ~ ' min') if age > 15 else 'Beating' }}

      - name: Wall tablet watchdog last heartbeat
        unique_id: wall_tablet_watchdog_last_heartbeat
        device_class: timestamp
        state: >-
          {% set hb = state_attr('input_datetime.wall_tablet_heartbeat', 'timestamp') | float(0) %}
          {{ (hb | as_datetime).isoformat() if hb > 0 else none }}

      - name: Wall tablet watchdog recoveries
        unique_id: wall_tablet_watchdog_recoveries
        icon: mdi:restart
        state: >-
          {% set s = states('input_text.wall_tablet_watchdog') %}
          {{ (s.split('recoveries=')[1].split(' ')[0] | int(0)) if 'recoveries=' in s else 0 }}

  - binary_sensor:
      - name: Wall tablet watchdog listener
        unique_id: wall_tablet_watchdog_listener
        device_class: running
        state: "{{ 'listener=true' in states('input_text.wall_tablet_watchdog') }}"
```

- Read the time from the `timestamp` attribute, never `as_timestamp(states('input_datetime...'))`: the state is
  local time without a zone, and the conversion can be off by your UTC offset.
- `sensor.wall_tablet_watchdog_recoveries` is the restart count the levels ask you to name (`H6-watchdog` in
  [`00-start-here/levels.md`](../00-start-here/levels.md)). Put it and the status row on the panel's health page.
- The **alert** is your health check, not these sensors: add "heartbeat older than 15 minutes" to the health sensor
  that already pages you (see `principles/health-checks.md`), with the panel's planned-restart flag as its
  suppression.

## 4. The on-battery watch

While the charger plug is off, check every 5 minutes (and on each change) that the panel is still there. Any check
failing turns the plug back on, then tells you. The checks, with the entities a kiosk app integration usually
provides (Fully's names shown; rename to yours):

| Check | Fails when | Why it matters on battery |
|---|---|---|
| Kiosk app reachable | `binary_sensor.wall_tablet_kiosk_mode` unavailable for 5 minutes | the app is wounded or the tablet is gone; either way, charge |
| Heartbeat fresh | older than 10 minutes (two missed beats at 5 minutes) | the supervisor stopped, so nothing will rescue the app |
| Kiosk app in front | `sensor.wall_tablet_foreground_app` is another package | the launcher or a dialog is on the wall, and the screen may never sleep |
| Battery above the floor | at or below the floor minus 5 | the window keeper did not switch the plug on at the floor |

One template sensor holds the reasons (fixed text, so its state changes only when a reason starts or ends; the
heartbeat's age is an attribute), so the watch, the dashboard and the Battery Optimizer (section 5) read the
same answer. Set `floor` to the keeper's floor. If you use a Heightened range, make the floor follow your *other*
Heightened reasons (the away mode, the guests), never `binary_sensor.wall_tablet_in_trouble` itself: section 5 makes
trouble a Heightened reason, so a floor that follows it would rise because of the trouble, add a "battery" reason of
its own and hold the trouble on until the battery charged past it. The example below has one such reason:

```yaml
template:
  - sensor:
      - name: Wall tablet trouble
        unique_id: wall_tablet_trouble
        icon: mdi:tablet-dashboard
        state: >-
          {% set heightened = is_state('alarm_control_panel.home_alarm', 'armed_away')
                or is_state('input_boolean.house_guests', 'on') %}
          {% set floor = 70 if heightened else 50 %}
          {% set app = states.binary_sensor.wall_tablet_kiosk_mode %}
          {% set fg = states('sensor.wall_tablet_foreground_app') %}
          {% set bat = states('sensor.wall_tablet_battery') | float(-1) %}
          {% set hb = state_attr('input_datetime.wall_tablet_heartbeat', 'timestamp') | float(0) %}
          {% set hb_age = (now().timestamp() - hb) | int %}
          {% set f = [] %}
          {% if app is none or (app.state in ['unavailable', 'unknown']
                and (now() - app.last_changed).total_seconds() >= 300) %}
            {% set f = f + ['kiosk app unreachable'] %}
          {% endif %}
          {% if hb == 0 %}{% set f = f + ['no heartbeat yet'] %}
          {% elif hb_age > 600 %}{% set f = f + ['heartbeat stale'] %}{% endif %}
          {% if fg not in ['de.ozerov.fully', 'unavailable', 'unknown'] %}
            {% set f = f + [fg ~ ' in front'] %}
          {% endif %}
          {% if 0 <= bat <= floor - 5 %}{% set f = f + ['battery ' ~ (bat | int) ~ '%'] %}{% endif %}
          {{ f | join(', ') if f else 'ok' }}
        attributes:
          heartbeat_age_min: >-
            {% set hb = state_attr('input_datetime.wall_tablet_heartbeat', 'timestamp') | float(0) %}
            {{ ((now().timestamp() - hb) // 60) | int if hb else none }}

  - binary_sensor:
      - name: Wall tablet in trouble
        unique_id: wall_tablet_in_trouble
        state: "{{ states('sensor.wall_tablet_trouble') not in ['ok', 'unknown', 'unavailable'] }}"
```

The watch itself (UI, YAML view). Replace the notify action with yours (the kit's notify script, or a
`notify.mobile_app_<phone>` call):

```yaml
alias: Wall tablet - on-battery watch
description: While the charger is off, turns it back on when the panel looks wrong, then tells the owner.
triggers:
  - trigger: time_pattern                 # the level: keep the plug on while the trouble lasts
    id: tick
    minutes: /5
  - trigger: state                        # the edge: the trouble starts
    id: trouble
    entity_id: binary_sensor.wall_tablet_in_trouble
    to: "on"
conditions:
  - condition: state
    entity_id: switch.wall_tablet_charger
    state: "off"
  - condition: state                      # a restart you do on purpose
    entity_id: input_boolean.wall_tablet_maintenance
    state: "off"
  - condition: state
    entity_id: binary_sensor.wall_tablet_in_trouble
    state: "on"
actions:
  - action: switch.turn_on
    target:
      entity_id: switch.wall_tablet_charger
  - variables:
      # One cause, one warning: drop 'kiosk app unreachable' here if an offline alert already reports it.
      push_reasons: >-
        {{ states('sensor.wall_tablet_trouble').split(', ')
           | reject('eq', 'kiosk app unreachable') | join(', ') }}
  - if:                                   # push on the edge only: a tick re-switches the plug quietly
      - condition: template
        value_template: "{{ trigger.id == 'trouble' and push_reasons | trim != '' }}"
    then:
      - action: notify.mobile_app_owner_phone
        data:
          title: Wall panel went quiet on battery
          message: "Wall panel problem on battery: {{ push_reasons }}. Charger switched back on."
          data:
            tag: wall_tablet_battery_watch
mode: single
max_exceeded: silent
```

- One push per trouble, not per check: the push goes out when the trouble starts with the plug off; a later tick
  that finds the plug off again (section 5) switches it on without a push.
- The 5-minute "unreachable" wait matches a 5-minute offline alert on purpose, so both act on the same minute and
  a blip shorter than that does neither.
- Fully reports its own package in front during normal use, and `unavailable` while it is restarting: neither
  counts. Another kiosk app: put its package in that list.
- A plug that shows up as a light: change `switch.` to `light.` in the condition and the action.
- No supervisor on the tablet yet: delete the two heartbeat lines from the trouble sensor, or it reads "no heartbeat
  yet" forever and the plug never turns off.

## 5. With the Battery Optimizer blueprint

The [Battery Optimizer](../blueprints/README.md#battery-optimizer) keeps the battery between a floor and a ceiling;
the watch turns the plug on when the panel is in trouble. Left alone they fight: the watch turns the plug on, the
optimizer's re-check sees the battery at the ceiling and turns it off, and five minutes later the watch turns it on
again. Give the optimizer the watch's answer instead:

- **Use the Heightened range while this is on:** `binary_sensor.wall_tablet_in_trouble` (or a template that is on
  when it or any of your other reasons holds, as in the blueprint README's example).
- **Heightened ceiling: 100.** On a tablet that never reports 100 % the plug then stays on until the trouble
  clears, which is what the watch wants (one that does: the bullet after next). When
  the panel is healthy again the Normal range comes back and the next re-check lets the battery cycle down.
- **Treat a silent battery as unreachable after: 120 min.** A kiosk app that stopped reporting leaves its last
  battery level standing; this holds the plug on even if the heartbeat check is not set up yet.
- **A tablet that does report 100 %.** The keeper switches the plug off at or above the ceiling, so at 100 it
  switches off while the trouble lasts, and the watch switches it back on at its next tick: one relay click per
  charge-up, no push. Where the device reports whole percents, a Heightened ceiling of 99 avoids even that.
- The optimizer's own charger faults (plug on and the battery not rising, and the rest) stay its job: the watch
  never reports them, and the optimizer never reports a stale heartbeat.

The plain window keeper has the same Heightened input and works the same way.

## 6. Tests

Run each once after setup and again after any change to the supervisor, with someone at the panel. Nothing here
sounds an alarm or needs a real alarm event.

| # | Test | Pass |
|---|---|---|
| 1 | Wait 5 minutes | the last-heartbeat sensor moves; the status reads Beating |
| 2 | Stop only the heartbeat loop | the health fault appears at about 15 minutes; restart the loop and it clears on the next beat |
| 3 | `adb shell am force-stop <kiosk package>` with the supervisor running | the dashboard is back within about 90 seconds with no hand on the glass; the recoveries count goes up by one |
| 4 | Turn the maintenance switch on, force-stop again | no recovery; switch off, and it recovers |
| 5 | Reboot the tablet, wait 3 minutes, force-stop | the supervisor resumed by itself and recovers; the heartbeat is back within 5 minutes of boot |
| 6 | With the plug off: stop the heartbeat loop | within 10-15 minutes the plug turns on and one push arrives; with the optimizer set as in section 5 the plug stays on until the loop is restarted |

Test 2 is the one that matters most: it is the first time the supervisor's own death is visible.

## How this goes wrong

- **The supervisor does not survive a reboot.** Its start-on-boot setting is per app and missed on a re-import; the
  panel then runs unsupervised and the first crash after the next power cut leaves the launcher on the wall. Test 5
  catches it; the heartbeat fault catches it in practice.
- **A wrong activity name.** `am start` on a component that does not exist returns quietly; the recovery count climbs
  and nothing comes back. Test the exact command once by hand.
- **No stand-down.** The supervisor restarts the kiosk app while you are changing its settings, or while an agent
  restarts it on purpose. Set the maintenance switch (and the panel's planned-restart flag) first.
- **Helpers on the dashboard.** A heartbeat time shown as an `input_datetime` row is a date picker; a tap rewrites it
  and the watchdog looks alive. Show the template sensors.
- **The watch and the keeper fight.** Without section 5 the charger flips every few minutes while the panel is in
  trouble at a high battery level: a relay click every few minutes and needless battery wear (the watch pushes
  only when the trouble starts).
- **Every reason pushed twice.** An offline alert and the on-battery watch both report "unreachable". Keep the
  reject in the watch, or drop the offline alert.
- **The tablet itself.** None of this covers lost power or Wi-Fi beyond telling you; the heartbeat going silent with
  the app also unavailable is the sign.
