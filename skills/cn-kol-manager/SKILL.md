---
name: cn-kol-manager
description: Manage Medibank's creator (博主/KOL/KOC) collaborations on 小红书 (蒲公英), 抖音 (星图), 微信公众号/视频号 (互选平台) and 微博 - search plans, scoring a candidate CSV, vetting, briefs, onboarding, reviewing creator drafts and wrap-ups. Use for 找博主/打分/这个博主行不行/写brief/审博主稿/博主复盘.
---

# cn-kol-manager

Paths are relative to the agent's root folder (`${CLAUDE_PLUGIN_ROOT}` when installed as a plugin, otherwise the repository root). Read first: `references/kol-playbook.md`,
`references/creator-contract-terms.md`, `references/student-strategy.md`, and the platform
file for the platform in question.

## Tasks

### 1. Search plan ("找博主")
You cannot see live platform data. Never name real creators unless the user supplied them.
Output per platform: target tiers and counts, marketplace filters (蒲公英 / 星图 / 互选 /
微任务), search keywords, data-tool checks, hard stops, and the CSV columns to export
(`examples/kol_candidates.csv`).

### 2. Score a list
Run `python tools/kol_score.py candidates.csv --out scored.csv`. The CSV has a `platform`
column; engagement is judged against that platform's baseline. Summarise: top picks per
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

### 7. Creator library (达人库)
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
