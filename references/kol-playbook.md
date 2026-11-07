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
OSHC, so their story is real. Why peers: [E-2] [E-3] [E-4].

Why small creators: ordinary users are the most trusted voice on 小红书 [E-3], engagement
falls as follower counts grow past the middle [E-7], a brand little known in China gains
less from big follower counts [E-8], and follower count itself does not predict purchase
[E-14]. Medibank's choice is to work mostly with creators **under 2k followers**; the exact
mix is an assumption [A-2].

| Band | Followers | Role in the campaign |
|------|-----------|----------------------|
| <500 | under 500 | Real students telling one story each; closest to a friend's post |
| 500–1k | 500–999 | Core: student storytellers with a small, engaged following |
| 1k–2k | 1,000–1,999 | Core: regular student creators, checklists and first-person stories |
| 2k+ | 2,000 and up | Few; only when the fit is strong |

**Paid route check:** small accounts may be below the 蒲公英 entry threshold (reported as
5,000 followers in 2022–23; some reports mention selected 1k–5k creators) [VERIFY with
Xiaohongshu]. Any paid or gifted post must still be labelled 广告 [E-12]; never pay off-platform
without disclosure.

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

Score out of 100. Six criteria, each measured 0–1 from the creator's last 10 or so posts.
Each weight is that criterion's correlation with purchase intention in two meta-analyses
[E-14] [E-15], divided by the sum of the six and rounded. The correlations are close
(0.43–0.55), so the weights are close too. They are an evidence-based starting point, to be
checked against our own results [A-5].

| Criterion | Weight | Evidence (r with purchase intention) | How it's measured |
|-----------|--------|--------------------------------------|-------------------|
| Useful content | 20 | 0.55 informational value [E-14] | Share of posts that are guides, checklists, how-tos |
| Like our students | 18 | 0.51 homophily [E-15] | Lives in Australia (half) + share of audience who are students (half) |
| Shares own life | 17 | 0.47 self-disclosure [E-14] | Share of posts about their own real experience |
| Topic fit | 16 | 0.45 brand fit [E-14] | Share of posts on study, life or health in Australia |
| Talks with followers | 15 | 0.43 communication [E-14] | Share of comment threads the creator replies to |
| Trustworthy | 14 | 0.43 trustworthiness [E-15] | Starts full; −half for diverting followers off-platform, −half for unreported past ads |

**Not scored:**
* **Follower count.** No positive link to purchase intention (r = −0.28, n.s.) [E-14];
  engagement peaks at a middle count [E-7]; fraud is more common in big accounts [E-16].
  Followers set the tier and the budget mix only [A-2].
* **Expertise.** Weaker (r = 0.36) [E-15], and the insurance facts come from Medibank, not
  the creator.
* **Price.** Handled in the budget, not the score.

**Hard stops (score = 0, reason shown):** sells agency or insurance services (non-insurers
may not consult on or compare insurance [E-13]); promoted another OSHC insurer in the last
90 days; history of undisclosed ads [E-12]; fake-fan flag from the data tool [E-16];
content that breaks platform rules.

Labelling a post 广告 does not reduce its effect (r = 0.06, n.s.) [E-14], so always label.

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
