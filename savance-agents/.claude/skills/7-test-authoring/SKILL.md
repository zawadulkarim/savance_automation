---
name: 7-test-authoring
description: Stage 07 step 2 of 3 — turn the Stage 05 test-cases.md, or a manual QA checklist, into Playwright specs: one independent test per row, titled with its id and name, from test.step blocks that read as the manual case. Covers genuine independence (including server-persisted state surviving re-login), assertions that pass for the wrong reason, asserting the app's real behaviour over the checklist's wording, destructive cases, and data-driven generation. Owns test-review.md. Use when porting a checklist into specs, writing new cases, or on /7-test-authoring.
---

# Test case authoring

Turning test cases into automated tests that are worth trusting.

The two failure modes to design against, in priority order:

1. **A test that passes for the wrong reason.** Far worse than a failing test,
   because nobody investigates it. Most of this skill is about these.
2. **A test that fails for a reason unrelated to what it checks.** Wastes the
   next person's afternoon.

## Where this sits — Stage 07, step 2 of 3

```
   test cases  (test-cases.md -- Stage 05, canonical)
   or checklist rows  (5 - QA Checklist.xlsx, or checklist.md)
        │
   1 ── [[7-locator-extraction]]   page objects, every locator proven live
        │
   2 ── [[7-test-authoring]]  ← YOU ARE HERE
        │      one independent spec per checklist row
        │
   3 ── run the suite            npx playwright test tests/<file>.spec.ts
        │
   4 ── [[7-test-healing]]        classify every red
```

### Which input you are working from

Two shapes arrive here, and they are not equivalent.

**`test-cases.md` (Stage 05) is the canonical one.** It carries what a spec
actually needs — preconditions, concrete test data, ordered steps with a
per-step expected result, postconditions, and a `TC-NNN` id.

**Check its `Review Status` line before you write a single spec:**

```bash
grep -m1 '^\*\*Review Status:\*\*' "<ticket folder>/test-cases.md"
```

Stage 05 holds a blocking human review gate at its Step 9, and only a person
writes `APPROVED — <reviewer>, <date>` on that line. On `DRAFT` or
`AWAITING HUMAN REVIEW`, stop and ask: the cases can still change, and specs
written against a superseded draft are the most expensive kind of rework in
this repo. The user may say proceed — that is their call, and it goes at the
top of `test-review.md`. A file with no stamp at all is an older or thinner
input, not a violation; say which you used.

Then read it and honour these fields:

- **`Automation Candidate: No`** — do not automate it. Record it in
  `test-review.md` as a manual case with the reason Stage 05 gave. Automating
  it anyway, in a weakened form, is the cardinal sin one stage displaced.
- **`Playwright Verified: No`** — the UI in those steps was never observed live.
  Expect the locators to be wrong and verify before you trust a green.
- **An Assumption against a case** — becomes a `test-review.md` line for a human
  to confirm. It never becomes an assertion.
- **Preconditions and Postconditions** — these are your setup and teardown. A
  case whose postcondition says "disable the setting" needs that in the spec, or
  the next test inherits it.

Keep the `TC-NNN` id in the test title, exactly as the checklist id is kept
below, so a result maps back to the case with no lookup table.

**A checklist row (`5 - QA Checklist.xlsx`, `checklist.md`) is the older, thinner
input.** It is a single atomic assertion with no preconditions and no data, so
you are inferring the surrounding procedure. That inference is where tests that
pass for the wrong reason come from — prefer `test-cases.md` when both exist,
and say which you used.

[[7-playwright-automation]] is the substrate — house naming, `checklistCase()`,
reporters, and the app quirks every assertion has to be written around. Load it
alongside this one.

**What you receive:** page objects whose locators have been proven against the
live app, plus whatever [[7-locator-extraction]] could not prove.

**What you hand on:** specs that have been **run at least once** (step 3 is part
of this skill, not an afterthought), the red ones passed to [[7-test-healing]],
and a review file entry for every judgement a human should confirm.

### The input contract — and the one thing that sends you back

A spec is written against page-object methods. If the method you need does not
exist:

- **Go back to [[7-locator-extraction]]** and add it there.
- **Do not** write `page.locator('#Something')` in the spec to get moving.
  It passes the typecheck, it may even go green, and it quietly destroys the
  one rule the whole framework rests on.

The only exception is asserting on a foreign page with no page object at all
(a login form after signing out) — and even then, prefer adding the method.

---

## Shape

### One test per checklist row, id and name in the title

```ts
test(
  'SC-32 — Check that the user can select a row',
  checklistCase('SC-32', 'The status board itself', [], 'checklist:71'),
  async ({ homePage }) => { /* ... */ },
);
```

The title carries the checklist **id** and its **words**, so a result maps back
to the row with no lookup table. Keep the checklist's own wording — resist
improving it, because the whole point is traceability.

### Every test is a list of `test.step()` blocks

```ts
await test.step('The list starts closed', async () => { ... });
await test.step('Click the arrow next to "Status"', async () => { ... });
await test.step('The list of statuses opens', async () => { ... });
```

Read the step names top to bottom and you have the manual test case. Each step
is a separate entry in the HTML report and the trace viewer, so a failure names
the step before anyone opens a stack trace.

Steps should be plain English about the *product*, not the automation. "Open
the status list", not "call openStatusMenu and await the panel".

### A test never writes a selector

If a test reaches for `page.locator('#Something')`, the page object is missing
a method. The only exception worth making is asserting on a foreign page you
have no page object for (a login form after signing out), and even then prefer
adding the method.

---

## Independence

The user-visible requirement is usually "every case must be independent". The
subtle part is that **a fresh login is not automatically a fresh start.**

### Server-persisted state defeats per-test login

Many apps save UI preferences server-side against the user. Filter dropdowns
survived reload *and* sign-out/sign-in. So a test that set a filter silently
changed what the next test saw, even though the next test logged in fresh.

This produced two failures that looked like unrelated locator timeouts.

**Detect it:** set a preference, reload, check. Then log out, log back in, check
again. Anything still set is shared state between your tests.

**Fix it:** reset in `beforeEach` for every section whose outcome depends on
that state.

```ts
test.describe('Filtering the board', () => {
  // Filters are remembered on the SERVER for this user, so whatever the last
  // test chose would otherwise still be in force here — even though every
  // test logs in fresh.
  test.beforeEach(async ({ homePage }) => {
    await homePage.resetFilters();
  });
```

Put the *reset logic* in the page object and the *decision to reset* in the
spec. The page object explains how; the spec explains why it is needed here.

Note which state persists and which does not — dropdowns and checkboxes
persisted, free-text boxes did not. Guessing wastes a run.

### Restore anything you change, in a `finally`

```ts
const startedTicked = await homePage.isRowTicked(0);
try {
  await homePage.setRowTicked(0, true);
  expect(await homePage.isRowTicked(0)).toBe(true);
  await homePage.setRowTicked(0, false);
  expect(await homePage.isRowTicked(0)).toBe(false);
} finally {
  await homePage.setRowTicked(0, startedTicked);
}
```

`finally`, not a trailing line — a failed assertion must not leave the account
in a changed state for every later test.

### Destructive cases: exercise the guard, never the action

A checklist row like *"can be clicked and asks for confirmation — cancel it, do
not confirm"* is testable and valuable. Test the confirmation contract:

```ts
await toolbar.clickClearRollCall();          // opens the question only
try {
  expect(await toolbar.isConfirmBoxOpen()).toBe(true);
  expect(await toolbar.readConfirmBoxHeading()).toBe(CLEAR_ROLL_CALL_HEADING);
  expect(await toolbar.readConfirmBoxQuestion()).toBe(CLEAR_ROLL_CALL_QUESTION);
  await expect(toolbar.confirmBoxYesButton).toBeVisible();
  await expect(toolbar.confirmBoxNoButton).toBeVisible();
} finally {
  await toolbar.pressNoInConfirmBox();       // never Yes
}
```

Say so in a comment in capitals, and list every such test in the file header so
a reader knows the blast radius before running anything.

---
## Assertions that actually prove something

Eight ways a green test can mean nothing —
→ `reference/assertions.md`. The two worth carrying without a lookup: **add a
control assertion wherever a check could pass for the wrong reason**, and
**assert the app's real behaviour, not the checklist's wording** — where they
disagree, the disagreement is a row in the review file, not a bent assertion.

## Generating near-identical cases

Eight "can I reach page X" rows differ only by destination. Generate them from
a list — each still becomes its own independent test:

```ts
const NAVIGATION_CHECKS = [
  { id: 'SC-08', name: 'Home', ref: 'checklist:32' },
  { id: 'SC-09', name: 'Notes', ref: 'checklist:33' },
  // ...
] as const;

for (const check of NAVIGATION_CHECKS) {
  const destination = TOOLBAR_BUTTONS[check.name];
  test(
    `${check.id} — Check that the user can navigate to the ${check.name} page`,
    checklistCase(check.id, 'Moving around from the top menu', ['@smoke'], check.ref),
    async ({ toolbar }) => {
      await test.step(`Click "${check.name}" on the top menu`, async () => {
        await toolbar.clickButtonAndWait(destination.selector, destination.urlPart);
      });
      await test.step('You arrive at the right page', async () => {
        expect(toolbar.currentUrl()).toContain(destination.urlPart);
      });
      await test.step('And the page really is the one expected', async () => {
        // Address alone is not enough — a redirect could keep the same path.
        expect(await toolbar.title()).toBe(destination.tabTitle);
      });
    },
  );
}
```

Keep the loop **flat and obvious**. If a generated test needs a special case,
write it out separately rather than adding a branch inside the loop.

**Watch the degenerate member of the list.** In the example above, "Home"
navigates from Home *to Home*. Any wait keyed on "the address now contains
`/Default.aspx`" is already satisfied before the click, so the test races the
navigation and reads the old document. Whenever you generate cases from a list,
ask which entry is the self-referential or empty one, and check it separately.

---

## The file header earns its place

Open every spec with:

- which checklist it implements, and that each test stands alone
- **the tests that touch real data**, named, with what they do and why it is safe
- **behaviours that surprised you**, so the next person does not "fix" a
  deliberately odd assertion back into a wrong one

That last section is the highest-value part of the file. Everything in it was
paid for once already.

---

## Run what you wrote — authoring is not done at "it compiles"

A spec that has never been executed is a draft. Finish the job:

```bash
cd automation_savance_workplace_web
npx tsc --noEmit                                  # cheap, catches most of it
npx playwright test tests/<file>.spec.ts --list   # confirm every test is discovered
npx playwright test tests/<file>.spec.ts          # the real thing
```

`--list` before the run is worth the two seconds: a `describe` that throws at
collection time, or a generated loop that produced fewer cases than you
expected, shows up here instantly instead of forty minutes into a run.

Then, on the results:

- **All green** → run each new test **alone** (`-g "WL-14"`). Green together but
  red alone means it was leaning on a neighbour. Green alone but red together
  means contamination. Both are [[7-test-healing]] category 4.
- **Anything red** → hand it to [[7-test-healing]]. Do **not** adjust the
  assertion yourself to get a green run; that is precisely the failure mode
  this stage exists to prevent.

Never report a suite as delivered on a typecheck alone.

---

## The review file

→ `reference/review-file.md` for the format, the seven categories that must be
raised, and what must not be. In short: `automation_savance_workplace_web/test-review.md`,
appended to rather than overwritten, and a case that was written, ran green and
raised nothing does **not** appear in it.

---

<!-- Stage 07, step 2 of 3. Agent: .claude/agents/7-testing-agent.md
     Upstream: 7-locator-extraction (page objects) and stage 05's APPROVED
     test-cases.md. Reds go to 7-test-healing. Substrate: 7-playwright-automation. -->
