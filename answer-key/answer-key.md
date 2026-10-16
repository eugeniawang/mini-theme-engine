---
title: Answer key for the four sample transcripts (open only after the run)
created: 2026-10-15 16:58
last_updated: 2026-10-16 09:30
owner: the workflow author
status: active
---

# Answer key

**Stop.** If you have not finished all three stages and written `output/results.md`, close this file now.

This key sits in a public repository, so the test is open-book: it only tells you something if you run first and compare after. `python3 scripts/qa.py all --answer-key` scores a finished run against this key automatically.

The four sample calls contain 12 planted pain points. Each is listed with an anchor phrase: a run's row matches a planted pain if its quote comes from the same buyer turn (the same paragraph of speech) that contains the anchor phrase. If one turn holds two planted pains, match the row by what its pain point describes.

## Planted pain points

| Key | Call | Buyer | Pain | Anchor phrase | Correct stage | Why |
|---|---|---|---|---|---|---|
| K1 | call-1 | Dana | Saturday no-shows leave a chair empty | "just not turn up" | Solution aware | Names a type of fix ("those apps that text people a reminder"), has not picked one, does not connect it to Kettlebook (Q3). |
| K2 | call-1 | Dana | Booking back-and-forth by text, late at night | "back-and-forth to find a time" | Problem aware | Calls it a problem ("killing me"), then "I don't even know what the fix for that is" (Q2). |
| K3 | call-1 | Dana | Four hours of bookkeeping every Sunday | "do all my books on Sunday nights" | Unaware | Frames it as normal: "That's just part of owning a business, it's fine" (Q1). |
| K4 | call-2 | Tom | Doubts parents will use the booking link | "Will they actually use your booking link" | Product aware | Doubt about whether this product works for his customers (Q4: whether, not how). |
| K5 | call-2 | Tom | Price: four times the cost of SlotPilot | "Is yours really worth four times as much" | Product aware | Compares this product with another and doubts the price (Q4). |
| K6 | call-2 | Tom | No-shows cost a tutor's whole Thursday | "The no-shows are the main reason I'm here" | Most aware | "The deposit feature you showed in the demo is exactly what I need. I'm in. What does the contract look like?" (Q4: asking how to buy). |
| K7 | call-3 | Ines | Chasing late payments with awkward messages | "Getting paid is still the worst bit" | Problem aware | "I don't know what else I can do about it." Her later "I didn't know you did that" confirms where she started (Q2). |
| K8 | call-3 | Ines | Same-morning cancellations | "people cancelling the morning of" | Solution aware | Names a type of fix ("a late-cancellation fee"), not linked to Kettlebook (Q3). |
| K9 | call-3 | Ines | Two hours a day driving between clients | "I drive about two hours a day" | Unaware | "that's just the job with mobile grooming" (Q1). |
| K10 | call-4 | Femi | Staff scheduling clashes, a client nearly left | "two of my cleaners turned up at the same house" | Most aware | Tested the add-on; "Just tell me how to turn it on" (Q4: how and when). |
| K11 | call-4 | Femi | Commercial clients pay 30 days late | "stretch it to sixty" | Solution aware | "My accountant says I should be using automatic payment reminders", not linked to Kettlebook (Q3). |
| K12 | call-4 | Femi | Older staff may not use the app | "I'm not sure your app is simple enough" | Product aware | Doubt about whether this product suits his people (Q4). |

Stage totals: Unaware 2, Problem aware 2, Solution aware 3, Product aware 3, Most aware 2.

## Traps (rows that must not appear as pain points)

- **Seller lines.** Call 1: "A lot of salon owners tell us chasing deposits is their biggest headache" (Sam). Dana denies it. Call 4: "We hear chasing payments is the number one pain in cleaning" (Lee). Femi's own words about payments are K11; the seller's line is not a source.
- **Praise.** Call 3: "The reminders have cut the no-shows a lot." Call 4: "reminders have been brilliant, no complaints there."
- **Small talk.** Call 1: "Busy, which is good." Call 2: "the coffee here is terrible but that's not your problem." Call 3: "Good podcasts."

## Themes

| Theme | Keys | Calls |
|---|---|---|
| No-shows and late cancellations (empty slots) | K1, K6, K8 | call-1, call-2, call-3 |
| Late or chased payments | K7, K11 | call-3, call-4 |
| People won't adopt the app (customers or staff) | K4, K12 | call-2, call-4 |
| Singletons | K2, K3, K5, K9, K10 | one each |

## Scoring steps

1. **Recall.** Count how many of K1 to K12 the stage 1 table matched. A row that splits one planted pain into two rows (for example, K6's "lost a tutor's whole Thursday" listed apart from "no-shows are the main reason") counts as one match and is not an error. Extra rows that are not planted pains and not traps (for example, a buyer saying they have not picked a tool yet) are not penalised; list them in the score so the author can judge them.
2. **Stage accuracy.** For each matched pain, compare the stage 2 tag with "Correct stage". Count the matches that agree.
3. **Traps.** Count rows whose quote comes from a seller line, or from the praise or small-talk lines above.
4. **Quotes.** Check that every quote in all three tables appears word for word in the transcript.
5. **Themes.** Check the three multi-call themes: each counts as found if one theme in the stage 3 table holds both or all of its keys. Late cancellations (K8) may be a separate theme from no-shows; if so, the no-shows theme counts as found when it holds K1 and K6.

## Pass mark

The run passes when all of these hold:

- Recall: at least 10 of 12 (83%).
- Stage accuracy: at least 9 of 12 planted pains carry the correct stage (75%). A missed pain counts as wrong.
- Traps: 0 seller-line rows. At most 1 praise or small-talk row.
- Quotes: 0 invented or reworded quotes.
- Themes: at least 2 of the 3 multi-call themes found.

Report each number, then PASS or FAIL.
