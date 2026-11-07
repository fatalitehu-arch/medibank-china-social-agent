---
name: cn-video-editor
description: Make short videos for Medibank on 抖音, 视频号 and 小红书 - either an animated explainer with no footage (pop-in text, icons, mock app screens, step lists, sound effects, subtitles) or an edit of the user's own footage (trim, join, vertical, subtitles, Medibank colour tone, title and end cards), plus a 剪映 asset pack. Checks every on-screen claim has its qualifiers. Use for 做视频/剪视频/剪辑/动画视频/科普视频/加字幕/竖屏/片头片尾/剪映素材. Needs ffmpeg on the computer.
---

# cn-video-editor

Paths are relative to the agent's root folder (`${CLAUDE_PLUGIN_ROOT}` when installed as a plugin, otherwise the repository root). Read first: `references/content-playbook.md` (short-video template) and the platform file in `references/platforms/`.

This skill makes two kinds of video. It does not film, generate people, or use clips, music
or logos the team has no licence for (TR-2 in `references/compliance.md`).

| The user has | Make | Tool |
|---|---|---|
| No footage, or a "how to" topic (claims, the app, steps) | **Animated explainer** | `tools/motion_video.py` |
| Their own clips (talking head, street scenes) | **Footage edit** | `tools/video_edit.py` |

## Before any video: confirm the plan and check the facts

1. **Facts first.** Every claim about Medibank must come from `references/brand-facts.md` or an
   official Medibank page opened today. Write down the source. A claim not found there goes in
   as `【待确认：…】` and is not rendered. Qualifiers travel with claims (e.g. Online Doctor
   "免费" → 试行服务 · 16 岁以上 · 家属不适用). The tools enforce the rules in
   `assets/brand/qualifiers.json`; add a rule there when brand-facts.md gains a new qualifier.
2. **Storyboard for the user to confirm** before rendering a full video: one row per shot with
   time, picture, subtitle / voice line and effect. 抖音/视频号 30–60 s, hook in the first 3 s,
   one idea per shot, subtitles ≤ 16 Chinese characters per line (Latin counts half).
3. **No real member data.** App screens are drawn as mock-ups labelled 示意图 until the user
   gives a screen recording with personal data hidden.

## Animated explainer (no footage)

1. Write the storyboard JSON (shape and every option: `examples/motion_storyboard.json` and the
   docstring of `tools/motion_video.py`). Scene types: `text` (`{词}` = yellow highlight), `icon`
   (thermometer, wallet, phone, video, clinic, receipt, card, check, clock, camera, upload),
   `card` (icon + label), `phone` (mock app screens with tap ripples), `steps` (numbered rows
   that light up one by one), `note` (fine print). Animations: pop, slide-left/right/up, fade.
   Optional `section` = black pill title at the top, `tag` = red number in it.
2. `python tools/motion_video.py board.json --check`: compliance scan, qualifier rules,
   subtitle length. Fix anything red.
3. `python tools/motion_video.py board.json --frames 2,10,20,30 --out outputs/videos/x.mp4`
   → PNG stills. Look at them: nothing cut off, nothing in the bottom 20% (抖音 caption area) or
   the right edge (like/comment buttons), keywords readable.
4. Render: `python tools/motion_video.py board.json --pack --out outputs/videos/<name>.mp4`.
   Sound effects (whoosh, pop, ding, click, success) are synthesised, so no licence is needed.
   There is no voice-over: suggest 剪映「文本朗读」on the .srt, or the user records one.
5. `--pack` also writes `<name>_剪映素材包/`: numbered scene clips, a no-subtitle version,
   `字幕.srt`, the sound effects (single and pre-aligned) and `时间表.csv`. The user usually
   finishes in 剪映 (its drafts can't be generated), so always deliver the pack.

## Footage edit (the user's own clips)

1. **Check the tools.** Run `ffmpeg -version`. Missing: tell the user the one command to
   install it (macOS `brew install ffmpeg`, Windows `winget install ffmpeg`) and stop.
2. **Look at the footage.** For each clip run `python tools/video_edit.py --probe <file>`
   for length and size. Ask the user which moments matter only if the brief doesn't say.
3. **Plan the cut** to the script (from cn-content-writer or the user): hook in the first
   3 seconds, one idea per shot, 30–60 s for 抖音 and 视频号. Real-life scenes beat talking
   heads [E-2].
4. **Subtitles.** Write an `.srt` from the script with times that follow the clips (the
   title card is added before them automatically). Max 16 Chinese characters per line. The
   compliance scan runs on subtitle text too: no prices, links, QR codes, WeChat IDs.
5. **Write the edit plan** JSON (shape: `examples/video_plan.json`): platform, clips with
   start/end seconds, subtitles, title card (headline ≤ 12 chars), end card (next step in
   words + 以保单条款为准), music only if the user has a licence for it, `"grade": true`.
6. **Render:** `python tools/video_edit.py plan.json --out outputs/videos/<name>.mp4`.
   It refuses to render when the subtitles or cards have a red compliance hit or a claim
   without its qualifiers.
   Use `--dry-run` to show the ffmpeg commands without running them.
7. **Check the result:** grab 3 frames (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 f.png`) at the
   title, a subtitle line and the end card, look at them, and fix overlaps or cut-off text.
8. **Hand over:** the file path, length, size, and the caption text for the post
   (from cn-content-writer, scanned with `tools/compliance_scan.py`).

Talking-head style the user likes (from past edits): one subtitle line at a time, white with a
dark outline, keywords yellow; black pill section titles (not orange boxes); key numbers pop up
large with a ding; whoosh on section changes; keep natural breath gaps.

## What the tool does

* Fits any clip to 1080×1920 (1080×1440 for 小红书) with a blurred fill, never stretching.
* Applies the Medibank colour tone from `assets/brand/theme.json` (slightly warmer and brighter).
* Burns subtitles in white with a dark outline, readable on any footage.
* Adds title and end cards drawn in Medibank colours (same renderer as the post cards).
* Ducks music under speech and normalises loudness to −16 LUFS for phone playback.

## Rules

* Brand videos say they are Medibank (end card footer). Creator videos carry no Medibank
  branding and are published by the creator through the marketplace (PL-1).
* No faces of people who haven't agreed, no real student documents (use
  `assets/images/mock-offer-letter.svg`), no screens showing personal data.
* No trending audio or show clips the team hasn't licensed (TR-2). Recreate the format instead.
