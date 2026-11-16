# Getting the kit, and making it yours

*Status: written (KIT-START0, 2026-10-27); the KIT-START0r findings enacted (KIT-START0.f, 2026-10-28); plain words
and the git identity (KIT-DRY.f6, 2026-11-10). For the person, both ways in. Two separate things: how the agent
reads the kit (once, read-only), and your own private repository, where your house's files will live.*

## 1. How the kit reaches the agent

The agent asks this before it fetches anything, and offers the three ways below. Whichever you pick, **a token is
never typed into the chat.** A chat is a transcript that gets saved, searched and backed up; a token in it is a
token on disk. The agent gives you the exact line to type at the shell prompt, outside the chat, and you type it
there.

**Which one is yours:**

- the kit is public: **(a)**;
- the kit is private and owned by an organization you belong to, or it is your own copy: **(b)**;
- the kit is private and a person shared it with you (you were added to a repository that someone else owns): **(c)**.
  A token of the kind in (b) cannot reach that kit, however it was shared; (c) can.

**(a) The public address.** If the kit is public, give the agent its address and there is nothing to sign in to.

**(b) A private repository and a read-only token.** A fine-grained token reaches only repositories owned by the
account you name as its *resource owner*: yourself, or an organization you are a member of. GitHub lists working in
a repository where you are a collaborator among the things these tokens cannot do (docs.github.com, "Fine-grained
personal access tokens limitations"), so a kit that another person owns will not appear in the picker below; for
that kit take (c). For a kit owned by an organization you belong to, or your own copy, you need a token that can
read that one repository and nothing else. On GitHub:

1. Your profile photo (top right) > **Settings** > **Developer settings** (bottom of the left column) > **Personal
   access tokens** > **Fine-grained tokens** > **Generate new token**.
2. Name it so you know what it is later ("starter kit, read-only, the box"). An expiration of 30 days is right: the
   kit is fetched once, and a later update can have a new token.
3. **Resource owner:** the organization that owns the kit (or you, for your own copy). **Repository access: Only
   select repositories**, and pick the kit. Not "all repositories". If the kit is not in that list, it is owned by
   someone else: stop here and take (c).
4. **Permissions > Repository permissions > Contents: Read-only.** That is the only one you set; "Metadata:
   Read-only" is added by itself and is fine. Nothing else.
5. Generate it and copy it once. GitHub shows it only this once.

Then the agent gives you a line to type at the shell prompt. In the app, that means leaving the chat for a moment
(`/exit`), typing the line, then coming back the way your runtime resumes a conversation (`adapters/agents/<runtime>.md`,
"Resuming a session") to pick it up where it was: a fresh start remembers nothing of this one. Before it sends you
out, the agent writes where it is (the kit's address, the way in you chose, the step that comes next) to
`/share/kit-setup-note.md`; if the chat comes back blank anyway, say "read `/share/kit-setup-note.md` and continue".
On a computer, a second terminal window, and the chat stays open. git asks for a username (your GitHub name) and a
password: the password is the token. **Default: not kept.** git saves nothing unless it is told to, and the agent
does not tell it to: the kit is fetched once, so the token is typed once. If something on the machine keeps it
anyway, the agent says so and where. **Where it lives afterward, and how to turn it off:** the token is good for
that one repository, read-only, until its expiration date; the same GitHub page lists it, and **Delete** revokes it
at once. Do that as soon as the kit is in your own repository (part 2 below).

**(c) The files reach the box, or the computer, some other way: a zip, or a deploy key.** This is the way for a kit
a person shared with you, and the simplest way in any case. Download the kit as a zip (on its GitHub page: the green
**Code** button > **Download ZIP**, from your own signed-in browser, which can see a repository shared with you where
a token cannot) and put it where the agent can read it. On the box: the `share` folder, through the **Samba share**
app. The **File editor** app stays inside the configuration folder unless its `enforce_basepath` option is
turned off (which widens what it can touch, so leave it on): with File editor, upload the zip into the configuration
folder and tell the agent, which moves it to `share`. On a computer: any folder. Tell the agent the path. A zip is
fine; it unpacks it.

Two other honest ways for a shared kit: the owner sends you the zip; or, for a box that should pull the kit's updates
later, the owner adds a read-only **deploy key** for it. The agent makes a key pair on the box in a file outside the
repository and names the file; you send the owner the public half (one line; it opens nothing by itself), and the
owner adds it under the kit's **Settings** > **Deploy keys**, leaving "Allow write access" off. A deploy key reads
one repository, has no expiration date, and the owner can delete it any day; delete it yourself the day you stop
needing it. **Never a classic token with the `repo` scope** for any of this: it opens every repository your account
can reach, and the person who shared the kit does not need that of you.

## 2. Your own private repository

Your house's files, the profile, the changelog, the rules, are yours and describe your home. They never go into the
kit's repository, and they go nowhere public. So the kit is copied into a private repository that you own, and
every session works in that copy. The agent does the copying; you make the empty repository and sign in once.

**In plain words.** A *repository* is a folder that remembers every saved version of its files, so any change can
be looked at or undone later. Each saved version (a *commit*) carries a label: a one-line note of what changed and
the name and email of who saved it, kept in the repository's history, where anyone who can open the repository
sees it (for a private one, you and whoever you add).

1. **An account at a git host.** GitHub is the one these steps name; the agent knows the others (GitLab, Gitea, or
   a bare repository on a computer you own). Turn on two-factor sign-in for the account.
2. **A new, empty, private repository.** On GitHub: the **+** (top right) > **New repository**. Name it after the
   house in a way that says nothing about where it is ("our-house", "the-house"), not after the street. Visibility:
   **Private**. Add nothing (no README, no .gitignore, no license). **Create repository.** Leave the page open: its
   address is what the agent needs next.
3. **The agent fills it.** It unpacks the kit into a folder named after your repository, makes that folder a git
   repository, points it at your new one, and pushes. git asks you to sign in once, at the shell prompt as in part
   1: username, and as the password a token for *your* repository with **Contents: Read and write** (a second token,
   made the same way, with you as the resource owner; the kit's read-only one does not open yours). Its expiration:
   the longest you are comfortable with (a year is a fair default; GitHub allows "no expiration" too). A token that
   expires turns the box's pushes into failures with nobody at the keyboard, so the agent writes the expiration date
   where the house keeps renewals: the maintenance calendar (`principles/maintenance-calendar.md`, a reminder 30
   days ahead), or, until there is one, a dated line at the top of `house/docs/backlog.md`.
   - **The label's name and email, before the first save.** A fresh copy has none, and git refuses to save
     without them. The agent sets them for this repository only, never for the whole computer or box:
     `git config user.name "<a role, such as house owner, or a first name>"` and
     `git config user.email "<an email>"`. For the email, GitHub gives you a private one: **Settings** > **Emails**
     > **Keep my email addresses private** shows an address ending in `@users.noreply.github.com`; use that. Each
     commit the agent makes also carries a second line naming the agent as co-author.
   - **On the box, the sign-in is kept (the default).** The box pushes your changes from now on, so the sign-in has
     to survive app restarts and updates, and the app's container keeps nothing between them except its own
     folder. The agent keeps it in one named file outside the repository, `/homeassistant/.claudecode/git-credentials`
     (beside the app's own sign-in), and points your repository's git settings at that file, so it is there after
     every restart. The file is inside the box's backups: one more reason a backup file is a secret. Say "do not keep
     it" and git asks at every push instead.
   - **On a computer, the sign-in is kept (the default)** in the computer's own password store, where git on
     Windows and macOS puts passwords by itself; on a computer whose git asks every time, the agent can set up the
     same kind of named file. Say "do not keep it" to be asked at every push.
   - **Where the folder lives on the box:** `/share/<repository name>`. The `share` folder is on the box's own disk,
     survives restarts and app updates, and is inside the box's backups. Not the Home Assistant configuration
     folder itself (`/homeassistant`): that is the live house, and your repository mirrors it rather than being it.
     **From then on, start every session with `cd /share/<repository name>` and then your runtime's start command
     (`adapters/agents/<runtime>.md`, "Resuming a session"):** the app opens in the configuration folder unless told
     otherwise, and there it finds neither `AGENTS.md` nor your notes. The one-time alternative is the app's
     working-directory setting set to `/share/<repository name>`; `adapters/agents/<runtime>.md`, "Access on the box", lists
     that as a choice to record.
   - **On a computer:** a folder you will not move or rename.
4. **Check.** Your repository's page shows the kit's files and the word **Private** beside its name. The kit's
   own repository shows no change (it never will; the agent cannot push there).

The kit stays reachable as a second remote named `kit`, read-only, so a later session can pull in the kit's updates
as a backlog item. Nothing of yours ever goes the other way.

If the kit is public and marked as a template, GitHub's **Use this template** button on its page does steps 2 and
3 in one click (pick **Private**); the agent then clones the result. Either way ends in the same place.

## What the agent never does here

Takes a token in the chat, or quotes one back. Signs in to a git host with your account on its own. Puts the kit,
or your files, anywhere public. Writes into the Home Assistant configuration folder as a place to keep your
repository. Asks for a classic token, or for any token that reaches more than the one repository it is for.
