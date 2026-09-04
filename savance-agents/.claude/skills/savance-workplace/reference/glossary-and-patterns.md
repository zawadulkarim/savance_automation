# Glossary, cross-module relationships and UI patterns

Referenced from `SKILL.md`. Read this when a term is unfamiliar or when working
out what else a change touches inside the Browser Interface.

## Contents
- Domain glossary
- Cross-module relationships
- Common UI / interaction patterns
- Notes for future testers

## Domain glossary

| Term | Meaning |
|---|---|
| Status | Core state of a person (In, Out, Lunch, Vacation, Business Trip, Home, Unavailable, Meeting, Home Office, Sales Call); admin-configurable, each flagged Paid/Unpaid and In/Out/Unavailable |
| Status Board | The live Home-page grid of everyone's current status |
| Roll Call | Emergency/muster feature; "Clear Roll Call" resets it |
| Watchlist | Screening list of flagged individuals cross-referenced against staff/visitors |
| MKDenial | Denied-party/sanctions-list screening integration |
| CheckrTrust | Background-check provider integration (Sex Offender, arrest, Criminal/traffic categories) |
| Savance Background Check | Savance's own in-house background-check product |
| Group | Organizational/departmental hierarchy node, used to scope permissions |
| Location | Physical site/place associated with a user or status, separate from Group |
| Customer | CRM-like entity a user's status/time can be attributed to for billing/reporting |
| Paid / Unpaid | Classification on each Status Type determining whether time counts toward paid hours |
| Return Time / Returning | Expected/actual time a person returns from an Out-type status |
| Future Status | A status change scheduled to take effect at a future time |
| Wait Time | Computed metric between a configurable Start Status and End Status |
| Pre-Registered Visitor | A visitor scheduled ahead of time |
| Question Profile / Question Manager | Branching questionnaire builder used during visitor sign-in |
| Contactless Visitor Registration | QR-code/link-based self check-in (Mobile Check-in) |
| Wallet Pass | Apple/Google Wallet-style digital visitor badge |
| Badge / Label | Physical printed credentials for staff/visitors |
| Credential | Badge/access-card record tied to a user, auto-managed and clearable |
| Work Item | Ticket/task entity — licensable module, modeled in Fields/Security |
| Resources / Resource Management | Bookable physical resources (rooms/equipment); an add-on |
| Security Group | Named permission bundle assignable per user, prefixed `EB` (legacy EIOBoard) |
| GPS Zone | Automatic status changes triggered by device entering/exiting a geofence |
| Organization | Top-level tenant/company record (here, "SM Org") |
| Marquee | Configurable scrolling text ticker/announcement banner |

## Cross-module relationships

- A **User/Contact** (Staff or Visitor) is the central entity: current **Status**
  (+ Location, Comment, Returning time), belongs to a **Group** and **Primary
  Location**, may tie to a **Customer**, carries a **Watchlist Comment**, holds
  **Security Groups**, and has a **Credential/Badge**.
- **Visitor Sign In** creates/looks up a Contact → runs **Question Manager**
  questionnaire → checks **Watchlist** (Savance BG Check / Checkr Trust / MK
  Denial) → on success can print a Badge/Label, issue a Wallet Pass, and send a
  Message Template (e.g. Visitor Welcome) containing a QR code/wallet-pass link.
- **Statuses** (Admin) are the single source of truth for the Status Board
  dropdown, Filters, Time & Attendance reports, and Timesheet Paid/Unpaid math.
- **Fields** (Admin) defines custom fields across Contact/Status/Resources
  View/Work Item/Reports — the schema layer behind several modules.
- **Registration & Licensing** add-ons gate whether Resources, Chat, Calendar
  Sync, Timecard, My Customers etc. are usable, independent of Security Group
  permissions.

## Common UI/interaction patterns

- **List + Filter**: nearly every list screen pairs a data grid with a
  collapsible Filters/search panel and page-size selector.
- **Admin sub-nav accordion**: 4 collapsible categories (General / Integrations
  / Messaging & Alerts / Users, Groups & Security), each expanding a link list.
- **Iframe-embedded sub-apps**: Watchlist, Visitor Sign In, Question Manager,
  Wallet Pass, Message Templates, Mobile Check-in render inside an `<iframe>`
  within the classic ASP.NET WebForms chrome — evidence of newer SPA modules
  layered on a legacy shell.
- **Postback-heavy navigation**: many links use `javascript:__doPostBack(...)`
  rather than real URLs — plain hrefs won't always identify the target when
  automating.
- **Deploy/propagate pattern**: Company User Settings can push default
  preferences org-wide ("Deploy All Defaults" / "Deploy All My Settings").
- **Category-tabbed marketplaces**: Reports (8 categories) and Access-Control
  Integrations (5 categories) both use an "All + named category tabs" browse UI.
- **Checkbox field value display**: a multi-select **Checkbox** custom field's
  chosen options render as one comma-separated string wherever the value is
  shown read-only (Visitor Confirmation, Contact Details) — a recurring
  cropping/no-wrap defect surfaces here when many options are selected; worth
  checking with a large option count whenever touching Checkbox-type fields.

## Notes for future testers

- Two distinct "Notes" concepts: personal `MyNotes.aspx` (inbox) vs. Admin →
  Notes (settings page) — don't conflate in test-case names.
- Two distinct "My Settings"-shaped screens: personal `MySettings.aspx` vs.
  org-wide `UserSettings.aspx` (Company User Settings, adds Save & Deploy) —
  easy to confuse.
- **Resources** and **Work Items** modules are fully modeled in
  Security/Fields/Global-Settings but weren't reachable as top-level nav items in
  this test org/license — likely gated by an add-on license or a settings
  toggle; check with a different license/permission profile if testing those
  areas.
- This test org has several empty setup areas (Doors, Groups & Locations,
  Customers) — automation assuming seeded data there needs setup first.
- Test data includes seeded watchlist fixtures (Timothy Dukes, Ezell Brooks) for
  exercising the Sex-Offender/CheckrTrust matching path, and obviously synthetic
  placeholder contacts (e.g. "VM Test/Two/Three").
