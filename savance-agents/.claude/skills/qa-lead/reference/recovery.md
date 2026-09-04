# When a gate fails, a session ends, or the run will not converge

Referenced from `SKILL.md`. Read this when something has actually gone wrong —
a gate did not pass, the conversation is being compacted or resumed, or a stage
is looping. None of it applies to a run that is progressing normally.

## Contents
- The revision protocol — capturing feedback and picking the re-entry point
- Keeping the run alive across a long session, a compaction, or a resume
- Stop conditions — when to halt the pipeline and say why

## The revision protocol — the "else, improve it" path

When a gate does not pass:

1. **Capture the feedback verbatim** into the run log. Not your paraphrase —
   their words. Paraphrase is where requirements get quietly softened.
2. **Turn it into a revision brief**: what must change, what must not, and
   which step of the stage it re-enters.
3. **Pick the re-entry point honestly.** A gap means the exploration failed —
   go back to the stage's research step, not to a wording pass. Rewriting the
   sentence around a missing app does not add the app.
4. **Re-invoke the stage** with the brief. Do not hand-edit its artefact
   yourself; the stage owns its output and its own quality checks, and an
   artefact edited outside the stage has bypassed them.
5. **Re-present at the same gate.** Say what changed and what you deliberately
   did not change, with the reason.

**At Gates D and E the loop runs inside the stage.** Stage 04 and Stage 05
each take the feedback, revise their own artefact, and re-present at their own
gate — you do not re-invoke them per round, and you do not hand-edit their
Markdown. What you do is log each round's feedback verbatim, because the stage
will not: it holds the conversation, the run log holds the record.

**Three human rounds on one stage, then stop and ask.** If a gate has not
passed after three revisions, the disagreement is not going to resolve by a
fourth attempt. Both stages cap their own gate loops at three for the same
reason. Lay out what the user wants, what the stage keeps producing,
and where you think the mismatch is — then ask whether to keep going, park it,
or change the approach.

## Keeping the run alive across a long session

This pipeline can span days and will outlive the context window.

- **The run log is the durable state.** Anything that matters — a gate
  decision, an override, a document received, a stage skipped — goes in the
  file, not just in the conversation. If it is only in chat, it is already
  lost.
- **Between stages, suggest compacting** if the conversation is long. Say so
  before starting the next stage, not in the middle of one. The run log means
  a compact costs nothing.
- **After a compact or a resume, re-read the run log first** and state where
  the run stands before doing anything. Do not reconstruct the state from
  memory of the conversation.

## Stop conditions

Halt the pipeline and say why:

- **No user to answer a gate.** Park, return blocked and clearly labelled.
- **The environment is broken** and `0-qa-initiation` cannot fix it.
- **The ticket changed underneath you** — the Asana body or scope was edited
  mid-run. Flag it; the completed stages may now be wrong.
- **A stage will not converge** — three human rounds at any gate, or Stage 04
  or Stage 05 still not approved after three rounds at its own gate. With every
  gate a human, a fourth round is the same person reading the same artefact
  again; the problem is upstream of the wording.
- **A gate is unanswerable** — nobody is there to approve
  `4 - Acceptance Criteria.md` or `test-cases.md`. The stage returns
  `BLOCKED — awaiting human approval`; park the run at that point and say so.
  Never approve on their behalf to keep the pipeline moving.
- **The ask has outgrown the ticket** — the work now covers several features.
  Say so; splitting it is a decision for the user, not a thing you absorb.

---
