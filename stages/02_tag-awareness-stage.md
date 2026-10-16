---
title: Stage 2 contract, tag each pain point with its awareness stage
created: 2026-10-15 16:58
last_updated: 2026-10-16 09:36
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

## Definition of Done

Stage 2 is done only when every criterion below passes. Each one is a row in the evaluation matrix that `python3 scripts/qa.py stage2` prints, with PASS or FAIL and the detail.

| # | Criterion |
|---|---|
| S2-1 | The stage 2 table is under its heading. |
| S2-2 | Every stage 1 row has exactly one stage, and no row is added. |
| S2-3 | Every stage is spelled as one of the five names above. |
| S2-4 | Every signal is the buyer's exact words from the same call. |
| S2-5 | Every "why" names a tie-break question (Q1 to Q4). |

## Check and redo loop

1. Run `python3 scripts/qa.py stage2`. It prints the evaluation matrix, the failing rows, and an overall PASS or FAIL.
2. **PASS:** Go on to stage 3.
3. **FAIL (it says REDO 1 of 2 or REDO 2 of 2):** redo this stage using the failing rows it lists. Fix those rows against the transcript, rewrite the stage 2 table, and run the check again. Do not start the next stage.
4. **At most 2 redos.** If the check fails a third time, it says STOP and writes `output/qa-stop-stage2.md` with the failing rows. Stop the run there and show that file to the human. Never mark the stage done, skip the check, or carry on as if it passed.
5. **No Python?** Check each criterion above by hand, write the matrix yourself (criterion, PASS or FAIL, detail), and apply the same loop: at most 2 redos, then stop and report.
