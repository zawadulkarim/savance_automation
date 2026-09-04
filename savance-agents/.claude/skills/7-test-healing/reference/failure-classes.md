# The six failure classes

Referenced from `SKILL.md` Step 2. Classify before you edit: the class decides
whether the fix belongs in the page object, in the spec, or nowhere at all.

## Contents
1. Locator wrong or ambiguous
2. The test's assumption was wrong
3. The app genuinely behaves differently
4. Cross-test contamination
5. Genuine flake or a bad wait
6. The app is genuinely broken - hands off the test

### 1. Locator wrong or ambiguous

```
Error: strict mode violation: locator('#PanelMore a[href="javascript:ClearRollCall();"]')
  resolved to 2 elements:
    1) <a id="HyperLink2" href="..."><img></a>       ← icon
    2) <a id="HyperLink3" href="...">Clear Roll Call</a>  ← words
```

Go to [[7-locator-extraction]] and re-derive it. Fix in the **page object** so
every test benefits at once. Then check whether sibling entries in the same map
have the same defect — this one affected three menu rows, not just the one that
failed.

### 2. The test's assumption was wrong

`readButtonsOnMainStrip()` returned everything except "Home" and "More Options".
Reading the method showed it deliberately iterates only the buttons a setting
can *move*; Home never moves and More Options is the destination.

The app was right and the test was wrong. Fix the spec — and if the API invited
the mistake, add the method that expresses the real intent
(`readAllTopMenuItems()`) with a comment saying why the other one is not it.

### 3. The app genuinely behaves differently

Two of these, both of which would have been "fixed" wrongly by adjusting numbers
until green:

- Two different people share a name, so a disjointness assertion across two
  filtered lists was invalid. Replaced with subset + difference checks, which
  prove the filter works without needing unique data.
- `Staff + Visitor === everybody` was false (6 + 7 ≠ 31) because not everyone
  has one of those types.

Rewrite the assertion around the **real invariant**, and put the finding in the
spec header so nobody reverts it.

### 4. Cross-test contamination

The tell is **passes alone, fails in the suite**. Always run the failing test in
isolation early:

```bash
npx playwright test tests/home.spec.ts -g "SC-39"
```

Green alone + red together = shared state. The usual culprits are server-side
saved preferences, a modal left open, or a filter left applied.

A worked example: `selectOption({label: 'Out'})` timed out with
`did not find some options`. Live probing showed a *dependent dropdown* — the
Status list is filtered by Status Type, so choosing "In" shrank it from 11
options to 2 and "Out" genuinely did not exist. An earlier test had set Status
Type, and that choice **persisted server-side across logins**.

Two lessons that generalise:

- A fresh login is not a fresh start.
- The obvious reset may be incomplete. Pressing Clear reset the *values* but
  left the dependent list stale; only a reload rebuilt it. Verify your reset
  actually resets, by reading the state back afterwards.

### 5. Genuine flake or a bad wait

Before calling anything flaky, **try to reproduce it in a loop**:

```ts
for (let round = 1; round <= 3; round++) {
  await home.goto();
  const t0 = Date.now();
  try {
    await page.locator('#Target').click({ timeout: 20_000 });
    results.push(`round ${round} PLAIN  ok in ${Date.now() - t0}ms`);
  } catch { results.push(`round ${round} PLAIN  TIMED OUT after ${Date.now() - t0}ms`); }
  // ...same again with the proposed fix, and compare
}
```

If it will not reproduce, still fix the *mechanism* the call log named. Do not
add a retry and move on.

### 6. The app is genuinely broken — hands off the test

The evidence for this verdict is always the same shape: you reproduced the
failure **by hand**, on the live app, doing what the checklist row says, and the
app did the wrong thing while you watched.

That is the whole bar. Not "the assertion looks reasonable" — you have to have
seen it.

What you do:

1. **Change nothing.** Not the assertion, not the locator, not the wait.
2. **Prove the test itself is sound**, so nobody can dismiss the finding as a
   bad test. Run it alone; check the failing `expect` reads a real value, not
   `""` or `undefined` from a mis-timed read; confirm it is not category 1, 4 or
   5 wearing a disguise.
3. **Write it into the review file** as an app defect, with: the test id, the
   expected and received values, the manual reproduction steps, and the plain
   statement *the test was not modified*.
4. **Say it out loud in the handoff.** "20 green, 2 red — both red are app
   defects, listed in `test-review.md`" is a successful run, and must be
   reported as one rather than buried as a partial failure.

Filing it in Asana is [[8-bug-reporting]]'s job, not yours, and it happens on a
human's say-so.

**The tell that you got this wrong:** you are about to write a commit message
like "relax the DOB assertion — the app allows it". That sentence is a bug
report with the wrong verb.

---
