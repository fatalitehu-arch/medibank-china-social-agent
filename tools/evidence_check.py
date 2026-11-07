#!/usr/bin/env python3
"""Check that every [E-n] / [A-n] citation in the agent points to a row in references/evidence.md.

Usage:
    python tools/evidence_check.py           # report citations and fail on missing rows
    python tools/evidence_check.py --list    # list each row and the files that cite it
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "references" / "evidence.md"
CITE = re.compile(r"\[([EA]-\d+)\]")
ROW = re.compile(r"^\| ([EA]-\d+) \|", re.M)
SCAN = ["SKILL.md", "skills", "references", "assets/templates", "README.md", "使用说明.md"]


def rows():
    return set(ROW.findall(REGISTER.read_text(encoding="utf-8")))


def citations():
    found = {}
    for item in SCAN:
        path = ROOT / item
        files = [path] if path.is_file() else sorted(path.rglob("*.md")) if path.exists() else []
        for f in files:
            if f == REGISTER:
                continue
            for cid in CITE.findall(f.read_text(encoding="utf-8")):
                found.setdefault(cid, set()).add(f.relative_to(ROOT).as_posix())
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)
    known, cited = rows(), citations()
    missing = sorted(set(cited) - known, key=lambda c: (c[0], int(c[2:])))
    unused = sorted(known - set(cited), key=lambda c: (c[0], int(c[2:])))
    if args.list:
        for cid in sorted(known | set(cited), key=lambda c: (c[0], int(c[2:]))):
            print(f"{cid}: {', '.join(sorted(cited.get(cid, []))) or '(not cited yet)'}")
    print(f"{len(known)} rows, {sum(len(v) for v in cited.values())} citing files, "
          f"{len(missing)} missing, {len(unused)} not cited yet")
    for cid in missing:
        print(f"MISSING {cid} cited in {', '.join(sorted(cited[cid]))}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
