# Building and verifying the checklist workbook

Referenced from `SKILL.md` Steps 3-5.

## Contents
- The JSON spec schema
- The generator invocation
- Visual verification via Excel COM (and why numeric checks are not enough)

## Step 3 — Build the JSON spec

Write a JSON file matching this schema (see the script's docstring for the
authoritative version):

```json
{
  "project_name": "Savance Q3 Release Items",
  "prepared_by": "Enosis QA",
  "start_index": 13,
  "features": [
    {
      "title": "Feature or bug title",
      "last_updated": "2026-07-26",
      "related_applications": "VMSuite Apps: Visitor Sign In, Self Check In | Kiosk App",
      "test_build": "https://test.savanceworkplace.com | DB: 12.1.10 | Web: 12.1.36",
      "environment": "Lenovo Thinkpad | Windows 11 Pro | Google Chrome",
      "assigned_to": "Zawad",
      "status": "QA Backlog",
      "est_hours": 6,
      "milestone": "MS-1",
      "modules": [
        {
          "name": "Web: Question Manager",
          "checks": ["Verify ...", "Verify ...", "Validate ...", "Confirm ..."]
        }
      ]
    }
  ]
}
```

Notes:
- Every field except `title` and `modules` is optional and falls back to
  `"-"` (or `"QA Backlog"` for `status`) if omitted — fill in what the source
  material actually gives you; don't invent build numbers or environment
  details that weren't provided.
- `start_index` controls the first sheet number (`#13` above). Ask the user
  whether the generated sheets should continue the master workbook's
  existing numbering (so they drop in cleanly later) or just start at `1` —
  don't assume. Standalone per-app checklists have been starting at `1`.
- A module's `checks` is a flat list, in the order a tester walks the module.
  The legacy nested `"acs": [{"checks": [...]}]` shape is still accepted and
  flattened in order (the `AC #` column no longer exists), so old spec files
  still build — but write new specs flat.
- One JSON spec can hold multiple `features` — this is how the "expand a
  whole feature-list spreadsheet in one run" case is handled: one entry per
  source row, in the same order.

## Step 4 — Generate the workbook

Run the script against your spec:

```bash
python .claude/skills/4-checklist-generation/scripts/build_checklist.py <spec.json> <output.xlsx>
```

**Output location.** Into the ticket folder every lifecycle stage shares:

```
tickets/<ticket-id> - <Ticket name>/5 - QA Checklist.xlsx
```

Locate the folder by globbing `tickets/<ticket-id> - */` — the Asana gid is
the stable key. Never overwrite an earlier round; add a `(rev 2)` suffix.

If a run has no ticket behind it, pick a name that identifies the
feature/batch and won't collide with the source workbook (e.g.
`Savance Q3 - New Checklist Items (batch).xlsx` next to it, or the scratchpad
for a throwaway preview). Never pass the original
`[Initial Checklist] Savance Q3 Release Items.xlsx` as the output path.

After it runs, the script prints a per-sheet summary (sheet name, check-item
count, title) — read it back to confirm the batch matches what was asked
for before telling the user it's done.

**Path gotcha in this environment (Bash tool = Git Bash/MSYS):** MSYS
auto-translates POSIX-looking paths (`/c/Users/...`) to Windows paths (
`C:\Users\...`) for arguments handed to a native `.exe` like `python.exe` —
but only when a path is its own standalone argv token. A path embedded
*inside* a longer string (e.g. `python -c "...open('$SCRATCH/x.json')..."`)
does **not** get translated, and native Windows Python will fail to find it.
Always pass file paths as their own argument (`python script.py "$SCRATCH/
spec.json" "$SCRATCH/out.xlsx"`, or write a tiny throwaway `.py` file and pass
the path via `sys.argv`) rather than interpolating them into a `-c` string.

## Step 5 — Verify visually, not just numerically

Re-opening the output with openpyxl and checking formulas/values (or, if
Excel is on the machine, driving it via COM and calling
`CalculateFullRebuild()`) confirms the *data* is right, but it does **not**
confirm the workbook *looks* right — colors, fills, and column widths can be
silently wrong even when every formula recalculates cleanly (see the dxf
fill gotcha above, which shipped in multiple "verified" deliverables before
anyone actually looked at rendered output). Before calling a workbook done:

1. **Export PNG snapshots of the actual ranges via Excel COM** — this is the
   route that works on this machine. `ExportAsFixedFormat(0, "<path>.pdf")`
   still produces a valid PDF, but the Read tool **cannot render it here**
   (`pdftoppm is not installed` — no poppler on this box), so don't burn a
   cycle on the PDF path. Instead, per range:

   ```powershell
   $xl.Visible = $true            # REQUIRED: with Visible = $false the
                                  # clipboard picture never lands and Export
                                  # silently writes a ~400-byte blank PNG
   $rng = $ws.Range('A1:N30'); $rng.Select(); $rng.CopyPicture(1, 2)
   Start-Sleep -Milliseconds 700  # let the clipboard settle
   $co = $ws.ChartObjects().Add(10, 10, $rng.Width, $rng.Height)
   $co.Chart.Paste(); $co.Chart.Export("<path>.png", "PNG"); $co.Delete()
   ```

   Sanity-check the file size — a real snapshot is hundreds of KB; a few
   hundred bytes means the paste failed and you're about to "verify" a blank
   image.
2. Read the PNGs and actually look: do status/priority/type badges show their
   fill color, does header text fit without an ugly mid-word wrap or clipping,
   do banding/borders read as intended? Cover the header block, a middle
   stretch, and the last rows. If something needs to change, edit the script,
   regenerate, and re-export rather than trusting the first pass.
3. Only once the rendered output looks right, move to handoff.
