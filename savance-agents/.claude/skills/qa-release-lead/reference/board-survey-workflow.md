# Optional: the board survey as a Workflow script

Referenced from `SKILL.md`. **Only run this if the user has explicitly opted
into multi-agent orchestration.** The survey is non-interactive and
embarrassingly parallel across tickets, which is what makes it a fit; the
readiness call it feeds is still yours.

## Contents
- Why this fan-out is safe where the pipeline spine is not
- The script

## The board survey as a Workflow script

Assessing N tickets is non-interactive, read-only, and independent per ticket —
the one shape the Workflow tool is genuinely for, and the clear contrast with
[[qa-lead]], whose gates rule it out entirely.

Run it only if the user has opted into multi-agent orchestration, and only for
a board big enough to be worth it (roughly ten tickets or more; below that,
just read them).

```javascript
export const meta = {
  name: 'qa-board-survey',
  description: 'Assess every ticket on the board for lifecycle state, stalls and risk',
  phases: [{ title: 'Assess' }, { title: 'Synthesize' }],
}

const STATE = {
  type: 'object',
  properties: {
    gid: { type: 'string' },
    name: { type: 'string' },
    state: {
      type: 'string',
      enum: ['NOT STARTED', 'IN ANALYSIS', 'HELD - CLIENT', 'IN SCOPE',
             'IN TEST DESIGN', 'READY TO EXECUTE', 'IN EXECUTION',
             'DEFECTS OPEN', 'CLOSED', 'UNTRACKED'],
    },
    evidence: { type: 'array', items: { type: 'string' } },
    stalledOn: { type: 'string' },
    whoseMove: { type: 'string', enum: ['QA', 'client', 'dev', 'nobody'] },
    blastRadius: { type: 'array', items: { type: 'string' } },
    unknowns: { type: 'array', items: { type: 'string' } },
    risk: { type: 'string', enum: ['high', 'medium', 'low', 'unknown'] },
  },
  required: ['gid', 'state', 'evidence', 'risk', 'whoseMove'],
}

const assessed = await pipeline(
  args.tickets,                        // [{gid, name}, ...] from the Asana read
  t => agent(
    `Assess ticket ${t.gid} "${t.name}". Read it in Asana. Glob ` +
    `tickets/${t.gid} - */ and read 0 - Run Log.md plus any artefacts. ` +
    `State comes from what is ON DISK, not the Asana section — a ticket in ` +
    `"Ready for QA" with no spec is not ready. Cite the file or field behind ` +
    `every claim. Use risk "unknown" when you could not determine it; never ` +
    `default an unassessed ticket to "low".`,
    { label: `assess:${t.gid}`, phase: 'Assess', schema: STATE }
  )
)

const rows = assessed.filter(Boolean)
const dropped = args.tickets.length - rows.length
if (dropped) log(`${dropped} ticket(s) failed assessment — reporting as UNKNOWN, not omitting`)

return { rows, dropped }
```

Two things that script does on purpose:

- **`risk: 'unknown'` is a real value.** An agent that could not assess a
  ticket must not return "low" — that is the aggregation failure in miniature.
- **Dropped tickets are logged, not silently missing.** A survey that quietly
  covers 19 of 23 reads exactly like one that covered all 23.

Synthesis stays with you, in the main conversation, because the ranking and
the verdict are judgement calls the user needs to be able to argue with.
