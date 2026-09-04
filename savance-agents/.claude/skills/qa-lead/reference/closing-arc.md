# The closing arc — Stages 07, 08 and 09

Referenced from `SKILL.md` Step 12. Read this when the user asks to go past test
case design. Most runs stop at Gate E, so most runs never need it.

## Contents
- Offering the remainder, once, without starting it
- Stage 07: what it automates and what stays manual
- Why its reds are not all failures
- Stages 08 and 09, the only stages that write to Asana


> That closes test case design. From here I can automate the test cases as a
> Playwright suite (`7-testing-agent`), then file the findings
> (`8-bug-reporting`) and post the closing comment (`9-qa-signoff`).
> Say the word.

- **Execution** is either the tester's, by hand from `test-cases.xlsx`, or
  **`7-testing-agent`** — which turns the **approved** `test-cases.md` into a
  Playwright suite, runs it, and returns `6 - Test Review.md`: the cases a
  human must sign off. It checks the `Review Status` stamp before it writes a
  spec, so a run parked at Gate E cannot be automated by accident. You do not
  start it unless they ask.
  - Cases marked `Automation Candidate: No` at Stage 05 stay manual. Carry that
    split when you present: "N automated, M for the tester by hand" — not a
    single suite count that quietly drops them.
  - Its reds are **not** all failures to clear. A red left standing because the
    *application* is wrong is the stage working correctly, and those rows are
    exactly what feeds `8-bug-reporting`. When you present its result, carry
    that distinction through rather than reporting "N failures".
  - **Gate F** is a human reading `6 - Test Review.md`, not a green run.
- **`8-bug-reporting`** files each finding as a correctly numbered subtask, on
  approval of each draft.
- **`9-qa-signoff`** posts the round sign-off, on approval of the draft.

The last two write to Asana, so both need an explicit yes on the exact text.
