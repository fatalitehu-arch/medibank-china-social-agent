"""Command-line runner for the Medibank 小红书 agent (Claude API).

For teams that don't use Claude Code or Claude.ai: it loads the same skill files
(skills/medibank-xhs) as the system prompt, calls Claude, and runs the local
compliance scan on every draft it writes.

    python -m xhs_agent post "写一篇：offer letter 里 OSHC 那一栏怎么看"
    python -m xhs_agent plan "2027 年 T1 开学季，4 周"
    python -m xhs_agent brief "UNSW 新生，腰部博主，图文"
    python -m xhs_agent check examples/draft_bad.txt
    python -m xhs_agent kol examples/kol_candidates.csv
    python -m xhs_agent chat
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "medibank-xhs"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import compliance_scan  # noqa: E402
import kol_score  # noqa: E402

MODEL = "claude-opus-5-5"

MODE_PROMPTS = {
    "post": "Mode A 写笔记. Write one brand-account note for this request:\n\n{task}",
    "plan": "Mode B 内容规划. Build a content plan for this request:\n\n{task}",
    "brief": "Mode C 博主合作. Write a 蒲公英 creator brief for this request:\n\n{task}",
    "review": "Mode C + D. Review this creator draft and give the verdict, problems and a fixed version:\n\n{task}",
    "check": "Mode D 审稿. Check this draft. The keyword scanner already ran; its report is below the draft.\n\n{task}",
}


def build_system_prompt():
    """SKILL.md followed by every reference file, in a fixed order so the prompt caches."""
    parts = [(SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")]
    for ref in sorted((SKILL_DIR / "references").glob("*.md")):
        parts.append(f"\n\n<reference file=\"references/{ref.name}\">\n"
                     f"{ref.read_text(encoding='utf-8')}\n</reference>")
    parts.append("\n\nYou are running through the API, not Claude Code: you cannot run the "
                 "scripts yourself. The runner scans your drafts after you answer, so "
                 "apply the rules by hand while writing.")
    return "".join(parts)


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


def scan_and_print(text, title="自动合规扫描 Keyword scan"):
    worst, hits = compliance_scan.scan(text)
    print(f"\n──── {title} ────")
    print(compliance_scan.format_report(worst, hits))
    return worst


def run_mode(mode, task):
    import anthropic

    if mode == "check":
        draft = Path(task).read_text(encoding="utf-8") if Path(task).is_file() else task
        worst, hits = compliance_scan.scan(draft)
        task = f"{draft}\n\n<scanner_report>\n{compliance_scan.format_report(worst, hits)}\n</scanner_report>"
    elif mode == "review" and Path(task).is_file():
        task = Path(task).read_text(encoding="utf-8")

    client = anthropic.Anthropic()
    final = ask_claude(client, build_system_prompt(),
                       [{"role": "user", "content": MODE_PROMPTS[mode].format(task=task)}])
    if mode in ("post", "review"):
        return scan_and_print(reply_text(final))
    return 0


def chat():
    import anthropic

    client = anthropic.Anthropic()
    system = build_system_prompt()
    messages = []
    print("Medibank 小红书 agent. Type your request; empty line or Ctrl-D to quit.\n")
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
    parser = argparse.ArgumentParser(prog="xhs_agent", description="Medibank 小红书 agent")
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode, help_text in [("post", "write a brand note"), ("plan", "content calendar / strategy"),
                            ("brief", "write a creator brief"), ("review", "review a creator draft (text or file)"),
                            ("check", "compliance check (text or file)")]:
        p = sub.add_parser(mode, help=help_text)
        p.add_argument("task")
    p = sub.add_parser("kol", help="score a creator CSV (offline, no API)")
    p.add_argument("csv")
    p.add_argument("--out")
    sub.add_parser("scan", help="keyword scan only (offline, no API)").add_argument("file")
    sub.add_parser("chat", help="interactive session")
    args = parser.parse_args(argv)

    if args.mode == "kol":
        return kol_score.main([args.csv] + (["--out", args.out] if args.out else []))
    if args.mode == "scan":
        return compliance_scan.main([args.file])
    if args.mode == "chat":
        return chat()
    return run_mode(args.mode, args.task)


if __name__ == "__main__":
    sys.exit(main())
