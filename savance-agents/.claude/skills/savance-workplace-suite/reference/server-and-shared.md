# Server, shared building blocks, and open items

Referenced from `SKILL.md`. Read this when a change touches something more than
one app consumes — which is where cross-app regression risk comes from.

## Contents
- Savance Workplace Server (SwServer)
- Cross-app shared building blocks
- Open items — needs domain knowledge

## Savance Workplace Server (SwServer)

Not a Dashboard-listed "application" (no ballpark testing-scope numbers), but
the on-premise backbone every other on-prem app depends on. A Windows tray
app/service wrapping the SQL database and several integration engines.

- **Settings tabs**: Database (server/name/credentials + Test Connection —
  this is *the* EIOBoard database holding users, statuses, chat history,
  everything); Email (SMTP config, retry count, force-all-emails-to override
  for testing, Gmail API option); AD Sync (bind to Active Directory: server/
  port/credentials/domain, field-mapping for what AD attributes flow into
  Savance Workplace, filters for "real" users only, auto-add-new-users,
  Windows-credential login, AD-only login lockdown); Chat (enable/history/
  history-retention-days/server+port); plus TAPI, Exchange Sync, SMS, RF
  Code, and Motorola RFID Devices sections all marked "Require Domain
  Knowledge" in this sheet — treat those as needing a subject-matter pass
  before they can be tested meaningfully.
- **Top toolbar**: File (open install folder / Exit), Service (Start/Stop/
  Restart, or open the Windows Service Control Panel directly), Management
  (open Settings; Schedules and Manage User Pictures both flagged Require
  Domain Knowledge), Log (three distinct logs — **Active Log** for DB-level
  actions/errors, **Admin Log** for the Server UI itself, **Service Log** for
  the Windows service, only viewable while the service is running — know
  which one to check for which kind of problem), Help/About (version info +
  Copy System Info, handy for bug reports).
- **Emailing tab**: live queue view (Currently Processing / Unprocessed, with
  Check Queue to refresh) and a searchable Processed log (filter by date/
  type, double-click an email for delivery/error detail) — the place to
  confirm whether a "the email never arrived" bug is a delivery problem or a
  never-queued problem.
- **SQL Tasks / Active Directory Sync / Exchange Sync** tabs: scheduled-task
  CRUD (New/Edit/Delete/Process Now/Refresh) for SQL Tasks; AD Sync adds
  Organization-unit selection, a sync schedule, a save/apply **Template**
  concept (pick which AD users belong to which org, save it, re-run later)
  and a Manual Sync Log showing per-user Skipped/Updated outcomes; Exchange
  Sync maps Outlook Free/Tentative/Busy/Out-of-Office states to Savance
  statuses per user, with several comment-masking options for
  confidential/personal/private calendar events.
- **System Tray** menu duplicates the top toolbar's Service/Log/Settings/Help
  actions for quick access without the main window open.

## Cross-app shared building blocks

These pieces of vocabulary/logic appear in **multiple** apps with the same
meaning — get familiar with them once rather than per-app:

- **Status / Status Board** — every person (staff or visitor) has one
  current Status (In/Out/Unavailable-type, admin-configured, colored); the
  Status Board is the live grid of everyone's status. Source of truth is the
  Browser Interface's Admin → Statuses; Kiosk, Desktop, Mustering, and both
  mobile surfaces all read/write against that same list.
- **Returning** — the expected-back time attached to an Out/Unavailable
  status. Consistently offered as Unknown / 1 Hour / 3 Hours / 4 Hours /
  1 Day / Custom across Web, Mobile Web, Mobile, and Kiosk.
- **The 16-ish shared Question types** — Name, Company Name, Text, Integer,
  Decimal, Date, Time, Date+Time, Custom Options (branching), Yes/No
  (branching), Agreement (PDF viewer, branching), Signature, Status Location,
  Video, Website, Photo Capture, Face Enrollment, Host, File Upload. Defined
  once in Question Manager (Browser Interface Admin) and rendered identically
  in Web Visitor Sign In, Kiosk Visitor Sign In (minus File Upload — no file
  picker on a kiosk), and the Outlook Visitor Management add-in. A rendering
  bug in one question type is worth checking in all three surfaces.
- **Watchlist** — flagged-person screening list; same list, same
  match-by-account (not by typed name) behavior, wherever sign-in happens
  (Web, Kiosk, self-check-in).
- **Groups & Locations** — two independent org-structure axes (Groups =
  departmental/organizational; Locations = physical sites) used for
  filtering/scoping almost everywhere (Status Board filters, Search panels,
  Kiosk defaults, Mustering filters, Mobile filters).
- **Credential** — a physical access-control record tied to a person,
  separate from a printed Badge/Label; can be auto-activated/deactivated on
  visitor sign-in/out if Door Integration is enabled (Web Admin → Doors,
  Kiosk → Door Control, Mustering's own credential settings all point at the
  same underlying integration).
- **Installation Key / License Key** — generated once per organization in
  the (internal) Admin App; used to activate SwServer, Kiosk, and Mustering
  installs against that org.
- **Add-on licensing matrix** — the internal Admin App's Applications
  accordion is the actual on/off switch for Mobile, Calendar, My Customers,
  Send Text, Chat, Pictures, Resource Management, Alerts, Timecard, SMS,
  Status Board, and Visitor Management everywhere else in the suite. A
  "missing feature" report should always be checked against this matrix
  before being treated as a functional bug.

## Open items — needs domain knowledge

Grouped by app, so this is ready to hand back for analysis whenever that's
the next task. Not exhaustive line-by-line (the spreadsheet has the full
list with exact row references) — this is the shape of what's missing.

- **SwKiosk**: Comms/hardware wiring (COM port + PCProx/barcode reader
  behavior, badge-to-account assignment flow), Face Scanner enrollment/sync
  hardware behavior, full Door Control relay/access-integration setup, ID
  Scanner (CR5400) image-capture options, license-key Registry storage
  location.
- **SwEmergencyMustering**: Communication (COM ports/baud/card reader) and
  Inputs (named "Listen to Input Module" IP/port list) hardware sections;
  what exactly "Batch server queries" / batch size do; Prompt-for-User /
  Validate-Badge-ID behavior; GPS History; Print Template.
- **SwServer**: TAPI dialer, Exchange Sync fine detail, Inbound SMS, RF Code,
  Motorola RFID Devices, Infinias Devices, RFID Readers/Zones/Rules, Queue
  internals, Schedules, Manage User Pictures.
- **SwDesktop**: essentially all of Workplace Administration (Users,
  Security, Fields, Manage Groups/Locations, Status Management, Doors, Work
  Item Status, Company Settings, Company User Settings, Hours of Operation,
  Resources, My Customers, Timecard, Telephone, Filters, Quick Pick Messages,
  Paging System, Group Move Alerts, Roll Calls) and all of Workplace
  Settings — likely inherits Browser Interface's Admin behavior 1:1, needs
  confirming rather than fresh discovery.
- **SwMobile**: max group-chat size, exact Chat "User Grid"/search-by-type
  behavior, per-device Biometric Login verification.
- **Browser Interface / VMSuite**: Print Template (badge/label designer)
  detail, Admin → Doors detail, GPS History detail — all flagged in the
  Mustering sheet as needing follow-up even though they're Web-side features.
- **SwAdminWeb**: which exact fields are required on the "Forgot Password"
  page (sheet flags them as unconfirmed); supported image formats for
  Watchlist photo upload.
