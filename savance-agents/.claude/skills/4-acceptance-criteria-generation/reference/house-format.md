# House format and writing style

Referenced from `SKILL.md` Steps 3-4. Learned from four accepted reference
workbooks (281 real AC rows) — these are measured conventions, not preferences.

## Contents
- Sheet and column layout, the AC ID scheme, calibration bands
- Writing style: atomicity, verbatim strings, voice, the compound-gate rule

Learned from these four, all in the project root:

| File | Shape it demonstrates |
|---|---|
| `[Internal][Acceptance Criteria] Savance Q3 Release Items.xlsx` | `per_ticket`: Dashboard + one `#N` sheet per ticket. **The canonical internal shape** — this is the one that pairs with the QA checklist. |
| `[Acceptance Criteria] Savance Miscellaneous (Phase 1).xlsx` | `single_sheet`: one sheet, many tickets, `Application` group column + `Task` column + `Status` column. |
| `[Acceptance Criteria] Outlook Add-In_ Visitor Management.xlsx` | One sheet per functional area (`Authentication`, `Add_Attendees`, …); `Expected System Behavior` left empty throughout. |
| `[Acceptance Criteria] Outlook Add-In_ Full Window App.xlsx` | Same, plus a per-row `Status` column carrying real Passed/Failed results. |

Read one of them once if they're still around, but treat them as worked
examples — this skill must work on whatever the user points it at.

**Sheet anatomy** (rows are fixed; the generator handles all of it):

- **Rows 1-4** — identity block: `Project Name`, `Application Name`,
  `Prepared By`, `Last Updated`. Label merged across `A:B`, value across
  `C:D`.
- **Row 5** — blank spacer.
- **Row 6** — section title bar: `Acceptance Criteria`, or
  `Acceptance Criteria: <section>` when a section name is given.
- **Row 7** — `Main Task: <ticket name>`. **Row 8** — `Sub Task: <name>`,
  only when the ticket has one.
- **Then** the table header, then one row per AC.

**Columns.** `ID | Module | Description | Acceptance Rules | Expected System
Behavior | Notes`, plus two optional ones — `Task` (after the group column)
and `Status` (before `Notes`). The group column (`Module`, or `Application`
in the single-sheet shape) is **merged over each contiguous block** of rows
sharing that value — the same sidebar treatment `4-checklist-generation` gives
its Module column.

**ID scheme:** `AC{sheet number}{seq:03d}` — sheet `#2` runs `AC2001,
AC2002, …`, sheet `#3` restarts at `AC3001`. The sequence restarts per
sheet, never continues across sheets. The `single_sheet` milestone workbooks
are the exception in practice: each one restarts at a flat `AC001` and runs
in order (`[Acceptance Criteria] Savance Miscellaneous (Phase 2).xlsx` and
its `- Milestone 2` sibling both do), which the generator produces via
explicit per-row `id` overrides.

**When the source already carries its own AC IDs** — a draft PDF, a master
AC index, a client-supplied sheet — those IDs are usually neither sequential
nor in the source's own row order. **Renumber to the house scheme and put
the original in `Notes` as `Draft ID: <original>`**, so the sheet reads in
order without severing traceability back to the source. Confirmed by the
user on the Milestone 3 run. Only keep the source IDs verbatim if the user
says dev or the client already reference them elsewhere.

**Visual design** is the modern house palette shared with
`4-checklist-generation` (Segoe UI, deep-navy title bars, medium-blue column
headers, light-blue group sidebar, alternating tint *by group block*, thin
borders, gridlines off) — deliberately **not** the reference files' raw
Google-Sheets look (Calibri, `#9CC2E5` labels, `#3C78D8` headers). The AC
workbook and the checklist ship to the same reviewer in the same folder;
they should read as one family. Don't re-derive or re-ask about styling.

Two deliberate deviations from the reference files, both worth keeping:

- **Vertical alignment is top, not centre.** The reference centres
  `Description`/`Rules`/`Expected` vertically, which leaves a short
  description floating in the middle of a tall row, visually detached from
  the rules it belongs to. Top-aligning all three lines their first line up.
- **Row 6 reads `Acceptance Criteria`.** Two reference sheets have it
  misspelled `Acceptance Critera`. That's a typo, not a convention — don't
  "fix" the generator to reproduce it.

## Writing style

This matters more than the formatting; the format is automated, the prose is
not. Measured across all four reference workbooks: **281 AC rows carrying
1063 acceptance rules.**

**Description** — one line naming what is being verified, not how.
`Ensure that ...` / `Ensure the ...` is the dominant house voice in the
Savance-project files (71 of 108 openers) and is the default:

> Ensure that a new setting is added to the **"Manage Host Profiles"** modal
> to manage unavailable hosts.

The two Outlook app-level workbooks instead use a declarative requirement
(`The add-in must be available on Microsoft add-in store.`). Either is
acceptable, but pick one per workbook and stay consistent — don't mix voices
across sheets.

**Acceptance Rules** — a numbered list. Each rule is one atomic,
independently verifiable assertion; if a rule needs an "and" joining two
observable outcomes, it's two rules. Default subject is the system:

> 1. The system must display the **"Agreement checkbox"** in an unchecked and
>    disabled state by default.

Name the application explicitly whenever the rule is app-specific — the
reference files switch to `The Kiosk application must ...`, `The "Visitor
Sign In" vmsuite app must ...` rather than leaving "the system" ambiguous
across surfaces. Other established forms, all in use:

- Conditional — `When this setting is turned on, the host selection must ...`
- Precondition — `If the host status changes to "Out" ... the visitor must be
  blocked ...`
- Interaction — `Clicking the "Confirm" button must trigger a live check ...`
- Compound gate, kept as one rule — `... must prevent the visitor from
  proceeding when all of the following conditions are met: The "Agreement"
  question is marked as "Required"; The "Agreement checkbox" remains
  unchecked.` (facets separated by semicolons, not split into sibling rules)

Quote every user-facing string **verbatim**, including punctuation:

> 3. The following message must be displayed if the host's status changes
>    during sign-in: `"Host status changed from 'In' to 'Out'. Please confirm
>    the status and try again."`

**Expected System Behavior** — one declarative sentence in the present
tense, describing the net observable outcome. No `must`; this is not a
restatement of each rule but a summary of what a tester will see when all of
them hold:

> The "Kiosk" app displays all hosts from the selected "Host Profile"
> alongside their current status, where hosts with an "Out" or "Unavailable"
> status are visually grayed out and unselectable, and tapping them triggers
> an on-screen pop-up alert stating: "This host is currently unavailable and
> cannot receive visitors."

A short numbered list is acceptable when one AC genuinely produces two
unrelated outcomes. Both Outlook workbooks leave this column empty
throughout — permissible when the user asks for that shape, but the default
is to fill it.

**Quoting.** Every reference to a named UI element — page, tab, button,
field, modal, dropdown — is quoted. Use **double** quotes; the reference
files are inconsistent (`#1` uses double, `#2`/`#3` single) and double is the
house standard shared with `8-asana-bug-report` and
`1-requirement-analysis`. Plain descriptive words ("the dropdown",
"the page") stay unquoted. Unlike the queries doc, cells are **not** bolded —
none of the reference workbooks use in-cell rich text.

Every Description and every rule ends in a period.

**Sizing.** Rules per AC row across the reference set: **mean 3.80, median
3**, range 1-13; the per-file means cluster tightly (3.46 / 3.63 / 4.02 /
4.14). The generator prints the achieved ratio — check it before handoff. A
draft averaging below ~2 is bundling too much into each rule or under-
specifying; above ~6 it is usually splitting one behavior across rules that
should be a single compound gate. Outliers on individual rows are fine and
expected; it's the sheet average that should sit in the 3-4.5 band.
