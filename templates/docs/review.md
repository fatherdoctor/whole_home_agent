# <What was reviewed> (<CODE>): <kind of review> (<reviewer role>, <YYYY-MM-DD>)

<!-- Template: templates/docs/review.md (kit KIT-BRD); goes to house/docs/reviews/<CODE>-<YYYY-MM-DD>.md, one file per
     review row (<CODE>r). Chapter: principles/board-and-lanes.md rules 7 to 9. Kinds: full review (first publication,
     a new feature or a changed behavior), diff-only check (a patch), closure check (only the findings of an earlier
     review were enacted). The reviewer writes sections 1 to 3; the author appends 4; the original reviewer appends 5.
     Severity: High = wrong, unsafe or sends something it should not; Medium = a real defect with a workaround;
     Low = a defect nobody hits today; Nit = wording, naming, style. Every finding says how to reproduce it or why
     it is reasoned, and what the fix is. PASS WITH NITS = only Low findings and nits, which the author carries in
     its next push with no fix row (never for public code or a protected domain: there every finding gets the fix row
     and the closure row, board-and-lanes rule 7). Keep the verdict line in exactly this shape: a closing script
     reads it. Delete this comment. -->

**Verdict: PASS | PASS WITH NITS | PASS WITH FINDINGS | FAIL** (<n> High, <n> Medium, <n> Low, <n> Nits). <Two to five sentences: what
the deliverable is, what it does right, what the findings are about.>

Reviewed at <repository> `<branch>` `<commit>`: <the files read>, against <the row, the design, the spec>. Tests run:
`<command>` - <result>. Every finding marked *reproduced* was reproduced; the rest are marked *reasoned*. Helpers
used: none | <role>: <what>.

## 1. Findings

### High
**H1. <One sentence: what is wrong.>** <Where (file, line or function). How it fails, with the input or state.
*Reproduced* or *reasoned*. The fix, in one or two sentences.>

### Medium
**M1. ...**

### Low
**L1. ...**

### Nits
**N1. ...**

## 2. What held
<The checks that passed and matter: the never list, nothing sent, no secret printed, the undo present, the tests.
One line each, so the closure check knows what not to re-check.>

## 3. Enactment
<What the board does next: PASS -> the row is DONE with this verdict in one line once the work has landed, else
`PASSED - MERGE <date> (review PASS) waits on <PR or file> -> <merge owner>`; PASS WITH NITS -> as PASS, and the
author enacts the nits in its next push on the same branch (`nits enacted <commit>` in the parent row, no card);
FINDINGS -> a fix row `<CODE>.f` for the author's lane listing H and M as must-fix, L and N as should-fix; FAIL -> the
row goes back to IN PROGRESS or PARTIAL with the High findings as its next step.>

## 4. Author's response (<CODE>.f, <lane>, <YYYY-MM-DD>)
<One line per finding: fixed in `<commit>` (what changed), or declined with the reason. Nothing is silently
skipped.>

## 5. Closure (<reviewer role>, <CODE>.fc or a Closure line, <YYYY-MM-DD>)
**CLOSED: PASS | FAIL.** <One line per finding: fixed, reasonably declined, or still open; then one line on anything
the fixes newly broke (tests run again, the diff read). No new round of findings. When the fix row was 2 points or
less there is no `<CODE>.fc` row: the original reviewer appends one line here in its next run,
`Closure: <commit> checked - PASS` (or `FAIL` with the missing item), and that line is the closure evidence.>
