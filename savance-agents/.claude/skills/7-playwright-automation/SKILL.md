---
name: 7-playwright-automation
description: Stage 07 substrate under 7-locator-extraction / 7-test-authoring / 7-test-healing — build, extend and run the Playwright + TypeScript Page-Object framework for the Savance Workplace Browser Interface: repo layout and naming, fixtures, reporters, the house Excel checklist reporter, and the verified app quirks (ASP.NET WebForms ids, visibility-hidden fly-outs, jqGrid refresh sync, toolbar relocation, account lockout) tests must be written around. Use when changing suites, page objects or locators in this repo, wiring reporting, debugging a flaky Savance test, or on /7-playwright-automation.
---

# Playwright automation (Savance Workplace)

The repo is a Page-Object Playwright framework in TypeScript targeting
`https://test.savanceworkplace.com`. This skill is the accumulated knowledge of
how it is put together and — more valuable — the app behaviours that were
learned the hard way and must not be rediscovered by trial and error.

**Read the "App behaviours" section before writing any assertion.** Most of it
is non-obvious, several items silently produce false passes, and all of it was
verified against the live app rather than inferred.

## What this skill is, and when to load it

The other three Stage 07 skills are **craft** — they would read much the same
for any Playwright project. This one is **this repo**: where the files live,
what the house calls things, which reporter to ask for, and the two dozen
Savance-specific behaviours that make an otherwise reasonable assertion wrong.

```
   1 ── [[7-locator-extraction]]   finding locators, writing page actions
   2 ── [[7-test-authoring]]       turning checklist rows into specs
   3 ── run the suite
   4 ── [[7-test-healing]]         diagnosing a red or flaky test
   ─────────────────────────────────────────────────────────────────────
        [[7-playwright-automation]]  ← the substrate under all four
```

Load it **alongside** whichever step you are in — never instead of one. The
split exists so the craft skills stay portable and this one stays specific:
a change to the app's behaviour is edited here and nowhere else.

The code it describes lives in
[automation_savance_workplace_web/](../../../automation_savance_workplace_web/),
whose own `CLAUDE.md` carries the short version of the hard rules.

## Layout and the one rule that holds it together

```
automation_savance_workplace_web/
├── pages/             *.page.ts       — ONE FILE PER PAGE. Locators AND actions.
├── tests/             *.spec.ts       — every assertion. Imports pages.
├── config/settings.ts                 — all config, read from .env
├── utils/                             — reporter, Excel builder, helpers
├── fixtures.ts                        — the page objects a spec asks for
├── playwright.config.ts               — runner, projects, reporters, artifacts
└── reports/                           — generated output (git-ignored)
```

    tests/  ->  pages/
    assert      where things are + what you can do

Each page file has exactly two halves, in this order:

```ts
export class LoginPage {
  readonly page: Page;

  // 1. THE THINGS ON THE PAGE — Locator properties, assigned in the constructor
  readonly usernameBox: Locator;
  readonly loginButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameBox = page.locator('#LoginUser_UserName');
    this.loginButton = page.locator('#LoginUser_LoginButton');
  }

  // 2. THE THINGS YOU CAN DO — intent-level methods
  async typeUsername(text: string) { await this.usernameBox.fill(text); }
  async clickLogin()               { await this.loginButton.click(); }
}
```

**A test never writes a selector and never touches the raw `page`.** If a test
needs a new element, add a `Locator` property to the page class and a method
that uses it. A test reaching for `page.locator('#SomeId')` — or building one by
string interpolation — is the signal the page class is missing a method.

There is no `BasePage`. Each page file is self-contained on purpose: you read
one file and know everything, with no jumping to a parent class.

Reference data that is NOT a selector (destination maps, expected wording,
limits) is an exported `const` at the TOP of the page file, above the class, so
a test can import it by name — `WRONG_LOGIN_MESSAGE`, `TOOLBAR_BUTTONS`.

### Naming convention

Names are chosen so a non-programmer can read a test out loud. Prefer the word a
user would say over the word the DOM uses.

| Thing | Rule | Example |
|---|---|---|
| Locator property | `camelCase`, named after what a user calls it | `usernameBox`, `signOutLink`, `moreOptionsMenu` |
| Locator matching many | pluralise | `tableRows`, `statusMenuOptions` |
| Reference-data const | `SCREAMING_SNAKE`, exported above the class | `WRONG_LOGIN_MESSAGE`, `TOOLBAR_BUTTONS` |
| Method that acts | verb first | `clickLogin()`, `pressSearch()`, `typeUsername()` |
| Method that reads | `read…` / `count…` / `is…` | `readCurrentStatus()`, `countRows()`, `isPasswordHidden()` |
| Method inside the SPA iframe | say so in the name | `findInApp()`, `findInBox()` |

Say `usernameBox`, not `txtUsr` or `USERNAME_INPUT`. Say `readCurrentStatus()`,
not `getStatusLabelText()`. A method that SAVES something to the server carries a
`*** THIS SAVES FOR REAL ***` line in its doc comment.

## Never guess a selector — verify it live first

This is the workflow that produced every locator in the repo, and skipping it
produces tests that are worthless even when green.

> Three companion skills carry the general craft, so this file can stay focused
> on **this app's** quirks:
> [[7-locator-extraction]] (finding locators and writing page actions),
> [[7-test-authoring]] (turning a checklist into specs),
> [[7-test-healing]] (diagnosing a red or flaky test).
> Load the relevant one alongside this skill.

1. Use the Playwright MCP server to log in
   (`#LoginUser_UserName` / `#LoginUser_Password` / `#LoginUser_LoginButton`).
2. `browser_evaluate` a DOM dump of the region you care about — `outerHTML` of
   the container, plus ids/classes/handlers of the controls inside. The
   accessibility snapshot is not enough: it hides ids and hides *why* an
   element is invisible.
3. For anything that hides/shows, probe `getComputedStyle` explicitly for
   `display`, `visibility` AND `getBoundingClientRect()` — see the fly-out trap
   below.
4. Only then write the locator, with a comment saying **where in the UI it
   lives** and **how to get there**.

Cheap trick for confirming a set of destinations in one call: `fetch()` each
path same-origin from an authenticated page and read back `<title>`. That is
how the whole `TOOLBAR_BUTTONS` title map was verified without eight
navigations.

If a behaviour cannot be verified, say so in the locator/page-object docstring
and make the test **skip with that reason** — never assert something you did
not observe.
## App behaviours (all verified live)

-> `reference/app-quirks.md`. The four that bite hardest: **generated WebForms
ids** (never text-match what has an id), **fly-outs hidden with `visibility`**
(so a visibility assertion lies), **toolbar items relocate rather than
disappear**, and **jqGrid refresh needs a real wait, never a sleep**.

## Writes, and the shared account

Almost everything is read-only. The exceptions are the two status-change checks
and all of Question Manager. Rules:

1. Read the original value **first**, restore it in a `finally` so a failing
   assertion cannot leave the account parked on the wrong status.
2. Confirm the write independently — e.g. re-read the Status Board, not just the
   header the widget itself painted.
3. `workers: 1` and `fullyParallel: false` in the config, because the whole
   suite shares one account. Raise it only when each worker gets its own user.

## Writing a spec

Use `test.step()` for every meaningful step. It turns the test into a readable
manual test case top-to-bottom, and each step becomes its own entry in the HTML
report and trace viewer, so a failure names the step before you open a stack
trace.

Declare checklist identity with `checklistCase()` from
[utils/testMeta.ts](../../../automation_savance_workplace_web/utils/testMeta.ts):

```ts
test.describe('Login', () => {                       // -> checklist MODULE
  test(
    'Password field is masked',                      // -> CHECK ITEM
    checklistCase('TC-LOGIN-002', 'Field Behaviour', ['@smoke'], 'checklist.md:3'),
    async ({ loginPage }) => {
      await test.step('The box is set to hide text before anything is typed', async () => {
        await expect(loginPage.passwordBox).toHaveAttribute('type', 'password');
      });
    },
  );
});
```

- **Module** = outermost `describe` title, **Area** = the `area` annotation,
  **Test ID** = the `test_id` annotation. Tags (`@smoke`, `@negative`) stay real
  Playwright tags so `--grep @smoke` works.
- Add a **control assertion** where a check could pass for the wrong reason —
  e.g. after asserting the password field is masked, assert the username field
  is *not*, or a page masking every input would still pass.
- Prefer a message on `expect(...)` explaining what the failure means.

Source cases come from `checklist.md`. Map each spec to its line via the
`checklistRef` argument, and put the mapping table in the file header.

## Reporting, TypeScript and running

-> `reference/repo-mechanics.md` for the Excel reporter, the ExcelJS/openpyxl
differences, the repo's TypeScript gotchas, which npm scripts are broken, and
how to add a new page or suite.

Two cheap checks before any real run, always in this order:

```bash
npx tsc --noEmit                                  # seconds
npx playwright test tests/<file>.spec.ts --list   # seconds, no browser
```

**`WORKERS=1` stays 1.** One shared account; parallel workers fight over it.

---

<!-- Stage 07 substrate, loaded alongside 7-locator-extraction /
     7-test-authoring / 7-test-healing. Code: automation_savance_workplace_web/ -->
