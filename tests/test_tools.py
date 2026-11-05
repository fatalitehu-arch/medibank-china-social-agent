from datetime import date
from pathlib import Path

import calendar_builder
import kol_score
import note_lint
import performance_report
import trend_score

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


def test_kol_hard_stops_and_bands():
    scored = {r["handle"]: r for r in kol_score.score_file(EXAMPLES / "kol_candidates.csv")}
    assert scored["示例_留学规划师Amy"]["score"] == 0
    assert scored["示例_保险科普小王"]["band"] == "no"
    assert scored["示例_悉尼吃喝玩乐"]["band"] == "no"
    assert scored["示例_悉尼读研日记"]["band"] == "go"
    assert scored["示例_生活好物分享"]["band"] == "no"


def test_kol_platform_baseline_changes_engagement_score():
    row = {"platform": "xiaohongshu", "followers": "40000", "based_in_australia": "yes",
           "audience_student_share": "0.8", "avg_likes": "500", "avg_saves": "100",
           "avg_comments": "20", "topic_relevance_share": "0.9"}
    xhs = kol_score.score_row(row, {})[1]
    weibo = kol_score.score_row({**row, "platform": "weibo"}, {})[1]
    assert weibo > xhs  # same numbers count for more on a lower-engagement platform


def test_note_lint_platform_limits():
    long_title = "【标题候选】\n1. 这是一个特别特别特别长的小红书标题已经超过二十个字了吧\n2. 短标题\n3. 另一个"
    assert any(level == "error" for level, _ in note_lint.lint(long_title, "xiaohongshu"))
    assert not any(level == "error" for level, _ in note_lint.lint(long_title, "wechat-oa"))
    weibo_long = "【正文】\n" + "很长的微博" * 40
    assert any(level == "error" for level, _ in note_lint.lint(weibo_long, "weibo"))


def test_good_drafts_pass_lint():
    for platform in ["xiaohongshu", "wechat-oa", "wechat-channels", "douyin", "weibo"]:
        text = (EXAMPLES / "drafts" / f"good_{platform}.txt").read_text(encoding="utf-8")
        errors = [m for level, m in note_lint.lint(text, platform) if level == "error"]
        assert not errors, (platform, errors)


def test_calendar_flags_mix_and_amber():
    rows = calendar_builder.load(ROOT / "assets" / "templates" / "content-calendar.csv")
    findings = calendar_builder.check(rows)
    assert any("needs Legal" in f for f in findings)
    assert "| Platform |" in calendar_builder.to_markdown(rows, findings)


def test_example_plan_passes_calendar_checks():
    rows = calendar_builder.load(EXAMPLES / "plan_t1_2027.csv")
    findings = [f for f in calendar_builder.check(rows) if "needs Legal" not in f]
    assert findings == []


def test_trend_score_verdicts():
    rows = trend_score.load(ROOT / "examples" / "trends_sample.csv")
    got = {r["trend"]: trend_score.score_row(r, date(2026, 11, 5))[1] for r in rows}
    assert got["令人心动的offer 第八季"] == "use now"
    assert got["闪身步"] == "adapt"
    assert got["后会友期"] == "adapt"
    assert got["（示例）某地自然灾害话题"] == "avoid"


def test_trend_score_freshness_decays():
    row = {"trend": "x", "type": "meme", "first_seen": "2026-11-01", "ends": "",
           "audience_match": "5", "oshc_link": "5", "flags": ""}
    fresh = trend_score.score_row(row, date(2026, 11, 2))[0]
    stale = trend_score.score_row(row, date(2026, 12, 30))[0]
    assert fresh > stale
    assert stale == 80.0


def test_creator_dashboard_flags_and_totals():
    import creator_dashboard

    roster = creator_dashboard.load(ROOT / "creators" / "roster.csv")
    posts = creator_dashboard.load(ROOT / "creators" / "posts.csv")
    data = creator_dashboard.build(roster, posts, date(2027, 1, 19))
    by_id = {c["id"]: c for c in data["creators"]}
    assert data["summary"]["inquiries"] == sum(int(p["inquiries"]) for p in posts)
    assert "Waiting for first post" in by_id["C08"]["flags"]
    assert any(f.startswith("Contract ends") for f in by_id["C05"]["flags"])
    assert any("amber" in f for f in by_id["C06"]["flags"])
    assert by_id["C01"]["flags"] == []


def test_welcome_page_is_current():
    import build_welcome

    assert (ROOT / "welcome.html").read_text(encoding="utf-8") == build_welcome.render(), \
        "run python tools/build_welcome.py"


def test_performance_report_sections():
    md = performance_report.build(performance_report.load(EXAMPLES / "metrics_sample.csv"))
    for heading in ["By platform", "Owned vs creator", "By pillar", "Top posts", "Bottom posts", "By creator"]:
        assert heading in md


def test_welcome_page_is_english_only():
    import re
    html = (Path(__file__).resolve().parent.parent / "welcome.html").read_text(encoding="utf-8")
    assert not re.search(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]", html)
