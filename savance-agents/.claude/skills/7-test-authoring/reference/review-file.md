# The review file — test-review.md

Referenced from `SKILL.md`. This stage owns `test-review.md`: the list of things
a human must decide. The suite and this file are both deliverables; neither run
is finished without the other.

## Contents
- Format, with a worked example
- The seven categories that must be raised
- What must NOT be raised (padding buries the rows that matter)
- Before you call it done

Every Stage 07 run produces one, and it is the stage's second deliverable
alongside the specs themselves:

```
automation_savance_workplace_web/test-review.md
```

If the run came from a ticket, copy the same content into the ticket folder as
`6 - Test Review.md` so it sits with the rest of the lifecycle's artefacts.

It answers exactly one question: **which test cases must a human look at before
this suite is trusted?** It is not a run summary and not a changelog — a test
that was written, ran green, and raised nothing does not appear in it at all.

### Format

Newest run at the top. Nothing is ever deleted: a reviewer signs a row off by
changing its **Status**, so the history of what was decided stays readable.

```markdown
# Test review — Savance Workplace web automation

Rows a human must decide on before this suite is trusted.
Status: ⬜ Needs review · ✅ Accepted · ✏️ Changed · 🐞 Filed as <ticket>

## 2026-09-02 — Watchlist (WL-01…WL-22), 22 tests, 20 green / 2 red

| Ref | Category | What a human has to decide | Status |
|---|---|---|---|
| WL-22 | App defect | LEFT RED. The app saves DOB `31/02/2026`. Test unchanged — it is correct and the app is not. Confirm, then file. | ⬜ |
| WL-14 | Checklist vs app | Checklist says Escape closes the menu; Escape does nothing, click-away works. Test asserts the real behaviour. Is the checklist wrong, or the app? | ⬜ |
| WL-08 | Writes real data | Creates a `Zzautoqa` record and deletes it in a `finally`. Approve running this against the shared account. | ⬜ |
| WL-05 | Not automated | Needs a second signed-in user; the suite has one account. | ⬜ |
```

### What must be raised

Raise it if any of these is true. When in doubt, raise it — a redundant row
costs a reviewer ten seconds, a missing one costs a release.

1. **Left red because the app is wrong.** The single most important category.
   Say plainly that the test was *not* modified, and that this is a candidate
   defect for [[8-bug-reporting]].
2. **The checklist and the app disagree.** You asserted what the app does; a
   human decides which of the two is the bug.
3. **The test writes real data.** Name it, say what it writes and how it cleans
   up, and let a person approve the blast radius.
4. **A checklist row you could not automate**, with the reason. Never drop a
   row silently — an unwritten test is invisible, and invisible is how a gap
   ships.
5. **An assumption you had to make** about test data, timing, or environment
   that a different environment would break.
6. **An assertion you are not confident actually proves the row.** Better
   flagged than trusted.
7. Anything [[7-locator-extraction]] or [[7-test-healing]] hands you for the
   file — unproven locators, exhausted heal budgets.

### What must NOT be raised

Ordinary work. A test that was written, ran, went green and raised none of the
above is finished — putting it in the file to show effort buries the seven
things above in noise, and a review file nobody can skim is a review file
nobody reads.

---

## Before you call it done

- [ ] One test per checklist row; title carries id + original wording
- [ ] Each test passes when run **alone** (`-g "SC-39"`) and in a full run
- [ ] Shared/persisted state reset in `beforeEach` where it matters
- [ ] Every write restored in a `finally`
- [ ] Every loop over results preceded by a non-empty assertion
- [ ] No assertion encodes today's row counts
- [ ] No set logic that assumes unique data
- [ ] Assertions match observed behaviour; discrepancies documented
- [ ] No spec writes a selector — every element reached through a page-object method
- [ ] The spec has actually been **run**, not just typechecked and listed
- [ ] Full suite run, not just the tests you changed — and every remaining red is
      a deliberate, documented app defect, never an unexamined one
- [ ] `test-review.md` updated, and copied to the ticket folder if there is one
