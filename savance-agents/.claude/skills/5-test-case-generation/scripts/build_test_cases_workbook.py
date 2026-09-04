#!/usr/bin/env python3
"""
Generate the Stage 05 test-case workbook for human QA review, from the JSON
spec derived out of `test-cases.md`.

Sheet 1 "Test Cases" -- a 4-row identity header block, a section title bar, a
"Main Task:" (and optional "Sub Task:") banner, then the flat step-level table

    Test Case ID | Test Case Title | Acceptance Criteria | Ticket | Test Type |
    Priority | Preconditions | Test Data | Step | Action | Expected Result |
    Postconditions | Automation Candidate | Playwright Verified |
    Reviewer Status | Remarks

`Ticket` names the client ticket/bug/observation the case's AC belongs to --
the same value on every case in a single-ticket run, or the thing that lets a
reviewer filter a batch/bundle folder's sheet down to one underlying ticket.

**One step per row, and no merged cells anywhere in the table** -- merges break
Excel's filters, and this sheet exists to be filtered. Case-level categorical
columns are repeated on every step row of a case so that filtering by Test Type
or Priority returns whole cases; the tall narrative columns (Preconditions,
Test Data, Postconditions, Remarks) are written on the first step row only, so
a 6-step case does not repeat a paragraph six times.

`Reviewer Status` is deliberately left EMPTY, carrying a dropdown. It is the
human reviewer's column; prefilling it would fake their input.

Sheet 2 "Traceability" -- Acceptance Criteria | Test Cases | Coverage | Notes,
colour-coded by coverage.

Styling is the modern house palette shared with build_ac_workbook.py and
build_checklist.py, so the acceptance criteria, the checklist and the test
cases read as one family of documents.

Usage:
    python build_test_cases_workbook.py <spec.json> <output.xlsx>

See ../SKILL.md for the JSON spec schema and the rules used to derive it.
"""
import re
import sys
import json
from collections import Counter

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

FONT_NAME = "Segoe UI"

# Ink / chrome -- identical constants to build_ac_workbook.py.
INK_PRIMARY = "0B0B0B"
INK_SECONDARY = "52514E"
BORDER_INK = "C3C2B7"
BAND_TINT = "F9F9F7"      # alternating per-test-case tint
NEUTRAL_TINT = "F2F1EE"

ACCENT_DARK = "184F95"    # section title bars
ACCENT = "2A78D6"         # column headers
ACCENT_LIGHT = "CDE2FB"

REGULAR = Font(name=FONT_NAME, size=10, color=INK_PRIMARY)
BOLD = Font(name=FONT_NAME, size=10, bold=True, color=INK_PRIMARY)
BOLD_MUTED = Font(name=FONT_NAME, size=10, bold=True, color=INK_SECONDARY)
ID_FONT = Font(name=FONT_NAME, size=10, bold=True, color=ACCENT_DARK)
HEADER_FILL = PatternFill("solid", fgColor=ACCENT)
HEADER_FONT = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
TITLE_FILL = PatternFill("solid", fgColor=ACCENT_DARK)
TITLE_FONT = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
BANNER_FILL = PatternFill("solid", fgColor=ACCENT)
BANNER_FONT = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
LABEL_FILL = PatternFill("solid", fgColor=ACCENT_LIGHT)

CENTER = Alignment(horizontal="center", vertical="center")
CENTER_WRAP = Alignment(horizontal="center", vertical="center", wrap_text=True)
CENTER_TOP = Alignment(horizontal="center", vertical="top", wrap_text=True)
LEFT_WRAP = Alignment(horizontal="left", vertical="center", wrap_text=True)
TOP_WRAP = Alignment(horizontal="left", vertical="top", wrap_text=True)

THIN = Side(style="thin", color=BORDER_INK)
CELL_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

HEADER_BLOCK_ROWS = 4     # Project / Application / Prepared By / Last Updated
SECTION_TITLE_ROW = 6     # blank row 5 separates the block from the title bar

# (key, header, width, alignment, scope)
#   scope "case"  -- repeated on every step row of the case (keeps filters sane)
#   scope "step"  -- per step
#   scope "first" -- first step row of the case only (tall or human-fill columns)
COLUMNS = [
    ("id",                  "Test Case ID",         14.0, "center", "case"),
    ("title",               "Test Case Title",      42.0, "top",    "case"),
    ("ac",                  "Acceptance Criteria",  18.0, "center", "case"),
    ("ticket",              "Ticket",               38.0, "top",    "case"),
    ("type",                "Test Type",            20.0, "center", "case"),
    ("priority",            "Priority",             11.0, "center", "case"),
    ("preconditions",       "Preconditions",        34.0, "top",    "first"),
    ("test_data",           "Test Data",            30.0, "top",    "first"),
    ("step",                "Step",                 7.0,  "center", "step"),
    ("action",              "Action",               48.0, "top",    "step"),
    ("expected",            "Expected Result",      48.0, "top",    "step"),
    ("postconditions",      "Postconditions",       28.0, "top",    "first"),
    ("automation",          "Automation Candidate", 15.0, "center", "case"),
    ("playwright_verified", "Playwright Verified",  14.0, "center", "case"),
    ("reviewer_status",     "Reviewer Status",      16.0, "center", "first"),
    ("remarks",             "Remarks",              32.0, "top",    "first"),
]

ALIGNMENTS = {"center": CENTER_WRAP, "left": LEFT_WRAP,
              "top": TOP_WRAP, "center_top": CENTER_TOP}

REVIEWER_STATUSES = ["Accepted", "Needs Change", "Rejected"]
REVIEWER_COLORS = {
    "Accepted": ("C6EFCE", "0A5A20"),
    "Needs Change": ("FFEB9C", "6B4E00"),
    "Rejected": ("FFC7CE", "9C0006"),
}
PRIORITY_COLORS = {
    "High": ("FFC7CE", "9C0006"),
    "Medium": ("FFEB9C", "6B4E00"),
    "Low": ("E8E8E4", "52514E"),
}
COVERAGE_COLORS = {
    "Covered": ("C6EFCE", "0A5A20"),
    "Partially Covered": ("FFEB9C", "6B4E00"),
    "Not Covered": ("FFC7CE", "9C0006"),
    "Requires Clarification": ("D9D2F0", "3F2C82"),
}

TRACE_COLUMNS = [
    ("ac", "Acceptance Criteria", 22.0, "center"),
    ("cases", "Test Cases", 46.0, "top"),
    ("coverage", "Coverage", 22.0, "center"),
    ("notes", "Notes", 60.0, "top"),
]

VALID_TYPES = {
    "Functional / Positive", "Negative", "Boundary / Validation", "UI / State",
    "Persistence", "Error handling", "Integration",
    "Permission / Authorization", "Regression",
}


def est_lines(text, width):
    """Wrapped-line count for `text` in a span `width` chars wide.

    Only needed for the **merged** identity block: Excel auto-fits the height of
    a wrapped row it was given no height for, which is exact and therefore what
    the data rows rely on -- but it refuses to auto-fit a row containing a
    merged cell, so a long "Application Name" in the merged C:D span would
    silently clip to one line. Runs deliberately generous (0.9 chars per width
    unit): a too-tall row is merely airy, a too-short one hides text.
    """
    if text is None:
        return 1
    per = max(8.0, width * 0.9)
    lines = 0
    for segment in str(text).split("\n"):
        lines += max(1, int(len(segment) / per) + (1 if len(segment) % per else 0))
    return max(1, lines)


# test-cases.md bolds every named UI element (**"Save"**) and that markup rides
# into the spec verbatim. A worksheet cell has no inline rich text here, so the
# asterisks would render literally -- "click ***Save***." -- which looked fine
# structurally and awful in the Excel-COM visual pass. Strip emphasis and code
# spans on the way in; the Markdown keeps its bolding, the workbook gets clean
# prose. Quoting is what carries the emphasis in Excel.
_EMPHASIS = re.compile(r"\*{1,3}(?=[^\s*])(.+?)(?<=[^\s*])\*{1,3}", re.S)
_CODE_SPAN = re.compile(r"`([^`]+)`")


def plain(text):
    """Markdown emphasis -> flat text, for a worksheet cell."""
    if text is None:
        return ""
    out = str(text)
    for _ in range(3):                     # nested/stacked markers
        new = _EMPHASIS.sub(r"\1", out)
        if new == out:
            break
        out = new
    return _CODE_SPAN.sub(r"\1", out)


def render_list(value):
    """A spec list -> one cell. Numbered when there is more than one item."""
    if value is None:
        return ""
    if isinstance(value, str):
        return plain(value)
    items = [plain(v) for v in value if str(v).strip()]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return "\n".join("{}. {}".format(i, item) for i, item in enumerate(items, 1))


def write_identity_block(ws, spec, last_col_letter):
    """Rows 1-4: label merged across A:B, value across C:D."""
    fields = [
        ("Project Name", spec.get("project_name", "")),
        ("Application Name", spec.get("application_name", "")),
        ("Prepared By", spec.get("prepared_by", "Enosis QA")),
        ("Last Updated", spec.get("last_updated", "")),
    ]
    for offset, (label, value) in enumerate(fields):
        row = offset + 1
        ws.merge_cells("A{0}:B{0}".format(row))
        ws.merge_cells("C{0}:D{0}".format(row))
        label_cell = ws.cell(row=row, column=1, value=label)
        label_cell.font = BOLD_MUTED
        label_cell.fill = LABEL_FILL
        label_cell.alignment = LEFT_WRAP
        value_cell = ws.cell(row=row, column=3, value=value)
        value_cell.font = REGULAR
        value_cell.alignment = LEFT_WRAP
        for col in range(1, 5):
            ws.cell(row=row, column=col).border = CELL_BORDER
        # Merged rows never auto-fit -- give this one an explicit height.
        width_cd = COLUMNS[2][2] + COLUMNS[3][2]
        ws.row_dimensions[row].height = 15.5 * est_lines(value, width_cd)


def write_title_and_banner(ws, spec, last_col_letter):
    """Row 6 title bar, row 7 Main Task, optional row 8 Sub Task.

    Returns the row number the table header should occupy.
    """
    title = "Test Cases"
    if spec.get("feature"):
        title = "Test Cases: {}".format(spec["feature"])
    ws.merge_cells("A{0}:{1}{0}".format(SECTION_TITLE_ROW, last_col_letter))
    cell = ws.cell(row=SECTION_TITLE_ROW, column=1, value=title)
    cell.font = TITLE_FONT
    cell.fill = TITLE_FILL
    cell.alignment = LEFT_WRAP
    ws.row_dimensions[SECTION_TITLE_ROW].height = 22

    row = SECTION_TITLE_ROW + 1
    for label, key in (("Main Task", "main_task"), ("Sub Task", "sub_task")):
        if not spec.get(key):
            continue
        ws.merge_cells("A{0}:{1}{0}".format(row, last_col_letter))
        banner = ws.cell(row=row, column=1,
                         value="{}: {}".format(label, spec[key]))
        banner.font = BANNER_FONT
        banner.fill = BANNER_FILL
        banner.alignment = LEFT_WRAP
        ws.row_dimensions[row].height = 19
        row += 1
    return row + 1          # one blank spacer row before the header


def write_test_cases_sheet(wb, spec):
    ws = wb.active
    ws.title = "Test Cases"
    ws.sheet_view.showGridLines = False

    last_col_letter = get_column_letter(len(COLUMNS))
    for index, (_key, _header, width, _align, _scope) in enumerate(COLUMNS, 1):
        ws.column_dimensions[get_column_letter(index)].width = width

    write_identity_block(ws, spec, last_col_letter)
    header_row = write_title_and_banner(ws, spec, last_col_letter)

    for index, (_key, header, _width, _align, _scope) in enumerate(COLUMNS, 1):
        cell = ws.cell(row=header_row, column=index, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER_WRAP
        cell.border = CELL_BORDER
    ws.row_dimensions[header_row].height = 30

    row = header_row + 1
    reviewer_cells = []
    for case_index, case in enumerate(spec.get("test_cases", [])):
        steps = case.get("steps") or [{"action": "", "expected": ""}]
        band = PatternFill("solid", fgColor=BAND_TINT) if case_index % 2 else None
        for step_index, step in enumerate(steps):
            first = step_index == 0
            values = {
                "id": case.get("id", ""),
                "title": plain(case.get("title", "")),
                "ac": case.get("ac", ""),
                "ticket": plain(case.get("ticket", "")),
                "type": case.get("type", ""),
                "priority": case.get("priority", ""),
                "preconditions": render_list(case.get("preconditions")),
                "test_data": render_list(case.get("test_data")),
                "step": step_index + 1,
                "action": plain(step.get("action", "")),
                "expected": plain(step.get("expected", "")),
                "postconditions": render_list(case.get("postconditions")),
                "automation": case.get("automation", ""),
                "playwright_verified": case.get("playwright_verified", ""),
                "reviewer_status": None,          # human fills this in
                "remarks": render_list(case.get("remarks")),
            }
            for col, (key, _h, _w, align, scope) in enumerate(COLUMNS, 1):
                value = values[key]
                if scope == "first" and not first:
                    value = None
                cell = ws.cell(row=row, column=col, value=value)
                cell.font = ID_FONT if key == "id" else REGULAR
                cell.alignment = ALIGNMENTS["center_top"] if align == "center" \
                    else ALIGNMENTS[align]
                cell.border = CELL_BORDER
                if band is not None:
                    cell.fill = band
                if key == "reviewer_status" and first:
                    reviewer_cells.append(cell.coordinate)
            row += 1

    last_row = row - 1
    if last_row < header_row + 1:          # no cases -- nothing more to do
        return ws, header_row, last_row

    ws.freeze_panes = "A{}".format(header_row + 1)
    ws.auto_filter.ref = "A{}:{}{}".format(header_row, last_col_letter, last_row)

    # Reviewer Status dropdown, on the first step row of each case only.
    if reviewer_cells:
        validation = DataValidation(
            type="list",
            formula1='"{}"'.format(",".join(REVIEWER_STATUSES)),
            allow_blank=True, showDropDown=False)
        ws.add_data_validation(validation)
        for coordinate in reviewer_cells:
            validation.add(ws[coordinate])

    _add_value_formats(ws, "N", header_row + 1, last_row, REVIEWER_COLORS)
    _add_value_formats(ws, "E", header_row + 1, last_row, PRIORITY_COLORS)
    return ws, header_row, last_row


def _add_value_formats(ws, column, first_row, last_row, colors):
    """Colour a column by exact cell value.

    Conditional-format fills use the OOXML *differential* convention: a solid
    dxf fill reads from start_color/end_color, NOT fgColor + patternType.
    openpyxl accepts the static-fill spelling silently and it even round-trips
    through a re-read, but Excel renders no fill at all. Same trap documented
    in build_checklist.py and build_ac_workbook.py.
    """
    span = "{0}{1}:{0}{2}".format(column, first_row, last_row)
    for value, (fill_rgb, font_rgb) in colors.items():
        ws.conditional_formatting.add(span, FormulaRule(
            formula=['EXACT(${0}{1},"{2}")'.format(column, first_row, value)],
            fill=PatternFill(start_color=fill_rgb, end_color=fill_rgb,
                             fill_type="solid"),
            font=Font(name=FONT_NAME, size=10, bold=True, color=font_rgb),
            stopIfTrue=False))


def write_traceability_sheet(wb, spec):
    rows = spec.get("traceability") or []
    ws = wb.create_sheet("Traceability")
    ws.sheet_view.showGridLines = False

    last_col_letter = get_column_letter(len(TRACE_COLUMNS))
    for index, (_key, _header, width, _align) in enumerate(TRACE_COLUMNS, 1):
        ws.column_dimensions[get_column_letter(index)].width = width

    ws.merge_cells("A1:{}1".format(last_col_letter))
    title = ws.cell(row=1, column=1, value="Traceability Matrix")
    title.font = TITLE_FONT
    title.fill = TITLE_FILL
    title.alignment = LEFT_WRAP
    ws.row_dimensions[1].height = 22

    header_row = 3
    for index, (_key, header, _width, _align) in enumerate(TRACE_COLUMNS, 1):
        cell = ws.cell(row=header_row, column=index, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER_WRAP
        cell.border = CELL_BORDER
    ws.row_dimensions[header_row].height = 24

    row = header_row + 1
    for entry in rows:
        cases = entry.get("cases") or []
        values = {
            "ac": entry.get("ac", ""),
            "cases": ", ".join(cases) if isinstance(cases, list) else str(cases),
            "coverage": entry.get("coverage", ""),
            "notes": plain(entry.get("notes", "")),
        }
        for col, (key, _h, _w, align) in enumerate(TRACE_COLUMNS, 1):
            cell = ws.cell(row=row, column=col, value=values[key])
            cell.font = ID_FONT if key == "ac" else REGULAR
            cell.alignment = ALIGNMENTS["center_top"] if align == "center" \
                else ALIGNMENTS[align]
            cell.border = CELL_BORDER
        row += 1

    last_row = row - 1
    if last_row >= header_row + 1:
        ws.freeze_panes = "A{}".format(header_row + 1)
        ws.auto_filter.ref = "A{}:{}{}".format(header_row, last_col_letter,
                                               last_row)
        _add_value_formats(ws, "C", header_row + 1, last_row, COVERAGE_COLORS)
    return ws


def validate(spec):
    """Fail loudly on the invariants the SKILL.md promises are checked."""
    problems = []
    cases = spec.get("test_cases") or []
    if not cases:
        problems.append("spec carries no test_cases")

    seen = set()
    for case in cases:
        case_id = case.get("id") or "<no id>"
        if case_id in seen:
            problems.append("duplicate test case id: {}".format(case_id))
        seen.add(case_id)
        if not str(case.get("ac") or "").strip():
            problems.append(
                "{}: no Acceptance Criteria reference (Hard rule 2)"
                .format(case_id))
        if not str(case.get("ticket") or "").strip():
            problems.append(
                "{}: no Ticket (fourteenth required field, case-format.md)"
                .format(case_id))
        if not case.get("steps"):
            problems.append("{}: no steps".format(case_id))
        case_type = str(case.get("type") or "").strip()
        if case_type and case_type not in VALID_TYPES:
            problems.append(
                "{}: test type {!r} is not one of the nine in SKILL.md Step 4"
                .format(case_id, case_type))

    for entry in spec.get("traceability") or []:
        for ref in entry.get("cases") or []:
            if ref not in seen:
                problems.append(
                    "traceability row {!r} names unknown test case {!r}"
                    .format(entry.get("ac", "?"), ref))

    if problems:
        sys.stderr.write("Spec validation failed:\n")
        for problem in problems:
            sys.stderr.write("  - {}\n".format(problem))
        sys.exit(1)


def report(spec):
    cases = spec.get("test_cases") or []
    types = Counter(c.get("type", "?") for c in cases)
    priorities = Counter(c.get("priority", "?") for c in cases)
    automation = Counter(str(c.get("automation", "?")) for c in cases)
    verified = Counter(str(c.get("playwright_verified", "?")) for c in cases)
    steps = sum(len(c.get("steps") or []) for c in cases)
    coverage = Counter(e.get("coverage", "?")
                       for e in spec.get("traceability") or [])

    print("Test cases: {}   steps: {}   steps/case: {:.1f}".format(
        len(cases), steps, steps / len(cases) if cases else 0))
    print("  by type:      " + ", ".join(
        "{} {}".format(v, k) for k, v in types.most_common()))
    print("  by priority:  " + ", ".join(
        "{} {}".format(v, k) for k, v in priorities.most_common()))
    print("  automation:   " + ", ".join(
        "{} {}".format(v, k) for k, v in automation.most_common()))
    print("  pw verified:  " + ", ".join(
        "{} {}".format(v, k) for k, v in verified.most_common()))
    if coverage:
        print("  coverage:     " + ", ".join(
            "{} {}".format(v, k) for k, v in coverage.most_common()))

    negative = sum(types[t] for t in
                   ("Negative", "Boundary / Validation", "Error handling"))
    if cases:
        share = 100.0 * negative / len(cases)
        note = ""
        if share < 20:
            note = "  <- under 20%: refusal paths may be missing"
        elif share > 60:
            note = "  <- over 60%: positive coverage may be thin"
        print("  negative+boundary+error share: {:.0f}%{}".format(share, note))


def main():
    if len(sys.argv) != 3:
        sys.stderr.write(__doc__)
        sys.exit(2)
    spec_path, out_path = sys.argv[1], sys.argv[2]

    # utf-8-sig: PowerShell 5.1's Set-Content -Encoding utf8 writes a BOM that
    # plain utf-8 json.load rejects outright.
    with open(spec_path, encoding="utf-8-sig") as handle:
        spec = json.load(handle)

    validate(spec)

    wb = openpyxl.Workbook()
    write_test_cases_sheet(wb, spec)
    if spec.get("traceability_sheet", True) and spec.get("traceability"):
        write_traceability_sheet(wb, spec)
    wb.save(out_path)

    report(spec)
    print("\nWrote {}".format(out_path))


if __name__ == "__main__":
    main()
