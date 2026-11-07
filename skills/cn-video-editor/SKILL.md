---
name: cn-video-editor
description: Cut simple short videos for Medibank on 抖音, 视频号 and 小红书 - trim and join clips, make them vertical, burn in subtitles, apply the Medibank colour tone, add title and end cards and background music, from the user's own footage. Use for 剪视频/剪辑/做个短视频/加字幕/竖屏/片头片尾. Needs ffmpeg on the computer.
---

# cn-video-editor

Paths are relative to the agent's root folder (`${CLAUDE_PLUGIN_ROOT}` when installed as a plugin, otherwise the repository root). Read first: `references/content-playbook.md` (short-video template) and the platform file in `references/platforms/`.

This skill edits footage the user already has. It does not film, generate people, or use
clips, music or logos the team has no licence for (TR-2 in `references/compliance.md`).

## Steps

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
   Use `--dry-run` to show the ffmpeg commands without running them.
7. **Check the result:** grab 3 frames (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 f.png`) at the
   title, a subtitle line and the end card, look at them, and fix overlaps or cut-off text.
8. **Hand over:** the file path, length, size, and the caption text for the post
   (from cn-content-writer, scanned with `tools/compliance_scan.py`).

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
