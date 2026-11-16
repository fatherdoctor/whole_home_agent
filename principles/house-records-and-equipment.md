# House records and the equipment that is not connected

*Status: written (2026-10-17). Distilled from a real install's first week of records intake; the failure modes are written generically.*

Water heaters, furnaces and condensers, the panel, the garage door, appliances, shutoffs, the irrigation backflow,
meters, the foundation, the HOA papers, insurance and service contracts. None of it is on the network, all of it
fails eventually, and when it does someone needs the model, the shutoff, the manual and the phone number in under a
minute. This principle turns the owner's photos and documents into that, without the owner doing anything but
taking pictures and answering what a photo cannot tell.

## The rule

1. [default, topic 10] **One inbox, one master copy, one full local copy.** The owner drops anything (label photos, PDFs, scans) into
   a single inbox folder in their cloud drive. The agent files every item into a fixed taxonomy (01 Equipment by
   system: HVAC, Water and plumbing, Kitchen, Laundry, Garage, Irrigation, Electrical, Other; 02 Plans, survey and
   foundation; 03 Warranties, receipts and contracts; 04 Service history; 98 Needs the owner), **moves and renames,
   never deletes**, and keeps a full copy on the box (`house/records/` or a share outside the web root) that rides
   in the encrypted backup. Files the owner linked from elsewhere are **copied, never moved**.
2. [core] **Facts go in the repository; files do not.** An inventory row per item: location, make, model, serial and
   what it decodes to (age), electrical rating, **shutoff**, consumables and part numbers, the file names, the date
   captured, open questions. Serial, model, account, contract, policy and receipt numbers are facts the next owner
   needs (the owner decides, in `house/docs/policies.md`). Pairing keys printed on a label (a Z-Wave DSK, a
   QR setup code), codes and passwords are secrets and are never written down, even when the photo shows them.
3. [core] **Identity and income documents are out of scope.** A refinance or closing package holds licenses, pay stubs,
   tax forms and bank statements next to the survey. Read and copy only the house documents the owner names; from a
   loan or insurance file record only what is needed in an emergency or for a claim (carrier, policy number, term,
   agent, claims line, deductibles), never amounts, limits, premiums, names or loan numbers unless the owner asks.
4. [core] **Look it up; ask only what a photo cannot tell.** A model number gives the manual, the filter size, the anode
   part and the serial-date decode: a bot fetches them. The owner is asked only for locations, which-is-which, and
   what they want. Cross-check against what the house already knows (breaker sizes against nameplate maximums,
   the HA device registry against a photographed sensor) and flag disagreements instead of picking one.
5. [core] **Guest safety first.** Shutoffs (water main, gas, the panel), "no hot water", "AC not cooling", the garage
   door's manual release, a leak or gas smell, and who to call go into the household manual's queue the day they
   are learned, ahead of everything else when a visitor stay is coming.
6. [default, topic 10] **Procedures are proposed, approved, then written.** Each system gets 1-10 maintenance and repair procedures
   scaled to its complexity, enough to handle the dire cases without a tradesperson. The writer proposes the list;
   the owner approves, cuts or changes each line; only approved procedures are written, each with its inverse
   (how to put it back).
7. [default, topic 10] **Mechanical before paper.** Equipment intake, manuals and procedures outrank records-only work (HOA, permits,
   plats, financial history), which goes in at the lowest priority unless the owner raises it.
8. [core] **Size the downstream work the moment a batch lands.** Every batch adds archive fetches (~0.5 point per model
   plus ~0.25 per consumable lookup), wiki pages and guest-manual lines; add or re-size those rows in the same
   commit so the board shows what the dump cost.
9. [core] **A photo that leaves the inbox loses its location first.** Phones write GPS coordinates into every
   photo by default; a label photo carries the house's position to anyone who opens it. Before any photo or crop
   goes into a manual, the wiki, a dashboard (`/local` is reachable through remote access without a login,
   `dashboards.md`) or the repository: strip its metadata (EXIF, which holds the location), save the pixels
   upright so nothing depends on the orientation tag, and look at it for people, faces, names, mail, a house
   number or a car plate, cropping them out. The push guard refuses a committed image whose EXIF still holds GPS
   (`templates/guard/README.md`); a photo shown anywhere else has no guard, so the habit is the fence.

## Why

The house's most valuable knowledge is in the owner's head and on stickers in the garage. Photographs are cheap to
take and expensive to turn into answers; an agent that files, decodes, looks up and writes means the owner only
ever takes pictures. The privacy lines exist because a records folder attracts everything with the house's address
on it.

## How this goes wrong

- **Paging misses half the inbox.** Cloud-drive search returns a page at a time; an agent that reads only the first
  page files part of the batch and reports done. Follow the page token until it is empty, and check each result's
  parent, because the index lags behind a move.
- **Large files fail silently.** A big photo or PDF can exceed what an agent's file tool returns. Copy it
  drive-to-drive (no size limit), read its text where the drive offers it, and ask the owner for a smaller export
  rather than skipping it without saying so.
- **A financial folder rides along.** A package shared for one purpose (a loan or refinance, say) often also holds
  identity documents and tax forms. Rule 3.
- **Two sources, one wrong.** The insurer and the county disagree on the year built; the integration names a model
  the photo contradicts. Record both and ask. Rule 4.
- **A batch with no follow-on rows.** A whole batch of photos is filed, but no fetch, page or manual rows are added:
  the work exists only in the agent's memory. Rule 8.

## How to check it

- Every inventory row has a location, a shutoff (or "-") and a photo file that exists in both copies.
- The inbox is empty after a pass, except the files the agent says it could not take.
- `grep` the inventory for DSK, PIN, password and long digit runs outside the number columns.
- Every guest-safety fact from a batch has a manual-queue line.

## Adapter notes

- **Cloud drive:** any with folders, move, copy and search (Google Drive, OneDrive, Dropbox). The taxonomy is the
  same; the IDs live in the agent's notes, not the repository.
- **Calendar:** schedules learned from records (service visits, yard applications) go to the maintenance calendar,
  `principles/maintenance-calendar.md`.
- **Agents:** a cheap model can do fetches and lookups; reading photos and deciding what is a secret stays with
  the main session.
