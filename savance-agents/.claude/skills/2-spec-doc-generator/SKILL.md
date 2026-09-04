---
name: 2-spec-doc-generator
description: Stage 02 — write the "Feature Spec & Test Scope" document in plain, high-level language: what is changing, what QA will test, and what it will not test and why. Three sections, nothing more. Needs the answered Stage 01 queries (overridable, then provisional), explores the codebase for the scope, and takes the draft straight to a blocking human gate. Never writes to Asana. Use when the queries come back answered, or on /2-spec-doc-generator.
---

# Spec doc generator — Feature Spec & Test Scope

Stage 02 of the QA lifecycle, sitting between requirement analysis (Stage 01)
and acceptance criteria (Stage 04). Once the client has answered the queries,
this stage turns the ticket into one short document anyone on the team can
read cold and come away knowing:

1. **What is changing** — at a high level, in plain language.
2. **What we will test.**
3. **What we will not test**, and why.

That is the whole document. Three sections, plus a short **Open items and
assumptions** note when something is open, assumed or overridden.

**Write for someone who has not read the ticket and does not read code.** No
file paths, no class or table names, no ticket shorthand, no internal
acronyms in the document body. The code-level evidence you gather belongs in
the chat report (Step 3), not in the deliverable.

This is a *high-level* document — a scope agreement, not a design doc and not
a test plan. Detailed cases come later from
`4-acceptance-criteria-generation` and `5-test-case-generation`.

This skill is **interactive and gated**: it stops and waits for a real human
reply at Steps 1, 2 and 7, plus a model check before it starts (Step 0). There
is no automated review layer — **Step 7 is the only check this document gets**,
which is why the draft is presented there with the evidence behind it rather
than on its own.

## What this document deliberately does not contain

The document is short on purpose. Do not add these back, and do not reinvent
them under other headings:

| Not in the document | Where it actually belongs |
| --- | --- |
| A table of affected apps, direct vs indirect | An **in-scope item** naming that app's regression: "Kiosk sign-in — shares the visitor status service." |
| A today / after workflow table | One or two **What is changing** bullets. If a bullet needs a before-and-after to land, write the sentence, not a table. |
| Environments, navigation paths, prerequisites, test data | Stage 05, which walks the live app and writes preconditions per test case. A path named here is a path guessed a gate early, and a tester will follow it. |
| Implementation detail of any kind | Your Step 3 chat report — that is the audit trail for the scope. |

A reader who wants to know *how* to test goes to the test cases. This document
answers *what* is changing and *what QA is agreeing to cover* — nothing else.

## Hard rules

1. **Asana is read-only here.** Reads only. **Never** call
   `asana_create_task`, `asana_update_task`, `asana_create_task_story`, or any
   other mutating Asana tool. If something needs filing, that is a different
   stage — say so and stop.
2. **Answered queries are required** (Step 1). Without them the scope is
   guesswork. The user may override; an override makes the document
   *provisional* and must be recorded, never hidden.
3. **Three sections, and nothing else** — what is changing · what we will
   test · what we will not test and why. An Open items note only when
   something is actually open. No app table, no workflow table, no
   environments, navigation paths or prerequisites, however useful they seem.
   See *What this document deliberately does not contain* above.
4. **The codebase exploration is mandatory** (Step 3), and a shorter document
   does not make it shallower. The testing scope is derived from code, not
   imagined from the ticket title. **What the exploration finds shows up as
   scope items** — a shared-code regression becomes an in-scope line, not a
   table row.
5. **Every scope item must trace to evidence** — an answered query, the
   ticket, or something you actually found in the codebase or on the live
   app. No speculative scope. The same applies to any UI element you name:
   quote and bold it as `**"Manage Options"**`, and only if you have actually
   seen it live or in the domain skills. Never chain them into a route — the
   document carries no navigation paths (rule 3).
6. **Step 7 is the only review.** Nothing checks this draft before the human
   does, so what you put in front of them has to be checkable: every scope item
   presented next to the evidence it came from, what is missing led with, and
   anything provisional named as provisional. Three revision rounds at that
   gate, then stop and ask rather than looping.
7. **No document before approval** (Step 7). Nothing is written to disk
   until the user says yes.
8. **Never overwrite** a previous spec for the same ticket. Write a fresh,
   distinctly named file alongside it.
9. **Warn if not running on Sonnet** (Step 0). This stage is tuned for Sonnet, and its
   agent definition pins `model: sonnet`. Check the model at Step 0 and warn
   the user if it is Opus — but the warning is a warning, not a block. If they
   choose to continue, continue. The only forbidden option is running on Opus
   *silently*.

---

## Step 0 — Model check (WARN, the user decides)

This stage is tuned for Claude Sonnet. The `model: sonnet` pin in the agent
definition binds when the stage is dispatched as a subagent; when you run this
skill in the main conversation — the normal mode — the session's own model
applies instead, and the pin cannot reach it.

So check first. If the session is running Opus (or anything other than
Sonnet), warn the user before you start:

> ⚠️ Heads up — this stage is set up to run on Claude Sonnet, but this
> session is on Opus. You can switch with `/model sonnet`, or I can carry on
> as-is. Continue on Opus?

Then do what they say:

- **They want to switch** — stop and let them run `/model sonnet`, then pick
  up from Step 1.
- **They want to continue** — continue. This is their call, not yours. Say
  "continuing on Opus" once, note it in the Step 11 hand-off, and then
  drop it: do not re-warn at every gate, do not hedge the output, and do not
  bring it up again unless they do.

If the model is already Sonnet, say nothing and go straight to Step 1.

## Step 1 — Require the answered query document (GATE 1)

The input this stage is built on is the Stage 01 queries document **with the
client's answers filled in**.

Find it:

- Look for `1 - Requirement Analysis.docx` in the ticket folder,
  `tickets/<ticket-id> - <Ticket name>/`, produced by
  [[1-requirement-analysis]]. Locate the ticket folder by globbing `tickets/<ticket-id> - */` — the Asana
  gid is the stable key; don't try to reconstruct the name.
- Answers may arrive in several shapes, all acceptable: the docx with
  `Answer:` lines filled in, a client email or Asana comment replying to the
  queries, or the user simply pasting the answers into chat.

Then check the state of it and act:

- **All queries answered** → proceed to Step 2.
- **No queries document exists at all** → stop and ask the user for it. If
  Stage 01 was never run for this ticket, say so — running
  `1-requirement-analysis` first is usually the right move, and it is the
  user's call, not yours.
- **The document exists but queries are unanswered** → stop, list exactly
  which queries are still open, and ask the user for the answers.

**The user may override.** If they explicitly say to proceed without full
answers:

- Proceed, but the document is **provisional**. Set the `provisional` field in
  the spec (Step 8) naming which queries are unanswered.
- List every unanswered query in **Open items and assumptions**, together with
  the assumption you made in its place so a reader can see exactly what would
  change if the real answer differs.
- State the override in the chat hand-off (Step 11).
- Never quietly fill a gap with an invented answer. An assumption that is
  labelled is fine; one that is disguised as a fact is not.

## Step 2 — Collect the rest of the inputs (GATE 2)

Confirm the ticket you are working from (an ID, URL, or conversational
reference) and read it in full — body, comments (`asana_get_stories_for_task`)
and attachments.

Then ask, as in Stage 01:

> Are there any other files you want to provide? (design docs, mockups, the
> client's reply, screenshots, anything else relevant.)

Wait for the answer. "No" is fine — but it must be the user's "no". Read
everything they name and list back what you read.

## Step 3 — Explore the codebase (MANDATORY GATE — this is where the scope comes from)

**Do not draft a testing scope before this step. Ever.** A scope written from
the ticket text alone will miss the parts of the product the change actually
touches, which is precisely the failure this document exists to prevent.

The document got shorter; the exploration behind it did not.

- **If a codebase-knowledge skill is available in this session, use it
  first.** <!-- codebase skill hooks in here once it exists -->
- Otherwise work the repository directly with `Glob` / `Grep` / `Read`.

Whichever route, come out of this step with a concrete, written list — and
note what each finding becomes, because in a three-section document
everything you find has to arrive as a scope item or not at all:

| What to find | What it becomes in the document |
| --- | --- |
| The modules / features the change lives in | The direct in-scope items |
| Shared code the change touches | **In-scope regression items** — the highest-value part of the scope, and the part a ticket-only reading always misses |
| Other apps consuming the same code or data | One in-scope item per app whose behaviour can shift (cross-check against [[savance-workplace-suite]]) |
| Permission, role, or licence checks around it | In-scope items naming the user types worth testing |
| Config or settings that alter the behaviour | In-scope items naming the variations worth covering |
| What the change provably does not reach | The out-of-scope items, each with its reason |

Also cross-check [[savance-workplace]] and [[savance-workplace-suite]] for the
module's documented behaviour and its place in the 11-app family.

**Report the evidence in chat** at Step 7 — the files and modules you found,
mapped to the scope items they justify. This is the audit trail for the scope;
it stays in chat and out of the document.

**If the codebase is not reachable from this session**, say so plainly. You
cannot claim a verified scope without it. Either stop and tell the user, or —
if they override — proceed with a scope derived from the ticket, domain
knowledge and the live app only, and mark the document provisional with the
missing-codebase gap named in Open items.

## Steps 4-6 — Write the three sections

-> `reference/section-guide.md` for what each section must contain and the
plain-language rules.

The three sections: what is changing · what we will test · what we will not
test and why. Plus an **Open items and assumptions** note when something is
open, assumed or overridden.

**Every scope item traces to evidence** from Step 3: the ticket, an answered
query, a codebase finding, or the live app. No speculative scope, and no file
paths, class names, table names or endpoints in the document body - that
evidence belongs in your chat report.

## Step 7 — Present and get approval (GATE — the only review this doc gets)

Nothing has checked this draft but you, so present it in a form a human can
actually check, in this order:

1. **What is missing** — an app nobody listed, a scope item with no criteria, a
   regression area nobody thought of. Lead with this: a spec can be right line
   by line and still be wrong because of one absent scope item.
2. The draft document, section by section.
3. **The codebase evidence** from Step 3 — files and modules found, mapped to
   the scope items they justify, and specifically which items came from the
   codebase rather than the ticket. A scope item whose source you cannot name
   is one the reviewer cannot check; take it out or move it to Open items.
4. Anything provisional, and why.
5. Anything you could not verify — an unreachable codebase, an unreachable app,
   a query answered ambiguously.

Then ask plainly:

> Does this spec and test scope look right to generate the document from?

- **User says yes** → Step 8.
- **User says no**, asks for changes, or replies ambiguously → **generate
  nothing.** No docx, no folder, no leftover spec file. Revise and come back to
  this gate, saying what changed and what you deliberately did not. A missing
  app or regression area means the *exploration* failed — re-enter at **Step
  3**, not at a wording pass. **Three rounds, then stop and ask.**

There is no implicit yes.

## Steps 8-10 - Build and verify the document

**Only after the Step 7 approval.** -> `reference/build-and-verify.md` for the
JSON spec schema and the structural verification.

```bash
python .claude/skills/2-spec-doc-generator/scripts/build_spec_doc.py <spec.json> "<ticket folder>/2 - Spec Document.docx"
```

There is no Word COM or LibreOffice here, so the `.docx` is verified
**structurally** - reopen it and walk its paragraphs. Never claim a visual
check you could not run.

## Step 11 — Hand off

Report to the user:

- Absolute path of the generated file — **or** an explicit statement that
  nothing was generated because the user did not approve.
- The ticket, and whether its queries were fully answered or the document is
  provisional (and on whose override).
- Counts: what-is-changing bullets, in-scope items, out-of-scope items, open
  items.
- **The codebase evidence** behind the scope, and any scope item that came
  from the codebase rather than the ticket — this is the value this stage
  adds, so make it visible.
- **The Gate (Step 7) outcome** — who approved it, when, how many rounds it
  took, and any feedback you did not act on with your reason.
- Anything you could not check, and what a reader should not rely on.
- If the run continued on Opus after the Step 0 warning, one line saying so.
- Explicit confirmation that no Asana state was touched.

Then note the natural next step: these scope items feed
`4-acceptance-criteria-generation` (Stage 04). Don't run it unprompted.
