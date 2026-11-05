#!/usr/bin/env python3
"""Build welcome.html, the page that shows what the agent contains, from the repository.

It reads the skills, the knowledge base, the compliance rules, the trend radar and the
creator library, and fills assets/welcome/template.html. Re-run it after changing any of
them; CI fails if welcome.html is out of date.

Usage:
    python build_welcome.py            # write welcome.html
    python build_welcome.py --check    # exit 1 if welcome.html is stale
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import creator_dashboard  # noqa: E402
import kol_score  # noqa: E402

TEMPLATE = ROOT / "assets" / "welcome" / "template.html"
OUT = ROOT / "welcome.html"

KB_GROUPS = [
    ("Rules & compliance", ["compliance.md", "crisis-playbook.md", "creator-contract-terms.md"]),
    ("Strategy & audience", ["student-strategy.md", "personas.md", "brand-facts.md", "market-landscape.md"]),
    ("Content", ["content-playbook.md", "style-checks.md", "glossary.md"]),
    ("Platforms", ["platforms/"]),
    ("Creators & trends", ["kol-playbook.md", "trend-playbook.md", "trend-radar.md"]),
]
WEIGHT_LABELS = {"audience": "Audience fit", "engagement": "Engagement quality", "relevance": "Topic relevance",
                 "trust": "Trust & safety", "cost": "Cost efficiency"}


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    return dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line) if m else {}


def yaml_value(text, key):
    m = re.search(rf'^\s*{key}:\s*"(.*)"\s*$', text, re.M)
    return m.group(1) if m else ""


def skills():
    out = []
    for skill_md in [ROOT / "SKILL.md"] + sorted((ROOT / "skills").glob("*/SKILL.md")):
        fm = frontmatter(skill_md)
        meta = skill_md.parent / "agents" / "openai.yaml"
        y = meta.read_text(encoding="utf-8") if meta.exists() else ""
        out.append({"name": fm.get("name", ""), "display_name": yaml_value(y, "display_name") or fm.get("name", ""),
                    "short": yaml_value(y, "short_description") or fm.get("description", ""),
                    "prompt": yaml_value(y, "default_prompt")})
    return out


def group_of(rel):
    for group, names in KB_GROUPS:
        if any(rel == n or (n.endswith("/") and rel.startswith(n)) for n in names):
            return group
    return "Other"


def knowledge():
    out = []
    for f in sorted((ROOT / "references").rglob("*.md")):
        rel = f.relative_to(ROOT / "references").as_posix()
        title = next((line.lstrip("# ").strip() for line in f.read_text(encoding="utf-8").splitlines()
                      if line.startswith("# ")), rel)
        out.append({"path": f"references/{rel}", "title": title, "group": group_of(rel)})
    return out


def tools():
    out = []
    for f in sorted((ROOT / "tools").glob("*.py")):
        doc = ast.get_docstring(ast.parse(f.read_text(encoding="utf-8"))) or ""
        out.append({"name": f"tools/{f.name}", "doc": doc.splitlines()[0] if doc else ""})
    return out


def rule_count():
    text = (ROOT / "references" / "compliance.md").read_text(encoding="utf-8")
    return len(set(re.findall(r"^\| ((?:CN|PL|AU|TR)-\d+) \|", text, re.M)))


def trends():
    text = (ROOT / "references" / "trend-radar.md").read_text(encoding="utf-8")
    snap = re.search(r"Snapshot: (\d{4}-\d{2}-\d{2})", text)
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) == 4 and cells[0] not in ("Trend",) and not cells[0].startswith("-"):
            rows.append(dict(zip(["trend", "what", "where", "verdict"], cells)))
    return {"snapshot": snap.group(1) if snap else None, "rows": rows}


def data():
    roster = creator_dashboard.load(ROOT / "creators" / "roster.csv")
    posts = creator_dashboard.load(ROOT / "creators" / "posts.csv")
    return {
        "skills": skills(),
        "knowledge": knowledge(),
        "kb_groups": [g for g, _ in KB_GROUPS],
        "tools": tools(),
        "rule_count": rule_count(),
        "trends": trends(),
        "criteria": {"weights": [{"label": WEIGHT_LABELS.get(k, k), "weight": v} for k, v in kol_score.WEIGHTS.items()],
                     "hard_stops": list(kol_score.HARD_STOPS.values())},
        "dashboard": creator_dashboard.build(roster, posts, creator_dashboard.as_of(posts)),
    }


def render():
    blob = json.dumps(data(), ensure_ascii=False, indent=1).replace("</", "<\\/")
    return TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", blob)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    html = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != html:
            print("welcome.html is out of date: run python tools/build_welcome.py")
            return 1
        print("welcome.html is up to date")
        return 0
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
