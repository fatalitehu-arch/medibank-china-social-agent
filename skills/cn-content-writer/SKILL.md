---
name: cn-content-writer
description: Write Medibank owned-account content for 小红书, 微信公众号, 微信视频号, 抖音 or 微博 - posts, long articles, short-video scripts, titles, covers, hashtags and image plans. Use for 写一篇/写笔记/写推文/写脚本/想标题/改稿. Not for creator content (use cn-kol-manager).
---

# cn-content-writer

Paths are relative to the repository root. Read first: `references/brand-facts.md`,
`references/content-playbook.md`, `references/personas.md`, and the platform file in
`references/platforms/`. Read `references/style-checks.md` and `references/compliance.md`
only **after** the body is written (reading them first makes the writing stiff).

## Three ways in

| Input | Mode |
|-------|------|
| A topic or brief ("写一篇：怎么激活 OSHC") | **共创 Draft** |
| Source material (a policy page, FAQ, university page) | **拼贴 Adapt** |
| An existing draft ("帮我改一下") | **改稿 Edit** |

## Steps

1. **Pin the job** in one line: platform, persona (`personas.md`), pillar
   (`content-playbook.md`), and the one thing the reader should know or do afterwards.
2. **Collect facts** only from `brand-facts.md`, the source material, or the user. Missing
   fact → `【待确认：…】`. Never invent numbers, stories, quotes or screenshots.
3. **Skeleton** using the template for the platform in `content-playbook.md`
   (图文 explainer · 公众号 guide · short-video script · 微博 short post).
4. **Write** in the brand voice, at the platform's length and format (platform file).
5. **Gate 1, mechanical**: save the draft and run
   `python tools/compliance_scan.py draft.txt --platform <id>` and
   `python tools/note_lint.py draft.txt --platform <id>`.
   Fix every 🔴. Fix 🟡 or add the qualifier. Fix lint errors unless that makes the
   sentence stiff.
6. **Gate 2, human read**: reread as the persona on that platform. Rewrite any line that
   sounds like an ad, a translation or a textbook.
7. **Packaging** per platform: titles/covers (`style-checks.md` limits), hashtags (counts in
   `content-playbook.md`), image or shot list. Use `assets/images/mock-offer-letter.svg`
   for offer-letter explainers; never a real student's document.

## Output format

```
【平台】 xiaohongshu / wechat-oa / wechat-channels / douyin / weibo
【正文】 (or 【脚本】 for video: time | on screen | voice-over)
【封面文案】 1–3        (小红书, 公众号 cover, video cover)
【标题候选】 1–5
【Hashtags】 one line   (if the platform uses them)
【配图建议】 numbered   (or 【分镜】 for video)
【合规结论】 🟢/🟡/🔴 + one line per issue (rule ID)
【需要 Medibank 确认】 every 【待确认】 item
```

## Series ideas

* 《看懂你的保险》5 集: offer letter → 保单日期 → 学校 OSHC 页面 → 激活和 app → 第一次报销
* 《在澳洲看病》4 集: GP vs 急诊 vs 000 → 预约 GP → 药房和处方 → 半夜不舒服怎么办
* 《24 小时热线能帮你什么》3 集: 护士咨询 → 心理支持 → 翻译和法律咨询
* 《写给家长》3 篇 (公众号/视频号): 孩子生病了怎么办 → 热线和翻译 → 怎么提醒孩子看保单

After writing, offer to run cn-repurpose for the other platforms.
