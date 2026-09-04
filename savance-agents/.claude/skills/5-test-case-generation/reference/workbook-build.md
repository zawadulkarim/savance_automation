# Building and verifying test-cases.xlsx

Referenced from `SKILL.md` Steps 11-12. Read this **only after** the human has
approved `test-cases.md` — nothing here applies before the gate.

## Contents
- The generator invocation and JSON spec schema
- Output path and the Git Bash path gotcha
- Structural verification (the counts the script prints)
- Visual verification via Excel COM
- Sharp edges already hit and fixed in the generator
- Sizing heuristic (uncalibrated)

## Build

**Only after the human approval at Step 9**, and from the approved Markdown.

Build the JSON spec from `test-cases.md` — the case IDs, titles and step
counts must match it one for one, and the workbook's printed counts are how
you check that — then:

```bash
python .claude/skills/5-test-case-generation/scripts/build_test_cases_workbook.py <spec.json> <output.xlsx>
```

```json
{
  "project_name": "Savance Q3 Release Items",
  "application_name": "Savance Workplace Browser Interface, Kiosk",
  "prepared_by": "Enosis QA",
  "last_updated": "2026-09-02",
  "feature": "Prevent visitors from checking in to hosts who are out",
  "main_task": "Toyoda Gosei Feature Request (Enosis)",
  "sub_task": "",
  "traceability_sheet": true,
  "test_cases": [
    {
      "id": "TC-001",
      "title": "Host with \"Out\" status cannot be selected on the Kiosk",
      "ac": "AC2003 r2",
      "ticket": "Toyoda Gosei Feature Request (Enosis)",
      "type": "Functional / Positive",
      "priority": "High",
      "preconditions": ["\"Prevent Out Status Type Host Selection\" is enabled."],
      "test_data": ["Host: \"QA Host 01\", status \"Out\""],
      "steps": [
        {"action": "Navigate to the Login page.", "expected": "The Login page loads."},
        {"action": "Enter credentials and click \"Log In\".", "expected": "Redirected to the Home page."},
        {"action": "Open the Kiosk app and tap \"Sign In\".", "expected": "The host list is displayed."}
      ],
      "expected_results": ["The out-status host is greyed out and unselectable."],
      "postconditions": ["None."],
      "automation": "Yes",
      "playwright_verified": "Yes",
      "remarks": ""
    }
  ],
  "traceability": [
    {"ac": "AC2003", "cases": ["TC-001", "TC-002"], "coverage": "Covered", "notes": ""}
  ]
}
```

Steps explode to one row each; the script repeats the categorical columns on
every step row so the filters stay correct, and writes the tall narrative
columns (`Preconditions`, `Test Data`, `Postconditions`, `Remarks`) on the first
row of each case only. `Reviewer Status` is left **blank** with a dropdown — it
is the human reviewer's column, and prefilling it would fake their input. Put
anything they need to know in `remarks` instead.

`ticket` is a categorical column, same scope as `ac`/`type`/`priority` — it
repeats on every step row of a case so filtering by Ticket returns whole cases.
In a single-ticket run every case's `ticket` is the same string; in a batch
folder covering several client tickets it is what lets a reviewer filter the
sheet down to one underlying ticket's cases. It is required in the spec — the
generator fails loudly (see Sharp edges below) if a case has no `ticket`, the
same way it already does for a missing `ac`.

**Output:** `tickets/<ticket-id> - <Ticket name>/test-cases.xlsx`. Never
overwrite an earlier round; add `(rev 2)`.

**Path gotcha (Bash tool = Git Bash/MSYS):** MSYS translates POSIX-looking paths
only for standalone argv tokens. A path interpolated inside a longer string
(`python -c "...open('$SCRATCH/x.json')..."`) is **not** translated and native
Windows Python will not find it. Pass paths as their own arguments, or write a
throwaway `.py` and pass the path via `sys.argv`.

Spec files are read as `utf-8-sig` — anything written by PowerShell 5.1's
`Set-Content -Encoding utf8` carries a BOM that plain `utf-8` `json.load`
rejects outright.

## Step 11 — Verify

**Structurally:** the script prints per-type and per-priority counts, the step
total, and the traceability coverage tally. Read them back. It also fails loudly
on the two invariants — a case with no AC reference, and a traceability row
naming a test case ID that does not exist.

**Visually:** re-reading with openpyxl proves the data landed, not that the
workbook looks right. Export PNG snapshots via Excel COM and actually look at
them:

```powershell
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $true          # REQUIRED: with $false the clipboard picture
                             # never lands and Export writes a ~250-byte blank
$wb = $xl.Workbooks.Open($book); Start-Sleep -Seconds 2
$ws = $wb.Worksheets.Item($name); $ws.Activate()
$rng = $ws.Range('A1:O20'); $rng.Select(); $rng.CopyPicture(1, 2)
Start-Sleep -Seconds 2       # clipboard needs to settle
$co = $ws.ChartObjects().Add(10, 10, $rng.Width, $rng.Height)
$co.Chart.Paste(); $co.Chart.Export($png, "PNG"); $co.Delete()
```

Run it **inline in one PowerShell call**, not via `powershell -File child.ps1` —
dispatched to a child process the clipboard paste silently fails and every PNG
comes out blank. Always check the file size: a real snapshot is tens to hundreds
of KB; a few hundred bytes means you are about to "verify" an empty image.

Confirm: no `Action` or `Expected Result` cell clipped at the row boundary, the
filter dropdowns present on the header row, the header row frozen, case banding
not cutting through a case, and the `Reviewer Status` dropdown working.

## Sharp edges already hit and fixed

Worth knowing before touching the generator:

- **Markdown emphasis is stripped on the way into Excel.** `test-cases.md`
  bolds every named UI element (`**"Save"**`) and that markup rides into the
  JSON spec verbatim. A worksheet cell has no inline rich text here, so the
  asterisks rendered literally — `click ***Save***.` — which passed the
  structural re-read and looked awful in the visual pass. `plain()` strips
  emphasis and code spans; in the workbook it is the **quoting** that carries
  the emphasis. Don't try to re-add bold in the cells.
- **The data table contains no merged cells, deliberately.** Merges break
  Excel's filters, and this sheet exists to be filtered. The only merges are
  the identity block and the title/banner rows *above* the header row, which is
  where the autofilter range starts.
- **Row heights are left unset on purpose.** Excel auto-fits a wrapped row it
  was given no height for, and auto-fit is exact where an estimate is not.
  **Exception:** Excel refuses to auto-fit a row containing a merged cell, so
  the merged `C:D` identity block gets an explicit estimated height — without
  it a long `Application Name` clips to one line.
- **Conditional-format fills use the OOXML differential convention** — a solid
  `dxf` fill reads from `start_color`/`end_color`, **not** `fgColor` +
  `patternType`. openpyxl accepts the static-fill spelling silently and it even
  round-trips through a re-read, but Excel renders no fill at all. Same trap
  documented in `build_checklist.py` and `build_ac_workbook.py`.
- **The script refuses to write on a failed invariant** and exits 1 — a case
  with no AC reference, a case with no `ticket`, a duplicate ID, a test type
  outside the nine, a case with no steps, or a traceability row naming a test
  case that does not exist. Fix the spec; do not work around it.

## Sizing — a starting heuristic, not a measurement

**This has not been calibrated against an accepted test-case suite for this
team.** Unlike [[4-acceptance-criteria-generation]], whose ratios come from 281
real AC rows, the numbers below are a starting point. If the user has an
accepted suite, measure it and replace this section.

- 1 acceptance rule → **1-3 test cases**. At Stage 04's measured 3.8 rules per
  AC row, a 12-row AC sheet lands roughly 45-90 cases for regression.
- **Sanity** keeps the positive paths and key validations — expect closer to a
  third of the regression count.
- 3-8 steps per case; over ~12 is two cases.
- A suite where negative + boundary cases are under ~20% of the total has
  usually skipped the refusal paths. Over ~60% and the positive coverage is
  probably thin. Both are worth a second look; neither is a rule.

Report the achieved figures rather than assuming them.
