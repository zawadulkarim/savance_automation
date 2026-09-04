---
name: 8-asana-bug-report
description: File a new Bug/Observation/Improvement ticket as an Asana subtask in the house QA template (testing environment, steps to reproduce, observed/expected behavior), correctly typed and numbered. Use when a finding from testing needs logging as a ticket, or on /8-asana-bug-report.
---

# Asana bug report

Creates a new Bug / Observation / Improvement subtask under a QA bug-tracking
parent task (e.g. "EnosisQA: Bug & Observation Reporting"), matching the house
template used on this workspace (workspace gid `36351424181263`). The user
will normally give you the parent tracking task (ID/URL) plus a rough
description of what they found — everything else in this skill is about
turning that into a correctly formatted, correctly numbered ticket and asking
only for what can't be derived automatically.

Reference example this template is based on (32 real subtasks spanning Bug,
Observation and Improvement types — read for your own understanding, not to
be reused verbatim):
`https://app.asana.com/1/36351424181263/project/1215927039992328/task/1216572205209251`.

**Current default parent (as of 2026-08-19):** unless the user names a different
one, file new subtasks under **"Bug & Observation Reporting"**, gid
`1216945480017099`
(`https://app.asana.com/1/36351424181263/task/1216945480017099`) — a subtask of
"QA Execution" (`1216945453915141`) in project **"Savance AI Reporting and Query
Assistant"** (`1216417328416226`, "To Do" section `1216417328416227`). This
replaces the Q3 tracker above as the live destination; the Q3 tracker stays only
as the formatting reference.

## Step 1 — Resolve context, don't ask for what you can fetch

1. Resolve the parent tracking task gid (from an ID or URL the user gives
   you, or from conversation context if already established; if none is given,
   use the current default parent listed above).
   **Sanity-check that parent before filing under it.** A real tracking
   parent comes back with existing subtasks and a project; if
   `asana_get_task` returns an empty `subtasks` array *and* `projects: []`,
   you are almost certainly on the wrong task — these QA parents sit among
   similarly-named siblings (observed 2026-08-25: the user pasted "Bugfix
   Testing" `1216945480017101`, an empty sibling of the real "Bug &
   Observation Reporting" `1216945480017099`). Say so, name the parent you
   believe was intended, and draft against that — don't file into an
   orphan, since a subtask created with no project never lands on a board.
2. `asana_get_task` on the parent with
   `opt_fields=name,subtasks.name,subtasks.completed,projects.name` to see
   the existing subtasks — this tells you the next number for each type (see
   Step 2) and the component-tag vocabulary already in use (e.g. `[Kiosk]`,
   `[SW Web]`, `[Mobile Check-in]`, `[Web]`).
3. Pull one recent subtask in full
   (`opt_fields=custom_fields.name,custom_fields.enum_options.name,assignee.name,followers.name,memberships.section.name`)
   to confirm the current custom-field gids and default section — these can
   drift per project, so re-derive them rather than trusting stale values.
   As of the reference example above, the project `Savance Q3 Release Items`
   (gid `1215927039992328`) uses:
   - **Issue Priority** (enum, gid `1122234914439647`): Critical
     (`1122234914439648`) / High (`1122239529818550`) / Medium
     (`1122234914439649`) / Low (`1122234914439650`)
   - **TKT** (text, gid `1206897910641200`) — an external ticket-tracker
     reference like `TKT-3442`; leave unset if the user has no such reference.
     In `Savance AI Reporting and Query Assistant` this field is
     `is_value_read_only: true` and an Asana rule **auto-populates it on
     creation** (observed twice: fresh subtasks came
     back stamped `TKT-3657` and, on 2026-08-25, `TKT-3691`, neither sent) — don't try to set it, and don't tell the user it's
     empty without reading the created task back.
   - New tickets go in the **To Do** section of that project (gid
     `1215927039992329`) — this is the intake column for freshly filed
     tickets, not "Ready for QA" (that's a later workflow stage). Re-derive
     the section gid via `asana_get_project_sections` for other projects
     rather than assuming it matches.

## Step 2 — Pick the type, number, and title

Every ticket is one of three types, each with its own independent counter
that increments across all components under the same parent (not per
component):

| Type | Counter example | Closing section is called |
|---|---|---|
| **Bug** | a real defect — something broken | "Expected Behavior" |
| **Observation** | a quirk/inconsistency worth flagging, not clearly wrong | "Suggested Behavior" |
| **Improvement** | a suggested enhancement, not a defect | "Suggested Behavior" |

Title format:

```
[Component] Bug NN: Short description of the defect
[Component] Observation NN: Short description of what was noticed
[Component][Existing] Bug NN: ...
Bug NN: Short description of the defect          <- single-app parent, no tag
```

- `NN` is zero-padded two digits, one past the highest existing number of
  that same type under the parent (from Step 1).
- `[Component]` is a bracketed tag for the app/area affected — reuse an
  existing tag from Step 1 if this bug is in the same area (`[Kiosk]`,
  `[SW Web]`, `[Web]`, `[Mobile Check-in]`, ...); coin a short new one only if
  none fits.
- **The tag is not universal — copy whatever the parent's own subtasks do.**
  Where a parent covers a single application there is no area to
  disambiguate and the house titles carry no tag at all: under "Bug &
  Observation Reporting" (`1216945480017099`, *Savance AI Reporting and Query
  Assistant*) every subtask is a plain `Bug 04: ...` / `Improvement 02: ...`.
  Bracketing one there makes the new ticket the odd one out in the list. Read
  the sibling titles you already pulled in Step 1 and match their shape; use
  the `[Component]` form only when the siblings use it.
- Stack a second bracket tag when relevant: `[Existing]` marks a pre-existing
  bug not introduced by the current release/dev work (a regression the team
  should know isn't new); `[Surface Device]` or similar marks a
  device/hardware-specific finding.
- The title itself should name the defect/observation concretely (what's
  wrong), not the test action (what you did) — that belongs in the steps.
## Steps 3-4 - Fill the template and its markup

-> `reference/template-and-html.md` for the section-by-section template and the
accepted HTML.

Four rules that hold regardless of the section being written:

- **Every repro sequence starts at the front door.** Step 1 navigates to the
  test server, Step 2 logs in, naming the role or account type. Never open on
  the deep state - a standing house rule, even when it feels redundant.
- **Repro steps must work for someone else, from a clean environment.** Generic,
  freshly-creatable test data, not a record sitting in the tester's own account.
- **Observed Behavior is what the tester reported**, not what you infer probably
  also happens. Expected Behavior is grounded in the domain skills, the Stage 04
  acceptance criteria, or live app behaviour - an expectation you cannot source
  is a question for the user, not a confident bullet.
- **Mentions use the resource gid** from `assignee` / `followers` /
  `created_by`, never the number in a `/0/profile/NNN` URL.

## Step 5 — Create and place the ticket

1. Draft the full ticket (title + `html_notes`) and **show it to the user
   for confirmation** before creating anything — this becomes a real,
   visible ticket that others will see and act on, not a local draft.
2. `asana_create_task` with `parent=<tracking task gid>`, `project_id`, and
   `section_id` set to **To Do** (Step 1) so the ticket lands in the intake
   column directly — pass all three together at creation time, since there
   is no tool available in this toolset to move an *existing* task's section
   afterward. Also set the drafted `name` and `html_notes`, `custom_fields`
   (Issue Priority, and TKT if given), `assignee` if the user named one, and
   `followers` for anyone to CC.
3. Report back the created task's link and gid.
