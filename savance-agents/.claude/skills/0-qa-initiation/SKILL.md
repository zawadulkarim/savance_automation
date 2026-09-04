---
name: 0-qa-initiation
description: Stage 00 — bootstrap a directory for QA: merge missing credentials (test server URL, username, password, Asana token) into .env without clobbering, install the Playwright MCP server, and prove both with one real login. Use for a fresh checkout or machine, when a stage fails for want of credentials or browser tooling, or on /0-qa-initiation.
---

# QA initiation

Stage 00 of the QA lifecycle. Everything downstream — requirement analysis,
spec docs, checklists, bug reports, sign-off — assumes two things are already
true: credentials live in a `.env` in the working directory, and the Playwright
MCP server is connected so the app can actually be driven. This skill makes
both true, then proves it.

It is **interactive**. It stops and waits for the user at Gate 1 (Step 3)
because it cannot invent a password. Run it in the main conversation thread,
not as a background subagent — a background agent has nobody to ask.

If everything is already in place, this skill is a no-op that says so in three
lines. That is the expected outcome on a machine that has been set up before,
and it is not a failure.

## Hard rules

1. **Never invent a credential.** Not a URL, not a username, not a password,
   not a token. If a value is missing and the user has not given it, the run
   stops at Gate 1 and waits. A plausible-looking guess written into `.env` is
   worse than no `.env` at all — it fails at login one stage later, far from
   the cause.
2. **Never overwrite the existing `.env`.** Merge into it.
   `scripts/env_manager.py` preserves every existing line, comment and blank
   line, updates a key in place if it is already present, and backs the file up
   before writing. Do not hand-roll this with `sed`, a `>` redirect, or the
   `Write` tool — a truncated `.env` costs the user credentials they may not
   have anywhere else.
3. **Mask secrets in everything you print.** Passwords and tokens never appear
   in full in your chat output, in a command you echo, or in a summary. The
   script's `check` and `merge` modes already emit masked values — quote those
   rather than reading the raw file and printing it. Never `cat` the env file.
4. **Pass secrets on stdin, never on the command line.** Argv lands in shell
   history and in the process list. The merge script takes JSON on stdin for
   exactly this reason.
5. **Verification is read-only.** The login check signs in, confirms it landed,
   and signs out. It does not change a status, save a setting, submit a form,
   or create anything. See the read-only posture in [[savance-workplace]].
6. **This skill sets up; it does not test.** When it is done, hand back. Do not
   drift into exploring the app, running a checklist, or filing anything.

## Step 0 — Establish where you are

Resolve the working directory (the project root the user invoked you from) and
state its absolute path. Everything below is relative to it. If the user named
a different directory, use that one and say which you picked.

The canonical env file is `.env` in that root. If a `.env.local`, `.env.qa` or
similar also exists, mention it but do not touch it — `.env` is the file the QA
stages read.

## Step 1 — Check what is already there

Run the check mode:

    python .claude/skills/0-qa-initiation/scripts/env_manager.py check --file .env

It prints JSON: which canonical keys are present (with masked values and the key
name they are actually stored under), and which are missing. Exit code 0 means
complete, 1 means something is missing.

The four canonical keys:

| Key | Secret | What it is |
| --- | --- | --- |
| `TEST_SERVER_URL` | no | Base URL of the QA instance, e.g. `https://test.savanceworkplace.com/` |
| `TEST_USERNAME` | no | Test account username |
| `TEST_PASSWORD` | yes | Test account password |
| `ASANA_ACCESS_TOKEN` | yes | Asana personal access token used by the Asana MCP server |

Aliases already in use in the wild count as satisfying a key — a pre-existing
lowercase `asana_token` **is** `ASANA_ACCESS_TOKEN`, and must not be duplicated
or re-prompted. The alias table lives in `SCHEMA` at the top of the script; read
it there rather than assuming.

If nothing is missing, skip Steps 2 and 3 entirely and go to Step 5. Say plainly
that the env file was already complete — do not re-ask "just to confirm", and do
not rewrite the file to no purpose.

## Step 2 — Prepare the prompt

For each missing key, work out whether you have a **defensible suggestion** to
offer, and label it as a suggestion rather than a fact:

- `TEST_SERVER_URL`, `TEST_USERNAME`, `TEST_PASSWORD` — if the project's domain
  skills record a test instance ([[savance-workplace]] documents
  `https://test.savanceworkplace.com/` and its test login), offer those as a
  one-tap default. They are still the user's to confirm.
- `ASANA_ACCESS_TOKEN` — if a token is already present under any alias, it is
  not missing. Only prompt when there is genuinely none.

Never present a suggestion as already-decided, and never fill one in on a
non-answer.

## Step 3 — Gate 1: ask the user

**Stop here and wait for a real reply.** Ask for every missing value in one
message, not one round trip per field. Where `AskUserQuestion` is available use
it — its free-text "Other" option carries the typed value; otherwise ask in
plain chat.

Two things the user should know once, briefly, before they type a password:

- It will be stored **in plain text** in `.env` in this directory.
- Whatever they type into the chat is in the conversation transcript.

For a QA/test environment the user controls, both are accepted practice on this
project — say it once, do not lecture, and do not refuse to proceed. If the
value they give is for a production system, stop and confirm before writing it.

If the user declines to supply something, or answers ambiguously, do not write
that key. Continue with the rest and report the gap at the end.

## Step 4 — Write the env file

Feed the collected pairs to the merge mode as JSON on stdin:

    echo '{"TEST_SERVER_URL":"...","TEST_USERNAME":"...","TEST_PASSWORD":"..."}' | python .claude/skills/0-qa-initiation/scripts/env_manager.py merge --file .env

The script reports what it created, updated and added, and where it put the
backup. Quote its masked summary; do not read the file back and print it.

Then, only if the root is a git repository (`git rev-parse --git-dir` succeeds),
make sure `.env` is ignored — append it to `.gitignore` if it is not already
covered, and say you did. In a non-repo directory, skip this silently; there is
nothing to protect against.

## Step 5 — Install the Playwright MCP server

Check first:

    claude mcp list

If a `playwright` entry is present and shows **Connected**, it is installed —
report that and move on. Do not reinstall it, and do not "refresh" it.

If it is absent, add it at project scope:

    claude mcp add playwright -- npx -y @playwright/mcp@latest

Then make sure the browser binary it drives is actually present:

    npx -y playwright install chromium

That download is large and slow on a cold machine. Run it in the background and
tell the user it is running, rather than blocking the session on it.

**A newly added MCP server is not live in the session that added it.** The
`mcp__playwright__*` tools appear only after the session restarts. If you just
added it, say so explicitly, tell the user to restart Claude Code, and note that
Step 6's login check is deferred until they do — then run Step 6 as the first
thing on the next invocation. Do not claim the server works because the `add`
command exited 0; that only proves the config was written.

## Step 6 — Verify

Two checks, in order. If the MCP server was only just added and the session has
not restarted, skip to the report and say the verification is pending. Do not
fake it.

**MCP handshake.** `claude mcp list` shows `playwright` as Connected.

**Live login.** Using the values now in `.env`:

1. `browser_navigate` to `TEST_SERVER_URL`.
2. `browser_snapshot` to find the login form.
3. `browser_fill_form` with `TEST_USERNAME` / `TEST_PASSWORD`, then click the
   log-in control.
4. `browser_snapshot` again. Success is landing on the authenticated landing
   page — for Savance Workplace, `Default.aspx` with the status board and the
   top nav. Still sitting on `Login.aspx`, or an error banner, is a failure.
5. Sign out, then `browser_close`.

Touch nothing else. This is a credential check, not an exploration.

If login fails, do not immediately re-prompt for the password. First distinguish
*wrong credential* (an error message on the login page) from *unreachable
server* (navigation timeout, DNS failure, certificate interstitial) from *locked
account*. Report which one you saw, and offer to re-run Step 3 for just the
field that looks wrong.

## Step 7 — Report

Close with a short status block:

- The env file path, whether it was created or merged, the backup path if one
  was written, and which keys are now present — **masked**.
- Any key still missing, and why.
- Playwright MCP: already present, or added now — and whether the session needs
  a restart before the tools are usable.
- Verification result: MCP connected yes/no, login succeeded yes/no, and what
  the failure was if it failed.
- The next stage the user can now run.

## What this skill does not do

- It does not install or configure the Asana MCP server. It stores the token;
  wiring the server up is a separate job.
- It does not test the application, explore it, or produce any QA artifact.
- It does not touch Asana at all.
- It does not manage credentials for any environment other than the one the user
  names — one env file, one test server.
