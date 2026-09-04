---
name: 1-requirement-analysis
description: Stage 01 — interactive requirement analysis for a client Feature Request or Change Request. Decomposes the ticket, grounds each ask against domain knowledge and the codebase, and turns what is left into plain-language client queries in a "Queries" docx, written only on the user's explicit approval. Never writes to Asana. Use for requirement analysis or clarifying questions on a new feature/CR ticket, or on /1-requirement-analysis.
---

# Requirement analysis

Stage 01 of the QA lifecycle. Turns a short — often one-line — client ask
into a clear picture of what is already settled and what genuinely still
needs someone to decide.

This skill is **interactive and gated**. It is a conversation with the user,
not a batch job. There are three points where it stops and waits for a real
human reply (Steps 1, 8 and 10), plus a model check before it starts (Step 0). Do not sail past them, do not answer them on
the user's behalf, and do not assume approval to save a round trip.

The final deliverable — a client-ready `.docx` of open queries — is written
**only** after the user says the queries are okay (Step 10).

## Hard rules

1. **Asana is read-only here.** Only `asana_get_task`, `asana_get_tasks`,
   `asana_get_project_sections`, `asana_get_stories_for_task`,
   `asana_get_attachments_for_object` and friends. **Never** call
   `asana_create_task`, `asana_update_task`, `asana_create_task_story`,
   `asana_set_parent_for_task`, or any other mutating Asana tool while
   running this skill — not even if a step below would be easier with one. If
   the user also wants something filed in Asana, that is a different stage
   (`8-asana-bug-report`), so say so and stop.
2. **No invented grounding.** Any location, setting, field name or existing
   behavior you state as fact must trace to a domain-knowledge skill, the
   codebase, or something you actually checked on the live test server.
   Anything you cannot ground becomes a question, not a confident guess.
3. **No file before approval.** The `.docx` is written at Step 12 and nowhere
   else. If the user has not said yes at Step 10, no file exists.
4. **Never overwrite** a prior queries doc or the reference PDF. Always a
   fresh file.
5. **Don't pad the query list.** A question the client could answer with "you
   already know this" is a defect in this stage's output.
6. **Warn if not running on Sonnet** (Step 0). This stage is tuned for Sonnet, and its
   agent definition pins `model: sonnet`. Check the model at Step 0 and warn
   the user if it is Opus — but the warning is a warning, not a block. If they
   choose to continue, continue. The only forbidden option is running on Opus
   *silently*.

**Reference example (learn the pattern, don't hardcode it):** if
`Misc Phase 2_ Queries from Enosis.pdf` is still in the project root, read it
once to internalize the house format and tone. It is the *answered* version,
with client replies threaded back in — this skill produces the pre-send
version, where only points the **user** could answer carry an answer line.

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
  "continuing on Opus" once, note it in the Step 14 hand-off, and then
  drop it: do not re-warn at every gate, do not hedge the output, and do not
  bring it up again unless they do.

If the model is already Sonnet, say nothing and go straight to Step 1.

## Step 1 — Collect the inputs (GATE 1)

Before any analysis, establish what you are working from. Check what the user
has already given you in this conversation:

- **An Asana ticket?** — an ID, a URL, or a conversational reference ("the
  Toyoda Gosei ticket").
- **Any other document?** — a requirement doc, a spec, a client email, a
  meeting note, a screenshot, a prior queries doc.

Then:

- **If neither was provided** — stop and ask the user for one. Do not guess a
  ticket, do not pick "the most recent thing on the board", do not proceed on
  a vague topic name. You need a concrete starting artifact.
- **If something was provided** — confirm back what you understood it to be,
  in one line, so a wrong ticket gets caught now rather than after the
  analysis.

Then, **always ask a second question** even when a ticket was already given:

> Are there any files you want to provide? (spec, mockups, client email,
> screenshots, exported data, anything else relevant.)

Wait for the reply. "No" is a perfectly good answer — but it has to be the
user's answer, not your assumption. Read every file they name before moving
on, and list back what you read.

## Step 2 — Resolve scope

- **A single ticket** — `asana_get_task` on it directly.
- **A parent / "Main Task"** (e.g. "Q3 Release Items (Enosis)") —
  `asana_get_task` with
  `opt_fields=name,notes,subtasks.name,subtasks.notes,subtasks.completed`,
  then process every in-scope child in one run, producing one combined docx
  section. This is the common case: the board groups a batch of client asks
  under one parent, and the client-facing queries doc covers the whole batch
  at once.

Also pull the ticket's comments (`asana_get_stories_for_task`) and
attachments — clarifications often live there rather than in the body.

## Step 3 — Filter out anything that isn't a client ask

In scope: Feature Requests, `[CR] ...` tickets, short prose asks from the
client.

Out of scope: tickets already shaped like a QA bug report — a title starting
`Bug NN:`, or a body already carrying the Testing-Environment /
Steps-to-reproduce / Observed-Behavior / Expected-Behavior template. Those are
QA's own fully-specified tickets, unambiguous by construction, and running
requirement analysis on them is redundant.

If you can't tell which bucket a child ticket is in, ask the user rather than
guessing.

## Step 4 — Decompose each ticket into distinct asks, and write the scope ledger

A short ticket routinely bundles several independent asks — never analyse it
as one monolithic requirement. Split on numbered/bulleted points already in
the body, or, for unstructured prose, on each distinct behavior change being
requested. A single ticket bundling seven bullet points is seven asks, each
getting its own question or small cluster of questions.

**Those asks are the ticket's slices, and this stage makes them durable.**
Stages 04 and 05 work one slice per iteration, and they cannot re-derive the
decomposition — a later session has never seen this analysis. So write
`0 - Scope Ledger.md` into the ticket folder now:

- One slice per independently testable ask. Merge two asks that cannot be
  verified apart; split one that spans two surfaces a tester would visit
  separately.
- **Order by risk, then dependency** — `S1` is the highest-risk slice, so a run
  that stalls halfway has covered what most needed covering.
- Three to eight slices is the working range. One slice is a legitimate answer
  for a genuinely single-ask ticket: write a one-row ledger and say so rather
  than inventing seams. Over about ten, the ask has outgrown the ticket — raise
  it at Gate 2 rather than absorbing it.

→ `reference/scope-ledger.md` for the format, the status vocabulary and the four
rules that keep the file bounded. The ledger is **state, not history**: fixed
rows, cells updated in place, no appended prose. What happened goes in the run
log; this file holds only where things stand.

Write it before Step 5, and present the slice list at Gate 2 (Step 8) alongside
the findings — the decomposition is a judgement the user should get to correct
while it is cheap, because every downstream iteration is shaped by it.

## Step 5 — Analyse and ground every ask

For each ask, work out as much of the concrete behavior as you can, in this
order. Stop as soon as a point is grounded.

1. **The ticket and the supplied documents.** Re-read them for the ask's own
   constraints before reaching outward — half the "open questions" people
   raise are answered in a sentence further down the ticket.
2. **Domain knowledge.** [[savance-workplace]] for deep Browser Interface
   detail; [[savance-workplace-suite]] for the feature map across all 11
   client/server apps. Look for the relevant module, its existing settings,
   and any precedent feature that already solves a similar problem.
3. **The codebase.** Check how the thing is actually built before assuming
   how it behaves.
   - If a codebase-knowledge skill is available in this session, use it
     first. <!-- codebase skill hooks in here once it exists -->
   - Otherwise fall back to `Glob` / `Grep` / `Read` over the repository:
     find the module, its config/settings model, its permission checks, and
     any existing feature the ask would sit next to.
   - If no codebase is reachable from this session, say so plainly in the
     Step 8 summary and treat it as a grounding gap — do not silently skip
     it, and do not describe code you have not read.
4. **The live app.** `test.savanceworkplace.com` via Playwright (see
   [[savance-workplace]] for login/nav) when the above don't settle it. The
   house standard of precision — "below the existing **"Screening Alert
   Email"** dropdown" — only reads that way because someone actually checked
   where things live. Match that; don't hand-wave a plausible location.
5. **Still not grounded?** It genuinely needs a product decision, or
   specialist knowledge this session doesn't have. That is a question, and
   Step 6 sorts it.

## Step 6 — Classify every point into one of three buckets

Per point, not per ticket:

| Bucket | Meaning | Where it goes |
| --- | --- | --- |
| **Resolved** | Fully answerable from the ticket, docs, domain knowledge, codebase or live app | Chat summary only (Step 8), one line each with its source. Never a client question. |
| **Vague** | Genuinely needs a business / design / UX decision | Question list — the user gets first crack at it in Step 8 |
| **Contradiction** | The ask conflicts with how the product currently works, or with another ask in the same batch | Question list, flagged as a conflict — **always** surfaced, never quietly resolved in the request's favour |

**Contradictions are the highest-value output of this stage.** Where you find
one, state both sides concretely: what the ticket asks for, what the product
does today, and where you verified today's behavior. Phrase the question as a
choice between the two, not as a bare "please clarify".

**Compound asks:** one ask with several facets ("should it apply to X, and if
not removed should there be a warning, and if so what should it say?") is
*one* question with roman-numeral follow-ups — not three sibling questions.

## Step 7 — Review your own questions (MANDATORY GATE)

Before a single question reaches the user, review the list you just drafted.
This step is not optional and not skippable, and it happens every run — a
question list that has not been through it must not be shown.

Walk the whole list and drop or rewrite anything that fails any of these:

1. **Is it actually unanswered?** Re-check it against the ticket, the
   supplied docs, the domain skills and the codebase one more time. If the
   answer was sitting there, move it to Resolved.
2. **Is it a decision only a human can make?** Business rules, UX choices,
   priorities, scope boundaries — yes. Implementation details the team will
   decide anyway — no, drop it.
3. **Is it a duplicate?** Two asks in a batch often collapse into one
   question. Merge them.
4. **Is it one question, or several wearing a trench coat?** Split it, or
   restructure it as a parent question with follow-ups.
5. **Is it answerable?** A question so broad that any answer would be useless
   ("how should this work?") is a failure of this stage, not a question.
   Narrow it, or propose a default to confirm.
6. **Does it carry enough context to be understood cold**, by someone who has
   not read the ticket?
7. **Is a sensible default available?** If yes, phrase it as a proposal to
   confirm — "We are assuming **X** — could you confirm?" / "Our suggestion
   would be **Y**." — rather than an open question.
8. **Does it end in a question mark?**

State the outcome of this review in one line when you present the list —
e.g. "Reviewed 11 drafted questions: merged 2, dropped 3 as already answered,
split 1." If the review changed nothing, say that too.

## Step 8 — Present findings and collect the user's answers (GATE 2)

Now talk to the user in chat. Present, in this order:

1. **Resolved points** — one line each, with the grounding source (which
   skill, which file, which page of the test server).
2. **Contradictions found** — each with both sides stated.
3. **Open questions** — numbered, grouped by ticket, after the Step 7 review.
4. **Grounding gaps** — anything you could not check (no codebase access, a
   module the domain skills don't cover, a page you couldn't reach).

Then ask the user to go through the open questions and answer any they
already know the answer to.

Record their replies:

- **User knows the answer** → it stops being a client query. Record it as an
  **answer** attached to that question (the `answer` field in the spec, Step
  11), so the doc shows both the point and its resolution and nobody asks the
  client something that was already settled internally.
- **User doesn't know** → it stays a **query to ask the client**.
- **User is unsure / half-answers** → treat it as unknown and keep it as a
  query, but fold what they did say into the question as context.

## Step 9 — Rewrite the remaining queries in plain language

Everything still headed to the client gets a language pass. These go to
people who do not read the codebase and may not know the internal vocabulary.

- Short sentences. One idea per sentence.
- No internal jargon, no table or column names, no ticket shorthand, no
  acronyms the client didn't use first.
- Name UI elements the way the client sees them on screen.
- Give the context before the question, briefly — what you are looking at,
  then what you need decided.
- Prefer a concrete choice ("Should it apply to A, or to both A and B?") over
  an abstract one ("What should the scope be?").
- Read each one back and ask: would someone outside the dev team understand
  this on first read? If not, rewrite it.

**House formatting rule** (shared with `8-asana-bug-report`): every reference to
a specific UI element — page / tab / button / field / modal / dropdown *name*
— is quoted and bolded, written inline in the spec as `**"Manage Options"**`.
Plain descriptive words ("the dropdown", "the page") stay unquoted and
unbolded.

## Step 10 — Approval gate (GUARDRAIL — the file depends on this)

Show the final list — answered points and remaining client queries — and ask
plainly:

> Are these queries okay to generate the document from?

- **User says yes** → continue to Step 11 and generate the doc.
- **User says no**, or asks for changes, or answers something else entirely →
  **do not generate anything.** No `.docx`, no folder, no spec file left
  behind. Revise per their feedback, re-run the Step 7 review on whatever you
  changed, and come back to this gate again.

There is no implicit yes. Silence, a follow-up question, or "looks
interesting" are not approval. Ask again if it's unclear.
## Steps 11-13 - Build and verify the document

**Only after the Step 10 approval.** -> `reference/build-and-verify.md` for the
JSON spec schema and the structural verification.

```bash
python .claude/skills/1-requirement-analysis/scripts/build_queries_doc.py <spec.json> "<ticket folder>/1 - Requirement Analysis.docx"
```

There is no Word COM or LibreOffice here, so the `.docx` is verified
**structurally** - reopen it and walk its paragraphs and tables. Never claim a
visual check you could not run.

## Step 14 — Hand off

Report to the user:

- Absolute path of the generated file.
- Tickets processed — count and names.
- Points resolved from analysis vs. answered by the user vs. still open as
  client queries, with counts.
- Contradictions surfaced.
- Anything deliberately excluded, and why (e.g. children already shaped as QA
  bug reports, per Step 3).
- If the run continued on Opus after the Step 0 warning, one line saying so.
- Explicit confirmation that no Asana state was touched.

Once the client answers these queries, the answered doc is the entry
condition for Stage 01B (`2-spec-doc-generator`), which turns it into the feature spec
and test scope. Mention that as the next step; don't run it unprompted.

The canonical copy lives in the ticket folder,
`tickets/<ticket-id> - <Ticket name>/`. This is a
client-facing document, so if it should also go to the shared review folder
`G:\My Drive\savance_review_task` (a Google Drive Desktop sync mount — the same
delivery path `4-checklist-generation` uses), **ask the user first** rather than
copying it there silently.
