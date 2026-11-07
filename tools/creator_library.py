#!/usr/bin/env python3
"""Scouted creator library: creators found with the tested search process.

One CSV per platform in creators/scouted/ (xiaohongshu.csv first; Xiaohongshu is the main
platform for Chinese students). Each row is one creator with platform IDs, a scan score
(5 dimensions x 1-5, x4 = /100) and a status: Shortlist, Watch, Exclude or Reference.
The process is in references/creator-finding.md; the library rules in creators/scouted/README.md.

Usage:
    python creator_library.py                       # Markdown summary + shortlist
    python creator_library.py --status Shortlist    # one status only
    python creator_library.py --check               # validate every row (CI)
    python creator_library.py --html                # rebuild creators/scouted/library.html
    python creator_library.py --next-id xiaohongshu # next free Library ID when adding a creator
"""

import argparse
import csv
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCOUTED = ROOT / "creators" / "scouted"
HTML_OUT = SCOUTED / "library.html"

PLATFORMS = {  # file stem -> (display name, ID prefix, profile URL prefix)
    "xiaohongshu": ("Xiaohongshu", "XHS", "https://www.xiaohongshu.com/user/profile/"),
    "douyin": ("Douyin", "DY", "https://www.douyin.com/user/"),
    "wechat-channels": ("WeChat Channels", "WXC", ""),
    "weibo": ("Weibo", "WB", "https://weibo.com/u/"),
}
STATUSES = ["Shortlist", "Watch", "Exclude", "Reference"]
CATEGORIES = ["Student Life", "Career & Study", "Resident Life", "Food & Lifestyle"]
TIERS = ["<500", "500-1k", "1k-2k", "2k+"]
DIMENSIONS = ["Fit (1-5)", "Size (1-5)", "Activity (1-5)", "Authenticity (1-5)", "Content (1-5)"]
COLUMNS = ["Library ID", "Platform", "Category", "Nickname", "Xiaohongshu ID", "User ID", "Profile URL",
           "Followers", "Tier", "Likes & Collects", "Following", "IP Location", "City", "Identity",
           "Content Focus", "Source Keyword", "Ad / Collab Signals", "Red Flags", *DIMENSIONS,
           "Score (/100)", "Status"]


def tier(followers):
    return "<500" if followers < 500 else "500-1k" if followers < 1000 else "1k-2k" if followers < 2000 else "2k+"


def load(folder=SCOUTED):
    rows = []
    for path in sorted(folder.glob("*.csv")):
        with open(path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                row["_file"] = path.stem
                rows.append(row)
    return rows


def check(rows):
    """Return a list of problems; empty means the library is valid."""
    problems, seen = [], set()
    for r in rows:
        rid = r.get("Library ID", "?")
        missing = [c for c in COLUMNS if c not in r]
        if missing:
            problems.append(f"{rid}: missing columns {missing}")
            continue
        name, prefix, url = PLATFORMS.get(r["_file"], (None, None, None))
        if name is None:
            problems.append(f"{rid}: unknown platform file {r['_file']}.csv")
            continue
        if rid in seen:
            problems.append(f"{rid}: duplicate Library ID")
        seen.add(rid)
        if not rid.startswith(prefix + "-"):
            problems.append(f"{rid}: ID should start with {prefix}-")
        if r["Platform"] != name:
            problems.append(f"{rid}: Platform should be {name}")
        if r["Status"] not in STATUSES:
            problems.append(f"{rid}: status {r['Status']!r} not in {STATUSES}")
        if r["Category"] not in CATEGORIES:
            problems.append(f"{rid}: category {r['Category']!r} not in {CATEGORIES}")
        if not r["User ID"] or (url and r["Profile URL"] != url + r["User ID"]):
            problems.append(f"{rid}: Profile URL must be {url}<User ID>")
        try:
            followers = int(r["Followers"])
            dims = [int(r[d]) for d in DIMENSIONS]
            score = int(r["Score (/100)"])
        except ValueError:
            problems.append(f"{rid}: Followers, sub-scores and score must be whole numbers")
            continue
        if r["Tier"] != tier(followers):
            problems.append(f"{rid}: tier should be {tier(followers)} for {followers} followers")
        if any(not 1 <= d <= 5 for d in dims) or score != 4 * sum(dims):
            problems.append(f"{rid}: score must be 4 x the five 1-5 sub-scores ({4 * sum(dims)})")
        if r["Status"] == "Shortlist" and (followers >= 2000 or score < 88):
            problems.append(f"{rid}: Shortlist needs under 2k followers and score >= 88")
        if r["Status"] == "Reference" and followers < 2000:
            problems.append(f"{rid}: Reference is for 2k+ accounts kept as benchmarks")
    return problems


def next_id(rows, platform):
    prefix = PLATFORMS[platform][1]
    nums = [int(r["Library ID"].split("-")[1]) for r in rows if r["Library ID"].startswith(prefix + "-")]
    return f"{prefix}-{max(nums, default=0) + 1:03d}"


def summary(rows):
    out = {"total": len(rows), "platforms": {}, "status": {}, "category": {}, "tier": {}}
    for r in rows:
        for key, val in (("platforms", r["Platform"]), ("status", r["Status"]),
                         ("category", r["Category"]), ("tier", r["Tier"])):
            out[key][val] = out[key].get(val, 0) + 1
    return out


def ranked(rows):
    order = {s: i for i, s in enumerate(STATUSES)}
    return sorted(rows, key=lambda r: (order.get(r["Status"], 9), -int(r["Score (/100)"]), r["Library ID"]))


def to_markdown(rows, status=None):
    s = summary(rows)
    show = [r for r in ranked(rows) if status is None or r["Status"] == status]
    lines = [f"## Creator library: {s['total']} creators scouted",
             "", "Platforms: " + ", ".join(f"{k} {v}" for k, v in s["platforms"].items()),
             "Status: " + ", ".join(f"{k} {s['status'].get(k, 0)}" for k in STATUSES), "",
             "| ID | Nickname | Xiaohongshu ID | Followers | Tier | City | Category | Score | Status |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in show:
        lines.append(f"| {r['Library ID']} | [{r['Nickname']}]({r['Profile URL']}) | {r['Xiaohongshu ID']} | "
                     f"{int(r['Followers']):,} | {r['Tier']} | {r['City']} | {r['Category']} | "
                     f"{r['Score (/100)']} | {r['Status']} |")
    return "\n".join(lines)


CSS = """
:root{--red:#CB2D2E;--ink:#141414;--bg:#fff;--panel:#f6f3f3;--muted:#6b6161;--line:#e7dede;--yellow:#FAE94E;
--ok:#1f8a4c;--warn:#b26a00;--bad:#CB2D2E;--sans:"Inter Tight","Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root{--ink:#f3eeee;--bg:#121010;--panel:#1d1919;--muted:#a99f9f;--line:#332c2c;
--red:#e5484a;--ok:#4cc483;--warn:#f0a83a;--bad:#ff6b6b;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:28px max(16px,env(safe-area-inset-left,0px)) 56px;display:grid;gap:26px}
.tag{background:var(--red);color:#fff;font-weight:700;font-size:12px;letter-spacing:.08em;padding:3px 10px;border-radius:3px;width:max-content}
h1{font-size:clamp(28px,5vw,42px);font-weight:900;margin:6px 0}h1 mark{background:linear-gradient(transparent 60%,var(--yellow) 60%);color:inherit}
h2{font-size:19px;font-weight:900;margin:0 0 10px}.sub{color:var(--muted);margin:0;max-width:70ch}
.plats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.plat{padding:14px;border:1px solid var(--line);display:grid;gap:4px}.plat.on{border:2px solid var(--red)}
.plat b{font-size:16px}.plat span{font-size:13px;color:var(--muted)}.plat .n{font-size:28px;font-weight:900;color:var(--ink)}
.bar{display:flex;height:34px;border-radius:4px;overflow:hidden;font-size:12px;font-weight:700}
.bar div{display:grid;place-items:center;color:#fff;min-width:28px}
.s-Shortlist{background:var(--ok)}.s-Watch{background:var(--warn)}.s-Exclude{background:var(--bad)}.s-Reference{background:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:13px;margin-top:6px}.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.card{border:1px solid var(--line);padding:12px 14px;display:grid;gap:6px;align-content:start}
.card .hd{display:flex;justify-content:space-between;gap:8px;align-items:baseline}.card a{color:var(--ink);font-weight:700;font-size:16px;overflow-wrap:anywhere}
.score{font-weight:900;font-size:22px;font-variant-numeric:tabular-nums}.ids{font-size:12px;color:var(--muted);font-family:ui-monospace,monospace;overflow-wrap:anywhere}
.chips{display:flex;flex-wrap:wrap;gap:5px}.chip{font-size:12px;background:var(--panel);padding:1px 7px;border-radius:3px}.chip.t{background:var(--ink);color:var(--bg)}
.card p{margin:0;font-size:13px}.flag{color:var(--bad)}
.tablewrap{overflow-x:auto;border:1px solid var(--line)}table{border-collapse:collapse;width:100%;font-size:13px;min-width:860px}
th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}th{background:var(--panel);font-weight:700;white-space:nowrap}
td.num{font-variant-numeric:tabular-nums;text-align:right}.pill{font-size:11px;font-weight:700;color:#fff;padding:1px 7px;border-radius:99px;white-space:nowrap}
.dims{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:8px;font-size:13px}.dims div{background:var(--panel);padding:10px}
.add{background:var(--panel);padding:14px 16px;font-size:14px}.add code{font-size:13px}
.note{font-size:12px;color:var(--muted)}
"""


def build_html(rows):
    e = html.escape
    s = summary(rows)
    plat_cards = []
    for stem, (name, _, _) in PLATFORMS.items():
        n = s["platforms"].get(name, 0)
        label = "Main platform" if stem == "xiaohongshu" else ("Active" if n else "Not yet scanned")
        plat_cards.append(f'<div class="plat{" on" if n else ""}"><b>{e(name)}</b><span class="n">{n}</span><span>{label}</span></div>')
    total = max(s["total"], 1)
    bar = "".join(f'<div class="s-{k}" style="flex:{s["status"].get(k, 0)}">{s["status"].get(k, 0)}</div>'
                  for k in STATUSES if s["status"].get(k))
    legend = "".join(f'<span><i class="s-{k}"></i>{k}</span>' for k in STATUSES)

    def card(r):
        flags = r["Red Flags"] if r["Red Flags"] not in ("", "None") else ""
        return (f'<div class="card"><div class="hd"><a href="{e(r["Profile URL"])}" target="_blank" rel="noopener">{e(r["Nickname"])}</a>'
                f'<span class="score">{e(r["Score (/100)"])}</span></div>'
                f'<div class="ids">{e(r["Library ID"])} · Xiaohongshu ID {e(r["Xiaohongshu ID"])}<br>User ID {e(r["User ID"])}</div>'
                f'<div class="chips"><span class="chip t">{e(r["Tier"])}</span><span class="chip">{int(r["Followers"]):,} followers</span>'
                f'<span class="chip">{e(r["City"])}</span><span class="chip">{e(r["Category"])}</span></div>'
                f'<p>{e(r["Identity"])}. {e(r["Content Focus"])}.</p>'
                + (f'<p class="flag">⚠ {e(flags)}</p>' if flags else "") + "</div>")

    shortlist = "".join(card(r) for r in ranked(rows) if r["Status"] == "Shortlist")
    trs = "".join(
        f'<tr><td>{e(r["Library ID"])}</td><td><a href="{e(r["Profile URL"])}" target="_blank" rel="noopener">{e(r["Nickname"])}</a></td>'
        f'<td>{e(r["Xiaohongshu ID"])}</td><td class="ids">{e(r["User ID"])}</td><td class="num">{int(r["Followers"]):,}</td>'
        f'<td>{e(r["Tier"])}</td><td>{e(r["City"])}</td><td>{e(r["Category"])}</td><td class="num">{e(r["Score (/100)"])}</td>'
        f'<td><span class="pill s-{e(r["Status"])}">{e(r["Status"])}</span></td><td>{e(r["Red Flags"])}</td></tr>'
        for r in ranked(rows))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Creator Library</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;700;900&family=Noto+Sans+SC:wght@400;700&display=swap">
<style>{CSS}</style></head><body><div class="wrap">
<header><div class="tag">KNOWLEDGE BASE</div><h1>Creator <mark>Library</mark></h1>
<p class="sub">Every creator found with the tested search process (references/creator-finding.md), sorted by platform, scored and given a status.
Xiaohongshu comes first: it is the platform Chinese students search and trust most for study-abroad life. New creators are added as rows in creators/scouted/&lt;platform&gt;.csv.</p></header>
<section><h2>1 · Platform</h2><div class="plats">{''.join(plat_cards)}</div></section>
<section><h2>2 · Scanned creators by status ({s['total']})</h2><div class="bar">{bar}</div><div class="legend">{legend}</div></section>
<section><h2>3 · Shortlist</h2><div class="cards">{shortlist}</div></section>
<section><h2>4 · How the score works (/100)</h2><div class="dims">
<div><b>Fit</b><br>IP location and identity match the target</div><div><b>Size</b><br>Under 2k followers scores 5</div>
<div><b>Activity</b><br>Posted in the last few days</div><div><b>Authenticity</b><br>Real person, no matrix signs, few ads</div>
<div><b>Content</b><br>Everyday life in their own voice</div></div>
<p class="note">Each dimension 1–5; total × 4. Shortlist ≥ 88 and under 2k followers · Watch 72–87 or minor flags · Exclude = serious red flag · Reference = 2k+ benchmark.</p></section>
<section><h2>5 · All scanned creators</h2><div class="tablewrap"><table><thead><tr><th>ID</th><th>Nickname</th><th>Xiaohongshu ID</th><th>User ID</th><th>Followers</th>
<th>Tier</th><th>City</th><th>Category</th><th>Score</th><th>Status</th><th>Red flags</th></tr></thead><tbody>{trs}</tbody></table></div></section>
<section class="add"><b>Add a creator:</b> run <code>python tools/creator_library.py --next-id xiaohongshu</code>, add a row to <code>creators/scouted/xiaohongshu.csv</code>,
then <code>python tools/creator_library.py --check --html</code>.</section>
<p class="note">Follower counts were recorded at scan time; check them again before contacting a creator. Generated by tools/creator_library.py.</p>
</div></body></html>
"""


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--status", choices=STATUSES)
    p.add_argument("--check", action="store_true", help="validate every row; exit 1 on problems")
    p.add_argument("--html", action="store_true", help=f"rebuild {HTML_OUT.relative_to(ROOT)}")
    p.add_argument("--next-id", choices=list(PLATFORMS), help="print the next free Library ID")
    args = p.parse_args(argv)
    rows = load()
    if args.next_id:
        print(next_id(rows, args.next_id))
        return 0
    if args.check:
        problems = check(rows)
        for msg in problems:
            print("✗", msg)
        if problems:
            return 1
        print(f"✓ {len(rows)} creators valid")
    if args.html:
        HTML_OUT.write_text(build_html(rows), encoding="utf-8")
        print(f"Saved {HTML_OUT.relative_to(ROOT)}")
    if not (args.check or args.html):
        print(to_markdown(rows, args.status))
    return 0


if __name__ == "__main__":
    sys.exit(main())
