# Mobile and Outlook applications

Referenced from `SKILL.md`. The native mobile clients and the two Outlook
add-ins.

## Contents
- App 6 — Outlook Add-In Full Window App
- App 7 — Outlook Add-In Visitor Management
- App 8/9 — iOS / Android App (SwMobile)

## App 6 — Outlook Add-In: Full Window App

Launched from Outlook's "More Apps" menu; requires the org admin to grant a
specific organization email before a user can even open it. Functionally
**this is the Browser Interface**, re-hosted inside Outlook — the sheet
explicitly says no separate feature list was kept because everything else
matches SwWeb 1:1 (same Login/Home/Status/Notes/Reports/Timesheet/Calendar/
Admin/etc. — see App 1 in `reference/web-apps.md`). Two things are
genuinely Outlook-specific:
- **SSO with multiple Outlook accounts**: if Outlook has 2+ accounts signed
  in, SSO always authenticates using whichever account is set as *primary* in
  Outlook's own settings — not necessarily the one the user expects.
- **Loader placement**: every page has a loading spinner in the top-left,
  next to the Status dropdown — a fixed, consistent location worth checking
  after any layout change.

## App 7 — Outlook Add-In: Visitor Management

A **task pane** add-in (Outlook → New Event → Calendar → Apps), not a full
window — built for one job: turning a meeting's invitee list into
pre-registered Savance Workplace visitors before the meeting happens.
Restricted to **Admin/Master Admin** accounts; everyone else gets an
access-denied screen. Persists login across restarts once authenticated.

- **Add Attendees**: a Refresh button pulls the current Outlook invite's
  guest list into the pane; after that, it **live-syncs** — typing a new
  email into Outlook's native attendee box, or removing one, updates the
  pane automatically (including de-duplication). Known emails get their
  First/Last Name auto-filled from Savance's existing contact records.
- **Attendees Settings**: hide-internal-guests (same email domain as the
  org) toggle, bulk welcome-email on/off, bulk and per-guest pre-registration
  checkboxes, inline name editing with a blank-name warning, per-guest
  welcome-email override, and a red→green question-completeness indicator
  per guest that jumps straight to that guest's unanswered questions.
- **Questions**: the same 16-ish question types shared across the suite (see
  below), rendered per-attendee with an "Apply to all attendees" checkbox to
  copy one answer set to everyone at once, and a profile switcher that warns
  before wiping in-progress answers.
- **Complete PreRegistration**: hooks Outlook's native **Send** button —
  clicking Send in the calendar invite is what actually triggers saving the
  pre-registration (either everyone, or just the guests individually checked
  off), blocking with an error if required answers are missing, then
  emailing welcome messages (with duplicate-send protection) and showing a
  success message. This Send-button interception is the one behavior in the
  whole suite most likely to break silently on an Outlook/Office update —
  worth a dedicated regression check after any Outlook version bump.

## App 8/9 — iOS / Android App (SwMobile)

The native mobile app — the richest client after Browser Interface, with
capabilities none of the other apps have (live location, geofencing, native
chat). Per the Dashboard, this is genuinely under-tested territory ("we have
not tested the new mobile apps... not sure which features are there").

- **Login**: Cloud vs. On-Premise (with Test Connection for on-prem),
  username/password with a Remember toggle, Forgot Password → email OTP flow
  (5-minute countdown, Resend Code once expired) → New/Confirm Password reset,
  Microsoft SSO, and a Biometric Login option (Face ID/fingerprint) flagged
  as needing domain knowledge to verify per-device.
- **Home**: profile card with current status + last-updated timestamp, and
  shortcut tiles to My Status, Status Board, Visitors, Notes, Chat, Support,
  Settings. A **Personalize Home** screen (via the header context menu) lets
  a user toggle any of those tiles (plus Emergency, Alerts) off the Home
  screen entirely — so an "expected" tile missing during testing may just be
  a personalization setting, not a bug.
- **My Status**: if Location permission/Location Access is off, shows a
  dismissible prompt nudging the user to Settings. Status picker (checkmark
  on current selection), Return Time (6 quick buttons: 30 Min/1 Hour/2
  Hours/3 Hours/4 Hours/1 Day, or a full calendar+time picker), Location
  (org-configured list), and read-only Last Update/Updated By/Comment.
- **Search**: dynamic-as-you-type user search with server-driven filter
  accordions (Group/Status/Primary Location/Status Location), sort by
  First or Last Name, Reset/Apply actions.
- **Visitors**: card-grid list; Register Visitor form (Last Name/Email/Phone/
  Registration Start+End Date/Company/Host Email, with Start Date + Company
  required) and Update Visitor form (pre-filled, First/Last Name + Start
  Date required) — note the *required* field set genuinely differs between
  Register (Company required, not First Name) and Update (First Name
  required, not Company) per the sheet; verify that isn't itself a
  documentation slip before treating it as intended behavior.
- **Notes vs. Chat**: both live under a "Communication" screen behind a
  segmented Chat/Notes toggle (Chat is the default landing tab). Notes:
  search + filter + a green FAB → New Note (recipient search/add/remove,
  2000-char counter, Choose From Template sheet pulling from Web-configured
  templates, per-note Send Email/Send Text/Make Private toggles). Chat: Edit
  mode for bulk-delete, New Chat modal supporting 1:1 or named group chats
  (max group size unknown — flagged as an open item), per-conversation
  Mark as Unread/Mute/Delete.
- **Settings**: Connection (server/username, Change Password sub-flow),
  Location (Location Access toggle gates Location-based Status Update toggle,
  which auto-changes status when entering/leaving an admin-drawn map Zone —
  Zone In/Zone Out statuses configured per zone, "None" = no auto-change on
  exit), Map (satellite/terrain/default view types, zone visibility toggle,
  zone creation by dropping ≥3 markers), Logging, and misc Visitor/Other
  toggles.
