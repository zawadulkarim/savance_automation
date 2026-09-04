# The scope ledger — `0 - Scope Ledger.md`

The pipeline's durable record of **how a ticket was sliced and how far each
slice has got**. Written once by Stage 01, then read and cell-updated by Stages
04 and 05 and by `qa-lead`. It is what makes an iterative run survive a context
compaction, a fresh session, and a subagent boundary — none of which can see the
conversation the slicing was decided in.

## Contents
- What a slice is, and how Stage 01 derives them
- The file format, with a worked example
- The four rules that keep the ledger bounded
- Status vocabulary
- How a stage reads it, and how it writes back
- How rejection feedback maps onto slices

## What a slice is

A **slice** is one independently testable piece of the ticket's scope — the same
unit Stage 01 Step 4 already calls a "distinct ask". A short ticket bundling
seven bullet points is seven asks, and therefore up to seven slices.

Merge asks into one slice when they cannot be verified apart (a setting and the
behaviour it gates are one slice). Split an ask into two slices when it spans
two surfaces a tester would visit separately (the Browser Interface toggle and
the Kiosk screen that honours it).

**Order slices by risk, then by dependency.** The highest-risk slice is `S1`, so
that a run which stalls halfway has covered the part that most needed covering.
A slice that cannot be written without another names it in `Depends on`.

Three to eight slices is the working range. One slice means the ticket did not
need slicing — say so and write a one-row ledger rather than inventing seams.
Over about ten, the ask has outgrown the ticket and that is worth raising.

## Format

```markdown
# Scope Ledger — <Ticket name> (<gid>)

**Ticket:** <URL>
**Slices:** 4 · **Created:** <YYYY-MM-DD>, Stage 01
**Iteration:** 2 of 4 · **Last updated:** <YYYY-MM-DD>, Stage 04

| # | Slice | Risk | Depends on | S04 | S05 | Produced |
|---|-------|------|-----------|-----|-----|----------|
| S1 | Out-status host blocking | High | — | done | done | AC2001-AC2004 · TC-001..TC-009 |
| S2 | Admin toggle and persistence | High | S1 | done | todo | AC2005-AC2007 |
| S3 | Kiosk surface parity | Med | S1 | todo | todo | — |
| S4 | Outlook add-in regression | Low | — | todo | todo | — |

## Slice definitions

### S1 — Out-status host blocking
Visitors must not be able to select a host whose status type is "Out".
**Not in this slice:** the admin setting that enables the behaviour (S2).
**Sources:** ticket bullets 1-2 · spec "What is changing" items 1, 3

### S2 — Admin toggle and persistence
...
```

The header block carries `Iteration: N of M`, so a stage that opens the ledger
knows where the run stands from the first line without parsing the table.

## The four rules that keep it bounded

The ledger is re-read at the start of every iteration. If it grows with each
one, it becomes the cost it was meant to remove.

1. **Fixed rows.** The table has exactly one row per slice, decided at Stage 01.
   Iterations change **cells**, never the number of rows.
2. **Never append prose.** No running commentary, no per-iteration notes, no
   history section. What happened belongs in `0 - Run Log.md`, which is the
   conductor's file; this one holds only current state.
3. **Slice definitions are written once** and are 2-4 lines each. A definition
   that turns out to be wrong is *corrected*, not amended with a note.
4. **`Produced` holds ID ranges, not content.** `AC2001-AC2004`, not the
   criteria themselves. It is the traceability thread from a slice to what it
   became, and it is what lets a reviewer's feedback be routed back to a slice.

A four-slice ledger is about 30 lines and stays about 30 lines to the end of the
run. That is the whole point.

## Status vocabulary

One of these in the `S04` and `S05` cells, and nothing else:

| Status | Means |
|---|---|
| `todo` | Not started. |
| `doing` | This iteration is working it. At most one slice per stage is `doing`. |
| `done` | The slice's content is in the stage's canonical Markdown. |
| `blocked` | Cannot proceed; the reason is a one-line parenthetical — `blocked (needs 2nd account)`. |
| `n/a` | Deliberately gets nothing from this stage. Requires a reason in the same form. |

**`done` means written, not approved.** Approval lives in the artefact's own
`Review Status:` line and is a whole-artefact fact, because the human gate fires
once, at the end. A ledger full of `done` with the Markdown still reading
`DRAFT` is the normal state just before the gate.

## How a stage uses it

At the start of an iteration:

```bash
grep -m1 '^\*\*Iteration:\*\*' "<ticket folder>/0 - Scope Ledger.md"
```

That one line says which iteration is next. Then read the ledger — it is small —
take the first slice whose cell for this stage is `todo` and whose `Depends on`
slices are `done`, and set that cell to `doing`.

**Load only that slice's sources.** The slice definition names them. This is the
saving the whole scheme exists for: iteration 3 does not re-read slices 1 and 2,
and does not re-read the artefact it is appending to.

At the end of an iteration: append the slice's block to the canonical Markdown,
set the cell to `done`, fill `Produced` with the ID range, and bump
`Iteration: N of M`. Update cells with `Edit`; never re-emit the file.

**Do not re-read the accumulated artefact between iterations.** It is
append-only by slice, and the ledger already records what is in it. Re-reading
it each round is the one mistake that makes an iterative run cost more than a
single-pass one.

## When the gate sends work back

The human gate fires once, on the complete artefact, so a rejection can touch
work from several iterations. The ledger is what makes that cheap:

1. Map each piece of feedback to the slice whose `Produced` IDs it names.
2. Set only those slices back to `todo`, with the feedback verbatim in the run
   log — not in the ledger.
3. Re-run those iterations. Slices the feedback did not touch stay `done` and
   are not regenerated.

Feedback that maps to no slice is a **missing slice**: add a row, and say
plainly at the gate that the decomposition missed it. That is the honest
outcome, and it is the failure mode this ledger exists to make visible.
