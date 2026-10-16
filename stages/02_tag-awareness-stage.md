---
title: Stage 2 contract, tag each pain point with its awareness stage
created: 2026-10-15 16:58
last_updated: 2026-10-15 17:15
owner: the workflow author
status: active
---

# Stage 2: tag each pain point with its awareness stage

**Input:** the stage 1 table in `output/results.md`, the transcripts, and `awareness-framework.md`.

**Job:** give each pain point exactly one of five stages: Unaware, Problem aware, Solution aware, Product aware, Most aware.

## How

1. Read `awareness-framework.md` in full before tagging anything.
2. For each pain point, reread the buyer's lines about that pain in the transcript, including the lines just before and after the quote.
3. Run the four tie-break questions from the framework, in order, and stop at the first "no".
4. Tag what the buyer **knew coming into the call**. A buyer's surprise after the seller explains something confirms they started earlier; it does not move them forward. Knowledge from before the call (a demo, a trial, a feature they use) counts, even if the seller repeats it during the call.
5. Write the signal: the buyer's exact words that decided the stage. These may differ from the stage 1 quote.

## Output

Under a heading `## Stage 2: awareness stages` in `output/results.md`:

| ID | Pain point | Stage | Signal (exact buyer words) | Why (one line, name the tie-break question that decided it) |
|---|---|---|---|---|
| P1 | ... | (one of the five stages) | "..." | Q(n): (the answer that decided it) |

## Definition of done

- Every stage 1 row has exactly one stage, spelled as one of the five names above.
- Every signal is the buyer's exact words from the same call.
- Every "why" names a tie-break question (Q1 to Q4).
