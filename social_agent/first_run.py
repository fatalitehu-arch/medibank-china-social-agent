"""Open welcome.html the first time the agent is used in a fresh copy of the repository.

Called by the CLI on its first run, by the Claude Code SessionStart hook in
.claude/settings.json, and by Codex when AGENTS.md asks it to. A marker file
(.welcome_shown, git-ignored) makes sure it only happens once per copy.

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
MARKER = ROOT / ".welcome_shown"


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
    if MARKER.exists() and not force:
        return None
    opened = open_page()
    MARKER.write_text("shown\n", encoding="utf-8")
    where = "opened in your browser" if opened else f"open it in a browser: {PAGE}"
    return f"Welcome! See what this agent contains in welcome.html ({where})."


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    msg = maybe_show(force="--force" in argv)
    if msg and "--hook" in argv:
        print(f"{msg} This is the user's first session in this repository: in your first reply, "
              "mention welcome.html (skills, knowledge base, creator library and dashboard) in one line.")
    elif msg:
        print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
