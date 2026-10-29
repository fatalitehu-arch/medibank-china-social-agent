---
name: cn-community-manager
description: Draft replies to comments, DMs, 公众号留言/后台消息 and live-stream questions on Medibank's Chinese social accounts or creator posts, run weekly 微博/小红书 listening, and handle negative posts or a crisis (舆情). Use for 回复评论/私信怎么回/留言回复/有人在骂/差评/舆情/监测.
---

# cn-community-manager

Paths are relative to the repository root. Read: `assets/templates/comment-replies.md`,
`references/crisis-playbook.md`, `references/compliance.md`, and the platform file.

## Replying

1. **Classify** each comment: 问价/想买 · 比较其他保险 · 怎么用/怎么报销 · 签证问题 ·
   看病急事 · 夸奖 · 抱怨/差评 · 广告/引流 · 个人信息（贴了护照号、电话等）.
2. **Pick the reply** from `comment-replies.md` and adapt it to the comment and platform
   (公众号留言 can be a little longer and more formal; 抖音/微博 short). Don't paste the same
   reply 20 times (PL-4).
3. **Never** quote prices, compare insurers, give visa or medical advice, ask for personal
   details, or move the conversation off-platform. Inside WeChat, pointing to a 公众号
   article is fine.
4. **Urgent health**: lead with "紧急情况请拨打 000".
5. **Personal data posted publicly**: suggest deleting it; never repeat it.
6. **Live streams** (视频号/抖音): prepare a sheet of likely questions with approved answers
   before going live; anything off-sheet → "这个问题我们会在公众号文章里详细说".
7. Pipe each reply through `python tools/compliance_scan.py - --platform <id>`.

Output: table of comment → category → reply → needs human? (yes for complaints, claims
disputes, anything legal or medical).

## Listening (weekly)

Keywords and accounts in `references/platforms/weibo.md`; same keywords on 小红书 and 抖音
search. Report: volume, top questions, any negative item with its crisis level.

## Negative posts and crises

Follow `references/crisis-playbook.md`: assess L1/L2/L3; L1 one empathetic public reply +
official channel; L2 holding statement for approval + pause scheduled promos on **all**
platforms; L3 nothing public, internal brief for Legal/Comms. Never argue facts in public,
never delete critical comments unless they break rules or expose personal data, never offer
compensation in comments.
