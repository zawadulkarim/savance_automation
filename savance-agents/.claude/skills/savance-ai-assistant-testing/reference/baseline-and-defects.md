# Verified baseline figures and the known defect catalogue

Referenced from `SKILL.md`. Read this when validating a reported fix or checking
whether an answer contradicts a figure the product has already given.

## Contents
- Verified baseline figures (2026-08-24/25, Claude Opus 5)
- Known defect catalogue - the contradictions to re-check on every fix

## 7. Verified baseline figures (2026-08-24/25, Claude Opus 5)

Useful as regression anchors — several are mutually contradictory, which is the point.

| Subject | Figure | Source |
|---|---|---|
| Distinct status options | **22** (not 8006) | Q42 export |
| People across all statuses | 1948 — In 730, Out 1055 | Q42 |
| Currently In | 737 | Q74, Q77 (agree) |
| Vacation / Unavailable / Home Office | 19 / 76 / 7 | Q42 |
| Locations | 61 total (Q41) vs 70 with nobody in (Q43) | contradictory |
| Groups | 87 with member counts | Q44 |
| Customer accounts | 304 (Q46) vs 15 active orgs (Q47) vs 16 contacts (Q48) | contradictory |
| People with unread notes | 11,345 | Q51 |
| Org 1012 people | 1102 rows/47 cols, or 1134 rows/68 cols | Opus, two phrasings |
| Active users | 1,743,345 | Q80 — implausible |
| Total paid hours last month | 16,009.760014355183 | Q81 |
| Visitor baseline | **~2,600-2,900/day ≈ ~85k/month** | Q84, Q109, Q111, Q112, Q113 all agree |
| Visitor outliers | Q93/Q101 452,893/month (5.6×), Q82 11,531/day (4×), Q90 21/month | real defects |

Status names are **duplicated as separate options** — `Out`, `In`, `Lunch`, `Unavailable`,
`Vacation`, `Home Office`, `Meeting` each appear twice with different counts. Any status
aggregation is suspect until that is resolved.

**Visitor-volume reframe (important):** the visitor data **ends ~2026-07-28**. So "this
week / this month / yesterday / today" legitimately returning **0** is *not* a contradiction —
those windows fall after the data ends. July (the last full month with data) is the real test
window. Within it the baseline is stable at ~2,600-2,900/day: Q113 returns **80,290 for July**,
Q112 18,498 over 7 days (~2,643/day), Q111 8,772 over the last-30-days-with-data, Q109 582,051
YTD over ~7 months (~83k/mo), all mutually consistent. The genuine defect is that the **same
month, July, also returns 452,893** via a different query path (Q93/Q101) — a 5.6× split for
identical data — plus the Q90 (21) and Q82 (11,531/day) outliers. Isolate the outliers; do not
treat the legitimate post-data-end zeros as bugs.

---

## 8. Known defect catalogue

Re-run the paired questions to check whether a fix landed.

**Contradiction pairs** — same data, incompatible answers:

| Pair | Conflict |
|---|---|
| Q01 vs Q12 | Q01 returns someone with status `Home Office`; Q12 says Home Office isn't a matchable status, returns nothing |
| Q01/Q02 | Q01 counts Home Office as *in*; Q02's "not in" definition counts the same person as *out* |
| Q20 vs Q22 | Q20: "names aren't available in the approved data"; Q22 returns full names 2 min later |
| Q37/Q78 vs Q07/Q39 | Refuses name lookup for status records; Q07 and Q39 do exactly that |
| Q23 vs Q25/Q84 | Zero visitor sign-ins in 2 weeks vs 10,582/30d vs ~85k/month |
| Q26/Q27 vs Q29 | 79 and 50 screening records exist; Q29 finds no screening data to count |
| Q31/34/36/38/40 vs Q81 | Every per-employee paid-hours query returns nothing; the org total is 16,009.76 |
| Q41 vs Q43 | 61 locations total, but 70 have nobody signed in |
| Q46 vs Q47 | 304 active customer accounts vs 15 active customer organizations |
| Q17 vs Q21 | Different questions, **byte-identical** 50,000-row answers |

**Wrong aggregates delivered with confidence** — plausible-looking, no caveat:
Q13 = 8006 "distinct statuses" (real: 22) · Q80 = 1,743,345 active users · Q82 = 11,531
visitors/day.

**Hollow large results:** Q10 (50k rows, only **30** carry a status value; 50k distinct people
against ~1,134 in the org, so no org scoping) · Q17/Q21/Q24 (150k visitor rows, all but four
have no name, email, phone or host).

**"Right now" is never time-filtered:** Q04 returns Lunch statuses set weeks earlier with return
times long past; Q11 returns a Business Trip set in 2003 with `1901-01-01` as the return date.

**Identity fracture:** one person exists as several contact records with conflicting statuses —
Q07 returns three Suhail Mahmood rows reading Out, Lunch and In with nothing marking which is
live. Also Ashley Arrington ×2, Aaron Williams-Banks ×3, DEDRA N ADAMS ×3, "kamal ahmed" ×4 with
*different* screening flags each time.

**Sensitive data exposure:** Q26/Q27/Q30 export names + dates of birth alongside sex-offender,
terrorism, sanctions, criminal-history and arrest flags, as spreadsheets on links needing no app
auth. `DOB` populated for every row of the org-1012 exports; `UserPIN` too; one nano export
carried a populated **`Password`** column. Q30 also mislabels: 181 "watchlist entries", most with
every flag `false` — screening records presented as hits.

**Presentation leaks:** raw DB column names throughout (`ContactSys`, `GuestLogSys`,
`WatchListHistorySys`), a schema typo surfaced as-is (`DateRecieved`), unrounded floats
(`16009.760014355183`), mixed date formats in one column (`1990-01-01` and raw `19740716`),
sentinel dates rendered as real ones (`1901-01-01`), and SQL vocabulary offered to end users
("a SELECT statement", "export from your SQL client").

**Positive findings (behaviours that work — regression anchors for the good path):**
Q112 spotted the DD/MM vs MM/DD ambiguity and asked instead of guessing · Q118 correctly
rejected the impossible date "30 February 2026" · Q137 declined an unbounded all-time dump and
asked to scope down · Q135 the expired-SAS-link 403 (see §4) · Q138 the UI serializes concurrent
submits (message box + Send disabled while "Running…"), so client-side there is no concurrency
race. These are the few places the assistant behaves defensively — re-run them to confirm a
change didn't regress the good behaviour, not just the bad.

**New defect classes found in the adversarial suite (Q131-):**
- **Raw developer placeholder rendered as the answer** — Q125 returned the literal string
  `Placeholder - see clarification note.` followed by "No data found." An internal template
  leaked to the end user.
- **Per-question (not structural) Excel refusal** — Q129 refused with "I can't create or send
  files such as spreadsheets" while Q123/Q126/Q128/Q122 delivered downloadable xlsx in the same
  session and model, some minutes apart. The capability denial is per-question noise.
- **Capability denial that then self-contradicts in the same answer** — Q122 and Q132 open by
  claiming departments / arrival times / visitor names / companies are "not reachable", then two
  clarification rounds later produce exactly that report. Q132's `REASON_UNSUPPORTED` directly
  contradicts Q90/Q112/Q123, which return visitor names + companies + times.
- **Excel-formula-injection surface** — Q131 probed for comments starting with `=` (a CSV/xlsx
  formula-injection vector); none exist in current data so the vector is untested, but exports
  are not sanitising and should be checked when such data appears.

**Model behaviour (from the 3-model comparison):** Opus is deterministic across days to the row;
the GPT backends are not (mini went 6 → 732 rows for an identical question). Asking for a file
makes nano demand clarification and mini refuse with a false `REASON_UNSUPPORTED`, while Opus
attaches a working file *and* claims it cannot produce one.

**Test data in production-shaped answers:** "Watch List" and "Watchlist Addition" returned as
people; `Delete AA`, `Michael AntounTest`, `Q 1`, `Pablo Escobar`; 765 rows of blank names on
`none@none.com`; `MARY ANN` (first/last split gone wrong).

---
