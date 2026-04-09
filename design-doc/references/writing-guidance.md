# Writing Guidance Per Section

Reference this file during Step 3 (Generate Document) for section-level writing tips.
These apply across all document types unless otherwise noted.

---

## TL;DR / Abstract
- **Do:** State what, why, and how in 2-3 sentences
- **Don't:** Include caveats, disclaimers, or hedge words
- **Test:** Could someone skip the rest and still understand the core proposal?

## Context & Motivation
- **Do:** Start with the problem, not the solution. Reference metrics, incidents, or user pain.
- **Don't:** Repeat information the audience already knows. Write for the least-informed reviewer.
- **Test:** Does this make the reader care about solving the problem?

## Goals & Non-Goals
- **Do:** Make goals measurable ("reduce latency below 100ms" not "improve performance")
- **Don't:** List activities as goals ("build a new service" is an approach, not a goal)
- **Non-goals test:** Would a reasonable person think this is in scope? If yes, it needs to be in Non-Goals.

## Proposed Design
- **Do:** Be specific enough that another engineer could start implementing
- **Don't:** Describe the obvious. Focus on the novel, non-trivial, or controversial parts.
- **Test:** Are there any "it depends" or "TBD" phrases? Replace them with concrete decisions or move to Open Questions.

## Alternatives Considered
- **Do:** Give each alternative a fair hearing. Explain the real trade-offs.
- **Don't:** Set up straw men. If an alternative wasn't seriously considered, don't include it.
- **Test:** Would a proponent of Option B feel their approach was fairly represented?

## Drawbacks (RFC)
- **Do:** Be your own harshest critic. Acknowledge every real downside.
- **Don't:** Immediately counter each drawback ("but this is mitigated by..."). State the drawback first, mitigations separately.
- **Test:** If you were arguing against this proposal, what would you say? Put that here.

## Consequences (ADR)
- **Do:** Be exhaustive. Think about code, team, process, users, and operations.
- **Don't:** Only list positive consequences. The negative and neutral ones are the most valuable.

## Open Questions
- **Do:** Distinguish between "must answer before starting" and "can answer during implementation"
- **Don't:** Use open questions to hide decisions you haven't made. If it's a decision, make it or explain what's blocking it.
