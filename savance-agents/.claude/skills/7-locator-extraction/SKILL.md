---
name: 7-locator-extraction
description: Stage 07 step 1 of 3 — discover locators from a live page with Playwright MCP and turn them into page-object properties and intent-level actions: the DOM-dump-first workflow, the count/visibility/uniqueness checks every locator must survive, the traps that produce silently-wrong locators, and the harness that proves each one resolves before you commit. Use when adding or repairing locators or page actions, onboarding a new screen, or on /7-locator-extraction.
---

# Locator extraction and page-level actions

How to go from "I need to automate this screen" to a page object whose every
locator is **proven** to resolve against the real application.

The rule this whole skill exists to enforce:

> **Never write a selector you have not watched resolve on the live page.**
> A locator that was reasoned about rather than observed is not a locator, it
> is a guess — and a guess that happens to be wrong usually fails *silently*,
> as a test that passes for the wrong reason.

## Where this sits — Stage 07, step 1 of 3

Stage 07 of the Savance QA lifecycle is **automated test execution**: it takes
the checklist Stage 04 produced and turns it into a Playwright suite that
actually runs. Four skills, in a fixed order:

```
   checklist rows  (5 - QA Checklist.xlsx, or checklist.md)
        │
   1 ── [[7-locator-extraction]]  ← YOU ARE HERE
        │      page objects: locators + intent-level actions, each proven live
        │
   2 ── [[7-test-authoring]]
        │      one independent spec per checklist row
        │
   3 ── run the suite            npx playwright test tests/<file>.spec.ts
        │
   4 ── [[7-test-healing]]
               classify every red. Script wrong → fix it.
               App wrong → leave the test red and report it.
```

[[7-playwright-automation]] sits underneath all three — framework layout, house
naming, reporters, and this app's verified quirks. Load it alongside this one.

**What you hand on:** a committed `pages/<name>.page.ts` whose every locator has
been watched resolving on the live app, plus entries in the review file for
anything you could **not** prove (see "What goes to the human" at the end).
[[7-test-authoring]] then writes specs against those methods and never writes a
selector of its own.

---

## The workflow

### 0. Start from what already exists — do not re-derive

**This step is not optional, and it is the single biggest saving in the whole
stage.** Most screens are already covered. Driving a browser to rediscover a
locator that is sitting in a file is slow, expensive, and adds nothing.

Before opening a browser:

```bash
cat automation_savance_workplace_web/pages/index.ts     # what screens exist
grep -n "readonly \|async " automation_savance_workplace_web/pages/<name>.page.ts
```

Then decide, per element the checklist needs:

| Situation | What to do |
|---|---|
| A page object exists with the locator **and** an action that does what the checklist row needs | Use it. Do not open a browser. |
| A page object exists but the action is missing | Add **only** the missing locator + method. Verify just that one, live. |
| No page object for the screen | Full derivation below. |
| A locator exists but resolves to 0 / N elements now | That is a heal, not a new extraction — [[7-test-healing]] step 1 first. |

Only the elements that survive this filter go to the live browser. Record which
ones you reused, so the handoff says what was newly proven versus inherited.

### 1. Get onto the page, authenticated

Drive the real app with the Playwright MCP browser. Log in the same way a
person would.

If a login form is scripted rather than typed, set values and click through
`browser_evaluate` — it is faster and avoids per-field round trips:

```js
() => {
  document.getElementById('UserName').value = 'someone';
  document.getElementById('Password').value = 'secret';
  document.getElementById('LoginButton').click();
  return 'submitted';
}
```

A transient blank page (`about:blank`) right after navigating is common. Just
navigate again before concluding anything is missing.

### 2. Dump the DOM — do not rely on the accessibility snapshot

The snapshot hides ids, hides classes, and hides *why* an element is
invisible. Every real decision needs the DOM.

The workhorse call. Ask for a whole region at once rather than one element at
a time:

```js
() => {
  const vis = e => e ? !!(e.offsetParent || e.getClientRects().length) : false;
  return Array.from(document.querySelectorAll('#SomePanel a, #SomePanel input'))
    .map(e => ({
      tag: e.tagName, id: e.id, cls: String(e.className),
      name: e.name, type: e.type, title: e.title,
      href: e.getAttribute('href'), onclick: e.getAttribute('onclick'),
      text: (e.innerText || e.value || '').trim().slice(0, 60),
      visible: vis(e),
      rect: e.getBoundingClientRect().toJSON(),
      outer: e.outerHTML.slice(0, 250),
    }));
}
```

Include `onclick` and `href` even when you do not think you need them. They
tell you what the control *does*, which is often the fastest way to find the
next thing (see "Read the app's own JavaScript" below).

### 3. Batch-verify candidate selectors before writing any of them

Put every candidate in one object and check them together. Count is the single
most valuable field:

```js
() => {
  const sels = { nameBox: '#TextBoxName', clearButton: "input[value='Clear']", /* ... */ };
  const out = {};
  for (const [k, s] of Object.entries(sels)) {
    const els = document.querySelectorAll(s);
    const e = els[0];
    out[k] = {
      count: els.length,
      tag: e ? e.tagName : null,
      visible: e ? !!(e.offsetParent || e.getClientRects().length) : false,
      text: e ? (e.innerText || e.value || '').trim().slice(0, 60) : null,
    };
  }
  return out;
}
```

Read the result with suspicion:

| What you see | What it means |
|---|---|
| `count: 0` | Wrong selector, or the element is built on demand |
| `count: 1` | The only good answer for a single-element locator |
| `count: > 1` | **Strict-mode violation waiting to happen.** Every click through it will throw |
| `visible: false` on something you expect to see | Either genuinely hidden, or hidden by a mechanism your check missed |
| `text: ""` on something with words | Almost always because it is hidden — see the trap below |
| `rect` all zeros | A dead element. Do not use it |

### 4. Only then write the locator, with a comment saying *where in the UI it
lives* and *how a person gets to it*.

### 5. Prove the whole file with a throwaway harness

See "The verification harness" at the end. Do not skip it — it is what turns
"I checked a few" into "every single one resolves".

---
## The traps

Eleven ways a locator can look right and prove nothing —
→ `reference/traps.md`. Read the entry that matches what you are looking at;
the strict-mode trap (two anchors per row) and the `visibility`-hidden fly-out
are the two this app hits most.

## Writing the page-level actions

→ `reference/page-actions.md` for the conventions. The two that are not
negotiable: **an action encapsulates its own wait** rather than leaving it to
the test, and **anything that writes says so in capitals** in its doc comment.

## The verification harness

Before committing a page object, prove it. Write a throwaway spec that walks
every locator and every read method, log a table, and assert no failures.

```ts
const report: string[] = [];
const ok  = (n: string, v: unknown) => report.push(`  OK   ${n.padEnd(32)} ${JSON.stringify(v)}`);
const bad = (n: string, e: unknown) => report.push(`  FAIL ${n.padEnd(32)} ${String(e)}`);

const singles = { nameBox: page.nameBox, clearButton: page.clearButton /* ...every one... */ };
for (const [name, loc] of Object.entries(singles)) {
  const c = await loc.count();
  if (c === 1) ok(name, { count: c, visible: await loc.first().isVisible() });
  else bad(name, `count=${c}`);          // 0 = missing, >1 = strict-mode violation
}

// then exercise every read method inside try/catch, and every round trip
// (open→read→cancel, switch view→switch back)

console.log(report.join('\n'));
const failures = report.filter(l => l.includes('FAIL'));
expect(failures, `Failures:\n${failures.join('\n')}`).toEqual([]);
```

Why it earns its keep:

- **Counts catch strict-mode violations** before they reach a real test.
- **Exercising round trips** catches waits that were wrong in only one direction.
- **It runs against the real app**, so it catches drift that a typecheck cannot.
- Logging *every* result, not just failures, gives you the live values to write
  accurate assertions from.

Delete it once the page object is committed. Its job was to prove the file, not
to live forever.

---

## What goes to the human — the review file

Anything you could not prove is **not** a private note in a docstring. It goes
into the Stage 07 review file, because a human has to decide what to do about
it before the suite is trusted:

```
automation_savance_workplace_web/test-review.md
```

Append one entry per unproven thing, under a `## Locators` heading in the
current run's section. The format is defined once in [[7-test-authoring]]
("The review file"); from this skill the entries that belong there are:

| Raise it when | Because |
|---|---|
| A locator could not be made to resolve to exactly 1 | Every spec built on it is unsafe |
| An action could not be made to work at all (drag, delete) | The checklist rows needing it cannot be automated |
| A control writes real data and you are not certain of the blast radius | Someone must approve running it against the shared account |
| The screen behaves differently from what the checklist assumes | Stage 04's checklist may itself be wrong |
| You used a client-generated id because nothing stable existed | It will break, and the next person should know it was a knowing choice |

Never quietly downgrade one of these to a `TODO` comment. A docstring is where
you say *how* it works; the review file is where you say *what a person still
has to decide*.

---

## Checklist before you commit a page object

- [ ] Existing page objects checked first — nothing re-derived that already existed

- [ ] Every single-element locator resolves to **exactly 1**
- [ ] Every multi-element locator returns the count you expect, not a superset
- [ ] Menu/list rows checked for the duplicate icon+text anchor
- [ ] Anything that hides checked with `visibility` *and* `display` *and* rect
- [ ] Container-scoped, not document-wide
- [ ] Framework-generated ids preferred over text matching
- [ ] Dropdown interdependencies recorded
- [ ] Every action encapsulates its own wait
- [ ] Everything that writes is marked `*** SAVES FOR REAL ***`
- [ ] Harness run green against the live app
- [ ] Everything unproven written into `test-review.md`, not left as a `TODO`
- [ ] Handoff states which locators were newly proven and which were reused
