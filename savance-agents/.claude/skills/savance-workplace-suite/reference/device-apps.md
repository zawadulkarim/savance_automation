# Device and desktop applications

Referenced from `SKILL.md`. The three installed/on-device surfaces.

## Contents
- App 3 — Desktop App (SwDesktop)
- App 4 — Emergency Mustering App (SwEmergencyMustering)
- App 5 — Kiosk App (SwKiosk)

## App 3 — Desktop App (SwDesktop)

A native Windows client that largely mirrors the Browser Interface's Status
Board, but almost entirely gated behind "Require Domain Knowledge" in this
sheet — the spreadsheet documents the *shell* well and the *admin depth*
barely at all.

- **First-run wizard**: choose Cloud (`cloud.savanceworkplace.com`) vs.
  On-Premise (enter server/IP + Test Connection), then sign in (username/
  password, "Sign in with Microsoft", or Windows Authentication for
  on-prem/AD-joined machines only), with an optional "Open EIOBoard's
  Administration screen" checkbox on finish (admins only).
- **Navbar**: quick status dropdown, full Update Status panel (Name/Status/
  Returning/Comment), Refresh, Search pane toggle, Settings, Administrator,
  Sign Out.
- **Status Board views**: Standard (full grid, right-click column headers to
  toggle metrics) and Mini (name + status-color block only) tabs, plus
  Customers/Resources/Guests/Work List tabs, Group tabs (org-defined, e.g.
  Development/HR/Sales), and a personal "My Friends" tab populated via
  right-click → Add My Friend on the Status Board.
- **Advanced Search pane**: User Type / Filter / Primary Location / Status
  Type / Status / Name / Ext / Organization dropdowns, plus a "Within
  Selected Group" checkbox to scope the search to the active Group tab.
- **Marquee & Notes config** exist under Workplace Administration with real
  detail (text/font size/color/scroll toggle+rate/preview/save/reset for
  Marquee; a checkbox-options list with New/Edit/Delete for Notes) — these
  are Desktop-specific *admin* screens, separate from the Browser Interface's
  own Admin → Marquee.
- Everything else under **Workplace Administration** (Users, Security,
  Fields, Manage Groups/Locations, Status Management, Doors, Work Item
  Status, Company Settings, Company User Settings, Hours of Operation,
  Resources, My Customers, Timecard, Telephone, Filters, Quick Pick Messages,
  Paging System, Group Move Alerts, Roll Calls) and all of **Workplace
  Settings** is marked "Require Domain Knowledge" — likely because it's
  functionally the same config surface as Browser Interface's Admin section,
  just rendered in the desktop shell, so it inherits that doc rather than
  needing new discovery.

## App 4 — Emergency Mustering App (SwEmergencyMustering)

A dedicated Windows app for roll call during an emergency/evacuation. Reads
live status/roster data from the same server as the Browser Interface but
mustering-specific state (Present/Not Present/Unknown) is local to this app.

- **Setup**: license (Activate or Start Trial via Activation Key), then a
  mandatory Connect Server step (Server/Username/Password + Test Connection)
  — the app is unusable (settings menu items disabled, warning banner shown)
  until this succeeds. Shows a live "Connected | Last Sync: {datetime}"
  status and an auto-refresh countdown once configured.
- **Status Board tab**: All or By Group view; 4 read-only columns (Name,
  Status, Returning, Comment) synced from SwWeb — can't edit here, only view/
  sort/filter/refresh. A "Grid View Change" toggle switches to a compact
  2-column name+status-color view.
- **Roll Calls tab** — the core mustering workflow: a card grid of everyone,
  color-coded PRESENT (green) / NOT PRESENT (red) / UNKNOWN (gray), with a
  footer count of each. Toggles: **Hide Mustered** (hide people already
  marked present) and **Group By Status** (bucket the grid into the three
  status groups). A **PiP** (picture-in-picture) camera view supports
  barcode/badge scanning and facial recognition for hands-free check-off.
  Opening a person's card → **User Profile** page with big PRESENT/NOT
  PRESENT/UNKNOWN buttons, contact info, and (if enabled in Settings →
  System) a Biometrics/Facial Recognition management panel.
- **Search/Filter** page: Name text filter plus multi-select filters (Status
  Type, Status, Group, Status Location, Organization Location, User Type),
  each with a tri-state "select all" checkbox (checked/unchecked/
  indeterminate-square when partially selected) — this indeterminate-state
  behavior repeats identically across all five filter categories, so one bug
  there likely affects all five.
- **Settings** duplicates the Connect Server step plus a large System panel:
  auto-refresh interval, auto-update-after-idle-time, logging, reconnect
  delay, on-screen keyboard, mini-view column count, windowed vs. full-screen,
  password-gated settings access, Facial Recognition (provider/integration
  dropdowns, only enabled when the feature toggle is on), Barcode Recognition
  (PDF417 state IDs / QR codes), and Status Board display options (include
  visitors, text size, show status color, lock to one group/location).
- Hardware-facing subsections (**Communication** — COM ports/baud/keyboard
  wedge card reader; **Inputs** — a named "Listen to Input Module" list tied
  to IP/port; **Actions** — input-triggered messages/mustering
  enable-disable) are marked "Require Domain Knowledge" — these need an
  actual reader/relay device to test meaningfully.

## App 5 — Kiosk App (SwKiosk)

The physical lobby/front-desk terminal. Two audiences in one app: **Staff**
(sign in/out, status board) and **Visitor Management** (guest sign-in flow).
Almost the entire feature list here is settings/config (`Checklist?` = False
throughout) rather than end-user flows, because most of it is one-time setup
done by an installer/admin, not something re-tested every release.

- **Installer**: shortcuts (Desktop/Start Menu/Startup), custom install path,
  and a long list of optional OS-hardening toggles baked into the installer
  itself — Disable Lock Screen, Gemalto Document Reader driver, Disable USB
  Storage, Disable Widgets, Enable Auto Login, Never Turn Off Display/Sleep,
  Disable Touchscreen Keyboard, Cyberlink Facial Recognition, GoToAssist,
  rfIDEAS tool.
- **Licensing & first connection**: Trial or full Activation on fresh
  install; Server/Username/Password + Test Connection to bind the kiosk to
  an org, after which it stays synced and never re-prompts for a license.
- **Staff — General**: which screen the kiosk defaults to (Main/Employee
  Login/Status Board/Visitor Login/Resource Availability), Admin Pin (default
  `7282623`, 5+ digits recommended to avoid colliding with a real User ID or
  badge number), offline caching (queues status changes while disconnected,
  uploads on reconnect), and separate log files for the kiosk itself and the
  temperature scanner.
- **Staff — Options/Status**: a large block of sign-in-flow toggles — masking
  ID/PIN entry, requiring a PIN after badge swipe, validating badge against
  PIN instead of ID, tap-to-change-status from the board, keypad vs.
  badge-only login, full keyboard vs. numpad, default status comment,
  logoff-after-timeout, per-status Question Profile prompting (with an
  "Only Ask for In Statuses" narrowing option and a "Skip Status Update" mode
  that just records answers without changing status), Auto Confirm.
- **Staff — Visitor Management** (the bulk of the sheet): sign-in/out
  enablement, Watchlist checking + alert email, welcome-message toggles
  (separately for visitors and staff), Anonymous Visitor, search behavior
  ("Starts with" vs. contains, letters-only), Epic EHR validation (health
  vertical); Advanced Options (auto-confirm timeouts for sign-in/out, various
  page timeout durations, default Type/Status/Group/Location per kiosk,
  sign-out list filtering/search-limit behavior); Alerts (override
  company-wide alert config per kiosk, "Here to See" auto-alert); Questions
  (profile switching); Badge Assign (admin-password-gated, alphanumeric IDs
  allowed); Label Printing (Dymo vs. custom, staff-exempt option, print
  preview); Label Alerts (Dymo-only low-label-count warning email); ID
  Scanner (2D-barcode-only mode, CR5400 driver's-license scanner with
  configurable image capture); Languages (secondary language + staff-
  questionnaire language toggle); Summary Page (custom HTML shown after
  confirmation); Screening Settings (temperature pass/fail thresholds in
  °C/°F, manual entry, pass/fail-only storage, per-audience pass/fail status
  assignment, alert email); Screening Advanced (credential auto-management,
  failed-sign-in alert sound, temperature scanner debug mode, watchlist
  toggle per kiosk).
- **Staff — Comms/Face Scanner/Door Control** are almost entirely "Require
  domain knowledge" — COM port wiring, badge-to-account assignment UI, face
  scanner enrollment sync, and the full Door Control module (PoE/Web relay
  device management, Kantech-style access integration, per-event door-open
  triggers) all need real hardware to validate.
- **Staff — Views**: the Status Board's own display designer — create/edit/
  delete named "Views", each either a no-code **Standard** board (filter by
  status/group/location, choose columns, font/sort/grouping/scroll options)
  or a fully custom **HTML Board** (raw HTML/CSS/JS).
- **Staff — Status Buttons / Return Buttons**: admin builds the actual
  buttons shown on the sign-in screen — each Status Button maps to a target
  status + caption + optional status-colored background + "skip return-time
  prompt" flag; each Return Button maps to an amount+unit of time (or
  "Unknown" or a custom manual-entry prompt) + caption.
- **Staff — Screen Locking / Auto Update**: idle-triggered lock screen with a
  configurable modifier-key unlock combo (Ctrl/Alt/Shift + one more key,
  default password `7282623`); silent auto-updates restricted to an idle
  window and off-peak hours.
- **Staff — Customizations** (Labels/Buttons/Text Boxes/Controls/Pop Ups):
  per-element color/font overrides with an "apply this style to everything"
  bulk action — cosmetic, but the bulk-apply action is the one thing worth an
  actual test (does it really touch every control, or miss some).
- **Visitor Sign In / Status Board (end-user flows)**: the actual guest-
  facing screens — Welcome screen (Sign In/Sign Out), the same 16 shared
  question types as elsewhere in the suite (see [Cross-app shared building
  blocks, in `reference/server-and-shared.md`; Kiosk explicitly skips the
  "File Upload" question type since there's no file picker on a kiosk), and
  a Status Update screen (photo/name/status, Timesheet button, Notes button,
  Status/Return buttons as configured above).
