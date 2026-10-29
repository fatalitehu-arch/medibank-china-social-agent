#!/usr/bin/env python3
"""Check a cross-platform content calendar CSV and render it as a Markdown table.

Columns (see assets/templates/content-calendar.csv):
    date,platform,stream,persona,pillar,working_title,format,creator_tier,kpi,risk

stream is owned or creator. Checks: platform split against references/platforms/overview.md,
owned/creator split, pillar mix against references/content-playbook.md, owned posts per
week per platform, same-day clashes, and every amber/red item that needs Legal.

Usage:
    python calendar_builder.py plan.csv
    python calendar_builder.py plan.csv --out calendar.md
"""

import argparse
import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

PILLAR_TARGET = {"看懂你的保险": 0.35, "在澳洲看病": 0.30, "用好 app 和热线": 0.20, "身心健康": 0.15}
PLATFORM_TARGET = {"xiaohongshu": 0.40, "wechat": 0.30, "douyin": 0.20, "weibo": 0.10}
# Max owned posts per ISO week, from the cadence table in references/content-playbook.md.
OWNED_PER_WEEK = {"xiaohongshu": 3, "wechat-oa": 2, "wechat-channels": 2, "douyin": 3, "weibo": 4}
CREATOR_TARGET = 0.70
TOLERANCE = 0.15
REQUIRED = ["date", "platform", "stream", "persona", "pillar", "working_title", "format", "kpi", "risk"]


def stream(row):
    value = row["stream"].strip().lower()
    return "owned" if value in {"owned", "brand"} else value


def platform_group(row):
    p = row["platform"].strip()
    return "wechat" if p.startswith("wechat") else p


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in REQUIRED if rows and c not in rows[0]]
    if missing:
        raise SystemExit(f"Missing columns: {', '.join(missing)}")
    for r in rows:
        r["_date"] = date.fromisoformat(r["date"].strip())
    return sorted(rows, key=lambda r: r["_date"])


def check(rows):
    """Return a list of findings (strings)."""
    findings = []
    n = len(rows)
    if not n:
        return ["Calendar is empty."]

    platforms = Counter(platform_group(r) for r in rows)
    for group, target in PLATFORM_TARGET.items():
        share = platforms.get(group, 0) / n
        if abs(share - target) > TOLERANCE:
            findings.append(f"Platform {group} is {share:.0%} (target ~{target:.0%}).")
    unknown_platforms = set(platforms) - set(PLATFORM_TARGET)
    if unknown_platforms:
        findings.append(f"Unknown platform(s): {', '.join(sorted(unknown_platforms))}.")

    creator_share = sum(stream(r) == "creator" for r in rows) / n
    if abs(creator_share - CREATOR_TARGET) > TOLERANCE:
        findings.append(f"Creator share is {creator_share:.0%} (target ~{CREATOR_TARGET:.0%}).")

    pillars = Counter(r["pillar"].strip() for r in rows)
    for pillar, target in PILLAR_TARGET.items():
        share = pillars.get(pillar, 0) / n
        if abs(share - target) > TOLERANCE:
            findings.append(f"Pillar 「{pillar}」 is {share:.0%} (target ~{target:.0%}).")
    unknown = set(pillars) - set(PILLAR_TARGET)
    if unknown:
        findings.append(f"Unknown pillar(s): {', '.join(sorted(unknown))}.")

    weeks = Counter((r["platform"].strip(), *r["_date"].isocalendar()[:2]) for r in rows if stream(r) == "owned")
    for (platform, year, week), count in sorted(weeks.items()):
        limit = OWNED_PER_WEEK.get(platform)
        if limit and count > limit:
            findings.append(f"{platform}: {count} owned posts in {year}-W{week:02d} (max ~{limit}).")

    days = Counter((r["_date"], r["platform"].strip()) for r in rows if stream(r) == "owned")
    for (day, platform), count in sorted(days.items()):
        if count > 1:
            findings.append(f"{count} owned posts on {platform} on {day}; spread them out.")

    for r in rows:
        if r["risk"].strip().lower() in {"amber", "red", "🟡", "🔴"}:
            findings.append(f"{r['date']} 「{r['working_title']}」 is {r['risk']}: needs Legal before publishing.")
    return findings


def to_markdown(rows, findings):
    head = "| Date | Platform | Stream | Persona | Pillar | Working title | Format | Tier | KPI | Risk |"
    sep = "|" + "---|" * 10
    icon = {"green": "🟢", "amber": "🟡", "red": "🔴"}
    lines = [head, sep]
    for r in rows:
        risk = icon.get(r["risk"].strip().lower(), r["risk"])
        lines.append(f"| {r['date']} | {r['platform']} | {stream(r)} | {r['persona']} | {r['pillar']} | {r['working_title']} | "
                     f"{r['format']} | {r.get('creator_tier', '')} | {r['kpi']} | {risk} |")
    lines.append("")
    lines.append("**Checks**")
    lines.extend(f"- {f}" for f in findings) if findings else lines.append("- All checks passed.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    rows = load(args.csv)
    md = to_markdown(rows, check(rows))
    if args.out:
        Path(args.out).write_text(md + "\n", encoding="utf-8")
        print(f"Saved to {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
