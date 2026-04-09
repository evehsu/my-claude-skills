# RFC — Template Reference

Read this file after the doc type is determined to be **RFC (Request for Comments)**.
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
| Overview | **Abstract** (one paragraph) |
| Key Thoughts on problem/motivation | **Motivation** — make it compelling |
| Key Thoughts on approach | **Detailed Design** |
| Implementation Approaches (rejected options) | **Alternatives** |
| Cons of the chosen approach | **Drawbacks** — be honest |
| Open Questions | **Unresolved Questions** |
| Sources & References | **References** |
| *Gap-fill needed* | **Implementation Plan** |

---

## Writing Rules

- **Tone:** Persuasive but balanced. You're making a case while honestly acknowledging weaknesses.
- **Motivation** must be compelling — lead with the pain point, quantify the impact if possible.
- **Drawbacks is mandatory and must be honest.** Do not soft-pedal. If the outline identified cons, state them directly. A good Drawbacks section builds credibility.
- **Alternatives** should explain why each was rejected, not just list them.
- **Implementation Plan** should include milestones, dependencies, and estimated effort.

---

## Self-Review Checklist

Run this checklist internally before writing the file. Auto-fix any failures.

- [ ] Abstract is one paragraph
- [ ] Motivation is compelling and leads with the pain point
- [ ] Drawbacks section is present, honest, and non-trivial
- [ ] Alternatives explain why each was rejected
- [ ] Unresolved Questions are listed
- [ ] Implementation Plan has milestones
- [ ] Length is 2-5 pages (roughly 1000-2500 words)

---

## Document Template

Use this structure for the generated document:

---

# RFC: [Title]

**Author:** [name] | **Date:** [date] | **Status:** Draft | In Review | Accepted | Implemented
**Reviewers:** [names]

## Abstract

[One paragraph summary of what is being proposed and why]

## Motivation

[Why this change is needed. Lead with the pain point.
Quantify the impact if possible. Make the reader feel the problem
before presenting the solution.]

## Detailed Design

[The proposal in full technical detail.
Include architecture, APIs, data models, and key implementation decisions.
Use code blocks and diagrams where they aid understanding.]

## Drawbacks

[Why should we NOT do this? Be honest and thorough.
Acknowledge complexity costs, migration burden, operational overhead,
learning curves, and any other downsides. A candid Drawbacks section
builds trust in the proposal.]

## Alternatives

[What other approaches were considered?
For each: what it is, why it was considered, and why it was rejected.
Don't dismiss alternatives superficially — give them a fair hearing.]

## Unresolved Questions

- [Question that must be answered before implementation]
- [Question that can be answered during implementation]

## Implementation Plan

| Milestone | Description | Estimated Effort |
|---|---|---|
| Phase 1 | [Description] | [Effort] |
| Phase 2 | [Description] | [Effort] |

## References

- [Source title](link)
