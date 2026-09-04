# Savance QA lifecycle

This repository is not an application — it is the **Savance QA lifecycle**
itself, built as Claude Code skills and agents. Each numbered stage takes a
client ticket one step further through the STLC, from raw request to signed-off
release. The `.claude/skills/*/SKILL.md` files are the procedures; the
`.claude/agents/*.md` files are the stage definitions that run them.

## The lifecycle

| Stage | Agent | Model | Skill(s) | Asana |
| --- | --- | --- | --- | --- |
| 00 | `0-qa-initiation` | haiku | `0-qa-initiation` | — |
| 01 | `1-requirement-analysis` | sonnet | `1-requirement-analysis` | read-only |
| 02 | `2-spec-doc-generator` | sonnet | `2-spec-doc-generator` | read-only |
| 04 | `4-ac-checklist-generator` | opus | `4-acceptance-criteria-generation` + `4-checklist-generation` | read-only |
| 05 | `5-test-case-generator` | sonnet | `5-test-case-generation` | read-only |
| 07 | `7-testing-agent` | opus | `7-locator-extraction` + `7-test-authoring` + `7-test-healing` + `7-playwright-automation` | none |
| 08 | `8-bug-reporting` | sonnet | `8-asana-bug-report` | **writes** |
| 09 | `9-qa-signoff` | sonnet | `9-asana-final-comment` | **writes** |

**Stage numbering has two gaps, 03 and 06, and they are deliberate.** Those
were the spec reviewer and the test-case reviewer — automated review gates that
sat between a generator and its human. They were removed: **every gate in this
pipeline is now a person.** The numbers are not reused, because the ticket
folder's file prefixes and every stage's cross-references are built on them,
and renumbering seven stages to close two holes trades a permanent source of
confusion for a cosmetic one.

**What removing them changed, and what it costs.** The two reviewers were the
pipeline's most expensive component by a wide margin — each ran an Opus agent
that rebuilt the evidence base from scratch, up to twice, on every ticket. They
were also its only defence-in-depth. With them gone, **Gate C and Gate E are
load-bearing in a way they were not before**: a scope item nobody notices is
missing, or an acceptance rule with no test case, now ships. That is why both
stages present *what is missing* first, show every claim beside the evidence
behind it, and name what they could not verify — a gate is only real if the
person holding it can falsify what they are being shown.

**The model column is a cost decision with a rule behind it.** Mechanical
stages go cheap (Stage 00 is a script and a login); template-shaped writing
under a human gate goes to Sonnet (Stages 01, 02, 05, 08, 09); and every stage
whose output nothing re-checks before delivery stays on Opus — Stage 04 (its
only checks are a self-review and the human) and Stage 07 (classifying a red is
the whole job). Stage 05 is the deliberate exception on the other side: it is
the highest-volume writing stage, and it stays on **Sonnet** because Gate E is
a blocking human read of every case. That was a judgement call made with the
reviewers' removal, and it is the one to revisit first if suites start reaching
Gate E with real gaps in them. Don't move a stage down a tier without asking
what would catch its mistake.

**Stages 04 and 05 are Markdown-first, and each holds its own human gate.**
Both render a plain-text canonical artefact, stop, and ask a person to approve
it — and only then build the workbooks the team files away:

```
Stage 04   one JSON spec -> 4 - Acceptance Criteria.md -> GATE D -> .xlsx + 5 - QA Checklist.xlsx
Stage 05   4 - Acceptance Criteria.md (APPROVED) -> test-cases.md -> GATE E -> test-cases.xlsx
Stage 07   test-cases.md (APPROVED) -> the Playwright suite
```

The order is the point. A reviewer reads a text file in one pass; a revision
costs a re-render rather than a workbook rebuild plus an Excel-COM visual pass;
and nobody is handed a finished-looking `.xlsx` to argue with when the content
is still in question. It is also where most of the pipeline's token cost went:
the Excel is now built once, after approval, instead of on every round.

**The approval is stamped in the artefact, not just in the chat.** The header
block of each canonical Markdown, directly under the title, carries
`**Review Status:**` — `DRAFT`, `AWAITING HUMAN REVIEW`, or
`APPROVED — <reviewer>, <YYYY-MM-DD>`. Stage 05
checks Stage 04's stamp before it starts and Stage 07 checks Stage 05's before
it writes a spec, so a gate holds across a subagent boundary, a fresh session
and a context compaction — none of which can see the conversation the approval
was given in. **Only a human's explicit yes writes `APPROVED`;** writing it on
their behalf forges a sign-off and silently disarms every stage downstream.

Stage 04 renders the same JSON spec twice — `build_ac_markdown.py` for the
Markdown, `build_ac_workbook.py` for the workbook. That is deliberate: if the
two were authored separately they could drift, and an approval that does not
bind the delivered workbook is worth nothing. Revisions edit the spec and
re-render; never hand-edit either artefact.

**Stage 05's traceability matrix is the evidence at Gate E**, and with no
reviewer behind it nothing re-derives coverage independently. So the rule is
that the matrix is built by walking the acceptance criteria list and looking
each one up in the cases that were actually written — never from intent, and
never carried forward stale from a previous round. Every `Not Covered` and
`Requires Clarification` row has a matching entry in Assumptions or
Clarifications; a bare status is a claim with nothing behind it, and nobody
downstream will catch it. The same applies to Stage 02's codebase evidence,
which is why it is presented at Gate C rather than left in the chat log.

**No stage dispatches another stage.** Neither generator carries the `Agent`
tool any more — the two review gates were its only use, and a tool nobody needs
is a schema shipped into that stage's context on every dispatch. Stages 02 and
05 are now flat: read the inputs, write the artefact, hold the gate.

**Stage 04 has no browser, deliberately.** It grounds its rules in the domain
skills and the Stage 02 spec's codebase evidence; a UI detail neither can
settle becomes a visible gap. Stage 05 walks the live app anyway before it
names an element, so verifying twice buys the same answer at two sessions'
cost — and buys it a gate earlier than anyone needs it.

Stage 07 is the one stage backed by **executable code** rather than documents:
it lives in `automation_savance_workplace_web/` (Playwright + TypeScript,
Page-Object) and turns the Stage 05 test cases — or the Stage 04 checklist —
into a suite that runs. Its four
skills run in a fixed order — locators, then specs, then the run, then healing —
with `7-playwright-automation` loaded underneath all of them as the repo's own
layout and app-quirk reference.

Its governing rule is the one thing to get right about it: **when a test fails
because the script is wrong, fix the script; when it fails because the
application is wrong, the test stays red and untouched** and becomes a candidate
defect for Stage 08. Bending an assertion to clear a red is the one
unrecoverable mistake in the lifecycle — it ships the bug *and* destroys the
evidence.

Above them sit two conductors: `qa-lead` (runs one ticket end to end, holding a
human gate between stages) and `qa-release-lead` (whose unit of work is the
release rather than the ticket).

The `savance-workplace`, `savance-workplace-suite` and
`savance-ai-assistant-testing` skills are domain knowledge, not stages — they
stay unnumbered and every stage draws on them.

## Slicing — how a ticket is worked in iterations

**Stage 01 cuts the ticket into slices; Stages 04 and 05 work one slice per
iteration.** A slice is one independently testable piece of scope — the same
unit Stage 01 already called a "distinct ask". Stages 02 and 07 are *not*
sliced: the spec has to be whole to be a scope picture, and Stage 07 takes the
approved suite whole.

```
Stage 01  decompose  ->  0 - Scope Ledger.md      S1..Sn, ordered by risk
                              |
Stage 04  iterate: S1, S2, ... Sn                 append to 4 - Acceptance Criteria.md
                              |                   (stays DRAFT for the whole loop)
          self-review once, whole file
          GATE D once  ->  stamp  ->  the two workbooks
                              |
Stage 05  iterate: S1, S2, ... Sn                 append to test-cases.md
                              |                   (reads only that slice's AC range)
          rebuild traceability once
          GATE E once  ->  stamp  ->  test-cases.xlsx
                              |
Stage 07  whole suite, not sliced
```

**The gate fires once, at the end of the loop, on the complete artefact.** The
iterations are how the work is *produced*, not how it is reviewed — a human
still reads one finished Markdown and approves it once. That is a deliberate
trade: fewer, larger reviews rather than many small ones.

**The ledger is state, not history.** `0 - Scope Ledger.md` holds a fixed row per
slice with cells updated in place — never appended prose. A four-slice ledger is
about 30 lines at the start of the run and about 30 lines at the end. What
*happened* goes in `0 - Run Log.md`, which is the conductor's file. Full format,
status vocabulary and the four bounding rules:
`.claude/skills/1-requirement-analysis/reference/scope-ledger.md`.

**Why this saves tokens rather than spending them.** Three rules carry the whole
benefit, and getting any of them wrong inverts it:

1. **An iteration loads only its own slice's sources.** Iteration 3 does not
   re-read what slices 1 and 2 were built from. This is the saving.
2. **No stage re-reads its accumulated Markdown between iterations.** It appends
   (Stage 05) or edits the spec and re-renders (Stage 04); the ledger already
   records what is in the file. Re-reading it every round is the one mistake
   that makes an iterative run cost *more* than a single-pass one.
3. **Whole-file structures are rebuilt once, at the end** — Stage 04's
   self-review, and Stage 05's traceability matrix and coverage summary.
   Running either per slice multiplies its cost by the slice count and still
   misses the cross-slice gaps — and the same is true of the human gate, which
   is why each stage holds exactly one, over the finished artefact.

Be honest about what slicing does and does not buy. It does not reliably cut the
*total* tokens of a clean run; what it does is **bound the peak** — no single
context holds the whole ticket — and make the work **resumable**, because the
ledger survives a compaction, a fresh session and a subagent boundary. Its
largest concrete win is on rework: a rejection at Gate D or E maps feedback to
the slices whose `Produced` ID ranges it names, and only those slices are
regenerated. Feedback that maps to no slice is a **missing slice** — add a row
and say plainly that the decomposition missed it.

This is Anthropic's *structured note-taking* pattern, which their context
engineering guidance describes as the technique that "excels for iterative
development with clear milestones". The ledger is the note; the slices are the
milestones.

## Conventions

**Numbering.** Agent filename, its `name:` frontmatter, and its `# Stage NN`
heading always agree. A stage that owns several skills gives all of them its
prefix — Stage 04 owns two `4-` skills, Stage 07 owns four `7-` ones. **03 and
06 are retired numbers** (the two review gates) and are never reassigned.

**Ticket folder.** Every file-producing stage writes into one shared folder per
ticket, named for the stage that produced it:

```
tickets/<ticket-id> - <Ticket name>/
    0 - Run Log.md                       qa-lead, the conductor's record
    0 - Scope Ledger.md                  stage 01, the slices 04 and 05 iterate
    1 - Requirement Analysis.docx        stage 01
    2 - Spec Document.docx               stage 02
    4 - Acceptance Criteria.md           stage 04   canonical, gated
    4 - Acceptance Criteria.xlsx         stage 04   built after Gate D
    5 - QA Checklist.xlsx                stage 04   built after Gate D
    test-cases.md                        stage 05   canonical, gated
    test-cases.xlsx                      stage 05   built after Gate E
    6 - Test Review.md                   stage 07
```

The two `0 -` files are pipeline state rather than deliverables: `0 - Run Log.md`
records what happened, `0 - Scope Ledger.md` records where things stand. Both
outlive the context window, which is the only reason either exists.

Two more files break the numbering on purpose. `test-cases.md` and
`test-review.md` are read **by machine** — Stage 07 opens the first by name, and both are the
canonical copy their stage rebuilds across rounds — so a stable filename is
worth more there than a position in the listing. Everything a human reads in
order keeps its number.

`4 - Acceptance Criteria.md` and `4 - Acceptance Criteria.xlsx` share their
number on purpose too: they are one artefact in two renderings of the same
JSON spec, and the human reads them at that position in the folder. Stage 05
opens the `.md` by that exact name, so don't "tidy" it into an unnumbered
`acceptance-criteria.md`.

**The canonical Markdown of a gated stage carries its approval in its header
block**, as `**Review Status:** ...` directly under the title. Downstream
stages find it with `grep -m1 '^\*\*Review Status:\*\*'` rather than re-reading
the artefact — so keep it in the header, keep the exact spelling, and never
write `APPROVED` without a human's explicit yes.

Stage 07's *code* — the page objects and specs — does not go in the ticket
folder. It belongs in `automation_savance_workplace_web/`, whose canonical
review file is `test-review.md`; `6 - Test Review.md` is a copy of it, so the
ticket folder tells the whole story on its own. Its `6 -` prefix is a
leftover from when Stage 06 existed and is kept only because it is the position
a reader expects it in the folder listing; it is Stage 07's file.

The Asana gid is the stable key — locate an existing folder by globbing
`tickets/<ticket-id> - */`, never by reconstructing the name. Never overwrite an
earlier round; add a `(rev 2)` suffix. Copies delivered to the shared review
folder `G:\My Drive\savance_review_task` keep their house-facing names, because
that folder is read by people who never see the ticket folder.

**Gates are real.** Stages 01 through 07 stop and wait for a human at
defined points, and several refuse to write their deliverable without an
explicit yes; `qa-lead` holds a gate between every stage.

**Gate D (Stage 04, on `4 - Acceptance Criteria.md`) and Gate E (Stage 05, on
`test-cases.md`) are held inside their stages, not by the conductor.** They are
no less real for that — both are blocking, both refuse to build the derived
workbooks without an explicit approval, and both stamp the outcome into the
artefact. `qa-lead` records them and does **not** re-present the same artefact
afterwards: asking twice trains the reviewer to skim, and skimming is how the
missing case ships. A stage that returns `BLOCKED — awaiting human approval` is
working correctly; park the run there.

Never answer a gate on the user's behalf, and never treat silence as approval.
Stages 01, 02 and 05 also warn — but do not block — when the session is on
Opus rather than Sonnet.

**Credentials** live in `.env` (managed by stage 00). Never print their values.

**Tool allowlists are the cheapest constraint in the repo, and they are load
bearing twice over.** Every MCP tool named in an agent's frontmatter ships its
whole JSON schema into that agent's context on every dispatch, whether it is
called or not — so a tool a stage does not need is a permanent tax on a stage
that runs dozens of times a release. It is also the only constraint a prompt
cannot talk its way around: **no stage carries `ToolSearch`**, which is what
turns "never load a mutating Asana tool" from a sentence a stage is asked to
obey into a thing it structurally cannot do. Stage 07 holds no Asana tool at
all, Stage 04 holds no browser, Stage 00 holds no `Write` or `Edit` (its `.env`
merge script is the only writer), **no stage holds `Agent`** now that nothing
dispatches a review subagent, and Stages 08 and 09 hold exactly the one or two
mutating tools their job needs.

When adding a tool to a stage, say in one line why the stage cannot do its job
without it. When a stage's prose says "do not load X via `ToolSearch`", the fix
is to remove `ToolSearch`, not to repeat the sentence.

**Where the tokens actually go**, in descending order — worth knowing before
optimising anything:

1. **Frontmatter `description:` of every agent and skill.** These sit in the
   system prompt of *every* session, used or not. Keep them to routing and
   trigger words; the procedure belongs in the body.
2. **MCP tool schemas**, per the allowlist rule above.
3. **A review gate run inline instead of as a subagent** — the single most
   expensive mistake available here, because it is paid again on every
   subsequent turn of the generator's run.
4. **A `SKILL.md` that carries what only some runs need.** See *Skill
   structure* below: the body loads in full on every invoke, a `reference/` file
   loads only when a step opens it.
5. **Re-derivation**: a browser session for a fact the domain skills hold, a
   whole-workbook dump for three columns, a `.docx` reopened for a phrase, a
   verifying read of a file just written, an `.xlsx` rebuilt per review round.
   Every stage's "Token discipline" section is a list of these; they are
   correctness rules as often as cost rules.

## Maintaining the stages

**When the user gives feedback on how a stage should behave — its inputs,
gates, output paths, naming, numbering, tone, model, or constraints — write it
into that stage's files in the same turn.** Applying the correction only to the
current run is not enough, and neither is promising to remember it.

The stages are executed by subagents and by future sessions that never see the
conversation the feedback was given in. A correction that lives only in chat is
silently lost the next time the stage runs, and the user has to give the same
feedback twice. These files are the pipeline's only durable memory.

How to do it properly:

- **Update both files.** The skill and the agent duplicate the gates, hard
  constraints and output paths on purpose. A one-sided edit leaves them
  contradicting each other.
- **Chase every cross-reference** the change touches: sibling stages,
  `[[wiki-links]]`, the HTML footer comment blocks, documented script paths,
  numbered file and folder names, and any downstream stage that reads the
  output.
- **Anchor your replacements on renames.** Several stage names are prefixes of
  others — `4-acceptance-criteria` sits inside `4-acceptance-criteria-generation`
  — so a bare find-and-replace corrupts the longer name. Anchor on `[[...]]`
  brackets, a trailing newline, or the full path.
- **Verify by grepping for the old string** afterwards. Don't assume the edit
  was complete.
- **State rules as numbered hard rules or gate steps**, not as prose buried
  mid-file.

## Skill structure — progressive disclosure

Every skill is `SKILL.md` plus a `reference/` directory, and the split is the
point rather than tidiness. Anthropic's skill-authoring guidance is the rule
followed here:

- **`SKILL.md` stays under 500 lines** and reads as an operating procedure with
  pointers — the steps, the gates, the hard rules, the script invocations.
- **`reference/*.md` holds what only some runs need**: format specs, JSON
  schemas, trap catalogues, templates, post-gate build instructions. A bundled
  file costs **zero context until something opens it**, so a run that stops at
  a gate never pays for the workbook-building instructions behind it.
- **References are exactly one level deep from `SKILL.md`.** Never
  `SKILL.md → a.md → b.md`: Claude previews a nested file with `head` rather
  than reading it whole, so the content arrives truncated and silently wrong.
  Two reference files may *mention* each other in prose, but never as a link to
  follow.
- **Every reference file over 100 lines opens with a `## Contents` list**, so a
  partial read still shows the full scope of what is in there.
- **`SKILL.md` names each reference file and says at which step to read it.** A
  reference file nothing points to is dead weight; a step that needs one and
  does not name it gets guessed at instead.

When adding to a skill, ask which of the two it belongs in. Procedure, gates and
invariants go in `SKILL.md`; everything a run might not need goes in
`reference/`. When `SKILL.md` approaches 500 lines, split it rather than trim
something load-bearing.

**Write for a model that is already competent.** The question for every
paragraph is whether it tells Claude something it does not already know about
*this* repo, this app, or this team's conventions. Verified app quirks, house
templates, gids, calibration bands and the reasons behind a gate all earn their
place. General explanations of how QA, Excel, Playwright or PDFs work do not.

**Scripts are executed, not read.** Each document-producing skill keeps exactly
one `scripts/build_*.py` per deliverable, and `SKILL.md` gives the invocation
rather than the algorithm — a script's contents never enter context, only its
output. Stage 00's `env_manager.py` is the same bargain: the merge logic stays
out of context and stays correct. Delete a script only when the deliverable it
builds is gone.

## Working on the generator scripts

Each document-producing skill has a `scripts/build_*.py` that turns a JSON spec
into the deliverable. They need `python-docx` / `openpyxl`. There is no Word-COM
or LibreOffice here, so `.docx` output is verified **structurally** — reopen the
file and walk its paragraphs and tables — not visually. The Excel skills do have
an Excel-COM visual pass; don't skip it because a sibling workbook looked fine.

**Stage 04 renders one spec through two scripts**, and they have to agree.
`build_ac_markdown.py` deliberately duplicates the AC ID scheme
(`AC{sheet index}{seq:03d}`, plus a row's `id` override) rather than importing
it, so the Markdown renders on a machine with no `openpyxl`. Change that rule
in one script and you must change it in the other — the IDs are the
traceability keys Stage 05 quotes in its matrix, so a divergence breaks
traceability silently, and it breaks it *after* a human has approved the
Markdown. The Markdown renderer also enforces the workbook's layout invariants,
so a spec can never be approved as Markdown and then fail at the `.xlsx` step.

The documented invocation path inside each SKILL.md must match the real file on
disk. After any skill rename, re-check that every `python .claude/skills/.../*.py`
line still resolves.
