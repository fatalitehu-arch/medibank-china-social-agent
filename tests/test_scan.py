import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "medibank-xhs" / "scripts"))

import compliance_scan  # noqa: E402
import kol_score  # noqa: E402

EXAMPLES = ROOT / "examples"


def ids(text):
    return {h.id for h in compliance_scan.scan(text)[1] if h.level != "note"}


def test_bad_draft_is_red():
    worst, hits = compliance_scan.scan((EXAMPLES / "draft_bad.txt").read_text(encoding="utf-8"))
    assert worst == 2
    assert {"price", "promo", "competitor", "buy_cta", "diversion", "visa_guarantee",
            "agent_attack", "undisclosed_ad", "absolute"} <= {h.id for h in hits}


def test_good_draft_is_green():
    worst, _ = compliance_scan.scan((EXAMPLES / "draft_good.txt").read_text(encoding="utf-8"))
    assert worst == 0


def test_first_time_is_not_an_absolute_term():
    assert "absolute" not in ids("我第一次在悉尼看病")
    assert "absolute" in ids("澳洲第一的保险")


def test_agent_helping_is_not_a_buy_cta():
    assert "buy_cta" not in ids("中介可以帮你办，但保险是你自己的")
    assert "buy_cta" in ids("私信我，我帮你买")


def test_free_needs_qualifier():
    assert compliance_scan.scan("Online Doctor 免费看医生")[0] == 1
    assert compliance_scan.scan("Online Doctor 无自付，以官网条款为准")[0] == 0


def test_kol_ranking_and_hard_stops():
    scored = {r["handle"]: r for r in kol_score.score_file(EXAMPLES / "kol_candidates.csv")}
    assert scored["示例_留学规划师Amy"]["score"] == 0
    assert scored["示例_悉尼吃喝玩乐"]["band"] == "no"
    assert scored["示例_悉尼读研日记"]["band"] == "go"
    assert scored["示例_生活好物分享"]["band"] == "no"
