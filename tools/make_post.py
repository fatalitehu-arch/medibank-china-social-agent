#!/usr/bin/env python3
"""Turn a post spec (JSON) into a ready-to-publish post: copy-paste text, image cards and a compliance check.

The agent (cn-content-writer) writes the spec; this script does the rest:
  1. runs compliance_scan.py and note_lint.py on the text,
  2. renders the cover and content cards as PNG in Medibank colours (assets/brand/theme.json),
  3. writes post.md with everything to paste into the platform.

Spec (see examples/post_spec.json):
    {"platform": "xiaohongshu", "pillar": "看懂你的保险", "account": "brand" | "creator",
     "title": "...", "titles": ["..."], "body": "...", "hashtags": ["#澳洲留学"],
     "cover": {"headline": "拿到offer\\n先看这一栏", "sub": "3 分钟看懂你的 OSHC"},
     "cards": [{"heading": "第一步", "body": "..."}],
     "end": {"line": "以保单条款为准", "next": "去学校官网搜 OSHC", "question": "..."},
     "evidence": ["E-3", "E-10"]}

Usage:
    python tools/make_post.py examples/post_spec.json                 # writes outputs/posts/<slug>/
    python tools/make_post.py spec.json --out my_folder --font /path/to/font.ttc
Needs Pillow (pip install Pillow) and a font with Chinese characters (found automatically on
macOS and Windows; pass --font elsewhere). Exit code 1 if the compliance verdict is red.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import compliance_scan  # noqa: E402
import note_lint  # noqa: E402

THEME = json.loads((ROOT / "assets" / "brand" / "theme.json").read_text(encoding="utf-8"))
C = THEME["colors"]
SIZES = {  # width, height of each card
    "xiaohongshu": (1080, 1440),
    "douyin": (1080, 1920),
    "wechat-channels": (1080, 1920),
    "weibo": (1080, 1080),
    "wechat-oa": (900, 383),
}


def find_font(explicit=None):
    for path in ([explicit] if explicit else []) + THEME["fonts"]:
        if path and Path(path).exists():
            return path
    raise SystemExit("No Chinese font found. Pass --font /path/to/a/font.ttc (e.g. PingFang, Microsoft YaHei, Noto Sans CJK).")


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def wrap(draw, text, font, width):
    """Wrap Chinese/English text to a pixel width; keeps explicit line breaks."""
    lines = []
    for para in text.split("\n"):
        line = ""
        for token in re.findall(r"[A-Za-z0-9@#%&+./:'-]+|\s|.", para):
            trial = line + token
            if draw.textlength(trial, font=font) <= width or not line:
                line = trial
            else:
                lines.append(line.rstrip())
                line = token.lstrip()
        lines.append(line.rstrip())
    return lines


class Renderer:
    def __init__(self, platform, font_path, account):
        from PIL import Image, ImageDraw, ImageFont  # imported here so the rest works without Pillow
        self.Image, self.ImageDraw, self.ImageFont = Image, ImageDraw, ImageFont
        self.w, self.h = SIZES[platform]
        self.font_path, self.account, self.platform = font_path, account, platform
        self.s = self.w / 1080  # scale for small formats

    def font(self, size):
        return self.ImageFont.truetype(self.font_path, int(size * self.s))

    def text_block(self, draw, xy, text, size, fill, width, spacing=1.35):
        f = self.font(size)
        x, y = xy
        for line in wrap(draw, text, f, width):
            draw.text((x, y), line, font=f, fill=fill)
            y += int(size * self.s * spacing)
        return y

    def footer(self, draw, page, total, dark):
        f = self.font(30)
        color = rgb(C["soft"]) if dark else rgb(C["muted"])
        label = "Medibank OSHC · 留学生健康科普" if self.account == "brand" else "以保单条款为准"
        draw.text((int(72 * self.s), self.h - int(90 * self.s)), label, font=f, fill=color)
        if total > 1:
            num = f"{page}/{total}"
            draw.text((self.w - int(72 * self.s) - draw.textlength(num, font=f), self.h - int(90 * self.s)),
                      num, font=f, fill=color)

    def cover(self, spec, total):
        img = self.Image.new("RGB", (self.w, self.h), rgb(C["primary"]))
        d = self.ImageDraw.Draw(img)
        r = int(self.w * 0.55)
        d.ellipse((self.w - r * 0.9, -r * 0.35, self.w + r * 0.6, r * 1.15), fill=rgb(C["primary_dark"]))
        d.ellipse((-r * 0.5, self.h - r * 0.6, r * 0.6, self.h + r * 0.5), fill=rgb(C["accent"]))
        pad = int(72 * self.s)
        y = int(self.h * (0.12 if self.h > self.w else 0.14))
        chip = spec.get("pillar", "")
        if chip:
            f = self.font(34)
            tw = d.textlength(chip, font=f)
            d.rounded_rectangle((pad, y, pad + tw + 48 * self.s, y + 64 * self.s), radius=int(32 * self.s), fill=rgb(C["highlight"]))
            d.text((pad + 24 * self.s, y + 12 * self.s), chip, font=f, fill=rgb(C["ink"]))
            y += int(120 * self.s)
        size = 140 if self.h >= self.w else 64
        y = self.text_block(d, (pad, y), spec["cover"]["headline"], size, rgb(C["paper"]), self.w - 2 * pad, 1.2)
        if spec["cover"].get("sub"):
            self.text_block(d, (pad, y + int(30 * self.s)), spec["cover"]["sub"], size * 0.42, rgb(C["soft"]), self.w - 2 * pad)
        self.footer(d, 1, total, dark=True)
        return img

    def card(self, card, page, total):
        img = self.Image.new("RGB", (self.w, self.h), rgb(C["paper"]))
        d = self.ImageDraw.Draw(img)
        pad = int(72 * self.s)
        d.rectangle((0, 0, self.w, int(18 * self.s)), fill=rgb(C["primary"]))
        y = int(110 * self.s)
        n = str(page - 1)
        dia = int(96 * self.s)
        d.ellipse((pad, y, pad + dia, y + dia), fill=rgb(C["primary"]))
        f = self.font(52)
        d.text((pad + (dia - d.textlength(n, font=f)) / 2, y + dia * 0.18), n, font=f, fill=rgb(C["paper"]))
        y = self.text_block(d, (pad + dia + int(32 * self.s), y + int(14 * self.s)), card["heading"], 60,
                            rgb(C["ink"]), self.w - 2 * pad - dia - 32 * self.s, 1.2)
        y = max(y, int(110 * self.s) + dia) + int(50 * self.s)
        inner = self.w - 2 * pad - int(88 * self.s)
        body_size = 52 if self.h >= self.w else 30
        lines = wrap(d, card["body"], self.font(body_size), inner)
        box_h = int(len(lines) * body_size * self.s * 1.55 + 88 * self.s)
        d.rounded_rectangle((pad, y, self.w - pad, y + box_h), radius=int(28 * self.s), fill=rgb(C["soft"]))
        self.text_block(d, (pad + int(44 * self.s), y + int(44 * self.s)), card["body"], body_size, rgb(C["ink"]), inner, 1.55)
        if card.get("tip"):
            self.text_block(d, (pad, y + box_h + int(48 * self.s)), "提示：" + card["tip"],
                            40, rgb(C["primary"]), self.w - 2 * pad)
        # large faint step number fills the lower part of tall cards
        if self.h > self.w and y + box_h < self.h * 0.62:
            big = self.font(520)
            d.text((self.w - pad - d.textlength(n, font=big), self.h - int(760 * self.s)), n, font=big, fill=rgb(C["soft"]))
        self.footer(d, page, total, dark=False)
        return img

    def end(self, end, page, total):
        img = self.Image.new("RGB", (self.w, self.h), rgb(C["soft"]))
        d = self.ImageDraw.Draw(img)
        pad = int(72 * self.s)
        y = int(self.h * 0.32)
        if end.get("next"):
            self.text_block(d, (pad, y - int(70 * self.s)), "下一步", 38, rgb(C["accent"]), self.w - 2 * pad)
            y = self.text_block(d, (pad, y), end["next"], 76, rgb(C["primary"]), self.w - 2 * pad, 1.25) + int(60 * self.s)
        if end.get("question"):
            y = self.text_block(d, (pad, y), end["question"], 46, rgb(C["ink"]), self.w - 2 * pad) + int(40 * self.s)
        if end.get("line"):
            self.text_block(d, (pad, y), end["line"], 36, rgb(C["muted"]), self.w - 2 * pad)
        self.footer(d, page, total, dark=False)
        return img


def post_text(spec):
    """The text block note_lint and compliance_scan expect, also used for post.md."""
    lines = [f"【平台】 {spec['platform']}", "【正文】", spec["body"].strip()]
    if spec.get("cover"):
        lines += ["【封面文案】", "1. " + spec["cover"]["headline"].replace("\n", "")]
    titles = spec.get("titles") or [spec["title"]]
    lines += ["【标题候选】"] + [f"{i}. {t}" for i, t in enumerate(titles, 1)]
    if spec.get("hashtags"):
        lines += ["【Hashtags】", " ".join(spec["hashtags"])]
    return "\n".join(lines) + "\n"


def slugify(text):
    return re.sub(r"[^\w一-鿿]+", "-", text).strip("-")[:40] or "post"


def build(spec, out_dir, font=None, render=True):
    out_dir.mkdir(parents=True, exist_ok=True)
    text = post_text(spec)
    all_text = "\n".join([text, json.dumps(spec.get("cards", []), ensure_ascii=False),
                          json.dumps(spec.get("end", {}), ensure_ascii=False), spec.get("cover", {}).get("sub", "")])
    worst, hits = compliance_scan.scan(all_text, platform=spec["platform"])
    lint = note_lint.lint(text, spec["platform"])
    report = compliance_scan.format_report(worst, hits, spec["platform"])
    report += "\n\nStyle lint:\n" + ("\n".join(f"  {lvl}: {msg}" for lvl, msg in lint) or "  clean")
    (out_dir / "compliance.txt").write_text(report + "\n", encoding="utf-8")

    images = []
    if render and spec["platform"] in SIZES:
        r = Renderer(spec["platform"], find_font(font), spec.get("account", "brand"))
        cards = spec.get("cards", []) if spec["platform"] != "wechat-oa" else []
        total = 1 + len(cards) + (1 if spec.get("end") and cards else 0)
        pages = [r.cover(spec, total)]
        pages += [r.card(c, i + 2, total) for i, c in enumerate(cards)]
        if spec.get("end") and cards:
            pages.append(r.end(spec["end"], total, total))
        for i, img in enumerate(pages, 1):
            name = f"{i:02d}.png"
            img.save(out_dir / name)
            images.append(name)

    verdict = compliance_scan.VERDICT[worst]
    md = [f"# {spec['title']}", "",
          f"Platform: {spec['platform']} · Account: {spec.get('account', 'brand')} · Pillar: {spec.get('pillar', '')}",
          f"Compliance: {verdict} (details in compliance.txt)", ""]
    if spec.get("evidence"):
        md += [f"Why this post works: {', '.join(spec['evidence'])} (references/evidence.md)", ""]
    md += ["## 标题 Title", "", spec["title"], ""]
    if spec.get("titles"):
        md += ["Other options: " + " / ".join(t for t in spec["titles"] if t != spec["title"]), ""]
    md += ["## 正文 Body (copy as is)", "", spec["body"].strip(), ""]
    if spec.get("hashtags"):
        md += ["## 话题 Hashtags", "", " ".join(spec["hashtags"]), ""]
    if images:
        md += ["## 图片 Images (upload in this order)", ""] + [f"{i}. ![{n}]({n})" for i, n in enumerate(images, 1)] + [""]
    if spec.get("account") == "creator":
        md += ["## Before publishing", "", "Book through the platform marketplace so the post carries its 广告/合作 label (PL-1, E-12).", ""]
    (out_dir / "post.md").write_text("\n".join(md), encoding="utf-8")
    return worst, images


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("spec", help="post spec JSON file")
    parser.add_argument("--out", help="output folder (default outputs/posts/<slug>)")
    parser.add_argument("--font", help="path to a font with Chinese characters")
    parser.add_argument("--no-images", action="store_true", help="text and compliance only")
    args = parser.parse_args(argv)
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    for key in ("platform", "title", "body"):
        if not spec.get(key):
            raise SystemExit(f"Spec is missing '{key}'.")
    out = Path(args.out) if args.out else ROOT / "outputs" / "posts" / slugify(spec["title"])
    worst, images = build(spec, out, args.font, render=not args.no_images)
    print(f"Wrote {out}: post.md, compliance.txt" + (f", {len(images)} images" if images else ""))
    print(f"Compliance: {compliance_scan.VERDICT[worst]}")
    return 1 if worst >= 2 else 0


if __name__ == "__main__":
    sys.exit(main())
