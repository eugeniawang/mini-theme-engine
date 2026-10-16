# Mini Theme Engine

An instruction-only folder that an AI follows to turn sales and client call transcripts into pain points, each tagged with its customer awareness stage (Schwartz's five stages), then rolled up into themes.

- **Start at [START-HERE.md](START-HERE.md).** Any AI chat that can read files can run it.
- **The four sample calls are fictional.** Every person, business and product in them is invented.
- **Before you use real calls:** use only transcripts you are allowed to use, remove names, contact and account details, get any consent required, and use an AI tool your organisation approves. Details in START-HERE.md.
- **What you get:** `output/results.md` with three tables: pain points with exact quotes, awareness stage per pain point, and themes ranked by how often they come up.
- **Checking the output:** `python3 scripts/qa.py all` checks every stage automatically (Python 3, no installs); add `--answer-key` to score the sample run against `answer-key/` (open-book).
