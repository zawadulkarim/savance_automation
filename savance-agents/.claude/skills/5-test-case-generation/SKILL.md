---
name: 5-test-case-generation
description: Stage 05 — turn the approved Stage 04 acceptance criteria into executable, traceable QA test cases. Tuned for Sonnet. Refuses an unapproved "4 - Acceptance Criteria.md", loads the savance-workplace domain skill then mandatorily discovers the real UI live with Playwright before naming an element (not skippable to save time), writes test-cases.md with every case self-contained from login and tagged with its source Ticket, plus a traceability matrix, then holds a blocking human gate before stamping it and building test-cases.xlsx. Use when acceptance criteria need turning into test cases, when a feature needs a suite before automation, or on /5-test-case-generation.
---

# Test case generation

Turn approved acceptance criteria into the test cases QA executes. Two
deliverables: `test-cases.md` (canonical, carries the approval stamp, read by
Stage 07) and `test-cases.xlsx` (the review copy, built only after approval).

## Reference files

Load only what the current step needs.

| File | Read it at |
| --- | --- |
| `reference/test-types.md` | Step 4 — the nine types, generate/skip conditions |
| `reference/case-format.md` | Steps 5-8 — the fourteen fields, priority rubric, coverage vocabulary, the `test-cases.md` template |
| `reference/workbook-build.md` | Steps 10-11 — the JSON schema, generator invocation, Excel-COM visual pass, generator sharp edges. **Only after the gate passes.** |

## Where this sits — Stage 05

```
   4 - Acceptance Criteria.md            Stage 04, APPROVED
   0 - Scope Ledger.md                   slice -> AC ID range
        |
   1 -- read THIS SLICE's AC blocks    <- not the whole file
        |   ^
   2 -- [[savance-workplace]], then MANDATORY live Playwright discovery
        |   |                           |  ONE SLICE PER ITERATION
   3 -- append cases to test-cases.md,  |  mark the slice done
        |   steps self-contained from login, each tagged with its Ticket
        |   +---------------------------+
        |
        |   ... every slice done or n/a ...
        |
   4 -- rebuild traceability + coverage  once, at the end of the loop
        |
   5 -- HUMAN REVIEW GATE              <- MANDATORY, blocking, once. No export
        |                                 and no Stage 07 before it.
   6 -- build test-cases.xlsx            the stamped human review copy
        |
   7 -- [[7-test-authoring]]             reads the APPROVED test-cases.md
```

**One gate, and it is a person.** Nothing reviews this suite before they do —
the gate at Step 9 is what clears it for export and for automation, and it is
the only thing standing between a fabricated expected result and a Playwright
assertion at Stage 07. So the draft never goes straight to Excel, and what
reaches the gate has to be checkable: the traceability matrix built from the
cases that exist, what is missing led with, and every unverified element named.

### The Review Status stamp

`test-cases.md` carries its review state in its header block, directly under the
title — the pipeline's durable record of the human's decision, readable by a
later session, a subagent, or Stage 07, none of which saw this conversation:

```
**Review Status:** DRAFT
**Review Status:** AWAITING HUMAN REVIEW
**Review Status:** APPROVED — <reviewer name>, <YYYY-MM-DD>
```

[[7-test-authoring]] checks it before it writes a single spec. **Only a human's
explicit approval writes `APPROVED`,** with the name and date they gave —
writing it yourself forges a sign-off and disarms every stage after this one.

## Hard rules

1. **Never invent product behavior** — not a business rule, UI element, error
   message, URL, API response or database effect. Ground it in the criteria, in
   [[savance-workplace]] / [[savance-workplace-suite]], or in a live snapshot.
   Ungrounded becomes a visible **Assumption** or **Clarification required**. A
   fabricated expected result becomes a Stage 07 assertion and then a Stage 08
   bug report against behavior nobody specified — the failure this stage exists
   to prevent.
2. **Every acceptance rule is accounted for** — Covered, Partially Covered, Not
   Covered or Requires Clarification, never silently absent. The traceability
   matrix is the proof, and it is checked, not asserted.
3. **One case, one purpose.** A title needing an "and" between two unrelated
   outcomes is two cases. A case that would still pass with half its steps
   deleted tests less than it claims.
4. **Steps are executable by someone who has not read the criteria.** Every
   step names where the tester is, what they do, what they should see. "Verify
   the setting works" is not a step.
5. **`Playwright Verified` is evidence, not confidence.** `Yes` only when every
   UI element in that case's steps came out of a live snapshot this run.
6. **The Step 9 human gate is mandatory, blocking, and the only review this
   suite gets.** No `test-cases.xlsx` and no Stage 07 until a person approves
   `test-cases.md`. **Three rounds at that gate, then stop and ask** rather
   than looping a fourth time.
7. **The traceability matrix is the evidence at the gate**, so build it from
   the cases you actually wrote by walking the AC list and looking each one up
   — never from intent. Nothing downstream re-derives it for you.
8. **Never write `APPROVED` on the user's behalf.** No user to ask → **stop**,
   leave `AWAITING HUMAN REVIEW`, return `BLOCKED — awaiting human approval of
   test-cases.md` with the path.
9. **Approved criteria are the entry condition** (Step 1). Cases built on a
   draft that then changes at Gate D are wasted work that looks finished.
10. **Regenerate the workbook, never hand-edit it.** The Markdown is the source.
11. **Never overwrite an earlier round.** Add a `(rev 2)` suffix.
12. **Never weaken a case to make it automatable.** Hard to automate → mark
    `Automation Candidate: No` with the reason and keep it manual. Trimming an
    assertion to suit Playwright is the Stage 07 cardinal sin, one stage early.
13. **Do not delete `test-cases.md` after the export.** Both ship.
14. **Live Playwright discovery is mandatory whenever the app is reachable —
    not a step a user's time-saving preference can waive.** Load
    [[savance-workplace]] first, then drive the app, before writing a single
    case. Only genuine unreachability (no credentials, not deployed, server
    down) permits `Playwright Verified: No` across the board. If a user
    explicitly instructs skipping discovery anyway, say plainly that it
    weakens every case's grounding, get their explicit confirmation, and
    record the override as prominently as the Hard rule 9 entry-condition
    override — a suite that skips this is not a lesser version of the real
    thing, it is a draft that needs redoing once discovery is possible.
15. **Every case's steps are self-contained from login** — step 1 navigates to
    the login page, enters credentials, submits; the real menu path to the
    target screen follows, in labels confirmed live; then the case's own
    action. No "logged in as admin" precondition shortcut, even for a case
    chained after another case's postcondition (re-logging in to prove state
    survived a fresh session is the point of that case). A precondition is
    reserved for state the tester cannot reach by following the steps.
16. **Every case carries a `Ticket` field**, the fourteenth required field —
    the client ticket/bug/observation its AC belongs to, verbatim from the
    source. One shared value in a single-ticket run; per-case in a batch
    folder covering several client tickets, so a case (and any defect it
    finds) traces back to the ticket it actually belongs to. Never `N/A`.

## Token discipline

The step order is already most of the saving: the Excel is built once, after
approval, rather than rebuilt every round.

1. **Read the criteria once, from the Markdown** — one Read replaces an openpyxl
   script and a whole-workbook dump.
2. **Refine with `Edit`, not a rewrite.** A finding usually touches one case.
   The traceability matrix and coverage summary are the deliberate exception —
   rebuilt whole every round, because a stale matrix asserts coverage that was
   true one round ago.
3. **Batch the Playwright discovery** — one snapshot per screen, everything that
   screen owes you taken from it, browser closed when the walk is done.
4. **Do not re-read a file you just wrote.**
5. **Enumerate a data-driven family once** — near-identical cases reference the
   first of them rather than restating preconditions per case.

## Step 0 — Model check (WARN, the user decides)

Tuned for Sonnet; the agent pins `model: sonnet`, but the pin binds only when
dispatched as a subagent — in the main conversation the session's model applies.
If the session is not on Sonnet:

> ⚠️ This stage is set up for Claude Sonnet and this session is on Opus. You
> can switch with `/model sonnet`, or I can carry on as-is. Continue on Opus?

Continuing is their call: say "continuing on Opus" once, note it in the
hand-off, and drop it. Already on Sonnet → say nothing. The only thing forbidden
is running on Opus silently.

## Step 1 — Establish the input (GATE)

| Input | Where | Notes |
|---|---|---|
| **Approved AC Markdown** (primary) | `tickets/<ticket-id> - */4 - Acceptance Criteria.md` | Stage 04's canonical output. One Read, and it carries the approval stamp. |
| **AC workbook** | `.../4 - Acceptance Criteria.xlsx` | Older runs or a client sheet. openpyxl — Read cannot open binary `.xlsx`. Prefer the Markdown; say which you used. |
| **AC prose** | chat or a document | Acceptable; say the criteria were unstructured. |
| **QA checklist** | `5 - QA Checklist.xlsx` | Supporting only. A check item is an atomic tick, not a case. |
| **Spec document** | `2 - Spec Document.docx` | Supporting. Its out-of-scope list says what gets no cases. |
| **Domain knowledge** | [[savance-workplace]], [[savance-workplace-suite]] | So an expected result states real behavior. |

Locate the folder by globbing `tickets/<ticket-id> - */` — the gid is the stable
key, never a reconstructed name.

**Check the criteria are approved first**, one cheap read:

```bash
grep -m1 '^\*\*Review Status:\*\*' "<ticket folder>/4 - Acceptance Criteria.md"
```

`APPROVED — <reviewer>, <date>` → proceed and quote it in the hand-off. `DRAFT`
or `AWAITING HUMAN REVIEW` → **say so and stop.** The user may override; record
it and mark every case as resting on unapproved criteria. An AC workbook or
prose with no stamp is not a violation — it is an older input, and it goes in
the hand-off as one.

Then settle, because they are expensive to redo: **no criteria at all** (ask;
on an override, flag every scope judgement as inferred) · **sanity or
regression** depth · **is the app reachable** (it decides what every
`Playwright Verified` may say) · **any other files**.

## Step 1B — Read the scope ledger and pick this iteration's slice

Stage 01 sliced the ticket and Stage 04 recorded, per slice, which acceptance
criteria it produced. **This stage works one slice per iteration.**

```bash
grep -m1 '^\*\*Iteration:\*\*' "<ticket folder>/0 - Scope Ledger.md"
```

Read the ledger — it is small — and take the first slice whose `S05` cell is
`todo` and whose `Depends on` slices are `done`. Set it to `doing`. Its `S04`
`Produced` column gives the **AC ID range this iteration covers**: that is the
thread from the slice to the criteria to the cases you are about to write, and
it is why you do not need to read the whole criteria file.

Full format and rules: `.claude/skills/1-requirement-analysis/reference/scope-ledger.md`

**No ledger?** The ticket was never sliced. Say so and offer the choice — slice
it now from the criteria's own AC groups, or run the whole suite in one pass as
before.

### The loop

Per iteration, for the chosen slice only:

| | |
| --- | --- |
| 1 | Read **only that slice's AC blocks**, by the ID range in `Produced`. |
| 2 | Discover the UI those blocks touch (Step 3), then write their cases (Steps 4-5). |
| 3 | **Append** the cases to `test-cases.md` with `Edit`. `TC-NNN` numbering continues across slices and never restarts. |
| 4 | Set the slice's `S05` cell to `done`, fill `Produced` with the TC range, bump `Iteration: N of M`. |

**Rebuild the traceability matrix and coverage summary only at the end of the
loop**, not per iteration — they are whole-file structures, and rebuilding them
every round is pure waste. Everything else in the file is append-only.

**The human gate at Step 9 happens once, after the last slice** — over the
whole suite, which is the only way the cross-slice gaps are visible at all.
Gating per slice costs the slice count over in a reviewer's attention and still
misses them.

**The Markdown stays `DRAFT` for the whole loop**, moving to
`AWAITING HUMAN REVIEW` only when the last slice is done and the traceability
matrix has been rebuilt over the complete suite.

Three rules, same as Stage 04: load only this slice's sources; never re-read the
accumulated `test-cases.md` between iterations; append with `Edit` rather than
re-emitting.

## Step 2 — Decompose the criteria

Read every AC row and every numbered rule, and ask what each one *asserts* — a
rule is an assertion about behavior; a case is the procedure that makes it
observable.

**Baseline: one rule → one functional case.** Add only the other types the rule
warrants (Step 4). A compound gate rule ("prevent X when A and B hold") is one
positive case proving the gate fires, plus one per facet proving it does *not*
fire when that facet is absent — that is where negative cases come from
honestly, rather than by invention.

## Step 3 — Discover the UI with Playwright MCP (mandatory, Hard rule 14)

**Discover before you write, every run.** This is not conditional on time
pressure or a user's stated preference — only genuine unreachability excuses
it (see below). Steps naming a button that does not exist are worse than steps
naming none, and a case written from AC prose alone is a draft, not a finished
case.

1. **Load [[savance-workplace]] first** — its login procedure and navigation
   map, before opening a browser.
2. Log in per that procedure and navigate the feature.
3. `browser_snapshot` each screen the criteria touch — the accessibility
   snapshot, not a screenshot; it gives the real accessible names.
4. Record verbatim, with real capitalisation and punctuation: navigation path,
   page and tab names, buttons, fields, toggles, labels, dialog titles,
   validation messages, table and column headers, filter controls, and the
   actual interaction each control needs.
5. Write **every** step in the app's own terminology, starting with login
   itself (Hard rule 15) — "Navigate to the Login page. Enter credentials,
   click **"Log In"**. Navigate to **Admin Console > Integrations > Watchlist
   History**. Click **"Export CSV"**." — not "go to the watchlist page and
   export the data", and not a "logged in as admin" precondition standing in
   for the login steps.
6. `Playwright Verified: Yes` only when every element the case names came out of
   a snapshot. `N/A` only for a case with no UI surface.
7. A control that would require a mutating, destructive, or org-wide action to
   exercise live (a bulk "Deploy", clearing shared state, an irreversible
   send) — do not click it casually. Confirm the screen and the control's
   presence/wording live, mark the case `Playwright Verified: No` with that
   reason, and say so; this is a discovery limit, not a discovery skip.

**App not reachable** — no credentials, not deployed, server down → say so once
up front, set every `Playwright Verified` to `No`, and write steps from the
criteria's own wording. Do not invent plausible UI; an unverified element named
in a step goes in Assumptions.

**A user asking to skip discovery while the app *is* reachable is a different
case from genuine unreachability**, and Hard rule 14 governs it: say plainly
that skipping weakens every case's grounding, get their explicit confirmation,
and record the override in the header exactly like the Hard rule 9
entry-condition override. Treat the resulting draft as provisional — worth a
full discovery-backed rework the moment the app is reachable and the user asks
for it, not as a lesser-but-acceptable final artefact.

**When the app contradicts the criteria** — control named differently, elsewhere,
or behaving differently — follow neither silently. Write the case against the
criteria, record the observed difference in Assumptions, and raise it. It is
either a Stage 08 defect or a stale criterion; both need a human.

## Step 4 — Choose the test types honestly

**Generate only the types the rule warrants.** Forcing all nine onto every
requirement produces a 300-case suite that tests less than a 60-case one,
because the padding hides the gaps.

→ `reference/test-types.md` for the nine types and their generate/skip
conditions. Two that are routinely got wrong: **regression** is the type most
often missed and most expensive to miss (a new setting in an existing modal
means that modal's existing settings still need to save), and **permission**
cases need a second account — without one, write the case, mark
`Automation Candidate: No`, and record the missing account as a Clarification
rather than dropping the type.

## Steps 5-8 — Write the cases and the file

→ `reference/case-format.md` for the fourteen required fields, the priority
rubric, the step convention, the coverage vocabulary, the Assumption vs
Clarification distinction, and the `test-cases.md` template.

The invariants worth carrying without a lookup:

- **Fourteen fields, none optional.** `None` or `N/A` is a value; empty is not.
  `Ticket` is never `N/A` (Hard rule 16).
- **Every AC has at least one High case.** All-Medium/Low means its main path
  was missed — go back.
- **Quote every user-facing string verbatim** in double quotes, bold named UI
  elements. House convention shared with [[4-acceptance-criteria-generation]]
  and [[8-asana-bug-report]].
- **Build the traceability matrix from the cases you actually wrote**, by
  walking the AC list and looking each one up — never from intent.
- **Every `Not Covered` / `Requires Clarification` row has a matching entry** in
  Assumptions / Clarifications. A bare status is a claim with nothing behind it,
  and nobody downstream will catch it for you.
- **Never write "repeat for each X"** — enumerate, or make it a data-driven
  family with distinct IDs.

Output: `tickets/<ticket-id> - <Ticket name>/test-cases.md`. The unnumbered
canonical name is deliberate — Stage 07 reads it by name. With no ticket behind
the run, write it to the working directory.

## Step 9 — HUMAN REVIEW GATE (MANDATORY, blocking, the only review)

**A person approves the test cases before they become a workbook or a Playwright
suite.** Nothing has checked them but you, so this gate is doing all the work —
present the suite in a form that can actually be checked, not a form that looks
finished.

First, set `Review Status` to `AWAITING HUMAN REVIEW`.

Then present, blunt and itemised, no preamble, no praise sandwich:

1. **What is missing** — acceptance rules with no case, refusal paths, role
   variations, regression areas. Lead with this: a suite can be flawless case by
   case and still be wrong because of one absent case.
2. **Could a tester execute this** — read two or three cases as someone who has
   not seen the criteria. Every point where they would stop and ask is a defect.
3. Counts: cases by type and priority, steps, ACs covered / partially / not,
   automation candidates — and the slice count and how many cases each slice
   contributed, so an unevenly covered slice is visible. When cases carry more
   than one distinct `Ticket` (a batch/bundle folder), break the count down by
   ticket too.
4. **Playwright posture** — how many cases are `Playwright Verified: No`, and
   why. A suite written entirely against unverified UI is worth saying out loud.
5. Assumptions standing and clarifications required, with the case IDs affected.
6. **Anything you are unsure of** — a case you could not ground, an AC whose
   intent you had to interpret, a coverage call you would defend but would not
   bet on. Nothing downstream will surface it, so surfacing it is on you.
7. The file path.

Then ask, and stop:

> Approve `test-cases.md`? On approval I stamp it, build `test-cases.xlsx`, and
> it becomes the input Stage 07 automates. Otherwise tell me what to change.

- **Explicit approval** → set `Review Status` to
  `APPROVED — <reviewer name>, <YYYY-MM-DD>` from what they actually said, then
  Step 10.
- **Anything else** → **map each piece of feedback to the slice whose
  `Produced` IDs it names**, set only those slices back to `todo`, and re-run
  just those iterations; untouched slices stay `done`. Feedback matching no
  slice is a *missing slice* — add a row and say the decomposition missed it.
  Then rebuild the matrix and coverage summary and re-present, saying what
  changed and what you deliberately did not. **Three rounds, then stop and
  ask.**
- **Silence, a question back, or "looks fine I guess"** → not an approval.
- **No user to ask** → **stop.** Return the Markdown path and `BLOCKED —
  awaiting human approval of test-cases.md`, status left at
  `AWAITING HUMAN REVIEW`.

A rejection re-enters at the honest step: missing coverage → Step 2 (decompose),
a wrong element name → Step 3 (discovery), a wording problem → Step 5. Rewriting
the sentence around a missing case does not add the case.

## Steps 10-11 — Build and verify the workbook

**Only after the approval at Step 9.** → `reference/workbook-build.md` for the
JSON spec schema, the generator call, the path gotchas, the Excel-COM visual
pass and the generator's refusal conditions.

```bash
python .claude/skills/5-test-case-generation/scripts/build_test_cases_workbook.py <spec.json> <output.xlsx>
```

Output: `tickets/<ticket-id> - <Ticket name>/test-cases.xlsx`; never overwrite —
add `(rev 2)`. The case IDs, titles and step counts must match the approved
Markdown one for one, and the workbook's printed counts are how you check that.

## Chaining into Stage 07

[[7-test-authoring]] reads `test-cases.md` and writes one Playwright spec per
case, keeping the `TC-NNN` id in the test title so a result maps back with no
lookup table.

**It checks the `Review Status` line first and refuses to author from an
unapproved suite.** That is what makes the Step 9 gate real across a session
boundary: Stage 07 may run days later, in a fresh context, dispatched by someone
who never saw the gate.

What carries over: `Automation Candidate: No` cases stay manual and are recorded
in `test-review.md`; an **Assumption** on a case becomes a `test-review.md` line
for a human to confirm, never an assertion; and where the app disagrees with a
case, Stage 07's rule governs — assert what the app does and flag the
disagreement, without editing the case here.

---

<!-- Stage 05. Agent: .claude/agents/5-test-case-generator.md (sonnet)
     Step 3 mandatory live discovery via savance-workplace + Playwright
     (Hard rule 14) · Step 9 HUMAN gate on test-cases.md, blocking, the only
     review the suite gets · Step 10 build the xlsx, only after approval.
     Fourteen required fields (case-format.md): steps self-contained from
     login (Hard rule 15), every case tagged with its Ticket (Hard rule 16).
     Upstream stage 04 (its APPROVED Review Status line is the entry condition).
     Downstream .claude/skills/7-test-authoring/SKILL.md. -->
