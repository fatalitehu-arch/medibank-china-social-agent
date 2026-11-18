"""Local web app: tools and the tool loop, with the Claude call replaced by a fake."""

import json
import sys
import types
from types import SimpleNamespace as NS

from social_agent import cli, web


def test_search_creators_filters_and_sorts():
    r = web.tool_search_creators("Shortlist", 2000, "", "", 5)
    assert r["total_in_library"] >= r["matches"] > 0
    scores = [int(c["Score (/100)"]) for c in r["creators"]]
    assert scores == sorted(scores, reverse=True)
    assert all(c["Status"] == "Shortlist" and int(c["Followers"]) <= 2000 for c in r["creators"])


def test_compliance_check_flags_selling():
    assert "RED" in web.tool_compliance_check("全网最低价，立即购买保险", "xiaohongshu")["verdict"]


def test_make_post_reports_missing_fields():
    result, is_error = web.run_tool("make_post", {"spec": {"platform": "xiaohongshu"}})
    assert "title" in result["error"] and not is_error


def test_unknown_tool_is_an_error():
    assert web.run_tool("nope", {})[1] is True


def test_system_prompt_uses_runner_note():
    assert cli.build_system_prompt(web.RUNNER_NOTE).endswith(web.RUNNER_NOTE)


def _fake_anthropic(monkeypatch):
    """CI installs only the dev requirements, so stand in for the SDK module."""
    mod = types.ModuleType("anthropic")

    class APIError(Exception):
        pass

    for name in ("AuthenticationError", "RateLimitError", "APIConnectionError", "APIStatusError"):
        setattr(mod, name, type(name, (APIError,), {}))
    mod.APIError = APIError
    mod.Anthropic = lambda **kw: object()
    monkeypatch.setitem(sys.modules, "anthropic", mod)


def test_tool_loop_runs_tools_and_returns_reply(monkeypatch):
    _fake_anthropic(monkeypatch)
    agent = web.Agent()
    agent.api_key = "test"
    agent.system = "sys"
    replies = [
        NS(stop_reason="tool_use", content=[
            NS(type="text", text="Searching the library."),
            NS(type="tool_use", id="t1", name="search_creators",
               input={"status": "Shortlist", "max_followers": 0, "city": "", "keyword": "", "limit": 3}),
        ]),
        NS(stop_reason="end_turn", content=[NS(type="text", text="Here are three creators.")]),
    ]
    monkeypatch.setattr(agent, "_call", lambda client: replies.pop(0))
    out = agent.chat("find creators")
    assert out["reply"].endswith("Here are three creators.")
    assert out["steps"] == [{"tool": "search_creators", "error": False}]
    tool_result = agent.messages[2]["content"][0]
    assert tool_result["tool_use_id"] == "t1"
    assert json.loads(tool_result["content"])["matches"] > 0
