#!/usr/bin/env python3
"""Score creator candidates (小红书, 抖音, 公众号, 视频号, 微博) for the Medibank OSHC campaign.

Input: a CSV exported from the platform marketplaces (蒲公英, 星图, 互选, 微任务) or a
data tool, tidied into the columns of examples/kol_candidates.csv. The `platform` column
picks the engagement baseline; rows without it are treated as 小红书. Scoring logic is explained in
references/kol-playbook.md, section 3.

Usage:
    python kol_score.py candidates.csv
    python kol_score.py candidates.csv --out scored.csv
"""

import argparse
import csv
import statistics
import sys
from pathlib import Path

WEIGHTS = {"audience": 30, "engagement": 25, "relevance": 20, "trust": 15, "cost": 10}

# Engagement rate (with saves counted twice) that earns full marks on 小红书, by tier.
FULL_MARKS_ENGAGEMENT = {"KOC": 0.10, "腰部": 0.06, "头部": 0.03}

# Platform multiplier on that threshold. Starting assumptions, not benchmarks: tune them
# with Medibank's own campaign data. For 公众号 use reads as "likes" and 在看/收藏 as saves.
PLATFORM_FACTOR = {"xiaohongshu": 1.0, "douyin": 1.0, "wechat-channels": 0.6,
                   "wechat-oa": 0.4, "weibo": 0.3}

HARD_STOPS = {
    "sells_agency_or_insurance": "Sells agency or insurance services",
    "competitor_90d": "Promoted another OSHC insurer in the last 90 days",
    "undisclosed_ads": "History of undisclosed ads",
    "fake_fans_flag": "Fake-fan flag from the data tool",
}


def tier(followers):
    if followers < 10_000:
        return "KOC"
    if followers < 100_000:
        return "腰部"
    return "头部"


def truthy(value):
    return str(value).strip().lower() in {"1", "y", "yes", "true", "是"}


def num(row, key, default=0.0):
    try:
        return float(row.get(key, "") or default)
    except ValueError:
        return default


def group_key(row):
    return ((row.get("platform") or "xiaohongshu").strip(), tier(max(num(row, "followers"), 1)))


def score_row(row, medians):
    followers = max(num(row, "followers"), 1)
    t = tier(followers)
    platform = (row.get("platform") or "xiaohongshu").strip()
    factor = PLATFORM_FACTOR.get(platform, 1.0)

    stops = [reason for key, reason in HARD_STOPS.items() if truthy(row.get(key, ""))]
    if stops:
        return t, 0.0, "no", "; ".join(stops)

    audience = (15 if truthy(row.get("based_in_australia")) else 0) + \
        15 * min(num(row, "audience_student_share"), 1.0)

    interactions = num(row, "avg_likes") + 2 * num(row, "avg_saves") + num(row, "avg_comments")
    eng_rate = interactions / followers
    engagement = WEIGHTS["engagement"] * min(eng_rate / (FULL_MARKS_ENGAGEMENT[t] * factor), 1.0)

    relevance = WEIGHTS["relevance"] * min(num(row, "topic_relevance_share"), 1.0)

    # Trust starts full; unreported past sponsorships and diversion habits cost points.
    trust = WEIGHTS["trust"]
    if truthy(row.get("diversion_in_past_notes")):
        trust -= 8
    if not truthy(row.get("past_sponsored_reported", "yes")):
        trust -= 7
    trust = max(trust, 0)

    price = num(row, "quote_cny")
    median = medians.get(group_key(row))
    if price and median:
        cost = WEIGHTS["cost"] * min(median / price, 1.0)
    else:
        cost = WEIGHTS["cost"] / 2  # unknown price: neutral

    total = round(audience + engagement + relevance + trust + cost, 1)
    band = "go" if total >= 70 else "maybe" if total >= 50 else "no"
    notes = f"eng {eng_rate:.1%}"
    return t, total, band, notes


def score_file(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # Median quote within each platform + tier, used for cost efficiency.
    per_group = {}
    for row in rows:
        price = num(row, "quote_cny")
        if price:
            per_group.setdefault(group_key(row), []).append(price)
    medians = {k: statistics.median(v) for k, v in per_group.items()}

    scored = []
    for row in rows:
        t, total, band, notes = score_row(row, medians)
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
