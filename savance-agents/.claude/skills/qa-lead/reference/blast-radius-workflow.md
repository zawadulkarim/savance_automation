# Optional: the blast-radius sweep as a Workflow script

Referenced from `SKILL.md`. **Only run this if the user has explicitly opted
into multi-agent orchestration.** It is an accelerator inside Stage 02, not part
of the pipeline spine — the findings still go back into that stage's own scope
reasoning.

## Contents
- Why the spine cannot be a Workflow, and why this one fan-out can
- The script, with its sweep and confirm phases

## Where a Workflow script actually helps

Not for the spine — the gates make that impossible. But Stage 02's blast-radius
question ("which of the 11 apps touch this shared code?") is exactly what the
Workflow tool is for: non-interactive, embarrassingly parallel, and the slowest
part of the stage.

Only run this if the user has opted into multi-agent orchestration. It is an
accelerator inside Stage 02, not a replacement for it — the findings still go
back into the stage's own scope reasoning:

```javascript
export const meta = {
  name: 'blast-radius-sweep',
  description: 'Fan out across the app family to find every consumer of the changed code',
  phases: [{ title: 'Sweep' }, { title: 'Confirm' }],
}
const APPS = args.apps          // e.g. ['Browser Interface', 'Kiosk', 'Mobile', ...]
const TARGET = args.target      // the module/service the change lives in

const HIT = {
  type: 'object',
  properties: {
    consumes: { type: 'boolean' },
    how: { type: 'string' },
    evidence: { type: 'array', items: { type: 'string' } },
    risk: { type: 'string', enum: ['direct', 'indirect', 'none'] },
  },
  required: ['consumes', 'how', 'evidence', 'risk'],
}

const results = await pipeline(
  APPS,
  app => agent(
    `Does the ${app} app consume ${TARGET}? Search the repo. ` +
    `Cite files. Answer "none" unless you found actual evidence.`,
    { label: `sweep:${app}`, phase: 'Sweep', schema: HIT }
  ),
  (hit, app) => hit && hit.consumes
    ? agent(
        `Refute this: ${app} consumes ${TARGET} via ${hit.how}. ` +
        `Check the cited files. Default to refuted if the evidence does not hold.`,
        { label: `confirm:${app}`, phase: 'Confirm', schema: HIT }
      ).then(v => ({ app, ...hit, confirmed: v && v.consumes }))
    : { app, ...hit, confirmed: false }
)

return results.filter(Boolean).filter(r => r.confirmed)
```

The second stage matters: an unverified "this app might be affected" padding
the scope wastes a tester's week, and the whole point of the sweep is to be
trusted. Each app flows straight from sweep to confirm without waiting on the
others — no barrier, because nothing here needs cross-app context.
