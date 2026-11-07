#!/usr/bin/env python3
"""Animated explainer video in Medibank colours, no footage needed: text that pops in, icons, mock app screens, step lists, key-word highlights, synthesised sound effects and burned-in subtitles.

The agent (cn-video-editor) writes a storyboard; this script renders it with Pillow + ffmpeg.

Storyboard (see examples/motion_storyboard.json):
    {"platform": "douyin", "account": "brand",
     "scenes": [
       {"seconds": 3, "bg": "red",                       # red | white | cream | soft | ink
        "section": "情况 1：小病",                        # optional black pill at the top
        "items": [
          {"type": "text", "text": "在澳洲看病\\n钱怎么{报}？", "size": 120, "y": 0.32, "at": 0, "anim": "pop"},
          {"type": "icon", "name": "thermometer", "x": 0.3, "y": 0.62, "size": 240, "at": 0.4, "anim": "pop"},
          {"type": "card", "icon": "phone", "label": "小病", "sub": "先线上问", "x": 0.28, "y": 0.5, "anim": "slide-left"},
          {"type": "phone", "y": 0.5, "screens": [{"at": 0, "title": "Medibank OSHC", "rows": ["我的保障", "Online Doctor"], "hl": 1}]},
          {"type": "steps", "items": ["登录 App", "点 Make a claim"], "at": 0.3, "interval": 1.2},
          {"type": "note", "text": "试行服务 · 16 岁以上 · 家属不适用"}],
        "subs": [[0, "留学生在澳洲看病"], [1.5, "钱怎么{报}？"]],    # or one string for the whole scene
        "sfx": [{"at": 0, "name": "whoosh"}]}],                    # whoosh | pop | ding | click | success
     "fine_print": "具体保障以保单条款为准"}                         # optional line on every frame

Text markup: {word} draws the word on a yellow highlight. anim: pop | slide-left | slide-right | slide-up | fade | none.
Items can also take "until" (seconds in the scene) to leave, and "sfx" to play a sound when they enter
(pop animations play "pop" by default; "sfx": null for silence).

Before rendering, every on-screen word goes through tools/compliance_scan.py and the claim
qualifier rules in assets/brand/qualifiers.json (e.g. "免费" for Online Doctor must say 试行 / 16 岁以上 /
家属不适用). A red result stops the render.

Usage:
    python tools/motion_video.py examples/motion_storyboard.json                # → outputs/videos/<name>.mp4
    python tools/motion_video.py board.json --pack                              # + 剪映 asset pack folder
    python tools/motion_video.py board.json --check                             # text checks only, no render
    python tools/motion_video.py board.json --frames 2,9.5,30 --out preview.mp4 # PNG stills at those seconds
Needs Pillow and ffmpeg.
"""

import argparse
import csv
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import compliance_scan  # noqa: E402

THEME = json.loads((ROOT / "assets" / "brand" / "theme.json").read_text(encoding="utf-8"))
C = THEME["colors"]
QUALIFIERS = ROOT / "assets" / "brand" / "qualifiers.json"
SIZES = {"douyin": (1080, 1920), "wechat-channels": (1080, 1920), "xiaohongshu": (1080, 1440), "weibo": (1080, 1920)}
FPS = 30
SUB_MAX = 16  # Chinese characters per subtitle line (Latin counts half)
BGS = {"red": "primary", "white": "paper", "cream": "accent", "soft": "soft", "ink": "ink"}

SFX = {  # synthesised with ffmpeg, no licensed audio needed
    "whoosh": "anoisesrc=d=0.5:c=pink:r=48000:a=0.5,highpass=f=600,lowpass=f=6000,"
              "afade=t=in:d=0.18:curve=exp,afade=t=out:st=0.18:d=0.32,volume=0.9",
    "pop": "aevalsrc='0.7*sin(2*PI*(280+1400*t)*t)*exp(-22*t)':d=0.22:s=48000",
    "ding": "aevalsrc='0.45*sin(2*PI*1568*t)*exp(-4.5*t)+0.2*sin(2*PI*3136*t)*exp(-7*t)"
            "+0.1*sin(2*PI*4704*t)*exp(-9*t)':d=1.1:s=48000",
    "click": "aevalsrc='0.8*sin(2*PI*1900*t)*exp(-70*t)+0.3*sin(2*PI*700*t)*exp(-50*t)':d=0.08:s=48000",
    "success": "aevalsrc='0.4*sin(2*PI*1046*t)*exp(-6*t)+gte(t,0.13)*0.45*sin(2*PI*1568*(t-0.13))*exp(-4*(t-0.13))'"
               ":d=1.2:s=48000",
}


# --- helpers ---------------------------------------------------------------------------

def rgb(hex_color, alpha=255):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def color(name):
    return rgb(C.get(name, name) if not str(name).startswith("#") else name)


def find_font(explicit=None):
    for path in ([explicit] if explicit else []) + THEME["fonts"]:
        if path and Path(path).exists():
            return path
    raise SystemExit("No Chinese font found. Pass --font /path/to/a/font.ttc")


def ease_out_back(p):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def plain(text):
    return text.replace("{", "").replace("}", "")


def segments(text):
    """'钱怎么{报}？' -> [('钱怎么', False), ('报', True), ('？', False)]."""
    return [(s.strip("{}"), s.startswith("{")) for s in re.findall(r"\{[^}]*\}|[^{]+", text) if s.strip("{}")]


def sub_width(line):
    """Subtitle length in Chinese-character widths (Latin letters, digits and spaces count half)."""
    return sum(0.5 if ord(ch) < 0x2E80 else 1 for ch in line)


def scene_subs(scene):
    subs = scene.get("subs") or []
    if isinstance(subs, str):
        return [[0.0, subs]]
    return sorted(([float(t), s] for t, s in subs), key=lambda x: x[0])


def all_text(board):
    """Every word that will be on screen, one line per piece (for compliance and qualifier checks)."""
    out = []
    for scene in board["scenes"]:
        if scene.get("section"):
            out.append(scene["section"])
        for item in scene.get("items", []):
            if item["type"] == "phone":
                out.append("[phone] 示意图，以 App 实际界面为准")
                for screen in item.get("screens", []):
                    out += [screen.get("title", "")] + [plain(r) for r in screen.get("rows", [])]
            for key in ("text", "label", "sub"):
                if item.get(key):
                    out.append(plain(item[key]))
            out += [plain(s) for s in item.get("items", []) if isinstance(s, str)]
        out += [plain(s) for _, s in scene_subs(scene)]
    if board.get("fine_print"):
        out.append(board["fine_print"])
    return [line.replace("\n", " ") for line in out if line]


def check_qualifiers(lines, path=QUALIFIERS):
    """Return problems: a claim (trigger + context) on screen without every qualifier it needs."""
    rules = json.loads(Path(path).read_text(encoding="utf-8"))["rules"]
    text = "\n".join(lines)
    problems = []
    for rule in rules:
        hit = next((t for t in rule["triggers"] if t in text), None)
        if not hit:
            continue
        if rule.get("context") and not any(c in text for c in rule["context"]):
            continue
        missing = [group for group in rule["require"] if not any(q in text for q in group)]
        if missing:
            need = " / ".join("「" + "」或「".join(g) + "」" for g in missing)
            problems.append(f"{rule['id']} {rule['claim']}: '{hit}' is on screen but the video never says {need}. "
                            f"Source: {rule['source']}")
    return problems


def check_board(board, platform=None):
    """Compliance scan + qualifier rules + subtitle length. Returns (worst level 0-2, report lines)."""
    lines = all_text(board)
    worst, hits = compliance_scan.scan("\n".join(lines), platform=platform)
    report = [compliance_scan.format_report(worst, hits, platform)] if hits else ["Compliance scan: green"]
    problems = check_qualifiers(lines)
    for scene_no, scene in enumerate(board["scenes"], 1):
        for _, sub in scene_subs(scene):
            for line in plain(sub).split("\n"):
                if sub_width(line) > SUB_MAX:
                    problems.append(f"Scene {scene_no}: subtitle line over {SUB_MAX} characters: {line}")
    if problems:
        worst = 2
        report += ["Claim and subtitle checks: red"] + ["  - " + p for p in problems]
    else:
        report.append("Claim qualifiers and subtitle length: OK")
    return worst, report


# --- drawing ---------------------------------------------------------------------------

class Painter:
    def __init__(self, size, font_path):
        from PIL import Image, ImageDraw, ImageFont
        self.Image, self.ImageDraw, self.ImageFont = Image, ImageDraw, ImageFont
        self.w, self.h = size
        self.font_path = font_path
        self._fonts = {}

    def font(self, size):
        size = int(size)
        if size not in self._fonts:
            self._fonts[size] = self.ImageFont.truetype(self.font_path, size)
        return self._fonts[size]

    def canvas(self, w, h):
        return self.Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))

    # rich text: {word} on a yellow highlight, bold via stroke
    def rich_text(self, text, size, fill, max_w=None, stroke=None, align="center", line_gap=1.28):
        max_w = max_w or self.w - 160
        f = self.font(size)
        bold = max(1, size // 40)
        d = self.ImageDraw.Draw(self.canvas(1, 1))
        lines = []
        for para in text.split("\n"):
            line, width = [], 0
            for seg, hl in segments(para):
                for ch in re.findall(r"[A-Za-z0-9/.+%'-]+|.", seg):
                    cw = d.textlength(ch, font=f)
                    if width + cw > max_w and line:
                        lines.append(line)
                        line, width = [], 0
                    if line and line[-1][1] == hl:
                        line[-1] = (line[-1][0] + ch, hl)
                    else:
                        line.append((ch, hl))
                    width += cw
            lines.append(line)
        lh = int(size * line_gap)
        pad = int(size * 0.18)
        widths = [sum(d.textlength(s, font=f) for s, _ in ln) for ln in lines]
        img = self.canvas(max(widths + [1]) + 2 * pad + 20, lh * len(lines) + 2 * pad)
        draw = self.ImageDraw.Draw(img)
        for i, ln in enumerate(lines):
            x = pad + 10 + ((img.width - 2 * pad - 20 - widths[i]) / 2 if align == "center" else 0)
            y = pad + i * lh
            for seg, hl in ln:
                sw = draw.textlength(seg, font=f)
                if hl:
                    draw.rounded_rectangle((x - pad * 0.6, y - pad * 0.15, x + sw + pad * 0.6, y + size * 1.12),
                                           radius=int(size * 0.18), fill=color("highlight"))
                    ink = color("ink")
                    draw.text((x, y), seg, font=f, fill=ink, stroke_width=bold, stroke_fill=ink)
                else:
                    if stroke:
                        draw.text((x, y), seg, font=f, fill=fill, stroke_width=stroke[0], stroke_fill=stroke[1])
                    draw.text((x, y), seg, font=f, fill=fill, stroke_width=bold, stroke_fill=fill)
                x += sw
        return img

    def pill(self, text, size=46, bg="ink", fg="paper", tag=None):
        f = self.font(size)
        d = self.ImageDraw.Draw(self.canvas(1, 1))
        tw = d.textlength(text, font=f)
        tag_w = d.textlength(tag, font=f) + size * 0.9 if tag else 0
        h = int(size * 1.9)
        img = self.canvas(tw + tag_w + size * 1.4, h)
        draw = self.ImageDraw.Draw(img)
        draw.rounded_rectangle((0, 0, img.width - 1, h - 1), radius=h // 2, fill=color(bg))
        x = size * 0.7
        if tag:
            draw.rounded_rectangle((size * 0.25, size * 0.25, size * 0.25 + tag_w, h - size * 0.25),
                                   radius=int(h * 0.35), fill=color("primary"))
            draw.text((size * 0.25 + size * 0.45, (h - size * 1.2) / 2), tag, font=f, fill=color("paper"))
            x = size * 0.25 + tag_w + size * 0.4
        draw.text((x, (h - size * 1.2) / 2), text, font=f, fill=color(fg), stroke_width=1, stroke_fill=color(fg))
        return img

    def icon(self, name, size, fg="primary", bg="paper", ring=True):
        S = int(size)
        img = self.canvas(S, S)
        d = self.ImageDraw.Draw(img)
        fgc, bgc = color(fg), color(bg)
        if ring:
            d.ellipse((0, 0, S - 1, S - 1), fill=bgc)
        u = S / 100  # draw on a 100-unit grid
        lw = max(3, int(6 * u))

        def R(x0, y0, x1, y1):
            return (x0 * u, y0 * u, x1 * u, y1 * u)
        if name == "thermometer":
            d.rounded_rectangle(R(43, 18, 57, 66), radius=int(7 * u), outline=fgc, width=lw)
            d.ellipse(R(36, 58, 64, 86), fill=fgc)
            d.rectangle(R(47, 40, 53, 66), fill=fgc)
            for y in (28, 36, 44):
                d.line(R(59, y, 66, y), fill=fgc, width=max(2, lw // 2))
        elif name == "wallet":
            d.rounded_rectangle(R(18, 32, 82, 76), radius=int(8 * u), fill=fgc)
            d.rounded_rectangle(R(24, 24, 70, 36), radius=int(5 * u), fill=fgc)
            d.rounded_rectangle(R(60, 46, 86, 62), radius=int(6 * u), fill=bgc)
            d.ellipse(R(66, 51, 72, 57), fill=fgc)
        elif name == "phone":
            d.rounded_rectangle(R(32, 14, 68, 86), radius=int(8 * u), outline=fgc, width=lw)
            d.rounded_rectangle(R(44, 20, 56, 24), radius=int(2 * u), fill=fgc)
            d.ellipse(R(46, 74, 54, 82), fill=fgc)
        elif name == "video":
            d.rounded_rectangle(R(16, 32, 66, 70), radius=int(8 * u), fill=fgc)
            d.polygon([(64 * u, 51 * u), (84 * u, 36 * u), (84 * u, 66 * u)], fill=fgc)
            d.ellipse(R(30, 42, 44, 56), fill=bgc)
        elif name == "clinic":
            d.rectangle(R(22, 40, 78, 80), fill=fgc)
            d.polygon([(16 * u, 42 * u), (50 * u, 18 * u), (84 * u, 42 * u)], fill=fgc)
            d.rectangle(R(45, 47, 55, 73), fill=bgc)
            d.rectangle(R(37, 55, 63, 65), fill=bgc)
        elif name == "receipt":
            pts = [(28 * u, 16 * u), (72 * u, 16 * u), (72 * u, 84 * u)]
            for i in range(6):
                x = 72 - (i + 0.5) * 44 / 6
                pts += [(x * u, (78 if i % 2 == 0 else 84) * u)]
            pts += [(28 * u, 84 * u)]
            d.polygon(pts, fill=fgc)
            for y in (30, 42, 54):
                d.line(R(36, y, 64 if y != 54 else 52, y), fill=bgc, width=lw)
        elif name == "card":
            d.rounded_rectangle(R(14, 28, 86, 74), radius=int(8 * u), fill=fgc)
            d.rectangle(R(14, 38, 86, 48), fill=bgc)
            d.rounded_rectangle(R(22, 56, 38, 66), radius=int(2 * u), fill=color("highlight"))
        elif name == "check":
            d.line([(28 * u, 52 * u), (44 * u, 68 * u), (74 * u, 34 * u)], fill=fgc, width=int(10 * u), joint="curve")
        elif name == "clock":
            d.ellipse(R(18, 18, 82, 82), outline=fgc, width=lw)
            d.line(R(50, 50, 50, 30), fill=fgc, width=lw)
            d.line(R(50, 50, 64, 58), fill=fgc, width=lw)
        elif name == "camera":
            d.rounded_rectangle(R(16, 32, 84, 76), radius=int(8 * u), fill=fgc)
            d.rectangle(R(36, 24, 64, 34), fill=fgc)
            d.ellipse(R(36, 40, 64, 68), fill=bgc)
            d.ellipse(R(43, 47, 57, 61), fill=fgc)
        elif name == "upload":
            d.line(R(50, 70, 50, 26), fill=fgc, width=int(9 * u))
            d.polygon([(32 * u, 42 * u), (50 * u, 22 * u), (68 * u, 42 * u)], fill=fgc)
            d.line(R(24, 78, 76, 78), fill=fgc, width=int(8 * u))
        else:
            raise SystemExit(f"Unknown icon '{name}'. Use one of: thermometer wallet phone video clinic receipt card "
                             f"check clock camera upload")
        return img

    def card(self, item):
        w, h = int(item.get("w", 420)), int(item.get("h", 520))
        img = self.canvas(w, h)
        d = self.ImageDraw.Draw(img)
        fill = color(item.get("bg", "paper"))
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(w * 0.09), fill=fill)
        ic = self.icon(item.get("icon", "check"), w * 0.5, fg=item.get("fg", "primary"), bg=item.get("ring", "soft"))
        img.alpha_composite(ic, (int((w - ic.width) / 2), int(h * 0.08)))
        y = int(h * 0.08 + ic.height + h * 0.06)
        label = self.rich_text(item.get("label", ""), item.get("size", 64), color(item.get("color", "ink")), w - 30)
        img.alpha_composite(label, (int((w - label.width) / 2), y))
        if item.get("sub"):
            sub = self.rich_text(item["sub"], item.get("size", 64) * 0.6, color("muted"), w - 30)
            img.alpha_composite(sub, (int((w - sub.width) / 2), y + label.height - 10))
        return img

    def phone(self, screen, width=560):
        """A mock app screen, always labelled 示意图 (never a real screenshot of member data)."""
        w, h = int(width), int(width * 1.9)
        img = self.canvas(w, h + 70)
        d = self.ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(w * 0.12), fill=color("ink"))
        m = int(w * 0.04)
        d.rounded_rectangle((m, m, w - m, h - m), radius=int(w * 0.09), fill=color("paper"))
        d.rounded_rectangle((w * 0.36, m + 12, w * 0.64, m + 36), radius=12, fill=color("ink"))
        top = m + 60
        d.rectangle((m, top, w - m, top + w * 0.2), fill=color("primary"))
        f = self.font(w * 0.068)
        d.text((m + 30, top + w * 0.065), screen.get("title", "Medibank OSHC"), font=f, fill=color("paper"),
               stroke_width=1, stroke_fill=color("paper"))
        y = top + w * 0.2 + 30
        rows = screen.get("rows", [])
        rf = self.font(w * 0.058)
        self._row_boxes = []
        for i, row in enumerate(rows):
            hl = i == screen.get("hl")
            box = (m + 24, y, w - m - 24, y + w * 0.17)
            d.rounded_rectangle(box, radius=int(w * 0.04), fill=color("primary" if hl else "soft"))
            d.text((box[0] + 28, y + w * 0.05), plain(row), font=rf, fill=color("paper" if hl else "ink"),
                   stroke_width=1 if hl else 0, stroke_fill=color("paper"))
            self._row_boxes.append(box)
            y += w * 0.17 + 22
        if screen.get("photo"):
            box = (m + 24, y, w - m - 24, y + w * 0.5)
            d.rounded_rectangle(box, radius=int(w * 0.04), outline=color("muted"), width=3)
            rc = self.icon("receipt", w * 0.32, fg="muted", bg="paper", ring=False)
            img.alpha_composite(rc, (int((w - rc.width) / 2), int(y + w * 0.09)))
        lf = self.font(30)
        label = "示意图，以 App 实际界面为准"
        d.text(((w - d.textlength(label, font=lf)) / 2, h + 18), label, font=lf, fill=color("muted"))
        return img


# --- timeline --------------------------------------------------------------------------

class Sprite:
    def __init__(self, img, x, y, start, until, anim, dur=0.45):
        self.img, self.x, self.y = img, x, y
        self.start, self.until, self.anim, self.dur = start, until, anim, dur

    def state(self, t):
        """(scale, dx, dy, alpha) at scene time t, or None when not visible."""
        if t < self.start or (self.until is not None and t > self.until + 0.25):
            return None
        p = min(1.0, (t - self.start) / self.dur)
        scale, dx, dy, alpha = 1.0, 0, 0, 1.0
        if self.anim == "pop":
            scale, alpha = 0.35 + 0.65 * ease_out_back(p), min(1, p * 3)
        elif self.anim == "slide-left":
            dx, alpha = -900 * (1 - ease_out_cubic(p)), min(1, p * 2)
        elif self.anim == "slide-right":
            dx, alpha = 900 * (1 - ease_out_cubic(p)), min(1, p * 2)
        elif self.anim == "slide-up":
            dy, alpha = 260 * (1 - ease_out_cubic(p)), min(1, p * 2)
        elif self.anim == "fade":
            alpha = p
        if self.until is not None and t > self.until:
            alpha *= max(0.0, 1 - (t - self.until) / 0.25)
        return scale, dx, dy, alpha


class Scene:
    def __init__(self, spec, painter, start, fine_print):
        self.spec, self.start = spec, start
        self.seconds = float(spec["seconds"])
        self.bg = color(BGS.get(spec.get("bg", "white"), spec.get("bg", "white")))
        dark = spec.get("bg", "white") in ("red", "ink")
        self.sprites, self.sfx, self.taps = [], [], []
        P, W, H = painter, painter.w, painter.h
        for s in spec.get("sfx", []):
            self.sfx.append((float(s["at"]), s["name"]))
        if spec.get("section"):
            img = P.pill(spec["section"], tag=spec.get("tag"))
            self.sprites.append(Sprite(img, W / 2, H * 0.095, 0.0, None, "slide-up", 0.35))
        default_fg = "paper" if dark else "ink"
        for item in spec.get("items", []):
            at, until = float(item.get("at", 0)), item.get("until")
            anim = item.get("anim", "pop")
            x, y = W * float(item.get("x", 0.5)), H * float(item.get("y", 0.5))
            kind = item["type"]
            if kind == "text":
                img = P.rich_text(item["text"], item.get("size", 96), color(item.get("color", default_fg)),
                                  W * float(item.get("width", 0.82)))
            elif kind == "icon":
                img = P.icon(item["name"], item.get("size", 220), item.get("fg", "primary"),
                             item.get("ring", "paper" if dark else "soft"))
            elif kind == "card":
                img = P.card(item)
            elif kind == "note":
                img = P.rich_text(item["text"], item.get("size", 38), color(item.get("color", "soft" if dark else "muted")),
                                  W * 0.86)
                y = H * float(item.get("y", 0.66))
                anim = item.get("anim", "fade")
            elif kind == "phone":
                width = item.get("width", 560)
                screens = item.get("screens", [])
                for i, screen in enumerate(screens):
                    img = P.phone(screen, width)
                    s_at = float(screen.get("at", 0))
                    s_until = float(screens[i + 1]["at"]) - 0.01 if i + 1 < len(screens) else until
                    first = i == 0
                    self.sprites.append(Sprite(img, x, y, s_at, s_until, anim if first else "none",
                                               0.45 if first else 0.01))
                    if screen.get("hl") is not None and screen.get("tap", True):
                        bx0, by0, bx1, by1 = P._row_boxes[screen["hl"]]
                        tap_x = x - img.width / 2 + (bx0 + bx1) / 2
                        tap_y = y - img.height / 2 + (by0 + by1) / 2
                        tap_t = s_at + float(screen.get("tap_at", 0.5))
                        self.taps.append((tap_t, tap_x, tap_y))
                        self.sfx.append((tap_t, "click"))
                continue
            elif kind == "steps":
                labels = item["items"]
                gap = float(item.get("interval", 1.0))
                top = H * float(item.get("y", 0.3))
                row_h = item.get("row", 170)
                for i, label in enumerate(labels):
                    row = self._step_row(P, i + 1, label, W * 0.82, row_h)
                    self.sprites.append(Sprite(row, W / 2, top + i * (row_h + 26), at + i * gap, until, "slide-left", 0.35))
                    self.sfx.append((at + i * gap, item.get("sfx", "click")))
                continue
            else:
                raise SystemExit(f"Unknown item type '{kind}'")
            self.sprites.append(Sprite(img, x, y, at, until, anim))
            sound = item.get("sfx", "pop" if anim == "pop" else None)
            if sound:
                self.sfx.append((at, sound))
        # subtitles
        self.subs = []
        subs = scene_subs(spec)
        for i, (t0, text) in enumerate(subs):
            t1 = subs[i + 1][0] if i + 1 < len(subs) else self.seconds
            img = P.rich_text(text, 62, color("paper"), W * 0.84, stroke=(7, color("ink")))
            self.subs.append((t0, t1, text, img))
        self.fine = P.rich_text(fine_print, 30, color("soft" if dark else "muted"), W * 0.9) if fine_print else None

    @staticmethod
    def _step_row(P, n, label, width, h):
        img = P.canvas(width, h)
        d = P.ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, width - 1, h - 1), radius=int(h * 0.28), fill=color("paper"),
                            outline=color("soft"), width=4)
        dia = h * 0.66
        d.ellipse((h * 0.17, h * 0.17, h * 0.17 + dia, h * 0.17 + dia), fill=color("primary"))
        f = P.font(h * 0.4)
        num = str(n)
        d.text((h * 0.17 + (dia - d.textlength(num, font=f)) / 2, h * 0.17 + dia * 0.14), num, font=f,
               fill=color("paper"), stroke_width=1, stroke_fill=color("paper"))
        text = P.rich_text(label, h * 0.36, color("ink"), width - h * 1.3, align="left")
        img.alpha_composite(text, (int(h * 1.0), int((h - text.height) / 2)))
        return img

    def frame(self, P, t, with_subs=True):
        img = P.Image.new("RGBA", (P.w, P.h), self.bg)
        for sp in self.sprites:
            st = sp.state(t)
            if not st:
                continue
            scale, dx, dy, alpha = st
            im = sp.img
            if abs(scale - 1) > 0.01:
                im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))))
            if alpha < 0.99:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda a, k=alpha: int(a * k)))
            img.alpha_composite(im, (int(sp.x - im.width / 2 + dx), int(sp.y - im.height / 2 + dy)))
        d = P.ImageDraw.Draw(img)
        for tap_t, x, y in self.taps:  # finger-tap ripple on mock screens
            p = (t - tap_t) / 0.5
            if 0 <= p <= 1:
                r = 30 + 60 * p
                a = int(200 * (1 - p))
                d.ellipse((x - r, y - r, x + r, y + r), outline=(26, 26, 26, a), width=8)
                d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(26, 26, 26, int(150 * (1 - p))))
        if with_subs:
            for t0, t1, _, sub in self.subs:
                if t0 <= t < t1:
                    img.alpha_composite(sub, (int((P.w - sub.width) / 2), int(P.h * 0.72)))
        if self.fine:
            img.alpha_composite(self.fine, (int((P.w - self.fine.width) / 2), int(P.h * 0.80)))
        return img.convert("RGB")


def build_scenes(board, painter):
    scenes, start = [], 0.0
    for spec in board["scenes"]:
        scenes.append(Scene(spec, painter, start, board.get("fine_print")))
        start += float(spec["seconds"])
    return scenes, start


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(scenes, path):
    rows, n = [], 1
    for sc in scenes:
        for t0, t1, text, _ in sc.subs:
            rows.append(f"{n}\n{srt_time(sc.start + t0)} --> {srt_time(sc.start + t1)}\n{plain(text)}\n")
            n += 1
    Path(path).write_text("\n".join(rows), encoding="utf-8")


def sfx_cues(scenes):
    return sorted((sc.start + t, name) for sc in scenes for t, name in sc.sfx if t < sc.seconds)


# --- render ----------------------------------------------------------------------------

def ff():
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found. Install it first: macOS `brew install ffmpeg`, Windows `winget install ffmpeg`.")
    return path


def make_sfx(folder):
    folder.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, src in SFX.items():
        path = folder / f"{name}.wav"
        subprocess.run([ff(), "-v", "error", "-y", "-f", "lavfi", "-i", src, "-ac", "2", "-ar", "48000", str(path)], check=True)
        out[name] = path
    return out


def mix_audio(cues, sfx_files, total, out):
    args, chains = [ff(), "-v", "error", "-y", "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"], []
    for i, (t, name) in enumerate(cues, 1):
        args += ["-i", str(sfx_files[name])]
        ms = int(t * 1000)
        chains.append(f"[{i}:a]adelay={ms}|{ms}[s{i}]")
    labels = "".join(f"[s{i}]" for i in range(1, len(cues) + 1))
    graph = ";".join(chains + [f"[0:a]{labels}amix=inputs={len(cues) + 1}:normalize=0:duration=first,"
                                f"alimiter=limit=0.9[a]"])
    subprocess.run(args + ["-filter_complex", graph, "-map", "[a]", "-t", f"{total:.3f}", str(out)], check=True)


def open_writer(path, size):
    return subprocess.Popen([ff(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)


def render(board, out, font=None, pack=False):
    size = SIZES.get(board.get("platform", "douyin"), (1080, 1920))
    P = Painter(size, find_font(font))
    scenes, total = build_scenes(board, P)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        writers = {"subs": open_writer(tmp / "v.mp4", size)}
        if pack:
            writers["clean"] = open_writer(tmp / "clean.mp4", size)
        n_frames = int(round(total * FPS))
        for i in range(n_frames):
            gt = i / FPS
            sc = next(s for s in reversed(scenes) if s.start <= gt + 1e-9)
            lt = gt - sc.start
            writers["subs"].stdin.write(sc.frame(P, lt, True).tobytes())
            if pack:
                writers["clean"].stdin.write(sc.frame(P, lt, False).tobytes())
        for w in writers.values():
            w.stdin.close()
            if w.wait():
                raise SystemExit("ffmpeg failed while encoding frames")
        sfx_dir = (out.parent / (out.stem + "_剪映素材包") / "音效") if pack else tmp / "sfx"
        files = make_sfx(sfx_dir)
        cues = sfx_cues(scenes)
        audio = tmp / "a.wav"
        mix_audio(cues, files, total, audio)
        mux = [ff(), "-v", "error", "-y", "-i", "{v}", "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
               "-shortest", "-movflags", "+faststart", "{o}"]
        subprocess.run([str(tmp / "v.mp4") if a == "{v}" else str(out) if a == "{o}" else a for a in mux], check=True)
        if pack:
            write_pack(scenes, cues, tmp, out, audio, mux)
    return out, total


def write_pack(scenes, cues, tmp, out, audio, mux):
    """剪映 asset pack: numbered scene clips, no-subtitle version, .srt, sound effects and a timing sheet."""
    pack = out.parent / (out.stem + "_剪映素材包")
    (pack / "分段").mkdir(parents=True, exist_ok=True)
    clean = pack / "无字幕版.mp4"
    subprocess.run([str(tmp / "clean.mp4") if a == "{v}" else str(clean) if a == "{o}" else a for a in mux], check=True)
    for i, sc in enumerate(scenes, 1):
        name = f"{i:02d}_{plain(scene_subs(sc.spec)[0][1])[:10] if sc.subs else 'scene'}.mp4".replace("/", "_")
        subprocess.run([ff(), "-v", "error", "-y", "-ss", f"{sc.start:.3f}", "-i", str(out), "-t", f"{sc.seconds:.3f}",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", str(pack / "分段" / name)],
                       check=True)
    write_srt(scenes, pack / "字幕.srt")
    shutil.copy(audio, pack / "音效" / "全部音效_已对齐.wav")
    with open(pack / "时间表.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["时间(秒)", "类型", "内容"])
        for i, sc in enumerate(scenes, 1):
            w.writerow([f"{sc.start:.2f}", "镜头", f"{i:02d} ({sc.seconds:g}s)"])
            for t0, _, text, _ in sc.subs:
                w.writerow([f"{sc.start + t0:.2f}", "字幕", plain(text)])
        for t, name in cues:
            w.writerow([f"{t:.2f}", "音效", f"音效/{name}.wav"])
    (pack / "使用说明.txt").write_text(
        "剪映里怎么用\n\n"
        "1. 导入「无字幕版.mp4」（或按顺序导入「分段」里的片段）。\n"
        "2. 文本 → 导入字幕 → 选「字幕.srt」，再套你喜欢的字幕样式；也可以用「文本朗读」给字幕配音。\n"
        "3. 音效已经混在视频里；想单独调就把视频静音，拖入「音效/全部音效_已对齐.wav」，或按「时间表.csv」放单个音效。\n"
        "4. App 画面是示意图，拿到真实录屏后替换对应分段。\n",
        encoding="utf-8")


def stills(board, times, out_dir, font=None):
    size = SIZES.get(board.get("platform", "douyin"), (1080, 1920))
    P = Painter(size, find_font(font))
    scenes, _ = build_scenes(board, P)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for gt in times:
        sc = next(s for s in reversed(scenes) if s.start <= gt + 1e-9)
        path = out_dir / f"frame_{gt:05.1f}s.png"
        sc.frame(P, gt - sc.start).save(path)
        paths.append(path)
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("board", help="storyboard JSON")
    parser.add_argument("--out", help="output .mp4 (default outputs/videos/<board name>.mp4)")
    parser.add_argument("--font", help="font with Chinese characters")
    parser.add_argument("--pack", action="store_true", help="also write a 剪映 asset pack next to the video")
    parser.add_argument("--check", action="store_true", help="run the text checks only")
    parser.add_argument("--frames", help="comma-separated seconds: save PNG stills instead of a video")
    parser.add_argument("--allow-red", action="store_true", help="render even if the checks are red (drafts only)")
    args = parser.parse_args(argv)
    board = json.loads(Path(args.board).read_text(encoding="utf-8"))
    if not board.get("scenes"):
        raise SystemExit("The storyboard has no scenes.")
    worst, report = check_board(board, board.get("platform"))
    print("\n".join(report))
    if args.check:
        return worst
    if worst == 2 and not args.allow_red:
        print("Red result: fix the text above before rendering (or --allow-red for an internal draft).")
        return 2
    out = Path(args.out) if args.out else ROOT / "outputs" / "videos" / (Path(args.board).stem + ".mp4")
    if args.frames:
        for p in stills(board, [float(x) for x in args.frames.split(",")], out.parent / (out.stem + "_frames"), args.font):
            print(f"Wrote {p}")
        return 0
    path, total = render(board, out, args.font, args.pack)
    print(f"Wrote {path} ({total:.1f}s)" + (f" and {path.parent / (path.stem + '_剪映素材包')}" if args.pack else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
