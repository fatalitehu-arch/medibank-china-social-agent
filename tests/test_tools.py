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


def test_kol_weights_follow_evidence_and_ignore_followers():
    assert sum(kol_score.WEIGHTS.values()) == 100
    total_r = sum(c["r"] for c in kol_score.CRITERIA.values())
    for key, c in kol_score.CRITERIA.items():
        assert abs(kol_score.WEIGHTS[key] - 100 * c["r"] / total_r) < 1.5
    row = {"platform": "xiaohongshu", "followers": "4000", "based_in_australia": "yes",
           "audience_student_share": "0.8", "topic_relevance_share": "0.9", "useful_post_share": "0.5",
           "personal_post_share": "0.5", "reply_rate": "0.5"}
    small = kol_score.score_row(row)[1]
    big = kol_score.score_row({**row, "followers": "400000"})[1]
    assert small == big  # follower count sets the tier, never the score


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


# --- evidence register, finished posts, video editor ---------------------------------

import json as _json
import pytest
import shutil as _shutil

import evidence_check
import make_post
import video_edit

_ROOT = Path(__file__).resolve().parent.parent


def test_every_evidence_citation_exists():
    assert evidence_check.main([]) == 0


def test_strategy_files_cite_evidence():
    for rel in ["references/student-strategy.md", "references/kol-playbook.md", "references/content-playbook.md",
                "references/platforms/overview.md"]:
        assert "[E-" in (_ROOT / rel).read_text(encoding="utf-8"), rel


def test_make_post_text_and_compliance(tmp_path):
    spec = _json.loads((_ROOT / "examples" / "post_spec.json").read_text(encoding="utf-8"))
    worst, images = make_post.build(spec, tmp_path, render=False)
    assert worst < 2 and images == []
    md = (tmp_path / "post.md").read_text(encoding="utf-8")
    assert spec["title"] in md and spec["hashtags"][0] in md


def test_make_post_flags_a_selling_post(tmp_path):
    spec = _json.loads((_ROOT / "examples" / "post_spec.json").read_text(encoding="utf-8"))
    spec["body"] += "\n现在购买立减，加微信 abc123 领取报价"
    worst, _ = make_post.build(spec, tmp_path, render=False)
    assert worst == 2


def test_make_post_renders_cards(tmp_path):
    pytest.importorskip("PIL")
    try:
        font = make_post.find_font()
    except SystemExit:
        pytest.skip("no Chinese font on this machine")
    spec = _json.loads((_ROOT / "examples" / "post_spec.json").read_text(encoding="utf-8"))
    _, images = make_post.build(spec, tmp_path, font)
    assert len(images) == 1 + len(spec["cards"]) + 1
    from PIL import Image
    assert Image.open(tmp_path / images[0]).size == (1080, 1440)


def test_srt_shift_moves_every_timestamp():
    out = video_edit.shift_srt("1\n00:00:01,500 --> 00:00:59,900\nhi\n", 1.5)
    assert "00:00:03,000 --> 00:01:01,400" in out


def test_video_plan_dry_run_builds_commands(tmp_path):
    plan = _json.loads((_ROOT / "examples" / "video_plan.json").read_text(encoding="utf-8"))
    cmds = video_edit.build_commands(plan, tmp_path / "out.mp4", tmp_path, render_cards=False)
    assert len(cmds) == len(plan["clips"]) + 2  # one per clip, concat, final
    assert any("subtitles=" in " ".join(c) for c in cmds)


def test_video_render_end_to_end(tmp_path):
    if not _shutil.which("ffmpeg"):
        pytest.skip("ffmpeg not installed")
    pytest.importorskip("PIL")
    try:
        make_post.find_font()
    except SystemExit:
        pytest.skip("no Chinese font on this machine")
    import subprocess
    clip = tmp_path / "a.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30", "-f", "lavfi",
                    "-i", "sine=frequency=440:sample_rate=48000", "-t", "2", "-c:v", "libx264", "-c:a", "aac", str(clip)], check=True)
    srt = tmp_path / "s.srt"
    srt.write_text("1\n00:00:00,200 --> 00:00:01,500\n测试字幕\n", encoding="utf-8")
    plan = {"platform": "douyin", "clips": [{"file": str(clip)}], "subtitles": str(srt),
            "title": {"headline": "测试", "seconds": 1}, "end": {"next": "去学校官网搜 OSHC", "seconds": 1}}
    (tmp_path / "plan.json").write_text(_json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    assert video_edit.main([str(tmp_path / "plan.json"), "--out", str(tmp_path / "out.mp4")]) == 0
    info = video_edit.probe(tmp_path / "out.mp4")
    assert (info["width"], info["height"]) == (1080, 1920) and 3.5 < info["duration"] < 4.6


def test_scouted_creator_library_is_valid():
    import creator_library
    rows = creator_library.load()
    assert len(rows) >= 28
    assert creator_library.check(rows) == []
    assert all(r["Profile URL"].endswith(r["User ID"]) for r in rows)
    assert creator_library.next_id(rows, "xiaohongshu") == f"XHS-{len([r for r in rows if r['_file'] == 'xiaohongshu']) + 1:03d}"


def test_scouted_library_html_is_up_to_date():
    import creator_library
    built = creator_library.build_html(creator_library.load())
    assert creator_library.HTML_OUT.read_text(encoding="utf-8") == built


def test_scouted_library_check_catches_bad_score():
    import creator_library
    row = dict(creator_library.load()[0])
    row["Score (/100)"] = "50"
    assert any("score must be" in p for p in creator_library.check([row]))


def test_creator_library_open_prints_both_pages(capsys, monkeypatch):
    import creator_library
    monkeypatch.setenv("CI", "1")
    creator_library.main(["--open"])
    out = capsys.readouterr().out
    assert "process.html" in out and "library.html" in out
    assert creator_library.PROCESS_HTML.exists() and creator_library.HTML_OUT.exists()
