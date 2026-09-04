---
name: 9-asana-final-comment
description: Post the final QA sign-off or issue-closure comment on an Asana ticket in the house format (testing environment, verification result, C.C. list). Use when a testing round is finished or a retested issue needs closing out, or on /9-asana-final-comment with a ticket ID.
---

# Asana final QA comment

Posts the closing QA comment on an Asana task, matching the house templates
used on this workspace (workspace gid `36351424181263`). The user will
normally give you **only the ticket ID** (a numeric task gid, or a full task
URL — extract the gid from it). Everything else in this skill is about
picking the right shape, filling it correctly, and asking only for what
can't be derived.

## Two shapes — pick one before drafting

There is no single house template. Two distinct comment shapes are in use,
and using the wrong one produces a comment that reads nothing like its
neighbours:

| | **A — Round sign-off** | **B — Single-issue closure** |
|---|---|---|
| Posted on | a feature/dev ticket QA just finished testing | one Bug/Observation subtask that was fixed and retested |
| Opens with | "We have completed testing this issue and found the following issue(s):" | `✅ **<Bug\|Observation> NN has been resolved.** After the latest deployment:` |
| Body | bullet list of linked sub-bug tasks, then fix status | bullets stating what was verified as fixed |
| Ping | yes — @-mention whoever confirms the fix | no |
| Build link | usually yes | no |
| Ends with | `C.C.` mentions | closing bullet ("marking this as complete and closing it") + `C.C:` mentions |

Reference comments (read for shape, never reuse verbatim):

- **A** — `https://app.asana.com/1/36351424181263/task/1215854267100030/comment/1216257529326741`
- **B** — `https://app.asana.com/1/36351424181263/task/1216068650562484/comment/1216257529326738`
  (Bug 26); a second real one at
  `https://app.asana.com/1/36351424181263/task/1216781591347180/comment/1216908288956159`
  (Observation 08).

**How to choose:** if the target task's name matches
`[Component] Bug|Observation|Improvement NN: ...` and it sits as a subtask
under a bug-tracking parent (e.g. "Bug Reporting", "EnosisQA: Bug &
Observation Reporting"), it's **B**. If it's a feature/dev/CR ticket that QA
tested as a whole, it's **A**. When genuinely ambiguous, ask — but state
which one you think it is rather than asking from scratch.

**If the user points you at a specific existing comment** ("follow this
comment", plus a comment URL): fetch that task's stories, find that comment's
`html_text`, and match its shape *exactly* — including the parts of the other
template it omits. Don't carry over a line from the generic template (a build
link, a ping) just because you have the information for it. Adding an extra
line to a shape the user explicitly pointed at is a correction waiting to
happen.

**Two different things a comment URL can mean.** Decide which before drafting:

- *"follow / match this comment"* — the comment is a **shape** model.
  Mirror its structure exactly, as above.
- *"draft the final comment **based on** this comment"* — the comment is
  a **content** source, not a shape. It's usually a dev's own write-up of what
  they changed; the job is to turn each thing it claims into a verification
  bullet, and to pick the template from the ticket as normal. Verified on
  2026-08-25: a dev's reply enumerating six CyberLink license-release
  scenarios became the six verified bullets of a Template A sign-off.

When it's a content source, say so in your draft notes — those bullets are
*your inference of what got retested*, and only the tester can confirm each
one actually was.
## The templates and the markup

| File | Read it at |
| --- | --- |
| `reference/templates.md` | Before drafting - Template A, Template B, and how to phrase the verdict |
| `reference/html-and-people.md` | While drafting - which HTML tags the API accepts, and how to build a mention that resolves |

Two things worth carrying without a lookup:

- **Mentions use the resource gid** from `assignee` / `followers` /
  `created_by`, never the number in a `/0/profile/NNN` URL. Those differ for
  most people, and a mention built from the wrong one silently fails to resolve.
- **`<h2>`, `<hr/>` and `<table>` all work.** The "flat environment block is an
  API limitation" claim is false, and it was told to the user across eight
  posted comments before being caught. Never repeat it.

## Steps

1. **Resolve the ticket ID.** If given a URL, extract the task gid (the
   segment after `/task/`).

2. **Fetch context automatically** — don't ask the user for anything you can
   get from Asana:
   - `asana_get_task` with
     `opt_fields=name,notes,html_notes,permalink_url,assignee.name,followers.name,created_by.name,completed,memberships.section.name,parent.name,custom_fields.name,custom_fields.display_value`
     — `name` + `parent.name` decide the template shape; `html_notes` gives
     you the ticket's own Observed-Behavior wording to mirror in the
     verification bullets; `memberships.section.name` and `completed` tell
     you what still needs doing after posting.
   - `asana_get_stories_for_task` with
     `opt_fields=text,html_text,created_at,created_by.name,type,resource_subtype`
     — use this to find: who reported/requested the ticket, who fixed it
     (the "Fixed the issue" / PR comment), who's been collaborating, whether
     the task already moved into a QA/testing section, and any prior comment
     the user may be pointing at as the model.

3. **Ask the user only for what's genuinely session-specific** — i.e. things
   that live in the tester's head, not in Asana. Ask concisely, in one go,
   offering your inferred defaults as the options:
   - **The verdict**: is it actually fixed on retest, fixed-with-a-caveat, or
     still reproducible? Never assume this — it's the one claim in the
     comment that only the tester can make, and getting it wrong misreports
     QA results to the whole team.
   - Bug/Observation tasks found this round (IDs/links, or "none")
   - Testing environment: OS, Application(s) tested, Version, Connected
     Server (the build under test is often newer than the version recorded
     in the ticket body — ask, don't copy the ticket's). The user usually
     gives the version inline with the instruction ("close this fixed,
     12.1.50.2"): that phrasing is *complete* — verdict and version both
     — so don't ask a follow-up question. When the version they give
     contradicts the ticket description or a build link inside it, use
     theirs and flag the discrepancy in the draft notes; don't edit the
     description to match unless asked. On a multi-app ticket put each
     app's build on its own line in one Version cell
     (`Kiosk: 12.1.50.2` newline `Mustering: 12.1.50.5`).
   - Build download link, if template A and there is one
   - Who to ping for confirmation and who else to C.C. (suggest defaults
     from step 2 — reporter for the ping, collaborators/assignee for C.C. —
     and let the user confirm or override)

4. **Draft the comment** following the chosen template and the HTML guidance
   above, using real gids for every `<a data-asana-gid="...">` mention/link.

5. **Show the drafted comment to the user and get explicit confirmation**
   before posting — this is a comment visible to the whole team, not a local
   edit, so never post without approval. Render it readably (not as raw
   HTML), and call out any judgement calls you made — a deviation from the
   template, a person you left out, a wording choice — as a short note under
   the draft. Expect one or two revision rounds on the C.C. list; re-show the
   full draft each time rather than describing the diff.

   The user may queue several drafts before authorizing any of them ("keep
   this in your list, prepare another draft for this one ... when I say go,
   post both together"). Hold each approved draft verbatim and post the whole
   batch on the single go-ahead — **"post" is that go-ahead**; don't
   re-ask per ticket.

6. **Post it** with `asana_create_task_story(task_id=<gid>, html_text=<draft>)`.
   Report back the story link (`https://app.asana.com/1/36351424181263/task/<task_gid>/comment/<story_gid>`)
   and confirm the mentions resolved (the returned `text` shows expanded
   profile URLs when they did).

7. **Follow through on what the comment promised.** Template B's closing
   bullet says the ticket is being marked complete and closed — that doesn't
   happen by itself:
   - Marking complete: `asana_update_task(task_id, completed=true)`.
   - Moving it to the **Closed** section: **not possible with this toolset**
     — `asana_update_task` can't change a task's section and there's no
     add-to-section tool. Tell the user to do that one in the Asana UI.

   Treat both as separate actions needing their own go-ahead: "post it" is
   permission to comment, not to close the ticket. Ask, and if the answer
   doesn't come, say plainly in your report that the task is still open and
   in which section — then **say it once and let it go**. Re-raising the
   same unanswered completion prompt after every subsequent post reads as
   nagging; carry the open items forward as one short line instead.

   Completion state also moves without you: tickets closed earlier in a
   session may already come back `completed: true` on a later fetch because
   someone marked them in the UI. Re-read before claiming a ticket is still
   open.
