#!/usr/bin/env python3
"""Style lint for a post, article or caption: titles, hashtags, length, punctuation, AI-flavour.

Complements compliance_scan.py (which checks legal/platform risk). Rules come from
references/style-checks.md.

The note file may use the agent's output markers:
    【正文】 ... 【封面文案】 ... 【标题候选】 ... 【Hashtags】 ...
Without markers the whole file is treated as the body.

Usage:
    python note_lint.py note.txt                       # default platform: xiaohongshu
    python note_lint.py article.txt --platform wechat-oa
Exit code: 0 = no errors (warnings allowed), 1 = errors.
"""

import argparse
import re
import sys
from pathlib import Path

SECTION = re.compile(r"【(平台|正文|脚本|封面文案|标题候选|Hashtags|配图建议|分镜|合规结论|需要 Medibank 确认)】")
AI_PHRASES = ["说白了", "本质上", "这意味着", "值得注意的是", "不难发现", "综上所述", "总的来说",
              "首先", "其次", "让我们", "在当今", "随着", "希望对你有帮助", "不可否认", "换句话说"]
TITLE_BANNED = ["干货", "必看", "超实用", "一定要收藏", "震惊"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

# Per-platform specs from references/platforms/*.md and references/style-checks.md.
# body = (min, max) chars; title = max chars; tags = (min, max); headings = sub-heads allowed.
SPECS = {
    "xiaohongshu":     {"body": (150, 1000), "title": 20, "tags": (5, 10), "headings": False},
    "wechat-oa":       {"body": (800, 3000), "title": 30, "tags": (0, 5), "headings": True},
    "wechat-channels": {"body": (20, 300), "title": 30, "tags": (0, 5), "headings": False},
    "douyin":          {"body": (10, 300), "title": 55, "tags": (3, 5), "headings": False},
    "weibo":           {"body": (10, 140), "title": 30, "tags": (1, 3), "headings": False},
}


def split_sections(text):
    parts = SECTION.split(text)
    if len(parts) == 1:
        return {"正文": text}
    sections = {}
    for name, body in zip(parts[1::2], parts[2::2]):
        sections[name] = body.strip()
    return sections


def numbered_lines(block):
    lines = [re.sub(r"^\s*(\d+[.、)]|[-*])\s*", "", l).strip() for l in block.splitlines()]
    return [l for l in lines if l]


def cjk_len(s):
    return len(re.sub(r"\s", "", s))


def lint(text, platform="xiaohongshu"):
    """Return a list of (level, message). level is 'error' or 'warn'."""
    spec = SPECS[platform]
    out = []
    sec = split_sections(text)
    body = sec.get("正文", sec.get("脚本", ""))

    n = cjk_len(body)
    lo, hi = spec["body"]
    if n < lo:
        out.append(("warn", f"Body is short for {platform} ({n} chars; expected {lo}–{hi})."))
    elif n > hi:
        level = "error" if platform == "weibo" else "warn"
        out.append((level, f"Body is long for {platform} ({n} chars; expected {lo}–{hi})."))

    for phrase in AI_PHRASES:
        if phrase in body:
            out.append(("warn", f"AI-flavour phrase 「{phrase}」 in body."))
    if re.search(r"[一-鿿],|,[一-鿿]", body):
        out.append(("warn", "Half-width comma inside Chinese text; use ，"))
    if "——" in body:
        out.append(("warn", "Long dash —— in body; use a comma or full stop."))
    if re.search(r"[！!？?]{3,}", text):
        out.append(("warn", "Stacked punctuation (！！！/？？？)."))
    if not spec["headings"] and re.search(r"^\s*#{1,6}\s|\*\*", body, re.M):
        out.append(("warn", f"Markdown heading or bold in body; {platform} shows it as raw symbols."))

    titles = numbered_lines(sec.get("标题候选", ""))
    if "标题候选" in sec:
        if not 3 <= len(titles) <= 5:
            out.append(("warn", f"{len(titles)} titles; give 3–5."))
        for t in titles:
            if cjk_len(t) > spec["title"]:
                out.append(("error", f"Title over {spec['title']} chars for {platform}: 「{t}」"))
            if EMOJI.search(t):
                out.append(("error", f"Emoji in title: 「{t}」"))
            for w in TITLE_BANNED:
                if w in t:
                    out.append(("error", f"Banned filler 「{w}」 in title: 「{t}」"))

    covers = numbered_lines(sec.get("封面文案", ""))
    for c in covers:
        if cjk_len(c) > 12:
            out.append(("warn", f"Cover line over 12 chars: 「{c}」"))

    if "Hashtags" in sec:
        tags = re.findall(r"#[^\s#]+#?", sec["Hashtags"])
        lo, hi = spec["tags"]
        if not lo <= len(tags) <= hi:
            out.append(("warn", f"{len(tags)} hashtags; {platform} uses {lo}–{hi}."))
        if len(set(tags)) != len(tags):
            out.append(("warn", "Duplicate hashtags."))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="note file, or - for stdin")
    parser.add_argument("--platform", choices=sorted(SPECS), default="xiaohongshu")
    args = parser.parse_args(argv)
    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    results = lint(text, args.platform)
    for level, msg in results:
        print(f"[{level.upper()}] {msg}")
    errors = sum(1 for level, _ in results if level == "error")
    print(f"\n{errors} error(s), {len(results) - errors} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
