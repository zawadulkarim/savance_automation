# Test case format

Referenced from `SKILL.md` Steps 5-8. The house format for a case, the coverage
vocabulary, and the `test-cases.md` template.

## Contents
- The fourteen required fields
- Priority rubric, and the one-High-case-per-AC invariant
- Step convention (Step / Action / Expected Result), quoting, sizing — every
  case's steps begin with login, never a "logged in" precondition
- Non-duplication test
- Traceability and the four coverage statuses
- Assumptions vs Clarifications
- The `test-cases.md` template and output location

## The fourteen fields

Every test case carries all fourteen fields. None is optional; `None` or `N/A`
is a legitimate value, an empty field is not.

| Field | Rule |
|---|---|
| **Test Case ID** | `TC-001`, sequential across the whole file, zero-padded to three. Never renumber on a later round — a removed case leaves a retired ID recorded in the Assumptions section. |
| **Title** | What is being verified, in one line, specific enough to identify the case in a filtered list. `Host with "Out" status cannot be selected on the Kiosk` — not `Test host selection`. |
| **Acceptance Criteria Reference** | The AC ID(s) from the Stage 04 workbook, e.g. `AC2003`, plus the rule number where the workbook numbers them: `AC2003 r2`. Never `N/A` — an untraceable case does not belong in the file. |
| **Ticket** | The client ticket/bug/observation this case's AC belongs to — its title exactly as given in the source (the Stage 04 spec's ticket reference, or the AC document's own per-item ticket description when a run bundles several client tickets into one AC document). In a normal single-ticket run every case carries the same value. In a batch/bundle ticket folder (see [[1-requirement-analysis]]'s "distinct ask" slicing, or a client-supplied AC document covering several bugs at once), this is what lets a reviewer or [[8-asana-bug-report]] trace a case, and any defect it finds, back to the ticket it actually belongs to. Never `N/A` — if the source names no ticket at all, use the ticket folder's own name and say so once in Assumptions. |
| **Test Type** | One of the nine, spelled exactly as in Step 4. One type per case; a case spanning two types is two cases. |
| **Priority** | `High` / `Medium` / `Low`, per the rubric below. |
| **Preconditions** | State that exists **before** step 1 and that the tester cannot reach just by following the steps — records already in the system, a setting already enabled elsewhere, another case's postcondition. **Never "logged in" or "on page X"** — those are steps now (see Steps below), not preconditions, even when the case is chained after another case's postcondition. |
| **Test Data** | Concrete values, not descriptions. `Visitor name: "QA Test Visitor 01"` — not "a valid visitor name". Where the value is arbitrary, say so and still give one. |
| **Steps** | Numbered, ordered, one action each, with a per-step expected result. **Step 1 is always login** — see the Steps convention below. |
| **Expected Results** | The case-level outcome — what is true when every step has passed. |
| **Postconditions** | The state left behind, and the cleanup needed to leave the system fit for the next test. `None` when the case changes nothing. |
| **Automation Candidate** | `Yes` / `No`, with the reason on `No`. |
| **Playwright Verified** | `Yes` / `No` / `N/A`, per Hard rule 5. |

**Priority rubric.** High: the primary path of the acceptance criterion; any
case whose failure blocks sign-off; permission enforcement, data loss, and
anything the client asked for by name. Medium: secondary paths, validation
messages, state and UI detail, persistence. Low: cosmetic detail, rare
combinations, low-traffic configuration permutations.

> **Invariant:** every AC has at least one High case. If all of an AC's cases
> came out Medium or Low, you have missed its main path — go back.

**Steps.** Each step is `Step | Action | Expected Result`, and **step 1 is
always login** — no case opens mid-workflow:

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the Login page (`https://test.savanceworkplace.com/Login.aspx`). | The Login page loads, showing **"User Name:"**, **"Password:"** and the **"Log In"** button. |
| 2 | Enter the QA test account's user name and password, then click **"Log In"**. | Redirected to the Home page (Status Board). |
| 3 | Navigate to **Admin > Question Manager** and open the **"Manage Host Profiles"** modal. | The modal opens with the **"Show Status"** checkbox visible. |
| 4 | Tick **"Prevent Out Status Type Host Selection"** and click **"Save"**. | The modal closes and a confirmation message is displayed. |

- **A case is executable standalone by someone with zero prior context.**
  "Logged in as admin" as a precondition used to stand in for this; it no
  longer does. Every case's first steps are the literal login sequence
  (navigate to the login page, enter credentials, submit) followed by the real
  menu path to the target screen, in the app's own labels — confirmed live,
  never invented. This holds even for a case chained after another case's
  postcondition (e.g. a persistence check that re-logs-in to prove the state
  survived a fresh session) — re-authenticating is the point of that case, not
  boilerplate to skip.
- Test data that is the same across most of a suite's cases (a QA test
  account's credentials) can be named once and referenced (`` `TEST_USERNAME` /
  `TEST_PASSWORD` from `.env` ``) rather than re-typed as a literal value in
  every case's Test Data field — never print the actual credential values into
  the file.
- The action is what the tester *does*; the expected result is what the system
  *shows*. A step with no observable result is a setup step — fold it into
  Preconditions or into the previous step.
- Quote every user-facing string **verbatim** in double quotes, punctuation
  included. Bold named UI elements. This is the house convention shared with
  [[4-acceptance-criteria-generation]] and [[8-asana-bug-report]].
- 3-8 steps is the working range for the case's *own* action once login and
  navigation are counted separately — most cases land around 5-7 steps total
  once the 2-4 login/navigation steps are included. Over ~12, the case is
  doing two things.
- Never write "repeat for each X" — enumerate, or make it a data-driven family
  of cases with distinct IDs.

**Non-duplication.** Two cases are duplicates when they would fail for the same
reason. Differing preconditions or data are what make two similar cases
distinct — if you cannot name the difference in one clause, delete one.

## Step 6 — Traceability and coverage

Build the matrix **from the cases you actually wrote**, by walking the AC list
and looking each one up. Never write it from intent.

| Coverage | Means |
|---|---|
| **Covered** | Every acceptance rule in that AC has at least one case asserting it, and none of those cases rests on an unverified assumption. |
| **Partially Covered** | At least one rule covered and at least one not. Name which rules are uncovered. |
| **Not Covered** | No case. Requires a stated reason — out of scope, blocked, needs an account you don't have. |
| **Requires Clarification** | Cannot become a pass/fail case until someone answers a question. |

> **Invariant:** every `Not Covered` and every `Requires Clarification` row has
> a matching entry in the Assumptions / Clarifications section. A bare status
> with no explanation is a claim with nothing behind it, and no stage after this
> one re-derives coverage to catch it.

**The Coverage cell holds only the status word** (`Covered`, `Partially
Covered`, `Not Covered`, `Requires Clarification`) — never a caveat appended in
parentheses (`Covered (TC-010's display step not exercised live)`). Put the
caveat in the table's fourth column, **Notes**, instead. The workbook colours
the Coverage column by an exact string match against the four status words;
a caveat folded into that cell breaks the match silently and the row loses its
colour-coding with no error to catch it.

The **coverage summary** is a short paragraph plus the counts: total cases, by
type, by priority, ACs fully covered / partially / not, automation candidates,
and how many cases are Playwright-verified. Two sentences of prose on what the
suite does and does not prove.

## Step 7 — Assumptions and clarifications

Two separate lists, and the distinction matters:

- **Assumption** — you proceeded, and named what you assumed. The case is
  written and executable; if the assumption is wrong the case is wrong.
  `Assumed the confirmation message wording; not observed live.`
- **Clarification required** — you could not proceed. No case, or a case that
  cannot state its expected result. Phrase it as a question someone can answer.

Both carry the test case IDs they affect, so a wrong assumption can be traced to
what it damaged.

## Step 8 — Write `test-cases.md`

````markdown
# Test Cases

**Review Status:** DRAFT
**Acceptance Criteria:** 4 - Acceptance Criteria.md — APPROVED <reviewer>, <date>
**Last Updated:** <YYYY-MM-DD>

## Feature
<feature name, ticket id, and one line on what it does>

## Acceptance Criteria

### AC-01
<the criterion, quoted from the Stage 04 workbook>

## Test Cases

### TC-001 — <title>

**Acceptance Criteria:** AC-01
**Ticket:** <the client ticket/bug/observation title this AC belongs to>
**Test Type:** Functional / Positive
**Priority:** High

**Preconditions:**
- ...

**Test Data:**
- ...

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the Login page. | ... |
| 2 | Enter credentials and click **"Log In"**. | ... |
| 3 | ... (navigate to the target screen, then the case's own action) | ... |

**Expected Results:**
- ...

**Postconditions:**
- ...

**Automation Candidate:** Yes
**Playwright Verified:** Yes

## Traceability Matrix

| Acceptance Criteria | Test Cases | Coverage | Notes |
|---|---|---|---|

## Coverage Summary

...

## Assumptions / Clarifications

...
````

**Output location** — the ticket folder every lifecycle stage shares:

```
tickets/<ticket-id> - <Ticket name>/test-cases.md
```

The canonical filename stays `test-cases.md` rather than taking a house number
prefix, for the same reason `test-review.md` does: it is read by machine at
Stage 07, and a stable name is worth more there than a position in the folder
listing. With no ticket behind the run, write it to the working directory.
