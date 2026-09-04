# Module details - Browser Interface

Referenced from `SKILL.md`. Purpose, fields and behaviour per module, all
live-verified against test.savanceworkplace.com.

## Contents
- Home / Status Board
- Notes, Reports, Timesheet, Calendar, Send Message
- Watchlist, Visitor Sign In, Self Check-in
- Contact Details ("Administer User")
- My Info & Settings
- Admin (Customers, Fields, Global Settings, Statuses, Security, Users)

## Module details

### Home / Status Board
Live grid of everyone's status. Columns (configurable via "Choose Columns"): My
(select), Full Name, Watchlist Comment, Ext, Status, Returning, Time, Comment,
Pic, Email. Filters: User Type (All/Staff/Visitor), Primary Location, Status
Location, Status Type (In/Out/Unavailable), Status, Name, Ext, "Within Selected
Group". View toggles: Standard/Mini, All/My Friends. Known watchlist-flagged test
fixture: **Timothy Dukes** shows a Sex Offender / CheckrTrust match comment —
useful for watchlist-related test cases.

### Notes (`MyNotes.aspx`)
Personal inbox of notes left for/about you: Date Added, Left By (→
`EmployeeDetail.aspx?ContactSys=`), Reply, Message, Email, SMS, Date Read.

### Reports (`Reports.aspx`)
27 canned reports across 8 categories: Communications Log, Customers, General,
Patients, Roll Call, Time and Attendance, Usage, Visitors. Report viewer
(`Reports/ReportTableTemplate.aspx`) has Filters (Organization, Status Location,
Customer, Group, date range, custom And/Or condition builder), Column Chooser,
Export To (Pdf/Excel), drag-to-group-by-column, and a "Create New Report" /
"Use Classic Reports" toggle implying a custom report builder.

### Timesheet (`MyTime.aspx`)
Name selector (all staff, visible to admins), date range with quick-range
buttons, per-day table with a **Review** link → `ShowStatusHistory.aspx` (Status
History Review: Time Stamp, Status, Paid Y/N, Return, Comment). Hour totals are
driven by each Status's **Paid/Unpaid** flag (set in Admin → Statuses).

### Calendar (`Calendar.aspx`)
"{User} Personal Calendar" plus a **Manage Calendars** button (multiple/shared
calendars). Standard Day/Work Week/Week/Month/Timeline/Agenda views.

### Send Message (`SendMessage.aspx`)
Broadcast by Contact / Group / Location / Status Location. Delivery channels:
SMS, Email, Note. 2000-char message cap. Uses **Quick Pick Messages** and
**Profile** (recipient-selection template) — configured under Admin.

### Watchlist (`Watchlist.aspx`, iframe)
Security-screening list: Name, Company, Phone, DOB, Gov ID, Comment. Populated
by three background-check integrations (see below); this is what produces the
"Watchlist Comment" seen on the Status Board.

### Visitor Sign In (`VisitorSignIn.aspx`, iframe kiosk flow)
"Find or Add Visitor": First/Last Name, DOB, "Pre-Register Visitor?" toggle,
Scan Barcode. Runs the visitor through Question Manager's questionnaire and a
Watchlist screening before completing sign-in.

### Self Check-in (Mobile Check-in, visitor-facing QR flow)
The visitor-facing counterpart to Admin → **Mobile Check-in**: a QR/link-based
flow a visitor completes on their own phone/browser, no kiosk needed. Runs the
same Question Manager questionnaire as kiosk Visitor Sign In (including
**Checkbox**-type questions configured via "Manage Options"), then ends on a
**Visitor Confirmation** screen: recap of entered Name and every answered
custom field (label left, value right), **Picture** and **Signature** capture
steps, and **Cancel** / **Back** / **Confirm** buttons. On narrow mobile
viewports (e.g. Pixel 6 Pro, iPhone 15 Pro Max) the answer column for a
multi-select **Checkbox** question can render cropped instead of wrapping —
see filed Mobile Check-in Checkbox bugs for detail.

### Contact Details (a.k.a. "Administer User" detail view)
Read view of a single Contact's full field set — reached from a Contact/
Visitor record (e.g. after Visitor Sign In, or via Admin → Users). Renders as
a two-column label/value grid, grouped under bold category headers matching
the org's **Fields** configuration (e.g. "Home Info", custom test categories),
covering every custom field type: text, file-upload ("No Files Uploaded" when
empty), date/time, and **Checkbox** (multi-select values rendered as a
comma-separated list in the value cell). With many options selected, the
Checkbox value list is long enough that a display bug reproduces here too:
the row/column can extend rather than wrap, cutting off later values.
Distinct from `Registration.aspx` (the *editable* staff/contact form reached
via Admin → Users → Edit) — Contact Details is the read-only recap grid.

### My Info & Settings (`UpdateInfo.aspx`, account menu)
4 tabs: **My Info** (contact record + your own Security Groups checklist), **My
Pictures**, **My Settings** (tooltips, colors, refresh interval, Update Status
button presets, Toolbar icon visibility, Log On/Off auto-status rules),
**Password** (`ChangePassword.aspx`, live policy checklist).

### Admin (`Administration/Administration.aspx`)
Four collapsible sections:

**General**
- **Customers** — lightweight CRM (Customer Lists + Contacts)
- **Fields** — custom fields across Contact/Status/Resources View/Work Item/Reports
  (confirms **Resources** and **Work Items** exist as modules, licensing-gated —
  not directly reachable in this test org)
- **Global Settings** — ~40 org-wide toggles (GPS auto-status, Future Status
  automation, calendar sync, watchlist enable/disable, pre-registration windows,
  date format, DST, etc.), Wait Time Settings, Company Logo, Credential Settings
  (password complexity, lockout, expiration)
- **Image Libraries**, **Mobile Check-in** (contactless/QR visitor registration),
  **Print Templates** (badge/label designer, opens JS modal)
- **Question Manager** (`QuestionManager.aspx`, iframe) — flowchart builder for
  the visitor-kiosk questionnaire with branching and a "Failed Message" screening
  gate
- **Registration & Licensing** — org name/number, expiration, max users, license
  key (obfuscated, Show/Apply), Add-ons matrix (SMS, Timecard, Calendar, Pictures,
  Chat, Resource Management, Exchange Sync, SDK, Mobile, Send Text, My Customers,
  TAPI)
- **Statuses** (`ManageStatuses.aspx`) — master list backing every status
  dropdown app-wide: Status Name, Alias, **Paid/Unpaid**, In/Out/Unavailable
  classification. Built-ins (In/Out/Unavailable) are "Not Configurable" for delete
  — good edge-case test target.

**Integrations**
- **Auto Credential Management**, **Doors** (physical door registry), **Hardware
  Integrations**
- **User & Access Control Integrations** — marketplace of ~25 physical
  access-control/identity-provider connectors (3xLogic, AMAG, Avigilon, Brivo,
  Genetec, Honeywell, Keri, Paxton, S2, Tyco, Microsoft Entra/Azure AD, etc.),
  filterable by category
- **Watchlist Integrations** — Savance BG Check, Checkr Trust, MK Denial (all
  Active in this test org)

**Users, Groups, & Security**
- **Company User Settings** (`UserSettings.aspx`) — org-wide default preferences
  mirroring My Settings, with **Save & Deploy** / **Deploy All Defaults** /
  **Deploy All My Settings** (bulk-propagate idiom, mutating — don't click)
- **Filters** — named, reusable data-scoping rules attachable elsewhere
- **Groups & Locations** (`ManageGroups.aspx`) — org hierarchy (Groups) and
  physical sites (Locations); empty in this test org
- **Security** (`Security.aspx`) — full permission catalog: Administrator, Admin,
  Master Admin, Users, Group Admin, User Manager, Timecard, Customers, GPS
  History, Reports, Work Items, Chat and Mass Messaging, Visitors (incl.
  Add/Edit/Bypass/Remove Watchlist, Sign In/Out Visitors), Resources, Badge and
  Label, API Permissions — richest source of exact domain terminology in the app
- **Users** (`ManageUsers.aspx`) — staff directory admin: Add User, Import Users,
  grid with Edit/Unlock/Disable/Delete. Edit opens `Registration.aspx?
  ContactSys=` (same form as My Info, plus per-user Security Groups/Groups/
  Primary Locations). ⚠️ **Note:** this form shows other users' passwords in
  plaintext — a security-sensitive UI behavior worth keeping in mind for test
  planning.

**Messaging & Alerts**
- **Group Move Alerts**, **Marquee** (scrolling ticker: text, scroll, font,
  color, rate), **Message Templates** (iframe; merge tokens like `[QRCode]`,
  `[QRLink]`, `[DownloadWalletPass-(TemplateId)]`), **Notes** (admin config for
  the Notes feature — distinct from personal `MyNotes.aspx`, don't conflate),
  **Quick Pick Messages**, **Wallet Pass** (iframe; Apple/Google Wallet-style
  visitor pass designer)
