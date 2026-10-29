# Team workflow

## Roles

| Role | Who (suggested) | Uses the agent for |
|------|-----------------|--------------------|
| Social lead | Medibank international student marketing | Monthly plan (`cn-content-planner`), owned content (`cn-content-writer`, `cn-repurpose`), final call on publishing |
| Creator manager | Same team or agency | Creator search, scoring, briefs and draft reviews on 蒲公英, 星图, 互选, 微任务 (`cn-kol-manager`) |
| Community manager | Same team or agency | Comments, DMs, 公众号留言, live Q&A (`cn-community-manager`) |
| Compliance reviewer | Medibank Legal & Compliance | Every 🟡 item, every creator campaign, every high-reach post (`cn-compliance-review` + `assets/templates/legal-signoff.md`) |
| Data owner | Digital team | `brand-facts.md` each intake; monthly exports for `cn-performance-review`; site and chatbot traffic |

## Weekly rhythm

| Day | Task | Skill |
|-----|------|-------|
| Mon | Check last week's numbers per platform; pick owned topics and creator slots | `cn-performance-review`, `cn-content-planner` |
| Tue | Write the week's lead piece (often a 公众号 article or 小红书 note), then adapt it | `cn-content-writer`, `cn-repurpose` |
| Tue | Send creator briefs through each marketplace | `cn-kol-manager` |
| Wed–Thu | Review creator drafts; fix and re-check | `cn-kol-manager`, `cn-compliance-review` |
| Thu | Legal review of anything 🟡 or creator-made | (human) |
| Fri–Sun | Publish in each platform's peak window (see `references/platforms/`); reply to comments | `cn-community-manager` |
| Daily | Watch 微博 and comment sections for complaints (crisis L1–L3) | `cn-community-manager` + `references/crisis-playbook.md` |

## Before anything goes live

1. Scanner verdict is 🟢 **for the platform it will be posted on**
   (`python tools/compliance_scan.py draft.txt --platform <id>`), or every 🟡 item has been
   fixed or signed off.
2. Every fact matches `references/brand-facts.md` (no `【待确认】` left).
3. Creator content is booked through the platform's marketplace and shows the sponsor tag.
4. No links, QR codes, WeChat IDs or phone numbers in text, images or video. Inside WeChat,
   pointing to the 公众号 menu is allowed; on 小红书, 抖音 and 微博 it is not.
5. Images and video use mock-ups (`assets/images/mock-offer-letter.svg`), never a real
   student's offer letter or policy.
6. Live streams have a Q&A sheet prepared (`assets/templates/comment-replies.md`).

## When something goes wrong

| Situation | Action |
|-----------|--------|
| Post throttled (限流) or removed | Record the post and the likely trigger words; add them to `tools/rules.json` and a case to `evals/scanner_cases.jsonl` |
| Comment asks for price / to buy | Use `assets/templates/comment-replies.md`; never quote |
| Creator posts without approval | Ask them to edit or remove; log it for the 90-day review |
| Complaint spreading on 微博 | Follow `references/crisis-playbook.md` (L2/L3 → Legal and comms same day) |
| Regulator or platform notice | Stop the campaign; escalate to Legal |

## Measuring success (monthly)

See `references/student-strategy.md` → "What to measure" and
`assets/templates/monthly-report.md`. Compare each platform with its own previous period,
not with the others. The key number is visits to the university Medibank OSHC site and
chatbot sessions from China-based students during the offer and pre-departure windows.
