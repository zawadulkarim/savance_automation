"""
Build a client-ready "Queries" docx from a JSON spec, matching the outline
style of the house reference doc (Misc Phase 2_ Queries from Enosis.pdf):

  Queries
  Main Task: <name>
  1. <Ticket name>
      a. <Question>?
          i. <Follow-up question>?
          ii. <Follow-up question>?
      b. <Question>?
  2. <Ticket name>
      a. ...

Usage:
    python build_queries_doc.py <spec.json> <output.docx>

Spec schema:
{
  "title": "Queries",                       // optional, defaults to "Queries"
  "sections": [
    {
      "heading": "Main Task: Q3 Release Items for Enosis",   // optional
      "tickets": [
        {
          "name": "(Support) Watchlist Issues (Enosis)",
          "url": "https://app.asana.com/...",                // optional
          "questions": [
            "Plain string question ending in a question mark?",
            {
              "text": "Question text?",
              "answer": "Answer the user supplied.",          // optional
              "followups": [                                  // optional
                "Follow-up a?",
                {"text": "Follow-up b?", "answer": "..."}
              ]
            }
          ]
        }
      ]
    }
  ]
}

Numbering restarts per scope: tickets restart at "1." for every section,
questions restart at "a." for every ticket, follow-ups restart at "i." for
every question — matching the reference doc exactly (confirmed by its own
"Queries: Other Items of..." section restarting at 1).

Design note: this deliberately does NOT use Word's native multilevel-list
numbering (numbering.xml abstractNum/num definitions). python-docx has no
high-level API for that, it would require raw OOXML surgery, and this
environment has no Word-COM/LibreOffice available to visually confirm the
result rendered correctly. Instead, labels ("1.", "a.", "i.") are written as
plain text at the front of a hanging-indent paragraph with a matching tab
stop. This looks identical to a native numbered list in the final document
and is trivial to verify by reading the paragraph text back — don't
"upgrade" this to real list numbering without a way to visually verify it.

An optional "answer" on a question or follow-up renders as an unnumbered,
italic "Answer: ..." line indented one level under it. It marks a point the
*user* resolved during analysis, so the client is never asked something the
team already settled internally — questions without an answer are the ones
still going out.

Inline "**bold**" markers in any question/ticket text render as bold runs —
use them to quote-and-bold specific UI element names (e.g. Ticket text or
question text containing `**"Manage Options"**`), matching the house
convention already used in the 8-asana-bug-report skill.
"""
import json
import sys

from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROMAN_VALUES = [
    (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
    (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
    (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
]


def int_to_roman(n):
    result = ""
    for val, sym in ROMAN_VALUES:
        while n >= val:
            result += sym
            n -= val
    return result


def index_to_letter(n):
    # 0 -> a, 1 -> b, ..., 25 -> z, 26 -> aa, 27 -> bb, ...
    if n < 26:
        return chr(ord("a") + n)
    return chr(ord("a") + (n // 26) - 1) * 2 + chr(ord("a") + (n % 26))


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


def render_inline(paragraph, text, bold_base=False):
    """Split on **bold** markers and add runs; bold_base ORs into every run."""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        run = paragraph.add_run(part)
        is_bold_span = (i % 2 == 1)
        run.bold = bold_base or is_bold_span


LEVEL_INDENT_STEP = Inches(0.4)
LEVEL_BASE_INDENT = Inches(0.3)
HANGING_INDENT = Inches(0.3)


def add_list_paragraph(doc, level, label, text, url=None, bold_label_text=False):
    p = doc.add_paragraph()
    left = LEVEL_BASE_INDENT + LEVEL_INDENT_STEP * level
    pf = p.paragraph_format
    pf.left_indent = left
    pf.first_line_indent = -HANGING_INDENT
    pf.space_after = Pt(6)
    p.paragraph_format.tab_stops.add_tab_stop(left)

    label_run = p.add_run(label + "\t")
    label_run.bold = True

    render_inline(p, text, bold_base=bold_label_text)

    if url:
        p.add_run("  ")
        add_hyperlink(p, url, "[ref]")

    return p


def add_answer_paragraph(doc, level, text):
    """Unnumbered italic 'Answer:' line, indented one level deeper than its
    question. Marks a point the user already resolved, so it is documented
    rather than sent to the client as an open query."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = LEVEL_BASE_INDENT + LEVEL_INDENT_STEP * (level + 1)
    pf.space_after = Pt(6)

    label_run = p.add_run("Answer: ")
    label_run.bold = True
    label_run.italic = True

    for part_idx, part in enumerate(text.split("**")):
        if not part:
            continue
        run = p.add_run(part)
        run.italic = True
        run.bold = (part_idx % 2 == 1)

    return p


def build(spec, output_path):
    doc = Document()
    doc.add_heading(spec.get("title", "Queries"), level=1)

    ticket_count = 0
    question_count = 0
    followup_count = 0
    answered_count = 0

    for section in spec.get("sections", []):
        heading = section.get("heading")
        if heading:
            doc.add_heading(heading, level=2)

        for t_idx, ticket in enumerate(section.get("tickets", []), start=1):
            ticket_count += 1
            add_list_paragraph(
                doc, level=0, label=f"{t_idx}.",
                text=ticket["name"], url=ticket.get("url"),
                bold_label_text=True,
            )

            for q_idx, question in enumerate(ticket.get("questions", [])):
                if isinstance(question, str):
                    question = {"text": question}
                question_count += 1
                letter = index_to_letter(q_idx)
                add_list_paragraph(
                    doc, level=1, label=f"{letter}.",
                    text=question["text"],
                )
                if question.get("answer"):
                    answered_count += 1
                    add_answer_paragraph(doc, level=1, text=question["answer"])

                for f_idx, followup in enumerate(question.get("followups", [])):
                    if isinstance(followup, str):
                        followup = {"text": followup}
                    followup_count += 1
                    roman = int_to_roman(f_idx + 1)
                    add_list_paragraph(
                        doc, level=2, label=f"{roman}.",
                        text=followup["text"],
                    )
                    if followup.get("answer"):
                        answered_count += 1
                        add_answer_paragraph(
                            doc, level=2, text=followup["answer"]
                        )

    doc.save(output_path)
    return {
        "sections": len(spec.get("sections", [])),
        "tickets": ticket_count,
        "questions": question_count,
        "followups": followup_count,
        "answered": answered_count,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python build_queries_doc.py <spec.json> <output.docx>")
        sys.exit(1)

    spec_path, output_path = sys.argv[1], sys.argv[2]
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    summary = build(spec, output_path)
    print(f"Wrote {output_path}")
    print(
        f"  sections: {summary['sections']}, tickets: {summary['tickets']}, "
        f"questions: {summary['questions']}, follow-ups: {summary['followups']}, "
        f"already answered: {summary['answered']}"
    )


if __name__ == "__main__":
    main()
