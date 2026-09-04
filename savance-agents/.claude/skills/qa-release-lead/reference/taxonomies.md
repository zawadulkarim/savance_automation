# The release-tier taxonomies

Referenced from `SKILL.md` Steps 2-6. The classification schemes the survey and
the readiness call are built on.

## Contents
- Step 2 - the lifecycle-state taxonomy (state comes from disk, not from the
  Asana section)
- Step 3 - the five risk factors and how depth is allocated
- Step 4 - the stall taxonomy, with owners
- Step 5 - cross-run pattern analysis
- Step 6 - the three release verdicts and the residual risk register

## Step 2 — Survey the board

Read the project (`asana_get_project_sections`, `asana_search_tasks`), then
establish each ticket's **real** lifecycle state — which is what is on disk,
not what section it sits in.

For each ticket, glob `tickets/<gid> - */` and read `0 - Run Log.md` if there
is one. Classify.

**Two greps settle most of the classification without opening a document.**
Stages 04 and 05 stamp their human approval into the header block of their
canonical Markdown, so the state of both gates is one cheap read each:

```bash
grep -m1 '^\*\*Review Status:\*\*' "tickets/<gid> - "*/"4 - Acceptance Criteria.md"
grep -m1 '^\*\*Review Status:\*\*' "tickets/<gid> - "*/"test-cases.md"
```

Prefer that to a run log's own account of a gate where the two disagree: the
stamp is in the artefact the next stage reads, and it is what Stage 05 and
Stage 07 actually enforce. A run log claiming an approval the artefact does
not carry is itself worth reporting.

The states:

| State | What it means |
| --- | --- |
| `NOT STARTED` | No folder, no run log |
| `IN ANALYSIS` | Stage 01 running or its gate not passed |
| `HELD — CLIENT` | Queries sent, answers not back. **Not a QA blocker; an external one.** |
| `IN SCOPE` | Stage 02 running, or spec not yet passed at Gate C |
| `IN TEST DESIGN` | Stage 04 running, or `4 - Acceptance Criteria.md` not yet `APPROVED` at Gate D. A `.md` sitting at `AWAITING HUMAN REVIEW` with no workbook beside it is a run parked on a human, not a stalled stage — say which. |
| `IN CASE DESIGN` | Stage 05 running, or `test-cases.md` not passed at Gate E. A `test-cases.md` still reading `AWAITING HUMAN REVIEW` with no `test-cases.xlsx` beside it is parked at the gate — check the run log for how long. |
| `READY TO EXECUTE` | `test-cases.md` reads `APPROVED` and `test-cases.xlsx` exists — or, on an older run, an approved checklist |
| `IN EXECUTION` | Test cases or checklist partly filled |
| `DEFECTS OPEN` | Filed bugs not yet closed |
| `CLOSED` | Signed off |
| `UNTRACKED` | On the board, no lifecycle run at all — **the state most worth reporting** |

`UNTRACKED` is the portfolio equivalent of "what is missing". A ticket nobody
has looked at does not appear in any run log, will not appear in any status
that is built from run logs, and is exactly what ships broken.

**This survey is where a Workflow script earns its place** — see the last
section. It is N independent read-only assessments with no human in the loop,
which is the one shape the Workflow tool is actually for.

## Step 3 — Risk-rank and allocate depth

Not everything deserves the same testing. Rank on five factors, and **show
them** — a ranking without its reasoning does not survive its first argument:

| Factor | Raises risk when… |
| --- | --- |
| **Blast radius** | It touches shared code several of the 11 apps consume ([[savance-workplace-suite]]) |
| **Change type** | New feature or reworked flow, rather than a contained fix or a config default |
| **Client visibility** | The client asked for it, will look for it, or it is in a demo path |
| **Unknowns** | Queries unanswered, spec provisional, behaviour undocumented |
| **Regression surface** | It sits under something that already works and people rely on |

Then allocate:

| Depth | For | Means |
| --- | --- | --- |
| **Deep** | High blast radius or high unknowns | Full lifecycle, regression matrix, cross-app checks |
| **Standard** | Normal feature work | Full lifecycle, sanity on adjacent areas |
| **Sanity** | Contained, low-radius, well-understood | Checklist against the AC only |
| **Defer** | Not in this release, or blocked beyond it | Say what defers it and what it costs |

**Say what you are not testing, and why.** A plan that only lists what gets
covered reads as complete coverage. The exclusions are the honest half, and
they are what the argument after a release is actually about.

## Step 4 — Find the stalls

Walk the run logs for anything stuck, and give each one an owner and an age:

- **Held on a client answer** — for how long, which queries, who chases.
- **Stuck at a human gate** — a draft presented and never answered. This is
  usually the cheapest thing on the board to fix and the easiest to miss.
- **Looping** — a stage that has been through three revision rounds at its
  human gate. That is a designed escalation and it needs a decision, not another
  round: the gap is usually upstream of the artefact being re-read.
- **Blocked on a dev fix** — a filed defect with no movement.
- **Blocked on environment** — credentials, a broken test server, missing data.

Every stall gets: the ticket, what it is waiting on, **whose move it is**, and
how long it has been waiting. A stall list without owners is a complaint, not
a management artefact.

## Step 5 — Look for what repeats

This is the tier's real leverage, and nothing below it can see it. One bad
spec is a lead's problem; four specs failing the same way is yours.

Read across the run logs, the gate feedback recorded in them, and the filed
bugs, and ask:

- **Which gate rejection keeps recurring?** If half the specs this release were
  sent back for a missing app, the gap is in the Stage 02 exploration step, not
  in four separate authors. With every gate a human, the run logs are the only
  place this pattern is visible at all — which is why Gate feedback is recorded
  verbatim.
- **Which module keeps producing defects?** That module wants deep depth next
  release regardless of how small its next change looks.
- **Which gate keeps taking three rounds?** Either the stage is under-briefed
  or the gate's expectations were never written down.
- **What keeps arriving unanswered?** If client queries routinely stall, the
  query stage is asking the wrong questions, or asking too many.

Report these as **process findings, separate from the ticket findings**, with
the specific change you would make. A pattern named without a proposed change
is an observation, not a finding.

## Step 6 — The release readiness call

Only when the user asked for a go/no-go. Do not volunteer a verdict on a
status request — a verdict nobody asked for gets quoted later as though
someone did.

Three verdicts, and nothing in between:

| Verdict | Condition |
| --- | --- |
| **GO** | Every in-scope item executed and passed; open defects are known, accepted and named; residual risk is understood |
| **GO WITH KNOWN RISK** | Shippable, but specific scope is unverified or specific defects are open. **Every one is named.** This is the honest verdict most releases deserve. |
| **NO-GO** | Something unresolved would break a user, or so much is unverified that the call cannot be made. Say which. |

Every verdict carries a **residual risk register**:

```markdown
| # | Risk | Why it is open | Blast radius | What would close it |
| --- | --- | --- | --- | --- |
| 1 | Kiosk visitor sign-in untested against the new watchlist rule | No test environment for Kiosk this cycle | Kiosk, Browser Interface | One manual pass on a staged Kiosk |
```

Rules for the register:

- **"Unverified" is not "low risk."** If you did not test it, the risk is
  *unknown*, and you say unknown. Downgrading unknown to low is the single
  most damaging thing this tier can do.
- **Every open defect is listed**, including ones deliberately accepted. An
  accepted defect that nobody wrote down is an unaccepted defect.
- **Name what would close each risk** — that is what turns a register into a
  plan rather than a disclaimer.

Then state the verdict in one line, first, before any of the detail.
