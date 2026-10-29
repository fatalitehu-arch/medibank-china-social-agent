import filecmp
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills" / "medibank-xhs"


def files(base):
    return sorted(p.relative_to(base) for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def test_tool_copies_match_source():
    """.agents (Codex) and .claude (Claude Code) copies must match skills/; run sync_skills.py if this fails."""
    for target in (ROOT / ".agents" / "skills" / "medibank-xhs", ROOT / ".claude" / "skills" / "medibank-xhs"):
        assert files(target) == files(SOURCE), target
        for rel in files(SOURCE):
            assert filecmp.cmp(SOURCE / rel, target / rel, shallow=False), f"{target}/{rel} is stale"
