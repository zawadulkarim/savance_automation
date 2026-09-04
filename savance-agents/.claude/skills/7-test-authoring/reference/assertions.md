# Assertions that actually prove something

Referenced from `SKILL.md`. The whole point of the suite is that a green test
means the behaviour works. Each entry below is a way a green test can mean
nothing instead.

## Contents
- Add a control assertion wherever a check could pass for the wrong reason
- Assert the invariant, not the current number
- Never assume test data is unique
- Assert what the app does, not what the checklist says
- Prefer a message on every non-obvious `expect`
- Check the round trip, not just the outgoing leg
- Cross-check two sources the app exposes
- Beware checks that cannot fail

### Add a control assertion wherever a check could pass for the wrong reason

If you assert the password field is masked, also assert the username field is
*not* — otherwise a page that masked every input would pass.

Applied here: asserting a filtered board shows only "Out" people is weak on its
own, because a broken filter returning **zero** rows also passes a
"every row is Out" loop vacuously. So assert the count first:

```ts
const statuses = await homePage.readAllStatuses();
expect(statuses.length, 'the test data should have somebody Out').toBeGreaterThan(0);
for (const status of statuses) expect(status.trim()).toBe('Out');
```

**Any `for` loop over results needs a non-empty check before it.** An empty
list passes every loop.

### Assert the invariant, not the current number

Clear does not restore a default board — it removes a restriction, so the row
count afterwards is not a fixed figure. Asserting `31` would encode today's
test data.

```ts
// Deliberately NOT a row count. Clear also unticks "Within Selected Group",
// which removes a limit rather than adding one, so the number afterwards is
// not predictable.
for (const [name, chosen] of Object.entries(await homePage.getSelectedFilters())) {
  expect(chosen, `"${name}" should be back to ${EVERYTHING_OPTION}`).toBe(EVERYTHING_OPTION);
}
```

Assert on the **controls**, which have a defined state, not on the **data**,
which does not.

### Never assume test data is unique

Two different people shared a name. An assertion that names in one filtered
list cannot appear in another was therefore wrong — and it looked completely
reasonable.

Before writing set-logic over data, check for duplicates. Then prefer:

- **subset** checks (`every filtered name appears in the full list`)
- **difference** checks (`the two filtered lists are not equal`)

over **disjointness** or **sums**, which need uniqueness to be meaningful.
`staff.length + visitors.length === everybody.length` was also false: 6 + 7 ≠ 31,
because not everyone has one of those two types.

### Assert what the app does, not what the checklist says

A checklist said the menu closes on *"clicking elsewhere or pressing Escape"*.
Escape does nothing. Clicking elsewhere works.

Test the behaviour that exists, and record the discrepancy in the file header
and to the user. Do not write a failing test to make a point, and do not
silently pretend the checklist was right.

Same for wording: a checklist said clicking a name "opens their detail page".
It opens a panel over the board. The test asserts the panel — and the header
says so.

### Prefer a message on every non-obvious `expect`

```ts
expect(onStrip, `"${item}" should be on the top menu`).toContain(item);
expect(tiles, 'Mini view should not be empty').toBeGreaterThan(0);
```

The message is what a non-author reads at 5pm. Say what the failure *means*,
not what the code did.

### Check the round trip, not just the outgoing leg

A view switch, a dialog, a collapse — assert the state before, after, and
after coming back:

```ts
const openWidth = await homePage.readFiltersPanelWidth();
await homePage.toggleFiltersPanel();
expect(await homePage.isFiltersPanelOpen()).toBe(false);
expect(await homePage.readFiltersPanelWidth()).toBeLessThan(openWidth);
await homePage.toggleFiltersPanel();
expect(await homePage.isFiltersPanelOpen()).toBe(true);
expect(await homePage.readFiltersPanelWidth()).toBe(openWidth);
```

This is where "it collapsed" versus "it disappeared entirely" gets caught.

### Cross-check two sources the app exposes

When the app states a fact twice, compare them. It catches half-rendered
states no single read would:

```ts
const rows = await homePage.countRows();
expect(await homePage.readTotalFromCounter()).toBe(rows);   // pager vs drawn rows
```

### Beware checks that cannot fail

Ask of every assertion: *what state of the app would make this red?* If the
answer is "none", delete or strengthen it.

Two real examples:

- `isFiltersPanelVisible()` tested the outer box, which never hides — only
  narrows. It could not fail. The inner fields container was the honest signal.
- A readiness check written for a table returned "ready" instantly on a view
  that has no rows, so a test asserting "the view loaded" passed against an
  empty screen.

---
