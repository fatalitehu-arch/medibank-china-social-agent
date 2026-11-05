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
| Audience fit: lives in Australia, audience mostly students 18–30 | 30 |
| Engagement quality: (likes + 2 × saves + comments) ÷ followers | 25 |
| Topic relevance: share of posts on study and life in Australia | 20 |
| Trust & safety: sponsored posts properly disclosed | 15 |
| Cost efficiency: price vs tier median | 10 |

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
