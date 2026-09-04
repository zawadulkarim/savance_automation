---
name: savance-workplace
description: Domain knowledge for the Savance Workplace app (test.savanceworkplace.com) — a workplace / visitor / employee in-out status board product, formerly branded EIOBoard. Covers login, the full navigation map, module-by-module purpose and fields, admin/security structure, and a domain glossary. Use when testing, QA'ing, filing bugs against, or otherwise working with Savance Workplace / EIOBoard / test.savanceworkplace.com.
---

# Savance Workplace domain knowledge

Reference doc built from a full read-only exploration of the **test** instance at
`https://test.savanceworkplace.com/` on 2026-07-24 (test org "SM Org", DB/Web version
12.1.39). Use this to orient quickly instead of re-discovering navigation/terminology
from scratch. See [[8-asana-bug-report]] for how findings from this app get filed as
tickets.

This doc covers the **Browser Interface only**. For the other 10 apps in the
product family (Kiosk, Desktop, Mobile, Mobile Web, Server, Emergency
Mustering, both Outlook Add-ins, and the internal Admin App) and how they all
depend on each other, see [[savance-workplace-suite]].

**Stay read-only by default.** This doc was produced without creating, editing,
deleting, saving, sending, or submitting anything. Unless the user is explicitly
executing a test case that requires a mutating action (and has said so), prefer
viewing/navigating/filtering over clicking Save/Submit/Create/Delete/Send/Invite/
Approve, and cancel out of confirmation dialogs rather than confirming them.

## Login

- URL: `https://test.savanceworkplace.com/Login.aspx?ReturnUrl=%2f`
- Test credentials: username `zawad.smorg`, password `Enosis123`
- Fields: **User Name**, **Password**, **Remember me**, **Log In** button
- Also present: **Forgot Password?** link, and a **Sign in with Microsoft** SSO
  button (backed by an "Identity Provider" integration under Admin → Integrations)
- On success redirects to `Default.aspx` (page title "Savance Workplace")

## What the product is

Savance Workplace is the modern rebrand of **EIOBoard** ("Electronic In/Out Board")
— the legacy name still surfaces everywhere: login page title, `EB`-prefixed
security groups (e.g. "EB Admin"), licensing URLs pointing at `eioboard.com`. Core
concept: every person (staff or visitor) has a live **Status** (In/Out/Lunch/
Vacation/etc.) shown on a shared board, with layers on top for visitor management,
time & attendance, messaging, calendar, physical access control, and reporting.

## Navigation map (top bar, in order)

1. **Home** (`Default.aspx`) — the Status Board
2. **Status** — inline flyout to change your own status (not a page)
3. **Notes** (`MyNotes.aspx`) — personal message inbox
4. **Reports** (`Reports.aspx`)
5. **Timesheet** (`MyTime.aspx`)
6. **Phone List** — auto-built system report/directory
7. **Calendar** (`Calendar.aspx`)
8. **Send Message** (`SendMessage.aspx`)
9. **Admin** (`Administration/Administration.aspx`) — only visible to admin accounts
10. **More Options** flyout: Help Desk, Visitor Sign In, Watchlist, Clear Roll Call

Header chrome (top-right): **My Info & Settings** | **Sign Out** | **Online Help**.
Nav icon visibility is independently toggleable per user (My Settings → Toolbar),
so the visible nav can legitimately differ between testers/accounts.
## Detail - load only what you need

| File | Contents |
| --- | --- |
| `reference/modules.md` | Purpose, fields and behaviour per module, including the whole Admin area |
| `reference/glossary-and-patterns.md` | Domain glossary, cross-module relationships, common UI patterns, notes for future testers |

Looking for one field or control rather than a module? Grep across them:

```bash
grep -rin "watchlist" .claude/skills/savance-workplace/reference/
grep -rin "status type" .claude/skills/savance-workplace/reference/
```

For the other ten applications and the cross-app dependency map, see
[[savance-workplace-suite]].

---

<!-- Domain knowledge, Browser Interface (live-verified). Companion:
     savance-workplace-suite (the other 10 apps + dependency map). -->
