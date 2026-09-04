# The JSON spec schema

Referenced from `SKILL.md` Step 4. **One spec, both artefacts** — this file is
the build source for the Markdown at Step 5 and the workbook at Step 8, and a
revision is an edit to it. That is what keeps the approved Markdown and the
delivered workbook in step. Write it to the scratchpad, not the ticket folder;
it is a build input, not a deliverable.

## Contents
- Top-level fields and layout modes
- Per-ticket / per-sheet structure
- Row fields, and the `id` override
- Gap and out-of-scope conventions

```json
{
  "project_name": "Savance Q3 Release Items",
  "application_name": "Savance Workplace Browser Interface, Kiosk",
  "prepared_by": "Enosis QA",
  "last_updated": "2026-08-03",
  "layout": "per_ticket",
  "start_index": 1,
  "tickets": [
    {
      "main_task": "Toyoda Gosei Feature Request (Enosis)",
      "sub_task": "Prevent visitors from checking in to hosts who are out",
      "assigned": "Wasif",
      "status": "In Progress",
      "url": "https://app.asana.com/1/36351424181263/project/.../task/...",
      "criteria": [
        {
          "module": "Question Manager\nVMSuite App",
          "description": "Ensure that a new setting is added to the \"Manage Host Profiles\" modal to manage unavailable hosts.",
          "rules": [
            "A setting named \"Prevent Out Status Type Host Selection\" must be introduced on the \"Manage Host Profiles\" modal.",
            "This setting must be located specifically under the \"Show Status\" checkbox."
          ],
          "expected": "A new setting appears directly beneath the \"Show Status\" checkbox in the \"Manage Host Profiles\" modal.",
          "notes": ""
        }
      ]
    }
  ]
}
```

Top level:

- `layout` — `per_ticket` (default): one `#N` sheet per entry plus a
  Dashboard index. `single_sheet`: one named sheet for the whole batch, no
  Dashboard; use `"sheets"` instead of `"tickets"` and set
  `"group_header": "Application"` + `"task_column": true`.
- `start_index` — first sheet number. **Ask** whether the sheets should
  continue an existing workbook's numbering (so they drop in cleanly) or
  start at 1; don't assume. It also drives the AC IDs (`start_index: 2` →
  `AC2001`).
- `task_column` / `status_column` — off by default. `status_column` adds a
  Passed/Failed/Untested dropdown with colour rules; leave it **off** for
  the `per_ticket` internal shape, since test status belongs in the
  checklist, not duplicated here.
- `group_header` — header text for the merged group column, default
  `"Module"`.
- `dashboard` — set `false` to suppress the Dashboard on a `per_ticket` run.
- `section_title` — appended to the row-6 bar (`Acceptance Criteria: X`);
  settable per sheet or globally.

Three more keys exist only for the Markdown renderer and are ignored by the
workbook builder. Use all three — the first two are what let a reviewer trust
the sheet in one pass instead of diffing it against the spec themselves:

- `spec_coverage` — `[{"item", "acs", "status", "notes"}]`, one row per
  in-scope item in the spec document, mapped to the criteria that cover it.
  **This is the "what is missing" answer** the human gate opens with, so an
  item you could not cover belongs here with its reason, not left out.
- `open_questions` — a list of strings: assumptions left standing, and
  anything still needing an answer, each naming the AC IDs it affects.
- `review_status` — the stamp described above. `DRAFT` while drafting,
  `AWAITING HUMAN REVIEW` once the self-review has passed, and
  `APPROVED — <reviewer>, <YYYY-MM-DD>` only once a human has said so.

Per criteria row: `module` (or `application` / `group`), `description`,
`rules` (list — a one-item list still renders as `1. …`, matching the
reference), `expected` (string for prose, list for a numbered outcome),
`task`, `status`, `notes`, and `id` to override the generated one. Embed
`\n` in a group name to stack it on two lines (`"Question Manager\nVMSuite
App"`), as the reference does.
