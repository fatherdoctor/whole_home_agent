# Public README style

*Status: written (RD, 2026-10-16); targets added from the popular-README baseline (README-BASEr, 2026-11-08). The
shape every README in this kit, and in every repo meant to go public, follows. It is taken from the README of [Alarmo](https://github.com/fatherdoctor/ha_alarmo/blob/main/README.md),
which does this well: a reader finds what the thing is, installs it, and looks up any state, attribute, service
or event without reading prose.*

A README is a reference first and a story second. Write it so that someone who has never seen the project can
install it in five minutes and find any single fact in one scroll.

## The shape

Use these sections in this order. Leave out a section that does not apply (a blueprint has no Services); do not
reorder the rest.

1. **Title and badges.** `# Name`, then one badge row: Marketplace compatibility (the HACS validation badge uses
   `custom` until the repository is on the default list, then `default`), latest release, license, and the minimum Home Assistant version when there is one -
   four at most, nothing a reader does not act on (downloads, stars, sponsors). Badges are `img.shields.io`
   images with alt text.
2. **What it is.** One paragraph, plain words, no jargon: what it does and for whom. Say what it does not do
   (for example "it sends no notifications") in the same paragraph.
3. **Table of contents.** Only when the README runs past about 1,000 words (the shortest and most readable
   READMEs in the baseline have none): a linked list of the level-2 headings, plus the level-3 headings under
   Usage. Never every heading; a reader on a phone scrolls past a wall of links before the first fact.
4. **Introduction.** The parts the project consists of (an integration, a card, a blueprint), as a short list or
   a table with one line each.
   - **Features:** short bullets, one idea each, no marketing.
   - **Preview:** a screenshot right after Features (see "Screenshots").
5. **Installation.** Marketplace first (Settings > Marketplace > Add from link, the repository URL and type if
   requested), then manual (copy this folder to that folder, restart). A custom repository needs a GitHub connection;
   follow the screen and do not put its sign-in code in chat. End with the first
   setup step: adding the integration, importing the blueprint.
6. **Updating.** Through the Marketplace or manually. Say what a restart does and what survives it.
7. **Uninstalling.** Remove the configuration first, then the files; name anything left behind (helpers,
   stored data, automations that referenced it).
8. **Usage.** The reference, in this order as applicable:
   - **Configuration:** every option, as a table (name, default, notes).
   - **The entity (or each entity):** a **States** table, an **Attributes** table, a **Commands** table.
   - **Services:** one heading per service (`#### domain.service`, under `### Services`), a field table, then a YAML example that can
     be pasted into the automation editor.
   - **Events:** one heading per event, when it fires, an example payload.
   - **Automations:** copy-paste examples for the common jobs (a notification, switching a device).
8a. **Versions.** A table after Usage when behavior changed between releases: version, what changed, whether a
    default changed.
9. **Third party platforms.** Only if the project is exposed to others (Apple Home, Google Home, MQTT).
10. **Making contributions.** How to report a problem (what to include), how to propose a change, how to run
    the tests.
11. **License.** One line and the file name.

**Forks.** A fork's README is upstream's file plus a fork block at the top (60 words or fewer: fork of what,
license, what it adds, how to install the fork if that is intended, where upstream is watched); nothing else in
the file is edited.

## Targets

Measured against the 15 most-starred HACS READMEs (`docs/reference/readme-baseline.md` in the install this kit
comes from, 2026-11-06: median about 3,000 words, about 120 words before the first install step, 8 images,
9 badge URLs; the three most readable run 80-840 words and push the long reference to a docs page). A review
of one of our READMEs checks these numbers; a miss on 1, 2 or 5 is a finding, the rest are nits.

1. **The first prose line says what it is and for whom**, in one sentence a stranger understands; only the title
   and the badge row may sit above it. The "What it is" paragraph is 60 words or fewer, including what it does
   not do.
2. **The first install step comes within about 150 words of prose** (badges, the table of contents and image
   lines not counted). Introduction, Features and Preview are what may sit between; history, credits,
   announcements and supported-device lists never do.
3. **Features: 5 to 10 bullets, one idea each, about 10 words each.** Longer is a list of options and belongs in
   Usage.
4. **Badges: four at most**, from the list in "The shape" item 1. **Pictures: one real screenshot of the thing
   working under Preview**, a few more where a step needs one; the rest on a docs page.
5. **Length: 3,000 words is the ceiling for a single-file README** (the sample median). Over it, the review asks
   for the reason; over about 7,000 the Usage reference (every option, state, attribute, service and event)
   moves to `docs/reference.md` in the same repository, linked from Usage, and the README keeps Configuration,
   one States table and one copy-paste example per common job. The YAML example stays next to its service,
   wherever the service section lives.
6. **Nothing is said twice.** Install steps, options and service fields are the usual repeats: each lives in one
   section and the others link to it.
7. **Required sections:** Title and badges, What it is, Installation, Usage (at least Configuration), Making
   contributions, License. **Optional, left out when they do not apply:** Table of contents (over about 1,000
   words), Introduction's parts list (more than one part), Preview (a real screenshot exists), Updating (it
   differs from "update in the Marketplace, restart"), Uninstalling (something is left behind), Versions (behavior changed
   between releases), Third party platforms, Events and Automations. The order of "The shape" is kept for the
   sections that stay.
8. **A phone read works:** a heading every few screens, tables of four columns or fewer, no wide image carrying
   text.
9. **Nothing for an AI in the README.** Build, test, check and release commands and the rules an agent keeps are
   in `AGENTS.md` (the Robot README); the README never copies them.

**Reviewing a README against this file:** read it once as a stranger on a phone, then count the targets. Verdict
line: `PASS` / `PASS WITH NITS` (one to three nits) / `PASS WITH FINDINGS` (a miss on target 1, 2 or 5) / `FAIL`
(the reader cannot say what it is, or cannot install it from the README).

## Rules

- **US English.** color, behavior, canceled, organize, center, license, gray.
- **No house specifics.** No names of people, rooms, streets, devices, entity ids, addresses or dates from a
  real home. Examples use `light.kitchen_ceiling`, "a family of four", "a pet sitter". Lessons may cite "a real
  install", never its files.
- **Author and maintainer: The Backshop.** In `manifest.json`, `codeowners` is `@fatherdoctor`. Never a tool's
  or the kit's name as author.
- **License: MIT** unless a row says otherwise.
- **Tables for facts.** States, attributes, inputs, commands, events: a table, with the value or type, then a
  short note. Prose carries the why.
- **Every service and event has a copy-paste YAML example.** Run it once; an example that does not work is worse
  than none.
- **Versions are stated once**, near the top, and in a Versions table when behavior changed between releases
  (what changed, whether a default changed).
- **Keep facts, change shape.** Restructuring a README never drops a fact; if a fact belongs in a design
  document instead, link to that document.

## Screenshots

- Stored in `screenshots/` at the repository root, referenced by raw URL
  (`https://raw.githubusercontent.com/<owner>/<repo>/main/screenshots/<file>.png`) so the Marketplace page and GitHub
  both render them.
- Alt text on every image, saying what the screen shows.
- Light theme. One window, cropped to the subject. GIFs for flows (a setup, a state change), under 2 MB each.
- **No personal data in any shot:** no real names, addresses, entity names from a real home, tokens, map
  locations or camera views. Use a demo instance or blur and redo.
- **Never fake or placeholder a screenshot, and never leave a broken link.** A section whose shot does not exist
  yet says nothing about it in the README; the shot is listed in `screenshots/NEEDED.md` (what screen, what
  state, file name, which README section) for someone to capture, and the image line is added with the file.

## A skeleton

````markdown
# Name
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Release](https://img.shields.io/github/v/release/<owner>/<repo>)](https://github.com/<owner>/<repo>/releases)
[![License](https://img.shields.io/github/license/<owner>/<repo>)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.10%2B-blue.svg)](https://www.home-assistant.io)

One paragraph: what it is, for whom, what it does not do.

- [Name](#name)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Updating](#updating)
  - [Uninstalling](#uninstalling)
  - [Usage](#usage)
  - [Making contributions](#making-contributions)
  - [License](#license)

## Introduction
### Features
### Preview
## Installation
## Updating
## Uninstalling
## Usage
### Entities
#### States
#### Attributes
#### Commands
### Services
#### domain.service
### Events
### Automations
## Versions
## Making contributions
## License
````
