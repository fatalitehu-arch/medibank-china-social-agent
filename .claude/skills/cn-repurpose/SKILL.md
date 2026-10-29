---
name: cn-repurpose
description: Turn one approved Medibank post, article or script into versions for the other Chinese platforms (小红书, 公众号, 视频号, 抖音, 微博), each in the right format and with that platform's rules. Use for 改成抖音版/同步到公众号/一稿多发/多平台分发.
---

# cn-repurpose

Paths are relative to the repository root. Read: `references/platforms/overview.md`, the
platform file for each target, and the "One idea, five platforms" table in
`references/content-playbook.md`.

## Steps

1. **Start from an approved source.** If the source hasn't passed cn-compliance-review, run
   it first. Facts don't change between versions; only shape and length do.
2. **Pick targets.** Default: every platform in the overview except the source's own. Skip a
   platform when the idea doesn't fit it (e.g. a long claims guide doesn't belong on 微博;
   say so instead of forcing it).
3. **Re-shape, don't copy.** For each target, rewrite to its format:
   * 小红书: 图文 steps, cover line, 5–10 hashtags, next step "学校官网搜 OSHC"
   * 公众号: full guide with sub-heads and FAQ; this is the canonical long version
   * 视频号: 60 s script; may say "完整版在 Medibank 公众号"
   * 抖音: 15–30 s hook-first script or creator angle; no WeChat mention
   * 微博: ≤ 140 chars + 1 image + 1–3 #话题#
   Mass-posting identical text across accounts breaks PL-4; each version must read as
   written for that platform.
4. **Fix cross-references.** Mentioning 公众号 is fine on 视频号; it is diversion on 小红书
   and 抖音 (PL-3). The scanner's `--platform` option checks this.
5. **Gate every version**: `python tools/compliance_scan.py v.txt --platform <id>` and
   `python tools/note_lint.py v.txt --platform <id>`.

## Output

One block per platform, using cn-content-writer's output format, plus a one-line
publishing order (usually: 公众号 guide first, then 视频号 and 小红书 the same week,
抖音/微博 at the next peak).
