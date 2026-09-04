---
name: 4-checklist-generation
description: Generate a new QA checklist workbook in the house "Savance Q3 Release Items" template — Dashboard plus one sheet per feature/bug, Module -> Check Item hierarchy, roll-up formulas, dropdowns, colour-coded status. Normally derived from the approved "4 - Acceptance Criteria.md" (it checks that Review Status line and refuses an unapproved one); also takes the AC workbook, AC text, an Asana ticket, or a feature-list sheet. Use when asked to generate or create a QA or test checklist, or on /4-checklist-generation.
---

# Checklist generation

Produces a new Excel workbook that matches the exact structure of
`[Initial Checklist] Savance Q3 Release Items.xlsx` — a `Dashboard` sheet plus
one `#N` sheet per feature/bug, each holding a Module -> Check Item hierarchy
with live roll-up formulas, dropdowns, and conditional-format colors. This
skill always writes a **new, separate output file** — it never modifies the
original/master workbook. The user merges the generated sheet(s) into the
master file themselves when ready.
## Reference files

| File | Read it at |
| --- | --- |
| `reference/house-template.md` | Step 2 - the sheet layout, columns, formulas, dropdowns and status palette |
| `reference/build-and-verify.md` | Steps 3-5 - the JSON spec schema, the generator call, and the Excel-COM visual pass |

## Step 1 — Gather the input

The user will point you at one of:

1. **Approved acceptance criteria** from
   [[4-acceptance-criteria-generation]] — `4 - Acceptance Criteria.md` in the
   ticket folder, the richest input and the one the lifecycle feeds you. The
   house `[Acceptance Criteria] ...xlsx` workbook carries the same content and
   is still accepted, but the Markdown is the canonical copy, is a third of
   the tokens to read, and is the file that carries the human's approval. See
   "Deriving a checklist from acceptance criteria" below for the mapping.

   **The `Review Status` line is the entry condition.** Check it first:

   ```bash
   grep -m1 '^\*\*Review Status:\*\*' "<ticket folder>/4 - Acceptance Criteria.md"
   ```

   Derive a checklist only from `APPROVED — <reviewer>, <date>`. On `DRAFT` or
   `AWAITING HUMAN REVIEW`, say so and stop: the criteria may still change at
   the Stage 04 gate, and a checklist built from a superseded draft is worse
   than none, because it looks finished. The user may override — if they do,
   say plainly at handoff that the checklist rests on unapproved criteria.
2. **Acceptance criteria text** — pasted directly or described in chat.
3. **An Asana ticket** — resolve it with the Asana MCP tools
   (`asana_get_task`, etc.) to pull the title and description/AC list.
4. **A feature-list spreadsheet** — an existing `.xlsx` with one row per
   feature/bug to expand (e.g. a "backlog" sheet shaped like the Dashboard's
   Test Execution Summary table). Read it with a small Python/openpyxl
   script the same way you'd inspect any `.xlsx` — the Read tool cannot open
   binary Excel files directly. **Process every row in one run** — generate
   one full `#N` sheet per feature in the batch, not one at a time, unless
   the user asks you to scope it down.

If the acceptance criteria / ticket / spreadsheet row doesn't already break
cleanly into modules and atomic check items, ask the user rather than
guessing at scope — getting the module grouping wrong produces a checklist
that reads as sloppy to whoever executes it.

### Deriving a checklist from acceptance criteria

**From `4 - Acceptance Criteria.md`** (the normal case): one
`### AC<id> — <module>` block per AC row, each with its description, its
numbered **Acceptance Rules**, its **Expected System Behavior** and its notes,
plus a per-sheet index table and a counts table. Read it with the Read tool —
one call, no script, and the module name is repeated on every block heading
rather than hidden in a merge.

**From the `.xlsx`** (an older run, or a client-supplied sheet): the same
columns — `ID | Module | Description | Acceptance Rules | Expected System
Behavior | Notes` — with the `Module` column merged over each block. Read it
with openpyxl, and note that a merged `Module` cell means only the **first**
row of each block carries the value, so carry it forward as you walk the rows.
Prefer the Markdown when both exist, and say which you used.

The mapping:

- **One acceptance rule → one check item.** Both are single atomic
  assertions, so this is largely mechanical: `The system must display the
  "Agreement checkbox" in an unchecked and disabled state by default.`
  becomes `Verify that the "Agreement checkbox" is displayed unchecked and
  disabled by default.` Reword from the requirement voice (`must`) into the
  checklist's imperative voice (`Verify`/`Validate`/`Confirm`), don't
  paste the rule verbatim.
- **The AC `Module` column becomes the checklist module**, unchanged — the
  grouping was already decided upstream, so don't re-derive it.
- **A rule spanning several surfaces splits** into one check item per surface,
  per the atomicity rule above.
- **Rows with empty `Acceptance Rules`** are deliberate markers, not gaps to
  fill: either explicitly-not-being-tested items or `[Needs domain
  knowledge]` rows. Carry them across as a single placeholder check item
  keeping the reason visible — never silently drop them and never invent
  rules to replace them.
- **`Expected System Behavior` is not a check item.** It's a summary of the
  rules' combined outcome; turning it into its own row duplicates coverage.

Reference AC workbooks average **3.8 acceptance rules per AC row**, so a
12-row AC sheet lands around 40-50 check items for a full **regression**
checklist. For **sanity**, keep happy-path and key-validation rules and drop
the pure edge-case ones. Compute and report the actual check-items-per-rule
ratio at handoff — a ratio far below 1.0 means rules were dropped, far above
1.0 means surfaces were split out (legitimate) or coverage was invented
(not).

This mapping is derived from the reference workbooks' rule counts; it has
**not** been calibrated against an accepted AC-plus-checklist pair for the
same feature. If one turns up, measure it and tighten this section.

**"Sanity" vs "regression" is a real, distinct vocabulary on this team** (seen
in a reference sheet that literally tracks "# of Checklist Items for
Regression Testing" separately from "...for Sanity Testing"). If the user
asks for a **sanity checklist**, that means core-feature/happy-path coverage
plus key validation gates only — not the exhaustive edge-case matrix a full
**regression** checklist would carry (blank/max-length/whitespace/special-
character variants of every field, every cross-surface repetition, etc.).
Confirm which one is wanted if it's ambiguous; don't default to full
exhaustive coverage when "sanity" was asked for, and don't quietly thin out
a "regression" or unqualified request either.

**Sizing a sanity checklist from a per-app domain doc** (the `SwMobile.xlsx` /
`SwServerDomain.xlsx` / `SW WorkplaceDomain.xlsx` shape — one row per feature
sub-item under `Module:` banner rows): the accepted deliverables land at
**~0.9-1.35 check items per source sub-item row** (SwMobile 148/110 = 1.35,
SwServer 129/142 = 0.91, Emergency Mustering 127/147 = 0.86, SwWeb 374/326 =
1.15). So roughly *one check item per source row* is the house calibration for
sanity, not a heavy reduction from it — some rows collapse (a row listing five
fields becomes one check) while others split (a row describing a modal becomes
four). If a draft is landing far below ~0.85, it's being thinned too
aggressively; far above ~1.4 and it's drifting into regression. Compute the
ratio and check it before handing off.

**Source specs are sometimes incomplete or duplicated — handle deliberately,
don't silently drop or duplicate:**
- If a source describes a feature/section that needs specialist or hardware
  domain knowledge you don't have (e.g. COM-port wiring, badge-reader
  validation, batch-query tuning), **don't skip it entirely**. Keep it as its
  own row with a placeholder check item instead, so nothing disappears
  from view: `[Needs domain knowledge] <topic> - <what it does>; requires
  domain knowledge to define a concrete check.` Status still defaults to
  `Untested` like every other row — this makes the gap visible and trackable
  rather than invisible.
- If the same feature is documented twice in the source (verbatim or
  near-verbatim, e.g. the same settings screen described under two different
  section headers), write it into the checklist once and say so — don't
  silently duplicate check items, and don't silently drop the duplicate
  without mentioning it either.
- If asked to expand coverage on a topic (e.g. "add more about X") **and**
  the source spec doesn't actually describe the deeper behavior being asked
  about, ask the user whether to (a) stay strictly grounded in what the
  source already says (splitting/rephrasing existing content, not inventing
  new claims), or (b) also write check items for plausible runtime behavior
  the source never mentions. Don't silently invent product behavior and
  present it as derived from the spec — the user should know which parts
  are sourced vs. inferred, and picked exactly which inferred scenarios to
  include (or gave them to you directly) rather than you guessing.

## Step 2 — Structure the content

For each feature, derive:

- **Modules**: the distinct screens/areas/components the feature touches
  (e.g. `"Web: Question Manager"`, `"Kiosk App"`, `"Web: Status Board"`).
  Group check items under the module they exercise, in the order a tester
  would naturally walk through them (configure the feature first, then
  exercise it end-to-end, then verify downstream effects like Status Board).
- **Check items**: atomic, testable, imperative statements. Cover the happy
  path, then validation/edge cases (blank input, max length, special
  characters, whitespace), then cross-surface consistency (does this show up
  identically across every place it's relevant — Web, Kiosk, Outlook Add-in,
  Status Board, etc., mirroring how the source checklist repeats the same
  check per surface rather than folding surfaces into one row).

## Steps 3-5 - Build and verify

-> `reference/build-and-verify.md` for the spec schema, the generator call and
the visual pass.

```bash
python .claude/skills/4-checklist-generation/scripts/build_checklist.py <spec.json> <output.xlsx>
```

**The visual pass is not optional and a numeric re-read does not replace it.**
openpyxl proves the data landed; only looking at an exported PNG proves the
workbook renders - a `dxf` fill written the static way round-trips through a
re-read and still shows no fill in Excel.

## Step 6 — Hand off and deliver to Google Drive

**The canonical copy stays in the ticket folder**, at
`tickets/<ticket-id> - <Ticket name>/5 - QA Checklist.xlsx`, alongside the
acceptance criteria it was derived from. It is written there first and never
moved out; the Google Drive copy below is an additional delivery, not a
relocation.

Tell the user that path and a one-line summary of what's in it
(feature count, total check items). Remind them this is a standalone file to
be merged into the master workbook, not an in-place edit — they may want to
copy the generated `#N` sheet(s) into the master file and add matching rows
to its Dashboard themselves, or ask you to do that copy step explicitly if
they want it done for them.

**Once the workbook is finished and approved (or immediately, for a
straightforward regenerate), copy the final file into the shared Google
Drive review folder:**

```
G:\My Drive\savance_review_task
```

This is a Google Drive Desktop sync mount already set up on this machine —
a plain file copy (`cp`, or `Copy-Item` in PowerShell) is enough; the Drive
Desktop client uploads it to the cloud in the background on its own, and
that background sync isn't something this skill can observe or confirm
directly. There is no Google Drive MCP connector available in this
environment, so this local sync-folder copy is the only automated delivery
path — don't attempt to invent an API/OAuth upload. If that exact path
doesn't exist or isn't reachable when you check, don't guess at a
substitute — tell the user and ask where the file should go instead, the
same way a locked/in-use destination filename gets a versioned fallback
(`(v2)`, `(v3)`, ...) with a note to the user rather than a silent failure.
