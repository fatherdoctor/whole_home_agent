# Keeping Home Assistant terms current

At each monthly Home Assistant release:

1. Read the official release notes and follow the documentation links for renamed
   menus and features. Do not infer a rename from an informal description.
2. Add a record to `tools/ha-terms/ha-terms.json`: old names, current label, first
   release and official source link. The initial labels are Apps (2026.2),
   Tools (2026.8) and Marketplace (2026.11); each record links its release notes.
3. Run `python3 tools/ha-terms/check_ha_terms.py --report-only --json` for the
   current count and locations, then update current reader-facing guidance.
4. Run `python3 tools/ha-terms/test_check_ha_terms.py` and the starter tests below.
   Check a clean fixture and a deliberately obsolete label before committing a rule.

The checker scans Markdown, reStructuredText and text files without editing them.
It skips symlinks, private storage, dependency directories and credential-named text
files. Diagnostics contain locations, rule IDs and paragraph digests, never source
lines. It reports one finding per rule per source line. It is a literal-label
checker, not a full Markdown renderer or a detector of every paraphrase.

Visible paragraph text includes emphasis, escaped punctuation and soft line breaks.
Lists, quotes, headings and separate paragraphs retain their boundaries. Declared
programming/configuration fences, indented code, HTML comments, reference-link
metadata and template placeholders are skipped. Plain-text/output fences and inline
menu paths remain visible. Lowercase inline code identifiers and lowercase paths
are ignored; a capitalized inline menu label is checked, including punctuation.
Complex HTML and nested Markdown still need human review.

## Historical exceptions

Exceptions live in the data file with a reason. A whole-file exception must name
one exact dated historical report. A prose exception must name an exact path and
case-sensitive text; only that span is exempt. A neighboring current instruction
is still checked. Never hide current guidance behind a broad exception. Preserve
upstream code identifiers and genuinely historical output.

## Existing findings and the ratchet

The standalone checker enforces every finding by default (exit 1).
`--report-only` reports the backlog with exit 0. Malformed data or unreadable
input returns exit 2 in either mode. Run the command for today's count; counts
change as guidance is updated.

The starter test uses `--report-only --ratchet --json`. The committed `baseline`
in the data file records each existing finding by exact path, rule, SHA-256 of its
paragraph text, and occurrence count. Existing records are tolerated, but a new
paragraph, changed text, moved path or extra occurrence fails with exit 1. Line
number changes alone do not invalidate a record. JSON output includes `new_count`
and the locations of `new_findings`; no original paragraph text is printed.
The checker also compares the candidate baseline with a separately pinned reviewed
ceiling in its source. JSON `baseline_growth` reports new identities and count
increases, including unused entries; either makes ratchet mode exit 1 even if
the stale paragraph and its matching baseline record were added together.

As findings are fixed, remove their baseline entries (or reduce their counts).
Do not automatically refresh the baseline: that would bless new stale guidance.
Baseline entries may only shrink under the existing ceiling. An exceptional
addition needs a separate change to `REVIEWED_BASELINE_LIMITS` in the checker and
a reviewer-visible PR line beginning `Baseline growth:` that names the affected
wording and explains why retaining it is necessary. The checker never infers
approval from the candidate data or reads a PR itself; reviewers must verify
that explanation before accepting a ceiling change. Do not regenerate the ceiling
from the candidate baseline.
The baseline is a transition aid, not permission to copy stale instructions.
Once the count reaches zero, remove the baseline and the two transition flags from
`test_ha_terms_report_only` in `tools/chat-starter/test_build_starter.py` and rename
that test for full enforcement. Agent-instruction findings belong to their
file's authorized owner; the checker never edits those files.

Run `python3 tools/chat-starter/build_starter.py --check` and
`python3 tools/chat-starter/test_build_starter.py` for the starter checks.
No workflow or CI file is changed to install this checker.
