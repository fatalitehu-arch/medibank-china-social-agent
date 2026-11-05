# Medibank China social media agent

For any request about Medibank's 小红书, 公众号, 视频号, 抖音 or 微博 work, use the
`medibank-cn-social` skill (`.claude/skills/medibank-cn-social/SKILL.md`), which routes to the
`cn-*` sub-skills. Paths inside the skills are relative to this repository root.

On the first session a SessionStart hook (`.claude/settings.json`) opens `welcome.html`, the
page that shows what the agent contains.

Maintainers: see `AGENTS.md` (edit sources, run `python sync_skills.py`, then
`python -m pytest -q tests`).
