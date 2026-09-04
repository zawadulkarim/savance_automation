# The house checklist template

Referenced from `SKILL.md`. Learned from the source workbook - sheet layout,
columns, roll-up formulas, dropdowns and the colour-coded status palette.

## Contents
- Dashboard sheet and per-feature sheets
- Module -> Check Item hierarchy
- Roll-up formulas, dropdowns, conditional formatting

- **Dashboard** sheet: environment/config header block, then four roll-up
  tables — Test Execution Summary (Total/Passed/Failed/Untested + Assigned
  To/Status/Est./Milestone, entered manually since nothing upstream supplies
  them), Priority Wise Bugs, Type Wise Bugs, Bug Fix Summary. Every numeric
  cell in these tables is a **live formula** pointing at the matching `#N`
  sheet, not a hardcoded number.
- **`#N` sheets** (one per feature/bug): a fixed header block (Task Link/
  title, Last Updated, Related Applications, Test Build/Server, Environment),
  a Test Status Summary + Bug Reporting Summary (all COUNTIF/SUM formulas
  against the check-item rows below), then the checklist table itself:
  - **Module** (col B, merged across a contiguous block of rows) -> **Check
    Item** (col C, one per row) — two-level hierarchy via merged cells, not
    indentation. Then Test Status (col D), Comment (cols E:F merged), and the
    bug-tracking block in H:N.
  - **There is no `AC #` column.** The original template carried one between
    Module and Check Item; it was dropped from the house layout (the module
    grouping alone is what testers actually navigate by). The generator still
    accepts the legacy nested `acs` spec shape and flattens it, so older spec
    files keep working — but new specs should use a flat `checks` list per
    module.
  - Check ID scheme: sheet `#N` uses `CN001, CN002, ...` for check items
    (e.g. sheet `#4` → `C4001`).
  - Check items are single, atomic, imperative assertions — "Verify...",
    "Validate...", "Confirm...", "Check the system behavior when..." — never
    compound/multi-part. One assertion per row; if a requirement has several
    independent facets (e.g. "displays correctly on Web, Kiosk, and Outlook
    Add-in"), split it into one row per facet rather than one row with "and".
  - **Test Status** (Passed/Failed/Untested) is a dropdown, color-coded green/
    red/yellow. New checklists default every row to `Untested`.
  - Bug-tracking columns (Bug ID/Title/Priority/Bug Type/Bug Fix Status/
    Reason for not fixing) exist per row but are largely unused in practice —
    this team tracks bugs in Asana instead (see
    the Stage 08 bug-report ticket), not inline in the sheet. Still
    generate the columns/dropdowns for completeness, but don't expect them to
    be filled in.

**Visual design** is modernized from the original template's raw Google-Sheets
palette: deep-navy section-title bars, medium-blue column headers, a
validated accessible status palette (green/amber/red for Passed/Untested/
Failed, red/orange/pale-blue for High/Medium/Low priority, purple/teal for
UI/Functional bug type — all bold white-or-dark text on a solid fill, chosen
via the `dataviz` skill's palette rather than eyeballed), Segoe UI throughout,
thin borders with Excel's default gridlines turned off, and alternating
background tint *by module group* (not raw row) so the banding respects the
merged-cell hierarchy instead of cutting through it. The Module column keeps
its own constant light-blue tint so it reads as a distinct sidebar rather
than banding with the body. This is the current default look for
every sheet this skill generates — no need to re-derive or re-ask about
styling unless the user requests a further change.

A generator script that reproduces all of this exactly (merges, formulas,
dropdowns, conditional-formatting colors, column widths, freeze panes,
modern styling) lives at `scripts/build_checklist.py` — use it rather than
hand-rolling openpyxl calls, since the cell-level layout is fiddly and this
script has already been verified (via Excel COM recalculation *and* a visual
PDF export pass — see Step 5) to produce error-free formulas and correctly
rendered colors.

**A sharp edge already hit and fixed, worth knowing if you ever touch the
script's styling code:** conditional-formatting fills (`CellIsRule(fill=...)`)
follow the OOXML *differential* formatting convention, which reads a solid
fill's color from `PatternFill`'s `start_color`/`end_color` (or `bgColor`) —
**not** `fgColor`+`patternType`, the way a normal static `cell.fill` does.
Using the static-fill convention on a conditional-formatting rule is accepted
silently by openpyxl and even round-trips through a re-read with `openpyxl`,
but Excel renders **no fill at all** — it only surfaces when you actually look
at the rendered output (see Step 5). This cost an entire round of "verified"
deliverables their status colors before it was caught.
