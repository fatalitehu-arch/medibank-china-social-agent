# Compliance guardrails for Medibank OSHC content on Chinese social media

Applies to 小红书, 微信公众号, 微信视频号, 抖音 and 微博 (platform details in
`references/platforms/`).

> **Status:** research summary prepared by a UNSW CDEV3000 student team, October 2026.
> It is **not legal advice**. Every rule below should be confirmed by Medibank Legal
> & Compliance (Australia) and by PRC counsel before the agent is used in production.
> Items marked **[VERIFY]** are ones the team could not confirm from a primary source.

The agent applies these rules whenever it **writes** content, **briefs a creator**,
**replies to comments**, or **checks** a draft, on every platform. Every output ends with a
traffic-light verdict: 🟢 publish after normal review, 🟡 fix the flagged lines first,
🔴 do not publish.

---

## 1. Why this market is different

Medibank is an Australian private health insurer. It holds no insurance licence in
mainland China. Most users of these platforms are mainland residents, and every one of the
five platforms is a mainland platform under mainland law. That creates a tension:

* Prospective students in China **must** buy OSHC before arriving in Australia
  (Student visa subclass 500 condition; Department of Health and Aged Care OSHC fact
  sheet, Aug 2026), so they genuinely need information about it.
* But content that **sells, quotes, compares or arranges** an overseas insurance
  product for mainland residents looks like unlicensed insurance business in China.

**The core rule:** on Chinese social media, Medibank *informs and helps*; it does not *sell*.
Purchase always happens off-platform, on Medibank's Australian website or through the
student's education provider or registered education agent.

---

## 2. Mainland China rules (PRC)

| # | Rule | What it means for a post |
|---|------|--------------------------|
| CN-1 | 《互联网保险业务监管办法》(原银保监会令2020年第13号, in force 1 Feb 2021) Art. 3: internet insurance business may only be carried out by licensed insurance institutions; "其他机构和个人不得开展互联网保险业务". | Medibank (and any creator) must not run insurance business through any of these platforms. |
| CN-2 | Same Measures, Art. 23 (negative list for non-insurers): no 提供保险产品咨询、比较保险产品/保费试算/报价比价、设计投保方案、代办投保手续、代收保费. | No price quotes, no premium calculators, no "Medibank vs Allianz vs Bupa" tables, no "DM me and I'll buy it for you". |
| CN-3 | Unlicensed insurance business is prohibited under the PRC Insurance Law (《保险法》, licensing chapter) and regulators have repeatedly warned mainland residents about cross-border insurance sold through unofficial channels. **[VERIFY exact articles with PRC counsel]** | Never present Medibank as available "in China", never imply a mainland office, agent or licence. |
| CN-4 | 《广告法》(2021 rev.) Art. 4 & 28: ads must be truthful, not false or misleading. Art. 14: ads must be identifiable as ads. | No exaggerated or absolute claims; sponsored content must be labelled. |
| CN-5 | 《互联网广告管理办法》(SAMR, in force 1 May 2023): internet ads must be identifiable, with "广告" shown clearly; paid-for KOL content counts. | Brand-paid creator content goes through the platform's marketplace and carries its sponsor/ad tag. |
| CN-6 | 《个人信息保护法》(PIPL) Arts. 13, 38–39: consent for collecting personal information; extra conditions for sending it outside China. | Don't collect names, phone numbers, passport or CoE details in comments, DMs, 留言 or live chat. Send people to Medibank's own site. |
| CN-7 | Absolute-term ban (广告法 Art. 9(3)): 最、第一、国家级、顶级、唯一 etc. | Medibank's own "largest OSHC insurer in Australia" claim (APRA data) is lawful in Australia but **cannot** be phrased as "最大/第一" on Chinese platforms. |

## 3. Platform rules (all five platforms)

| # | Rule | What it means | Platform specifics |
|---|------|---------------|-------------------|
| PL-1 | Paid creator content must be booked through the platform's official marketplace and show its sponsor/ad label. Private deals are penalised. | Never pay or brief a creator outside the marketplace. | 小红书 **蒲公英** (《品牌违规扣分管理规则》, Apr 2022); 抖音 **巨量星图** (deals outside 星图 risk takedown/limits); 微信 **互选平台** (公众号 and 视频号); 微博 commercial orders (**微任务**) [VERIFY] |
| PL-2 | Paid ads in finance/insurance categories need qualification documents. **[VERIFY whether an overseas insurer can get brand accounts or ad access on each platform; assume NO paid ads until confirmed]** | Default plan = organic owned content + marketplace creator content. | 小红书 聚光, 抖音 巨量引擎, 微信 广点通, 微博 粉丝通 all review advertiser qualifications |
| PL-3 | Off-platform diversion (导流) is restricted and throttled. | No QR codes, phone numbers, WeChat IDs or purchase links. Name the next step in words. | 小红书/抖音: naming WeChat or a 公众号 counts as diversion. Inside WeChat (公众号 ↔ 视频号) internal links are normal. |
| PL-4 | Fake engagement (刷量), fake "real user" posts from paid accounts, and mass copy-paste content are banned. | No seeding networks with near-identical scripts. | All platforms |

## 4. Australian rules

| # | Rule | What it means |
|---|------|---------------|
| AU-1 | Australian Consumer Law (Competition and Consumer Act 2010, Sch 2) s 18 (misleading or deceptive conduct) and s 29 (false or misleading representations). Applies to Medibank's conduct wherever the audience is. | Every factual claim must be accurate and current: benefits, limits, waiting periods, "no out-of-pocket" claims. |
| AU-2 | ACCC influencer sweep (7 Dec 2023): influencers must clearly disclose promotional posts, including gifts; businesses must make sure influencers know their ACL obligations and must not script them to misrepresent their experience. | Creator briefs must require disclosure and must let creators speak in their own words about real experiences. |
| AU-3 | AANA Code of Ethics s 2.7: advertising must be clearly distinguishable as advertising. | Same as CN-4/5: sponsored = labelled. |
| AU-4 | Private Health Insurance Act 2007 and APRA prudential regime; OSHC is provided under a Deed with the Commonwealth. The Private Health Insurance Code of Conduct sets standards for sales and marketing. **[VERIFY with Medibank which internal policies apply to social content]** | Product descriptions must match the current policy documents. Use Medibank's approved wording for cover levels. |
| AU-5 | Students can choose their own OSHC insurer and do not have to accept an education provider's choice (DoHAC OSHC fact sheet). | Never say or imply Medibank is "the official/required" OSHC, or that a visa needs Medibank specifically. |
| AU-6 | Migration advice may only be given by registered migration agents (Migration Act 1958, Part 3). | Visa content is limited to "OSHC is a visa condition, check Home Affairs". No visa strategy, no "this guarantees your visa". |
| AU-7 | Privacy Act 1988 / APPs; Spam Act 2003. | Same as CN-6: no lead capture through social comments, DMs or 留言. |

## 5. The red / amber / green list (used by `rules/red_flags.json`)

### 🔴 Never publish
* Prices, premiums, "from $X", discounts, promo codes, "限时优惠"
* Premium calculators, quotes, "帮你算保费"
* Side-by-side comparisons with named competitors (Allianz, Bupa, nib, ahm, CBHS…)
* Buy / sign-up instructions on the platform: "点击链接购买", "私信下单", "代买", "代办"
* Collecting personal data: "留下手机号/微信/护照号"
* Absolute terms: 最好, 最便宜, 第一, 唯一, 100%, 保证, 绝对
* Visa guarantees: "买了就能过签", "保证下签"
* Unpaid-but-actually-paid creator posts, private deals outside the platform marketplace
* Claims about being licensed or present in mainland China
* Health or medical outcome claims ("治好", "保证报销")

### 🟡 Allowed with care (needs a qualifier or Legal check)
* Any specific benefit, limit, or waiting period → must match the current policy doc and say "以官网条款为准"
* "No out-of-pocket" / "免费" → only for the exact service and conditions Medibank states
* Mental-health topics → supportive tone, include crisis line info, no diagnosis
* Mentions of universities → no implied endorsement unless there is a partnership agreement
* User-generated stories → real, consented, and not edited to change meaning

### 🟢 Encouraged
* How the Australian health system works (Medicare vs OSHC, GP vs hospital)
* "What to do when you're sick in Sydney at 2 am" style service explainers
* How to use the Medibank app, make a claim, find a GP, use the Student Health and Support Line
* Arrival checklists, culture and wellbeing content
* Creators sharing genuine experiences of using cover, clearly labelled when sponsored

---

## Sources

* Department of Health and Aged Care, *Overseas Student Health Cover (OSHC) – Fact sheet* (Aug 2026), health.gov.au
* ACCC, *Social media influencer testimonials and endorsements* (7 Dec 2023) and media release *Scrutiny of influencers and businesses for misleading advertising and online reviews continues* (7 Dec 2023), accc.gov.au
* 德恒律师事务所, 《互联网保险业务监管办法》解读 (Art. 3, Art. 23 summary), dehenglaw.com
* 界面新闻 (28 Jun 2022), 小红书《品牌违规扣分管理规则》, jiemian.com
* 36氪 (21 Jul 2018), 抖音星图上线及商单规则, 36kr.com
* 人人都是产品经理 (21 Sep 2023), 视频号互选平台, woshipm.com
* Dragon Trail, *FAQ: Opening a brand account on WeChat*, dragontrail.com
* Medibank, *Overseas Student Health Cover* product page (accessed 29 Oct 2026), medibank.com.au
