#!/usr/bin/env python3
"""
Render the human-review copy of the acceptance criteria --
"4 - Acceptance Criteria.md" -- from the same JSON spec that
build_ac_workbook.py turns into the .xlsx.

One spec, two renderers, on purpose. The Markdown is what the human reviewer
reads and approves at the Stage 04 gate; the workbook is built from the same
spec only *after* that approval. If the two were authored separately they
could drift, and an approval that does not bind the delivered workbook is
worth nothing.

So: this script never invents content, and neither renderer is allowed to
compute an AC ID the other would not. The ID scheme below is duplicated from
build_ac_workbook.py deliberately (this script must run with no openpyxl
installed); if you change it in one place, change it in both.

Usage:
    python build_ac_markdown.py <spec.json> <output.md> [--status "<text>"]

`--status` (or the spec's "review_status" key, default "DRAFT") fills the
**Review Status:** line every downstream stage greps for. Legal values:

    DRAFT
    AWAITING HUMAN REVIEW
    APPROVED - <reviewer>, <YYYY-MM-DD>

Never write APPROVED without a human having actually said so -- Stage 05 and
Stage 07 both read that line as the human's signature.

See ../SKILL.md for the spec schema and the review flow.
"""
import sys
import json


# --- keep in step with build_ac_workbook.py ----------------------------------

def ac_id(item, sheet_index, seq):
    """AC{sheet index}{seq:03d}, or the row's explicit `id` override.

    Identical to the workbook builder's rule. The IDs are the traceability
    keys Stage 05 quotes in its matrix, so a mismatch between the two renderers
    would break traceability silently.
    """
    return item.get("id") or f"AC{sheet_index}{seq:03d}"


def numbered(value):
    """A list renders as "1. ..\n2. ..", a string passes through as prose --
    matching the workbook's `numbered()` so a single-rule cell still reads
    "1. ..." in both artefacts."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    items = [str(v).strip() for v in value if str(v).strip()]
    if not items:
        return None
    return "\n".join(f"{i}. {text}" for i, text in enumerate(items, 1))


def group_of(item):
    return item.get("module") or item.get("application") or item.get("group") or "-"


# --- rendering ---------------------------------------------------------------

def flatten(text):
    """Collapse the embedded newlines a stacked group name carries ("Question
    Manager\\nVMSuite App") so it stays on one line in a heading or a table
    cell."""
    if text is None:
        return ""
    return " / ".join(part.strip() for part in str(text).split("\n") if part.strip())


def cell(text):
    """Escape a value for a Markdown table cell."""
    return flatten(text).replace("|", "\\|")


def block(lines, value, prefix=""):
    """Append a possibly-multiline value as its own paragraph."""
    if not value:
        return
    for line in str(value).split("\n"):
        lines.append(f"{prefix}{line}")
    lines.append("")


def render_sheet(lines, spec, sheet_spec, sheet_index, sheet_label):
    criteria = sheet_spec.get("criteria", []) or []
    rows = []
    for seq, item in enumerate(criteria, start=1):
        rows.append((ac_id(item, sheet_index, seq), item))

    main_task = sheet_spec.get("main_task") or sheet_label
    lines.append(f"## {sheet_label} — {flatten(main_task)}")
    lines.append("")
    if sheet_spec.get("sub_task"):
        lines.append(f"**Sub Task:** {flatten(sheet_spec['sub_task'])}")
    if sheet_spec.get("application_name") or spec.get("application_name"):
        lines.append(
            "**Application:** "
            f"{flatten(sheet_spec.get('application_name') or spec.get('application_name'))}")
    if sheet_spec.get("assigned"):
        lines.append(f"**Assigned:** {flatten(sheet_spec['assigned'])}")
    if sheet_spec.get("url"):
        lines.append(f"**Ticket:** {sheet_spec['url']}")
    lines.append("")

    # At-a-glance index. The reviewer's first pass is "is anything missing?",
    # which is a scan of IDs and descriptions -- not a read of every rule.
    lines.append("| ID | Module | Description | Rules |")
    lines.append("|---|---|---|---|")
    for ac, item in rows:
        rules = item.get("rules") or []
        count = len(rules) if isinstance(rules, list) else 1
        flag = "**0 — gap**" if count == 0 else str(count)
        lines.append(
            f"| {ac} | {cell(group_of(item))} | {cell(item.get('description'))} | {flag} |")
    lines.append("")

    for ac, item in rows:
        lines.append(f"### {ac} — {flatten(group_of(item))}")
        lines.append("")
        block(lines, item.get("description"))

        rules = numbered(item.get("rules"))
        if rules:
            lines.append("**Acceptance Rules**")
            lines.append("")
            block(lines, rules)
        else:
            # An empty `rules` list is the house convention for a visible gap
            # (not tested by decision, or needs domain knowledge). It must
            # read as a gap, not as an oversight.
            lines.append("**Acceptance Rules:** *none — see Description for why "
                         "this row carries no rules.*")
            lines.append("")

        expected = numbered(item.get("expected"))
        if expected:
            lines.append("**Expected System Behavior**")
            lines.append("")
            block(lines, expected)

        if item.get("task"):
            lines.append(f"**Task:** {flatten(item['task'])}")
            lines.append("")
        if item.get("notes"):
            lines.append(f"**Notes:** {flatten(item['notes'])}")
            lines.append("")

    return len(rows), sum(
        len(item.get("rules") or []) if isinstance(item.get("rules"), list)
        else (1 if item.get("rules") else 0)
        for _, item in rows)


def render(spec, status):
    lines = []
    project = spec.get("project_name", "-")
    lines.append(f"# Acceptance Criteria — {flatten(project)}")
    lines.append("")
    lines.append(f"**Review Status:** {status}")
    lines.append(f"**Application:** {flatten(spec.get('application_name', '-'))}")
    lines.append(f"**Prepared By:** {flatten(spec.get('prepared_by', 'Enosis QA'))}")
    lines.append(f"**Last Updated:** {flatten(spec.get('last_updated', '-'))}")
    lines.append("")
    lines.append("<!-- Rendered by build_ac_markdown.py from the Stage 04 JSON spec. "
                 "Fix the spec and re-render; do not hand-edit this file. -->")
    lines.append("")

    layout = spec.get("layout", "per_ticket")
    sheets = spec.get("tickets") or spec.get("sheets")

    totals = []
    if layout == "per_ticket":
        start_index = spec.get("start_index", 1)
        for i, sheet_spec in enumerate(sheets):
            n = start_index + i
            label = sheet_spec.get("sheet_name", f"#{n}")
            totals.append((label, *render_sheet(lines, spec, sheet_spec, n, label)))
    else:
        for i, sheet_spec in enumerate(sheets, start=1):
            label = sheet_spec.get("sheet_name") or project
            totals.append((label, *render_sheet(lines, spec, sheet_spec, i, label)))

    coverage = spec.get("spec_coverage")
    if coverage:
        lines.append("## Spec Coverage")
        lines.append("")
        lines.append("| Spec in-scope item | Acceptance Criteria | Status | Notes |")
        lines.append("|---|---|---|---|")
        for row in coverage:
            acs = row.get("acs") or []
            lines.append(
                f"| {cell(row.get('item'))} | {cell(', '.join(acs)) or '—'} "
                f"| {cell(row.get('status', ''))} | {cell(row.get('notes', ''))} |")
        lines.append("")

    questions = spec.get("open_questions")
    if questions:
        lines.append("## Open Questions / Assumptions")
        lines.append("")
        for q in questions:
            lines.append(f"- {flatten(q)}")
        lines.append("")

    lines.append("## Counts")
    lines.append("")
    lines.append("| Sheet | AC rows | Acceptance rules | Rules/row |")
    lines.append("|---|---|---|---|")
    for label, rows, rules in totals:
        ratio = (rules / rows) if rows else 0
        lines.append(f"| {cell(label)} | {rows} | {rules} | {ratio:.2f} |")
    all_rows = sum(t[1] for t in totals)
    all_rules = sum(t[2] for t in totals)
    ratio = (all_rules / all_rows) if all_rows else 0
    lines.append(f"| **Total** | **{all_rows}** | **{all_rules}** | **{ratio:.2f}** |")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n", totals, all_rows, all_rules, ratio


def main():
    argv = [a for a in sys.argv[1:]]
    status = None
    positional = []
    i = 0
    while i < len(argv):
        if argv[i] == "--status":
            if i + 1 >= len(argv):
                print("--status needs a value")
                sys.exit(1)
            status = argv[i + 1]
            i += 2
            continue
        if argv[i].startswith("--status="):
            status = argv[i].split("=", 1)[1]
            i += 1
            continue
        positional.append(argv[i])
        i += 1

    if len(positional) != 2:
        print('Usage: python build_ac_markdown.py <spec.json> <output.md> '
              '[--status "<text>"]')
        sys.exit(1)

    spec_path, out_path = positional
    # utf-8-sig, not utf-8: anything written by PowerShell 5.1's Set-Content
    # -Encoding utf8 / Out-File carries a BOM that plain utf-8 json.load
    # rejects outright. Same trap as build_ac_workbook.py.
    with open(spec_path, "r", encoding="utf-8-sig") as f:
        spec = json.load(f)

    # The same two invariants the workbook builder enforces, so a spec can
    # never render as Markdown and then fail at the .xlsx step -- the human
    # would have approved something that cannot be delivered.
    layout = spec.get("layout", "per_ticket")
    if layout not in ("per_ticket", "single_sheet"):
        print(f"Unknown layout {layout!r}: use 'per_ticket' or 'single_sheet'")
        sys.exit(1)
    if not (spec.get("tickets") or spec.get("sheets")):
        print("Spec has no 'tickets' (per_ticket) / 'sheets' (single_sheet) entries")
        sys.exit(1)

    status = status or spec.get("review_status", "DRAFT")

    text, totals, all_rows, all_rules, ratio = render(spec, status)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

    print(f"Wrote {out_path}: {len(totals)} section(s) | {all_rows} AC rows, "
          f"{all_rules} acceptance rules ({ratio:.2f} rules/row)")
    print(f"  Review Status: {status}")
    for label, rows, rules in totals:
        per = (rules / rows) if rows else 0
        print(f"  {label}: {rows} AC rows, {rules} rules ({per:.2f} rules/row)")
    gaps = 0
    for sheet_spec in (spec.get("tickets") or spec.get("sheets")):
        for item in sheet_spec.get("criteria", []) or []:
            rules = item.get("rules")
            if isinstance(rules, list) and not rules:
                gaps += 1
    if gaps:
        print(f"  {gaps} row(s) with no acceptance rules (visible gaps)")


if __name__ == "__main__":
    main()
