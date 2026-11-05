---
name: cn-trend-scout
description: Find what is trending right now on Chinese social media (小红书, 抖音, 微博, 公众号, 视频号) - variety shows, memes, dance challenges, hashtags, events - judge which ones Medibank can safely ride, and turn them into post angles and creator ideas. Use for 热点/热梗/最近火什么/蹭热点/追热点/trend/综艺/挑战/话题.
---

# cn-trend-scout

Paths are relative to the agent's root folder (`${CLAUDE_PLUGIN_ROOT}` when installed as a plugin, otherwise the repository root). Read first: `references/trend-playbook.md`
(where to look, the scoring rubric, angle patterns, the never-touch list), then
`references/trend-radar.md` (the last dated snapshot), `references/personas.md` and
`references/compliance.md` section 6 (riding trends).

Trends move in days. Anything you say about "now" must come from a source you checked in
this session, with its date. If you can't search the web, say so, work only from what the
user pastes and from `trend-radar.md`, and give the snapshot's date.

## Steps

1. **Collect.** Search for current trends on each platform the user cares about (default:
   all five). Use the sources in `trend-playbook.md` section 1: platform hot lists, entertainment
   news, data sites. Search in Chinese, add the month and year, and prefer pages from the
   last 14 days. For each candidate note: what it is, where it is hot, when it started, one
   source link with its date. Drop anything you can't source.
2. **Explain each trend in one line** a Medibank marketer in Sydney would understand
   ("a Tencent Video show following medical students through surgery rotations").
3. **Screen out** anything on the never-touch list (`trend-playbook.md` section 4): politics,
   disasters and tragedies, celebrity scandals and feuds, crime, anything mocking a group,
   medical misinformation. These are 🔴 and get no angle.
4. **Score** the rest with the rubric (audience match, link to OSHC/health, freshness,
   safety). With a CSV, run `python tools/trend_score.py trends.csv --today YYYY-MM-DD`;
   columns are in `examples/trends_sample.csv`. Verdicts: **use now**, **adapt**
   (light touch or creator-led), **watch**, **avoid**.
5. **Find the angle** for each "use now" / "adapt" trend with the patterns in
   `trend-playbook.md` section 3. The angle borrows the format, feeling or question of the
   trend, then lands on one of the four content pillars. Never borrow show footage, logos,
   music or a celebrity's name or face.
6. **Match a stream and creator type.** Owned post, creator post, or both; which platform;
   which creator type from `references/kol-playbook.md` (e.g. an Australian medical-student
   KOC for a medical show). Hand-offs: posts → cn-content-writer, creators → cn-kol-manager,
   slots in the calendar → cn-content-planner.
7. **Check.** Run every sample title or hook through
   `python tools/compliance_scan.py --platform <id>`; trend copy is where "必看", "最好",
   "一定要" slip in.
8. **Update the radar.** Offer to add the new snapshot to `references/trend-radar.md` with
   today's date and sources, and to remove trends past their lifespan.

## Output

```
## 热点雷达 Trend radar · <date> · sources checked: <n>

| Trend | What it is | Where | Since | Verdict | Score |

### <Trend> · use now / adapt
- Why it fits: <one line, which persona and pillar>
- Angle: <hook in Chinese> → <the insurance-awareness point>
- Format & platform: <e.g. 小红书 图文 + 抖音 creator vlog>
- Creator type: <type, tier>
- Watch out: <IP, celebrity, health-risk or sponsor issue>
- Shelf life: <post by date>
- Source: <link, date>

### Avoid
- <Trend>: <reason, one line>
```

Sample titles under each angle go through the scanner and carry its verdict.

## Rules

* Don't invent trends, view counts, ratings or creator names. Numbers only with a source.
* Riding a trend never relaxes the core rule: inform, don't sell. No prices, links or
  "DM me", even in a playful meme post.
* Show names and memes may appear as a topic or hashtag in a post; show clips, stills,
  logos, theme music and cast names or faces may not (copyright and portrait rights,
  implied endorsement).
* A trend sponsored by another insurer, or involving a real person's conflict, is at most
  "adapt", creator-led, with no reference to the sponsor or the people.
* If a trend involves physical risk (a dance or stunt), the post must not encourage
  copying it; frame it around safety and what to do if hurt.
