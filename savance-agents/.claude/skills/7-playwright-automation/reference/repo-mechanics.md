# Reporting, TypeScript and npm mechanics in this repo

Referenced from `SKILL.md`. Repo plumbing rather than app behaviour.

## Contents
- Reporting: the house Excel QA-checklist reporter
- ExcelJS porting gotchas (coming from openpyxl)
- TypeScript gotchas in this repo
- Running: the two cheap checks before any real run
- Broken npm scripts - do not trust the whole list
- Adding a new page or suite

## Reporting

`@playwright/test` owns reporting natively, so the framework no longer emulates
it (the Python port had to). Selected by name via the `REPORTER` env var:

| Name | Output |
|---|---|
| `list` / `line` / `dot` | console |
| `html` | `reports/html` — includes the built-in trace viewer |
| `json` | `reports/results.json` |
| `junit` | `reports/junit.xml` |
| `blob` | `reports/blob` — for `merge-reports` across shards |
| `github` | `::error` annotations on a PR |
| `checklist` | **ours** — `reports/test_results.json` + the Excel workbook |

```powershell
$env:REPORTER="dot,checklist"; npx playwright test
```

A CLI `--reporter=` **replaces** the whole list, so the checklist would not be
built — use the env var when you want it composed in.

The checklist reporter fills **Test Status from the real outcome** instead of
defaulting to "Untested", and follows the house "Savance Q3 Release Items"
template (see [[4-checklist-generation]] for the template itself).

### ExcelJS porting gotchas (from openpyxl)
- Colours are **ARGB** — every hex needs an `FF` alpha prefix. A bare 6-digit
  hex renders transparent, silently.
- Data validation is **per cell** (`cell.dataValidation`), not per range —
  expand the range yourself.
- Conditional-format fills use `bgColor` (dxf convention), not `fgColor`.
- **Sheets cannot be reordered.** The Dashboard must be created *first*; its
  cross-sheet formulas are plain text, so the sheets they point at can be
  created afterwards. Compute the per-module counts before creating any sheet.

## TypeScript gotchas in this repo

An `as const` object whose own functions reference that same object makes its
type **circular** (`TS7022` / `TS2456`). Fix by declaring the map as a separate
top-level `const` and deriving the exported type from *that*. See the
`COLUMN_LABELS` block in [pages/home.page.ts](../../../automation_savance_workplace_web/pages/home.page.ts),
which `ColumnName` is derived from and which `readColumn()` reads directly.

`devices['Desktop Chrome']` carries its own 1280x720 viewport, so re-apply the
configured viewport **after** the spread in each project, or the device default
silently wins and recorded video will not match what ran.

## Running

**Every command below runs from `automation_savance_workplace_web/`**, not the
repository root. Running them a level up fails with a config-not-found error
that reads as though Playwright is missing.

```powershell
npm install
npx playwright install chromium

npx playwright test                                   # whole suite
npx playwright test tests/login.spec.ts               # one file
npx playwright test --grep @smoke                     # by tag
npx playwright test tests/login.spec.ts --headed      # watch it
npx playwright test --debug                           # inspector, step through
npx playwright test --ui                              # timeline + DOM snapshots
npx playwright test -g "Password field is masked"     # one test by name
npm run report                                        # open the HTML report
npx tsc --noEmit                                      # typecheck
```

### The two cheap checks to run before any real run

```powershell
npx tsc --noEmit                          # seconds; catches most authoring slips
npx playwright test --list                # seconds; no browser, no login
```

`--list` is the one people skip and should not. It collects the suite without
launching anything, so a `describe` that throws at collection time, or a
generated loop that produced three cases where you expected eight, surfaces in
two seconds instead of forty minutes into a run against a shared account.

Baseline as of 2026-09-02, both verified in this repo: `tsc --noEmit` exits
clean, and `--list` reports **79 tests in 3 files**
(`home.spec.ts`, `login.spec.ts`, `watchlist.spec.ts`). A materially different
count after your change means discovery broke — investigate before running.

### Broken npm scripts — do not trust the whole list

`package.json` predates the current suite and two of its scripts point at spec
files that do not exist:

```
npm run test:toolbar   -> tests/topToolbar.spec.ts tests/mainToolbar.spec.ts
```

Neither file is in `tests/`. Toolbar coverage lives inside `home.spec.ts`. The
scripts that do work: `test`, `test:login`, `test:smoke`, `test:negative`,
`test:headed`, `test:debug`, `test:ui`, `report`, `typecheck`,
`install:browsers`, `codegen`.

`$env:SLOW_MO=500` with `--headed` to slow it down; `HEADLESS=false` in `.env`
to make headed the default. Everything tunable lives in `.env` (copy from
`.env.example`) — credentials, browser, timeouts, artifact retention, reporters.

## Adding a new page or suite

1. Verify the selectors **live** (see above). Do not skip this.
2. Add a `pages/<name>.page.ts` with the two halves in order: exported
   reference-data consts, then the class with its `Locator` properties assigned
   in the constructor, then the methods. Open the file with a comment block
   saying what the page is, how you reach it by hand, and any app behaviour the
   methods exist to work around. Mark anything that **writes**.
3. Export it from `pages/index.ts`.
4. Add a fixture in `fixtures.ts` if specs will need it pre-loaded, chaining off
   `homePage` for anything authenticated.
5. Write `tests/<name>.spec.ts` with `test.step()` and `checklistCase()`.
6. If the module should sort ahead of others in the workbook, add it to
   `MODULE_ORDER` in `utils/checklistBuilder.ts`.
7. `npx tsc --noEmit`, then `npx playwright test <file> --list` to confirm
   discovery, then run it.
8. Triage every red through [[7-test-healing]] — script wrong, fix it; app
   wrong, leave it red — and record what a human still has to decide in
   `test-review.md` (format in [[7-test-authoring]]). The suite and that file
   are the two deliverables of Stage 07; neither is finished without the other.
