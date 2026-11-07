#!/usr/bin/env python3
"""Score creator candidates (小红书, 抖音, 公众号, 视频号, 微博) for the Medibank OSHC campaign.

Input: a CSV exported from the platform marketplaces (蒲公英, 星图, 互选, 微任务) or a
data tool, tidied into the columns of examples/kol_candidates.csv. Six evidence-weighted
criteria, each measured 0-1; hard stops score 0. Scoring logic and sources:
references/kol-playbook.md section 3 and references/evidence.md (E-14, E-15).

Usage:
    python kol_score.py candidates.csv
    python kol_score.py candidates.csv --out scored.csv
"""

import argparse
import csv
import math
import sys
from pathlib import Path

# Six criteria, each measured 0-1 and weighted by its pooled correlation with purchase
# intention in two meta-analyses (references/evidence.md E-14, E-15): weight = r / sum(r) x 100,
# rounded. Follower count is NOT scored: it showed no positive link to purchase intention
# [E-14], so it only sets the tier and budget mix [A-2]. Re-test with real results [A-5].
WEIGHTS = {"useful": 20, "like_students": 18, "own_life": 17, "topic_fit": 16, "talks": 15, "trust": 14}

CRITERIA = {
    "useful": {"label": "Useful content", "r": 0.55, "source": "E-14",
               "what": "Share of recent posts that are guides, checklists or how-tos (useful_post_share)"},
    "like_students": {"label": "Like our students", "r": 0.51, "source": "E-15",
                      "what": "Lives in Australia (half) + share of audience who are students (half)"},
    "own_life": {"label": "Shares own life", "r": 0.47, "source": "E-14",
                 "what": "Share of recent posts about their own real experience (personal_post_share)"},
    "topic_fit": {"label": "Topic fit", "r": 0.45, "source": "E-14",
                  "what": "Share of recent posts on study, life or health in Australia (topic_relevance_share)"},
    "talks": {"label": "Talks with followers", "r": 0.43, "source": "E-14",
              "what": "Share of comment threads the creator replies to (reply_rate)"},
    "trust": {"label": "Trustworthy", "r": 0.43, "source": "E-15",
              "what": "Starts full; loses half for diverting followers off-platform, half for unreported past ads"},
}

HARD_STOPS = {
    "sells_agency_or_insurance": "Sells agency or insurance services",
    "competitor_90d": "Promoted another OSHC insurer in the last 90 days",
    "undisclosed_ads": "History of undisclosed ads",
    "fake_fans_flag": "Fake-fan flag from the data tool",
}


TIERS = ["<500", "500–1k", "1k–2k", "2k+"]  # Medibank works mostly with creators under 2k followers


def tier(followers):
    if followers < 500:
        return "<500"
    if followers < 1_000:
        return "500–1k"
    if followers < 2_000:
        return "1k–2k"
    return "2k+"


def truthy(value):
    return str(value).strip().lower() in {"1", "y", "yes", "true", "是"}


def num(row, key, default=0.0):
    try:
        return float(row.get(key, "") or default)
    except ValueError:
        return default


def criteria_scores(row):
    """Each criterion as a 0-1 value."""
    trust = 1.0
    if truthy(row.get("diversion_in_past_notes")):
        trust -= 0.5
    if not truthy(row.get("past_sponsored_reported", "yes")):
        trust -= 0.5
    clip = lambda x: max(0.0, min(x, 1.0))
    return {
        "useful": clip(num(row, "useful_post_share")),
        "like_students": clip(0.5 * truthy(row.get("based_in_australia")) + 0.5 * num(row, "audience_student_share")),
        "own_life": clip(num(row, "personal_post_share")),
        "topic_fit": clip(num(row, "topic_relevance_share")),
        "talks": clip(num(row, "reply_rate")),
        "trust": clip(trust),
    }


def score_row(row):
    followers = max(num(row, "followers"), 1)
    t = tier(followers)

    stops = [reason for key, reason in HARD_STOPS.items() if truthy(row.get(key, ""))]
    if stops:
        return t, 0.0, "no", "; ".join(stops)

    eng_rate = (num(row, "avg_likes") + 2 * num(row, "avg_saves") + num(row, "avg_comments")) / followers
    parts = criteria_scores(row)
    total = round(math.fsum(WEIGHTS[k] * v for k, v in parts.items()), 1)  # fsum: same result on every Python version
    band = "go" if total >= 70 else "maybe" if total >= 50 else "no"
    top = sorted(parts, key=lambda k: WEIGHTS[k] * parts[k], reverse=True)[:2]
    notes = f"eng {eng_rate:.1%}; strongest: " + ", ".join(CRITERIA[k]["label"] for k in top)
    return t, total, band, notes


def score_file(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    scored = []
    for row in rows:
        t, total, band, notes = score_row(row)
        scored.append({**row, "tier": t, "score": total, "band": band, "notes": notes})
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", help="candidate CSV")
    parser.add_argument("--out", help="write the scored table to this CSV")
    args = parser.parse_args(argv)

    scored = score_file(args.csv)
    print("#  | platform | creator | tier | score | band | notes")
    for i, r in enumerate(scored, 1):
        print(f"{i:<2} | {r.get('platform') or 'xiaohongshu'} | {r.get('handle', '?')} | {r['tier']} | "
              f"{r['score']} | {r['band']} | {r['notes']}")

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(scored[0].keys()))
            writer.writeheader()
            writer.writerows(scored)
        print(f"\nSaved to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
