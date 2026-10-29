# Medibank China social media agent

This repository is an agent for Medibank's China-facing social media on 小红书, 微信公众号,
微信视频号, 抖音 and 微博: owned content, creator collaborations, compliance checks,
community management and reporting.

For any request about this work, follow `SKILL.md` (the router, also installed as
`.agents/skills/medibank-cn-social/`). It routes to sub-skills in `.agents/skills/cn-*`.
All paths in the skills are relative to this repository root.

The one rule that overrides everything: on Chinese social media, Medibank informs and helps,
it does not sell (no prices, comparisons, purchase links, "DM to buy", or data collection).

## Tools (Python 3.9+, no packages)

| Command | What it does |
|---------|--------------|
| `python tools/compliance_scan.py <file> --platform <id>` | Keyword compliance scan; exit 0 green / 1 amber / 2 red |
| `python tools/note_lint.py <file> --platform <id>` | Length, title, hashtag and style checks |
| `python tools/kol_score.py <csv>` | Score creator candidates |
| `python tools/calendar_builder.py <csv>` | Check and render a content calendar |
| `python tools/performance_report.py <csv>` | Cross-platform performance report |

Platform ids: `xiaohongshu`, `wechat-oa`, `wechat-channels`, `douyin`, `weibo`.

## For maintainers

- Edit skills only at the source (`SKILL.md`, `agents/`, `skills/<name>/`), then run
  `python sync_skills.py` to refresh `.agents/skills/` (Codex) and `.claude/skills/` (Claude Code).
- Run `python -m pytest -q tests` before committing. CI runs the same checks.
- Add new scanner regressions to `evals/scanner_cases.jsonl`.
