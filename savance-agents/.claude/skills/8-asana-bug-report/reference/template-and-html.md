# The bug-report template and its HTML

Referenced from `SKILL.md` Steps 3-4. The house template section by section, and
which tags `html_notes` actually accepts (probed, not assumed).

## Contents
- Step 3 - filling the template: testing environment, steps to reproduce,
  observed and expected behavior
- Step 4 - HTML in `html_notes`: what works, what is silently dropped, and how
  mentions must be built

## Step 3 — Fill the template

Ask the user only for what's genuinely session-specific — the stuff in the
tester's head, not derivable from Asana:

- Testing environment: OS, Browser or Application (+ version), Test/Connected
  Server URL, build Version(s) (e.g. `DB: 12.1.37`, `Web: 12.1.37`)
- Steps to reproduce (numbered, concrete — account/role used, exact
  navigation, exact inputs). Write these generically/reproducibly, not
  tied to the tester's own named test data: say "create a new Question
  Profile with a Checkbox-type question," not "select the '{tester's own
  profile name}' Question Profile" — anyone on the team should be able to
  follow the steps from a clean environment. Only name a specific
  pre-existing record/config when the bug genuinely depends on it already
  existing (e.g. a particular Watchlist integration entry) and can't be
  freshly created as part of the repro.
- Observed behavior (what actually happens)
- Expected/Suggested behavior (what should happen instead)
- Attachment (screenshot/recording link — Google Drive or an Asana asset
  link) if one exists
- Issue Priority, and whether there's a TKT reference number
- Anything else worth a trailing note: test data used, a pre-condition, a
  related/duplicate ticket to cross-link, a PR link if already fixed

Render these into the body in this order — every section is plain, no
markup beyond what's listed in Step 4:

1. `Testing Environment` — heading, then the fields as a **real `<table>`**
   (see Step 4): a header row of label cells, then one row of values. Standard
   columns are OS / Browser or Application / Test Server or Connected Server /
   Version. Add a **Device** column whenever the finding is device-specific
   (`[Surface Device]`, a phone/tablet viewport, a Kiosk unit) — a
   device-specific ticket that doesn't name the device is missing the one
   detail that makes it reproducible. Put multiple build numbers in a single
   Version cell on separate lines (`DB: 12.1.45` newline `Web: 12.1.45`),
   matching the house tickets. Plain `Label: value` lines are an acceptable
   fallback for short/simple tickets, but the table is the house format.
2. Separator — real `<hr/>` (see Step 4; don't hand-type a dashed line)
3. `Steps to reproduce:` — ordered list (`<ol><li>`)
4. `Observed Behavior` — what happens now, as a **bullet list** (`<ul><li>`),
   one point per fact — even a single-point observation still gets one `<li>`,
   not a paragraph
5. `Please see the below attachment:` + link, if one exists
6. `Expected Behavior` (Bug) or `Suggested Behavior` (Observation/
   Improvement) — what should happen, also as a **bullet list** (`<ul><li>`)
7. Optional trailing block, separated by another `<hr/>`: additional notes,
   test data, related-ticket links, PR link(s), or a `C.C:` line linking
   people to loop in

Section labels are conventionally prefixed with an emoji — ℹ️ steps, ⚠️
observed, ✅ expected/suggested — though plenty of real tickets just bold the
label with no emoji. Either is fine; keep it consistent within one ticket.
Bullet-vs-paragraph for Observed/Suggested/Expected is not optional, though —
always bullets, regardless of emoji style.

Every reference to a specific UI element — module/page name, menu item,
button, modal/dialog name, field, tab, dropdown, or field-type name (e.g.
"Checkbox", "Custom Options") — always gets wrapped in quotation marks *and*
bolded together, quote marks included:
`<strong>"Manage Options"</strong>`, `<strong>"Question Manager"</strong>`,
`<strong>"Save"</strong>`. Add the quotes even if the user's own phrasing
didn't include them — this is a standing formatting rule for every ticket,
not a reflow of pre-existing quotes. Applies wherever it occurs: steps,
observed/expected/suggested bullets, notes. Plain descriptive words that
don't name a specific UI element (e.g. "dropdown", "option", "the page")
stay unquoted and unbold.

## Step 4 — HTML in `html_notes`

`html_notes` requires well-formed XML with a single root `<body>`. The tool
schema lists `body`, `strong`, `em`, `u`, `s`, `code`, `ol`, `ul`, `li`, `a`,
`blockquote`, `pre`, `h1`, `h2`, `hr`, `img` and says only `<a>` may carry
attributes.

**`<table>` also works, despite not being listed.** Verified by direct probe
against workspace `36351424181263` on 2026-07-30 (created a throwaway task
with a table in `html_notes`, read `html_notes` back, then deleted the task):

- `<table>` / `<tr>` / `<td>` are **accepted** by both `asana_create_task` and
  `asana_update_task`, so an existing ticket's description can be retrofitted
  with a table too.
- Asana **auto-injects `width="120" data-cell-widths="120"`** onto every
  `<td>`, which is exactly what the web editor does — which is why older
  hand-authored tickets carry those same attributes. **So send bare
  `<td>OS</td>` cells with no attributes of your own** and let Asana stamp
  them (reconfirmed 2026-08-25); this is the one spot where the schema's
  "only `<a>` may carry attributes" rule would otherwise trip you up if you
  copied an existing ticket's markup verbatim.
- **Custom widths are silently overridden.** Sending `width="141"` (the value
  the house tickets use for their wider Test Server column) comes back as
  `120`. You cannot control column widths through the API; don't bother
  setting them, and don't promise the user a match to a specific existing
  ticket's column proportions.
- No `<th>` — the house format uses a plain first `<tr>` of `<td>` label cells
  as the header row. Follow that.

If a tag ever does get rejected the 400 is harmless (nothing is created), so
probing is cheap. To probe safely: `asana_create_task(name=..., assignee="me")`
with no `project_id` lands a private task in My Tasks; read it back, then
`asana_delete_task`.

**Emoji must be literal characters, never HTML entities.** Verified on
2026-08-19: sending `&#8505;&#65039;` for ℹ️ comes back as `&amp;#8505;&amp;#65039;`
— Asana escapes the ampersand instead of decoding the entity, so the ticket
displays the raw `&#8505;` text to every reader. Put the actual ℹ️ / ⚠️ / ✅
characters in `html_notes`. (Recoverable after the fact with
`asana_update_task`, but read `html_notes` back to confirm.)

**Named entities are fine, though.** `&quot;`, `&amp;`, `&apos;` and `&lt;`
all decode normally on the way in (reconfirmed 2026-08-25 — `&apos;` came
back as a plain apostrophe). It is specifically *numeric* character
references that Asana double-escapes, so the rule is "literal emoji, named
entities as usual", not "no entities anywhere". You still need `&quot;`/
`&amp;` to keep `html_notes` well-formed XML.

Other markup rules:
- Task/person links → `<a data-asana-gid="GID"/>` (gid only; Asana expands
  it). Don't hand-build hrefs for objects you have access to.
  ⚠️ Use the **resource gid** from `assignee` / `followers` / `created_by` —
  *not* the number in the `/0/profile/NNN` URL that story `html_text` renders.
  Those differ for most users (e.g. Md Oshim is `1205168551136132` but his
  profile URL reads `1205168831751965`), and a mention built from the
  profile-URL number will not resolve.
  On a `C.C:` line the house convention is **Md Shofiur Rahman
  (`1209277490925824`) then Wasif Azmaeen (`1204185846850019`)** first, in that
  order, then anyone else; confirm the rest with the user.
- Attachment/external links (Drive, PR links) → normal `<a href="...">`.
- Bold section labels → `<strong>`; steps → `<ol><li>`; Observed Behavior and
  Expected/Suggested Behavior → `<ul><li>` (always — see Step 3); any other
  bullet list (e.g. multiple attachments) → `<ul><li>` too.
