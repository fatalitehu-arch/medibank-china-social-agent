---
name: cn-performance-review
description: Turn exported data from 小红书, 公众号, 视频号, 抖音 and 微博 (and their creator marketplaces) into a weekly or monthly cross-platform performance report for Medibank with insights and next actions. Use for 数据复盘/月报/周报/哪个平台效果好/博主效果怎么样.
---

# cn-performance-review

Paths are relative to the repository root. Read: `references/student-strategy.md`
(measurement table), `references/platforms/overview.md`, `assets/templates/monthly-report.md`.

## Steps

1. **Get the data.** One CSV, one row per post, columns as in `examples/metrics_sample.csv`
   (includes `platform`). Each platform exports differently; map its fields to these
   columns (e.g. 公众号 "阅读" → reads, "在看/分享" → shares; 抖音 "播放" → impressions).
   Optional: site/chatbot visits from Medibank web analytics.
2. **Run** `python tools/performance_report.py metrics.csv --out report.md`: totals, rates
   by platform, owned vs creator, pillar, format, top/bottom posts, cost per save.
3. **Compare platforms fairly.** Rates differ by platform (a 公众号 read is not a 抖音 view);
   compare each platform to its own last month first, then across platforms on the funnel
   KPI (site/chatbot visits).
4. **Explain** the top 3 and bottom 3 posts in one line each (hook, persona, timing, format,
   platform fit). Label guesses as guesses.
5. **Connect to the funnel.** Did spikes line up with site or chatbot visits? If no analytics
   were given, say this is the missing link.
6. **Recommend** 3–5 specific next actions (repeat, stop, test), including any change to the
   channel split.
7. Fill `assets/templates/monthly-report.md`.

Never invent numbers or benchmarks.
