# One-Pager — Template Reference

Read this file after the doc type is determined to be **One-Pager**.
It contains the mapping rules, writing rules, self-review checklist, and document template for this type.

## Table of Contents
1. [Mapping Rules](#mapping-rules) — Step 2: Map & Augment
2. [Writing Rules](#writing-rules) — Step 3: Generate Document
3. [Self-Review Checklist](#self-review-checklist) — Step 3: Generate Document
4. [Document Template](#document-template) — Step 3: Generate Document

---

## Mapping Rules

Map outline content to document sections:

| Outline Content | → Document Section |
|---|---|
| Overview | **Problem** (2-3 sentences of what's broken/missing) |
| Winning approach | **Proposed Approach** (concise how) |
| Key trade-offs from Pros/Cons | **Key Decisions** (1-3 decisions with brief rationale) |
| Top risks from Open Questions | **Risks** (top 1-2 with mitigations) |
| Prerequisites with timing | **Timeline** (milestones) |

---

## Writing Rules

- **Tone:** Executive, action-oriented. Written for someone who has 5 minutes.
- **Total length: 1 page maximum.** Ruthlessly cut anything that doesn't directly serve the reader.
- **Problem** is 2-3 sentences. If the reader doesn't already feel the pain, the one-pager won't convince them.
- **Proposed Approach** is what you'll do, not how you'll do it. Save implementation details for a full design doc.
- **Key Decisions** are the 1-3 choices you've already made with brief rationale.
- **No open questions** — a one-pager is a recommendation, not a discussion. If there are unresolved questions, note them as risks.

---

## Self-Review Checklist

Run this checklist internally before writing the file. Auto-fix any failures.

- [ ] Problem is 2-3 sentences
- [ ] No open questions section (risks only)
- [ ] Total length fits on 1 page (under 500 words)
- [ ] Every sentence directly serves the reader

---

## Document Template

Use this structure for the generated document:

---

# [Title] — One-Pager

**Author:** [name] | **Date:** [date]
**Reviewers:** [names]

## Problem

[What's broken or missing, in 2-3 sentences.
The reader should feel the pain immediately.]

## Proposed Approach

[What you plan to do — the strategy, not the implementation.
Keep it high-level. 1-2 paragraphs max.]

## Key Decisions

1. **[Decision 1]** — [Brief rationale]
2. **[Decision 2]** — [Brief rationale]
3. **[Decision 3]** — [Brief rationale]

## Risks

| Risk | Mitigation |
|---|---|
| [Risk 1] | [Mitigation] |
| [Risk 2] | [Mitigation] |

## Timeline

| Milestone | Target Date |
|---|---|
| [Milestone 1] | [Date] |
| [Milestone 2] | [Date] |
