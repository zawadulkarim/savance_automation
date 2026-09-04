"""
Build a "Feature Spec & Test Scope" docx from a JSON spec.

This is the Stage 02 deliverable: a short, plain-language document that tells a
reader who has NOT followed the ticket what is changing, what QA will test, and
what QA will not test and why.

Three sections and nothing more. There is deliberately no affected-apps table,
no today/after workflow table and no environments/navigation/prerequisites
section -- the affected apps appear inside the scope items, and how to reach a
screen is Stage 05's job. See "What this document deliberately does not
contain" in the skill.

Deliberately high-level. It is not a design doc and not a test-case list --
detailed cases come later, from 4-acceptance-criteria-generation and
5-test-case-generation.

Usage:
    python build_spec_doc.py <spec.json> <output.docx>

Spec schema (sections optional -- an omitted or empty one is skipped, so a
provisional spec can be generated before every section is filled in):
{
  "title": "Feature Spec & Test Scope",         // optional, this is the default
  "ticket": {                                    // optional
    "name": "(Support) Watchlist Issues (Enosis)",
    "id": "1210439317493381",
    "url": "https://app.asana.com/..."
  },
  "provisional": "Queries 3 and 5 unanswered — user approved proceeding.",
                                                 // optional; renders a warning banner
  "summary": ["What is changing, one plain sentence per bullet."],
  "scope": {
    "in":  ["What QA will test.",
            "Kiosk sign-in — shares the visitor status service."],
    "out": ["What QA will not test, and why."]
  },
  "open_items": ["Anything still unanswered, assumed, or overridden."]
                                                 // optional, renders unnumbered
}

Inline "**bold**" markers render as bold runs anywhere in the document — use
them to quote-and-bold specific UI element names, matching the house
convention shared with 8-asana-bug-report and requirement-analysis.
"""
import json
import sys

from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT


def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rpr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rpr.append(underline)
    run.append(rpr)

    text_el = OxmlElement("w:t")
    text_el.text = text
    run.append(text_el)

    hyperlink.append(run)
    paragraph._p.append(hyperlink)
    return hyperlink


def render_inline(paragraph, text, bold_base=False, italic=False):
    """Split on **bold** markers and add runs."""
    for idx, part in enumerate(str(text).split("**")):
        if not part:
            continue
        run = paragraph.add_run(part)
        run.bold = bold_base or (idx % 2 == 1)
        run.italic = italic


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        render_inline(p, item)
        p.paragraph_format.space_after = Pt(4)


def add_section(doc, heading, items):
    doc.add_heading(heading, level=2)
    add_bullets(doc, items)


def build(spec, output_path):
    doc = Document()
    rendered = []

    doc.add_heading(spec.get("title", "Feature Spec & Test Scope"), level=1)

    ticket = spec.get("ticket") or {}
    if ticket.get("name"):
        p = doc.add_paragraph()
        render_inline(p, ticket["name"], bold_base=True)
        if ticket.get("id"):
            p.add_run(f"  (ID {ticket['id']})")
        if ticket.get("url"):
            p.add_run("  ")
            add_hyperlink(p, ticket["url"], "[ref]")

    if spec.get("provisional"):
        p = doc.add_paragraph()
        warn = p.add_run("PROVISIONAL — ")
        warn.bold = True
        warn.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
        render_inline(p, spec["provisional"], italic=True)

    summary = spec.get("summary") or []
    if summary:
        add_section(doc, "1. What is changing", summary)
        rendered.append("summary")

    scope = spec.get("scope") or {}
    scope_in = scope.get("in") or []
    scope_out = scope.get("out") or []

    if scope_in:
        add_section(doc, "2. What we will test", scope_in)
        rendered.append("scope_in")

    if scope_out:
        add_section(doc, "3. What we will not test", scope_out)
        rendered.append("scope_out")

    # Unnumbered and optional: present only when something is genuinely open.
    open_items = spec.get("open_items") or []
    if open_items:
        add_section(doc, "Open items and assumptions", open_items)
        rendered.append("open_items")

    doc.save(output_path)
    return {
        "sections": rendered,
        "missing": [s for s in ["summary", "scope_in", "scope_out"]
                    if s not in rendered],
        "summary_points": len(summary),
        "in_scope": len(scope_in),
        "out_scope": len(scope_out),
        "open_items": len(open_items),
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python build_spec_doc.py <spec.json> <output.docx>")
        sys.exit(1)

    spec_path, output_path = sys.argv[1], sys.argv[2]
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    s = build(spec, output_path)
    numbered = [x for x in s["sections"] if x != "open_items"]
    print(f"Wrote {output_path}")
    print(f"  sections: {len(numbered)}/3 ({', '.join(numbered) or 'none'})")
    print(
        f"  what is changing: {s['summary_points']}, "
        f"will test: {s['in_scope']}, will not test: {s['out_scope']}, "
        f"open items: {s['open_items']}"
    )
    if s["missing"]:
        print(f"  WARNING - empty sections skipped: {', '.join(s['missing'])}")


if __name__ == "__main__":
    main()
