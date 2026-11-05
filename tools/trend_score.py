#!/usr/bin/env python3
"""Score Chinese social media trends for Medibank: use now, adapt, watch or avoid.

Columns (see examples/trends_sample.csv):
    trend,platform,type,first_seen,ends,audience_match,oshc_link,flags,note

type is show, meme, challenge, hashtag or event; ends (optional) is the last airing or
event date; audience_match and oshc_link are 1-5; flags are separated by ";". The rubric
is explained in references/trend-playbook.md, section 2.

Usage:
    python trend_score.py trends.csv
    python trend_score.py trends.csv --today 2026-11-05 --out radar.md
"""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

WEIGHTS = {"audience": 30, "link": 30, "freshness": 20, "safety": 20}

# Expected life in days when no end date is given.
LIFESPAN = {"meme": 21, "challenge": 21, "hashtag": 7, "show": 56, "event": 14}

SOFT_FLAGS = {
    "ip_heavy": "Someone else's show or song: topic only, no clips, logos or music",
    "celebrity": "Real people at the centre: no names, faces or taking sides",
    "health_risk": "Physical risk: don't encourage copying; frame around safety",
    "competitor_sponsor": "Another insurer sponsors it: creator-led only, no sponsor reference",
}
HARD_FLAGS = {
    "politics": "Political or national topic",
    "tragedy": "Disaster, accident or death",
    "scandal": "Celebrity scandal or feud",
    "crime": "Crime",
    "mocking": "Mocks a group",
    "misinformation": "Medical misinformation",
}
SOFT_PENALTY = 5


def flags_of(row):
    return [f.strip() for f in (row.get("flags") or "").split(";") if f.strip()]


def freshness(row, today):
    start = date.fromisoformat(row["first_seen"].strip())
    end = (row.get("ends") or "").strip()
    if end:
        life = (date.fromisoformat(end) - start).days or 1
    else:
        life = LIFESPAN.get(row["type"].strip(), 14)
    age = (today - start).days
    return max(0.0, min(1.0, 1 - age / life))


def score_row(row, today):
    """Return (score, verdict, notes) for one trend."""
    flags = flags_of(row)
    unknown = [f for f in flags if f not in SOFT_FLAGS and f not in HARD_FLAGS]
    hard = [HARD_FLAGS[f] for f in flags if f in HARD_FLAGS]
    soft = [SOFT_FLAGS[f] for f in flags if f in SOFT_FLAGS]
    notes = hard + soft + [f"Unknown flag: {f}" for f in unknown]
    if hard:
        return 0.0, "avoid", notes

    audience = max(1, min(5, int(row["audience_match"]))) / 5
    link = max(1, min(5, int(row["oshc_link"]))) / 5
    safety = max(0, WEIGHTS["safety"] - SOFT_PENALTY * len(soft))
    total = (WEIGHTS["audience"] * audience + WEIGHTS["link"] * link
             + WEIGHTS["freshness"] * freshness(row, today) + safety)
    if total >= 70:
        verdict = "use now"
    elif total >= 50:
        verdict = "adapt"
    else:
        verdict = "watch"
    if freshness(row, today) == 0:
        notes.append("Past its expected life: post this week or drop it")
    return round(total, 1), verdict, notes


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def to_markdown(rows, today):
    order = {"use now": 0, "adapt": 1, "watch": 2, "avoid": 3}
    scored = []
    for r in rows:
        s, v, notes = score_row(r, today)
        scored.append((order[v], -s, r, s, v, notes))
    scored.sort(key=lambda x: (x[0], x[1]))
    lines = [f"## Trend radar · {today.isoformat()}", "",
             "| Trend | Platform | Type | Since | Score | Verdict | Watch out |",
             "|---|---|---|---|---|---|---|"]
    for _, _, r, s, v, notes in scored:
        lines.append(f"| {r['trend']} | {r['platform']} | {r['type']} | {r['first_seen']} | "
                     f"{s:g} | {v} | {'; '.join(notes) or '–'} |")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv")
    parser.add_argument("--today", help="YYYY-MM-DD (default: today)")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    today = date.fromisoformat(args.today) if args.today else date.today()
    md = to_markdown(load(args.csv), today)
    if args.out:
        Path(args.out).write_text(md + "\n", encoding="utf-8")
        print(f"Saved to {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
