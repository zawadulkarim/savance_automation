---
name: savance-ai-assistant-testing
description: Test harness and defect catalogue for the Savance AI Assistant — the natural-language reporting front end at ai-test.savanceworkplace.com answering data questions over Savance Workplace data. Covers login (including the expired-cert click-through), the low-token capture harness, the response/error taxonomy, retry protocol, baseline figures, and the known contradictions to re-check when validating fixes. Use when running question suites against it, filing bugs on the Savance AI Reporting project, or verifying a fix.
---

# Savance AI Assistant — testing playbook

The **Savance AI Assistant** (`ai-test.savanceworkplace.com`) takes a plain-language data
question and answers it from Savance Workplace data. It is a separate app from the Workplace
browser interface — for that, see [[savance-workplace]] and [[savance-workplace-suite]].

Everything below was established by running two suites end-to-end and reading the exported
workbooks, not by reading source: a 130-question reporting suite (`test-question.md`) and a
132-question adversarial/security suite (`test-question2.md`, Q131-Q262). Figures are dated;
re-verify before quoting them as current.

---

## 1. Access

| | |
|---|---|
| URL | `https://ai-test.savanceworkplace.com/` |
| Login | user `zawad`, password `Enosis123` (test env) |
| Bug parent | Savance AI Reporting project — see [[8-asana-bug-report]] |

Login is a two-field form then a **"Sign in"** button. The session persists across page
reloads (localStorage), so a reload gives a fresh chat *without* re-authenticating — but a
browser restart requires logging in again.

### Expired TLS certificate — click-through

As of **2026-08-25** the wildcard cert `CN=*.savanceworkplace.com` (Sectigo RSA DV) expired at
`2026-08-24 23:59:59 GMT`. Chrome refuses the site with `ERR_CERT_DATE_INVALID` and
`browser_navigate` throws. The interstitial *is* rendered, so click through it:

1. `browser_navigate` → it throws; ignore the error
2. `browser_snapshot` → shows "Your connection is not private"
3. Click **"Advanced"**
4. Click **"Proceed to ai-test.savanceworkplace.com (unsafe)"**
5. The site loads; the exception is now accepted for the browser session

Do **not** add `--ignore-https-errors` to the Playwright MCP config — the click-through needs no
reconnect and leaves the user's config clean. The expired cert is a real defect affecting the
whole wildcard (so `test.savanceworkplace.com` too); keep it in the bug report even after
bypassing it.

---

## 2. The interface

- **Model dropdown** — exactly three options: `GPT 5.4 nano` (default), `GPT 5.4 mini`,
  `Claude Opus 5`. Resets to nano on some reloads, so select explicitly every time.
- **Message box** — hard **200-character** cap with a live counter. Long questions must be
  trimmed; the box shows ~2 lines and does not grow (filed as an Improvement).
- **Send** — button, or Enter. Turns into "Running…" then "Cancel" while working.

### Selectors that survive re-renders

Element `ref=` ids change on every snapshot. Use selectors instead and skip a snapshot per run:

| Target | Selector |
|---|---|
| Message box | `textarea` |
| Send button | `button:has-text("Send")` |
| Model dropdown | `select` |

---

## 3. Low-token capture harness

A 130-question suite will blow out context if each answer is pulled into the transcript — a
single 10-row × 11-column table snapshot costs thousands of tokens. Instead **dump the snapshot
to a file and grep it**.

Per question (8 calls, all with tiny outputs):

1. `browser_navigate` (reload = fresh chat)
2. `browser_select_option` → `Claude Opus 5`
3. `browser_fill_form` → `textarea`
4. `browser_click` → `button:has-text("Send")`
5. `browser_wait_for` `textGone: "Running"` — **often needs a second call**; the default 5s
   timeout expires on slower queries. On a third failure use `browser_wait_for time: 25`.
   **Gotcha:** when the *question itself* contains the word "running" (e.g. "show a running
   total"), `textGone: "Running"` matches the echoed question text and returns instantly before
   the answer lands. For any such question use a fixed `time: 25` wait instead of `textGone`.
6. `browser_snapshot` with `filename: "snap/qNN.yml"` — returns nothing to context
7. `browser_take_screenshot` → `ai-reporting-results/screenshots/qNN_opus.png`, `fullPage: true`
8. `sh probe.sh NN` — summarises the file and auto-downloads any report

`snap/` must exist first (`mkdir -p snap`) or the snapshot call errors.

### probe.sh

```sh
#!/bin/sh
# usage: sh probe.sh NN  -> summarise the LAST response in snap/qNN.yml, download any report
n="$1"; f="snap/q$n.yml"
[ -f "$f" ] || { echo "NO SNAPSHOT $f"; exit 1; }
last() { grep -n "$1" "$f" 2>/dev/null | tail -1 | cut -d: -f1; }
be=$(last "REASON_EXECUTION_ERROR"); br=$(last "REASON_"); bc=$(last "Needs clarification")
bn=$(last "No data found"); bt=$(last "columnheader")
best=0; out="DATA"
for pair in "$be:EXECUTION_ERROR" "$br:REASON_OTHER" "$bc:NEEDS_CLARIFICATION" "$bn:NO_DATA" "$bt:DATA"; do
  ln=${pair%%:*}; lbl=${pair#*:}
  [ -n "$ln" ] && [ "$ln" -gt "$best" ] 2>/dev/null && { best=$ln; out=$lbl; }
done
[ "$out" = "REASON_OTHER" ] && out=$(grep -o 'REASON_[A-Z_]*' "$f" | tail -1)
echo "OUTCOME: $out"
grep -o "Showing first [0-9]* of [0-9,]* rows[^\"]*" "$f" | tail -1
echo "inline_rows: $(grep -c '^ *- row ' "$f")"
grep -o 'paragraph \[ref=[^]]*\]: .*' "$f" | tail -3 | cut -c1-380
grep -o 'listitem \[ref=[^]]*\]: .*' "$f" | tail -4 | cut -c1-170
grep -o 'columnheader "[^"]*"' "$f" | tail -14 | sed 's/columnheader //' | tr '\n' ' ' | cut -c1-420; echo
url=$(grep -o 'https://savanceaireportsdev[^ "]*' "$f" | tail -1)
if [ -n "$url" ]; then
  curl -sS -o "ai-reporting-results/report_files/q${n}_opus.xlsx" "$url" \
    && echo "DOWNLOADED q${n}_opus.xlsx $(stat -c %s "ai-reporting-results/report_files/q${n}_opus.xlsx")b"
else echo "no file"; fi
```

It reads the **last** response in the file, so it works after clarification rounds. Pipe through
`2>/dev/null` — a harmless `echo: write error` sometimes appears mid-script and can abort the
download step; if that happens, re-run the curl by hand.

### Output layout and naming

```
ai-reporting-results/
  screenshots/    qNN_opus.png          (one per question; qNN_opus_retry.png for retries)
  report_files/   qNN_opus.xlsx         (only where a download was offered)
  run-log.tsv     q / question / outcome / rows / file / notes
  RESUME.md       stop point + protocol, for picking the run back up
snap/             qNN.yml               (working snapshots, not a deliverable)
```

Zero-pad to two digits (`q07`) so ordering survives past q9. Append to `run-log.tsv` every few
questions — an interruption then costs at most one question.

---

## 4. Response taxonomy

| Shape | Meaning |
|---|---|
| Prose + inline table | ≤10 rows. **No file offered.** |
| `Showing first 10 of N rows` + **"Download to view more"** | >10 rows. File link present. |
| `Showing first 10 of 50000 rows (truncated at the row limit)` | Hit the **50,000-row ceiling** — the true count is unknown, not 50,000. |
| `No data found` | Query ran, returned nothing. |
| `❓ Needs clarification` + option list | Wants a follow-up; answer in the same chat. |
| `🚫 REASON_*` | Refusal or failure. See below. |

**A download link appears purely because the result exceeds 10 rows** — not because the question
asked for a file. Asking for Excel explicitly makes things *worse* on the GPT backends.

### REASON_* enums (all leak raw as the response heading — itself a bug)

| Enum | Meaning | Handling |
|---|---|---|
| `REASON_UNSUPPORTED` | Claims a capability it lacks — frequently **false** | Log, continue |
| `REASON_EXECUTION_ERROR` | "The query could not be run" | Log, continue |
| `REASON_AMBIGUOUS` / `REASON_OUT_OF_SCOPE` | Rejected the question | Log, continue |
| `REASON_LIMIT_EXCEEDED` | **Daily usage cap** — account-wide across all three models | Hard gate; stop |
| `Exception was thrown by handler.` (raw, no enum) | Session-state corruption | Close browser, re-login, retry ×2; if it persists, log and stop |

### Blob downloads are unauthenticated bearer links (verified by curl)

Reports land on `savanceaireportsdev.blob.core.windows.net` with a SAS token valid **~15
minutes**. Download immediately in the same turn — never batch them for later. The security
shape was confirmed directly with `curl`, no browser session:

- **Q133** — a fresh SAS URL returns the full xlsx over `curl` with **no cookies, no session, no
  login** (HTTP 200). It is a pure bearer link.
- **Q134** — the URL carries **no user identity**, so a different user (or none) holding it gets
  the same file. There is no per-user authorization on the download.
- **Q135 (positive)** — the ~15-minute window **is** enforced: an expired link (`se=` in the
  past) is correctly rejected with **HTTP 403**.

So sensitive exports (screening flags, DOB, PINs — see §8) are protected *only* by a
short-lived, shareable, no-login link that is printed in plain text in the chat transcript.

---

## 5. Protocols

### Clarification rounds
Answer from the assistant's own offered options, verbatim, so the choice is traceable. Note that
it sometimes **offers an option it then refuses** (Q25), and that the wording and option list
**differ on every attempt** for the same question — so clarification-derived results are not
reproducible. Cap at ~3 rounds; Q45 asked three times then returned nothing.

### Errors
Only `Exception was thrown by handler.` justifies the close-reopen-retry-×2-then-stop cycle.
Every other error is logged and the run continues. `REASON_LIMIT_EXCEEDED` is a hard account
gate — nothing succeeds until it resets, so stop rather than logging dozens of identical rows.

### Fresh chat per question
Reload before each question. Without it, answers reference earlier turns and model differences
become indistinguishable from context effects.

### The daily cap is the real scheduling constraint
`REASON_LIMIT_EXCEEDED` is **account-wide across all three models** (not per-model). It behaves
like a small rolling budget, not a clean daily counter: ~85 questions exhausted the account the
first time, then after it cleared it re-tripped after only ~16 more. It did **not** reset at UTC
midnight or US Eastern midnight (both observed still capped 5h+ after the first hit) — it clears
**overnight**, and in practice was clear again after ~06:00 local. Plan suites around this, or
get the cap raised before starting — a 130+ question suite cannot finish in one sitting.

**Resume protocol when capped:** arm a `/loop` (dynamic mode) that re-checks every ~20 min via
`ScheduleWakeup`, hold real testing until after 06:00 local, and `PushNotification` the user when
it actually resumes. Do not log dozens of identical capped rows while waiting.

---

## 6. Verification discipline

**Never trust the on-screen row count or the prose summary.** Parse the workbook. Across 10
exports the `Showing first N of M` label matched the file exactly — but the *contents* routinely
contradict the prose.

Reading xlsx without openpyxl: unzip, parse `xl/worksheets/sheet1.xml` + `xl/sharedStrings.xml`.
**Critical gotcha:** cells are sparse. You must map each `<c>` by its `r` attribute
(`"C7"` → column index) — iterating `<c>` positionally silently shifts every column and produces
convincing but wrong numbers. This caused a false "1085 duplicate rows" reading that had to be
retracted; the true figure was 2.

Check per export: row count vs claimed, presence/emptiness of the columns the question was
actually about, whether the org/date filter is visible at all, duplicate entity ids, and which
sensitive columns are populated.

---
## 7-8. Baseline figures and known defects

-> `reference/baseline-and-defects.md` for the verified baseline figures and the
catalogue of known contradictions. Check a new answer against it before filing:
a "new" defect that is already in the catalogue is a duplicate, and a figure
that disagrees with the baseline is the finding.

## 9. Reporting

File findings as subtasks via [[8-asana-bug-report]] on the Savance AI Reporting project. Repro
steps must start with navigate-to-test-server + login. Keep steps generic (say "any invalid
credentials", not the account you happened to use).

For a run summary, publish an Artifact — a scanned QA deliverable, so lead with the
contradiction that makes the problem undeniable, and state plainly which figures were read from
the workbooks versus taken from the screen.

### Multi-iteration runs
A full pass over both suites is ~260 questions and cannot finish before the cap trips, so runs
span days. Keep each iteration in its own folder (`ai-reporting-results/` for pass 1,
`ai-reporting-results/iteration2/` for pass 2) and **never delete or move an earlier
iteration's screenshots, exports or log** — the whole point is comparing runs for
non-determinism. Reuse iteration 1's clarification answers **verbatim** in later passes so any
difference is the model's, not the prompt's. Opus is deterministic to the row across days, so a
rote re-run of the adversarial refusals mostly re-confirms; the reporting questions (Q01-Q130),
where non-determinism is the story, are where a second iteration earns its cost. `RESUME.md`
holds the durable stop-point + standing directives so a capped run can be picked back up.

---

## 10. Where to continue (live run state)

The resume point is **not** hard-coded here — it lives in two files that are updated as the run
progresses. Read them first, in this order, before asking the user or re-running anything:

1. **`ai-reporting-results/RESUME.md`** — durable stop-point, standing directives, the agreed
   plan, and the exact `/loop` text to re-arm an interrupted run. This is the source of truth.
2. **`ai-reporting-results/run-log.tsv`** — the definitive record of what has actually completed.
   The **last numbered row** is the last question finished; resume at the next number.

Quick check to find the true resume point:

```sh
tail -1 ai-reporting-results/run-log.tsv | cut -f1   # last completed qNN -> resume at NN+1
```

**Snapshot as of 2026-08-26 (verify against the log, which always wins):**

| | |
|---|---|
| Iteration 1, `test-question.md` (Q01-Q130) | **complete** |
| Iteration 1, `test-question2.md` (Q131-Q262) | in progress — **last done Q138, resume at Q139** |
| Skipped (do not run) | **Q261, Q262** + any token-drain / quota-exhaustion item; **Q241** can't be entered (2000-word question exceeds the 200-char input cap) |
| Iteration 2 (all 262 → `ai-reporting-results/iteration2/`) | not started; begins only after iteration 1 finishes |

When the log and this table disagree, **the log is right** — this snapshot goes stale between
sessions; RESUME.md and the log do not.
