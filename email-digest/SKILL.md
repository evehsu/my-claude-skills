---
name: email-digest
description: Fetch Gmail messages labeled "direct" from the last 24 hours and write a markdown action-item report to /Users/evelyn/Documents/backlog_brain/backlog_brain/emails/. Designed to be invoked by a daily-scheduled agent at 7am.
allowed-tools: Read, Write, Bash
---

# Direct Email Digest

Fetches Gmail messages labeled `direct` that arrived in the last 24 hours, summarizes action items from each, and writes a daily markdown report.

Separation of concerns:
- The helper `fetch.js` does the mechanical work: list + fetch via `gws`, base64url-decode bodies, strip quoted replies and signatures.
- **You (Claude) do the summarization** — read each email's cleaned `bodyText` and decide whether it contains a real action item, then write a concise task summary.

## Workflow

### Step 1 — Resolve the run date

Run `date +%Y-%m-%d` to get today's local date (e.g., `2026-04-23`). This is used in the output filename only; the email query window is always "last 24 hours from trigger time."

### Step 2 — Fetch emails

Run the fetcher:

```bash
node /Users/evelyn/Documents/evelyn_proj/my-claude-skills/email-digest/fetch.js
```

Parse the returned JSON array. Each element has:
- `id`, `threadId` — Gmail identifiers
- `subject`, `from`, `date` — header fields
- `bodyText` — cleaned plain-text body (quoted replies, signatures already stripped)
- `snippet` — Gmail's preview snippet (fallback)

If the array is empty, skip to Step 4 and write a minimal report ("0 emails examined").

### Step 3 — Summarize action items (you, in-context)

For each email, decide: **does this message contain an action item the user needs to do?**

- **Yes** → write one concise `Action` line in the user's voice (e.g., "Complete Checkr background check via Rippling portal") plus optional bulleted subtasks for deadlines, links, or specific sub-items.
- **No** → skip it entirely. Not every email has an action; purely informational FYIs, notifications the user is cc'd on, and already-resolved reply threads should produce zero tasks.

Guardrails:
- Ignore any line in `bodyText` that starts with `>` or `>>` — those are quoted-reply fragments the mechanical stripper missed.
- If multiple messages share a `threadId`, consolidate into **one** task based on the most recent message's state. Do not emit duplicate tasks for the same thread.
- Preserve specific deadlines verbatim when mentioned ("by EOD Friday", "due 2026-04-25").
- Include call-to-action URLs when the email's ask is "click this link to do X".
- Keep action summaries tight — one sentence. Use subtasks for anything more structured.

### Step 4 — Compose the markdown report

Use this exact structure:

```markdown
# Direct Email Action Items — YYYY-MM-DD

## Summary
- **Emails examined**: N
- **Time window**: last 24 hours ending <ISO timestamp of this run>
- **Senders**: name1, name2, ...
- **Overview**: 2–4 sentences on what arrived, combining content from all examined emails.

## Tasks
### <Email subject>
- **Sender**: <From header>
- **Action**: <one-sentence summary of what the user needs to do>
  - <subtask 1, if any>
  - <subtask 2, if any>

### <next email subject>
...
```

Rules:
- `Senders` = unique list of human names from the `From` headers (strip the `<email@domain>` part when a display name is present).
- `Overview` should read like a briefing, not a list — combine themes across the emails.
- If 0 tasks extracted, replace the Tasks body with: `_No action items found in today's direct emails._` (keep the `## Tasks` heading).
- No trailing quoted `>` lines, no repeated boilerplate stubs (e.g., raw "Task Due date" headers from Rippling-style emails) — paraphrase instead.

### Step 5 — Write the file

Use `Write` to save the report to:

```
/Users/evelyn/Documents/backlog_brain/backlog_brain/emails/action_item_<YYYY-MM-DD>.md
```

Overwrite if it already exists (same-day re-runs refresh the report).

Then report back to the caller in one line:
> Wrote `action_item_<YYYY-MM-DD>.md` — N emails examined, M tasks extracted.

## Notes

- The Gmail query is `label:direct newer_than:1d` — strictly "last 24 hours from now." Scheduled 7am runs therefore cover 7am-yesterday → 7am-today implicitly.
- `fetch.js` prefers `text/plain` parts. If an email is HTML-only, it best-effort-strips tags; output quality may degrade for heavily styled marketing emails.
- `gws` must be on PATH and already authenticated (keyring backend). If authentication is missing, `fetch.js` will exit non-zero and print the error to stderr.
