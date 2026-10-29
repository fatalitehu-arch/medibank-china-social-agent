#!/usr/bin/env python3
"""Build a cross-platform performance report from exported social media data.

Columns (see examples/metrics_sample.csv), one row per post/article/video:
    post_id,date,platform,stream,creator,pillar,format,impressions,reads,likes,saves,
    comments,shares,follows,question_comments,cost_cny

Map each platform's export to these columns, e.g. 公众号 阅读 → impressions and reads,
在看 → likes, 收藏 → saves, 分享 → shares; 抖音/视频号 播放 → impressions.

Output: totals, rates by platform, owned vs creator, by pillar, by format, top/bottom
posts, and
cost per save for paid notes. Interpretation (why a note worked) is left to the agent.

Usage:
    python performance_report.py metrics.csv
    python performance_report.py metrics.csv --out report.md
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

NUMERIC = ["impressions", "reads", "likes", "saves", "comments", "shares", "follows",
           "question_comments", "cost_cny"]


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in NUMERIC:
            try:
                r[k] = float(r.get(k) or 0)
            except ValueError:
                r[k] = 0.0
    return rows


def rates(group):
    imp = sum(r["impressions"] for r in group) or 1
    saves = sum(r["saves"] for r in group)
    engagements = sum(r["likes"] + r["saves"] + r["comments"] + r["shares"] for r in group)
    cost = sum(r["cost_cny"] for r in group)
    paid_saves = sum(r["saves"] for r in group if r["cost_cny"] > 0)
    return {
        "notes": len(group),
        "impressions": int(imp if group else 0),
        "saves": int(saves),
        "question_comments": int(sum(r["question_comments"] for r in group)),
        "follows": int(sum(r["follows"] for r in group)),
        "engagement_rate": engagements / imp,
        "save_rate": saves / imp,
        "cost_cny": cost,
        "cost_per_save": (cost / paid_saves) if paid_saves else None,
    }


def table(title, groups):
    lines = [f"### {title}", "",
             "| Group | Posts | Impressions | Saves | Save rate | Eng. rate | Question comments | Cost/save (CNY) |",
             "|---|---|---|---|---|---|---|---|"]
    for name, g in groups.items():
        r = rates(g)
        cps = f"{r['cost_per_save']:.1f}" if r["cost_per_save"] is not None else "–"
        lines.append(f"| {name} | {r['notes']} | {r['impressions']:,} | {r['saves']:,} | {r['save_rate']:.2%} | "
                     f"{r['engagement_rate']:.2%} | {r['question_comments']} | {cps} |")
    return "\n".join(lines) + "\n"


def group_by(rows, key):
    out = defaultdict(list)
    for r in rows:
        out[r.get(key, "") or "(blank)"].append(r)
    return dict(sorted(out.items()))


def note_score(r):
    """Rank notes by usefulness: saves and real questions per impression."""
    imp = r["impressions"] or 1
    return (r["saves"] + 2 * r["question_comments"]) / imp


def build(rows):
    total = rates(rows)
    ranked = sorted(rows, key=note_score, reverse=True)
    lines = ["# China social media performance report", "",
             f"**{total['notes']} posts · {total['impressions']:,} impressions · {total['saves']:,} saves · "
             f"save rate {total['save_rate']:.2%} · {total['question_comments']} question comments**", ""]
    if total["cost_per_save"] is not None:
        lines.append(f"Creator spend {total['cost_cny']:,.0f} CNY · cost per save on paid posts "
                     f"{total['cost_per_save']:.1f} CNY\n")
    lines.append(table("By platform", group_by(rows, "platform")))
    lines.append("_Rates are not comparable across platforms (a 公众号 read is not a 抖音 view); "
                 "compare each platform with its own previous period._\n")
    lines.append(table("Owned vs creator", group_by(rows, "stream")))
    lines.append(table("By pillar", group_by(rows, "pillar")))
    lines.append(table("By format", group_by(rows, "format")))

    def note_rows(items):
        out = ["| Post | Date | Platform | Stream | Creator | Pillar | Save rate | Question comments |",
               "|---|---|---|---|---|---|---|---|"]
        for r in items:
            out.append(f"| {r['post_id']} | {r['date']} | {r['platform']} | {r['stream']} | {r.get('creator', '')} | {r['pillar']} | "
                       f"{r['saves'] / (r['impressions'] or 1):.2%} | {int(r['question_comments'])} |")
        return "\n".join(out)

    k = min(3, len(ranked))
    lines += ["### Top posts (saves + 2 × question comments per impression)", "", note_rows(ranked[:k]), ""]
    lines += ["### Bottom posts", "", note_rows(ranked[-k:][::-1]), ""]

    creators = {c: g for c, g in group_by([r for r in rows if r["stream"] == "creator"], "creator").items()}
    if creators:
        lines.append(table("By creator", creators))
    lines.append("_Why each post did well or badly is for the agent or the team to explain; "
                 "this report only shows the numbers._")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    md = build(load(args.csv))
    if args.out:
        Path(args.out).write_text(md + "\n", encoding="utf-8")
        print(f"Saved to {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
