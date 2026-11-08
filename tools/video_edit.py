#!/usr/bin/env python3
"""Simple short-video editor for Medibank posts: cut, join, make vertical, colour, subtitle, add title and end cards.

Built on ffmpeg (must be installed: brew install ffmpeg / winget install ffmpeg). The agent
(cn-video-editor) writes an edit plan; this script renders it.

Edit plan (see examples/video_plan.json):
    {"platform": "douyin",                       # douyin | wechat-channels | xiaohongshu (sets size)
     "clips": [{"file": "raw/a.mp4", "start": 3.0, "end": 9.5}, ...],
     "subtitles": "raw/subs.srt",                # optional; times follow the clips (the title card is added for you)
     "title": {"headline": "第一次在悉尼看病", "sub": "3 步搞定", "seconds": 2},
     "end": {"next": "去学校官网搜 OSHC", "line": "具体保障以保单条款为准", "seconds": 2.5},
     "music": "raw/bgm.mp3",                     # optional, licensed music only; ducked under speech
     "grade": true}                              # Medibank colour tone from assets/brand/theme.json

Usage:
    python tools/video_edit.py plan.json --out outputs/videos/first-gp.mp4
    python tools/video_edit.py plan.json --dry-run      # print the ffmpeg commands only
    python tools/video_edit.py --probe raw/a.mp4        # show length and size of a clip
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

THEME = json.loads((ROOT / "assets" / "brand" / "theme.json").read_text(encoding="utf-8"))
SIZES = {"douyin": (1080, 1920), "wechat-channels": (1080, 1920), "xiaohongshu": (1080, 1440), "weibo": (1080, 1920)}
FPS = 30


def ffmpeg_bin():
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found. Install it first: macOS `brew install ffmpeg`, Windows `winget install ffmpeg`.")
    return path


def probe(path):
    out = subprocess.run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=width,height,codec_type", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True)
    data = json.loads(out.stdout)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), {})
    has_audio = any(s["codec_type"] == "audio" for s in data["streams"])
    return {"duration": float(data["format"]["duration"]), "width": video.get("width"),
            "height": video.get("height"), "audio": has_audio}


def shift_srt(text, seconds):
    """Move every SRT timestamp later by `seconds` (so subtitles written for the clips skip the title card)."""
    import re

    def move(m):
        h, mi, s, ms = (int(x) for x in m.groups())
        total = max(0, round(((h * 60 + mi) * 60 + s) * 1000 + ms + seconds * 1000))
        h, rem = divmod(total, 3_600_000)
        mi, rem = divmod(rem, 60_000)
        s, ms = divmod(rem, 1000)
        return f"{h:02d}:{mi:02d}:{s:02d},{ms:03d}"
    return re.sub(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", move, text)


def ass_color(hex_color):
    h = hex_color.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def vertical_filter(w, h, grade):
    """Fit any clip into w x h: blurred fill behind, sharp clip centred; optional colour grade."""
    g = "," + THEME["video"]["grade"] if grade else ""
    return (f"split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2[bg];"
            f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"
            f"fps={FPS},format=yuv420p,setsar=1{g}")


def card_images(plan, size, tmp, font):
    """Render title and end cards as PNG with make_post's renderer (Medibank colours)."""
    import make_post
    platform = plan.get("platform", "douyin")
    r = make_post.Renderer(platform if platform in make_post.SIZES else "douyin", make_post.find_font(font),
                           plan.get("account", "brand"))
    r.w, r.h = size
    r.s = r.w / 1080
    out = {}
    if plan.get("title"):
        spec = {"cover": {"headline": plan["title"]["headline"], "sub": plan["title"].get("sub", "")},
                "pillar": plan.get("pillar", "")}
        path = tmp / "title.png"
        r.cover(spec, 1).save(path)
        out["title"] = (path, float(plan["title"].get("seconds", 2)))
    if plan.get("end"):
        path = tmp / "end.png"
        r.end(plan["end"], 1, 1).save(path)
        out["end"] = (path, float(plan["end"].get("seconds", 2.5)))
    return out


def build_commands(plan, out, tmp, font=None, render_cards=True):
    ff = ffmpeg_bin() if render_cards else "ffmpeg"
    w, h = SIZES.get(plan.get("platform", "douyin"), (1080, 1920))
    grade = plan.get("grade", True)
    cmds, parts = [], []
    cards = card_images(plan, (w, h), tmp, font) if render_cards else {}

    def still(name):
        path, secs = cards[name]
        part = tmp / f"{name}.mp4"
        cmds.append([ff, "-y", "-loop", "1", "-t", str(secs), "-i", str(path), "-f", "lavfi", "-t", str(secs),
                     "-i", "anullsrc=r=48000:cl=stereo", "-vf", f"scale={w}:{h},fps={FPS},format=yuv420p,setsar=1",
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-shortest", str(part)])
        parts.append(part)

    if "title" in cards:
        still("title")
    for i, clip in enumerate(plan["clips"]):
        part = tmp / f"clip{i:02d}.mp4"
        src = str(Path(clip["file"]).expanduser())
        trim = []
        if clip.get("start") is not None:
            trim += ["-ss", str(clip["start"])]
        if clip.get("end") is not None:
            trim += ["-to", str(clip["end"])]
        info = probe(src) if render_cards else {"audio": True}
        audio_in = [] if info["audio"] else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest"]
        cmds.append([ff, "-y", *trim, "-i", src, *audio_in, "-filter_complex", f"[0:v]{vertical_filter(w, h, grade)}[v]",
                     "-map", "[v]", "-map", "0:a" if info["audio"] else "1:a", "-c:v", "libx264", "-preset", "veryfast",
                     "-crf", "20", "-c:a", "aac", "-ar", "48000", "-ac", "2", str(part)])
        parts.append(part)
    if "end" in cards:
        still("end")

    joined = tmp / "joined.mp4"
    listing = tmp / "parts.txt"
    listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    cmds.append([ff, "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c:v", "libx264", "-preset", "veryfast",
                 "-crf", "20", "-c:a", "aac", str(joined)])

    vf, extra_in, afilter = [], [], "loudnorm=I=-16:TP=-1.5:LRA=11"
    if plan.get("subtitles"):
        c = THEME["colors"]
        src = Path(plan["subtitles"]).expanduser()
        shifted = tmp / "subs.srt"
        lead = float(plan["title"].get("seconds", 2)) if plan.get("title") else 0.0
        if src.exists():
            shifted.write_text(shift_srt(src.read_text(encoding="utf-8-sig"), lead), encoding="utf-8")
        elif render_cards:
            raise SystemExit(f"Subtitle file not found: {src}")
        srt = shifted.resolve().as_posix().replace(":", r"\:").replace("'", r"\'")
        style = (f"FontName={THEME['video']['subtitle_font']},FontSize=13,PrimaryColour={ass_color(c['paper'])},"
                 f"OutlineColour={ass_color(THEME['video']['subtitle_outline'])},BorderStyle=1,Outline=2,Shadow=0,"
                 f"MarginV=70,Alignment=2")
        vf.append(f"subtitles='{srt}':force_style='{style}'")
    if plan.get("music"):
        extra_in = ["-stream_loop", "-1", "-i", str(Path(plan["music"]).expanduser())]
        afilter = ("[1:a]volume=0.25[m];[m][0:a]sidechaincompress=threshold=0.05:ratio=8[duck];"
                   "[0:a][duck]amix=inputs=2:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
    final = [ff, "-y", "-i", str(joined), *extra_in]
    if vf:
        final += ["-vf", ",".join(vf)]
    if plan.get("music"):
        final += ["-filter_complex", afilter, "-map", "0:v", "-map", "[a]"]
    else:
        final += ["-af", afilter]
    final += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
              "-b:a", "160k", "-movflags", "+faststart", str(out)]
    cmds.append(final)
    return cmds


def text_problems(plan):
    """Compliance scan (red only) and claim qualifiers (assets/brand/qualifiers.json) on subtitles and cards."""
    import compliance_scan
    import motion_video
    lines = [plan.get("title", {}).get("headline", ""), plan.get("title", {}).get("sub", "")]
    lines += [str(v) for k, v in plan.get("end", {}).items() if k != "seconds"]
    srt = Path(plan["subtitles"]).expanduser() if plan.get("subtitles") else None
    if srt and srt.exists():
        lines += [ln for ln in srt.read_text(encoding="utf-8-sig").splitlines()
                  if ln.strip() and "-->" not in ln and not ln.strip().isdigit()]
    lines = [ln for ln in lines if ln]
    worst, hits = compliance_scan.scan("\n".join(lines), platform=plan.get("platform"))
    problems = [f"{h.id} {h.match}: {h.message}" for h in hits if h.level == "red"]
    return problems + motion_video.check_qualifiers(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan", nargs="?", help="edit plan JSON")
    parser.add_argument("--out", help="output .mp4 (default outputs/videos/<plan name>.mp4)")
    parser.add_argument("--font", help="font with Chinese characters for the cards")
    parser.add_argument("--dry-run", action="store_true", help="print the ffmpeg commands without running them")
    parser.add_argument("--probe", help="print duration and size of a clip, then exit")
    args = parser.parse_args(argv)
    if args.probe:
        print(json.dumps(probe(args.probe), indent=1))
        return 0
    if not args.plan:
        parser.error("give an edit plan JSON, or --probe FILE")
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    if not plan.get("clips"):
        raise SystemExit("The plan has no clips.")
    problems = text_problems(plan)
    if problems:
        print("Fix the on-screen text before rendering:\n" + "\n".join("  - " + p for p in problems))
        return 2
    out = Path(args.out) if args.out else ROOT / "outputs" / "videos" / (Path(args.plan).stem + ".mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        cmds = build_commands(plan, out, Path(t), args.font, render_cards=not args.dry_run)
        for cmd in cmds:
            if args.dry_run:
                print(" ".join(f'"{c}"' if " " in c else c for c in cmd))
                continue
            run = subprocess.run(cmd, capture_output=True, text=True)
            if run.returncode:
                sys.stderr.write(run.stderr[-2000:])
                raise SystemExit(f"ffmpeg failed on step: {' '.join(cmd[:6])} ...")
    if not args.dry_run:
        info = probe(out)
        print(f"Wrote {out} ({info['duration']:.1f}s, {info['width']}x{info['height']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
