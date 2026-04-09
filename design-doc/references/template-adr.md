# ADR — Template Reference

Read this file after the doc type is determined to be **ADR (Architecture Decision Record)**.
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
| Overview | **Context** (condense to 1-2 paragraphs — the forces at play) |
| Winning approach from Key Thoughts | **Decision** — one clear "We will..." statement |
| Pros across all approaches | **Consequences: Positive** |
| Cons of chosen approach | **Consequences: Negative** |
| Other effects | **Consequences: Neutral** |

---

## Writing Rules

- **Tone:** Terse, decisive. Every word counts.
- **Total length: 1 page maximum.** If it's longer, cut aggressively.
- **Context** is 1-2 paragraphs describing the forces at play — technical, business, social.
- **Decision** is a single statement: "We will use [X] for [Y] because [Z]."
- **Consequences** must cover Positive, Negative, and Neutral effects. Be exhaustive about consequences even while being brief about context.
- **Status** field: Proposed (default), Accepted, Deprecated, or Superseded.

---

## Self-Review Checklist

Run this checklist internally before writing the file. Auto-fix any failures.

- [ ] Context is 1-2 paragraphs max
- [ ] Decision is a single "We will..." statement
- [ ] Consequences has Positive, Negative, AND Neutral subsections
- [ ] Total length fits on 1 page (under 500 words)
- [ ] Status field is present

---

## Document Template

Use this structure for the generated document:

---

# ADR-[number]: [Decision Title]

**Date:** [date] | **Status:** Proposed

## Context

[The forces at play — technical constraints, business requirements,
team capabilities, timeline pressures, and any other factors
influencing this decision. Keep to 1-2 paragraphs.]

## Decision

We will [specific decision in active voice].

[Optional: 1-2 sentences of key rationale.]

## Consequences

### Positive

- [What becomes easier or better]
- [New capabilities enabled]

### Negative

- [What becomes harder or worse]
- [New constraints introduced]
- [Technical debt incurred]

### Neutral

- [Effects that are neither clearly positive nor negative]
- [Changes to team workflow or processes]
