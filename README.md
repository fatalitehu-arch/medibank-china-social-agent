# Medibank China Social Media Agent

**An AI agent that helps Medibank manage content creation on Chinese social media
(小红书, 微信公众号, 微信视频号, 抖音, 微博): what to post, which trends to ride, and which
creators (网红/博主) to work with, with a compliance check on every post.**

## 👉 Install: copy this, paste it into Claude Code

```text
Install the Medibank China Social Agent and start using it right away:
1. Run in the shell: claude plugin marketplace add fatalitehu-arch/medibank-china-social-agent
2. Run in the shell: claude plugin install medibank-cn-social@medibank-china-social
3. Find the installed folder (~/.claude/plugins/cache/medibank-china-social/medibank-cn-social/<version>/)
   and run: python3 social_agent/first_run.py --force   (this opens the welcome page in my browser)
4. Read SKILL.md in that folder and act as this agent for the rest of this conversation,
   using the folder's skills/, references/, tools/ and creators/. Then ask me what I want to do.
```

Click the copy button on the box above, paste it into a **Claude Code** conversation (the Code
tab in the Claude desktop app, or `claude` in a terminal), and press Enter. Claude installs
the agent, opens the welcome page and starts working as the agent in the same conversation,
with no restart. In later sessions the nine skills load on their own.

<details>
<summary>Other ways to install, and why "download" gives you a ZIP</summary>

* Asking Claude to "download" the repo only gives you a ZIP file, and a normal Claude chat
  can't install plugins. Use Claude Code as above.
* Type it yourself in a Claude Code session: `/plugin marketplace add fatalitehu-arch/medibank-china-social-agent`,
  then `/plugin install medibank-cn-social@medibank-china-social` and pick a scope.
  (Claude Code v2.1.275+ can do both at once: `/plugin install medibank-cn-social --marketplace fatalitehu-arch/medibank-china-social-agent`.
  The `--marketplace` flag only works inside a session, not with `claude plugin install` in the shell.)
* New skills load in the next session, or straight away after `/reload-plugins`.
* Check it worked: ask "怎么找博主？" or "有推荐的博主吗？". The agent should explain the tested
  search method and show the creator library (28 Xiaohongshu creators).
* Cowork in the desktop app: in Customize, find the plugins section, choose "Add marketplace",
  enter `fatalitehu-arch/medibank-china-social-agent`, then install `medibank-cn-social`.
  The menu names may differ between app versions.
* Update later with `/plugin marketplace update medibank-china-social`.

</details>

Works in **Claude** (Claude.ai Projects, Claude Code) and **OpenAI Codex**, or from the
command line through the Claude API. Built by UNSW CDEV3000 MB Group 6 (T3 2026) as the
project deliverable for Medibank.

> ⚠️ The compliance rules in this repo are a student research summary, not legal advice.
> Medibank Legal & Compliance and PRC counsel should review `references/compliance.md`
> before the agent is used for real campaigns. Anything marked `[VERIFY]` needs checking.

**Start here: open [`welcome.html`](https://htmlpreview.github.io/?https://github.com/fatalitehu-arch/medibank-china-social-agent/blob/main/welcome.html)** in a browser for a visual overview of the skills,
knowledge base and creator library (it also opens automatically the first time you use the
agent in Claude Code or from the command line). 中文使用说明：[使用说明.md](使用说明.md)

---

## The problem it solves

Most Chinese international students let an education agent (留学中介) handle everything,
including their OSHC. The agent picks the insurer and arranges the cover, so Medibank never
has direct contact with the student, and the student never thinks about insurance until
they need it in Australia.

Before they leave, these students get their information from 小红书, 公众号, 抖音, 视频号
and 微博. That is where Medibank can meet them first. But these are mainland platforms and
Medibank has no insurance licence in China, so it can build awareness there, never sell.
The agent is built around one rule:

> **On Chinese platforms, Medibank informs and helps. It does not sell.**

## What it aims for

**The end goal:** Chinese students realise student insurance matters, and take part
themselves in choosing their insurer, comparing each company's price and coverage,
instead of leaving the choice to their education agent. Students can choose their own
OSHC insurer (Department of Health OSHC fact sheet; `references/compliance.md` AU-5).

The agent's goals on social media, in order:

1. **Know Medibank**: students meet Medibank on the platforms they already use, before departure.
2. **Care about OSHC**: they realise student insurance affects them (seeing a GP, emergencies, claims).
3. **Choose for yourself**: they want to join the insurer choice and compare options themselves.

Social content builds the awareness; it never compares prices or insurers itself (that
would be selling in China, CN-1/CN-2). Students do the comparing themselves, off the
platform. They follow the link in their **UNSW offer letter** to the UNSW Medibank OSHC
site, where an AI chatbot (a separate project) helps them understand Medibank OSHC.

![Student funnel](assets/images/funnel.svg)

```
Post or video (creator 70% / owned 30%) on 小红书 · 公众号 · 视频号 · 抖音 · 微博
  →  "insurance matters, I should choose and check it myself"
  →  the OSHC link in their UNSW offer letter  →  UNSW Medibank OSHC site
  →  chatbot on that site helps them understand Medibank OSHC
  →  the student compares insurers themselves and decides
```

Content never contains prices, links, QR codes or "DM me to buy". It names the next step
in words.

## What the agent does

| Skill | Ask it… | You get |
|-------|---------|---------|
| `medibank-cn-social` (router) | Anything vague: "下个月社媒怎么做" | Picks the platform and the sub-skill, runs multi-step work |
| `cn-trend-scout` | "最近有什么热点可以蹭？" / "心动的offer 8 能不能借势？" | Trend radar: what's hot on each platform (dated sources), score and verdict (use now / adapt / watch / avoid), post angles and creator types, what to avoid |
| `cn-content-writer` | "写一篇小红书：第一次在悉尼看 GP" / "写一篇公众号长文" / "写一个抖音 60 秒脚本" | **A finished post**: final text, titles, hashtags and image cards (PNG, Medibank colours) in `outputs/posts/`, with the compliance verdict; also articles and video scripts |
| `cn-video-editor` | "把这三段素材剪成 45 秒抖音竖屏，加字幕" | **An edited vertical video** from your footage: trimmed, joined, subtitled, Medibank colour tone, title and end cards, music ducked (needs ffmpeg) |
| `cn-repurpose` | "把这篇公众号改成另外四个平台" | One idea, five native versions, each scanned at its own platform level |
| `cn-content-planner` | "2027 T1 开学季 4 周计划" | Cross-platform calendar (platform, owned/creator, persona, pillar, format, KPI, risk) checked by `calendar_builder.py` |
| `cn-kol-manager` | "找 UNSW 新生相关的博主" / "给这批博主打分" / "写星图 brief" / "审这篇博主稿" | Search plan per marketplace, scored shortlist, vetting, brief, draft review with change requests |
| `cn-compliance-review` | Paste any draft | 🟢 / 🟡 / 🔴 verdict, each problem line with rule ID and fixed wording |
| `cn-community-manager` | "这些评论怎么回" / "有人在微博骂我们" | Replies by platform tone, escalation, crisis level (L1–L3), live-stream Q&A sheet |
| `cn-performance-review` | "这是上个月的数据导出" | Cross-platform report, what worked and why, next month's changes |

The two core jobs are **what to post** (trend-scout → planner → writer → repurpose) and
**who to work with** (kol-manager). Every publishable output passes two checks: a deterministic keyword scanner
(`tools/compliance_scan.py`, 22 rule groups mapped to PRC, platform and Australian rules,
with per-platform levels) and the model reading the draft against the full rulebook for
meaning. A human (Medibank Legal) signs off before anything goes live.

### Built on evidence

Every strategy choice (which platform, which creators, what format, how much budget) points
to a row in [`references/evidence.md`](references/evidence.md): **13 published sources**
(`E-` rows: link, date checked, reliability) and **8 working assumptions** (`A-` rows: how
and when the team will test each one). Highlights:

| Choice | Evidence |
|--------|----------|
| Reach students before the agent decides | 73% of Chinese students in Australia enrolled through an education agent (2018) [E-1] |
| Student creators carry the message | On Xiaohongshu 46.6% trust regular users vs 22.9% brand accounts [E-3]; international students rate peers above any university service [E-4] |
| Mostly small and mid-tier creators | Engagement peaks at a middle follower count, then falls (1,700+ influencers) [E-7] |
| First-person experience posts, facts from the official page | People judge experiences by peers and insurance by experts [E-9]; ~70% of Xiaohongshu users search [E-10] |
| Lead with "know your cover" | Only 39% of struggling students know what OSHC excludes [E-5] |

The agent cites these rows when it recommends anything, and says plainly when something is
an assumption. `python tools/evidence_check.py` fails if a cited row is missing.

### Finished posts and videos

```bash
pip install Pillow                                    # once, for image cards
python tools/make_post.py examples/post_spec.json     # → outputs/posts/<title>/ post.md + 01–05.png + compliance.txt
python tools/video_edit.py my_plan.json               # → outputs/videos/my_plan.mp4 (needs ffmpeg)
```

The agent writes the spec or edit plan for you; these commands are what it runs. Colours
live in `assets/brand/theme.json`: Medibank red `#CB2D2E` with white and black, sampled from
medibank.com.au (swap in official values from Medibank's brand team if they differ).

### How we find creators, and the creator library (博主库)

Ask the agent "怎么找博主？" or "有推荐的博主吗？". It explains the field-tested method (a real
person logs in to a Xiaohongshu account by QR code, then the agent searches lifestyle keywords,
reads profiles and screens out fake or ad accounts) and shows the creator library.

| | Text | Visual |
|---|---|---|
| Method (8 steps) | [`references/creator-finding.md`](references/creator-finding.md) | [Open the web page](https://htmlpreview.github.io/?https://github.com/fatalitehu-arch/medibank-china-social-agent/blob/main/assets/creator-finding/process.html) (`assets/creator-finding/process.html`) |
| Creator library (28 Xiaohongshu creators, IDs, scores) | [`creators/scouted/README.md`](creators/scouted/README.md), [`xiaohongshu.csv`](creators/scouted/xiaohongshu.csv) | [Open the web page](https://htmlpreview.github.io/?https://github.com/fatalitehu-arch/medibank-china-social-agent/blob/main/creators/scouted/library.html) (`creators/scouted/library.html`) |

GitHub shows `.html` files as code, so the links above open them as web pages. Previews:

| Method | Creator library |
|---|---|
| ![How the agent finds creators](assets/creator-finding/process-preview.png) | ![Creator library](creators/scouted/library-preview.png) |

Xiaohongshu is the main platform. New creators are added as rows and checked with
`python tools/creator_library.py --check --html`.

### Signed-creator roster (达人库)

`creators/roster.csv` lists the creators Medibank works with (platform, tier, status,
contract, score) and `creators/posts.csv` their results (likes, comments, saves, shares,
inquiries, compliance verdict, cost). `python tools/creator_dashboard.py` turns them into a
dashboard with follow-ups; the welcome page shows the same view. Selection criteria and hard
stops: `creators/README.md`. **The rows are demo data until the team adds real creators.**

### Platforms

| Platform | id | Role in the mix | Creator marketplace |
|----------|----|-----------------|---------------------|
| 小红书 | `xiaohongshu` | ~40%: search and saves, "how to" notes | 蒲公英 |
| 微信公众号 | `wechat-oa` | ~30% with 视频号: long guides, parents | 互选平台 |
| 微信视频号 | `wechat-channels` | (WeChat share) short video, live Q&A | 互选平台 [VERIFY] |
| 抖音 | `douyin` | ~20%: short video, reach | 巨量星图 |
| 微博 | `weibo` | ~10%: news hooks, intake moments, crisis watch | 微任务 [VERIFY] |

Details per platform are in `references/platforms/`.

---

## How Medibank uses it

All entry points read the same files. Pick the one that matches the team.

### Option 1: Claude.ai Project (no code, for the social team)

1. In Claude.ai, create a **Project** called "Medibank 中国社媒".
2. Upload `SKILL.md`, every `skills/*/SKILL.md`, and everything in `references/`
   (including `references/platforms/`) and `assets/templates/` to the project knowledge.
3. Paste this into the project instructions:
   > Follow SKILL.md. Use the sub-skill that fits each request. Reply in Chinese for
   > content and in English for notes to the Medibank team. Always state the platform.
   > Never write prices, links, QR codes or purchase calls to action.
4. Ask in plain Chinese or English: "写一篇小红书笔记：落地第一周怎么激活 OSHC".

Claude.ai can't run the Python tools, so the model applies the rules by hand. Run
`tools/compliance_scan.py` (Option 3) on anything high-reach before Legal review.

### Option 2: Claude Code or OpenAI Codex (for the digital team)

In Claude Code the quickest route is the plugin install at the top of this README. To work
on the agent itself (or to use Codex), clone it:

```bash
git clone https://github.com/fatalitehu-arch/medibank-china-social-agent.git
cd medibank-china-social-agent
```

* **Claude Code**: run `claude` in the folder. Skills load from `.claude/skills/`;
  `CLAUDE.md` gives the project rules. Try `/medibank-cn-social` or just ask.
* **Codex**: run `codex` in the folder. Skills load from `.agents/skills/` with display
  names from each `agents/openai.yaml`; `AGENTS.md` gives the project rules. Try
  `$medibank-cn-social` or just ask.

In both, the agent runs the tools in `tools/` itself (scanner, linter, scorer, calendar,
report). Skill copies are generated: after editing `SKILL.md` or `skills/`, run
`python3 sync_skills.py` (CI fails if the copies drift).

### Option 3: Command line (Claude API)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # from console.anthropic.com

python -m social_agent write    "offer letter 里 OSHC 那一栏怎么看" --platform xiaohongshu
python -m social_agent repurpose examples/drafts/good_wechat-oa.txt
python -m social_agent plan     "2027 年 T1 开学季，4 周"
python -m social_agent brief    "UNSW 新生，腰部博主，短视频" --platform douyin
python -m social_agent review   creator_draft.txt --platform xiaohongshu
python -m social_agent check    my_draft.txt --platform wechat-oa
python -m social_agent reply    comments.txt --platform weibo
python -m social_agent trends   "本周留学生相关热点"          # searches the web
python -m social_agent chat
```

Offline, no API key and no dependencies (Python 3.9+):

```bash
python -m social_agent scan     examples/drafts/bad_douyin.txt --platform douyin
python -m social_agent lint     examples/drafts/good_weibo.txt --platform weibo
python -m social_agent kol      examples/kol_candidates.csv
python -m social_agent calendar examples/plan_t1_2027.csv
python -m social_agent report   examples/metrics_sample.csv
python -m social_agent trendscore examples/trends_sample.csv --today 2026-11-05
python -m social_agent creators
python -m social_agent welcome
```

`scan` exits 0 for 🟢, 1 for 🟡 and 2 for 🔴, so it can gate a publishing script.

---

## Day-to-day workflow

See [docs/workflow.md](docs/workflow.md) for roles, the weekly rhythm and the pre-publish
checklist. In short:

1. **Trends** every Monday with `cn-trend-scout` (dated radar, verdicts, angles).
2. **Plan** monthly with `cn-content-planner` (pillar mix: 看懂你的保险 35%, 在澳洲看病 30%,
   用好 app 和热线 20%, 身心健康 15%).
3. **Write** owned content with `cn-content-writer`, then `cn-repurpose` for the other
   platforms.
4. **Creators**: export candidates from each marketplace → `kol_score.py` → brief from
   `assets/templates/creator-brief.md` → review drafts with `cn-kol-manager`.
5. **Gate**: `cn-compliance-review` + Legal sign-off (`assets/templates/legal-signoff.md`).
6. **Community**: `cn-community-manager` with `assets/templates/comment-replies.md`.
7. **Measure**: export data → `performance_report.py` → `cn-performance-review` →
   `assets/templates/monthly-report.md`.

## What it will not do

* Quote prices, compare insurers, offer discounts or say "buy", "DM me" or "link in bio".
* Put links, QR codes, WeChat IDs or phone numbers in content (except WeChat-internal
  pointers to the 公众号, where allowed per platform).
* Claim to be the "best", "No. 1" or "largest" in China, or promise visa outcomes.
* Invent creators, follower counts, metrics or product facts. Facts come only from
  `references/brand-facts.md`; anything missing is marked `【待确认】`.
* Use a real student's offer letter, policy or personal data.

## Repository map

```
SKILL.md                 Router skill (medibank-cn-social)
.claude-plugin/          Claude Code plugin manifest + marketplace (one-step install)
hooks/hooks.json         Plugin hook: opens welcome.html on the first session
agents/openai.yaml       Codex display metadata for the router
skills/cn-*/             Nine sub-skills (SKILL.md + agents/openai.yaml each)
.claude/skills/          Generated copies for Claude Code   (sync_skills.py)
.agents/skills/          Generated copies for Codex         (sync_skills.py)
references/              Shared knowledge: evidence register, compliance, brand facts, strategy, personas,
                         content and creator playbooks, crisis, contracts, glossary
references/platforms/    One file per platform + overview (channel mix)
tools/                   compliance_scan.py + rules.json, note_lint.py, kol_score.py,
                         calendar_builder.py, performance_report.py, trend_score.py,
                         creator_dashboard.py, evidence_check.py, build_welcome.py,
                         make_post.py (finished posts + image cards), video_edit.py (ffmpeg)
social_agent/            CLI runner (Claude API + offline tool wrappers), first-run welcome
creators/                scouted/ (real creator library, Xiaohongshu first), roster.csv, posts.csv (demo data), README
welcome.html             Visual overview, generated by tools/build_welcome.py
assets/templates/        Creator brief, onboarding, calendar, replies, monthly report,
                         Legal sign-off
assets/images/           Icon, funnel diagram, mock offer letter (for content mock-ups)
assets/brand/theme.json  Medibank colours and fonts for cards, videos and the welcome page
outputs/                 Finished posts and videos (git-ignored)
examples/                Sample drafts (good/bad per platform), CSVs, sample outputs
evals/                   Scanner regression cases + model behaviour scenarios
tests/                   pytest suite (scanner, tools, skill integrity)
docs/workflow.md         Team roles and weekly rhythm
DESIGN.md                Why it is built this way
AGENTS.md / CLAUDE.md    Project rules for Codex / Claude Code
```

## Keeping it up to date

| When | Update |
|------|--------|
| Each intake | `references/brand-facts.md` (product features, URLs, support numbers) |
| A post is throttled, removed or flagged | Add the trigger words to `tools/rules.json` and a case to `evals/scanner_cases.jsonl` |
| Rules or platform policies change | `references/compliance.md`, `references/platforms/*.md` |
| Each month | Tune `kol_score.py` baselines with real data |
| Weekly | Update `creators/roster.csv` and `creators/posts.csv` from the marketplace exports |
| A test result answers an assumption | Move the `A-` row to `E-` in `references/evidence.md` with your own data and dates |
| After any change above | `python tools/build_welcome.py` so the welcome page matches |

Then run the checks:

```bash
pip install -r requirements-dev.txt
python3 sync_skills.py
python -m pytest -q tests
```

## Credits

Structure and some style checks are adapted from open-source agent skills; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Released under the [MIT License](LICENSE).
