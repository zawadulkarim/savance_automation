# Writing page-level actions

Referenced from `SKILL.md`. Once the locators are proven, these are the
conventions for the intent-level methods a spec actually calls.

## Contents
- Name things the way a user would
- An action encapsulates its wait
- Make toggles idempotent
- Mark anything that writes, in capitals, in the doc comment
- Provide a reset when the app persists state
- Keep a real method when you rename one
- Document what you could not verify

Locators are half the job. The other half is methods that say what a *person*
is doing.

### Name things the way a user would

| Thing | Rule | Example |
|---|---|---|
| Locator | `camelCase`, what a user calls it | `nameBox`, `clearButton`, `miniViewButton` |
| Locator matching many | plural | `tableRows`, `miniTiles` |
| Reference data | `SCREAMING_SNAKE`, exported above the class | `COLUMN_CHOOSER_HEADING` |
| Method that acts | verb first | `pressSearch()`, `openColumnChooser()` |
| Method that reads | `read…` / `count…` / `is…` / `get…` | `readCounterText()`, `countRows()`, `isFullScreen()` |

### An action should encapsulate the wait, not leave it to the test

```ts
async openColumnChooser(): Promise<void> {
  await this.columnChooserButton.click();
  await this.columnChooserDialog.waitFor({ state: 'visible' });
}
```

A test that has to know what to wait for after calling your method means the
method is unfinished.

Match the wait to what actually happens. `state: 'detached'` when a dialog is
destroyed on close; `state: 'hidden'` when it is merely hidden. Getting this
wrong produces a hang, not an error.

### Make toggles idempotent

Never assume a starting state — especially when the app remembers preferences
server-side.

```ts
async setRowTicked(rowNumber: number, shouldBeTicked: boolean): Promise<void> {
  const box = this.rowCheckboxFor(rowNumber);
  if ((await box.isChecked()) === shouldBeTicked) return;   // already right
  await box.click();
  await this.waitForRefreshToFinish();
}
```

### Mark anything that writes, in the doc comment, in capitals

```ts
/**
 * The tick box at the start of one person's row.
 *
 * *** TICKING THIS SAVES FOR REAL *** It is not a "select this row" box —
 * it adds or removes that person from your My Friends list.
 */
```

Discover this by reading the handler (`onclick="MyFriend(chk107144)"`), not by
assuming from appearance. A box that looks like row selection was a friend
toggle.

### Provide a reset when the app persists state

If preferences survive reload *and* re-login, no amount of fresh logins makes
tests independent. Ship the reset as a page-object method with the reasoning
attached:

```ts
/**
 * Put the board back to a known starting state.
 * Filters are saved SERVER-SIDE per user — they survive reload and re-login.
 * Clear alone is not enough: it resets the values but leaves the dependent
 * Status list stale, so a reload is required to rebuild it.
 */
async resetFilters(): Promise<this> {
  await this.pressClear();
  await this.goto();
  return this;
}
```

### Keep a real method when you rename one

```ts
/** Old name for `isFiltersPanelOpen()`. Kept so existing tests still run. */
async isFiltersPanelVisible(): Promise<boolean> {
  return this.isFiltersPanelOpen();
}
```

### Document what you could not verify

If a behaviour could not be confirmed, say so in the docstring and make the
test **skip with that reason**. Never assert something you did not observe.

---
