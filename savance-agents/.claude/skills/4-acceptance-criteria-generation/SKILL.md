---
name: 4-acceptance-criteria-generation
description: Stage 04 — turn an approved feature spec into acceptance criteria, Markdown first: one JSON spec rendered as "4 - Acceptance Criteria.md", self-reviewed, then a blocking human gate; only on approval is it stamped and the .xlsx built and handed to 4-checklist-generation. Input can be a spec doc, Asana ticket, queries doc, AC prose or a feature list. Use when asked to write or generate acceptance criteria or AC, or on /4-acceptance-criteria-generation.
---

# Acceptance criteria generation

Turn an approved feature spec into the acceptance criteria QA works from —
Markdown first, and a human approves it before anything else is built.

## Reference files

Load only what the current step needs.

| File | Read it at |
| --- | --- |
| `reference/house-format.md` | Steps 3-4 — sheet/column layout, the AC ID scheme, calibration bands, writing style |
| `reference/spec-schema.md` | Step 4 — the JSON spec schema and row fields |
| `reference/workbook-build.md` | Steps 8-9 — stamping, the workbook generator, the Excel-COM visual pass, generator sharp edges. **Only after the gate passes.** |

## Two artefacts, in a fixed order

```
   spec document / ticket / answered queries
        |
   0 -- 0 - Scope Ledger.md                 slices, from Stage 01
        |
   1 -- one JSON spec                       the single build source
        |   ^
        |   |  ONE SLICE PER ITERATION
        |   |  append rows, re-render, mark the slice done
        |   +---------------------------------------+
        |                                           |
   2 -- 4 - Acceptance Criteria.md       <- canonical, grows per iteration
        |                                    stays DRAFT for the whole loop
        |
        |   ... every slice done or n/a ...
        |
   3 -- self-review against the rubric      once, over the whole file
        |
   4 -- HUMAN REVIEW GATE               <- blocking, once. No workbook before it.
        |
   5 -- 4 - Acceptance Criteria.xlsx        built from the same spec
        |
   6 -- 5 - QA Checklist.xlsx               [[4-checklist-generation]]
```

**The Markdown is the canonical artefact, not a preview.** It is what the human
approves and what [[5-test-case-generation]] reads downstream — plain text opened with Read, rather than a binary workbook opened
through an openpyxl dump. The `.xlsx` is the delivery copy.

**Both come from one JSON spec, and that is what makes the approval mean
something.** Authored separately they could disagree, and then a human has
approved something the workbook does not say. Revisions edit the spec and
re-render, never the `.md`.

### The Review Status stamp

The Markdown's header block, directly under the title, carries the review state
— the pipeline's durable record of the human's decision, readable by a later
session, a subagent, or a stage that never saw this conversation:

```
**Review Status:** DRAFT
**Review Status:** AWAITING HUMAN REVIEW
**Review Status:** APPROVED — <reviewer name>, <YYYY-MM-DD>
```

It comes from the spec's `review_status` key (or `--status`). Downstream stages
check it with one cheap read:

```bash
grep -m1 '^\*\*Review Status:\*\*' "<ticket folder>/4 - Acceptance Criteria.md"
```

**Only a human's explicit approval writes `APPROVED`,** with the name and date
they actually gave. Writing it yourself forges a sign-off and silently disarms
the gate for every stage after this one.

## Hard rules

1. **No workbook before approval.** The `.xlsx` and the checklist are built at
   Step 8, after the human approves at Step 7. Building them early is not a head
   start — it spends two Excel-COM passes on content that may change and invites
   the human to review the workbook instead of the file the gate is on.
2. **Never write `APPROVED` yourself.** Silence, a question back, or "looks fine
   I guess" is not an approval. No user to ask → stop and return blocked.
3. **Fix the spec, re-render — never hand-edit the `.md` or the `.xlsx`.** An
   edit to either breaks the guarantee that the approved Markdown and the
   delivered workbook agree.
4. **Don't invent product behavior.** Ground every rule in the spec, the ticket,
   or [[savance-workplace]] / [[savance-workplace-suite]]. Ungrounded becomes a
   visible gap row or an `open_questions` entry, never a plausible sentence.
5. **Trace every criteria block to the spec's scope**, and report the
   `spec_coverage` table at the gate. An in-scope item with no criteria is the
   defect that matters most here.
6. **Never overwrite an earlier round.** Add `(rev 2)` to both artefacts,
   keeping their names in step.

## Token discipline

1. **Build the workbook once**, after approval. A revision round costs a
   re-render (milliseconds, no Excel) instead of a rebuild plus a visual pass.
2. **Revise the spec with `Edit`, not a rewrite.** A wording change to one rule
   is one edit, not a re-emission of the whole JSON.
3. **Read the spec document once** and work from your notes. Re-opening a
   `.docx` to re-check a phrase costs more than writing the phrase down did.
4. **Open an `.xlsx` input at most once**, with a small openpyxl script printing
   only the columns you need — never a whole-workbook dump.
5. **Do not re-read a file you just wrote.** The scripts print their own counts.
6. **Hand downstream stages the Markdown path, not its content.**
7. **No browser at this stage.** Ground in the domain skills and the spec's own
   evidence; what they cannot answer becomes a visible gap. Live UI discovery
   belongs to Stage 05, which walks the app anyway — duplicating it here spends
   a browser session for the same answer, one gate earlier than it is needed.

## Step 1 — Gather and scope the input

Resolve what you are writing criteria for, in priority order:

1. **A Feature Spec & Test Scope doc** from Stage 02 — `2 - Spec Document.docx`
   in `tickets/<ticket-id> - */`. **The primary input whenever one exists**: its
   in-scope items are the agreed test scope, so each maps to a criteria block,
   and its out-of-scope list says what deliberately gets none.
2. **An Asana ticket / parent task** — read with `asana_get_task`,
   `opt_fields=name,notes,subtasks.name,subtasks.notes`. A parent with subtasks
   is the common case and becomes one sheet per in-scope child.
3. **An answered queries doc** from Stage 01 — the client's answers are what turn
   an open question into a concrete rule.
4. **Acceptance-criteria prose** pasted in chat.
5. **A feature-list spreadsheet** — a small openpyxl script; Read cannot open
   binary `.xlsx`. Process every row in one run unless told to scope down.

Ask rather than guessing when the scope is genuinely unclear (which subtasks are
in, one sheet or many) — a wrong sheet split means regenerating everything
downstream. Settle **sheet numbering** (continue an existing workbook's, or start
at 1) and **sanity vs regression** here too.

## Step 1B — Read the scope ledger and pick this iteration's slice

Stage 01 sliced the ticket into independently testable pieces and recorded them
in `0 - Scope Ledger.md`. **This stage works one slice per iteration**, so the
criteria are built up across several passes instead of one large one.

```bash
grep -m1 '^\*\*Iteration:\*\*' "<ticket folder>/0 - Scope Ledger.md"
```

That line says where the run stands. Then read the ledger — it is deliberately
small — and take the first slice whose `S04` cell is `todo` and whose
`Depends on` slices are already `done`. Set that cell to `doing`.

Full format, status vocabulary and the rules that keep the file bounded:
`.claude/skills/1-requirement-analysis/reference/scope-ledger.md`

**No ledger?** The ticket was never sliced — Stage 01 did not run, or ran before
this convention. Say so and offer the choice: slice it now (write the ledger
yourself from the spec's in-scope items, using the same risk ordering) or run
the whole ticket in one pass as before. Both are legitimate; a one-slice ledger
is the honest record of the second.

### The loop

Per iteration, for the chosen slice only:

| | |
| --- | --- |
| 1 | Read **that slice's sources** — the definition names them. Steps 2-3 below, scoped to the slice. |
| 2 | Write its criteria rows and **append them to the JSON spec** with `Edit`. |
| 3 | Re-render the Markdown (Step 5). The script rebuilds the whole file from the whole spec — cheap, and its output never enters context. |
| 4 | Set the slice's `S04` cell to `done`, fill `Produced` with the AC ID range it created, and bump `Iteration: N of M`. |

Then take the next slice. **The self-review at Step 6 and the gate at Step 7
happen once, after the last slice** — not per iteration.

**Three rules make the loop cheaper than a single pass rather than more
expensive:**

1. **Load only the current slice's sources.** Iteration 3 does not re-read what
   slices 1 and 2 were built from.
2. **Never re-read the accumulated Markdown between iterations.** You append to
   the spec and re-render; the ledger already records what is in the file.
   Re-reading it every round is the one mistake that makes slicing cost more
   than not slicing.
3. **Edit the spec, never re-emit it.** A slice adds rows; it does not rewrite
   the ones already there.

**The Markdown stays `DRAFT` for the whole loop.** It moves to
`AWAITING HUMAN REVIEW` only when every slice is `done` or `n/a`, because the
gate is on the complete artefact. A ledger full of `done` beside a `DRAFT`
Markdown is the normal state immediately before Step 6.

## Step 2 — Ground every rule before writing it

A rule asserts how the product behaves; a wrong one propagates into the
checklist and then into a bogus bug report. In order:

1. [[savance-workplace]] (Browser Interface detail) and
   [[savance-workplace-suite]] (the 11-app feature map) for the module, its
   existing settings, and precedent features.
2. Then the Stage 02 spec document and the answered queries — its codebase
   evidence is what makes a scope item concrete. **This stage has no browser:** a
   UI detail neither the domain skills nor the spec can settle is a gap to make
   visible, not a rule to guess at, and Stage 05 verifies it live before it
   writes a step.
3. Still ungrounded → **do not invent it.** An explicit open question, or a row
   with the gap visible (Step 3) — never a plausible-sounding fabrication.

## Step 3 — Handle gaps and out-of-scope items visibly

Never silently drop, never silently invent:

- **Explicitly not being tested** (dev said so, deferred, out of contract): keep
  the row, reason in `Description`, `rules` empty (`[]`).
- **Needs specialist/hardware knowledge** you don't have: keep the row as
  `[Needs domain knowledge] <topic> — requires domain knowledge to define
  concrete acceptance rules.` so the gap stays trackable.
- **Duplicated in the source**: write it once and say so.
- **Asked to expand beyond the source**: ask whether to stay strictly grounded or
  also write rules for plausible runtime behavior the source never mentions. The
  user should know which rules are sourced and which inferred.

## Step 4 — Build the JSON spec

**One spec, both artefacts** — the build source for the Markdown at Step 5 and
the workbook at Step 8. Write it to the scratchpad, not the ticket folder; it is
a build input, not a deliverable.

→ `reference/spec-schema.md` for the schema and row fields.
→ `reference/house-format.md` for the layout conventions and the AC ID scheme
the IDs must follow — they become the traceability keys Stages 05 and 06 quote.

## Step 5 — Render `4 - Acceptance Criteria.md`

```bash
python .claude/skills/4-acceptance-criteria-generation/scripts/build_ac_markdown.py <spec.json> "<ticket folder>/4 - Acceptance Criteria.md"
```

Per sheet it renders the identity block, an at-a-glance
`ID | Module | Description | Rules` index — a zero-rule row is marked `0 — gap`,
so a deliberate gap cannot read as an oversight — then one
`### AC<id> — <module>` block per row, then `spec_coverage`, `open_questions`
and a counts table.

**Output:** `tickets/<ticket-id> - <Ticket name>/4 - Acceptance Criteria.md`.
Locate the folder by globbing `tickets/<ticket-id> - */` — the gid is the stable
key. Never overwrite an earlier round; add `(rev 2)`. With no ticket, write to
the working directory.

The script prints AC rows, rules, the achieved rules/row ratio and the gap-row
count. Read it back and check the 3-4.5 band now, before a human looks at
anything.

**Path gotcha (Bash tool = Git Bash/MSYS):** MSYS translates POSIX-looking paths
only for standalone argv tokens. A path interpolated inside a longer string
(`python -c "...open('$SCRATCH/x.json')..."`) is **not** translated and native
Windows Python won't find it. Pass paths as their own arguments. Both generators
take their paths as separate argv tokens for exactly this reason.

## Step 6 — Self-review the draft before a human sees it

**Runs once, after the last slice** — every `S04` cell is `done` or `n/a`. One
pass over the rendered Markdown, whole. It costs a single read and saves a human
round trip, the most expensive thing in this stage. Fix the **spec**, re-render
— never edit the `.md`.

This is the first time you read the artefact as a whole, and that is deliberate:
it is also the only pass that can catch what slicing hides — a rule stated twice
in two slices, two slices that contradict each other, or a seam where neither
slice claimed a behaviour that sits between them. Check for those explicitly.

1. **Coverage** — every in-scope item has a criteria block; nothing out of scope
   has one. An in-scope item with no AC is the defect that matters most. Check
   it against the ledger too: every slice `done`, and every slice's `Produced`
   range actually present in the file.
2. **Groundedness** — every rule traces to the spec, the ticket or a domain
   skill. Anything else becomes a gap row or an `open_questions` entry.
3. **Atomicity** — no rule joining two independently observable outcomes with
   "and". A compound *gate* stays one rule, semicolon-separated.
4. **Verbatim strings** — every user-facing string quoted exactly, double
   quotes, punctuation included.
5. **Ratio** — rules/row inside the 3-4.5 band, or a stated reason why not.
6. **Consistency** — one description voice per workbook; descriptions and rules
   end in a period.
7. **Traceability** — source-supplied IDs carried into `Notes` as
   `Draft ID: <original>`.

Then set `review_status` to `AWAITING HUMAN REVIEW`, re-render, and go to the
gate.

## Step 7 — HUMAN REVIEW GATE (blocking)

**Nothing is built from this spec until a human has approved the Markdown.**

Present, blunt and itemised, no preamble, no praise sandwich:

1. **What is missing** — every `spec_coverage` row that is not `Covered`, every
   gap row, and anything you expected to write criteria for and did not.
2. **Could a tester execute this** — any rule that would leave a tester
   guessing, plus every open question.
3. Counts: AC rows, acceptance rules, rules/row, gap rows — and the slice
   count, so they can see the shape the ticket was cut into.
4. Anything **inferred** rather than sourced, so they can challenge it.
5. The file path.

Then ask, and stop:

> Approve `4 - Acceptance Criteria.md`? On approval I build the workbook and
> derive the QA checklist from it. Otherwise tell me what to change.

- **Explicit approval** → Step 8.
- **Anything else** → **map each piece of feedback to the slice whose
  `Produced` IDs it names**, set only those slices back to `todo`, and re-run
  just those iterations. Slices the feedback did not touch stay `done` and are
  not regenerated — that is what keeps a late rejection cheap. Feedback that
  maps to no slice is a *missing slice*: add a row and say plainly that the
  decomposition missed it. Then re-render and re-present, saying what changed
  and what you deliberately did not. **Three rounds, then stop and ask.**
- **Silence, a question back, or "looks fine I guess"** → not an approval.
- **No user to ask** → **stop.** Return the Markdown path and `BLOCKED —
  awaiting human approval of 4 - Acceptance Criteria.md`, status left at
  `AWAITING HUMAN REVIEW`. Do not build the workbook to be helpful.

## Steps 8-9 — Build and verify the workbook

**Only after the approval.** → `reference/workbook-build.md`. In short: stamp
`review_status` with the name and date the human gave and re-render the Markdown
so the approval lives in the artefact, then build the `.xlsx` from the same
spec, then verify it visually — not just structurally.

```bash
python .claude/skills/4-acceptance-criteria-generation/scripts/build_ac_workbook.py <spec.json> "<ticket folder>/4 - Acceptance Criteria.xlsx"
```

## Step 10 — Chain into the checklist

The approved criteria feed **two** downstream stages, wanting different things:

- [[4-checklist-generation]] — one atomic check item per acceptance rule. Feed
  it the approved **`4 - Acceptance Criteria.md`**: same content as the
  workbook, and a plain-text read rather than an openpyxl walk over merged
  cells.
- [[5-test-case-generation]] — one executable test case per rule, plus whichever
  test types the rule warrants. It reads the approved Markdown, so the AC IDs
  assigned here become its traceability keys, and the `Review Status` line is
  its entry condition. A vague rule costs more at Stage 05 than it does here.

The mapping into the checklist:

- **One acceptance rule → one check item** is the baseline. Both are atomic
  single assertions, so it is mostly mechanical: reword `The system must display
  X` to `Verify that X is displayed`.
- The AC **group column becomes the checklist module**, unchanged.
- A rule spanning several surfaces splits into one check item per surface.
- At the measured 3.8 rules per AC row, a 12-row sheet lands around 40-50 check
  items for **regression**. For **sanity**, keep the happy-path and
  key-validation rules and drop the pure edge cases — don't carry the full
  matrix over.

Compute and report the actual ratio rather than assuming it. This mapping is
derived from the rule counts, not yet calibrated against an accepted
AC-plus-checklist pair for the same feature; if the user has one, measure it and
update this section.

## Step 11 — Hand off and deliver

Report: both artefact paths, the `Review Status` line as it stands and who
approved it, sheets written, AC rows and rules per sheet, the achieved
rules/row ratio, the `spec_coverage` outcome, anything left as a gap
(empty-rules rows, `[Needs domain knowledge]` rows) and anything inferred
rather than sourced.

**The canonical copy is `4 - Acceptance Criteria.md`** in the ticket folder.
That is what the checklist phase and Stage 05 read, and what carries
the approval — written there first and never moved out. The workbook lives
beside it as the delivery copy.

Then *additionally* copy the workbook to the shared review folder under its
house-facing name (`[Acceptance Criteria] <project or batch>.xlsx`):

```
G:\My Drive\savance_review_task
```

A Google Drive Desktop sync mount — a plain file copy is enough; the Drive
client uploads in the background, which this skill cannot observe or confirm.
There is no Google Drive MCP connector here, so don't attempt an API upload. If
the path isn't reachable, tell the user and ask rather than guessing a
substitute; if the destination filename is locked, fall back to a versioned name
(`(v2)`) and say so. An `[Internal]`-prefixed draft may not belong there at all
— ask if the audience is unclear.

---

<!-- Stage 04. Agent: .claude/agents/4-ac-checklist-generator.md
     scripts/build_ac_markdown.py -> the canonical .md (Step 5)
     scripts/build_ac_workbook.py -> the .xlsx (Step 8, after the gate)
     Gate D = Step 7, on the Markdown, blocking. No browser: live UI is stage 05's.
     Upstream stage 02 · Downstream 4-checklist-generation and stage 05. -->
