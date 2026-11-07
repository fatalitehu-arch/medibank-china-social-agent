# Trend playbook (热点)

How the agent finds Chinese social media trends and decides whether Medibank should ride
them. Used by `skills/cn-trend-scout/SKILL.md` and `tools/trend_score.py`. The latest
dated snapshot is in `references/trend-radar.md`.

## 1. Where to look

| Source | What it shows | Notes |
|--------|---------------|-------|
| 微博热搜 / 微博文娱榜 | What the whole internet is talking about today | Fastest signal; also where crises start |
| 抖音热榜 / 巨量算数 | Rising videos, sounds, challenges; search trends | Challenges and dances show up here first |
| 小红书 搜索发现 / 热门话题 / 灵感 | What students search and save | Best for "how to" angles that last weeks |
| 微信指数 / 公众号 10w+ articles | What parents and long-form readers follow | Slower, good for explainers |
| 视频号 热门 | Older and family audience | Useful for parent-facing angles |
| Entertainment news (新浪娱乐, 腾讯新闻, 澎湃, 36氪, 虎嗅) | Context and dates for shows and memes | Use for the one-line explanation and the source link |
| Data sites (云合数据, 猫眼, 灯塔, 新榜, 千瓜) | Show ratings, creator and topic data | Cite numbers only from here or the platform |

Search in Chinese with the month and year (e.g. "热梗 2026年11月", "综艺 热度 本周").
Keep only items with a dated source from the last 14 days (or a long-running show still airing).

## 2. Scoring rubric (what `tools/trend_score.py` does)

The weights are a working assumption [A-6]; test them against trend posts' saves.

| Factor | Weight | Question |
|--------|--------|----------|
| Audience match | 30 | Do Chinese students heading to or living in Australia (and their parents) care about it? 1–5 |
| OSHC / health link | 30 | How naturally does it lead to health, getting care, or insurance awareness? 1–5 |
| Freshness | 20 | How far into its expected life is it? Meme or challenge ≈ 3 weeks, hashtag ≈ 1 week, show ≈ its run (default 8 weeks), event until the date |
| Safety | 20 | Starts at 20, −5 for each soft flag |

Soft flags (−5 each): `ip_heavy` (the trend is someone's show or song), `celebrity`
(real people at the centre), `health_risk` (physical injury risk), `competitor_sponsor`
(another insurer sponsors it).
Hard flags (always **avoid**): `politics`, `tragedy`, `scandal`, `crime`, `mocking`,
`misinformation`.

| Score | Verdict | Meaning |
|-------|---------|---------|
| ≥ 70 | use now | Owned and creator posts this week |
| 50–69 | adapt | Light touch: creator-led, or borrow the format only |
| < 50 | watch | Not worth it yet; re-check next week |
| hard flag | avoid | No angle at all |

## 3. Angle patterns

The angle borrows the trend's **question, format or feeling**, then lands on a content
pillar (看懂你的保险 · 在澳洲看病 · 用好 app 和热线 · 身心健康). It never borrows the footage.

| Pattern | Works for | Shape | Example |
|---------|-----------|-------|---------|
| **The show asks, Australia answers** | Shows about hospitals, jobs, study | Take a moment or theme from the show, answer the same question for a student in Australia | Medical show → "在澳洲第一次去医院，流程是这样的" |
| **Safety twist** | Dances, sports, food, travel trends | Join the fun, then what to do if it goes wrong | Viral dance → "扭到脚了？在悉尼看急诊前先知道这 3 件事" |
| **Format borrow** | Reality formats, quizzes, "测一测" | Reuse the structure, not the content | Friendship show → "留学搭子互相检查：你们的保险都看过吗？" |
| **Catchphrase hook** | Memes and quotes | Use the phrase as an opener only when its meaning fits and it isn't tied to a person's conflict | |
| **Moment calendar** | Holidays, exams, intake, O-Week | Plan ahead; not strictly a trend but scored the same way | 双十一 → "别囤药，先看看你的保险里有什么" |

## 4. Never touch

Politics, national or historical topics, disasters and accidents, deaths, crime, celebrity
scandals or feuds (taking sides in a real person's conflict), anything that mocks a region,
gender or group, medical misinformation, and content that encourages dangerous copying.
Rules and sources: `references/compliance.md` section 6.

## 5. Shelf life and cadence

* Check trends every Monday (with the weekly plan) and any day a big show or meme breaks.
* Memes and challenges: post within 7 days of picking them up, or drop them.
* Shows: one owned angle per week of the run is plenty; creators can ride it longer.
* Record every trend you used, with its result, in the monthly report; a trend that drove
  saves and questions is a pattern to reuse.
