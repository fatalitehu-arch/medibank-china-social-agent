# Creator (博主) playbook

Creators carry the "看懂自己的保险" message (see `student-strategy.md`). This file
covers finding, scoring, briefing and reviewing them.

## 1. Who we want

**Profile:** Chinese students or recent graduates **currently living in Australia**,
who post about study and life there. They have personally used (or can genuinely use)
OSHC, so their story is real.

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

1. **蒲公英** (pgy.xiaohongshu.com) is the only channel for paid collaborations (XHS-1).
   Filter: category 教育/留学 or 生活; follower location 澳大利亚 or creator IP 澳大利亚;
   audience 18–30.
2. Search 小红书 for: `澳洲留学 行前`, `OSHC`, `澳洲看病`, `悉尼 GP`, `UNSW 新生`,
   `墨大 新生`, `澳洲 留学生 保险`, `offer 怎么看`. Note who ranks in the top results and
   whose comments are full of real questions.
3. Third-party data tools (千瓜数据, 灰豚数据, 新红) for engagement history and fake-fan
   checks. [VERIFY Medibank has a licence for one of these]
4. Export candidates to CSV (template: `examples/kol_candidates.csv`) and score them.

## 3. Scoring (what `scripts/kol_score.py` does)

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

## 5. The 蒲公英 brief template

```
项目名称：看懂自己的保险｜Medibank OSHC 留学生健康科普
合作形式：图文 / 视频（蒲公英报备，带合作标识）
发布时间：【日期】

一、为什么做这个
很多同学的 OSHC 是中介或学校帮忙办的，自己没看过保单，不知道保了什么、生病了怎么用。
我们希望你用自己的经历，提醒大家花几分钟看懂自己的保险。

二、请你分享的（用你自己的话）
- 你自己拿到 offer / 办签证 / 落地时，对 OSHC 的真实了解程度和经历
- 你会怎么看 offer letter 或学校官网里 OSHC 的信息
- 你在澳洲看病 / 用保险的真实经历（如果有）

三、可以使用的事实（只能用这些，不能改数字或条件）
【从 brand-facts.md 选 2–4 条，附原文限定条件】

四、必须做到
- 走蒲公英报备，保留平台合作标识
- 只讲你真实的经历和看法；没用过的功能不要说"我用过"
- 提到具体权益时加"以官网条款为准"
- 引导大家去"学校官网搜 OSHC"或"Medibank 官网"，用文字，不放链接

五、请不要
- 写价格、优惠、折扣码；和其他保险公司比较
- 说"最好/第一/保证/100%"；说"买了就能过签"
- 放微信号、二维码、电话；在评论或私信里帮人买保险或收集个人信息
- 说中介坏话
- 给签证或医疗建议

六、交稿与审核
初稿交给 Medibank 审核（合规检查约 2 个工作日），通过后发布。
```

## 6. Reviewing a creator draft

Run the normal compliance check (mode D), then also check:

| Check | Fail example |
|-------|--------------|
| Sponsor tag present / will be added by 蒲公英 | Draft says "纯分享，无广" while it is paid |
| Genuine experience | "我用了 Online Doctor 三次" when the creator has never used it |
| Not scripted | Lines copied word-for-word from the brief's fact list in every creator's note |
| No diversion | "评论区扣1我私你资料" |
| Comment plan | Creator agrees not to answer "多少钱/怎么买" with prices; replies "去学校官网或 Medibank 官网看" |

## 7. Comment-section rules (for brand and creators)

Prepared replies for common questions:

| Question | Reply |
|----------|-------|
| 多少钱？ | 价格和保障以 Medibank 官网和你学校的 OSHC 页面为准哦 |
| 能帮我买吗？ | 这里不能办理，可以去学校官网搜 OSHC，或者 Medibank 官网 |
| 和 XX 保险哪个好？ | 每家保障不一样，建议直接看各家官网条款，选适合自己的 |
| 我生病了怎么办？ | 紧急情况拨打 000。非紧急可以看看你保险的 24 小时支持热线和 app |
