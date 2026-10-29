#!/usr/bin/env python3
"""Copy the skill from skills/medibank-xhs into the folders each agent tool scans.

skills/medibank-xhs is the only copy to edit. Run this after any change:

    python sync_skills.py

  .claude/skills/medibank-xhs   Claude Code (project skill)
  .agents/skills/medibank-xhs   OpenAI Codex (repo skill)
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "skills" / "medibank-xhs"
TARGETS = [ROOT / ".claude" / "skills" / "medibank-xhs", ROOT / ".agents" / "skills" / "medibank-xhs"]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")

if __name__ == "__main__":
    for target in TARGETS:
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SOURCE, target, ignore=IGNORE)
        print(f"synced {target.relative_to(ROOT)}")
