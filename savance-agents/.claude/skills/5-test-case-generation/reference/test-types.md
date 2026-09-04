# Test types — when each one is warranted

Referenced from `SKILL.md` Step 4. Nine types; generate only the ones a rule
actually warrants.

## Contents
- The nine types, with generate/skip conditions
- Two judgement calls: regression, and permission cases

**Generate only the types the rule warrants.** Forcing all nine onto every
requirement is the classic way to produce a 300-case suite that tests less than
a 60-case one, because the padding hides the gaps.

| Type | Generate when | Skip when |
|---|---|---|
| **Functional / Positive** | Always — every acceptance rule gets at least one. | Never. |
| **Negative** | The rule accepts input, an action can be refused, or a required precondition can be absent. | Display-only behavior with no user input and no refusal path. |
| **Boundary / Validation** | The rule names a limit, length, count, range, format, or a required field. | No bounded or formatted value anywhere in the rule. |
| **UI / State** | The rule changes enabled/disabled, visible/hidden, checked state, default value, ordering, or placement. | The rule has no observable state change. |
| **Persistence** | The outcome must survive reload, re-login, or navigating away and back. | Transient UI that is not meant to persist. |
| **Error handling** | The rule names an error or warning message, or the operation can fail. | No failure path in scope. |
| **Integration** | The rule spans two apps or modules of the suite — a Kiosk setting read by the Browser Interface, a change that must reach the Outlook add-in. Check [[savance-workplace-suite]] for the blast radius. | The behavior lives on one surface. |
| **Permission / Authorization** | The rule mentions a role, security group, admin-only surface, or a right that can be withheld. | No role dimension. |
| **Regression** | The change touches a shared control, an existing setting, or a workflow that already worked. | A brand-new, isolated surface with nothing upstream of it. |

Two judgement calls worth stating out loud:

- **Regression is the type most often missed and most expensive to miss.** A new
  setting added to an existing modal means the modal's existing settings still
  need to save correctly. If the criteria touch anything that already worked,
  there is a regression case.
- **Permission cases need a second account.** If you do not have one, write the
  case, mark `Automation Candidate: No` and record the missing account as a
  Clarification rather than quietly dropping the type.
