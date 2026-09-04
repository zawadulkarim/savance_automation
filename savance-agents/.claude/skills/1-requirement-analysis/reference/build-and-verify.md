# Building and verifying the queries docx

Referenced from `SKILL.md` Steps 11-13. Read this **only after** the user has
approved the question list at Step 10 - the document is written nowhere else.

## Contents
- The JSON spec schema
- The generator invocation and output path
- Structural verification (there is no Word COM here, so no visual pass)

## Step 11 — Build the JSON spec

```json
{
  "title": "Queries",
  "sections": [
    {
      "heading": "Main Task: Q3 Release Items for Enosis",
      "tickets": [
        {
          "name": "(Support) Watchlist Issues (Enosis)",
          "url": "https://app.asana.com/1/36351424181263/project/1215927039992328/task/1210439317493381",
          "questions": [
            "Plain string question — shorthand for {\"text\": ...}?",
            {
              "text": "A question the user already answered?",
              "answer": "Recorded answer from the user — renders as an italic Answer: line."
            },
            {
              "text": "A question with compound facets?",
              "followups": [
                "First facet?",
                {"text": "Second facet?", "answer": "Answered facet."}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

One `sections` entry per Main Task processed in this run (a lone ticket with
no parent is one section with one ticket). Numbering restarts automatically:
tickets at `1.` per section, questions at `a.` per ticket, follow-ups at `i.`
per question. `url` is optional and renders as a small `[ref]` hyperlink back
to the Asana task. `answer` is optional, valid on both questions and
follow-ups, and marks a point the **user** resolved during Step 8.

## Step 12 — Generate the docx

```bash
python .claude/skills/1-requirement-analysis/scripts/build_queries_doc.py <spec.json> <output.docx>
```

Requires `python-docx` (`pip install python-docx` once if missing — not
preinstalled in this environment as of this writing).

**Output location.** Every QA-lifecycle artefact for a ticket lives together
in one folder for that ticket, under a top-level `tickets/` folder in the
project root, each file named for the stage that produced it:

```
tickets/<ticket-id> - <Ticket name>/
    1 - Requirement Analysis.docx        <- stage 1
    2 - Spec Document.docx               <- stage 2
    4 - Acceptance Criteria.md           <- stage 4, canonical
```

This stage writes `1 - Requirement Analysis.docx`.

- `<ticket-id>` is the Asana task gid — the parent's gid for a Main Task
  batch, the ticket's own gid for a single ticket. **The gid is the stable
  key**: to find an existing ticket folder, glob `tickets/<ticket-id> - */`
  rather than trying to reconstruct the name.
- `<Ticket name>` is there for humans, so sanitize it for the filesystem —
  replace `\ / : * ? " < > |` with `-`, collapse runs of whitespace, strip
  trailing dots and spaces, and cap it at about 80 characters.
- Create the folder if it isn't there; every later stage reuses the same one.
- **Never overwrite a previous round.** If the file already exists, write
  `... (rev 2).docx` alongside it.

The script deliberately does **not** use Word's native multilevel-list
numbering (`numbering.xml` abstractNum/num definitions) — `python-docx` has no
high-level API for it, it would need raw OOXML surgery, and this environment
has no Word-COM (`pywin32`) or LibreOffice (`soffice`) to visually confirm
such XML rendered correctly. Every `1./a./i.` label is instead plain text at
the front of a hanging-indent paragraph with a matching tab stop — visually
indistinguishable in the output, and trivially verifiable by reading the
paragraph text back. Don't "upgrade" this without a way to see the result.

## Step 13 — Verify structurally, not visually

There is no way to render a `.docx` to an image here (no Word-COM, no
LibreOffice), so unlike `4-checklist-generation`'s Excel visual pass, this is a
structural check. Reopen the file and dump every paragraph before handing it
off:

```python
from docx import Document
doc = Document("<output.docx>")
for p in doc.paragraphs:
    print(p.paragraph_format.left_indent, "".join(r.text for r in p.runs))
```

Confirm from the dump: numbering restarts correctly per section/ticket/
question, every question ends in `?`, answer lines sit under the right
questions, bolded spans landed on the intended UI-element names, and nothing
was dropped or duplicated across the batch.
