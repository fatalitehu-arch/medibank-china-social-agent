# Creator library (达人库)

The creators Medibank works with on Chinese social media, and how each one is doing.
**The rows here are demo data (示例_ handles, made-up numbers).** Replace them with real
creators and real exports before use.

| File | What it holds | Who updates it |
|------|---------------|----------------|
| `roster.csv` | One row per creator: platform, tier, persona, status (`active` / `briefed` / `paused` / `ended`), contract dates, fee per post, score from `tools/kol_score.py` | Creator manager, when a creator is signed, paused or ends |
| `posts.csv` | One row per published creator post: impressions, likes, comments, saves, shares, inquiries, compliance verdict, cost | Creator manager, weekly, from the marketplace export |

"Inquiries" (咨询) are comments and DMs asking about OSHC (怎么买, 保什么, 怎么报销). Reply
with `assets/templates/comment-replies.md`: point to the university OSHC page, never quote
or sell.

## Selection criteria (选达人标准)

Full rules: `references/kol-playbook.md`. Scoring: `tools/kol_score.py`.

| Criterion | Weight |
|-----------|--------|
| Useful content: share of posts that are guides and checklists | 20 |
| Like our students: lives in Australia, audience mostly students | 18 |
| Shares own life: share of posts about their own experience | 17 |
| Topic fit: share of posts on study, life or health in Australia | 16 |
| Talks with followers: share of comments they reply to | 15 |
| Trustworthy: no follower diversion, past ads disclosed | 14 |

Weights come from published effect sizes (`references/evidence.md` E-14, E-15). Follower
count is not scored; it only sets the tier.

**Hard stops:** sells agency or insurance services; promoted another OSHC insurer in the
last 90 days; history of undisclosed ads; fake-fan flag. Bands: ≥70 go, 50–69 human look,
<50 no. Paid collaborations only through the platform marketplace (蒲公英, 巨量星图, 互选平台, 微任务).

## Dashboard

```bash
python tools/creator_dashboard.py            # Markdown table
python tools/creator_dashboard.py --json     # data for the welcome page
```

It flags active creators with no post in 30 days, contracts ending within 14 days, posts
that needed changes, and briefed creators still waiting for a first post. The welcome page
(`welcome.html`, rebuilt with `python tools/build_welcome.py`) shows the same data.
