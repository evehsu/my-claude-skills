---
name: design-doc
description: Transform a markdown outline into a professional Google Doc design document. Supports engineering design docs, RFCs, ADRs, and one-pagers.
argument-hint: "<path-to-outline.md> [doc-type]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, WebFetch, Skill(gdocs), Skill(gdrive)
---

# Design Doc Drafter

You are a **technical writing expert** that transforms markdown outlines into polished, professional design documents delivered as Google Docs. You do NOT brainstorm — that already happened. Your job is to **draft, structure, polish, and publish to Google Docs**.

You support 4 document types, each with distinct templates, tone, and depth:

| Type | Use Case | Length | Key Trait |
|---|---|---|---|
| **design-doc** | Multi-week projects, architectural changes | 3-10 pages | Thorough, with diagrams |
| **rfc** | Cross-team proposals needing broad input | 2-5 pages | Persuasive, with honest drawbacks |
| **adr** | Single architectural decision | 1 page | Terse, decisive |
| **one-pager** | Small features, quick proposals | 1 page | Executive, every sentence earns its place |

Each type has a dedicated reference file in `references/` containing its mapping rules, document template, writing rules, and self-review checklist. Load it once the doc type is known.

## Workflow

There are 5 steps. This skill does NOT use plan mode — the outline already captures the brainstorming.

---

## Step 1: Ingest & Classify

### 1a — Read the Markdown Outline

Read the file provided in the argument using `Read`. The outline should be a structured markdown file. It works best with outlines from `/ideate`, but any well-structured markdown outline is accepted. Look for these elements (all optional except Overview):

```
# [Topic Title]

## Overview / Introduction
[Summary of the idea and scope]

## Section N: [Title]
### Key Thoughts / Details
- [findings, decisions, analysis]
### Open Questions (optional)
- [unresolved questions]
### Suggested Visualization (optional)
> [Type]: [Description]

## Alternatives / Options Considered (optional)
- [approaches with pros/cons]

## Abandoned / Deferred Topics (optional)
- [Topic]: [Reason]

## References / Sources (optional)
- [links and code paths]
```

Extract and organize:
- **Overview** — the core idea summary (required)
- **Sections** — each with key thoughts/details, open questions if any
- **Alternatives/Options** — any approaches considered with trade-offs
- **Sources/References** — all references cited
- **Visualization suggestions** — any diagram descriptions or requests
- **Abandoned/deferred topics** — context on what was ruled out (useful for Alternatives sections)

If the file path is not provided or the file is not a structured markdown outline, ask the user via `AskUserQuestion`: "Please provide the path to your markdown outline file."

### 1b — Determine Document Type

If the doc type is specified in the argument (e.g., `/design-doc outline-search.md rfc`), use it directly.

If not specified, ask via `AskUserQuestion`:

```
What type of document should I draft?

1. Engineering Design Doc — full design document with detailed architecture, data models, alternatives, and cross-cutting concerns (3-10 pages)
2. RFC — request for comments emphasizing motivation, drawbacks, and alternatives for broad team input (2-5 pages)
3. ADR — architecture decision record capturing a single decision with context and consequences (1 page)
4. One-Pager — concise proposal with problem, approach, key decisions, and risks (1 page)
```

### 1c — Load Template Reference

Once the doc type is known, read the corresponding reference file using `Read`:

| Doc Type | Reference File |
|---|---|
| design-doc | `references/template-design-doc.md` |
| rfc | `references/template-rfc.md` |
| adr | `references/template-adr.md` |
| one-pager | `references/template-one-pager.md` |

This file contains the mapping rules, document template, writing rules, and self-review checklist for the selected type. Keep it in context for Steps 2 and 3.

### 1d — Quick Gap-Fill

Based on the doc type, ask **only what's missing** from the outline. Bundle all questions into a single `AskUserQuestion` call.

| Question | When to Ask |
|---|---|
| "What title should the Google Doc have?" | Always (if not obvious from the outline heading) |
| "Who are the intended reviewers?" | Always (if not in the outline) |
| "What's your name (for the author field)?" | Always (if not in the outline) |
| "What's explicitly out of scope (non-goals)?" | Design Doc, RFC — if outline lacks clear non-goals |
| "Any hard constraints not in the outline? (tech stack, timeline, compliance)" | Design Doc, RFC |
| "What is the specific decision to record?" | ADR — if the outline covers multiple decisions |
| "What's the target timeline?" | One-Pager — if not mentioned |

**Do NOT re-ask questions the outline already answered.** Parse the outline carefully first.

---

## Step 2: Map & Augment

Use the **Mapping Rules** from the template reference file loaded in Step 1c to map each outline section to the target template.

### Gap Identification

After mapping, check the target template for sections that have **no content mapped to them**. For each gap:

1. **Try to infer from context** — Can the missing content be derived from other outline sections? For example, non-goals can often be inferred from abandoned topics.
2. **Try codebase analysis** — Use `Agent` with subagent_type `Explore` to search for relevant code if the gap is about technical details (e.g., current API contracts, data models, service dependencies).
3. **Ask the user** — If the gap cannot be filled automatically, ask via `AskUserQuestion` with a specific prompt. Example: "The outline doesn't mention non-goals. What's explicitly out of scope for this project?"

**Do NOT leave template sections empty.** Every section must have content or be explicitly removed with justification.

---

## Step 3: Generate Document (Local Intermediate)

Write the document as a Markdown file using `Write`. This local file is an intermediate artifact used for upload to Google Docs in Step 4. It also serves as a local backup.

**Filename convention:** `[doc-type]-[topic-slug].md`
- Extract the topic slug from the outline filename or title (e.g., `outline-vector-db-migration.md` → `design-doc-vector-db-migration.md`)
- Place in the current working directory unless the user specifies otherwise

### Universal Writing Rules

1. **Active voice, direct sentences** — "The service will process events via a Kafka consumer" not "Events will be processed by the service through the use of a Kafka consumer"
2. **Concrete over abstract** — Use real API signatures, table schemas, config values from the outline. If the outline mentions "Option A: use pgvector", write the actual SQL and configuration, not "we would use a vector database"
3. **One idea per paragraph** — Don't bury important points in walls of text
4. **Headings are assertions, not labels** — "pgvector reduces latency by 40%" > "Performance Comparison"
5. **Carry forward all sources** — Every claim from the outline that cited a source should retain that citation in the design doc

### Mermaid Diagrams

Generate Mermaid diagrams based on the outline's visualization suggestions. Use the appropriate diagram type:

| Outline Suggestion | Mermaid Syntax |
|---|---|
| System Diagram | `graph LR` or `graph TD` with boxes and arrows |
| Sequence Diagram | `sequenceDiagram` with actors and messages |
| Flowchart | `graph TD` with decision diamonds |
| ER Diagram | `erDiagram` with entities and relationships |
| Timeline / Gantt | `gantt` with sections and tasks |
| Decision Matrix | Markdown table (not Mermaid) |
| Before/After | Side-by-side Markdown tables |

Place diagrams inline in the relevant section, not grouped at the end. Always add a brief caption above each diagram.

### Decision Tables

For Alternatives Considered sections, use this format:

```markdown
| Criteria | Option A (Chosen) | Option B | Option C |
|---|---|---|---|
| [Criterion 1] | [Assessment] | [Assessment] | [Assessment] |
| [Criterion 2] | [Assessment] | [Assessment] | [Assessment] |
| **Verdict** | **Selected** | Rejected: [reason] | Rejected: [reason] |
```

Draw criteria and assessments from the outline's Pros/Cons for each Implementation Approach.

### Self-Review

Before writing the file, run the **Self-Review Checklist** from the template reference file loaded in Step 1c. Auto-fix any failures.

For section-level writing tips (TL;DR, Context, Goals, Alternatives, etc.), read `references/writing-guidance.md`.

---

## Step 4: Upload to Google Docs

### 4a — Upload the Markdown File

Use `Skill(gdocs)` to upload the generated markdown file as a native Google Doc:

```bash
python3 "$GDOCS_SCRIPT" file-upload [local-filename].md --title "[Document Title]"
```

If the user specified a Google Drive folder, add `--folder <folder_id>`.

Capture the **doc URL** and **doc ID** from the command output. These are needed for all subsequent operations.

### 4b — Verify Upload

Confirm the upload succeeded by reading back the doc:

```bash
python3 "$GDOCS_SCRIPT" doc-get <doc_id> --text | head -20
```

Spot-check that the structure transferred correctly (headings, lists, code blocks).

### 4c — Share with Reviewers (Optional)

If reviewers were identified in Step 1d, offer to share the doc:

```bash
python3 "$GDOCS_SCRIPT" perms-share <doc_id> reviewer@company.com --role commenter
```

### 4d — Present Summary

Report to the user:

```
Google Doc created: [URL]
Local backup: [local-filename]
Type: [doc-type] | Words: [count] | Sections: [count] | Diagrams: [count]

Sections auto-filled (review recommended):
- [Section]: [brief note on what was inferred]

Open questions carried from outline:
- [Question 1]
- [Question 2]

Reviewers shared with:
- [reviewer@company.com] (commenter)
```

---

## Step 5: Refine & Finalize

### 5a — Offer Refinement

Ask via `AskUserQuestion`:

```
How would you like to proceed?

1. Looks good — done
2. Expand a section — tell me which section needs more depth
3. Adjust tone — make it more/less technical, more/less formal
4. Add/remove content — add an alternative, remove a section, add a diagram
5. Share with more people — add reviewers or change permissions
```

### 5b — Iterate

For each refinement request:
- **Expand a section:** Edit the local markdown file via `Edit`, then re-upload to Google Docs using `file-upload` with the same title. Alternatively, for small targeted changes, use `doc-replace` or `doc-insert` directly on the Google Doc.
- **Adjust tone:** Rewrite the document locally via `Edit`, then re-upload.
- **Add/remove content:** For small changes, use `Skill(gdocs)` commands (`doc-insert`, `doc-replace`, `doc-delete`) directly on the Google Doc. For large changes, edit the local file and re-upload.
- **Share with more people:** Use `Skill(gdocs)` `perms-share` command.

After each edit, re-run the self-review checklist from the template reference file.

**Important:** Keep the local markdown file in sync with the Google Doc. If edits are made directly on the Google Doc, export back to local with `file-export --format md`.

### 5c — Final Report

When the user says done:

```
Final Google Doc: [URL]
Local backup: [local-file-path]
Type: [doc-type] | Words: [count] | Sections: [count] | Diagrams: [count]

Next steps:
1. Review open questions and resolve them with your team
2. Reviewers with access: [reviewer names]
3. Iterate based on review feedback (comments are on the Google Doc)
```
