# Creator (博主) playbook: all platforms

Creators carry the "看懂自己的保险" message (see `student-strategy.md`). This file
covers finding, scoring, briefing and reviewing them.

## 1. Who we want

| Platform | Best creator type |
|----------|-------------------|
| 小红书 | KOC and 腰部 students in Australia writing checklists and first-person stories |
| 抖音 | 腰部 vlog creators (留学第一周, 悉尼生活) for awareness at intake peaks |
| 视频号 | Creators followed by parents (留学家长, education explainers) |
| 公众号 | Student-life and city-guide accounts (e.g. 悉尼/墨尔本留学生活号) for co-published guides |
| 微博 | University alumni and study-abroad bloggers, only at O-Week topic peaks |


**Profile:** Chinese students or recent graduates **currently living in Australia**,
who post about study and life there. They have personally used (or can genuinely use)
OSHC, so their story is real.

Follower tiers are the same on every platform; engagement baselines differ (see
`tools/kol_score.py`, which takes a `platform` column).

| Tier | Followers | Role in the campaign | Share of budget |
|------|-----------|----------------------|-----------------|
| KOC (素人/小博主) | 1k–10k | Many authentic first-person stories; high trust; cheap | ~40% |
| 腰部 KOL | 10k–100k | Core reach in 澳洲留学 niche; tutorials and checklists | ~45% |
| 头部 KOL | 100k+ | One or two per intake for awareness peaks (O-Week) | ~15% |

Priority niches: 澳洲留学/悉尼生活/墨尔本生活, 留学行前准备, 学校新生 (UNSW, USYD,
Monash, UniMelb…), 留学生日常 vlog, 健康/心理 (with care).

**Avoid:** 留学中介 accounts or creators who sell agency services (conflict of
interest, and the message is about not over-relying on agents); 保险代理/理财 accounts
(they'd turn it into selling); accounts that post 搬运/搞钱/引流 content; anyone with a
recent sponsored note for another OSHC insurer (in the last 90 days).

## 2. How to find them

1. **The platform's official marketplace** is the only channel for paid collaborations (PL-1):
   小红书 蒲公英 · 抖音 巨量星图 · 微信公众号/视频号 互选平台 · 微博 微任务 [VERIFY].
   Filters below use 蒲公英 terms; the other marketplaces have equivalents.
   Filter: category 教育/留学 or 生活; follower location 澳大利亚 or creator IP 澳大利亚;
   audience 18–30.
2. Search 小红书 and 抖音 for: `澳洲留学 行前`, `OSHC`, `澳洲看病`, `悉尼 GP`, `UNSW 新生`,
   `墨大 新生`, `澳洲 留学生 保险`, `offer 怎么看`. Note who ranks in the top results and
   whose comments are full of real questions.
3. Third-party data tools (千瓜数据, 灰豚数据, 新红) for engagement history and fake-fan
   checks. [VERIFY Medibank has a licence for one of these]
4. Export candidates to CSV (template: `examples/kol_candidates.csv`) and score them.

## 3. Scoring (what `tools/kol_score.py` does)

Score out of 100. Weights are in the script and can be changed by Medibank.

| Criterion | Weight | How it's measured |
|-----------|--------|-------------------|
| Audience fit | 30 | Lives in Australia (15) + audience mostly students 18–30 (15) |
| Engagement quality | 25 | (likes+saves+comments) ÷ followers on recent notes; saves weighted ×2 because saves mean "useful" |
| Topic relevance | 20 | Share of recent notes on study/life in Australia |
| Trust & safety | 15 | No hard red flags, past sponsored notes properly reported |
| Cost efficiency | 10 | Quoted price per 1k followers vs tier median |

**Hard stops (score = 0, reason shown):** sells agency or insurance services; promoted
another OSHC insurer in the last 90 days; history of undisclosed ads; fake-fan flag
from the data tool; content that breaks platform rules.

Bands: **≥70 go**, **50–69 maybe (human look)**, **<50 no**.

## 4. Vetting checklist (for a single creator)

- [ ] Real person, really in Australia (posts show local life, not stock photos)
- [ ] Comments are real questions and conversations, not emoji spam
- [ ] Follower growth looks organic (no sudden jumps)
- [ ] Past sponsored notes carry the 蒲公英 tag
- [ ] No 引流 (WeChat IDs, QR codes) in past notes
- [ ] No agency or insurance selling
- [ ] Tone fits: helpful, honest, not 标题党
- [ ] No conflicts in the last 90 days

## 5. The creator brief

Template: `assets/templates/creator-brief.md`. Send it with
`assets/templates/creator-onboarding.md`. Contract terms: `references/creator-contract-terms.md`.

## 6. Reviewing a creator draft

Run the normal compliance check (mode D), then also check:

| Check | Fail example |
|-------|--------------|
| Sponsor tag present / will be added by the marketplace | Draft says "纯分享，无广" while it is paid |
| Genuine experience | "我用了 Online Doctor 三次" when the creator has never used it |
| Not scripted | Lines copied word-for-word from the brief's fact list in every creator's note |
| No diversion | "评论区扣1我私你资料" |
| Comment plan | Creator agrees not to answer "多少钱/怎么买" with prices; replies "去学校官网或 Medibank 官网看" |

## 7. Comment-section rules

Prepared replies: `assets/templates/comment-replies.md`. Creators agree to use them for
questions about price, buying, comparisons and health emergencies.
