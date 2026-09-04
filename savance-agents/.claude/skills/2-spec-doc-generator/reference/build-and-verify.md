# Building and verifying the spec docx

Referenced from `SKILL.md` Steps 10-12. Read this **only after** the user has
approved at Step 7 - nothing here applies before the gate.

## Contents
- The JSON spec schema
- The generator invocation and output path
- Structural verification (there is no Word COM here, so no visual pass)

## Step 8 — Build the JSON spec

```json
{
  "title": "Feature Spec & Test Scope",
  "ticket": {"name": "...", "id": "1210439317493381", "url": "https://app.asana.com/..."},
  "provisional": "Queries 3 and 5 unanswered — user approved proceeding.",
  "summary": ["Plain sentence about what changes."],
  "scope": {
    "in":  ["What QA will test.", "Kiosk sign-in — shares the visitor status service."],
    "out": ["Email templates — unchanged by this ticket."]
  },
  "open_items": ["..."]
}
```

That is the whole schema. There is **no `apps`, `workflow` or `where` field** —
those sections were removed from the document on purpose (`SKILL.md` hard rule
3), and the affected apps live inside `scope.in` items instead. If you find
yourself wanting one of them back, re-read *What this document deliberately
does not contain* in `SKILL.md`.

`summary`, `scope.in` and `scope.out` are the three rendered sections; the
generator prints a `WARNING - empty sections skipped` line naming any that came
through empty, and a skipped section must be explained in the hand-off.

`open_items` is genuinely optional and renders unnumbered — an empty one is
normal for a fully-answered spec and raises no warning. `provisional` renders a
red banner under the title; omit it entirely for a fully-answered spec.

Inline `**bold**` markers render as bold runs anywhere in the document — use
them for the house UI-element convention, `**"Manage Options"**`.

## Step 9 — Generate the docx

```bash
python .claude/skills/2-spec-doc-generator/scripts/build_spec_doc.py <spec.json> <output.docx>
```

Requires `python-docx` (`pip install python-docx` once if missing).

**Output location.** Into the **same ticket folder** Stage 01 already
created — every stage's artefacts for a ticket live together, each file named
for the stage that produced it:

```
tickets/<ticket-id> - <Ticket name>/
    1 - Requirement Analysis.docx        <- stage 1
    2 - Spec Document.docx               <- stage 2
    4 - Acceptance Criteria.md           <- stage 4, canonical
```

This stage writes `2 - Spec Document.docx`, alongside the requirement analysis
rather than in a folder of its own. Locate the ticket folder by globbing `tickets/<ticket-id> - */` — the Asana
gid is the stable key; don't try to reconstruct the name. Create the folder if
Stage 01 never ran. If a spec for that ticket already exists, write
`2 - Spec Document (rev 2).docx` alongside it — never overwrite an earlier
round.

## Step 10 — Verify structurally

There is no way to render a `.docx` to an image here (no Word-COM, no
LibreOffice), so verify structurally. Reopen the file and walk the body in
document order:

```python
import sys
from docx import Document
from docx.text.paragraph import Paragraph

doc = Document("<output.docx>")
for child in doc.element.body.iterchildren():
    if child.tag.endswith("}p"):
        p = Paragraph(child, doc)
        text = "".join(r.text for r in p.runs)
        if text.strip():
            print(f"[{p.style.name}] {text}")
```

The document is now all headings and bullets, so there is no table to walk.
Confirm from the dump:

- All three numbered sections present — `1. What is changing`,
  `2. What we will test`, `3. What we will not test` — or a skipped one
  explained in the hand-off.
- **No fourth numbered section**, and no table anywhere. Either means content
  crept back in that hard rule 3 excludes.
- Every out-of-scope bullet carries its reason.
- Bolded spans landed on the intended UI element names.
- The provisional banner is present exactly when it should be, and the
  unnumbered `Open items and assumptions` section is present exactly when
  there are open items.
