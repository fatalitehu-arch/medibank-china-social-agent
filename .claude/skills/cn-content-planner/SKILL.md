---
name: cn-content-planner
description: Plan Medibank's China social media content across 小红书, 公众号, 视频号, 抖音 and 微博 - monthly calendars, intake campaigns, channel and owned/creator mix, budgets and KPIs - around the 看懂自己的保险 message. Use for 内容规划/排期/下个月发什么/开学季计划/怎么吸引学生/渠道怎么分配.
---

# cn-content-planner

Paths are relative to the repository root. Read first: `references/student-strategy.md`,
`references/platforms/overview.md`, `references/personas.md`,
`references/content-playbook.md`.

## Steps

1. **Fix the window and audience.** Intake (T1/T2/T3, S1/S2), journey stage
   (offer → visa → pre-departure → arrival → semester), personas. If the user gives only a
   month, infer the stage from the seasonal calendar in `student-strategy.md` and say so.
2. **Set one objective and 2–3 KPIs** from the measurement table in `student-strategy.md`.
   Primary KPI is usually visits to the university Medibank OSHC site / chatbot sessions.
3. **Choose the mix.**
   * Channel split from `platforms/overview.md` (小红书 40 · WeChat 30 · 抖音 20 · 微博 10)
   * Owned vs creator ≈ 30/70; on WeChat owned leads (公众号 is the hub)
   * Pillars per `content-playbook.md`
   Explain any change in one sentence.
4. **Draft the calendar** as rows with the columns of
   `assets/templates/content-calendar.csv`: date, platform, stream (owned/creator), persona,
   pillar, working title, format, creator tier, KPI, risk.
5. **Check and render**: `python tools/calendar_builder.py plan.csv` checks platform split,
   owned/creator split, pillar mix, per-platform cadence and 🟡 items, and prints a
   Markdown calendar.
6. **Budget** (only if asked): creator-tier shares from `references/kol-playbook.md`, per
   platform. Give ranges labelled as assumptions.
7. **Risks**: every 🟡 idea and what Legal must check; any platform still waiting on account
   or ad eligibility (`[VERIFY]` items in the platform files).

## Output

* Plan summary (objective, audience, channel mix, why)
* Calendar table (from `calendar_builder.py`)
* KPIs and how each is measured per platform
* Risks and Legal checks
* Hand-offs: posts → cn-content-writer, creator slots → cn-kol-manager, cross-posting →
  cn-repurpose

## Campaign templates

| Campaign | Window | Shape |
|----------|--------|-------|
| 《拿到 offer 先看这一栏》 | 8 weeks before intake | 公众号 guide wk 1 · 小红书 3 KOC stories/wk · 视频号 explainer for parents · 抖音 1 腰部 vlog at visa week |
| 《落地第一周》 | O-Week ±2 weeks | 抖音 + 小红书 creator "first GP visit" · 公众号 arrival checklist · 微博 #澳洲留学# topic posts |
| 《考试周，照顾好自己》 | Exam weeks | 小红书 wellbeing stories · 公众号 support-line guide · crisis wording from `references/crisis-playbook.md` |
| 《写给家长》 | Any, esp. before departure | 视频号 + 公众号 series for parents on the support line and interpreter service |
