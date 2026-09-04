#!/usr/bin/env python3
"""
Generate a new QA checklist workbook in the house "Savance Q3 Release Items"
template: a Dashboard sheet plus one sheet per feature (#N), each with a
Module -> Check Item hierarchy, live roll-up formulas, dropdowns, and
conditional-formatting colors matching the original template.

Modules carry a flat "checks" list. The legacy nested {"acs": [{"checks":
[...]}]} shape is still accepted and flattened (the AC # column was dropped
from the house layout), so older spec files keep working.

Usage:
    python build_checklist.py <spec.json> <output.xlsx>

See ../SKILL.md for the JSON spec schema and the rules used to derive it.
"""
import sys
import json

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation

FONT_NAME = "Segoe UI"

# Ink / chrome (from the house data-viz palette: references/palette.md)
INK_PRIMARY = "0B0B0B"
INK_SECONDARY = "52514E"
BORDER_INK = "C3C2B7"
BAND_TINT = "F9F9F7"      # alternating module-group tint
MODULE_TINT = "E3EEFC"    # module-column tint (light accent-blue)
AC_TINT = "F2F1EE"        # neutral tint (summary sub-headers)

ACCENT_DARK = "184F95"    # section title bars
ACCENT = "2A78D6"         # column headers
ACCENT_LIGHT = "CDE2FB"   # subtle highlight (e.g. Low priority, Overall Total)

REGULAR = Font(name=FONT_NAME, size=10, color=INK_PRIMARY)
BOLD = Font(name=FONT_NAME, size=10, bold=True, color=INK_PRIMARY)
BOLD_MUTED = Font(name=FONT_NAME, size=10, bold=True, color=INK_SECONDARY)
BOLD_MODULE = Font(name=FONT_NAME, size=10, bold=True, color=ACCENT_DARK)
HEADER_FILL = PatternFill("solid", fgColor=ACCENT)
HEADER_FONT = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
TITLE_FILL = PatternFill("solid", fgColor=ACCENT_DARK)
TITLE_FONT = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
TOTAL_FILL = PatternFill("solid", fgColor=ACCENT_LIGHT)

CENTER = Alignment(horizontal="center", vertical="center")
CENTER_WRAP = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_WRAP = Alignment(horizontal="left", vertical="center", wrap_text=True)
MODULE_ALIGN = Alignment(horizontal="center", vertical="top", wrap_text=True)

THIN = Side(style="thin", color=BORDER_INK)
CELL_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Status palette -- fixed, semantic, validated for contrast (good/warning/
# critical from the house data-viz palette) -- (fill, text) pairs, always bold.
STATUS_COLORS = {
    "Passed": ("0CA30C", "FFFFFF"),
    "Failed": ("D03B3B", "FFFFFF"),
    "Untested": ("FAB219", "0B0B0B"),
}
PRIORITY_COLORS = {
    "High": ("D03B3B", "FFFFFF"),
    "Medium": ("EC835A", "0B0B0B"),
    "Low": ("CDE2FB", "0B0B0B"),
}
TYPE_COLORS = {
    "UI": ("4A3AA7", "FFFFFF"),
    "Functional": ("1BAF7A", "FFFFFF"),
}
FIX_COLORS = {
    "Fixed": ("0CA30C", "FFFFFF"),
    "Not Fixed": ("D03B3B", "FFFFFF"),
}

DASHBOARD_WIDTHS = {"A": 3.25, "B": 6.38,
                    # C holds each sheet's full title in all four roll-up
                    # tables. At the original 37.63 a long title (e.g. one
                    # naming two applications) overflowed into D and got
                    # clipped at the table's edge; widened and wrapped below.
                    "C": 46.0, "D": 12.63,
                    # E/F hold the "Executed By / Executed On / Test URL /
                    # Browser Info." label+value pairs; without explicit
                    # widths they fall back to 8.43 and the labels render
                    # clipped ("Executed (", "Browser Ir") because the
                    # adjacent value cell blocks overflow.
                    "E": 13.0, "F": 14.0,
                    "G": 11.5, "H": 10.5, "I": 10.5,
                    # J/K carry the "Assigned To" header and "Status" values
                    # ("QA Backlog" clips at the default width).
                    "J": 13.0, "K": 13.0,
                    "L": 6.38, "M": 12.63, "N": 3.25, "O": 12.63}
ITEM_WIDTHS = {"A": 6.38, "B": 18.88, "C": 62.63, "D": 12.63,
               "F": 18.88, "G": 2.63, "H": 18.88,
               # I-M are the Bug Reporting Summary label/value pairs and the
               # Bug Title/Priority/Bug Type/Bug Fix Status headers. Left at
               # the 8.43 default these clip ("Functiona", "Bug Fix Status").
               "I": 14.0, "J": 12.0, "K": 10.0, "L": 12.0, "M": 14.0,
               "N": 37.63}

# Every data column that takes the alternating module-group band -- i.e. all
# of them except B (the module sidebar, which keeps a constant tint) and G
# (the narrow spacer between the checklist and the bug-tracking block).
DATA_BAND_COLS = ["A", "C", "D", "E", "F", "H", "I", "J", "K", "L", "M", "N"]


def label(ws, coord, text, bold=True, muted=False):
    c = ws[coord]
    c.value = text
    c.font = BOLD_MUTED if (bold and muted) else (BOLD if bold else REGULAR)
    return c


def style_header_row(ws, row, cols):
    for col in cols:
        c = ws[f"{col}{row}"]
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = CENTER_WRAP


def style_title(ws, coord):
    c = ws[coord]
    c.fill = TITLE_FILL
    c.font = TITLE_FONT


def border_range(ws, min_row, max_row, cols):
    for r in range(min_row, max_row + 1):
        for col in cols:
            ws[f"{col}{r}"].border = CELL_BORDER


def add_dropdown(ws, rng, options):
    dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"',
                         allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(rng)


def add_cellis_rule(ws, rng, value, color, font_color):
    # Differential (conditional-format) fills follow OOXML's dxf convention,
    # not the normal cellXfs one: a solid dxf fill is read from bgColor, and
    # setting patternType/fgColor here (as for a *static* cell.fill) silently
    # fails to render in Excel even though openpyxl accepts it without error.
    ws.conditional_formatting.add(
        rng,
        CellIsRule(operator="equal", formula=[f'"{value}"'],
                   fill=PatternFill(start_color=color, end_color=color, fill_type="solid"),
                   font=Font(name=FONT_NAME, bold=True, color=font_color)),
    )


def build_item_sheet(wb, n, feature, project_name):
    sheet_name = f"#{n}"
    ws = wb.create_sheet(sheet_name)
    ws.sheet_view.showGridLines = False
    ws.sheet_format.defaultRowHeight = 18

    title = feature["title"]

    # --- header block ---
    ws.merge_cells("A1:B1"); label(ws, "A1", "Project Board")
    style_title(ws, "A1")
    ws["C1"] = project_name
    ws["C1"].font = BOLD
    ws.merge_cells("D1:E2"); label(ws, "D1", "Test Status Summary")
    style_title(ws, "D1")
    ws.merge_cells("H1:M1"); label(ws, "H1", "Bug Reporting Summary")
    style_title(ws, "H1")

    ws.merge_cells("A2:B2"); label(ws, "A2", "Task Link", muted=True)
    ws["C2"] = title
    ws["C2"].font = REGULAR
    ws.merge_cells("H2:I2"); label(ws, "H2", "Priority Wise", muted=True)
    ws["H2"].fill = PatternFill("solid", fgColor=AC_TINT)
    ws.merge_cells("J2:K2"); label(ws, "J2", "Type Wise", muted=True)
    ws["J2"].fill = PatternFill("solid", fgColor=AC_TINT)
    ws.merge_cells("L2:M2"); label(ws, "L2", "Fixed Status", muted=True)
    ws["L2"].fill = PatternFill("solid", fgColor=AC_TINT)

    ws.merge_cells("A3:B3"); label(ws, "A3", "Last Updated", muted=True)
    ws["C3"] = feature.get("last_updated", "-")
    ws.merge_cells("A4:B4"); label(ws, "A4", "Related Applications", muted=True)
    ws["C4"] = feature.get("related_applications", "-")
    ws.merge_cells("A5:B5"); label(ws, "A5", "Test Build No. | Connected Server Details", muted=True)
    ws["C5"] = feature.get("test_build", "-")
    ws.merge_cells("A6:B6"); label(ws, "A6", "Environment Details (Device, OS, Browser)", muted=True)
    ws["C6"] = feature.get("environment", "-")
    for coord in ("C3", "C4", "C5", "C6"):
        ws[coord].font = REGULAR
    for row in range(2, 7):
        for col in ("A", "C"):
            ws[f"{col}{row}"].alignment = LEFT_WRAP
    # The A:B label block is only ~25 characters wide, so the two longest
    # labels ("Test Build No. | Connected Server Details", "Environment
    # Details (Device, OS, Browser)") need room for a second wrapped line --
    # at the default row height Excel just clips them mid-word.
    ws.row_dimensions[5].height = 27
    ws.row_dimensions[6].height = 27

    # --- flatten modules -> checks into row plan ---
    # A module carries a flat "checks" list; the legacy nested "acs" shape is
    # flattened in order (the AC # column is no longer part of the layout).
    rows = []  # (module_name, check_text)
    for module in feature.get("modules", []):
        checks = list(module.get("checks", []))
        for ac in module.get("acs", []):
            checks.extend(ac.get("checks", []))
        for check in checks:
            rows.append((module["name"], check))

    first_row = 9
    last_row = first_row + len(rows) - 1 if rows else first_row

    # --- Test Status Summary formulas ---
    label(ws, "D3", "Total", muted=True); ws["E3"] = "=SUM(E4:E6)"
    label(ws, "D4", "Passed", muted=True); ws["E4"] = f'=COUNTIF(D{first_row}:D{last_row},"Passed")'
    label(ws, "D5", "Failed", muted=True); ws["E5"] = f'=COUNTIF(D{first_row}:D{last_row},"Failed")'
    label(ws, "D6", "Untested", muted=True); ws["E6"] = f'=COUNTIF(D{first_row}:D{last_row},"Untested")'

    # --- Bug Reporting Summary formulas ---
    label(ws, "H3", "High", muted=True); ws["I3"] = f'=COUNTIF(K{first_row}:K{last_row},"High")'
    label(ws, "H4", "Medium", muted=True); ws["I4"] = f'=COUNTIF(K{first_row}:K{last_row},"Medium")'
    label(ws, "H5", "Low", muted=True); ws["I5"] = f'=COUNTIF(K{first_row}:K{last_row},"Low")'
    label(ws, "H6", "Total", muted=True); ws["I6"] = "=SUM(I3:I5)"

    label(ws, "J3", "Functional", muted=True); ws["K3"] = f'=COUNTIF(L{first_row}:L{last_row},"Functional")'
    label(ws, "J4", "UI", muted=True); ws["K4"] = f'=COUNTIF(L{first_row}:L{last_row},"UI")'
    label(ws, "J5", "-", muted=True); ws["K5"] = "-"
    label(ws, "J6", "Total", muted=True); ws["K6"] = "=SUM(K3:K4)"

    label(ws, "L3", "Fixed", muted=True); ws["M3"] = f'=COUNTIF(M{first_row}:M{last_row},"Fixed")'
    label(ws, "L4", "Not Fixed", muted=True); ws["M4"] = f'=COUNTIF(M{first_row}:M{last_row},"Not Fixed")'
    label(ws, "L5", "-", muted=True); ws["M5"] = "-"
    label(ws, "L6", "Total", muted=True); ws["M6"] = "=SUM(M3:M4)"

    for coord in ("E3", "E4", "E5", "E6", "I3", "I4", "I5", "I6",
                  "K3", "K4", "K5", "K6", "M3", "M4", "M5", "M6"):
        ws[coord].font = REGULAR
        ws[coord].alignment = CENTER

    border_range(ws, 1, 6, ["A", "B", "C", "D", "E"])
    border_range(ws, 1, 6, ["H", "I", "J", "K", "L", "M"])

    # --- table header row ---
    headers = {
        "A8": "#", "B8": "Module", "C8": "Check Item",
        "D8": "Test Status", "E8": "Comment",
        "H8": "Bug ID", "I8": "Bug Title", "K8": "Priority",
        "L8": "Bug Type", "M8": "Bug Fix Status", "N8": "Reason for not fixing",
    }
    for coord, text in headers.items():
        ws[coord] = text
    ws.merge_cells("E8:F8")
    ws.merge_cells("I8:J8")
    style_header_row(ws, 8, ["A", "B", "C", "D", "E", "H", "I", "K", "L", "M", "N"])
    ws.row_dimensions[8].height = 22

    # --- data rows: write each check, tracking module merge ranges + banding ---
    r = first_row
    prev_module = None
    module_seq = 0
    module_range_start = r

    def close_module_block(start, end):
        """Merge the module sidebar over its block and tint the whole span --
        tinting only the merge anchor leaves the rest of the block white."""
        if end > start:
            ws.merge_cells(f"B{start}:B{end}")
        ws[f"B{start}"].alignment = MODULE_ALIGN
        ws[f"B{start}"].font = BOLD_MODULE

    for module_name, check_text in rows:
        check_seq = r - first_row + 1
        if module_name != prev_module:
            module_seq += 1

        # Banding alternates per module group, so it never cuts through a
        # merged module block.
        band = PatternFill("solid", fgColor=BAND_TINT) if module_seq % 2 == 0 else None
        if band is not None:
            for col in DATA_BAND_COLS:
                ws[f"{col}{r}"].fill = band

        ws[f"A{r}"] = f"C{n}{check_seq:03d}"
        ws[f"A{r}"].alignment = CENTER
        ws[f"A{r}"].font = REGULAR
        ws[f"C{r}"] = check_text
        ws[f"C{r}"].alignment = LEFT_WRAP
        ws[f"C{r}"].font = REGULAR
        ws[f"D{r}"] = "Untested"
        ws[f"D{r}"].alignment = CENTER
        ws.merge_cells(f"E{r}:F{r}")
        ws.merge_cells(f"I{r}:J{r}")

        if module_name != prev_module:
            if prev_module is not None:
                close_module_block(module_range_start, r - 1)
            module_range_start = r
            ws[f"B{r}"] = module_name
            prev_module = module_name

        r += 1

    if rows:
        close_module_block(module_range_start, r - 1)

        # The module column gets a constant tint (not banded) so it reads as a
        # distinct sidebar rather than blending into the banded body.
        for row_ in range(first_row, r):
            ws[f"B{row_}"].fill = PatternFill("solid", fgColor=MODULE_TINT)

        border_range(ws, 8, r - 1, ["A", "B", "C", "D", "E"])
        border_range(ws, 8, r - 1, ["H", "I", "K", "L", "M", "N"])

        # Dropdowns applied across the FULL data range. The source template
        # only applied the Priority/Bug Type/Bug Fix Status dropdowns to a
        # single row (row 9) -- that reads as a template oversight, not a
        # convention worth repeating, so every row gets a working dropdown.
        add_dropdown(ws, f"D{first_row}:D{last_row}", ["Passed", "Failed", "Untested"])
        add_dropdown(ws, f"K{first_row}:K{last_row}", ["High", "Medium", "Low", "No Priority"])
        add_dropdown(ws, f"L{first_row}:L{last_row}", ["Functional", "UI", "No Type"])
        add_dropdown(ws, f"M{first_row}:M{last_row}", ["Fixed", "Not Fixed", "No Status"])

        for value, (color, font_color) in STATUS_COLORS.items():
            add_cellis_rule(ws, f"D{first_row}:D{last_row}", value, color, font_color)
        for value, (color, font_color) in PRIORITY_COLORS.items():
            add_cellis_rule(ws, f"K{first_row}:K{last_row}", value, color, font_color)
        for value, (color, font_color) in TYPE_COLORS.items():
            add_cellis_rule(ws, f"L{first_row}:L{last_row}", value, color, font_color)
        for value, (color, font_color) in FIX_COLORS.items():
            add_cellis_rule(ws, f"M{first_row}:M{last_row}", value, color, font_color)

    # --- layout ---
    ws.freeze_panes = "A9"
    for col, w in ITEM_WIDTHS.items():
        ws.column_dimensions[col].width = w

    return {
        "n": n, "sheet_name": sheet_name, "title": title, "total": len(rows),
        "assigned_to": feature.get("assigned_to", "-"),
        "status": feature.get("status", "QA Backlog"),
        "est_hours": feature.get("est_hours", "-"),
        "milestone": feature.get("milestone", "-"),
    }


def build_dashboard_table(ws, title_row, section_title, col_labels, metas,
                           value_cols, total_span):
    """col_labels: dict col_letter -> header text (besides '#'/'Module'),
    first entry must be the 'Total' column.
    value_cols: dict col_letter -> callable(meta) -> formula/value string,
    for every column except the Total column.
    total_span: (start_col, end_col) that the per-row Total column sums."""
    ws.merge_cells(f"B{title_row}:F{title_row}")
    label(ws, f"B{title_row}", section_title)
    style_title(ws, f"B{title_row}")

    header_row = title_row + 1
    label(ws, f"B{header_row}", "#")
    label(ws, f"C{header_row}", "Module")
    for col, text in col_labels.items():
        label(ws, f"{col}{header_row}", text)
    style_header_row(ws, header_row, ["B", "C"] + list(col_labels.keys()))
    ws.row_dimensions[header_row].height = 20

    total_col = next(iter(col_labels))  # e.g. "F"
    start_col, end_col = total_span
    all_cols = ["B", "C"] + list(col_labels.keys())

    first_data_row = header_row + 1
    for i, meta in enumerate(metas):
        r = first_data_row + i
        band = PatternFill("solid", fgColor=BAND_TINT) if i % 2 == 1 else None
        ws[f"B{r}"] = i + 1
        ws[f"B{r}"].font = REGULAR
        ws[f"B{r}"].alignment = CENTER
        ws[f"C{r}"] = meta["title"]
        ws[f"C{r}"].font = REGULAR
        ws[f"C{r}"].alignment = LEFT_WRAP
        # Wrapped text needs an explicit height here -- the sheet sets a
        # defaultRowHeight, so Excel will not auto-grow the row for us.
        if len(str(meta["title"])) > 46:
            ws.row_dimensions[r].height = 30
        ws[f"{total_col}{r}"] = f"=SUM({start_col}{r}:{end_col}{r})"
        for col, fn in value_cols.items():
            ws[f"{col}{r}"] = fn(meta)
        for col in all_cols:
            cell = ws[f"{col}{r}"]
            if col not in ("B", "C"):
                cell.font = REGULAR
                cell.alignment = CENTER
            if band is not None:
                cell.fill = band

    total_row = first_data_row + len(metas)
    label(ws, f"B{total_row}", "Overall Total")
    # Only the Total column plus the numeric columns it sums get an
    # Overall Total -- descriptive columns (e.g. Assigned To, Milestone in
    # the Test Execution Summary table) don't, matching the source template.
    summable_cols = [total_col] + [
        chr(c) for c in range(ord(start_col), ord(end_col) + 1)
    ]
    for col in summable_cols:
        ws[f"{col}{total_row}"] = f"=SUM({col}{first_data_row}:{col}{total_row - 1})"
    for col in all_cols:
        cell = ws[f"{col}{total_row}"]
        cell.fill = TOTAL_FILL
        cell.font = BOLD
        if col != "B":
            cell.alignment = CENTER

    border_range(ws, header_row, total_row, all_cols)

    return total_row


def build_dashboard(wb, project_name, prepared_by, metas):
    ws = wb.create_sheet("Dashboard", 0)
    ws.sheet_view.showGridLines = False
    ws.sheet_format.defaultRowHeight = 18

    ws.merge_cells("B1:F1")
    label(ws, "B1", "Test Environment Configuration")
    style_title(ws, "B1")

    label(ws, "B2", "Project Name and Board Link", muted=True); ws["D2"] = project_name
    label(ws, "B3", "Prepared By", muted=True); ws["D3"] = prepared_by
    label(ws, "E3", "Executed By", muted=True); ws["F3"] = "-"
    label(ws, "B4", "Updated On", muted=True); ws["D4"] = "-"
    label(ws, "E4", "Executed On", muted=True); ws["F4"] = "-"
    label(ws, "B5", "Version No.", muted=True); ws["D5"] = "-"
    label(ws, "E5", "Test URL", muted=True); ws["F5"] = "-"
    label(ws, "B6", "Device OS", muted=True); ws["D6"] = "-"
    label(ws, "E6", "Browser Info.", muted=True); ws["F6"] = "-"
    for coord in ("D2", "D3", "D4", "D5", "D6", "F3", "F4", "F5", "F6"):
        ws[coord].font = REGULAR
    border_range(ws, 1, 6, ["B", "C", "D", "E", "F"])

    # Table 1: Test Execution Summary (includes Assigned To / Status / Est. / Milestone)
    t1_total = build_dashboard_table(
        ws, 9, "Test Execution Summary",
        {"F": "Total", "G": "Passed", "H": "Failed", "I": "Untested",
         "J": "Assigned To", "K": "Status", "L": "Est.", "M": "Milestone"},
        metas,
        {
            "G": lambda m: f"='{m['sheet_name']}'!$E$4",
            "H": lambda m: f"='{m['sheet_name']}'!$E$5",
            "I": lambda m: f"='{m['sheet_name']}'!$E$6",
            "J": lambda m: m["assigned_to"],
            "K": lambda m: m["status"],
            "L": lambda m: m["est_hours"],
            "M": lambda m: m["milestone"],
        },
        total_span=("G", "I"),
    )

    next_title = t1_total + 3
    t2_total = build_dashboard_table(
        ws, next_title, "Priority Wise Bugs",
        {"F": "Total", "G": "High", "H": "Medium", "I": "Low"},
        metas,
        {
            "G": lambda m: f"='{m['sheet_name']}'!$I$3",
            "H": lambda m: f"='{m['sheet_name']}'!$I$4",
            "I": lambda m: f"='{m['sheet_name']}'!$I$5",
        },
        total_span=("G", "I"),
    )

    next_title = t2_total + 3
    t3_total = build_dashboard_table(
        ws, next_title, "Type Wise Bugs",
        {"F": "Total", "G": "Functional", "H": "UI"},
        metas,
        {
            "G": lambda m: f"='{m['sheet_name']}'!$K$3",
            "H": lambda m: f"='{m['sheet_name']}'!$K$4",
        },
        total_span=("G", "H"),
    )

    next_title = t3_total + 3
    build_dashboard_table(
        ws, next_title, "Bug Fix Summary",
        {"F": "Total", "G": "Fixed", "H": "Not Fixed"},
        metas,
        {
            "G": lambda m: f"='{m['sheet_name']}'!$M$3",
            "H": lambda m: f"='{m['sheet_name']}'!$M$4",
        },
        total_span=("G", "H"),
    )

    for col, w in DASHBOARD_WIDTHS.items():
        ws.column_dimensions[col].width = w


def main():
    if len(sys.argv) != 3:
        print("Usage: python build_checklist.py <spec.json> <output.xlsx>")
        sys.exit(1)

    spec_path, out_path = sys.argv[1], sys.argv[2]
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    project_name = spec.get("project_name", "Savance Q3 Release Items")
    prepared_by = spec.get("prepared_by", "Enosis QA")
    start_index = spec.get("start_index", 1)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # drop the default blank sheet

    metas = []
    for i, feature in enumerate(spec["features"]):
        n = start_index + i
        meta = build_item_sheet(wb, n, feature, project_name)
        metas.append(meta)

    build_dashboard(wb, project_name, prepared_by, metas)

    wb.save(out_path)
    print(f"Wrote {out_path}: Dashboard + {len(metas)} sheet(s) "
          f"({', '.join(m['sheet_name'] for m in metas)})")
    for m in metas:
        print(f"  {m['sheet_name']}: {m['total']} check items - {m['title']}")


if __name__ == "__main__":
    main()
