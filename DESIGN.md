# Design

## Goal

Give Medibank's international student team one agent that runs its China-facing social
media on five platforms (小红书, 微信公众号, 微信视频号, 抖音, 微博), covering both owned
content and creator collaborations, without ever crossing the line into selling insurance
in mainland China.

## Constraints that shaped the design

| Constraint | Design response |
|------------|-----------------|
| Medibank has no insurance licence in China; selling, quoting or comparing there is high risk (CN-1, CN-2) | One overriding rule at the top of every skill; a compliance gate every output must pass |
| Each platform has its own formats, marketplace and diversion rules | One reference file per platform; `--platform` on every tool |
| The partner's team uses different tools (Claude.ai, Claude Code, Codex, or none) | Plain-Markdown skills in the open Agent Skills format + Python tools with no dependencies + an optional API runner |
| The agent can't see live platform data | Tools work on CSV exports the team provides; skills forbid inventing creators or numbers |
| Rules and product facts change | Facts in one file (`brand-facts.md`), rules in one file (`compliance.md`) and one editable list (`tools/rules.json`), with `[VERIFY]` markers |
| A keyword list can't judge meaning | Two gates: the scanner for words, the model reading against the full rulebook for meaning, then human Legal sign-off |

## Architecture

```
                 ┌──────────────────────────────────────────────┐
 Entry points    │ Claude.ai Project │ Claude Code │ Codex │ CLI (Claude API) │
                 └──────────────────────────────────────────────┘
                                     │
 Router          SKILL.md  (medibank-cn-social: core rule, platform choice, routing)
                                     │
 Sub-skills      cn-content-writer   cn-repurpose   cn-content-planner   cn-kol-manager
                 cn-community-manager   cn-performance-review
                                     │
                         every publishable output
                                     ▼
 Gate            cn-compliance-review ── tools/compliance_scan.py (words) + model (meaning)
                                     │
 Human           Medibank Legal & Compliance sign-off (assets/templates/legal-signoff.md)
                                     │
 Publish         owned account  or  platform marketplace (蒲公英 · 星图 · 互选 · 微任务)

 Shared knowledge  references/ (+ platforms/)     Deterministic tools  tools/
 Templates         assets/templates/              Examples & evals     examples/, evals/
```

### Why a router plus sub-skills

Each sub-skill loads only the references it needs, so the model's context stays focused,
and descriptions let Claude Code and Codex pick the right sub-skill directly when the
request is specific ("给这批博主打分"). The router handles vague requests and multi-step
work.

### Why skill files point to repo-root paths

Shared knowledge lives in one place (`references/`, `tools/`, `assets/`). Skill folders
stay tiny, so the copies in `.claude/skills/` and `.agents/skills/` (one per tool) are
cheap to keep in sync with `sync_skills.py`, and a CI step fails if they drift.

### Why the scanner is deterministic

Compliance must be repeatable and explainable to Legal: the same draft always gets the same
hits, each tied to a rule ID in `compliance.md`. Rules are data (`rules.json`) so Medibank
can add words without code. Platform differences (e.g. naming the 公众号 is fine on 视频号
but diversion on 小红书) are per-rule `platform_levels`. The model then catches what words
can't: implied comparisons, fake neutrality, unqualified claims.

## Data flow for a creator campaign

1. Planner builds the calendar (`calendar_builder.py` checks mix and cadence).
2. Team exports candidates from each marketplace → `kol_score.py` ranks them; hard stops
   remove agency/insurance sellers and recent competitor partners.
3. KOL manager writes the brief from `assets/templates/creator-brief.md` with facts copied
   from `brand-facts.md`.
4. Creator drafts → compliance review with the right `--platform` → change requests.
5. Legal sign-off → publish through the marketplace.
6. Export metrics → `performance_report.py` → monthly report → next plan.

## Testing

* `evals/scanner_cases.jsonl`: regression cases for the scanner (text, platform, expected
  verdict, rules that must fire), run by `tests/test_compliance_scan.py`.
* `tests/test_tools.py`: scorer, linter, calendar and report behaviour.
* `tests/test_skills.py`: frontmatter, every referenced path exists, tool copies in sync.
* `evals/evals.md`: 12 behaviour scenarios for the model, scored by hand.
* CI runs all of the above on Python 3.9 and 3.12.

## Known limits

* Rules marked `[VERIFY]` (account eligibility for an overseas insurer on each platform,
  current marketplace names, WeChat menu links) need confirmation by Medibank and PRC counsel.
* Platform algorithms are not public; `references/platforms/` describes commonly reported
  behaviour.
* The scanner's keyword list will miss new slang; add hits to `rules.json` when a post is
  throttled or rejected.
* Engagement baselines in `kol_score.py` are starting assumptions, to be tuned with data.
