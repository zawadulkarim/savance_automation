# When a *green* test is the bug

Referenced from `SKILL.md`. A test that passes because it never actually ran its
check is worse than a red one. Also carries the signature failure messages and
what each really means.

## Contents
- A function passed as a string is never executed
- A readiness check that is vacuously true
- An unbounded polling loop
- Signature messages and what they mean
- The endless-polling app

## Silent no-ops: when a *green* test is the bug

The worst failures never go red. Check for these whenever a wait looks
suspicious or a test is "too fast".

### A function passed as a string is never executed

Playwright treats a string argument as an **expression**, not a function to
call. Passing `` `() => {...}` `` builds a function object and stops there:

```ts
page.evaluate("() => false")          // → undefined   (always falsy)
page.waitForFunction("() => false")   // → resolves IMMEDIATELY (object is truthy)
```

Neither throws. The consequences were severe: every `waitForFunction` returned
instantly and waited for nothing, and a poll loop gated on the `evaluate` result
could never finish, spinning until the whole test timed out.

The fix is one pair of brackets — make the browser call it:

```ts
const runInBrowser = (check: string) => `(${check})()`;
await page.waitForFunction(runInBrowser(IS_READY), undefined, { timeout: 45_000 });
```

Verified after the fix: `waitForFunction` correctly timed out on a false
condition and waited ~1215 ms for a real DOM change. Prefer passing a **real
function** whenever it does not need browser-only globals.

### A readiness check that is vacuously true

A check written for a table asked "do the drawn rows match the pager?". On a
view with no rows and no pager it answered *yes* instantly, so
"switch view and wait for it to load" passed against an empty screen.

Every readiness predicate needs a positive signal — something that must
**appear** — not just the absence of a negative one.

### An unbounded polling loop

```ts
while (goodChecksSoFar < timesInARow) { /* no overall deadline */ }
```

If the condition can never be satisfied, this burns the entire test timeout and
reports a meaningless "Test timeout exceeded". Give such loops their own
deadline and a message that says what was actually wrong:

```ts
if (Date.now() > giveUpAt) {
  throw new Error('The board never stopped moving — it kept flipping between ' +
                  '"finished" and "still working" for 60 seconds.');
}
```

---

## Signature messages and what they mean

| Message | Almost always means |
|---|---|
| `strict mode violation ... resolved to N elements` | Selector needs scoping — check for an icon+text pair |
| `did not find some options` | The `<select>` genuinely lacks that option — look for a dependent dropdown upstream |
| `click action done` then `waiting for scheduled navigations to finish` | The click worked; the app never goes quiet. Use `noWaitAfter: true` plus an explicit `waitForURL` |
| `Timeout ... waiting for element to be visible` on an element you can see | Hidden by `visibility`, or a zero-size dead duplicate, or an ancestor is `display:none` |
| `Test timeout exceeded` with no useful frame | An unbounded wait loop — add a deadline |
| Title/text is `""` | Read mid-navigation, or read from a hidden element (`innerText` is layout-dependent) |
| Passes alone, fails in suite | Cross-test contamination |

### The endless-polling app

Apps that poll on a timer never reach `networkidle`, and a plain `click()` can
hang waiting for navigations to settle. The pattern:

```ts
// `noWaitAfter` is doing real work — do not drop it. The board keeps talking
// to the server forever, so Playwright is never told things went quiet.
await this.page.locator(selector).click({ noWaitAfter: true });
await this.page.waitForURL(`**${expectedUrlPart}**`, { timeout: settings.NAVIGATION_TIMEOUT });
await this.page.waitForLoadState('domcontentloaded');
```

**Then check the same-URL case.** If the destination equals the current address,
`waitForURL` is satisfied *before the click*, so both waits pass against the old
document and the next read races the navigation — producing an empty title. Wait
for the new document explicitly, passing a real function, not a string:

```ts
await this.page.waitForFunction(
  () => document.readyState !== 'loading' && document.title.trim().length > 0,
  undefined,
  { timeout: settings.NAVIGATION_TIMEOUT },
);
```

---
