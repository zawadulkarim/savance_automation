# Web applications

Referenced from `SKILL.md`. The four browser-delivered surfaces.

## Contents
- App 1 — Browser Interface (SwWeb)
- App 2 — VMSuite (Visitor Management feature-set)
- App 10 — Mobile Browser Interface (SwMobileWeb)
- App 11 — Admin App / Savance Internal Admin Portal (SwAdminWeb)

For live-verified Browser Interface detail — navigation map, field-level
behaviour, login route — see [[savance-workplace]] instead; this file is the
feature-scope view.

## App 1 — Browser Interface (SwWeb)

The core web product every customer logs into. Already documented in depth in
[[savance-workplace]] (navigation map, Admin sub-nav, glossary, live test
creds). This spreadsheet adds a few things not yet in that doc:

- **Status modal, fuller behavior**: besides the basic Status/Returning/
  Comment fields, there's a **Future Status** checkbox — when checked, it
  hides the One-Click Return buttons and reveals "Add to Company Calendar" +
  a **Starting** date/time (defaults to now) to schedule a status change for
  later. **One-Click Return Time** offers 1 Hour/3 Hours/4 Hours/1 Day
  shortcuts that just populate Returning. **Return Status** is a separate
  checkbox+dropdown (defaulting to "[Previous Status]") that appends the
  chosen return status to the Comment field — a way to pre-declare what
  status you'll flip to when you come back.
- **Context Menu** (right-click a row on the Status Board) is a bigger
  surface than it looks: one-click Out/Unavailable status change, Sign In/Out
  Visitor, Credential & Label printing, Contact Details, View Status History
  (→ Timesheet), Send Note (with Quick Pick Message templates + email/SMS/
  private checkboxes), Calendar, GPS History, Add/Remove My Friend, Group
  Membership, Administer User, and Static Comment (an admin-only note field
  distinct from a personal Note).
- **Reports** in this sheet lists ~20 canned reports (Dispatch Queue Status,
  Customer Summary, Future Status Summary, Group Audit, Phone List, Patient
  Status / Patient Visit Detail / Summary — Savance Health vertical — Roll
  Call Detail, In/Out History Summary, Late Returning Summary, Start/End Time
  Summary, Time and Attendance Calendar/Detail, Daily Non-Usage Summary,
  System Usage Summary, Visitor Activities Detail/Summary), plus a **Create
  New Report** custom builder and a **Use Classic Report** fixed/legacy mode.
  [[savance-workplace]] counted 27 across 8 categories from the live app —
  treat any discrepancy as the spreadsheet not being exhaustive, not as a
  contradiction.
- **Watchlist add flow**: once a Watchlist entry is saved, its **Company**
  field becomes permanently non-editable (only Comment stays editable) —
  worth an explicit test case since it's an easy-to-miss one-way field.
- **Visitor Sign In "Unique Identifier"** (configured in Question Manager)
  changes which fields are even shown/required at sign-in: Name Only, Phone
  Only, Name+Phone, Name+Company (Company becomes a free-add dropdown),
  Name+DOB, or Name+Government ID. Test each mode separately — the required
  fields and Possible-Matches search logic differ per mode.
- **Admin → Question Manager**: 16 question types are reused identically
  across Web Visitor Sign In, Kiosk visitor sign-in, and the Outlook VM
  add-in (see the shared list under [Cross-app shared building
  blocks, in `reference/server-and-shared.md`) — so a Question Manager bug
  usually needs verifying in all three surfaces, not just one.

## App 2 — VMSuite (Visitor Management feature-set)

Not a separately-installed app; it's the visitor-management workflow shared
by Browser Interface, Kiosk, and both Outlook Add-ins. Core pieces:

- **Visitor Sign In** — find-or-add a visitor (fields driven by the Unique
  Identifier setting above), run them through the configured Question
  Profile, screen against Watchlist, then confirm (with optional welcome
  email, picture, signature, label/badge print).
- **Watchlist** — a flagged-persons list (First/Last Name required; Company
  locked after save); any sign-in attempt matching a watchlist entry blocks
  and alerts a configured recipient. Matching is by visitor *account*, not
  free-typed name — so manually choosing "New Visitor" instead of an existing
  match bypasses the watchlist check (a documented, intentional gap worth
  knowing before filing it as a bug).
- **Question Manager** — the branching-questionnaire builder; profiles can be
  cloned, one marked as the org default, and built for either a normal screen
  layout or a Kiosk terminal layout.
- **Badge/Label printing & Credential activation** — Dymo (via Dymo Connect)
  or a custom designer for other printers; can auto-activate a physical
  access credential on sign-in/out if Door Integration is enabled.
- **Auto Credential Management** — separate from printing: can auto-issue and
  auto-deactivate access credentials for visitors and/or staff on sign-
  in/out, gated behind Door Integration being enabled.

## App 10 — Mobile Browser Interface (SwMobileWeb)

The older/lighter mobile web UI at `https://cloud.savanceworkplace.com/mobile/`
— a stripped-down page-based experience (Login → Home → sub-pages), not the
richer native app above. No apps are listed as impacted by changes here per
the Dashboard, and it doesn't impact others either — it's the most isolated
surface in the suite.

- **Home**: Update Status link, Status tile (icon + current status + color),
  Notes tile (unread count), People, Help, Settings, Sign Out.
- **Status update** has two depths: **MobileStatusLite** (pick a status,
  hit Update — no other fields) vs. the fuller **MobileStatusUpdate**
  (Status, Returning dropdown — Unknown/1hr/3hr/4hr/1day/Custom — conditional
  Date/Time fields disabled only when Returning = Unknown, Customer dropdown,
  free-text Comment).
- **Notes**: list view (photo, sender, timestamp, message, Reply, Delete) and
  a separate **Leave Notes** compose page (multi-recipient add/remove,
  Email/Text/Private checkboxes that turn green when checked, red Send
  button).
- **Find People**: Groups vs. Friends tabs; each listed user shows status
  color + last-refresh time and a direct Leave Note shortcut; a Search
  People page lets the user add/remove specific search criteria chips
  (Name/Ext by default) rather than a single fixed form.
- **Contact Details**: full profile (name/org/location/groups/status) plus
  quick In/Out buttons and a "More" button that jumps to the fuller
  MobileStatusUpdate page.
- **Settings**: site-wide Filter, User Type, and Time Picker Interval
  (controls the granularity of every MobileStatusUpdate time dropdown
  site-wide) — these are personal-but-site-scoped, unusual for a "Settings"
  page, worth remembering when a change here seems to affect other users'
  view unexpectedly (it's the same account's setting, not a shared one,
  unless the app is genuinely applying it org-wide — confirm which before
  filing that as a bug).

## App 11 — Admin App / Savance Internal Admin Portal (SwAdminWeb)

**Not customer-facing.** This is Savance's own back-office tool for creating
and administering every customer organization that exists on the platform —
the thing a Savance sales/support rep uses, not something any customer ever
sees. Best documented of the "peripheral" apps in this workbook (`Domain?`
and `Checklist?` are True almost everywhere).

- **Navbar**: Logout, "Sales Overview" (modal: Cloud/On-Prem/Total customer
  counts), global Search (matches against any Organization field), Create
  New Account.
- **Create/Edit Account** — the shape of a customer org record:
  - *Organization Information*: Org Number/Savance Customer Number/
    Installation Key/License Key are all system-generated and read-only
    (Install/License Keys are what customers use to activate SwServer, Kiosk,
    and Mustering); Org Name; Max Users (or Unlimited toggle, which disables
    the numeric field).
  - *Contact Information*: First/Last Name + Email required; Extension/Zip
    numeric; Phone/Address/City/State/Country optional.
  - *Account Information*: Cloud vs. On-Premise radio; Demo/Trial and Health
    toggles (Health = Savance Health vertical branding/features);
    Integrator/Internal/Sandbox flags (internal categorization only); Date
    Created/Expired (or Never Expire, which disables Date Expired); Support
    Expiration (only enabled for On-Premise); Purchase Price/Renewal;
    Max Install Attempts/Install Count; Account Representative; a
    **Service Center** button (only shown when editing, not creating) that
    deep-links to `servicecenter.savanceworkplace.com` — shows client info
    for a valid org, "Invalid Account" for a bad one.
  - *Applications*: this is the licensing matrix — 12 "One Times" toggles
    (Bundle enables all of them at once; disabling any one auto-disables
    Bundle) covering Mobile, SDK, Calendar, My Customers, Send Text, Chat,
    Pictures, TAPI, Exchange Sync, Resource Management, Alerts, plus separate
    Kiosk/Mustering/Punch license-count fields (each with a read-only
    "Installed" counter), a Timecard sub-block (toggle + expiration date/
    Never Expire), an SMS sub-block (status-update toggle + expiration +
    relay-to text), and standalone Status Board / Visitor Management toggles.
    **This matrix is the actual gate** behind most of the add-on features
    documented throughout the other 10 apps — if a feature seems "missing"
    in Web/Kiosk/Desktop, check here first before assuming it's a bug.
  - *Sign In Information*: the Admin Username/Password created here is what
    that org's first admin uses to log into every other app.
  - *Account Message*: free text shown in red in the Admin App's own search
    results — an internal-only annotation, not visible to the customer.
- **Search Criteria / Search Results**: heavy filter panel (Cloud/On-Prem,
  Active/Disabled/Expiring-within-N-days, Integrator/Internal/Sandbox/Trial,
  per-add-on filters, full contact-field search) feeding a paginated grid
  with Copy Info/Copy Account/Merge Account/Enable-Disable/Open/Delete row
  actions — Merge Account and Delete are the two higher-risk actions here
  worth being deliberate about in any test pass (data-destructive/
  data-combining, not easily undone).
- **Notes / Transaction History / Install History** tabs on an open account:
  free-text dated notes; a billing ledger (Create/Edit/Refund/Void/Delete
  transaction, with Authorization Code/Invoice #); and a per-install audit
  trail (Interface/Version/Trial-Expires/Upgraded?/Uninstall time) with
  Extend Trial / Revoke License actions.
