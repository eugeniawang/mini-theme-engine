---
title: Stage 3 contract, roll up themes across calls
created: 2026-10-15 16:58
last_updated: 2026-10-16 09:36
owner: the workflow author
status: active
---

# Stage 3: roll up themes across calls

**Input:** the stage 1 and stage 2 tables in `output/results.md`.

**Job:** group pain points that are the same underlying problem into themes, count them, and pick the best quote for each.

## How

1. Group by the underlying problem, not the wording. The test: put two pain points in one theme when one fix would remove both, or when they are the same objection to the product raised by different people (for example, two buyers who both say it costs too much). For example, in a restaurant, "the walk-in fridge keeps breaking" and "we threw out a week of stock" are one problem if both mean spoiled food, even though the words share nothing. Do not split a theme because buyers used different words or are at different stages.
2. A theme can hold one pain point. Every pain point belongs to exactly one theme.
3. Count pain points and count distinct calls.
4. Pick the best quote: the one that states the pain most concretely (a number, a loss, a feeling). Copy it exactly.
5. List the stages the theme's pain points carry. If one theme spans early and late stages, that is worth noticing, not fixing.

## Output

Under a heading `## Stage 3: themes` in `output/results.md`, sorted by pain point count, highest first:

| Theme | Pain points (IDs) | Count | Calls | Stages seen | Best quote |
|---|---|---|---|---|---|
| ... | P(n), P(n) | 2 | call-(n), call-(n) | (stages) | "..." |

Then write two lines under the table: the theme to act on first and why, and which awareness stage is most common across all pain points. If two or more stages tie, name all of them and their count.

## Definition of Done

Stage 3 is done only when every criterion below passes. Each one is a row in the evaluation matrix that `python3 scripts/qa.py stage3` prints, with PASS or FAIL and the detail.

| # | Criterion |
|---|---|
| S3-1 | The stage 3 table is under its heading. |
| S3-2 | Every pain point ID from stage 1 appears in exactly one theme. |
| S3-3 | Counts, calls and stages seen match the IDs listed. |
| S3-4 | Every best quote appears word for word in a transcript. |
| S3-5 | Themes are sorted by pain point count, highest first. |
| S3-6 | The two lines under the table are there: the theme to act on first, and the most common stage (all tied stages named). |

## Check and redo loop

1. Run `python3 scripts/qa.py stage3`. It prints the evaluation matrix, the failing rows, and an overall PASS or FAIL.
2. **PASS:** Go on to scoring (START-HERE.md, "After the run").
3. **FAIL (it says REDO 1 of 2 or REDO 2 of 2):** redo this stage using the failing rows it lists. Fix those rows against the transcript, rewrite the stage 3 table, and run the check again. Do not start the next stage.
4. **At most 2 redos.** If the check fails a third time, it says STOP and writes `output/qa-stop-stage3.md` with the failing rows. Stop the run there and show that file to the human. Never mark the stage done, skip the check, or carry on as if it passed.
5. **No Python?** Check each criterion above by hand, write the matrix yourself (criterion, PASS or FAIL, detail), and apply the same loop: at most 2 redos, then stop and report.
