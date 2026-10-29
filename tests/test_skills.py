"""Structure checks: skills are well-formed, copies are in sync, referenced files exist."""

import filecmp
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_FILES = [ROOT / "SKILL.md"] + sorted((ROOT / "skills").glob("*/SKILL.md"))
PATH_RE = re.compile(r"`((?:references|tools|assets|examples|skills|evals)/[^`\s]+?)`")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path} has no frontmatter"
    return dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)


def test_frontmatter_name_and_description():
    for path in SKILL_FILES:
        fm = frontmatter(path)
        assert fm.get("description"), path
        expected = "medibank-cn-social" if path.parent == ROOT else path.parent.name
        assert fm.get("name") == expected, path


def test_referenced_paths_exist():
    for path in SKILL_FILES + sorted((ROOT / "references").rglob("*.md")):
        for ref in PATH_RE.findall(path.read_text(encoding="utf-8")):
            ref = ref.rstrip(".,;:)")
            if "<" in ref or "*" in ref:
                continue
            assert (ROOT / ref).exists(), f"{path.relative_to(ROOT)} points to missing {ref}"



def test_copies_match_sources():
    import importlib.util

    spec = importlib.util.spec_from_file_location("sync_skills", ROOT / "sync_skills.py")
    sync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sync)
    for tool_dir in sync.TOOL_DIRS:
        for name, files in sync.sources():
            for src, rel in files:
                dest = tool_dir / name / rel
                assert dest.exists(), f"missing {dest.relative_to(ROOT)}; run python sync_skills.py"
                assert filecmp.cmp(src, dest, shallow=False), f"stale {dest.relative_to(ROOT)}; run python sync_skills.py"
