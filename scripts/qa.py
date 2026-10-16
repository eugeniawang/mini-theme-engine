#!/usr/bin/env python3
"""Automated checks for the Mini Theme Engine output. Python 3 standard library only.

Usage:
    python3 scripts/qa.py stage1          check the stage 1 table
    python3 scripts/qa.py stage2          check the stage 2 table (against stage 1)
    python3 scripts/qa.py stage3          check the stage 3 table (against stages 1 and 2)
    python3 scripts/qa.py all             run all three
    python3 scripts/qa.py all --answer-key   also score the run against answer-key/answer-key.md

Options:
    --results PATH       results file (default: output/results.md)
    --transcripts DIR    transcript folder (default: sample-transcripts/)

Exit code 0 means every check passed. Any failure prints the file, the row and the reason, and exits 1.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STAGE_HEADINGS = {
    1: "## Stage 1: pain points",
    2: "## Stage 2: awareness stages",
    3: "## Stage 3: themes",
}
SELLER_ROLES = ("seller", "account manager", "sales")


# ---------- text helpers ----------

def norm(text):
    """Normalise only whitespace, quote marks and dashes, so 'verbatim' survives copy-paste."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip()


def unquote(cell):
    """Strip the quote marks a table cell wraps an exact quote in."""
    cell = norm(cell)
    if len(cell) >= 2 and cell[0] == '"' and cell[-1] == '"':
        cell = cell[1:-1].strip()
    return cell


def words(text):
    return re.findall(r"[a-z0-9']+", norm(text).lower())


# ---------- transcripts ----------

class Transcript:
    def __init__(self, path):
        self.path = path
        self.call = re.match(r"(call-\d+)", path.name).group(1)
        self.turns = []  # list of (speaker, text)
        self.sellers = set()
        self.speakers = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("Speakers:"):
                for name, role in re.findall(r"\*{0,2}([A-Z][\w'-]*)\*{0,2}\s*\(([^)]*)\)", line):
                    self.speakers.add(name)
                    if role.strip().lower().startswith(SELLER_ROLES):
                        self.sellers.add(name)
                continue
            m = re.match(r"^\*{0,2}([A-Z][\w'-]*):\*{0,2}\s+(.*)$", line)
            if m:
                self.turns.append((m.group(1), norm(m.group(2).replace("**", ""))))
            elif self.turns and line.strip() and not line.startswith(("#", "---")):
                speaker, text = self.turns[-1]
                self.turns[-1] = (speaker, text + " " + norm(line))

    def buyers(self):
        return {s for s, _ in self.turns} - self.sellers

    def find(self, quote, speaker=None):
        """Index of the first turn holding the quote, spoken by speaker if given; else None."""
        q = norm(quote)
        for i, (s, text) in enumerate(self.turns):
            if (speaker is None or s == speaker) and q and q in text:
                return i
        return None


def load_transcripts(folder):
    files = sorted(Path(folder).glob("call-*.md"), key=lambda p: int(re.match(r"call-(\d+)", p.name).group(1)))
    return {t.call: t for t in (Transcript(p) for p in files)}


# ---------- results tables ----------

def read_table(results_text, heading):
    """Return (header cells, list of row dicts, text after the table) for the first table under heading."""
    lines = results_text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower() == heading.lower())
    except StopIteration:
        return None, [], ""
    header, rows, after, in_table = None, [], [], False
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                header = cells
                in_table = True
            elif set("".join(cells)) <= set("-: "):
                continue
            elif in_table:
                rows.append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
        elif header is not None:
            in_table = False
            after.append(line)
    return header, rows, "\n".join(after)


def col(row, prefix):
    """Fetch a cell by the start of its column name, so headings with notes in brackets still match."""
    for key, value in row.items():
        if key.lower().startswith(prefix.lower()):
            return value.strip()
    return ""


class Report:
    def __init__(self, results_path):
        self.file = results_path
        self.failures = []

    def fail(self, stage, item, reason):
        self.failures.append(f"FAIL {stage} | {self.file} | {item} | {reason}")


def allowed_stages():
    text = (ROOT / "awareness-framework.md").read_text(encoding="utf-8")
    names = re.findall(r"^\|\s*\d\.\s*([A-Za-z ]+?)\s*\|", text, flags=re.M)
    return names or ["Unaware", "Problem aware", "Solution aware", "Product aware", "Most aware"]


# ---------- stage checks ----------

def check_stage1(results, transcripts, rep):
    header, rows, _ = read_table(results, STAGE_HEADINGS[1])
    if header is None:
        rep.fail("stage1", "table", f"heading '{STAGE_HEADINGS[1]}' or its table not found")
        return {}
    pains, seen_ids, seen_quotes, calls_covered = {}, set(), {}, set()
    order = list(transcripts)
    last_pos = (-1, -1)
    for n, row in enumerate(rows, 1):
        pid, call, speaker = col(row, "ID"), col(row, "Call"), col(row, "Speaker")
        pain, quote = col(row, "Pain point"), unquote(col(row, "Exact quote"))
        item = pid or f"row {n}"
        if pid.lower() == "none":
            if call not in transcripts:
                rep.fail("stage1", item, f"call '{call}' has no transcript file")
            calls_covered.add(call)
            continue
        if not re.fullmatch(r"P\d+", pid):
            rep.fail("stage1", item, "ID must be P1, P2, ... (or 'none' for a call with no pain points)")
            continue
        if pid in seen_ids:
            rep.fail("stage1", item, "duplicate ID")
        seen_ids.add(pid)
        if int(pid[1:]) != len(seen_ids):
            rep.fail("stage1", item, f"IDs must run P1, P2, ... without gaps; expected P{len(seen_ids)}")
        for field, value in (("Call", call), ("Speaker", speaker), ("Pain point", pain), ("Exact quote", quote)):
            if not value or value == '""':
                rep.fail("stage1", item, f"required field '{field}' is empty")
        if pain and len(words(pain)) >= 12:
            rep.fail("stage1", item, f"pain point must be under 12 words (has {len(words(pain))})")
        t = transcripts.get(call)
        if t is None:
            rep.fail("stage1", item, f"call '{call}' has no transcript file in the transcript folder")
            continue
        calls_covered.add(call)
        if speaker in t.sellers:
            rep.fail("stage1", item, f"speaker '{speaker}' is the seller in {t.path.name}; only buyer or client lines count")
        turn = t.find(quote, speaker) if quote else None
        if quote and turn is None:
            if t.find(quote) is not None:
                who = t.turns[t.find(quote)][0]
                rep.fail("stage1", item, f"quote is spoken by {who}, not {speaker}, in {t.path.name}: \"{quote}\"")
            else:
                rep.fail("stage1", item, f"quote not found verbatim in any {speaker} line of {t.path.name}: \"{quote}\"")
        if turn is not None:
            pos = (order.index(call), turn)
            if pos < last_pos:
                rep.fail("stage1", item, "rows must be in transcript order, call 1 first")
            last_pos = max(last_pos, pos)
        key = (call, norm(quote).lower())
        for (c, q), other in seen_quotes.items():
            if c == call and q and key[1] and (q in key[1] or key[1] in q):
                rep.fail("stage1", item, f"duplicate of {other}: same or overlapping quote in {call}")
        seen_quotes[key] = pid
        pains[pid] = {"call": call, "speaker": speaker, "quote": quote, "pain": pain}
    for call, t in transcripts.items():
        if call not in calls_covered:
            rep.fail("stage1", call, f"{t.path.name} produced no rows; add its pain points or a 'none' row")
    if not rows:
        rep.fail("stage1", "table", "the table has no rows")
    return pains


def check_stage2(results, transcripts, pains, rep):
    header, rows, _ = read_table(results, STAGE_HEADINGS[2])
    if header is None:
        rep.fail("stage2", "table", f"heading '{STAGE_HEADINGS[2]}' or its table not found")
        return {}
    allowed = {s.lower(): s for s in allowed_stages()}
    tags, counts = {}, {}
    for n, row in enumerate(rows, 1):
        pid = col(row, "ID")
        item = pid or f"row {n}"
        counts[pid] = counts.get(pid, 0) + 1
        if pid not in pains:
            rep.fail("stage2", item, "not a stage 1 ID; stage 2 must not add pain points")
            continue
        stage, signal, why = col(row, "Stage"), unquote(col(row, "Signal")), col(row, "Why")
        if stage.lower() not in allowed:
            rep.fail("stage2", item, f"stage '{stage}' is not one of: {', '.join(allowed.values())}")
        else:
            tags[pid] = allowed[stage.lower()]
        if not signal:
            rep.fail("stage2", item, "signal (the buyer's exact words) is empty")
        else:
            p = pains[pid]
            t = transcripts[p["call"]]
            if t.find(signal, p["speaker"]) is None:
                where = t.find(signal)
                reason = (f"signal is spoken by {t.turns[where][0]}, not {p['speaker']}" if where is not None
                          else f"signal not found verbatim in any {p['speaker']} line of {t.path.name}")
                rep.fail("stage2", item, f"{reason}: \"{signal}\"")
        if not re.search(r"\bQ[1-4]\b", why):
            rep.fail("stage2", item, "'Why' must name the deciding tie-break question (Q1 to Q4)")
    for pid in pains:
        if counts.get(pid, 0) == 0:
            rep.fail("stage2", pid, "stage 1 pain point has no stage 2 row")
        elif counts[pid] > 1:
            rep.fail("stage2", pid, f"tagged {counts[pid]} times; each pain point gets exactly one stage")
    return tags


def check_stage3(results, transcripts, pains, tags, rep):
    header, rows, after = read_table(results, STAGE_HEADINGS[3])
    if header is None:
        rep.fail("stage3", "table", f"heading '{STAGE_HEADINGS[3]}' or its table not found")
        return []
    themes, placed, prev_count = [], {}, None
    for n, row in enumerate(rows, 1):
        name = col(row, "Theme") or f"row {n}"
        item = f"theme '{name}'"
        ids = re.findall(r"P\d+", col(row, "Pain points"))
        if not ids:
            rep.fail("stage3", item, "cites no pain point IDs")
        for pid in ids:
            if pid not in pains:
                rep.fail("stage3", item, f"cites {pid}, which is not a stage 1 ID")
            elif pid in placed:
                rep.fail("stage3", item, f"{pid} is already in theme '{placed[pid]}'; every pain point belongs to exactly one theme")
            else:
                placed[pid] = name
        real = [p for p in dict.fromkeys(ids) if p in pains]
        count = col(row, "Count")
        if not count.isdigit() or int(count) != len(ids):
            rep.fail("stage3", item, f"Count is '{count}' but {len(ids)} IDs are listed")
        want_calls = {pains[p]["call"] for p in real}
        got_calls = set(re.findall(r"call-\d+", col(row, "Calls")))
        if got_calls != want_calls:
            rep.fail("stage3", item, f"Calls lists {sorted(got_calls)} but its IDs come from {sorted(want_calls)}")
        want_stages = {tags[p] for p in real if p in tags}
        got_stages = {s for s in allowed_stages() if re.search(rf"\b{re.escape(s)}\b", col(row, "Stages"), re.I)}
        if got_stages != want_stages:
            rep.fail("stage3", item, f"Stages seen lists {sorted(got_stages)} but its pain points carry {sorted(want_stages)}")
        quote = unquote(col(row, "Best quote"))
        sources = [transcripts[pains[p]["call"]] for p in real]
        if not quote:
            rep.fail("stage3", item, "best quote is empty")
        elif not any(t.find(quote, s) is not None for t in sources for s in t.buyers()):
            rep.fail("stage3", item, f"best quote not found verbatim in a buyer line of the theme's calls: \"{quote}\"")
        if prev_count is not None and len(ids) > prev_count:
            rep.fail("stage3", item, "themes must be sorted by pain point count, highest first")
        prev_count = len(ids)
        themes.append({"name": name, "ids": real})
    for pid in pains:
        if pid not in placed:
            rep.fail("stage3", pid, "pain point is in no theme")
    if not 1 <= len(themes) <= max(len(pains), 1):
        rep.fail("stage3", "table", f"{len(themes)} themes; must be between 1 and the number of pain points ({len(pains)})")
    # The line naming the most common stage must name every stage that ties for the top count.
    stage_counts = {}
    for s in tags.values():
        stage_counts[s] = stage_counts.get(s, 0) + 1
    if stage_counts:
        top = max(stage_counts.values())
        leaders = [s for s, c in stage_counts.items() if c == top]
        line = next((l for l in after.splitlines() if re.search(r"common", l, re.I)), "")
        if not line:
            rep.fail("stage3", "summary lines", "no line under the table names the most common awareness stage")
        else:
            missing = [s for s in leaders if not re.search(rf"\b{re.escape(s)}\b", line, re.I)]
            if missing:
                rep.fail("stage3", "summary lines", f"most common stage line misses {missing} ({top} pain points each)")
        if not re.search(r"first", after, re.I):
            rep.fail("stage3", "summary lines", "no line under the table names the theme to act on first")
    return themes


# ---------- answer key ----------

def score_answer_key(results, transcripts, pains, tags, themes, rep):
    key_text = (ROOT / "answer-key" / "answer-key.md").read_text(encoding="utf-8")
    _, planted, _ = read_table(key_text, "## Planted pain points")
    _, key_themes, _ = read_table(key_text, "## Themes")
    traps_section = key_text.split("## Traps", 1)[1].split("\n## ", 1)[0]
    trap_quotes = [norm(q).lower() for q in re.findall(r'"([^"]+)"', traps_section)]

    # Match each run row to a planted pain: same call, quote in the buyer turn that holds the anchor.
    matched = {}  # key -> list of pain ids
    extras = []
    for pid, p in pains.items():
        t = transcripts[p["call"]]
        turn = t.find(p["quote"], p["speaker"])
        cands = []
        for k in planted:
            if col(k, "Call") != p["call"] or turn is None:
                continue
            if t.find(unquote(col(k, "Anchor")), p["speaker"]) == turn:
                cands.append(k)
        if len(cands) > 1:
            in_quote = [k for k in cands if norm(unquote(col(k, "Anchor"))).lower() in p["quote"].lower()]
            cands = in_quote or sorted(cands, key=lambda k: -len(set(words(col(k, "Pain"))) & set(words(p["pain"]))))[:1]
        if cands:
            matched.setdefault(col(cands[0], "Key"), []).append(pid)
        else:
            extras.append(pid)

    recall = len(matched)
    correct = sum(1 for k in planted if col(k, "Key") in matched
                  and tags.get(matched[col(k, "Key")][0]) == col(k, "Correct stage"))
    seller_rows = [pid for pid, p in pains.items() if p["speaker"] in transcripts[p["call"]].sellers]
    trap_rows = [pid for pid, p in pains.items()
                 if any(tq in p["quote"].lower() or p["quote"].lower() in tq for tq in trap_quotes)]
    invented = [f for f in rep.failures if "not found verbatim" in f or "is spoken by" in f]

    found_themes = []
    for kt in key_themes:
        keys = re.findall(r"K\d+", col(kt, "Keys"))
        if col(kt, "Theme").lower().startswith("singleton") or len(keys) < 2:
            continue
        need = [keys, [k for k in keys if k != "K8"]] if "K8" in keys else [keys]
        hit = any(all(any(pid in th["ids"] for pid in matched.get(k, [])) for k in want)
                  for want in need for th in themes)
        found_themes.append((col(kt, "Theme"), hit))

    total = len(planted)
    checks = [
        ("Recall", f"{recall} of {total}", recall >= 10),
        ("Stage accuracy", f"{correct} of {total}", correct >= 9),
        ("Seller-line rows", str(len(seller_rows)), not seller_rows),
        ("Praise or small-talk rows", str(len(trap_rows)), len(trap_rows) <= 1),
        ("Invented or reworded quotes", str(len(invented)), not invented),
        ("Multi-call themes found", f"{sum(h for _, h in found_themes)} of {len(found_themes)}",
         sum(h for _, h in found_themes) >= 2),
    ]
    print("\nAnswer-key score")
    for name, value, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {value}")
    missed = [col(k, "Key") for k in planted if col(k, "Key") not in matched]
    wrong = [col(k, "Key") for k in planted if col(k, "Key") in matched
             and tags.get(matched[col(k, "Key")][0]) != col(k, "Correct stage")]
    print(f"  Missed planted pains: {', '.join(missed) or 'none'}")
    print(f"  Wrong stage: {', '.join(wrong) or 'none'}")
    theme_notes = "; ".join(n + (" = found" if h else " = not found") for n, h in found_themes)
    print(f"  Themes: {theme_notes}")
    print(f"  Extra rows (not planted, not traps; author to judge): {', '.join(extras) or 'none'}")
    passed = all(ok for _, _, ok in checks)
    print(f"  Answer key: {'PASS' if passed else 'FAIL'}")
    for name, value, ok in checks:
        if not ok:
            rep.fail("answer-key", name, f"{value} is below the pass mark in answer-key/answer-key.md")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description="Check Mini Theme Engine output, stage by stage.")
    ap.add_argument("stage", choices=["stage1", "stage2", "stage3", "all"])
    ap.add_argument("--answer-key", action="store_true", help="also score against answer-key/ (after the run only)")
    ap.add_argument("--results", default=str(ROOT / "output" / "results.md"))
    ap.add_argument("--transcripts", default=str(ROOT / "sample-transcripts"))
    args = ap.parse_args()

    results_path = Path(args.results)
    rep = Report(results_path)
    transcripts = load_transcripts(args.transcripts)
    if not transcripts:
        print(f"FAIL setup | {args.transcripts} | - | no call-N_*.md transcript files found")
        return 1
    for t in transcripts.values():
        if not t.sellers:
            rep.fail("setup", t.path.name, "no 'Speakers:' line marking who is the seller, e.g. **Sam** (seller)")
    if not results_path.exists():
        print(f"FAIL setup | {results_path} | - | results file not found")
        return 1
    results = results_path.read_text(encoding="utf-8")

    want = {"stage1": 1, "stage2": 2, "stage3": 3, "all": 3}[args.stage]
    pains = check_stage1(results, transcripts, rep)
    stage1_failures = len(rep.failures)
    tags, themes = {}, []
    if want >= 2:
        tags = check_stage2(results, transcripts, pains, rep)
    if want >= 3:
        themes = check_stage3(results, transcripts, pains, tags, rep)
    if args.stage in ("stage2", "stage3") and stage1_failures:
        print(f"note: stage 1 has {stage1_failures} failure(s); later checks build on it, so fix stage 1 first")
    if args.answer_key:
        score_answer_key(results, transcripts, pains, tags, themes, rep)

    for line in rep.failures:
        print(line)
    if rep.failures:
        print(f"\n{args.stage}: {len(rep.failures)} failure(s)")
        return 1
    print(f"{args.stage}: all checks passed ({len(pains)} pain points, {len(tags)} tags, {len(themes)} themes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
