#!/usr/bin/env python3
"""Keyword compliance scan for Medibank drafts on Chinese social platforms.

Catches words, not meaning: the agent (or a person) still reads the draft against
references/compliance.md. Rules live in rules.json next to this file.

Usage:
    python compliance_scan.py draft.txt                       # strictest (all platforms)
    python compliance_scan.py draft.txt --platform wechat-oa  # one platform's rules
    echo "文本" | python compliance_scan.py - --platform douyin
    python compliance_scan.py draft.txt --json

Platforms: xiaohongshu, wechat-oa, wechat-channels, douyin, weibo.

Exit code: 0 = green, 1 = amber, 2 = red.
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

RULES_PATH = Path(__file__).with_name("rules.json")
LEVEL_ORDER = {"note": 0, "amber": 1, "red": 2}
VERDICT = {0: "🟢 GREEN", 1: "🟡 AMBER", 2: "🔴 RED"}


@dataclass
class Hit:
    id: str
    level: str
    rule: str
    match: str
    line_no: int
    line: str
    message: str
    fix: str


def load_rules(path=RULES_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for rule in data["rules"]:
        rule["compiled"] = [re.compile(p, re.IGNORECASE) for p in rule["patterns"]]
    return data


def scan(text, rules=None, platform=None):
    """Return (verdict_level, hits). verdict_level is 0, 1 or 2.

    platform=None applies every rule at its base (strictest) level.
    """
    rules = rules or load_rules()
    if platform and platform not in rules.get("platforms", []):
        raise ValueError(f"Unknown platform {platform!r}; use one of {rules.get('platforms')}")
    qualified = any(q in text for q in rules.get("qualifiers", []))
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for rule in rules["rules"]:
            for pattern in rule["compiled"]:
                found = pattern.search(line)
                if not found:
                    continue
                level = rule.get("platform_levels", {}).get(platform, rule["level"])
                if level == "amber" and rule.get("qualifiable") and qualified:
                    level = "note"
                hits.append(Hit(rule["id"], level, rule["rule"], found.group(0),
                                line_no, line.strip(), rule["message"], rule["fix"]))
                break  # one hit per rule per line is enough
    worst = max((LEVEL_ORDER[h.level] for h in hits), default=0)
    return worst, hits


def format_report(worst, hits, platform=None):
    out = [f"平台 Platform: {platform or 'all (strictest)'}", f"结论 Verdict: {VERDICT[worst]}"]
    for level in ("red", "amber", "note"):
        group = [h for h in hits if h.level == level]
        if not group:
            continue
        out.append(f"\n[{level.upper()}] {len(group)}")
        for h in group:
            out.append(f"  L{h.line_no} 「{h.match}」 {h.rule} · {h.message}")
            out.append(f"      line: {h.line[:80]}")
            out.append(f"      fix:  {h.fix}")
    if not hits:
        out.append("No keyword hits. Still read the draft against compliance.md for meaning.")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="draft file, or - for stdin")
    parser.add_argument("--platform", choices=load_rules()["platforms"],
                        help="apply one platform's rules (default: strictest)")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args(argv)

    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    worst, hits = scan(text, platform=args.platform)
    if args.json:
        print(json.dumps({"platform": args.platform, "verdict": ["green", "amber", "red"][worst],
                          "hits": [asdict(h) for h in hits]}, ensure_ascii=False, indent=2))
    else:
        print(format_report(worst, hits, args.platform))
    return worst


if __name__ == "__main__":
    sys.exit(main())
