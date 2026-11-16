# Put secrets in Home Assistant without showing them to the agent

The goal is to let you enter and change private values while the agent works only with their names. Prefer an
integration's own setup screen when it offers one: you type the login or key into Home Assistant yourself.
The agent does not inspect the saved credentials or `.storage/`. Most integrations can be configured in the
UI, according to the [current configuration guide](https://www.home-assistant.io/docs/configuration/).

When YAML really needs a secret, use the **File editor app** on Home Assistant OS. It opens in your browser,
including on a tablet. The **Studio Code Server app** is the alternative if you want a richer browser editor and live
syntax checking; **Samba** is an option for editing from a computer. These are file editors, not a masked secret
form or password vault. Only you open the private file. For a box-side agent, install the runtime deny list
before its first read: it stops the agent's file tools from reading `secrets.yaml`; the agent must not bypass
that protection through a shell or script. The short
[research note](../docs/research/secrets-ui-2026-11-10.md) records what was and was not verified.

## 1. Open a private editor yourself

Use the [official OS file-access steps](https://www.home-assistant.io/common-tasks/os/#installing-and-using-the-file-editor-app):
if File editor is already installed, open **Settings > Apps > File editor**. Otherwise, open **Settings > Apps > Install app**,
choose **File editor**, and install it. Then choose **Start > Open Web UI**. Keep its default
access boundary to the configuration folder. The agent can explain the buttons, but pause screen sharing and
screenshots before opening a file with secrets. Never send the editor contents to the chat.

If the app is missing, check the installation type with the agent before proceeding. Home Assistant Container
has no apps; its owner needs a private editor for the mounted configuration folder. Do not follow OS app steps
by guessing a different installation or exposing a file share to the internet.

## 2. The agent writes the reference; you type the value

Agree on a plain key name that says what the value is for, such as `service_api_key`. It carries no value or
personal detail. The agent writes the ordinary configuration change with a reference:

```yaml
api_key: !secret service_api_key
```

The setting on the left must be one the integration actually supports; this is the shape of a reference, not a
complete integration configuration. The agent also writes this **key-only commented placeholder** in the work
note for you to copy, never by reading or editing an existing private file:

```yaml
# service_api_key:
```

You open `secrets.yaml` in the configuration folder using File editor's file browser. If it does not exist,
you create it there yourself. Check privately whether the key already exists; do not add a duplicate. Copy the
placeholder, remove the comment mark, and type or paste the value after its colon in the private editor. Save.
A comment alone does not define a secret; the placeholder must be filled before a configuration check can pass.

Keep the value on one line and quote it as YAML text, especially if it contains `#`, `:`, or starts with a number.
For a single-quoted value containing an apostrophe, type that apostrophe twice inside the quotes. If the syntax
is unclear, let the agent explain with invented ordinary text, never with your value. Do not send a screenshot
of the filled line. The [official secrets guide](https://www.home-assistant.io/docs/configuration/secrets/)
explains the reference and lookup rules; `!secret` separates values from configuration, it does not encrypt them.

The private file stays outside git and chat. Keep the runtime's deny list and push guard installed. Do not let
a shell command, an agent editor or a repository diff print its contents. Backups may contain credentials too;
keep them protected (`../principles/backups-and-recovery.md`, rule 6).

## 3. Check without reading the value

Close the secret file before showing the agent your screen again. You run **Settings > Tools > YAML > Check
configuration**, following the [current OS check instructions](https://www.home-assistant.io/common-tasks/os/#configuration-check).
If your version labels the page differently, use that official page rather than guessing. Report success or
the failing file, line and key only. Inspect any error privately first: an integration's error output may contain
values. Do not paste raw logs or a filled configuration line into the chat.

The agent records the reported result and its limits. A successful syntax/configuration check does not prove
the remote service accepted the credential. If it fails, fix the key name, location or syntax privately and
check again. Do not bypass a failed check. Apply through the integration's supported reload only after the
owner agrees; a restart is a separate explicit decision. Then you check the integration's normal status page
and report only whether it works. The agent neither sends a test message nor opens the value to diagnose it.

The [official secrets page](https://www.home-assistant.io/docs/configuration/secrets/) also warns that secrets
used in automations can appear in source and trace viewers. Do not put a secret directly in the UI YAML editor
for automations/scripts; that editor does not support `!secret`. Keep credential-bearing configuration in the
integration's supported location. Do not give the agent a trace that might reveal it.

## 4. Change or rotate one later

For a UI-configured integration, use its supported reconfigure/reauthenticate screen and enter the new value
yourself. For a YAML-backed key, open File editor privately, replace only that key's value, save, close it and
repeat the check and approved reload. Keep the same key name when its purpose is unchanged, so references need
no value-bearing edits. Follow the provider's own instructions for issuing and revoking a credential; the agent
can help locate those instructions without seeing the credential.

For a planned rotation, allow an overlap only if the provider supports it: issue the replacement, update it,
verify service access, then revoke the old one. If a value leaked into a transcript, screenshot or commit, treat
it as exposed: tell the owner by key only and revoke/replace it promptly. Do not wait for routine testing while
a known leaked credential remains usable, and do not reuse the old value as an undo.

Record the date, key name, service kind, what was checked and the recovery route in the CHANGELOG. Keep values,
account identifiers and provider recovery details in the owner's private records. A safe undo for a failed
rotation is another replacement or the provider's recovery route, not a copied old secret in git.

## 5. What belongs in the emergency kit

Keep the backup encryption key, authenticator setup/recovery material and instructions for reaching your
password manager somewhere you can reach if Home Assistant is down, never in this repository or only on the
box. Keep any required credentials in that private password manager or sealed offline record, not in the
agent's notes. The repository may name the key and record that recovery was checked, without the value or a
personal location. A password vault hosted only on the same failed box cannot be your only recovery copy.
See `network-and-backups-first.md` for backup and authenticator recovery.

*Checked against the linked official documentation on 2026-11-10. This guide was validated as documentation;
no real secret file was opened and no live configuration check or rotation was performed.*
