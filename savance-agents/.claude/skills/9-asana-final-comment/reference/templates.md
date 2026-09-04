# The two comment templates

Referenced from `SKILL.md`. Pick the shape **before** drafting - they differ in
what they omit as much as in what they contain.

## Contents
- Template A - round sign-off on a feature/CR ticket
- Template A lines the user will often delete
- Template B - single-issue closure on a Bug/Observation subtask
- Phrasing the verdict

## Template A — round sign-off

1. **Heading** — "⚙️Testing Environment" (real `<h2>` — see the HTML section)
2. **Environment block** — a real `<table>`; four base fields: OS Info.,
   Application, Version, Connected Server. Add a **Device** field whenever the
   ticket is device-specific (`[Surface Device]`, a phone/tablet viewport, a
   Kiosk unit) — a closure on a device-specific bug that doesn't name the
   device it was retested on doesn't actually assert anything. Add **Browser**
   as its own field when the browser or emulated viewport is the substance of
   the bug rather than incidental.
3. **Separator line** — real `<hr/>`
4. **Findings** — "We have completed testing this issue and found the
   following issue(s):" + a bullet list of linked bug/observation tasks.
   If nothing was found, say so plainly instead (no bullet list) — do not
   invent placeholder issues.
5. **Fix status** — one line confirming the found issues are fixed (or that
   there was nothing to fix).
6. **Optional anomaly note** — only if the tester mentions something observed
   but not reliably reproducible; bold the follow-up commitment sentence.
7. **Ping the requester/reporter** — @-mention the person who should confirm
   the fix, asking them to test and give feedback.
8. **Build location** — "Please download the build from this page: <link>"
   (skip this line if there's no build link this round). If the link the user
   gives is a direct installer/`.exe` rather than a page, write "from this
   link" instead of "from this page".
9. **C.C.** — @-mentions of everyone else who should be looped in.

### Template A lines the user will often delete

The **ping** (step 7) and the **build location** (step 8) get cut more often
than not. Once they're gone the comment ends on the C.C. line and reads much
closer to Template B — that's fine. Don't reinstate either one on a later
revision round just because the template lists them.

**Closing line for a Template A ticket that needs no further work.** Template
B's "As this issue is resolved..." doesn't fit a dev/enhancement ticket where
nothing was broken. The house wording for that case is:

> All the <...> scenarios are working as expected. As this ticket does not
> have any action item, we are marking this as complete and closing it.

Use it in place of a fix-status line that promises separate tracking. It
carries the same follow-through obligation as Template B's closing bullet —
see Steps, step 7.

## Template B — single-issue closure

1. **Heading** — "⚙️Testing Environment" (real `<h2>`)
2. **Environment block** — same fields and same Device/Browser rules as A
3. **Separator line** — real `<hr/>`
4. **Verdict line** — `✅ ` + bold
   `<Bug|Observation> NN has been resolved.` + ` After the latest deployment:`
   Use the same type word and number as the ticket title (`Observation 08`,
   not "the observation"). Drop the `[Component]` tag here.
5. **Verification bullets** — one per behaviour actually re-verified, phrased
   as the fixed state ("The PiP camera window no longer hovers over other
   applications"), mirroring the ticket's own Observed-Behavior bullets.
6. **Closing bullet** — last item in the same list: "As this issue is
   resolved, we are marking this as complete and closing it."
7. **C.C:** — mentions, comma-separated.

No ping and no build link in this shape unless the user asks for them.

## Phrasing the verdict

The verdict is the one claim in the comment that only the tester can make.
Three rules learned by correction:

- **A qualified pass stays qualified.** When the dev's own comment explains a
  residual limitation, don't flatten it into a clean pass. Real example
  (Bug 32, Kiosk PiP): the fix cut Status Board render time but the PiP still
  pauses while the UI thread is blocked, so the bullet read "is still observed
  to be non-responsive while the Status Board is loading, but the
  non-responsive duration is noticeably reduced ... and resumes on its own
  once rendering completes" — not "remains responsive". If the ticket
  itself carried a caveat ("may be caused by test-server slowness"), state in
  your draft notes that you're asserting it fixed, and offer the hedge.
- **Never present the dev's measurements as QA's.** Numbers from the dev's
  comment — render times, memory figures, percentages — are *their*
  benchmark, not your retest result. Leave them out by default; offer to cite
  them attributed if the user wants them.
- **An Improvement is not an issue.** When the round logged an Improvement
  rather than a defect, drop the template's "found the following issue(s)"
  wording — write "Additionally, we have logged the following
  improvement:" and keep issue-framing out of the entire comment. Same for
  Observations when the user frames them that way.

**Folding bullets.** Mirror the ticket's Observed-Behavior bullets, but fold a
symptom into the bullet for its cause rather than giving it a line of its own
(e.g. "PiP still enabled in Admin while invisible" belongs inside the "no
longer disappears" bullet). Name the folds in your draft notes.
