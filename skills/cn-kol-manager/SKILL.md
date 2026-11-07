---
name: cn-kol-manager
description: Find and manage Medibank's creators (博主/KOL/KOC): the tested Xiaohongshu search method and the scouted creator library, plus collaborations on 小红书 (蒲公英), 抖音 (星图), 微信公众号/视频号 (互选平台) and 微博 - search plans, scoring a candidate CSV, vetting, briefs, onboarding, reviewing creator drafts and wrap-ups. Use for how to find the right creators / who to work with / 怎么找博主/有推荐的博主吗/博主库/找博主/打分/这个博主行不行/写brief/审博主稿/博主复盘.
---

# cn-kol-manager

Paths are relative to the agent's root folder (`${CLAUDE_PLUGIN_ROOT}` when installed as a plugin, otherwise the repository root). Read first: `references/creator-finding.md`, `creators/scouted/README.md`, `references/kol-playbook.md`,
`references/creator-contract-terms.md`, `references/student-strategy.md`, and the platform
file for the platform in question.

## Tasks

### 1. "How do we find creators?" / "Any creators you recommend?" (怎么找博主 / 有推荐的博主吗)
Any question about finding, choosing or recommending creators ("how can I find the right
creators", "who should we work with", "找博主", "推荐博主", "博主库") starts here.

**First, before writing anything, open the two visual pages:** run
`python3 tools/creator_library.py --open`. It opens the method page
(`assets/creator-finding/process.html`) and the creator library
(`creators/scouted/library.html`) in the browser. If no browser opens, give the user the two
paths it prints. Then answer in this order, short, in the user's language, pointing at the pages
instead of repeating them:

1. **The method.** Say it has been field-tested and give the 8 steps from
   `references/creator-finding.md`. Lead with step 1: **a real person logs in by QR code on a
   real Xiaohongshu account** (search does not work without it; the agent never types a
   password). Point to the visual: `assets/creator-finding/process.html` (8-step flow with
   screenshots), already open.
2. **The knowledge base.** Every creator found this way is stored in the creator library,
   `creators/scouted/` (one CSV per platform, rules in `creators/scouted/README.md`). Say
   **Xiaohongshu is the main platform**, because it is where Chinese students search and trust
   peers most (`references/student-strategy.md`; 小红书 40% of the channel mix). Run
   `python tools/creator_library.py` and say how many creators are built in, by status.
   The library page is already open (platform → status → shortlist with scores and IDs).
3. **The recommendations.** Show the Shortlist (`python tools/creator_library.py --status
   Shortlist`): nickname, Library ID, Xiaohongshu ID, followers and tier, city, score, one line
   on why. Add "follower counts were recorded at scan time; check again before contacting".
4. **Adding more.** The library grows: new scans add rows (task 1b). Offer to run a new
   search if the user can log in on a browser you can use.
5. **Recommend 蒲公英.** End by recommending Medibank open a 蒲公英 brand account: it shows each
   creator's back-end data (audience, reach, engagement, price) that a profile scan cannot,
   and it is the only allowed route for paid collaborations (MCN agencies book through it
   too). Details: "Next step" in `references/creator-finding.md`.

Never invent creators. Name only creators in `creators/scouted/` or supplied by the user.

### 1b. Run a new search and add creators to the library
Only with a browser the user is logged in to (step 1 needs a person). Follow
`references/creator-finding.md` exactly: lifestyle keywords (not insurance or doctor words),
human pace, view only (no likes, follows, comments or DMs, no bulk scraping). For each fit:
get the next ID (`python tools/creator_library.py --next-id xiaohongshu`), add a row to
`creators/scouted/xiaohongshu.csv` with every column, score the five dimensions 1-5 (total ×4),
set the status, then run `python tools/creator_library.py --check --html`. Other platforms
get their own file (`douyin.csv`, `weibo.csv`, `wechat-channels.csv`) with the same columns.

### 1c. Marketplace search plan (paid bookings)
For a paid campaign through the platform marketplaces: per platform, target tiers and counts,
marketplace filters (蒲公英 / 星图 / 互选 / 微任务), search keywords, data-tool checks, hard
stops, and the CSV columns to export (`examples/kol_candidates.csv`). The scouted library is
the shortlist to look up there first.

### 2. Score a list
Run `python tools/kol_score.py candidates.csv --out scored.csv`. Six criteria, each 0–1,
weighted by published effect sizes (`references/kol-playbook.md` §3). Follower count sets the
tier only. Summarise: top picks per
platform and tier, every hard stop and why, and the "maybe" band for a human look. Propose a
shortlist matching the tier and channel mix.

### 3. Vet one creator
Walk the vetting checklist in `kol-playbook.md` §4. Verdict: go / maybe / no, with the
missing information listed.

### 4. Brief
Fill `assets/templates/creator-brief.md` for the platform (format, length, tag, next-step
wording). Key messages are facts copied from `references/brand-facts.md` with their
qualifiers. The creator tells the story in their own words; never script a fake experience.
Attach `assets/templates/creator-onboarding.md`.

### 5. Review a creator draft
1. Run cn-compliance-review on the draft with the right `--platform`.
2. Add the creator checks from `kol-playbook.md` §6 (sponsor tag, genuine experience, not
   scripted, no diversion, comment plan). For video, review the script **and** the cut
   (on-screen text, captions, spoken claims).
3. Return: verdict, numbered change requests the creator can act on, and a polite message to
   the creator in Chinese.

### 6. Wrap-up
From exported data, run `python tools/performance_report.py metrics.csv` and summarise per
creator: reach, saves/shares, comments with real questions, cost per save, rebook yes/no.

### 7. Signed-creator roster and dashboard (达人库)
The creators Medibank works with live in `creators/roster.csv` (status, contract, fee,
score) and their published posts in `creators/posts.csv` (likes, comments, saves, shares,
inquiries, verdict). Keep both up to date when a creator is signed, paused or ends, and
weekly from the marketplace export. `python tools/creator_dashboard.py` shows results per
creator and what needs follow-up (no post in 30 days, contract ending, a post that needed
changes, first post overdue). After editing, run `python tools/build_welcome.py` so the
welcome page shows the same data. Details: `creators/README.md`.

## Rules that never bend

* Paid = the platform's marketplace + its tag. No private deals, no "无广" on paid content.
* No affiliate or per-sale commission: paying per policy sold would make the creator an
  unlicensed insurance intermediary in China (CN-1/CN-2).
* No creator who sells agency or insurance services; no competitor OSHC deal in the last
  90 days.
* Creators must not collect personal data or "help buy" in comments, DMs or live chat.
