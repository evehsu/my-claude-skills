---
name: web-search
description: Research a topic via web search and produce a Markdown report with 5–10 results plus locally archived source pages (raw HTML/PDF). Prioritizes top AI org sources for AI/IT topics. Default output directory is /Users/evelyn/Documents/backlog_brain/backlog_brain/wiki/web-search-result/{topic-slug}/.
argument-hint: "<topic query> [reference-url] [output-dir]"
allowed-tools: Read, Write, Bash, WebSearch, WebFetch, AskUserQuestion
---

# Web Search Report

You research a user-given topic on the open web and produce a Markdown report with 5–10 well-chosen results. You also archive each source as raw HTML or PDF alongside the report so the user can re-read offline.

Separation of concerns:
- The helper `fetch.sh` does the mechanical work: HEAD-probe the URL's `Content-Type`, pick a `.html`/`.pdf` extension, and `curl` the raw bytes.
- **You (Claude) do the search, ranking, and writing** — choose what to search for, filter candidates, write the summaries, and compose the report.

## Workflow

There are 5 steps. This skill does NOT use plan mode.

---

## Step 1 — Parse argument & slugify

Parse the full argument string into:
- **Topic phrase** — the subject of research (required; may span multiple words).
- **Description** — any additional framing the user supplied.
- **Reference URL(s)** — anything matching `https?://` is treated as an attached link, not part of the topic text.
- **Output-dir override** — a non-URL token that looks like an absolute path (starts with `/` and is not a URL).

### 1a — Ambiguity check

If — and only if — the topic is genuinely ambiguous (e.g., a single bare keyword with no description AND no attached URL), bundle 1–2 clarifying questions into a single `AskUserQuestion` call (typical questions: intended angle, timeframe, audience). **Skip clarification for clear queries.** Err on the side of not asking.

### 1b — Slugify

Derive `TOPIC_SLUG`:
1. Lowercase the topic phrase.
2. Replace every run of non-alphanumeric characters with a single `-`.
3. Trim leading/trailing `-`.
4. Truncate to 60 characters (cut at the nearest `-` boundary).

Example: `"Mixture of Experts (MoE) training"` → `mixture-of-experts-moe-training`.

### 1c — Resolve output directory

- If the user provided an output-dir token, use it verbatim.
- Otherwise: `OUTPUT_DIR=/Users/evelyn/Documents/backlog_brain/backlog_brain/wiki/web-search-result/${TOPIC_SLUG}/`

Create it:

```bash
mkdir -p "$OUTPUT_DIR"
```

---

## Step 2 — Classify domain

Decide whether the topic is **AI/IT-related**. Match against indicative keywords, including (non-exhaustive):

> ai, ml, llm, agent, agentic, neural, transformer, attention, diffusion, rag, retrieval, embedding, fine-tun*, pre-train*, inference, gpu, tpu, distributed training, mixture of experts, moe, alignment, rlhf, reasoning, multimodal, vision, speech, nlp, mlops, kubernetes, docker, vector db, observability, compiler, database, distributed systems, os kernel

If the topic is AI/IT, keep the **Prioritized AI/IT source allowlist** (below) in context for Step 4's ranking boost. Otherwise, no special prioritization.

**Prioritized AI/IT source allowlist:**
- `openai.com`, `anthropic.com`, `x.ai`, `deepmind.google`, `deepmind.com`
- `research.google`, `blog.google` (AI sections), `ai.google.dev`
- `microsoft.com/research`, `blogs.microsoft.com` (AI), `research.microsoft.com`
- `salesforce.com/blog`, `research.salesforce.com`
- `ai.meta.com`, `huggingface.co`, `nvidia.com` (blogs/research)
- `arxiv.org` (papers), `cohere.com`, `mistral.ai`

---

## Step 3 — Seed context from attached link (if any)

If the user attached one or more URLs in Step 1:

1. `WebFetch` each attached URL with a prompt like: "Extract the main thesis, author/organization, publication date if visible, and 3 key claims."
2. Use what you learn to steer Step 4's search queries (pick up jargon, adjacent concepts, named approaches).
3. **Reserve the attached URL as one of the final results.** Do not re-search for it in Step 4.

If no URL is attached, skip this step.

---

## Step 4 — Web search, rank, select

### 4a — Query

Issue 2–3 `WebSearch` queries:
1. The raw topic phrase.
2. The topic plus a recency modifier (`2025`, `2026`).
3. One angle-refined variant (using jargon discovered in Step 3 if applicable, or a narrower sub-aspect otherwise).

### 4b — Filter and rank

Collect all candidates and apply these filters in order:

| Filter | Rule |
|---|---|
| Dedupe | Same URL appears once. Near-duplicate URLs on the same domain (`?utm=` variants, mobile mirrors) keep only the canonical one. |
| Noise | Drop listicles, content farms, SEO-only pages, auto-generated wrapper sites, and pure aggregator reposts. |
| Recency | Prefer work from the last ~18 months, unless the topic is inherently historical. |
| Primary sources | Prefer official blog posts, papers, and documentation over aggregators (Medium, LinkedIn reposts, news round-ups). |
| Per-domain cap | At most 2 results from the same domain. |
| AI/IT boost | If Step 2 flagged AI/IT, boost candidates whose domain is on the Prioritized AI/IT source allowlist. |

### 4c — Select

Select **5–10 final results**. Include the attached-link result from Step 3 (if any) as one of them. Aim for a mix of primary sources (official blogs, papers, docs) rather than all from one type.

---

## Step 5 — Archive + compose report

### 5a — Archive each result

For each selected result, indexed from `01`:

1. Build a per-result slug from the result's title using the same slugify rules as Step 1b, truncated to 40 characters.
2. Run the helper:

   ```bash
   bash /Users/evelyn/Documents/evelyn_proj/my-claude-skills/web-search/fetch.sh "<url>" "$OUTPUT_DIR/result-NN-<slug>"
   ```

   The script prints the final filename (with `.html` or `.pdf`). Capture it.
3. Run a brief `WebFetch` on the URL with a prompt like: "In 2–4 sentences, describe what this piece is about, its main claim/contribution, and why it's relevant to `<TOPIC>`." This readable summary will go into the report (the raw archive may be JS-heavy or paywalled).
4. If `fetch.sh` fails or returns non-zero, continue — include the result in the report but mark `_archive unavailable_` in place of the archived-file link.

### 5b — Compose the report

Use `Write` to save the report to `${OUTPUT_DIR}/summary.md` with this exact structure:

```markdown
# Web Search Report — {Topic Title}

_Generated: YYYY-MM-DD | {N} results_

## Summary

3–5 sentences describing the overall landscape: WHO (organizations, authors) is proposing WHAT (idea, solution, approach), where the field is converging or diverging, and what stands out. Reference results by number, e.g., "[1], [3]".

## Index

1. [Result title](https://...) — [result-01-<slug>.html](./result-01-<slug>.html)
2. [Result title](https://...) — [result-02-<slug>.pdf](./result-02-<slug>.pdf)
...

## Results

### 1. [Result title](https://...)
**Source**: {org or domain} | **Published**: {date if known, else `unknown`} | **Archived**: [result-01-<slug>.html](./result-01-<slug>.html)

2–4 sentence story summary of what the piece is about, its main claim/contribution, and why it's relevant to the topic.

### 2. [Result title](https://...)
...
```

Rules:
- **Title is a clickable external link** (to the original URL).
- **Archived field is a clickable local link** (relative path to the file `fetch.sh` produced). If archive failed, write `_archive unavailable_` instead.
- Use today's date (run `date +%Y-%m-%d` via Bash) in the `_Generated:_` line.
- Topic Title = human-readable rewrite of the topic phrase (title case, no slug dashes).
- Use Markdown hyperlinks, not raw URLs.

### 5c — Report back

Print one line to the caller:

> Wrote `summary.md` to `{OUTPUT_DIR}` — {N} results, {M} archived files.

Where `M` is the count of successful `fetch.sh` downloads (may be less than `N` if some archives failed).

---

## Notes

- `fetch.sh` sets a Mozilla User-Agent and a 60-second timeout. JavaScript-rendered pages will still save the raw HTML (which may be mostly a script bootstrap); the readable summary in the report comes from `WebFetch`, so the report stays useful even when the archive is bare.
- The skill does not re-fetch if `summary.md` already exists — it overwrites. Archive filenames with the same slug will be overwritten too.
- If `WebSearch` returns fewer than 5 usable candidates after filtering, return what you have (with a note in the Summary section) rather than padding with low-quality results.
