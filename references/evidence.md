# Evidence register

Every strategic choice in this agent points to a row here. **E-** rows are published
evidence (opened and checked on the date shown). **A-** rows are working assumptions: no
published data yet, so each one says how the team will test it. Skills and reference files
cite rows as `[E-3]` or `[A-2]`; `tools/evidence_check.py` fails if a cited row is missing.

When the agent recommends a strategy, it names the row it rests on. When nothing here
supports a claim, it says so and adds an A- row instead of stating it as fact.

## E: published evidence

| ID | Finding | Number | Source | Checked | Reliability |
|----|---------|--------|--------|---------|-------------|
| E-1 | Education agents arrange most Chinese students' enrolments in Australia (and usually their OSHC) | 73% of Chinese students referred by agents, 2018 | [ICEF Monitor, Oct 2019](https://monitor.icef.com/2019/10/education-agents-refer-75-of-australias-international-students/), from Dept of Education PRISMS data | 2026-11-05 | Official data; 2018 figure |
| E-2 | People trust people they know far more than ads; real-life situations are the most trusted ad style | 88% trust friends and family; 71% trust influencers | [Nielsen Trust in Advertising 2021](https://www.nielsen.com/ja/news-center/2021/trust-in-advertising-study-reveals-real-life-situations-and-humour-as-the-top-attributes/) | 2026-11-05 | Global industry survey, not student-specific |
| E-3 | On Xiaohongshu, regular users are trusted more than KOLs or brand accounts | 46.6% trust regular users, 30.3% KOLs, 22.9% brand accounts | [Digital Business Lab 2025, via Marketing-Interactive](https://www.marketing-interactive.com/singapore-consumers-trust-peers-over-brands-on-xiaohongshu) | 2026-11-05 | n = 510, Hong Kong and Singapore users |
| E-4 | International students in Australia rate peers among the most trusted sources, above any university service; Medibank recommends equipping peer networks | Report p. 23, 26 | [Medibank and Nous, From Surviving to Thriving, 2026](https://www.medibank.com.au/content/dam/overseas/pdfs/Medibank-Nous-From-Surviving-to-Thriving-Report-2026.pdf) | 2026-11-05 | n = 2,296, six universities, 34% from China; cross-sectional |
| E-5 | Students don't understand their OSHC | Only 39% of students with poorer wellbeing know what OSHC does not cover (54% of others); fewer than 1 in 5 understand the Australian health system well | Same report, p. 32; [Insurance Business, Oct 2026](https://www.insurancebusinessmag.com/au/news/life-insurance/struggling-international-students-understand-their-health-cover-least-medibank-finds-595667.aspx) | 2026-11-05 | As E-4 |
| E-6 | Chinese students read study-abroad content shared by friends | About 60% would read it in friends' WeChat Moments vs 34.6% from WeChat generally | [Ali and Hu 2022, OJCMT 12(4)](https://ojcmt.editorialpark.com/download/online-information-and-communication-through-wechat-and-chinese-students-decisions-for-studying-in-12468.pdf) | 2026-11-05 | Peer-reviewed; n = 104, New Zealand, convenience sample |
| E-7 | Engagement peaks at a middle follower count, then falls; own-style content helps small creators | Inverted U across 1,700+ influencers, 800+ campaigns | [Wies, Bleier and Edeling 2022, Journal of Marketing](https://ama.org/2022/10/11/finding-goldilocks-influencers-why-high-follower-count-may-not-be-the-best-driver-of-engagement-on-social-media), DOI 10.1177/00222429221125131 | 2026-11-05 | Peer-reviewed; Instagram data |
| E-8 | Lesser-known brands gain less from big follower counts | Follower effect weaker for unfamiliar brands | Same study, [EurekAlert summary](https://www.eurekalert.org/news-releases/967572) | 2026-11-05 | Peer-reviewed |
| E-9 | People use peers for experience services, experts for credence services (insurance, medical) | Qualitative result, experiments | [Keh and Sun 2018, Journal of Service Research](https://impact.monash.edu/marketing/peers-versus-experts-whose-opinion-do-we-value-more/) | 2026-11-05 | Peer-reviewed |
| E-10 | Xiaohongshu works as a search engine | ~70% of monthly users search; ~1/3 search first on opening; ~90% say results affect what they buy | [IT之家, 13 Dec 2024](https://www.ithome.com/0/817/514.htm), citing Xiaohongshu data | 2026-11-05 | Official figures relayed by press; undated |
| E-11 | Study-abroad audience on Xiaohongshu is young and mostly female; daily-life content performs best | 84.2% female; 18–34 = 78.6%; daily life top category | [iClick 2026](https://kr.i-click.com/iclick-news/xiaohongshu-insightshow-to-capture-the-evolving-chinese-study-abroad-market-in-2026/) | 2026-11-05 | Agency data, 118 creators, 30 days |
| E-12 | Experience-sharing or review content that promotes a product must be labelled 广告 | 《互联网广告管理办法》Art. 9, in force 1 May 2023 | [中国新闻网, Mar 2023](https://www.chinanews.com.cn/cj/2023/03-24/9978027.shtml) | 2026-11-05 | Regulation; check official SAMR text before external use |
| E-14 | Across 251 papers, what an influencer posts and how they behave predicts purchase intention; follower count does not | Correlation r with purchase intention: informational value 0.55, self-disclosure 0.47, influencer–brand fit 0.45 (0.80 on content platforms), communication 0.43 (0.51 with actual purchase); follower count −0.28 (n.s.); ad disclosure 0.06 (n.s.) | [Pan, Blut, Ghiassaleh & Lee 2025, Journal of the Academy of Marketing Science 53:52–78](https://doi.org/10.1007/s11747-024-01052-7) | 2026-11-07 | Peer-reviewed meta-analysis; 1,531 effect sizes, 27 countries; open access |
| E-15 | Creators similar to their audience, and trusted ones, drive purchase intention more than expert ones | r with purchase intention: homophily 0.51, trustworthiness 0.43, expertise 0.36 | [Han & Balabanis 2024, Psychology & Marketing 41(2):394–426](https://openaccess.city.ac.uk/id/eprint/31583/) | 2026-11-07 | Peer-reviewed meta-analysis; 53 studies, n = 25,080; high heterogeneity (I² often >85%) |
| E-16 | Fake followers and bought engagement are common, and more common in bigger accounts | 55% of Instagram influencers involved in some fraud; 66% of 1M+ accounts vs 42% of 1k–5k | [HypeAuditor 2020, via Campaign](https://www.campaignlive.co.uk/article/half-instagram-influencers-engaged-fraud-45-accounts-fake/1713079) | 2026-11-07 | Vendor data, 12M Instagram accounts; not Chinese platforms |
| E-13 | Only licensed insurers may run internet insurance business; non-insurers may not consult on, compare or quote insurance | 《互联网保险业务监管办法》Arts. 3, 23 (in force 1 Feb 2021) | `references/compliance.md` CN-1, CN-2 | 2026-10-29 | Regulation; [VERIFY] with PRC counsel |

## A: working assumptions (to test)

| ID | Assumption | Used in | How to test | Decide by |
|----|------------|---------|-------------|-----------|
| A-1 | 70% creator content, 30% brand-owned | `student-strategy.md` | Compare saves and inquiries per ¥1,000 for creator vs brand posts in the creator dashboard | After month 1 |
| A-2 | Budget split KOC ~40%, mid tier ~45%, top tier ~15% (shape from E-7, E-8; the exact split is ours) | `kol-playbook.md` | Cost per save and cost per inquiry by tier (`tools/creator_dashboard.py`) | After month 1 |
| A-3 | Channel split 小红书 40 · WeChat 30 · 抖音 20 · 微博 10 (小红书 first because of E-10, E-11) | `platforms/overview.md` | 10-question survey of UNSW Chinese students: which apps they used to research OSHC and studying in Australia | Before T1 2027 intake |
| A-4 | Pillar mix: 看懂你的保险 35 · 在澳洲看病 30 · 用好 app 和热线 20 · 身心健康 15 (weighted to the gaps in E-5) | `content-playbook.md` | Saves per 1k impressions by pillar (`tools/performance_report.py`) | After month 2 |
| A-5 | Creator score weights 20/18/17/16/15/14, taken from E-14 and E-15 effect sizes (r ÷ sum of r); the studies are not about students or insurance | `kol-playbook.md`, `tools/kol_score.py` | Correlate score with real saves and inquiries once 10+ posts exist | After 10 posts |
| A-6 | Trend score rubric (audience 30, OSHC link 30, freshness 20, safety 20) | `trend-playbook.md`, `tools/trend_score.py` | Compare trend posts' saves with non-trend posts | After 5 trend posts |
| A-7 | Chinese students in Australia search Xiaohongshu for OSHC (no study yet) | All platform choices | Same survey as A-3, plus 小红书 search suggestions for OSHC / 澳洲保险 | Before T1 2027 intake |
| A-8 | Video in Medibank colours with subtitles is enough; no paid ads | `skills/cn-video-editor` | Completion rate and saves per video | After 5 videos |

## How the agent uses this file

* Recommending a strategy, mix, budget or creator: cite the E- row, or name the A- row and
  say it is an assumption.
* A new fact from the web: add an E- row with link, date checked and a reliability note,
  only after opening the page (a search snippet is not a source).
* An A- row that the data has now answered: move the result to E- (source = our own
  dashboard export, with dates) and update the files that use it.
