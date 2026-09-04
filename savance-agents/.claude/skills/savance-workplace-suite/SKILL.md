---
name: savance-workplace-suite
description: Domain knowledge for the full Savance Workplace (formerly EIOBoard) family — all 11 client/server applications (Browser Interface, Admin Web, Kiosk, Desktop, Mobile, Mobile Web, Server, Emergency Mustering, two Outlook Add-ins), how they depend on each other, and what each feature/module does. Use when scoping regression or sanity testing across apps, tracing a change's blast radius, or orienting on an unfamiliar module. Browser Interface detail: [[savance-workplace]].
---

# Savance Workplace — full application suite

## Source & how to use this doc

Built from a full read of `Savance Workplace_ Feature List_Scope of All Applications.xlsx`
(11 sheets: Dashboard + one per application). That workbook is the **source of
truth** for field-level detail — every row has `Domain?` / `Checklist?` /
`Automation?` flags and an `Other Impacted Areas` / `Notes` column. This skill
is a *synthesized map* of it: what each app is for, what each module actually
does, and how the apps connect — so you don't have to re-read 1,500+ rows to
get oriented. When you need exact field-by-field wording (for writing a
checklist item, say), go back to the spreadsheet.

The spreadsheet's own sub-rows are intentionally incomplete in places — many
say "Require Domain Knowledge" or have a Note asking a question (e.g. "Where
does it get stored in Registry?", "Need badge to test this flow"). Those are
follow-up items to resolve **later, per-item**, not something this doc
resolves. `reference/server-and-shared.md` carries the running list of what's
still unanswered, organized by app, so it's ready when that analysis happens.

This is a companion to [[savance-workplace]], which is a deep, live-verified
walkthrough of the Browser Interface only (test.savanceworkplace.com). Where
the two overlap, this doc stays brief and defers to that one; where this doc
covers ground the other doesn't (the other 10 apps, and the cross-app
dependency map), it's the primary reference.

## The 11 applications, at a glance

| # | Application | Platform | Sheet name | Who uses it |
|---|---|---|---|---|
| 1 | Browser Interface | Web App | `SwWebSwOutlookAddin - FullWindo` (shared) + `WebApp Browser Interface` (index) | Every end-customer employee/admin — the core product |
| 2 | VMSuite (Visitor Management) | Web App feature-set, not a standalone app | spread across Kiosk/Web/Outlook sheets | Front-desk/reception workflows, embedded in other apps |
| 3 | Desktop App | Desktop (Windows) | `SwDesktop` | Employees who prefer a native client over the browser |
| 4 | Emergency Mustering App | Desktop (Windows) | `SwEmergencyMustering` | Safety/emergency wardens doing roll call during an evacuation |
| 5 | Kiosk App | Desktop (Windows, kiosk mode) | `SwKiosk` | Front-desk/lobby physical terminal — staff sign-in + visitor sign-in |
| 6 | Outlook Add-In: Full Window App | MS Outlook add-in | `SwWebSwOutlookAddin - FullWindo` | Same as Browser Interface, launched from inside Outlook |
| 7 | Outlook Add-In: Visitor Management | MS Outlook add-in (task pane) | `SwOutlookAddin - VM` | Admins/Master Admins pre-registering meeting guests as visitors from a Calendar invite |
| 8/9 | iOS / Android App | Mobile App | `SwMobile` | Employees, native app w/ live location, chat, visitor mgmt |
| 10 | Mobile Browser Interface | Mobile Web App | `SwMobileWeb` | Employees on a phone browser, lighter-weight than the native app |
| 11 | Admin App | Web App | `SwAdminWeb` | **Savance's own internal staff**, not customers — see below |
| — | Savance Workplace Server | Windows Server app | `SwServer` | IT/on-prem admins configuring the DB, email, AD sync, chat, etc. |

⚠️ **Naming trap:** "Admin" means two very different things in this product:
- **Admin App (`SwAdminWeb`)** — an internal Savance tool (not sold to
  customers) for Savance staff to create/manage **customer organizations**:
  licensing, add-on toggles, billing/transactions, install history, support
  notes. This is the app in row 11 of the Dashboard.
- **Admin** (inside the Browser Interface) — the customer-facing
  configuration area (Customers, Fields, Global Settings, Statuses, Security,
  Users, etc.) that an org's own admin uses to configure *their* org. This is
  what [[savance-workplace]] documents in depth.
When this doc says "Admin App" it always means the internal `SwAdminWeb` tool
unless stated otherwise; the in-product area is always called "Admin (Browser
Interface)".

## Dependency map — what breaks what

From the Dashboard sheet's `Impacted Applications` column: if you change **X**,
also sanity-check **Y**.

- **Browser Interface** → *everything*. It's the hub; every other app either
  displays data it owns or is a thinner client of the same backend. Any
  regression here has the widest blast radius in the suite.
- **VMSuite (Visitor Management feature-set)** → Kiosk, Outlook Add-In (Full
  Window), Outlook Add-In (Visitor Management). VMSuite isn't a separate
  installable app — it's the visitor-management pages/APIs (Visitor Sign In,
  Watchlist, Question Manager, badge/label printing, credential activation)
  that those three surfaces all render against.
- **Desktop App** → Browser Interface, Outlook Add-In (Full Window).
- **Emergency Mustering App** → Browser Interface, Outlook Add-In (Full
  Window). (Mustering pulls its roster/status data live from the same server
  the Browser Interface uses.)
- **Kiosk App** → Browser Interface, Outlook Add-In (Full Window), VMSuite.
- **Outlook Add-In: Full Window App** → Browser Interface + VMSuite (the
  source sheet also lists the Full Window app as impacting itself, which
  looks like a copy/paste artifact in the spreadsheet rather than a real
  self-dependency — flagged here rather than silently resolved).
- **Outlook Add-In: Visitor Management** → Browser Interface, Outlook Add-In
  (Full Window).
- **iOS / Android App** → scope not yet mapped. The Dashboard explicitly notes
  the new mobile apps haven't been tested yet, so impact/effort is unknown.
- **Mobile Browser Interface** and **Admin App** → no other apps listed as
  impacted. Admin App in particular is a dead end in the graph — it's
  Savance-internal and doesn't touch customer-facing surfaces directly (it
  writes account/licensing records that the *other* apps then read).
- **Savance Workplace Server** doesn't appear in the Dashboard's ballpark
  list at all (only the 11 client-side apps got size estimates) — but
  everything on-premise depends on it being configured correctly (DB, email,
  AD sync), so treat server config changes as an implicit dependency of every
  on-prem app.

Rule of thumb when scoping a regression pass: **changes to Browser Interface
or VMSuite have the widest ripple; changes to Admin App (internal) or Mobile
Browser Interface are the most contained.**

## Per-app detail — load only what you need

The 11 apps' module-by-module detail lives in four reference files. Read the one
that covers the app in question; the others cost nothing until opened.

| File | Apps |
| --- | --- |
| `reference/web-apps.md` | 1 Browser Interface · 2 VMSuite · 10 Mobile Browser Interface · 11 Admin App (SwAdminWeb) |
| `reference/device-apps.md` | 3 Desktop · 4 Emergency Mustering · 5 Kiosk |
| `reference/mobile-and-outlook-apps.md` | 6 Outlook Full Window · 7 Outlook Visitor Management · 8/9 iOS / Android |
| `reference/server-and-shared.md` | Savance Workplace Server · cross-app shared building blocks · open items needing domain knowledge |

Looking for one module rather than one app? Grep across them:

```bash
grep -rin "watchlist" .claude/skills/savance-workplace-suite/reference/
grep -rin "badge print" .claude/skills/savance-workplace-suite/reference/
```

**For tracing a change's blast radius, the dependency map above is usually
enough** — open a per-app file only when you need what a module actually does.
`reference/server-and-shared.md` is the one to read when a change touches
something several apps consume, which is where cross-app regression risk comes
from.

## Using this skill

- For **Browser Interface** field-level detail, live URLs, and test
  credentials → [[savance-workplace]].
- For filing a bug found while exploring any of these apps → [[8-asana-bug-report]].
- When picking up one of the "Open items" above for real analysis, go back
  to the source workbook (`Savance Workplace_ Feature List_Scope of All
  Applications.xlsx`) and its per-row `Notes` column — those rows already
  have the specific question written down.
