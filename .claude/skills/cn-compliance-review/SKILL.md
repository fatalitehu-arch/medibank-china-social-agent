---
name: cn-compliance-review
description: Check any Medibank draft for 小红书, 微信公众号, 视频号, 抖音 or 微博 - post, article, video script, caption, cover text, comment reply or creator content - against PRC, Australian and platform rules, and return a 🟢/🟡/🔴 verdict with fixes. Use for 能不能发/审稿/合规检查, and as the final gate for every other sub-skill.
---

# cn-compliance-review

Paths are relative to the repository root. Read: `references/compliance.md` (always, in
full), the platform file in `references/platforms/`, `references/style-checks.md`,
`references/brand-facts.md`.

## Steps

1. **Scan words.** Save the text and run
   `python tools/compliance_scan.py draft.txt --platform <id>` (`--json` to parse).
   Platform matters: e.g. naming the 公众号 is fine on 视频号 but diversion on 小红书.
2. **Read for meaning** against every table in `compliance.md`. The scanner misses:
   * implied comparison ("别家报销要等很久，这家很快")
   * implied selling ("出发前把这件事办了，评论区告诉你怎么弄")
   * fake neutrality (a paid creator writing as if unpaid)
   * claims that need a qualifier but have none
   * video: on-screen text, spoken lines and captions (ask for the script if only a
     description was given); live-stream talking points
   * images and cover text (ask for them if mentioned but not given)
   * facts that don't match `brand-facts.md`
3. **Check facts.** Every benefit, number and service must match `brand-facts.md`.
4. **Decide.**
   * 🔴 any red rule hit, or a meaning-level issue of the same kind
   * 🟡 amber items without their qualifier, or facts not in `brand-facts.md`
   * 🟢 nothing above (creator and high-reach content still go to Legal)

## Output

```
平台：…
结论：🟢/🟡/🔴（一句话原因）

问题清单
1. 原文：「…」
   规则：CN-2（报价）
   改为：「…」

需要人工确认（Medibank Legal / PRC counsel）
- …

修改后全文（only if there were 🔴/🟡 items）
```

Keep the user's voice when fixing; change only what the rule requires.

## Escalate, don't decide

"Send to Legal before publishing" for: claims refusals or disputes, mental-health crisis
content, mentions of a regulator or media, a university partnership not listed in
`brand-facts.md`, any paid ads (聚光/巨量引擎/广点通/粉丝通), any live stream, and opening
a new platform account.
