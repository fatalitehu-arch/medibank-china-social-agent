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
import base64
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
# welcome.html is English only. Source files keep their Chinese; these map it at build time.
EN_SKILLS = {
    "medibank-cn-social": ("Medibank China Social Agent", "Content, creators and compliance for Xiaohongshu, WeChat, Douyin and Weibo",
                           "Make next month's content plan for all five platforms and check compliance."),
    "cn-community-manager": ("Comments & sentiment", "Replies, comments, live Q&A, listening and crisis handling",
                             "How should we reply to these comments?"),
    "cn-compliance-review": ("Compliance review", None, "Check whether this Douyin script can be published."),
    "cn-content-planner": ("Content planner", None, "Build a 4-week, five-platform calendar for the T1 intake."),
    "cn-content-writer": ("Content writer", None, "Write a Xiaohongshu post: how to read the OSHC line on your offer letter."),
    "cn-kol-manager": ("Creator manager", "Find, score, brief and review creators on the official platform marketplaces",
                       "Score the creators in examples/kol_candidates.csv and give me a shortlist."),
    "cn-performance-review": ("Performance review", None, "Write a monthly review from examples/metrics_sample.csv."),
    "cn-repurpose": ("Repurpose", None, "Turn this WeChat article into Xiaohongshu, Channels, Douyin and Weibo versions."),
    "cn-trend-scout": ("Trend radar", None, "What is trending on Chinese social media, and which trends should Medibank ride?"),
    "cn-video-editor": ("Video editor", "Cut, subtitle and brand short videos for Douyin, WeChat Channels and Xiaohongshu",
                        "Cut the three clips in raw/ into a 45-second vertical Douyin video with subtitles and title and end cards."),
}
EN_TERMS = [
    ("《互联网广告管理办法》", "Internet Advertising Measures"), ("《互联网保险业务监管办法》", "Internet Insurance Business Measures"),
    ("IT之家", "IT Home"), ("中国新闻网", "China News"), ("广告", "\"advertisement\""),
    ("看懂你的保险", "Know your cover"), ("在澳洲看病", "Using healthcare"), ("用好 app 和热线", "App and helpline"),
    ("身心健康", "Wellbeing"), ("澳洲保险", "Australian insurance"),
    ('"看懂自己的保险" (Know your own cover)', '"Know your own cover"'), ("小红书 (RED / Xiaohongshu)", "Xiaohongshu (RED)"),
    ("令人心动的offer 第八季", "Heart-Racing Offer, Season 8"), ("闪身步", "\"Flash step\" dance"), ("后会友期", "Friends Reunion show"),
    ("微信公众号", "WeChat Official Account"), ("微信视频号", "WeChat Channels"), ("小红书", "Xiaohongshu"),
    ("公众号", "WeChat OA"), ("视频号", "WeChat Channels"), ("抖音", "Douyin"), ("微博", "Weibo"),
    ("蒲公英", "Pugongying"), ("巨量星图", "Xingtu"), ("互选平台", "Huxuan"), ("微任务", "Weirenwu"),
    ("头部", "Top tier"), ("腰部", "Mid tier"), ("尾部", "Small"), ("安徽花鼓灯", "Anhui flower-drum lantern dance"),
    ('"我画地为牢"', '"I drew my own prison" (a line about self-imposed limits)'),
    ("舆情", ""), ("术语表", ""), ("博主", ""), ("热点", ""), ("看懂自己的保险", ""),
]
EN_HANDLES = {
    "示例_悉尼读研日记": "demo_SydneyMastersDiary", "示例_墨尔本小鹿": "demo_MelbourneDeer",
    "示例_悉尼留学生活号": "demo_SydneyStudentLife", "示例_留学家长课堂": "demo_StudyAbroadParents",
    "示例_留学生阿Ken的一天": "demo_ADayWithKen", "示例_澳洲生活vlog": "demo_AustraliaLifeVlog",
    "示例_澳洲留学那些事": "demo_StudyInAustralia", "示例_UNSW新生说": "demo_UNSWFreshers",
}
CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")


def to_english(text):
    if not isinstance(text, str) or not CJK.search(text):
        return text
    text = EN_HANDLES.get(text, text)
    for zh, en in EN_TERMS:
        text = text.replace(zh, en)
    text = re.sub(r"\s*\(\s*\)|\s*\(\s*\"\s*\"\s*\)", "", text)          # empty brackets left by removals
    text = re.sub(r"\s*[(（][^()（）]*" + CJK.pattern + r"[^()（）]*[)）]", "", text)  # other bracketed Chinese
    text = re.sub(r"^(.+?) \(\1\)$", r"\1", text)                         # "Douyin (Douyin)"
    text = re.sub(r"\s{2,}", " ", text).strip(" :")
    if CJK.search(text):
        raise ValueError(f"welcome.html must be English; add a translation for: {text}")
    return text


def english(obj):
    if isinstance(obj, dict):
        return {k: english(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [english(v) for v in obj]
    return to_english(obj)


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
        name = fm.get("name", "")
        en_name, en_short, en_prompt = EN_SKILLS.get(name, (None, None, None))
        out.append({"name": name, "display_name": en_name or yaml_value(y, "display_name") or name,
                    "short": en_short or yaml_value(y, "short_description") or fm.get("description", ""),
                    "prompt": en_prompt or yaml_value(y, "default_prompt")})
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


def md_table(text, heading):
    """Rows of the first pipe table after a '## heading' line, as lists of cells."""
    part = text.split(heading, 1)[1]
    rows = []
    for line in part.splitlines()[1:]:
        if line.startswith("## "):
            break
        if line.startswith("|") and not line.startswith("|--") and not line.startswith("| ID"):
            rows.append([c.strip() for c in line.strip().strip("|").split(" | ")])
    return rows


def md_links(cell):
    """Turn [text](url) into {'text', 'url'} pieces; strip other markdown."""
    links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", cell)
    plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell).replace("`", "")
    return plain, [{"text": a, "url": b} for a, b in links]


def evidence():
    text = (ROOT / "references" / "evidence.md").read_text(encoding="utf-8")
    facts = []
    for r in md_table(text, "## E: published evidence"):
        source, links = md_links(r[3])
        facts.append({"id": r[0], "finding": r[1], "number": r[2], "source": source, "links": links,
                      "checked": r[4], "reliability": r[5]})
    tests = [{"id": r[0], "assumption": md_links(r[1])[0], "test": r[3], "when": r[4]}
             for r in md_table(text, "## A: working assumptions (to test)")]
    return {"facts": facts, "assumptions": tests}


def examples():
    folder = ROOT / "assets" / "welcome" / "examples"
    pics = {}
    for f in sorted(folder.glob("*.jpg")):
        pics[f.stem] = "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
    return pics


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
        "evidence": evidence(),
    }


def render():
    payload = english(data())
    payload["examples"] = examples()  # images: not text, so not passed through english()
    blob = json.dumps(payload, ensure_ascii=False, indent=1).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    theme = json.loads((ROOT / "assets" / "brand" / "theme.json").read_text(encoding="utf-8"))
    for key, value in theme["colors"].items():
        html = html.replace(f"__C_{key}__", value)
    return html.replace("__DATA__", blob)


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
