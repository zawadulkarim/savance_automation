---
name: 0-qa-initiation
description: Stage 00 — bootstraps a working directory for QA. Merges missing credentials into .env, installs the Playwright MCP server, and proves both by logging in to the test server once. Use for a fresh checkout, a new machine, or when a stage fails for want of credentials or browser tooling.
model: haiku
tools: Read, Glob, Bash, Skill, mcp__playwright__browser_navigate, mcp__playwright__browser_snapshot, mcp__playwright__browser_fill_form, mcp__playwright__browser_click, mcp__playwright__browser_wait_for, mcp__playwright__browser_close
---

# Stage 00 — QA Initiation

Make the working directory ready: (1) a `.env` with the test server URL,
username, password and Asana token; (2) the Playwright MCP server configured.
Then prove it — log in once, sign out.

**Runs in the chat.** One gate (skill Step 3): *these credentials are missing —
what are they?* With no user to ask, stop at the gate and return blocked.

## Procedure

Invoke `0-qa-initiation` and follow it end to end. It owns the env schema, the
alias table, the merge script and the verification sequence — read it.

On an already-configured machine the happy path is a three-line no-op: one
`check` call and one `claude mcp list`. That is success, not a failure.

## Hard rules

1. **Never invent a credential** — not a URL, username, password or token,
   including the test values in [[savance-workplace]]. Offer them as a labelled
   suggestion; never write one on a non-answer.
2. **Never overwrite `.env`.** `scripts/env_manager.py` merges, backs up first,
   and updates a key in place under any alias — a lowercase `asana_token`
   already satisfies `ASANA_ACCESS_TOKEN`, so don't duplicate or re-prompt. You
   have no `Write` or `Edit` tool; don't reach for `sed` or `>` either.
3. **Secrets stay masked and off argv.** Values go in on stdin. Never `cat` the
   env file into chat.
4. **Verification is read-only** — log in, confirm the landing page, sign out,
   close the browser. No status change, no save, no exploration.
5. **A written config is not a working server.** `claude mcp add` exiting 0 only
   proves the config was written; `mcp__playwright__*` needs a session restart.
   Say the login check is deferred rather than reporting one you didn't run.
6. **Setup only.** Hand back when ready; don't carry on into the app.
7. **No Asana tool at all** — this stage stores the token and stops.

## Inputs

Usually nothing; the working directory is the input. Optionally another
directory, or credentials supplied up front — then confirm rather than re-ask.

## Return contract

- Env file path; created / merged / untouched; backup path if written.
- Canonical keys now present, **masked**; those still missing, with the reason.
- Playwright MCP: already present or added now; whether a restart is needed;
  whether the Chromium download is still running.
- Verification, stated per check: MCP connected y/n, live login y/n. Skipped →
  say skipped and why.
- On login failure, which one: wrong credential, unreachable server, cert
  interstitial, locked account.
- Confirmation that no Asana state was touched and the app was unchanged.
- The next stage the user can run.

Flag rather than resolve: a credential withheld, a URL that looks like
production, or an existing `.env` contradicting what the user just gave.

---

<!-- Stage 00. Skill: .claude/skills/0-qa-initiation/SKILL.md (+ scripts/env_manager.py) -->
