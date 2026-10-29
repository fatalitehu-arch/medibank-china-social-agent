#!/usr/bin/env python3
"""Copy every skill into the folders each agent tool scans.

Edit skills only in their source location, then run:

    python sync_skills.py

Sources                         Copied to
  SKILL.md + agents/  (router)    .claude/skills/medibank-cn-social/   .agents/skills/medibank-cn-social/
  skills/<name>/                  .claude/skills/<name>/         .agents/skills/<name>/

.claude/skills is read by Claude Code, .agents/skills by OpenAI Codex. Skill files point
to shared folders (references/, tools/, assets/) by repo-root paths, so the copies stay
small and the shared files have one home.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL_DIRS = [ROOT / ".claude" / "skills", ROOT / ".agents" / "skills"]


def sources():
    """Yield (skill name, list of (source path, relative destination))."""
    yield "medibank-cn-social", [(ROOT / "SKILL.md", "SKILL.md"),
                           (ROOT / "agents" / "openai.yaml", "agents/openai.yaml")]
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if (skill_dir / "SKILL.md").is_file():
            files = [(p, str(p.relative_to(skill_dir))) for p in sorted(skill_dir.rglob("*")) if p.is_file()]
            yield skill_dir.name, files


def sync():
    for tool_dir in TOOL_DIRS:
        if tool_dir.exists():
            shutil.rmtree(tool_dir)
        for name, files in sources():
            for src, rel in files:
                dest = tool_dir / name / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        print(f"synced {tool_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    sync()
