# Sample output: one idea, five platforms

**Request:** 把《offer letter 里 OSHC 那一栏怎么看》改成五个平台的版本
**Sub-skill:** cn-repurpose. Source: the approved 公众号 guide.

| Platform | Draft | Shape | Scanner (`--platform`) |
|----------|-------|-------|------------------------|
| 微信公众号 | [`drafts/good_wechat-oa.txt`](../drafts/good_wechat-oa.txt) | Full guide with sections and FAQ (canonical version) | 🟢 |
| 小红书 | [`drafts/good_xiaohongshu.txt`](../drafts/good_xiaohongshu.txt) | 图文 steps, first-person hook, "学校官网搜 OSHC" | 🟢 |
| 视频号 | [`drafts/good_wechat-channels.txt`](../drafts/good_wechat-channels.txt) | 60 s for parents, "完整指南在 Medibank 公众号" (allowed inside WeChat) | 🟢 |
| 抖音 | [`drafts/good_douyin.txt`](../drafts/good_douyin.txt) | 60 s creator-style script, no WeChat mention | 🟢 |
| 微博 | [`drafts/good_weibo.txt`](../drafts/good_weibo.txt) | ≤ 140 chars + #澳洲留学# | 🟢 |

Same facts everywhere; different shape for each platform. The 视频号 version mentions the
公众号; the same sentence would be 🔴 on 小红书 or 抖音 (PL-3):

```
$ python tools/compliance_scan.py examples/drafts/good_wechat-channels.txt --platform wechat-channels
结论 Verdict: 🟢 GREEN
$ python tools/compliance_scan.py examples/drafts/good_wechat-channels.txt --platform douyin
结论 Verdict: 🔴 RED   (「公众号」 PL-3 diversion)
```

Publishing order: 公众号 guide (Mon) → 视频号 + 小红书 (Wed–Thu) → 抖音 creator video and
微博 post at the next intake peak.
