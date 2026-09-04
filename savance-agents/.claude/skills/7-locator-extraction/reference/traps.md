# Traps that produce silently-wrong locators

Referenced from `SKILL.md`. Each of these yields a selector that resolves, or
appears to, while asserting nothing — the failure mode that makes a test pass
for the wrong reason. Consult the entry that matches what you are looking at.

## Contents
- Two anchors per row — the strict-mode trap
- `innerText` is empty for hidden elements
- Hidden by `visibility`, not `display`
- Unanchored selectors that reach the whole document
- Zero-size dead elements
- Elements that relocate instead of duplicating
- Dependent dropdowns
- Framework-generated ids beat text matching
- "Which one is selected?" is usually a class, not a state
- Read colour from the attribute, not the computed style
- Read the app's own JavaScript to find the next element

Each of these was hit for real. Each produces a locator that looks right.

### Two anchors per row — the strict-mode trap

Menus and toolbars very often render each row as **an icon link and a text
link, side by side, pointing at the same place**:

```html
<td><a href="Watchlist.aspx"><img ...></a></td>   <!-- icon -->
<td><a href="Watchlist.aspx">Watchlist</a></td>   <!-- words -->
```

So `#Menu a[href='Watchlist.aspx']` matches **2** elements and every click
through it dies with a strict-mode violation.

Scope to the cell that holds the words — the half a person actually clicks:

```ts
"#Menu td:nth-child(2) > a[href='Watchlist.aspx']"
```

Always run the count check on menu rows. This one is invisible until click time.

### `innerText` is empty for hidden elements

Reading the labels of a menu while it is closed returns `['', '', '', '']`, and
it is very easy to conclude the rows have no text and go looking for a
different selector.

`innerText` is layout-dependent. Open the panel first, *then* read. Use
`textContent` if you genuinely need the words while hidden.

### Hidden by `visibility`, not `display`

Fly-out panels are frequently always in the DOM with `display: block`, a real
bounding box, and a truthy `offsetParent` — hidden only by
`visibility: hidden`.

- Playwright's `isVisible()` / `toBeVisible()` read this correctly. **Use them.**
- A manual `offsetParent` / `display` probe reports them as visible. This is
  the single most common way a manual DOM probe misleads you.

When probing by hand, check all three: `display`, `visibility`, and
`getBoundingClientRect()`.

### Unanchored selectors that reach the whole document

`.some-grid-class th` looked correct and returned **79** cells, of which 69
were switched-off columns, with the first heading being one no user has ever
seen.

Two fixes, apply both:

```ts
// 1. anchor to this screen's container   2. let Playwright filter visibility
page.locator('#gview_TableRows .ui-jqgrid-htable th:visible')
```

`:visible` in the selector is also far faster than looping `nth(i).isVisible()`
over 79 elements — that is 79 round trips.

### Zero-size dead elements

A page can contain a *second*, older control for the same job that is no
longer reachable:

```
a.selectColumns → rect 0x0, parent display:none   ← dead, ignore
td[title='Choose Columns'] → 22x20, in the pager  ← the real one
```

`count: 1` and `visibility: visible` were both true for the dead one. Only the
`rect` and the **parent's** `display` gave it away. When something will not
click, check the ancestors, not just the element.

### Elements that relocate instead of duplicating

Switching a view can *physically move* a container rather than build a second
one. A grid's id stayed valid across both views — but in the second view it was
emptied and its pager removed, so a readiness check written for the first view
returned "ready" instantly against an empty screen.

Check whether an id survives a mode switch, and whether it still *means* the
same thing.

### Dependent dropdowns

One `<select>` can be repopulated by another. Choosing a "Status Type" shrank
the "Status" list from 11 options to 2 — so `selectOption({label:'Out'})` waited
30 s for an option that no longer existed.

When you meet a group of filters, record each dropdown's options **after
changing each of the others**. Note the dependency in the page object.

### Framework-generated ids beat text matching

Prefer ids the server framework generates. They are ugly but stable, and they
survive relabelling:

```ts
// fragile — breaks on a rename, and matches a decorative inner div
page.locator("div.as_ul:text-is('Standard')")

// stable
page.locator('#__tab_ContentPlaceHolder1_TabContainerMainBoard_TabPanelStandard')
```

Framework id conventions worth recognising: ASP.NET WebForms
(`#ContentPlaceHolder1_*`), AjaxControlToolkit tabs (`#__tab_<panel>` for the
clickable part, `#<panel>_tab` for the part that carries the active class),
jqGrid (`#gview_<id>`, `#gbox_<id>`, `#load_<id>`).

**Exception:** ids that a client framework *generates and renumbers* (Angular's
`mat-select-0`) are the opposite — never use those.

### "Which one is selected?" is usually a class, not a state

Active tabs are marked with a class on a *sibling or parent*, not the element
you click:

```ts
private async isTabActive(panelId: string): Promise<boolean> {
  const tab = this.page.locator(`#${panelId}_tab`);
  if ((await tab.count()) === 0) return false;
  const classes = (await tab.getAttribute('class')) ?? '';
  return classes.split(/\s+/).includes('ajax__tab_active');
}
```

Split on whitespace. Do not use `String.includes` on the class attribute —
`"tab_active_x"` would match `"tab_active"`.

### Read colour from the attribute, not the computed style

Apps that colour-code rows usually write the configured value into an
attribute (`status-color="#71D637"`, `bgcolor="#71D637"`). Read that.

The computed background can be altered by hover, selection, striping or theme,
so `getComputedStyle` gives you a value that is right on your machine and wrong
in CI.

### Read the app's own JavaScript to find the next element

When a control runs a function, print the function. It names the elements you
need, with no hunting:

```js
() => ClearRollCall.toString()
// → ShowMasterMessageBoxPopup('Clear Roll Call Status', 'Are you sure...', ClearRollCallConfirmed)

() => ShowMasterMessageBoxPopup.toString()
// → $get('SpanMasterMessageBoxHeader') ... ButtonMasterMessageBoxYes / ...No
```

Two calls produced the entire confirmation-dialog contract — heading, message,
Yes and No — without opening it once.

---
