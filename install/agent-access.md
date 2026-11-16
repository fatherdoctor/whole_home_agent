# Giving the agent access to the box

*Status: written (O4, 2026-10-14), after a fresh-agent dry run found the kit never said how an agent reads or changes
the box. From the official Home Assistant authentication, REST API and app documentation as of October 2026. Any
agent, any hardware. Re-check the official pages when a menu does not match. Section 0 (KIT-BASE, 2026-10-27) is
for an agent that already runs inside the box as an app: the first lab run walked an off-box agent through a
token it did not need.*

**For the agent:** walk the person through this after `network-and-backups-first.md`, one numbered step at a time.
You never see the token: the person puts it where your runtime reads it, and you check that it works by reading,
never by changing anything. Write what was chosen into `setup.agent_access` in `house/profile.yaml`.

## 0. If you already run inside the box (the app way in)

The tell is Step 0's: `SUPERVISOR_TOKEN` is set in your environment and `/homeassistant` is the box's
configuration folder. Those variables alone are not proof that this session is on the intended box.
After the owner confirms the endpoint in section 2, the box probe can report `via the Supervisor (inside an add-on)`: the app sets
`HA_URL=http://supervisor/core` and `HA_TOKEN` (the Supervisor's token) itself at each start, and the probe names
the path by where that address goes, not by which variable held it. Then sections 1 to 4 are not for you: do not
create an agent user, do not ask for a long-lived token, do not ask for `HA_URL` (it is already set). Say so in one
line ("I run inside the box; the owner-confirmed read check uses its existing access") and record section 5 with
`read: addon`, `deploy: addon` after that check passes. An agent on a computer or in a cloud session records
`read: api` only after the bound read check succeeds; having `HA_URL` and `HA_TOKEN` set does not skip section 2.

What your runtime's app already grants, and what it rewrites at start, is in `adapters/agents/<runtime>.md`,
"Access on the box"; the kit's own grants below are the same for every runtime. Install the secrets deny list
(`adapters/agents/<runtime>.md`, "The secrets deny list") before the agent's first read of the box: read-write on
`/homeassistant` includes `secrets.yaml` and `.storage/`.

**Be honest about the limit, whatever the runtime.** An agent inside an app reaches Home Assistant through the
Supervisor and can act on any entity. The owner's [optional guard rails](../templates/agent-guard-rails.md), such as
the lock line prohibiting locking or unlocking, are instructions to the agent, not access controls enforced by
Home Assistant. Check the runtime's own policy and standing instructions before promising a choice can be applied;
the template cannot loosen a rule enforced elsewhere. Say that to the person in one line (the "Done when" list asks
whether you did).

What still needs a decision (ask, write the answer into `house/profile.yaml` and the CHANGELOG):
- **Unattended runs on the box:** none until level 4 (`00-start-here/levels.md`); until then every run has the
  person in the session.
- **Which model for setup** (`AGENTS.md`, Step 0): the cheapest that follows a guide; the person changes it, you
  only say how.

## What the agent needs, and the three ways to give it

For a person editing YAML on Home Assistant OS, start with the File editor app; the Studio Code Server app is an
alternative when a richer editor is wanted. Other access methods below remain available by choice.

| Need | Best | Middle | Without any access |
|---|---|---|---|
| **Read** states, areas, devices, entities | the REST/WebSocket API with a token | the same | the person reads Settings pages back to you |
| **Deploy** files (`house/ha/` to the box's config folder) | copy over SSH | a Samba share mounted on the agent's computer | the person pastes into the File editor app |
| **Check and reload** | `ha core check`, then a reload action | the config check button (Settings > Tools > YAML) | the person presses it and reads you the result |

A house can start at "without any access" and move up later. Record the choice; Phase 2's loop changes shape with it
(below).

## 1. A user for the agent
1. **Settings > People > Users > Add user** (switch on Advanced mode in the person's profile if the Users tab is not
   shown). Display name: the agent's role (`Agent`), not a person's name.
2. **Administrator: off to start.** A non-administrator user can read every state and call actions (lights, scripts).
   Some reads the kit uses need an administrator: the configuration check, rendering templates through the API, and
   some registry lists. **Reading the error log and creating areas also need administrator access.** A
   non-admin error-log request can look like 404, and an area-creation request can say Unauthorized: neither means
   there are no errors or that the area was created. Have the owner read **Settings > System > Logs** or create
   the area in the UI. Turn administrator on only for an explicitly approved backlog item, record why in the
   CHANGELOG, and return to non-admin when that need ends; never escalate automatically.
   Set **Local network only / Local access only: on** for this user. API tokens do not use an authenticator
   challenge, so the agent user does not need MFA for API access; keep MFA on the human owner account. If a
   local-only user cannot be used from a cloud session, use an approved network path or person-reads instead of
   silently widening access.
3. **Be honest about the limit.** Home Assistant has no "lights and switches only" user. A token can do whatever its
   user can, including arming, unlocking and deleting. The owner's
   [optional guard rails](../templates/agent-guard-rails.md), such as the lock line prohibiting locking or
   unlocking, are instructions in the agent's brief, not access controls enforced by Home Assistant.
   For unattended runs, wrapper scripts the model cannot edit can enforce runtime limits
   (`principles/tier-2-support-agent.md`). Say this to the person in one line.

## 2. A token, kept out of the chat and the repository
1. The person logs in **as the agent's user** (a private browser window), opens **Profile > Security > Long-lived
   access tokens > Create token**, names it after the agent's computer, and copies it once.
2. They choose one private credential source: the existing runtime secret store / `HA_TOKEN` environment
   variable, or the file option below. Set `HA_URL` privately to the working endpoint (port 80 on the kit's
   new-install path; an older install may use port 8123). Use HTTPS for a remote endpoint. No credential or
   personal URL goes in chat, shell history, the repository or `house/profile.yaml`.
3. **Revoking it is the off switch.** The same Security page deletes it; tell the person where it is.

### File option on Linux
The standard name is **`~/.config/home-assistant/ha_token`**, outside the household and kit repositories.
The deny list in `templates/runtime/claude-code-settings.json` covers this location. Install the runtime's
deny list before using the file. The model never opens or prints it; only the shipped reader loads it.

The person creates the folder (`mkdir -p ~/.config/home-assistant`), then uses a private editor to paste the
one token into `ha_token` as a single line. They save it and run `chmod 600 ~/.config/home-assistant/ha_token`.
Do not use a command containing the token itself. The reader tries this file first. If it is absent, it tries
`HA_TOKEN`, then the app's Supervisor credential when running inside the box. `HA_TOKEN_FILE` can select the
private file explicitly; a missing or unsafe selected file stops the read instead of using an old token.

### Confirm the box before the first read
On a computer or in a cloud session, the owner opens the address privately and checks it is the right house.
Inside an app, they confirm they opened it from the right Home Assistant and that this repository belongs to it.
**Inside an app, this check is the owner's confirmation only: the internal address is the same on every box.**
Do not confirm an address just because the shell already has one.

After the owner confirms it, run this local command. It makes a short record of the address without connecting
or reading a token:
```sh
python3 templates/tools/ha_read.py --fingerprint-url
```
Copy only the resulting digest into `setup.agent_access.box_url_sha256` in `house/profile.yaml`, in quotes.
Keep the address itself out of the profile and chat. Check that the profile is readable:
```sh
python3 templates/tools/profile_check.py house/profile.yaml
```
A `valid_shape` answer says the file is readable, not that setup is done. If it cannot check the file, stop
and say so. The reader checks this record before loading a token. If the address or box changes, ask the
owner to confirm it again. The record cannot prove which physical box is behind a reused address.
Agent details and supported file formats are in `templates/tools/README.md`.

## 3. Check reading works (read only)
From the household repository root, use the shipped standard-library reader:
```sh
python3 templates/tools/ha_read.py --registry all
```
If the kit is kept in a separate folder, run its script by that path and supply `--root <household-repository>`;
the credential-file boundary is the household repository, not the kit's location. A pass is JSON status `ok`
and counts for areas, devices and entities. The CLI never prints registry contents. Its Python API
`RegistryReader` returns a selected registry in memory; only the three fixed list commands are accepted:
`config/area_registry/list`, `config/device_registry/list` and `config/entity_registry/list`.

The runtime probe separately checks the pinned `/api/` response and `/api/states` count. A refused token or
registry read is not a zero count or an empty registry; say unverified and use owner-read pages where needed.
Never enable administrator or write a registry just to make this read check pass. A persistent export remains
its own backlog item; this reader creates none.

## 4. A deploy path (when the first build needs one)
Choose one with the person; it is needed at the first Phase 2 item that changes a file, not before.
- **SSH (best).** Install the official **Terminal & SSH** app (**Settings > Apps > Install app**). In its
  configuration, add the agent computer's **public** key (a public key is not a secret; the private key never leaves
  that computer). Deploy is a copy of `house/ha/packages/` to `/config/packages/`, then `ha core check` in the same
  SSH session. The check must say the configuration is valid; a partial success is a failure.
- **Samba share.** The official **Samba share** app; the person mounts `config` on the agent's computer with the
  username and password they set in the app (kept in their password manager, never shown to you). Deploy is a file
  copy; the check is **Settings > Tools > YAML > Check configuration**, which the person presses and reads back.
- **Person pastes (no access).** You write the file in `house/ha/`; the person opens the **File editor** app, pastes
  it, and presses the check. Slow, safe, and fine for the first weeks.

Packages need one line in the box's `configuration.yaml`, added once, by the person or over the deploy path:
```yaml
homeassistant:
  packages: !include_dir_named packages
```
After a successful check, reload instead of restarting where you can (**Settings > Tools > YAML > Reload** for
automations, scripts, helpers and template entities; or the action `homeassistant.reload_all`). A restart is an
"ask first" action.

## 5. Record it
In `house/profile.yaml`:
```yaml
setup:
  agent_access:
    read: api            # api | addon | person-reads   (addon: section 0, the agent runs inside the box)
    deploy: null         # ssh | samba | addon | person-pastes | null until the first build
    admin: false         # true only after a backlog item needed it (and the CHANGELOG says which)
    box_url_sha256: "<owner-confirmed endpoint fingerprint>"  # no address or credential
```
Add a CHANGELOG entry: "Agent user and token created; read check passed; undo: delete the token (Profile >
Security) and the user."

## How Phase 2 changes with the choice
- **read: person-reads** - every plan lists the Settings pages you need read back, and every id is marked
  "(read back by the person)". Nothing is built on a guessed id.
- **deploy: person-pastes or samba** - the test step includes the person reading you the check's result verbatim.
- **No unattended runs** until `read: api` and a push guard exist (`templates/guard/`, `principles/budget-and-pacing.md`).

## Done when
- [ ] The agent has its own user, not the owner's login, and the person knows whether it is an administrator
      (inside the box, section 0: the person has heard, in one line, that the app can do anything on the box).
- [ ] The token is stored outside the chat and the repository, and the person knows where to revoke it
      (inside the box, section 0: no token was made; the off switch is stopping or uninstalling the app and
      signing the agent's account out, and the person knows the app's sign-in travels inside every backup: `adapters/agents/<runtime>.md`, "Access on the box").
- [ ] The target was confirmed before credential use, and the reader returned registry counts / the runtime
      probe returned `200` and a state count (or `read: person-reads` is recorded on purpose). Shape validation
      alone is not a read check; install the runtime deny list before using the credential file.
- [ ] `setup.agent_access` is written in `house/profile.yaml`.
