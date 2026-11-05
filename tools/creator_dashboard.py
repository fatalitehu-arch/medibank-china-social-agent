#!/usr/bin/env python3
"""Creator library dashboard: per-creator results and follow-ups from creators/*.csv.

Inputs (see creators/README.md):
    creators/roster.csv  one row per creator Medibank works with (status, contract, fee)
    creators/posts.csv   one row per published creator post (likes, comments, saves,
                         shares, inquiries, compliance verdict, cost)

"inquiries" counts comments and DMs asking about OSHC (怎么买/保什么/怎么报销). They are
answered with the standard replies in assets/templates/comment-replies.md, never with a
quote or a sale.

Usage:
    python creator_dashboard.py
    python creator_dashboard.py --today 2027-01-25 --json
"""

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ["impressions", "likes", "comments", "saves", "shares", "inquiries", "cost_cny"]
QUIET_DAYS = 30
CONTRACT_WARNING_DAYS = 14


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def as_of(posts):
    """Latest post date, so the dashboard is reproducible without --today."""
    return max(date.fromisoformat(p["date"]) for p in posts) if posts else date.today()


def build(roster, posts, today):
    creators = []
    for c in roster:
        mine = [p for p in posts if p["creator_id"] == c["creator_id"]]
        totals = {k: sum(float(p.get(k) or 0) for p in mine) for k in METRICS}
        impressions = totals["impressions"] or 1
        last = max((date.fromisoformat(p["date"]) for p in mine), default=None)
        flags = []
        if c["status"] == "active" and (last is None or (today - last).days > QUIET_DAYS):
            flags.append(f"No post in {QUIET_DAYS} days")
        end = date.fromisoformat(c["contract_end"])
        if c["status"] in {"active", "briefed"} and today <= end <= today + timedelta(days=CONTRACT_WARNING_DAYS):
            flags.append(f"Contract ends {end.isoformat()}")
        if any(p["verdict"] != "green" for p in mine):
            flags.append("A post needed changes (amber/red)")
        if c["status"] == "briefed" and not mine:
            flags.append("Waiting for first post")
        creators.append({
            "id": c["creator_id"], "handle": c["handle"], "platform": c["platform"],
            "tier": c["tier"], "followers": int(c["followers"]), "persona": c["persona"],
            "status": c["status"], "marketplace": c["marketplace"], "kol_score": int(c["kol_score"]),
            "posts": len(mine), "last_post": last.isoformat() if last else None,
            **{k: int(v) for k, v in totals.items()},
            "save_rate": round(totals["saves"] / impressions, 4),
            "cost_per_inquiry": round(totals["cost_cny"] / totals["inquiries"]) if totals["inquiries"] else None,
            "flags": flags,
        })
    summary = {k: sum(c[k] for c in creators) for k in METRICS}
    summary.update({"creators": len(creators), "active": sum(c["status"] == "active" for c in creators),
                    "posts": len(posts), "as_of": today.isoformat()})
    return {"summary": summary, "creators": creators}


def to_markdown(data):
    s = data["summary"]
    lines = [f"## Creator dashboard · as of {s['as_of']}", "",
             f"**{s['creators']} creators ({s['active']} active) · {s['posts']} posts · "
             f"{s['likes']:,} likes · {s['comments']:,} comments · {s['saves']:,} saves · "
             f"{s['inquiries']:,} inquiries**", "",
             "| Creator | Platform | Status | Posts | Likes | Comments | Saves | Inquiries | Save rate | CNY / inquiry | Follow up |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in sorted(data["creators"], key=lambda c: -c["inquiries"]):
        cpi = f"{c['cost_per_inquiry']:,}" if c["cost_per_inquiry"] is not None else "–"
        lines.append(f"| {c['handle']} | {c['platform']} | {c['status']} | {c['posts']} | {c['likes']:,} | "
                     f"{c['comments']:,} | {c['saves']:,} | {c['inquiries']} | {c['save_rate']:.1%} | {cpi} | "
                     f"{'; '.join(c['flags']) or '–'} |")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--roster", default=str(ROOT / "creators" / "roster.csv"))
    parser.add_argument("--posts", default=str(ROOT / "creators" / "posts.csv"))
    parser.add_argument("--today", help="YYYY-MM-DD (default: date of the latest post)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    roster, posts = load(args.roster), load(args.posts)
    today = date.fromisoformat(args.today) if args.today else as_of(posts)
    data = build(roster, posts, today)
    print(json.dumps(data, ensure_ascii=False, indent=2) if args.json else to_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
