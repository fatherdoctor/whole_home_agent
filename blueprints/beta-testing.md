# Beta testing our integrations and apps

A beta tester runs a pre-release of an integration or app on their own Home Assistant before everyone else gets it,
and reports what goes wrong. This page sets up a tester's box: get the item, switch on its betas, and get one short
phone notice when a new version is ready.

Items today: [Codex for Home Assistant](https://github.com/fatherdoctor/ha_codex) (an app with its own
integration). To join,
open an issue in the item's repository and ask.

## What you need

- Home Assistant 2025.4 or later, with the Home Assistant Companion app on your phone.
- For an integration: the Marketplace **signed in to a GitHub account**. Without a sign-in you cannot add a
  custom repository, and the Marketplace never checks it for updates on its own. The Marketplace can add only a
  repository that account can read.

## 1. Add the item

**An integration.** Marketplace > three dots > **Custom repositories**. Paste the repository URL, choose the
category **Integration**, add it, then open the item and install it. Restart Home Assistant when asked.

**An app.** Settings > Apps > **App store** > three dots > **Repositories**. Paste the repository URL. An app
has no beta switch: its betas come from a separate beta repository URL (the item's README names it when it has one).
Add that URL instead of the stable one, not both.

## 2. Switch on betas (integrations)

Use one of these:

- On the item's page in the Marketplace, turn on the beta option.
- Settings > Entities, find the item's **Pre-release** switch (for example `switch.example_integration_pre_release`).
  It is created disabled: enable it, wait about 30 seconds, then turn it on. The automation below keeps it on.

With betas on, the Marketplace offers the newest pre-release while it is newer than the newest stable release, and
the newest stable release after that.

## 3. Get a notice when a new version is ready

Import the blueprint [`automation/beta_update_notice.yaml`](automation/beta_update_notice.yaml) (Settings >
Automations & scenes > Blueprints > Import blueprint, with its raw file URL), then create an automation from it:

| Input | What to put |
|---|---|
| Update entities | The update entity of each item, for example `update.example_integration`, and the app's update entity. |
| Notify action | Your phone's notify action, for example `notify.mobile_app_my_phone`. |
| Pre-release switches | The Pre-release switch of each integration, once enabled. Optional. |

The notice reads, for example, "Update ready: Example Integration" and "v1.0.0 -> v1.1.0-beta.1, pre-release.". Tapping it
opens the release page. A version with a beta marker (`-beta.1`, `b2`, `rc1`) is called a pre-release. A short
commit hash means the item has no releases yet, and the notice says "commit build". A newer notice for the same
item replaces the older one.

## When updates show up

| Where the item comes from | When your box sees a new version |
|---|---|
| A custom repository, signed in | At each restart and every 48 hours. **Update information** on the item's page checks at once. |
| The default Marketplace list | Within about 10 hours: up to 4 for the list to be rebuilt, then up to 6 on your box. A restart skips the wait on your box. |
| An app repository | When the Supervisor reloads its store (Settings > Apps > App store > three dots > **Check for updates** checks at once). |

## Reporting a problem

Open an issue in the item's repository. Say the version (from the notice), what you did, what you expected and what
happened. Attach the item's diagnostics download if it has one. Never paste tokens, passwords or your home's
address into an issue: anyone who can read the repository can read it.

## Leaving

Turn off the item's beta option or Pre-release switch, update to the newest stable version, and delete the
automation. For an app, remove the beta repository and add the stable one.
