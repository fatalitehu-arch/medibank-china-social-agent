# Medibank China social media agent

This repository is an agent that manages Medibank's content creation on Chinese social media
(小红书, 微信公众号, 微信视频号, 抖音, 微博): what to post, which trends to ride and which creators
to work with, with compliance checks, community management and reporting.

**First session:** if the file `.welcome_shown` does not exist in the repository root, run
`python3 social_agent/first_run.py` before anything else and tell the user in one line that
`welcome.html` shows what the agent contains (skills, knowledge base, creator library).

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
| `python tools/trend_score.py <csv>` | Score trends: use now / adapt / watch / avoid |
| `python tools/creator_library.py` | Scouted creator library (`creators/scouted/`): summary, `--pages` / `--serve` (method + library pages for the side panel), `--open` (external browser), `--status Shortlist`, `--check`, `--html`, `--next-id xiaohongshu` |
| `python tools/creator_dashboard.py` | Signed-creator dashboard from `creators/roster.csv` and `posts.csv` |
| `python tools/make_post.py <spec.json>` | Finished post: text, image cards (needs Pillow) and compliance report in `outputs/posts/` |
| `python tools/video_edit.py <plan.json>` | Edited vertical video in Medibank colours (needs ffmpeg); `--dry-run`, `--probe FILE` |
| `python tools/motion_video.py <board.json>` | Animated explainer video, no footage needed (Pillow + ffmpeg); `--check`, `--frames`, `--pack` (剪映 asset pack) |
| `python tools/evidence_check.py` | Every `[E-n]`/`[A-n]` citation points to a row in `references/evidence.md` |
| `python tools/build_welcome.py` | Rebuild `welcome.html` from the repository |

Platform ids: `xiaohongshu`, `wechat-oa`, `wechat-channels`, `douyin`, `weibo`.

## For maintainers

- Edit skills only at the source (`SKILL.md`, `agents/`, `skills/<name>/`), then run
  `python sync_skills.py` to refresh `.agents/skills/` (Codex) and `.claude/skills/` (Claude Code).
- Run `python -m pytest -q tests` before committing. CI runs the same checks.
- Add new scanner regressions to `evals/scanner_cases.jsonl`.
- After changing skills, `references/`, `creators/` or the trend radar, run
  `python tools/build_welcome.py` (CI checks `welcome.html` is up to date).
