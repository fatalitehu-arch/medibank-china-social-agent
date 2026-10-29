# Medibank 小红书 agent

This repository is an agent for Medibank's China-facing Xiaohongshu (小红书) work:
brand notes, creator (博主) collaborations, and compliance checks.

When the user asks for anything about 小红书 content, creators, content plans or
compliance, follow the skill in `.agents/skills/medibank-xhs/SKILL.md` and read the
reference files it names. The one rule that overrides everything: on 小红书, Medibank
informs and helps, it does not sell (no prices, comparisons, links, "DM to buy").

Tools you can run (Python 3.9+, no packages):

- `python .agents/skills/medibank-xhs/scripts/compliance_scan.py <file>` keyword compliance scan (exit 0/1/2)
- `python .agents/skills/medibank-xhs/scripts/kol_score.py <csv>` creator scoring

## For maintainers

- Edit the skill only in `skills/medibank-xhs/`, then run `python sync_skills.py`
  to refresh `.agents/skills/` (Codex) and `.claude/skills/` (Claude Code).
- Run `python -m pytest tests` before committing.
