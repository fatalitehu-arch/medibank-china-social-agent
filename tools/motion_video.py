#!/usr/bin/env python3
"""Animated explainer video in Medibank colours, no footage needed: voice-over, subtitles synced to it, 3D emoji, real or mock app screens with tap and highlight effects, step lists, scene transitions and sound effects.

The agent (cn-video-editor) writes a storyboard; this script lays it out on a timeline driven by the
voice-over, draws every frame as an HTML page in headless Chromium (Playwright), and encodes it with ffmpeg.

Storyboard (full example: examples/motion_storyboard.json):
    {"platform": "douyin", "brand": "Medibank · 留学生健康指南", "fine_print": "具体保障以保单条款为准",
     "voice": {"dir": "voice/xiaoxiao", "gap": 0.18},        # NN.mp3 per spoken line, in order (tools/make_voice.py)
     "scenes": [
       {"bg": "red",                                          # red | cream | white
        "say": ["留学生在澳洲看病，钱怎么{报}？"],              # voice lines = subtitles; {word} = yellow
        "wipe": true,                                         # colour wipe into this scene
        "items": [
          {"type": "headline", "text": "看病的钱\\n怎么{报}？", "size": 150, "y": 0.33, "at": 0},
          {"type": "emoji", "name": "face_with_thermometer", "x": 0.3, "y": 0.6, "size": 300, "at": "L0+0.6", "float": true}]}]}

Item types: headline (宋体), text (黑体), big (huge number), chip (black pill, "n" = red number), emoji
(3D icon from assets/emoji/), card (emoji + title + sub), note (fine print box), phone (screenshot in a
phone frame: "src", "scroll": [[t, fraction, secs]], "rings": [{"t", "box": [x0,y0,x1,y1] as fractions}],
"taps": [{"t", "at": [x,y]}]), steps ("items": [{"text", "emoji"}], "at": ["L0", "L1", ...]).
"at" is seconds into the scene, or "L<n>[+s]" = when the scene's n-th voice line starts. "until" works
the same way. "anim": pop | rise | left | right | drop | zoom | fade. "sfx": whoosh | pop | ding | click |
success | null (sensible defaults are added).

Before rendering, all on-screen words go through tools/compliance_scan.py and the claim qualifier rules in
assets/brand/qualifiers.json. A red result stops the render.

Usage:
    python tools/motion_video.py board.json --check                        # text checks only
    python tools/motion_video.py board.json --frames 2,10,20 --out x.mp4   # PNG stills to look at
    python tools/motion_video.py board.json --pack --out outputs/videos/x.mp4
Needs: ffmpeg, `pip install playwright` + `playwright install chromium`. Fonts: PingFang SC / Songti SC on
a Mac; elsewhere Noto Sans SC / Noto Serif SC are downloaded once to ~/.cache/medibank-agent/fonts.
"""

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import compliance_scan  # noqa: E402

QUALIFIERS = ROOT / "assets" / "brand" / "qualifiers.json"
EMOJI = ROOT / "assets" / "emoji"
TEMPLATE = ROOT / "tools" / "motion_template.html"
CACHE = Path(os.environ.get("MEDIBANK_AGENT_CACHE", Path.home() / ".cache" / "medibank-agent"))
SIZES = {"douyin": (1080, 1920), "wechat-channels": (1080, 1920), "xiaohongshu": (1080, 1440), "weibo": (1080, 1920)}
FPS = 30
SUB_MAX = 16  # Chinese characters per subtitle line (Latin counts half)
CHARS_PER_SEC = 4.6  # speaking speed used when there is no voice file yet
FONT_URLS = {  # SIL Open Font License, https://github.com/notofonts/noto-cjk
    "Noto Sans SC": [(700, "Sans/SubsetOTF/SC/NotoSansSC-Bold.otf"), (900, "Sans/SubsetOTF/SC/NotoSansSC-Black.otf"),
                     (500, "Sans/SubsetOTF/SC/NotoSansSC-Medium.otf")],
    "Noto Serif SC": [(900, "Serif/SubsetOTF/SC/NotoSerifSC-Black.otf"), (700, "Serif/SubsetOTF/SC/NotoSerifSC-Bold.otf")],
}
MAC_FONTS = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Supplemental/Songti.ttc"]

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


# --- text helpers and checks ------------------------------------------------------------

def plain(text):
    return text.replace("{", "").replace("}", "")


def sub_width(line):
    """Subtitle length in Chinese-character widths (Latin letters, digits and spaces count half)."""
    return sum(0.5 if ord(ch) < 0x2E80 else 1 for ch in line)


def show_line(text):
    """Subtitle text as shown: no trailing comma or full stop; a line over SUB_MAX breaks at its comma."""
    line = re.sub(r"[，。,]+$", "", text.strip())
    if sub_width(plain(line)) > SUB_MAX and "，" in line:
        line = line.replace("，", "\n", 1)
    return line


def all_text(board):
    """Every word that will be on screen or spoken, one piece per line (for compliance and qualifier checks)."""
    out = []
    for scene in board["scenes"]:
        out += [plain(s) for s in scene.get("say", [])]
        for item in scene.get("items", []):
            if item["type"] == "phone":
                out.append("[phone] 示意" if item.get("mock") else "[phone] 真实 App 界面，个人信息已打码，示意")
            for key in ("text", "title", "sub"):
                if item.get(key):
                    out.append(plain(item[key]))
            out += [plain(s["text"] if isinstance(s, dict) else s) for s in item.get("items", [])]
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
            problems.append(f"{rule['id']} {rule['claim']}: '{hit}' is in the video but it never says {need}. "
                            f"Source: {rule['source']}")
    return problems


def check_board(board, platform=None):
    """Compliance scan + qualifier rules + subtitle length. Returns (worst level 0-2, report lines)."""
    lines = all_text(board)
    worst, hits = compliance_scan.scan("\n".join(lines), platform=platform)
    report = [compliance_scan.format_report(worst, hits, platform)] if hits else ["Compliance scan: green"]
    problems = check_qualifiers(lines)
    for n, scene in enumerate(board["scenes"], 1):
        for line in scene.get("say", []):
            if max(sub_width(part) for part in show_line(plain(line)).split("\n")) > SUB_MAX:
                problems.append(f"Scene {n}: subtitle over {SUB_MAX} characters, split it: {plain(line)}")
        for item in scene.get("items", []):
            if item["type"] in ("emoji", "card") and not (EMOJI / f"{item.get('name', item.get('emoji'))}.png").exists():
                problems.append(f"Scene {n}: no emoji '{item.get('name', item.get('emoji'))}' in assets/emoji/")
    if problems:
        worst = 2
        report += ["Claim, subtitle and asset checks: red"] + ["  - " + p for p in problems]
    else:
        report.append("Claim qualifiers, subtitle length and assets: OK")
    return worst, report


# --- timeline ---------------------------------------------------------------------------

def audio_length(path):
    out = subprocess.run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def voice_files(board, base):
    voice = board.get("voice") or {}
    if not voice.get("dir"):
        return None
    folder = (base / voice["dir"]) if not Path(voice["dir"]).is_absolute() else Path(voice["dir"])
    n = sum(len(s.get("say", [])) for s in board["scenes"])
    files = [folder / f"{i:02d}.mp3" for i in range(1, n + 1)]
    missing = [f.name for f in files if not f.exists()]
    if missing:
        raise SystemExit(f"Voice files missing in {folder}: {', '.join(missing[:5])}. Run tools/make_voice.py first.")
    return files


def resolve(at, scene, default=0.0):
    """'L2+0.3' -> seconds into the scene (2nd voice line start + 0.3); numbers pass through."""
    if at is None:
        return default
    if isinstance(at, (int, float)):
        return float(at)
    m = re.fullmatch(r"L(\d+)([+-][\d.]+)?", str(at).replace(" ", ""))
    if not m:
        raise SystemExit(f"Bad time '{at}': use seconds or L<n>+<s>")
    k = int(m.group(1))
    starts = scene["_line_starts"]
    if k >= len(starts):
        raise SystemExit(f"'{at}' points to voice line {k}, but the scene has {len(starts)} lines")
    return starts[k] + float(m.group(2) or 0)


SFX_DEFAULT = {"emoji": "pop", "card": "whoosh", "headline": None, "big": "ding", "chip": "whoosh", "phone": "whoosh"}


def build_timeline(board, base):
    """Fill in absolute times for scenes, voice lines, items and sound effects. Returns (layout, cues, voice)."""
    files = voice_files(board, base)
    gap = float((board.get("voice") or {}).get("gap", 0.18))
    lead, tail = float(board.get("lead", 0.35)), float(board.get("tail", 0.6))
    t, k, lines, cues, voice = 0.0, 0, [], [], []
    scenes = []
    for n, spec in enumerate(board["scenes"]):
        sc = dict(spec)
        sc["t0"] = t
        cursor = lead if n == 0 else 0.25
        starts = []
        for text in spec.get("say", []):
            dur = audio_length(files[k]) if files else max(1.2, len(plain(text)) / CHARS_PER_SEC)
            starts.append(cursor)
            lines.append({"t0": t + cursor, "t1": t + cursor + dur + gap * 0.6, "show": show_line(text),
                          "text": plain(text)})
            if files:
                voice.append((t + cursor, files[k]))
            cursor += dur + gap
            k += 1
        sc["_line_starts"] = starts
        seconds = max(float(spec.get("min", 0)), cursor + float(spec.get("hold", 0.25)))
        if n == len(board["scenes"]) - 1:
            seconds += tail
        sc["t1"] = t + seconds
        items = []
        for it in spec.get("items", []):
            it = dict(it)
            local = 0.0 if isinstance(it.get("at"), list) else resolve(it.get("at"), sc)
            it["t0"] = t + local
            it["t1"] = t + (resolve(it["until"], sc) if it.get("until") is not None else seconds - 0.05)
            if it["type"] in ("emoji", "card"):
                it["src"] = (EMOJI / f"{it.get('name', it.get('emoji'))}.png").as_uri()
            if it["type"] == "phone":
                it["src"] = (base / it["src"]).resolve().as_uri() if not it["src"].startswith(("file:", "data:")) else it["src"]
                for key in ("rings", "taps"):
                    for x in it.get(key, []):
                        x["t"] = t + resolve(x.get("t"), sc)
                        if x.get("until") is not None:
                            x["until"] = t + resolve(x["until"], sc)
                it["scroll"] = [[t + resolve(a, sc), f, d] for a, f, d in it.get("scroll", [])]
                cues += [(x["t"], "click") for x in it.get("taps", [])]
                cues += [(x["t"], "pop") for x in it.get("rings", [])]
            if it["type"] == "steps":
                ats = it.get("at") if isinstance(it.get("at"), list) else [it.get("at", 0)] * len(it["items"])
                it["times"] = [t + resolve(a, sc) for a in ats]
                it["t0"] = min(it["times"]) - 0.01
                for s in it["items"]:
                    if s.get("emoji"):
                        s["src"] = (EMOJI / f"{s['emoji']}.png").as_uri()
                cues += [(x, it.get("sfx", "click")) for x in it["times"]]
            sound = it.get("sfx", SFX_DEFAULT.get(it["type"]))
            if it["type"] == "headline" and "{" in it.get("text", "") and "sfx" not in it:
                sound = "ding"
            if sound and it["type"] != "steps":
                cues.append((it["t0"] + (0.25 if sound == "ding" and it["type"] == "headline" else 0), sound))
            items.append(it)
        if spec.get("wipe") or (n > 0 and spec.get("bg") != board["scenes"][n - 1].get("bg")):
            cues.append((max(0.0, t - 0.15), "whoosh"))
        for s in spec.get("sfx", []):
            cues.append((t + resolve(s["at"], sc), s["name"]))
        sc["items"] = items
        scenes.append(sc)
        t += seconds
    layout = {"scenes": scenes, "lines": lines, "total": t, "brand": board.get("brand", ""),
              "fine_print": board.get("fine_print", "")}
    return layout, sorted(cues), voice


# --- rendering --------------------------------------------------------------------------

def font_faces():
    """@font-face rules: Mac system fonts if present (PingFang / Songti are referenced by name), else Noto."""
    if all(Path(p).exists() for p in MAC_FONTS):
        return ""
    rules = []
    for family, files in FONT_URLS.items():
        for weight, rel in files:
            path = CACHE / "fonts" / Path(rel).name
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                url = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/" + rel
                print(f"Downloading {path.name} (once) ...")
                urllib.request.urlretrieve(url, path)
            rules.append(f'@font-face{{font-family:"{family}";font-weight:{weight};src:url("{path.as_uri()}")}}')
    return "\n".join(rules)


def write_page(layout, size, folder):
    w, h = size
    html = (TEMPLATE.read_text(encoding="utf-8").replace("__FONTFACES__", font_faces())
            .replace("__BOARD__", json.dumps(layout, ensure_ascii=False)).replace("__W__", str(w))
            .replace("__H__", str(h)).replace("__SUBY__", str(int(h * 0.705)))
            .replace("__FINEY__", str(int(h * 0.80))))
    page = folder / "page.html"
    page.write_text(html, encoding="utf-8")
    return page


def browser(p):
    try:
        return p.chromium.launch()
    except Exception:
        import glob
        for exe in sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome")):
            return p.chromium.launch(executable_path=exe, args=["--allow-file-access-from-files"])
        raise


def ff():
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found. Install it first: macOS `brew install ffmpeg`, Windows `winget install ffmpeg`.")
    return path


def capture(page_path, size, times, sink, subs=True):
    """Render each time in `times`; sink(jpeg_bytes) receives the frames."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = browser(p)
        pg = b.new_page(viewport={"width": size[0], "height": size[1]})
        pg.goto(page_path.as_uri())
        pg.evaluate("window.ready")
        pg.evaluate(f"setSubs({str(subs).lower()})")
        for t in times:
            pg.evaluate(f"renderAt({t:.4f})")
            sink(pg.screenshot(type="jpeg", quality=93))
        b.close()


def encode(page, size, total, out, subs=True):
    proc = subprocess.Popen([ff(), "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                             "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                             "-r", str(FPS), str(out)], stdin=subprocess.PIPE)
    n = int(round(total * FPS))
    capture(page, size, [i / FPS for i in range(n)], proc.stdin.write, subs)
    proc.stdin.close()
    if proc.wait():
        raise SystemExit("ffmpeg failed while encoding frames")


def make_sfx(folder):
    folder.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, src in SFX.items():
        path = folder / f"{name}.wav"
        subprocess.run([ff(), "-v", "error", "-y", "-f", "lavfi", "-i", src, "-ac", "2", "-ar", "48000", str(path)], check=True)
        out[name] = path
    return out


def mix(tracks, total, out, normalise=True):
    """tracks: list of (start seconds, file, volume). Writes one stereo wav of length `total`."""
    args = [ff(), "-v", "error", "-y", "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    chains = []
    for i, (t, path, vol) in enumerate(tracks, 1):
        args += ["-i", str(path)]
        ms = max(0, int(t * 1000))
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{i}]")
    labels = "".join(f"[s{i}]" for i in range(1, len(tracks) + 1))
    tail = ",loudnorm=I=-16:TP=-1.5:LRA=11" if normalise else ",alimiter=limit=0.9"
    graph = ";".join(chains + [f"[0:a]{labels}amix=inputs={len(tracks) + 1}:normalize=0:duration=first{tail}[a]"])
    subprocess.run(args + ["-filter_complex", graph, "-map", "[a]", "-ar", "48000", "-t", f"{total:.3f}", str(out)], check=True)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(lines, path):
    Path(path).write_text("\n".join(f"{i}\n{srt_time(L['t0'])} --> {srt_time(L['t1'])}\n{plain(L['show'])}\n"
                                    for i, L in enumerate(lines, 1)), encoding="utf-8")


def render(board, base, out, pack=False):
    size = SIZES.get(board.get("platform", "douyin"), (1080, 1920))
    layout, cues, voice = build_timeline(board, base)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    total = layout["total"]
    pack_dir = out.parent / (out.stem + "_剪映素材包")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        page = write_page(layout, size, tmp)
        encode(page, size, total, tmp / "v.mp4", True)
        sfx = make_sfx(pack_dir / "音效" if pack else tmp / "sfx")
        sfx_vol = float(board.get("sfx_volume", 0.35 if voice else 0.9))
        tracks = [(a, f, 1.0) for a, f in voice] + [(a, sfx[name], sfx_vol) for a, name in cues if a < total]
        mix(tracks, total, tmp / "a.wav", normalise=bool(voice))
        mux = lambda video, dst: subprocess.run(  # noqa: E731
            [ff(), "-v", "error", "-y", "-i", str(video), "-i", str(tmp / "a.wav"), "-c:v", "copy", "-c:a", "aac",
             "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(dst)], check=True)
        mux(tmp / "v.mp4", out)
        if pack:
            (pack_dir / "分段").mkdir(parents=True, exist_ok=True)
            encode(page, size, total, tmp / "clean.mp4", False)
            mux(tmp / "clean.mp4", pack_dir / "无字幕版.mp4")
            for i, sc in enumerate(layout["scenes"], 1):
                name = f"{i:02d}_{plain(sc['say'][0])[:10] if sc.get('say') else 'scene'}.mp4"
                subprocess.run([ff(), "-v", "error", "-y", "-ss", f"{sc['t0']:.3f}", "-i", str(out), "-t",
                                f"{sc['t1'] - sc['t0']:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                "-c:a", "aac", str(pack_dir / "分段" / re.sub(r'[\\/:*?"<>|，。？！、]', "", name))],
                               check=True)
            write_srt(layout["lines"], pack_dir / "字幕.srt")
            if voice:
                (pack_dir / "配音").mkdir(exist_ok=True)
                mix([(a, f, 1.0) for a, f in voice], total, pack_dir / "配音" / "配音_已对齐.wav")
            mix([(a, sfx[name], 0.9) for a, name in cues if a < total], total, pack_dir / "音效" / "音效_已对齐.wav",
                normalise=False)
            with open(pack_dir / "时间表.csv", "w", newline="", encoding="utf-8-sig") as fh:
                w = csv.writer(fh)
                w.writerow(["时间(秒)", "类型", "内容"])
                for i, sc in enumerate(layout["scenes"], 1):
                    w.writerow([f"{sc['t0']:.2f}", "镜头", f"{i:02d} ({sc['t1'] - sc['t0']:.1f}s)"])
                for L in layout["lines"]:
                    w.writerow([f"{L['t0']:.2f}", "字幕/配音", L["text"]])
                for a, name in cues:
                    w.writerow([f"{a:.2f}", "音效", f"音效/{name}.wav"])
            (pack_dir / "使用说明.txt").write_text(
                "剪映里怎么用\n\n"
                "1. 想自己做字幕：导入「无字幕版.mp4」，文本 → 导入字幕 → 选「字幕.srt」，再套字幕样式。\n"
                "2. 配音和音效已经混在视频里。想单独调音量：把视频静音，再拖入「配音/配音_已对齐.wav」和"
                "「音效/音效_已对齐.wav」，都从 0 秒开始放。\n"
                "3. 「分段」里是每个镜头单独的片段，按编号排；「时间表.csv」列出每句字幕和每个音效的时间。\n",
                encoding="utf-8")
    return out, total


def stills(board, base, times, out_dir):
    size = SIZES.get(board.get("platform", "douyin"), (1080, 1920))
    layout, _, _ = build_timeline(board, base)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with tempfile.TemporaryDirectory() as t:
        page = write_page(layout, size, Path(t))
        frames = []
        capture(page, size, times, frames.append)
    for t, data in zip(times, frames):
        path = out_dir / f"frame_{t:05.1f}s.jpg"
        path.write_bytes(data)
        paths.append(path)
    return paths, layout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("board", help="storyboard JSON")
    parser.add_argument("--out", help="output .mp4 (default outputs/videos/<board name>.mp4)")
    parser.add_argument("--pack", action="store_true", help="also write a 剪映 asset pack next to the video")
    parser.add_argument("--check", action="store_true", help="run the text checks only")
    parser.add_argument("--frames", help="comma-separated seconds: save JPEG stills instead of a video")
    parser.add_argument("--voice", help="override the voice folder (e.g. voice/yunxi)")
    parser.add_argument("--allow-red", action="store_true", help="render even if the checks are red (drafts only)")
    args = parser.parse_args(argv)
    board_path = Path(args.board)
    board = json.loads(board_path.read_text(encoding="utf-8"))
    if args.voice:
        board.setdefault("voice", {})["dir"] = str(Path(args.voice).resolve())
    if not board.get("scenes"):
        raise SystemExit("The storyboard has no scenes.")
    worst, report = check_board(board, board.get("platform"))
    print("\n".join(report))
    if args.check:
        return worst
    if worst == 2 and not args.allow_red:
        print("Red result: fix the text above before rendering (or --allow-red for an internal draft).")
        return 2
    base = board_path.resolve().parent
    out = Path(args.out) if args.out else ROOT / "outputs" / "videos" / (board_path.stem + ".mp4")
    if args.frames:
        paths, layout = stills(board, base, [float(x) for x in args.frames.split(",")], out.parent / (out.stem + "_frames"))
        print(f"Timeline {layout['total']:.1f}s; wrote {len(paths)} stills to {paths[0].parent}")
        return 0
    path, total = render(board, base, out, args.pack)
    print(f"Wrote {path} ({total:.1f}s)" + (f" and {path.parent / (path.stem + '_剪映素材包')}" if args.pack else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
