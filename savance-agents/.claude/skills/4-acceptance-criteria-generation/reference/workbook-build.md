# Building and verifying the AC workbook

Referenced from `SKILL.md` Steps 8-9. Read this **only after** the human has
approved the Markdown at Step 7 — nothing here applies before the gate.

## Contents
- Stamping the approval and re-rendering
- The workbook generator invocation
- Visual verification via Excel COM (and why it cannot be skipped)
- Sharp edges already hit and fixed in the generators

1. Set `review_status` in the spec to
   `APPROVED — <reviewer name>, <YYYY-MM-DD>`, using the name and date the
   human actually gave, and re-render the Markdown so the approval is
   recorded in the artefact itself rather than only in the conversation. This
   is the line every downstream stage greps.
2. Build the workbook from the **same** spec:

```bash
python .claude/skills/4-acceptance-criteria-generation/scripts/build_ac_workbook.py <spec.json> <output.xlsx>
```

**Output location:**

```
tickets/<ticket-id> - <Ticket name>/4 - Acceptance Criteria.xlsx
```

Never overwrite an earlier round; add a `(rev 2)` suffix, matching the
Markdown's. If a run has no ticket behind it (a feature-list batch, say),
fall back to the house filename
`[Acceptance Criteria] <project or batch>.xlsx` in the working directory.

The copy delivered to the shared review folder at Step 11 keeps the
house-facing name `[Acceptance Criteria] <project or batch>.xlsx`
(`[Internal]` prefix for internal-only drafts) — that folder is read by people
who never see the ticket folder. Never pass a reference workbook as the output
path.

The script prints per-sheet AC-row and rule counts plus the achieved
rules/row ratio. They must agree with what the Markdown printed at Step 5 —
both came from one spec, so a difference means you rendered from a stale copy.

Then derive the checklist per Step 10.

## Step 9 — Verify the workbook visually, not just structurally

This runs **once, after approval**, and on the workbook only. The Markdown
needs no visual pass — that saving is most of what moving the gate earlier
buys.

Re-reading with openpyxl proves the *data* landed; it does not prove the
workbook *looks* right. Export PNG snapshots via Excel COM and actually look
at them:

```powershell
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $true          # REQUIRED: with $false the clipboard picture
                             # never lands and Export writes a ~250-byte blank
$wb = $xl.Workbooks.Open($book); Start-Sleep -Seconds 2
$ws = $wb.Worksheets.Item($name); $ws.Activate()
$rng = $ws.Range('A1:F14'); $rng.Select(); $rng.CopyPicture(1, 2)
Start-Sleep -Seconds 2       # clipboard needs to settle
$co = $ws.ChartObjects().Add(10, 10, $rng.Width, $rng.Height)
$co.Chart.Paste(); $co.Chart.Export($png, "PNG"); $co.Delete()
```

**Run this inline in one PowerShell call, not via `powershell -File
child.ps1`** — dispatched to a child process the clipboard paste silently
fails and every PNG comes out blank. Always check the file size: a real
snapshot is tens to hundreds of KB, a few hundred bytes means you're about
to "verify" an empty image.

Then read the PNGs and confirm: no `Acceptance Rules` cell clipped at the
row boundary, group merges spanning the right blocks, banding not cutting
through a merged block, `Status` badges actually showing their fill colour,
and the header block not truncating a long `Application Name`.

## Sharp edges already hit and fixed

Worth knowing before touching the generator:

- **Row heights are left unset on purpose.** Excel auto-fits a wrapped row
  it was given no height for, and auto-fit is exact where an estimate is
  not — an earlier version estimated heights and clipped the last line of a
  5-rule cell while leaving slack on a 4-rule one. The reference workbooks
  carry no row heights either. **Exception:** Excel refuses to auto-fit a row
  containing a **merged** cell, so the merged `C:D` identity block *does*
  get an explicit estimated height — without it a long `Application Name`
  clips to one line.
- **Conditional-format fills use the OOXML differential convention** —
  a solid `dxf` fill reads from `start_color`/`end_color`, **not**
  `fgColor` + `patternType`. openpyxl accepts the static-fill spelling
  silently and it even round-trips through a re-read, but Excel renders no
  fill at all. Same trap documented in `build_checklist.py`.
- **Spec files are read as `utf-8-sig`.** Anything written by PowerShell
  5.1's `Set-Content -Encoding utf8` / `Out-File` carries a BOM, which plain
  `utf-8` `json.load` rejects outright.
