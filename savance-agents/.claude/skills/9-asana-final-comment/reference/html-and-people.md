# HTML in html_text, and resolving people

Referenced from `SKILL.md`. Which tags the Asana API actually accepts (probed,
not assumed) and how to build a mention that resolves.

## Contents
- HTML tags in `html_text` - what works and what is silently dropped
- Resolving people: the resource gid vs the /0/profile/NNN number
- The person-gid table and the C.C. conventions

## HTML tags in `html_text`

**The `asana_create_task_story` tool schema is wrong about what it accepts.**
Its description says `html_text` allows only `body`, `strong`, `em`, `u`, `s`,
`code`, `ol`, `ul`, `li`, `a`, `blockquote`, `pre`, and that `<h1>`, `<h2>`,
`<hr/>` and `<img>` return a 400. That is **not** what the API does. Verified
by direct probe against workspace `36351424181263` on 2026-07-30 (each tag
posted as its own comment on a throwaway task, then the task deleted):

| Tag | Schema says | Actually |
|---|---|---|
| `<hr/>` | 400 | **accepted**, stored as `<hr />` |
| `<h2>` | 400 | **accepted**, stored as `<h2>` |
| `<h1>` | 400 | **accepted**, stored as `<h1>` |
| `<table>`/`<tr>`/`<td>` | not listed | **accepted**; Asana auto-injects `width="120" data-cell-widths="120"` onto each `<td>` |
| `<img>` | 400 | untested — probe it before relying on it |

So you **can** reproduce the house reference comments faithfully, including a
real `<h2>` heading and the 4-column `<table>` environment block. The table
normalization the API applies is the same as the web editor's, which is why
older hand-authored comments carry those same `data-cell-widths` attributes.

Use, in preference order:

- Heading → real `<h2>⚙️Testing Environment</h2>`. (`<strong>` on its own line
  is an acceptable fallback but no longer necessary.)
- Environment block → a real `<table>`: header row of field labels, one data
  row of values. Keep the house field labels including the trailing dot on
  `OS Info.`. Plain `Label: value` lines are still fine for tickets whose own
  description uses that flatter style — match the ticket you're commenting on.
- Separator → real `<hr/>`. Asana's plaintext renderer flattens it to
  `----------------------------------------`, which is why older comments look
  dashed in the `text` field; that dashed line was never a workaround, just the
  plaintext projection of a real rule. Don't hand-type dashes.
- Task/user links → `<a data-asana-gid="GID"/>`. Provide only the gid; Asana
  expands it to the correct mention or task-link automatically. Do not
  hand-build `href`s for objects you have access to.
- Bullet lists → `<ul><li>...</li></ul>`.
- Bold commitments/emphasis → `<strong>`.
- Emoji (✅, ⚙️) are plain text and pass through fine.

Compose the whole thing as a single well-formed `<body>...</body>` and pass
it via `html_text` (not `text`, so mentions/links render).

**If a tag does get rejected**, the 400 is harmless — nothing is posted — so
probing is cheap. To probe safely without a team-visible comment: create a
task with `asana_create_task(name=..., assignee="me")` and no `project_id`
(it lands privately in My Tasks), post the test comment, then
`asana_delete_task`. Stories cannot be deleted through this toolset, so
deleting the parent task is the only way to clean up a test comment.

Don't tell the user the flat environment block is an API limitation — that
claim was false and was repeated to them across eight posted comments before
being caught.

## Resolving people

Get gids from the task itself — `followers`, `assignee`, and story authors
(`created_by`) — not from a search. `asana_typeahead_search` with
`resource_type=user` currently errors out on this workspace
(`Cannot read properties of null`), so don't rely on it.

Recurring participants on Savance QA tickets, for cross-checking a name the
user gives you by first name only (re-derive from the task's own followers
where possible; treat these as a lookup aid, not gospel):

| Name | gid |
|---|---|
| A.S.M. Zawadul Karim (the tester/user) | `1212017242030561` |
| Md. Aminul Islam | `1205486317973744` |
| Wasif Azmaeen | `1204185846850019` |
| MD Ariful Alam | `1214051602681749` |
| Ferdousur Rahman | `1208395667350547` |
| Numan Ibn Mazid | `1211109145544363` |
| Md Shofiur Rahman | `1209277490925824` |
| Md Oshim | `1205168551136132` |
| Shamim Imtiaz | `1210021537132268` |
| MD Farhan Shahriar | `1210947769673215` |
| Mosfak Rimon | `1210947769673212` |

⚠️ The gid you need is the **resource gid** from `assignee` / `followers` /
`created_by` — *not* the number in the `/0/profile/NNN` URL that story
`html_text` renders. Those two differ for most users (e.g. Md Oshim is
`1205168551136132` but his profile URL reads `1205168831751965`). Mentions
built from the profile-URL number will not resolve.

C.C. rules learned the hard way:

- **Standing list: Md Shofiur Rahman then Wasif Azmaeen lead every C.C. line**,
  in that order, without being asked. The dev/assignee is usually wanted third.
  Ask about anyone beyond those three rather than assuming. Pre-populating the
  three and flagging it as an assumption in the draft notes is better than
  blocking on a question — the user reviews the draft before posting anyway.
- **"The assigned dev" can be ambiguous.** On a ticket that changed hands the
  current `assignee` and the dev who actually wrote the fix comment are
  different people. Include both — assignee then fix-comment author, after
  Shofiur and Wasif — and name the ambiguity in the draft notes so the user
  can trim.
- **Say which mentions will newly add someone.** Shofiur and Wasif are
  frequently *not* followers of the ticket being closed, so C.C.-ing them
  adds them as collaborators. State in the draft notes which names are new
  collaborators and which were already following.
- **The user dictates the order.** If they give an explicit list, keep that
  exact order; when they later say "add X and Y", append X and Y to the end
  rather than re-sorting into your own preferred order.
- The C.C. list is **not** the follower list. People already following the
  task get notified regardless, so the user may deliberately leave out the
  assignee/dev. Don't add anyone back in on your own initiative — offer, and
  name who's currently omitted so the choice is informed.
- @-mentioning someone who isn't a collaborator **adds them as one**. Flag
  that when it applies.
- Label is `C.C:` in template B and `C.C.` in template A — copy whichever
  shape you're following.
