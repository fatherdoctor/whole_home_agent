# Your first automation, with the agent beside you

You can make one small thing yourself before the agent starts building for you. Once Home Assistant has at
least one device, the agent offers this lesson once, before its first build. It explains one step, waits while
you click, then checks what happened. A tablet or computer works. There is no quiz, and no YAML unless you ask.
You can pause or say skip; the agent records that answer in `house/docs/backlog.md` and keeps helping.

The normal interview and your limits still apply. Choose a small light or a plug with a harmless lamp attached,
not a heater, lock, alarm, garage door, message or speaker. The agent reads the devices you actually have and
asks what you would like. These are suggestions, not devices to buy:

| If it fits your devices and wishes | What it teaches |
|---|---|
| A lamp plug that turns on at a chosen time | A clock can start an automation; choose an off time too. |
| A light that comes on at sunset | A trigger can follow the sun rather than a fixed clock time. |
| A Guest mode toggle that changes one light's behavior | A helper stores your choice, and a condition checks it. |
| A Good night button for one safe light | A script gives a list of steps a name, and a dashboard can run it. |

Pick one, change it, or suggest your own. The agent adapts the steps to that choice and says which exact device
will change before you save anything. If you have no suitable safe device, leave the offer for later.

## 1. Write your own small board row first

In `house/docs/board.md`, write one row with the agent coaching: a new unique code, your plain name for the
lesson, lane `owner`, a small point estimate, status BACKLOG, a link and any decision still needed. Follow
`../templates/docs/board-format.md`; add its plain-name entry in `house/docs/card-names.tsv` too. If the board
has not been introduced, the agent explains the six columns and helps you start it from the template; do not
leave its sample work as real work. You type your row and choose its size. Before clicking to build, mark it
IN PROGRESS with the time. This can count toward `L2-own-row`; doing the lesson does not pass all of level 2.

Agree the intended behavior, a quick test and an undo. The following worked example uses one ordinary light:
turning on a new lesson toggle runs a script that turns the light on, but only when the light is off. The other
suggestions use the same pieces with a different trigger or condition.

## 2. Make a helper: a choice on the screen

A helper is a value you can change without touching a physical device. In **Settings > Devices & services >
Helpers > Create helper**, choose **Toggle** and give it a clear name, such as **Try the light**. Create it and
leave it off for now. Choose the actual helper from the list in later steps; do not copy an invented identifier.
For the Guest mode option, call it **Guest mode** and decide together what on should mean.

The agent explains each screen and waits for done. The [official toggle guide](https://www.home-assistant.io/integrations/input_boolean/)
shows the current screens. It stores on or off; it is not a real light switch.

## 3. Make a script: a named list of steps

Open **Settings > Automations & scenes > Scripts**, create a new script and add one action: turn on the exact
light you chose. Give the script a clear name such as **Lesson light on**, then save. The agent points out the
target before you confirm it; do not choose a whole area for this first try. For Good night, choose a safe light
off instead. You can add steps later, one at a time.

A script runs its steps when something calls it, including you pressing a dashboard button. An automation can
call the same script. The [official scripts guide](https://www.home-assistant.io/docs/script/)
shows how the steps run. Ask the agent to explain an unfamiliar action before selecting it.

## 4. Make an automation: when, only if, then do

Open **Settings > Automations & scenes > Automations > Create automation > Create new automation**. In the
visual editor, add these parts for the worked example:

- **When**: a state change of your new lesson helper from off to on. This is the **trigger**, the event that
  starts a run. Use the helper's actual entry, not the physical light.
- **And if**: your chosen light is off. This is the **condition**, a question checked when the trigger happens.
  If it is false, the automation stops. It does not wait for the light to become off.
- **Then do**: run your saved **Lesson light on** script. This is the **action**, what happens after the check.

Save with a name you recognize and check whether it is enabled. For a scheduled plug or sunset choice, the
agent substitutes that trigger, and uses the helper as an optional allow/skip condition. Do not silently add
an off time or other behavior you have not chosen. The [visual editor](https://www.home-assistant.io/docs/automation/editor/)
and [trigger guide](https://www.home-assistant.io/docs/automation/trigger/) explain these parts in the current UI.

## 5. Put your controls on a dashboard

Use a dashboard you already edit, or make a small practice dashboard. Keep the automatic Overview dashboard
as it is: taking control changes how it updates. In the dashboard's edit screen, add an **Entities** card with
your helper and script selected from the real entity list. The helper's row shows its state and lets you
change it; the script's row offers a run control. Save the card and leave edit mode. If the script row does not
offer a run control on your screen, use the card editor to add a button with a **Perform action** tap action
that runs that exact script; the agent walks the current screen rather than inventing a menu.

[Entities cards](https://www.home-assistant.io/dashboards/entities/) can show states and buttons, and
[dashboard actions](https://www.home-assistant.io/dashboards/actions/) define what a tap does. Check the target
before you tap: running the script bypasses the automation's condition.

## 6. You try it; the agent reads the result

The agent uses read access only: it may inspect the saved settings, states, last-run time and trace, but it
creates, edits, reloads and triggers nothing. If that access is missing, you read the screen back; the result
stays unverified until it can be checked. Neither path grants broader permissions.

1. You run the script once from the dashboard, and watch the chosen light. This checks the script and button.
2. For the worked example, you turn the light off, set the helper off, then turn the helper on. Watch the light
   turn on. This is a real trigger test. Leaving the helper on does not trigger it again.
3. Open the automation's trace together. Check that the helper change started it, the condition passed, and the
   saved script ran. The agent compares the read state and last-run time with what you saw physically.
4. With the light already on, you set the helper off and on again. The trace should stop at the false condition.
   That is the intended result. For other choices, the agent proposes an equally small test of the chosen event;
   a temporary near-future test time must be restored and recorded before calling a sunset schedule finished.

**Run actions** is not proof that a trigger or condition works. If something fails, say what you saw, check the
selected helper, target, enabled state and trace, then change one thing yourself and retry. A failed or unread
trace is reported as failed or not checked, not passed. Nothing sends a message or speaks for a lesson test.

## 7. Write down what you made, and its undo

You write a short dated CHANGELOG entry with the agent coaching, using `../templates/docs/CHANGELOG.md`: why,
your go, the new helper/script/automation/card, what each test actually showed, and undo. A useful first undo is:
disable the lesson automation, remove only its new dashboard card, and return the light to its previous state.
Disabling an automation does not stop a script it already started. An adapted lesson can start a script with a
delay through `script.turn_on`, and that script runs on its own. Read the automation's actions to find that exact
script. Open **Settings > Tools > Actions**, choose `script.turn_off`, select that script only, and select
**Perform action**. Do not stop other scripts. Then check the light again after the delay has passed. ([Scripts](https://www.home-assistant.io/integrations/script/#waiting-for-a-script-to-complete);
[Turn off script](https://www.home-assistant.io/actions/script.turn_off/).)
If you later delete the lesson script/helper, check that nothing else uses them first. Do not delete a preexisting
control or restore the whole house just to remove the lesson.

Put the lesson's code in the entry, link your board row to it, and record the outcome. Mark DONE only when the
chosen behavior and checks passed; otherwise use PARTIAL or BLOCKED with what remains. If you stopped early,
that is a valid stopping point. The record helps the next session resume rather than offer the lesson again.

## Next: let Alexa run your safe script

If your plugs already work in Home Assistant, you can reuse the script before migrating every other plug.
Follow [the voice guide's scene-script example](../install/voice-assistants.md#4-a-safe-scene-script-with-an-alexa-phrase) for Cloud exposure, a phrase, tests and undo.
Expose only the approved safe script; leave original Alexa plug entries alone on SHARE or KEEP.
Check the script's own actions and targets first: Alexa does not run the condition in your lesson automation.
The agent still explains while you sign in, save and speak the test phrase.

What you just learned: a **helper** keeps a choice, a **script** names some steps, an **automation** connects an
event and a check to those steps, and a **dashboard** puts the controls in reach. You built it. The agent starts
its normal build loop only after this lesson, or after you say skip, and still asks for your go on the next item.

*UI references checked on 2026-11-10; no live device was used to validate this lesson. The kit's board and
CHANGELOG formats above supply the record rules. If a menu differs, follow the current official page and your
screen rather than guessing.*
