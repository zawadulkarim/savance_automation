# Savance Workplace app behaviours (all verified live)

Referenced from `SKILL.md`. These are the app quirks that make an otherwise
sensible assertion wrong. Read the entry for the screen you are working on.

## Contents
- ASP.NET WebForms in general (generated ids, postbacks)
- Fly-out panels are hidden with `visibility`, not `display`
- Toolbar items relocate, they never disappear
- Login page (including the 8-attempt account lockout)
- Status Board (jqGrid) - never wait with a sleep
- Statuses
- Question Manager - the one screen that is not WebForms

### ASP.NET WebForms in general
- Server-control ids (`#LoginUser_UserName`, `#DropDownListStatus`,
  `#ContentPlaceHolder1_...`) are stable across redeploys. Prefer them.
- Much navigation is `__doPostBack` or `javascript:`, so an `href` does not
  always identify a target. `Calendar` is `javascript:goToCalendar()` which
  appends `?clientTZO=<offset>`; assert the landing URL, not the href.
- Control ids contain the app's internal vocabulary, not the UI wording:
  Timesheet is `TimeRecords`, Send Message is `MassText`, and Admin is
  misspelled `Adminstrations`. Watchlist's label span is `Label1SettingsWatchlist`.

### Fly-out panels are hidden with `visibility`, not `display`
`#PanelStatusPopup` and `#PanelMore` are **always** in the DOM with
`display: block`, a real bounding box, and a truthy `offsetParent`. They are
hidden with `visibility: hidden`.

- Playwright's `toBeVisible()` / `isVisible()` read this correctly — use them.
- Any check based on `display` or `offsetParent` will report them as visible
  when they are not. This burns anyone probing the DOM manually.

Both triggers are **toggles** (`hidePanelIfVisible(...)`), not openers, so
`openStatusMenu()` / `openMoreOptionsMenu()` must check first and only click
when closed — otherwise the second call closes the panel.

### Toolbar items relocate, they never disappear
Whether an item sits on the main strip or inside the More Options fly-out is
configuration, read from My Info & Settings → My Settings
(`#ContentPlaceHolder1_CheckBoxSettings*`). Checked → main strip; unchecked →
fly-out. On the current environment Visitor Sign In, Watchlist and Clear Roll
Call are unchecked and therefore live in the fly-out.

So a test must assert **which of the two homes** an item is in
(`ToolbarPage.findWhereButtonIs()` returns
`'main strip' | 'more options menu' | 'nowhere'`),
not that it is present on the strip. `'nowhere'` is a real finding.

`Help Desk` is always in the fly-out regardless of configuration — exclude it
(`ALWAYS_IN_MORE_OPTIONS`) when comparing the fly-out against the hidden set.

### Login page
- **The account locks after 8 failed attempts** ("Invalid attempt 1/8"). Every
  negative test must use a non-existent username (`no.such.user.qa`), never
  `SAVANCE_USERNAME`. This is the single most important rule in the repo.
- Blank-submit validation is client-side `RequiredFieldValidator`s:
  `#LoginUser_UserNameRequired` / `#LoginUser_PasswordRequired`. They render a
  `*` that starts at `visibility: hidden` and flips visible on failure, and the
  real message is in the **`title` attribute** ("User Name is required."), not
  the text. A failed validation blocks the postback entirely.
- Both credential inputs are `maxlength=255`, so oversized input is truncated
  by the browser rather than rejected by the app.
- Two *different* failure messages exist and mean different things:
  `Invalid Username or Password` (credentials) and `Error contacting Server`
  (the test environment's SQL backend drops intermittently). A negative test
  must assert the outage message is **absent**, or a flaky environment passes
  as a green negative test.
- Signing out lands on `Login.aspx?SignOut=1`. Visiting `Login.aspx` while
  authenticated redirects to `/default.aspx` — note the **lowercase** `d`,
  so compare case-insensitively.

### Status Board (jqGrid) — never wait with a sleep
The two refresh triggers behave completely differently:

- **Search** → client-side jqGrid AJAX reload, no navigation. The **previous
  rows stay in the DOM for ~1.4 s**, so reading straight after the click
  returns stale data.
- **Clear** → ASP.NET async postback that rebuilds the grid contents. The grid,
  the overlay and the pager all survive it.

Neither a load-state wait nor a fixed timeout is reliable. `HomePage` gates on
the two signals the app actually exposes — jqGrid's `#load_TableRows` overlay
and `PageRequestManager.get_isInAsyncPostBack()` — waits for the reload to
*start* then finish, and finally requires the rendered row count to agree with
the pager across several consecutive samples. This was the root cause of two
flaky failures; **do not replace it with a timeout.**

Also: **`networkidle` never arrives** — the board polls on an interval.
Never gate on it. `HomePage.waitUntilTableIsReady()` is the correct wait.

The pager has four states, all handled: `View 1 - 31 of 31 , Refreshed: 6:58 PM`,
the same line prefixed `[Results Limited]` when the server caps the result set,
`No records to view`, and *absent entirely* — which happens in **Mini view**,
not after Clear.

**Clear does not empty the board — it widens it.** Clear resets every dropdown
to `<ALL>` and *unchecks* "Within Selected Group". Unchecking removes a
restriction, so you end up seeing MORE people, not fewer (verified: 31 rows,
pager intact). Assert on the filter *controls*, not a row count — the count
afterwards is not a fixed figure.

**Filter state is saved SERVER-SIDE per user.** The dropdowns and the
"Within Selected Group" checkbox come back exactly as you left them after a
reload *and* after signing out and back in. (Free-text boxes do not persist.)
So a fresh login is **not** a fresh start, and one spec's filter choice will
silently change what the next spec sees. Reset with `HomePage.resetFilters()`
in a `beforeEach` for any suite whose outcome depends on who is on the board.

**The Status dropdown is filtered by Status Type.** Choosing the type `In`
shrinks the Status list from eleven options to two, so a later
`selectOption({label:'Out'})` waits 30 s for an option that no longer exists.
Pressing Clear resets the *values* but leaves that list stale — only a page
reload rebuilds it, which is why `resetFilters()` does Clear **then** `goto()`.

### Statuses
`Admin → Statuses` (`ManageStatuses.aspx`, `#ContentPlaceHolder1_GridViewStatuses`)
is the authoritative list and drives the topmost dropdown, the Update Status
modal and the board filter. When checking "the dropdown lists every configured
status", read **both sides from the app** — a hard-coded list still passes
after someone adds an eleventh status the dropdown failed to pick up.

### Question Manager is the one screen that is not WebForms
`QuestionManager.aspx` is a shell whose body is a same-origin **iframe** hosting
an Angular Material SPA. Everything — including dialogs and dropdown overlays —
lives inside that frame, so `QuestionManagerPage` uses `*InApp` helpers. A plain
`this.click()` there silently finds nothing.

- Angular **generates and renumbers** ids (`mat-select-0`) — never use them.
  What is stable: a question box carries its **QuestionSys as its element id**
  (`[id='30966']`), jsPlumb anchors are `{qid}_source` / `{qid}_target`, and the
  terminal boxes use reserved ids `0` and `-2`.
- Those ids are not valid CSS identifiers — always `[id='...']`.
- A question saves only once it has **both** a prompt and a field, and selecting
  the field is the commit trigger. Until then it sits at id `-1` with no delete
  button; the only way to discard it is `reloadApp()`.
- Unresolved: Delete Question appears to be a no-op, and re-routing a branch by
  dragging could not be made to work. Both are flagged in the page object.
