# Writing the three sections

Referenced from `SKILL.md` Steps 4-6. What each section of the document must
contain, and the plain-language rules that keep it readable by someone who
neither followed the ticket nor reads code.

## Contents
- Step 4 - what is changing
- Step 5 - the testing scope (what we will test, what we will not)
- Step 6 - the plain-language pass
- The Open items note
- What does not go in this document

## Step 4 — What is changing

From the ticket, the answered queries and the Step 3 codebase findings, write
the **What is changing** bullets:

- One idea per bullet, one plain sentence each.
- Describe outcomes a user would notice, not implementation.
- **Aim for three to six bullets.** If it needs more, the ticket probably
  bundles several features and you should say so rather than write a longer
  list.
- Where a change only makes sense against today's behaviour, put both in the
  one sentence — "Watchlist matches are shown at sign-in, where today the
  receptionist has to check the list manually." One sentence, not a
  before-and-after table.

Good: "Staff can be added to a watchlist directly from the visitor screen."
Not: "Adds a `watchlist_id` FK to the `Visitor` model and a new POST endpoint."

This section is the whole of the "what is being built" answer. Keep it high
level — a reader who needs more detail has the ticket, and a tester who needs
steps has the test cases.

## Step 5 — The testing scope

Two sections, and between them they are the agreement this document exists to
record.

### What we will test

Each item traceable to the ticket, an answered query, or a Step 3 codebase
finding, and each one **executable** — something a person could turn into a
pass/fail test. "Watchlist behaviour works" is not an item; "A flagged visitor
is blocked at sign-in and the receptionist is warned" is.

Two kinds of item belong here, and the second is the one that earns the stage:

- **Direct** — the behaviour the ticket asked for.
- **Regression** — what the change could break because it shares code, data
  or a service with something else. Name the area plainly, with the reason in
  the same line: "Kiosk sign-in — shares the visitor status service." These
  come out of the Step 3 shared-code findings, they are invisible from the
  ticket text, and **a cross-app risk that lives only in your chat report is
  not in scope.** If the exploration found it and it matters, it is a line
  here.

Group affected apps into these items rather than tabulating them separately —
the app's name in the item is what a reader needs.

### What we will not test

What QA will not cover, **and why**. A bare exclusion list is not useful;
"Email templates — unchanged by this ticket" is. Cover:

- Areas a reader would reasonably expect to be in scope, and are not.
- Anything deferred to a later round, with what defers it.
- Anything that cannot be tested at all right now — that is a finding in its
  own right, so say it here rather than leaving it out.

This section is what stops the argument later about whether something should
have been caught, so every line carries its reason.

## Step 6 — Plain-language pass

Read the whole draft back as if you were a team member who has never seen the
ticket:

- Short sentences, one idea each.
- No file paths, class names, table or column names, endpoints, or ticket
  shorthand anywhere in the document body.
- No acronym the reader hasn't been given, and no internal codename.
- Name UI elements exactly as they appear on screen — quoted and bolded,
  written inline as `**"Manage Options"**` (the house convention shared with
  `8-asana-bug-report` and `1-requirement-analysis`). Plain descriptive words
  ("the dropdown", "the page") stay unquoted and unbolded. Only name an
  element you have actually seen, live or in the domain skills.
- If a sentence needs product knowledge the reader may not have, add the
  half-line of context that makes it land.
- Then count the sections. Three, plus Open items if something is open.
  Anything else is creep — cut it.

## The Open items note

Not a numbered section, and present only when there is something to put in it:
an unanswered query, an assumption, an override, or a part of the change with
nowhere to test it.

- Every unanswered query listed, **with the assumption used in its place**, so
  a reader sees exactly what would change if the real answer differs.
- Every assumption labelled as one. A labelled assumption is fine; one
  disguised as a fact is the failure the provisional banner exists to prevent.

## What does not go in this document

Repeated here because it is the easiest rule to drift on mid-draft (`SKILL.md`
hard rule 3):

- **No app table.** The apps appear inside the scope items.
- **No today / after workflow table.** It collapses into Step 4's bullets.
- **No environments, navigation paths, prerequisites or test data.** Stage 05
  walks the live app and writes preconditions per case; a path written here is
  a path guessed a gate early, and a tester will follow it.
- **No implementation detail.** That is the Step 3 chat report's job.
