---
name: 7-test-healing
description: Stage 07 step 3 of 3 — diagnose and repair a failing or flaky Playwright test without weakening what it proves: classify the failure from the call log (wrong locator, wrong assumption, changed app behaviour, cross-test contamination, flake), reproduce live before changing anything, fix in the page object or the spec, then re-run targeted and full. Script wrong, fix the script; APP wrong, leave it red for 8-asana-bug-report. Use when a test goes red or flaky, or on /7-test-healing.
---

# Test healing

Deciding what a red test actually means, and repairing it **only** when the
test is the thing that is broken.

## Where this sits — Stage 07, step 3 of 3

```
   1 ── [[7-locator-extraction]]   page objects, every locator proven live
   2 ── [[7-test-authoring]]       one independent spec per checklist row
   3 ── run the suite             npx playwright test tests/<file>.spec.ts
   4 ── [[7-test-healing]]  ← YOU ARE HERE
```

[[7-playwright-automation]] is the substrate — the app quirks below are the
reason half of these failures happen. Load it alongside this one.

**What you receive:** a run with reds in it. **What you hand on:** a suite whose
every remaining red is a *deliberate, explained* red, plus review-file entries
for each one.

---

## The fork — decide this before you edit a single character

Every red test is one of two things, and they have **opposite** treatments:

> ### The script is wrong → fix the script.
> The locator drifted, the wait was wrong, the assumption was wrong, a
> neighbouring test left state behind. Repair it in the page object or the spec
> and get it green.
>
> ### The app is wrong → LEAVE THE TEST EXACTLY AS IT IS.
> The test is correct. Red is the **right answer** and the suite is doing its
> job. Do not edit the assertion, do not add a `skip`, do not loosen a matcher,
> do not soften a message, do not `expect.soft` it away. Leave it red, and
> write it into the review file as a candidate defect for [[8-bug-reporting]].

A red test that found a genuine bug is the most valuable output this stage
produces. "Healing" it is the one unrecoverable mistake available here: the bug
goes to production *and* the evidence that would have caught it is gone.

**When you cannot tell which it is** — the evidence is ambiguous, the
environment is unstable, the behaviour is undocumented — the answer is the
*second* one. Leave the test as it is and raise it for a human. Never guess
your way to a green suite.

The corollary, which is the same rule stated from the other end:

> **Never change an assertion just to make it pass.**
> Only two of the six categories below are fixed by editing an assertion — and
> in both cases the assertion was wrong on the day it was written, and you must
> be able to say *why*.

### The heal budget

**Two attempts per failing test, then stop.** If a test is still red after two
diagnosed, reproduced fix attempts, it goes to the review file as
"heal budget exhausted" with everything you learned. It does not get a third
round, and it certainly does not get a weakened assertion.

This is deliberate: past two rounds, the odds that the next edit is a *real*
fix drop sharply, while the odds that it is an assertion quietly bent to fit
rise just as sharply. Cost is the lesser reason; a suite that lies is the
larger one.

---

## Step 1 — Read the call log, not just the error

The error line is a summary. Playwright's **call log** underneath says what it
was doing when it gave up, and it usually names the cause outright.

The distinction that matters most:

```
- attempting click action
  - waiting for element to be visible, enabled and stable
  - element is visible, enabled and stable
  - scrolling into view if needed
  - performing click action
  - click action done                              ← THE CLICK WORKED
  - waiting for scheduled navigations to finish    ← this is what hung
```

That is not a locator problem. The selector was perfect. Reading only
`TimeoutError: locator.click` would have sent you to rewrite a correct locator.

Compare with a genuine actionability failure, which never reaches
"click action done":

```
- attempting click action
  2 × waiting for element to be visible and enabled
    - did not find some options                    ← the option is absent
```

Also read `expect` failures for the **received** value, which is often the whole
diagnosis:

```
Expected value: "Home"
Received array: ["Status", "Notes", "Reports", ...]   ← Home was never included
```

---
## Step 2 - Classify the failure

Six classes, and the class decides the treatment ->
`reference/failure-classes.md`. Class 6 (**the app is genuinely broken**)
overrides everything else: hands off the test, leave it red, raise it for
[[8-asana-bug-report]].

Before trusting a *pass*, check `reference/green-test-traps.md` - a check that
cannot fail reads exactly like a check that passed.

## Step 3 — Reproduce live before changing anything

Open the app with the Playwright MCP browser, put it in the failing state, and
read the DOM. Guessing from a stack trace is how correct code gets "fixed".

This is what turned each of the above from a theory into a fact:

- clicking the button by hand proved the locator was fine → the hang was the wait
- reading the dropdown's options after changing another dropdown proved the
  dependency
- filtering by Staff then Visitor proved two distinct people share a name

Screenshots and the `error-context.md` in the artifacts folder are the fastest
way in:

```bash
reports/artifacts/<test-dir>/error-context.md   # error + call log + page snapshot
reports/artifacts/<test-dir>/test-failed-1.png  # what the screen looked like
```

---

## Step 4 — Decide where the fix belongs

Ask: **would another test hit this?**

- Yes → page object. One fix, everywhere.
- No, this test's expectation was simply wrong → spec.

Prefer adding a correctly-named method over loosening an existing one. When you
rename, keep a delegating alias so unrelated specs keep working:

```ts
/** Old name for `isFiltersPanelOpen()`. Kept so existing tests still run. */
async isFiltersPanelVisible(): Promise<boolean> {
  return this.isFiltersPanelOpen();
}
```

---

## Step 5 — Verify the fix

1. **Run just the tests that failed.** Fast feedback that the fix works.
   ```bash
   npx playwright test tests/home.spec.ts -g "SC-07|SC-12|SC-37|SC-39|SC-41"
   ```
2. **Run each healed test alone.** Proves you fixed the test, not the ordering.
3. **Run the whole suite.** Your fix may have changed shared state — adding a
   filter reset to a `beforeEach` changes the board every later test sees.
4. **Re-check the tests you did not touch.** A green-to-red elsewhere is a real
   result, not noise.
5. **Account for every remaining red.** "All green" is not the target — *every
   red explained* is. Each one left standing must be a category 6 app defect
   with a row in `test-review.md`. A red you cannot account for means the heal
   is not finished, not that the suite is nearly there.

Do not pipe a long background run through `grep` — the pipeline buffers and you
see nothing until it finishes. Let it write plainly and tail the file.

---

## Reporting a heal

For each failure say:

- **what failed** and the evidence (the call log line, the received value)
- **the root cause**, in one sentence
- **the verdict** — script or app
- **where the fix went** — page object or spec — and why. Or, for an app
  defect, the explicit words *"left red, unchanged"*

The verdict matters most. "The test was wrong" and "the app is wrong" lead to
completely different follow-ups, and a heal that does not say which has not
finished the job.

### And into the review file

Every one of these goes to `automation_savance_workplace_web/test-review.md`
(format in [[7-test-authoring]] → "The review file"):

| Category | Row to write |
|---|---|
| 6 — app defect | `App defect` — left red, evidence, manual repro. The one a human must act on. |
| 3 — checklist wrong | `Checklist vs app` — what the row claimed, what the app does, what you asserted instead. |
| Budget exhausted | `Unresolved` — the two attempts, what each ruled out, current state. |
| A fix that changed shared state | `Assumption` — e.g. a new `beforeEach` reset that changes what every later test sees. |

Categories 1, 2, 4 and 5, fixed cleanly and green alone and in a full run, need
no row. They were ordinary work.

---

## Before you call it healed

- [ ] Verdict named — **script wrong** or **app wrong** — before any edit was made
- [ ] Root cause named, not just "it passes now"
- [ ] Reproduced live before the fix was written
- [ ] Nothing was weakened to buy a pass
- [ ] The assertion still proves what the checklist row asked
- [ ] **App defects left red and untouched**, and written into `test-review.md`
- [ ] No test was skipped, softened, or deleted to clear a red
- [ ] Heal budget respected — two attempts, then the review file
- [ ] Fixed in the page object if other tests could hit it
- [ ] Sibling entries checked for the same defect
- [ ] Passes alone **and** in a full run
- [ ] Non-obvious fixes carry a comment saying why, so nobody reverts them
