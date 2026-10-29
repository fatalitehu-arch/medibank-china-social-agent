"""Command-line runner for the Medibank China social media agent (Claude API).

For teams that don't use Claude Code or Codex: it loads the same skill files as the
system prompt, calls Claude, and runs the local compliance scan on every draft it writes.

    python -m social_agent write   "offer letter 里 OSHC 那一栏怎么看" --platform xiaohongshu
    python -m social_agent repurpose approved_post.txt
    python -m social_agent plan    "2027 年 T1 开学季，4 周"
    python -m social_agent brief   "UNSW 新生，腰部博主，图文" --platform douyin
    python -m social_agent review  creator_draft.txt --platform xiaohongshu
    python -m social_agent check   my_draft.txt --platform wechat-oa
    python -m social_agent reply   comments.txt --platform weibo
    python -m social_agent chat

Offline (no API key):
    python -m social_agent scan  draft.txt --platform douyin
    python -m social_agent lint  draft.txt --platform weibo
    python -m social_agent kol   examples/kol_candidates.csv
    python -m social_agent calendar plan.csv
    python -m social_agent report examples/metrics_sample.csv
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import calendar_builder  # noqa: E402
import compliance_scan  # noqa: E402
import kol_score  # noqa: E402
import note_lint  # noqa: E402
import performance_report  # noqa: E402

MODEL = "claude-opus-5-5"
PLATFORMS = ["xiaohongshu", "wechat-oa", "wechat-channels", "douyin", "weibo"]

MODE_PROMPTS = {
    "write": "Use cn-content-writer. Platform: {platform}. Write this:\n\n{task}",
    "repurpose": "Use cn-repurpose. Adapt this approved content for the other platforms:\n\n{task}",
    "plan": "Use cn-content-planner. Build a content plan for:\n\n{task}",
    "brief": "Use cn-kol-manager task 4. Platform: {platform}. Write a creator brief for:\n\n{task}",
    "review": "Use cn-kol-manager task 5. Platform: {platform}. Review this creator draft:\n\n{task}",
    "check": "Use cn-compliance-review. Platform: {platform}. The keyword scanner already ran; "
             "its report is below the draft.\n\n{task}",
    "reply": "Use cn-community-manager. Platform: {platform}. Draft replies to these comments:\n\n{task}",
}
SCAN_AFTER = {"write", "repurpose", "review", "reply"}


def build_system_prompt():
    """Root SKILL.md, sub-skills, then references, in a fixed order so the prompt caches."""
    files = [ROOT / "SKILL.md"]
    files += sorted((ROOT / "skills").glob("*/SKILL.md"))
    files += sorted((ROOT / "references").rglob("*.md"))
    parts = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        parts.append(f'<file path="{rel}">\n{f.read_text(encoding="utf-8")}\n</file>')
    parts.append("You are running through the API, not an agent tool: you cannot run the "
                 "scripts in tools/ yourself. The runner scans your drafts after you answer, "
                 "so apply the rules by hand while writing. Sub-skills referenced by name are "
                 "the skills/<name>/SKILL.md files above.")
    return "\n\n".join(parts)


def ask_claude(client, system, messages):
    """Stream one reply to the terminal and return the final message."""
    import anthropic

    try:
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=32000,
            system=system,
            messages=messages,
            output_config={"effort": "medium"},
            cache_control={"type": "ephemeral"},
            # On a policy decline, the API re-runs the request on a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
            final = stream.get_final_message()
    except anthropic.AuthenticationError:
        sys.exit("\nNo valid API key. Set ANTHROPIC_API_KEY (see README).")
    except anthropic.RateLimitError:
        sys.exit("\nRate limited by the API. Wait a minute and try again.")
    except anthropic.APIConnectionError:
        sys.exit("\nCould not reach the Claude API. Check your network.")
    except anthropic.APIStatusError as e:
        sys.exit(f"\nAPI error {e.status_code}: {e.message}")
    print()
    if final.stop_reason == "refusal":
        print("\n[The model declined this request. Rephrase it or check it with Legal.]")
    return final


def reply_text(message):
    return "".join(b.text for b in message.content if b.type == "text")


def scan_and_print(text, platform=None):
    worst, hits = compliance_scan.scan(text, platform=platform)
    print("\n──── 自动合规扫描 Keyword scan ────")
    print(compliance_scan.format_report(worst, hits, platform))
    return worst


def read_task(task):
    path = Path(task)
    return path.read_text(encoding="utf-8") if path.is_file() else task


def run_mode(mode, task, platform):
    import anthropic

    task = read_task(task)
    if mode == "check":
        worst, hits = compliance_scan.scan(task, platform=platform)
        task = f"{task}\n\n<scanner_report>\n{compliance_scan.format_report(worst, hits, platform)}\n</scanner_report>"

    client = anthropic.Anthropic()
    prompt = MODE_PROMPTS[mode].format(task=task, platform=platform or "xiaohongshu")
    final = ask_claude(client, build_system_prompt(), [{"role": "user", "content": prompt}])
    if mode in SCAN_AFTER:
        # repurpose spans platforms, so scan it at the strictest level.
        return scan_and_print(reply_text(final), None if mode == "repurpose" else platform)
    return 0


def chat():
    import anthropic

    client = anthropic.Anthropic()
    system = build_system_prompt()
    messages = []
    print("Medibank China social agent. Type your request; empty line or Ctrl-D to quit.\n")
    while True:
        try:
            user = input("你 > ").strip()
        except EOFError:
            break
        if not user:
            break
        messages.append({"role": "user", "content": user})
        print("agent > ", end="")
        final = ask_claude(client, system, messages)
        messages.append({"role": "assistant", "content": final.content})
        scan_and_print(reply_text(final))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="social_agent", description="Medibank China social media agent")
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode, help_text in [("write", "write owned content"), ("repurpose", "adapt for other platforms"),
                            ("plan", "content calendar / strategy"), ("brief", "creator brief"),
                            ("review", "review a creator draft"), ("check", "compliance check"),
                            ("reply", "draft comment replies")]:
        p = sub.add_parser(mode, help=help_text)
        p.add_argument("task", help="text, or a path to a text file")
        p.add_argument("--platform", choices=PLATFORMS)
    for mode, help_text in [("scan", "keyword compliance scan (offline)"), ("lint", "style lint (offline)")]:
        p = sub.add_parser(mode, help=help_text)
        p.add_argument("file")
        p.add_argument("--platform", choices=PLATFORMS)
    for mode, help_text in [("kol", "score a creator CSV (offline)"), ("calendar", "check a calendar CSV (offline)"),
                            ("report", "performance report from a metrics CSV (offline)")]:
        p = sub.add_parser(mode, help=help_text)
        p.add_argument("csv")
        p.add_argument("--out")
    sub.add_parser("chat", help="interactive session")
    args = parser.parse_args(argv)

    platform_args = ["--platform", args.platform] if getattr(args, "platform", None) else []
    out_args = ["--out", args.out] if getattr(args, "out", None) else []
    if args.mode == "scan":
        return compliance_scan.main([args.file] + platform_args)
    if args.mode == "lint":
        return note_lint.main([args.file] + platform_args)
    if args.mode == "kol":
        return kol_score.main([args.csv] + out_args)
    if args.mode == "calendar":
        return calendar_builder.main([args.csv] + out_args)
    if args.mode == "report":
        return performance_report.main([args.csv] + out_args)
    if args.mode == "chat":
        return chat()
    return run_mode(args.mode, args.task, args.platform)


if __name__ == "__main__":
    sys.exit(main())
