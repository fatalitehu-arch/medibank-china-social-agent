"""Open welcome.html the first time the agent is used in a fresh copy of the repository.

Called by the CLI on its first run, by the Claude Code SessionStart hook (in
.claude/settings.json for a cloned copy, in hooks/hooks.json when installed as a Claude
plugin), and by Codex when AGENTS.md asks it to. A marker file (.welcome_shown) makes sure
it only happens once per copy. As a plugin the marker lives in ${CLAUDE_PLUGIN_DATA}, which
survives plugin updates; otherwise it sits in the repository root (git-ignored).

    python social_agent/first_run.py          # open once, then stay quiet
    python social_agent/first_run.py --hook   # same, and print a note for the agent's context
    python social_agent/first_run.py --force  # open again
"""

import os
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "welcome.html"


def marker():
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if data:
        Path(data).mkdir(parents=True, exist_ok=True)
        return Path(data) / ".welcome_shown"
    return ROOT / ".welcome_shown"


def open_page():
    """Open the page in the default browser; return False where there is no browser (CI, servers)."""
    if os.environ.get("CI"):
        return False
    try:
        return webbrowser.open(PAGE.as_uri())
    except webbrowser.Error:
        return False


def maybe_show(force=False):
    """Return a one-line message if the page was shown (or should be), else None."""
    mark = marker()
    if mark.exists() and not force:
        return None
    opened = open_page()
    mark.write_text("shown\n", encoding="utf-8")
    where = "opened in your browser" if opened else f"open it in a browser: {PAGE}"
    return f"Welcome! See what this agent contains in welcome.html ({where})."


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    msg = maybe_show(force="--force" in argv)
    if msg and "--hook" in argv:
        print(f"{msg} This is the user's first session in this repository: in your first reply, "
              f"mention the welcome page ({PAGE}: skills, knowledge base, creator library and dashboard) in one line.")
    elif msg:
        print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
