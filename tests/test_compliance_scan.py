import json
from pathlib import Path

import pytest

import compliance_scan

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "examples" / "drafts"
VERDICT = {0: "green", 1: "amber", 2: "red"}
CASES = [json.loads(line) for line in (ROOT / "evals" / "scanner_cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.mark.parametrize("case", CASES, ids=[c["text"][:20] for c in CASES])
def test_scanner_cases(case):
    worst, hits = compliance_scan.scan(case["text"], platform=case["platform"])
    hit_ids = {h.id for h in hits if h.level != "note"}
    assert VERDICT[worst] == case["verdict"], [(h.id, h.match) for h in hits]
    assert set(case["must_hit"]) <= hit_ids


@pytest.mark.parametrize("platform", ["xiaohongshu", "wechat-oa", "wechat-channels", "douyin", "weibo"])
def test_good_drafts_are_green_on_their_platform(platform):
    worst, hits = compliance_scan.scan((DRAFTS / f"good_{platform}.txt").read_text(encoding="utf-8"), platform=platform)
    assert worst == 0, [(h.id, h.match) for h in hits if h.level != "note"]


@pytest.mark.parametrize("name", ["bad_xiaohongshu", "bad_douyin", "bad_wechat-oa"])
def test_bad_drafts_are_red(name):
    platform = name.split("_", 1)[1]
    assert compliance_scan.scan((DRAFTS / f"{name}.txt").read_text(encoding="utf-8"), platform=platform)[0] == 2


def test_unknown_platform_rejected():
    with pytest.raises(ValueError):
        compliance_scan.scan("hi", platform="tiktok")


def test_every_rule_compiles_and_cites_a_rule_id():
    rules = compliance_scan.load_rules()
    text = (ROOT / "references" / "compliance.md").read_text(encoding="utf-8")
    for rule in rules["rules"]:
        for rule_id in rule["rule"].split("/"):
            rid = rule_id if "-" in rule_id else rule["rule"].split("-")[0] + "-" + rule_id
            assert f"| {rid} |" in text, f"{rule['id']} cites {rid}, not defined in compliance.md"
