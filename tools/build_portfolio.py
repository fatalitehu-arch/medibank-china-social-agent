"""Build portfolio.html: one self-contained page that switches between the welcome page,
the creator-finding process and the creator library (tabs at the top).

Run after tools/build_welcome.py:  python tools/build_portfolio.py
"""
import base64
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "portfolio.html"
REPO = "https://github.com/fatalitehu-arch/medibank-china-social-agent/blob/main/"
SWITCH = "onclick=\"parent.postMessage('tab:{0}','*');return false;\""

TABS = [  # (hash, label, file)
    ("portfolio", "Content portfolio", ROOT / "welcome.html"),
    ("find", "How we find creators", ROOT / "assets" / "creator-finding" / "process.html"),
    ("library", "Creator library", ROOT / "creators" / "scouted" / "library.html"),
]


def inline_images(text, folder):
    def repl(m):
        f = folder / m.group(1)
        if not f.exists():
            return m.group(0)
        kind = "png" if f.suffix == ".png" else "jpeg"
        return 'src="data:image/%s;base64,%s"' % (kind, base64.b64encode(f.read_bytes()).decode())
    return re.sub(r'src="([^":]+\.(?:jpg|jpeg|png))"', repl, text)


def fix_links(text):
    text = re.sub(r'href="[^"]*library\.html"', 'href="#library" ' + SWITCH.format("library"), text)
    text = re.sub(r'href="[^"]*process\.html"', 'href="#find" ' + SWITCH.format("find"), text)
    text = re.sub(r'href="(?:\.\./)*(references/[^"]+\.md)"', lambda m: 'href="%s%s" target="_blank" rel="noopener"' % (REPO, m.group(1)), text)
    # other external links open in a new tab instead of inside the frame
    return re.sub(r'<a (?![^>]*target=)([^>]*href="https?://)', r'<a target="_blank" rel="noopener" \1', text)


def page(path):
    return fix_links(inline_images(path.read_text(encoding="utf-8"), path.parent))


SHELL = """<title>Project BRIDGE Agent</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: one thin tab bar on top, the chosen page fills the rest of the screen */
:root { --bg: #ffffff; --ink: #141414; --muted: #6b6161; --line: #e7dede; --red: #CB2D2E; --on-red: #ffffff;
  --sans: "Inter Tight", "Inter", system-ui, -apple-system, "Segoe UI", sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #121010; --ink: #f3eeee; --muted: #a99f9f; --line: #332c2c; --red: #e5484a; color-scheme: dark } }
:root[data-theme="dark"] { --bg: #121010; --ink: #f3eeee; --muted: #a99f9f; --line: #332c2c; --red: #e5484a; color-scheme: dark }
html, body { height: 100%; }
body { background: var(--bg); color: var(--ink); font-family: var(--sans); display: flex; flex-direction: column; }
.bar { display: flex; align-items: center; gap: 6px 16px; flex-wrap: wrap; border-bottom: 1px solid var(--line);
  padding-block: 8px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.brand { font-weight: 800; font-size: 15px; letter-spacing: .01em; }
.brand span { color: var(--red); }
.tabs { display: flex; gap: 6px; flex-wrap: wrap; }
.tabs button { font: 600 14px/1 var(--sans); color: var(--ink); background: transparent; border: 1px solid var(--line);
  border-radius: 99px; padding: 8px 14px; cursor: pointer; }
.tabs button:hover { border-color: var(--red); }
.tabs button[aria-selected="true"] { background: var(--red); border-color: var(--red); color: var(--on-red); }
.tabs button:focus-visible { outline: 2px solid var(--red); outline-offset: 2px; }
.frames { flex: 1; min-height: 0; position: relative; }
iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; background: var(--bg); }
@media (max-width: 560px) { .brand { width: 100%; } .tabs button { padding: 7px 10px; font-size: 13px; } }
</style>
<div class="bar">
  <div class="brand">Project BRIDGE <span>·</span> Medibank social agent</div>
  <div class="tabs" role="tablist">__BUTTONS__</div>
</div>
<div class="frames">__FRAMES__</div>
<script>
(function () {
  var ids = __IDS__;
  function show(id) {
    if (ids.indexOf(id) < 0) id = ids[0];
    ids.forEach(function (k) {
      document.getElementById("f-" + k).hidden = k !== id;
      document.getElementById("t-" + k).setAttribute("aria-selected", k === id ? "true" : "false");
    });
  }
  function go(id) { if (location.hash !== "#" + id) location.hash = id; else show(id); }
  ids.forEach(function (k) { document.getElementById("t-" + k).addEventListener("click", function () { go(k); }); });
  window.addEventListener("hashchange", function () { show(location.hash.slice(1)); });
  window.addEventListener("message", function (e) { if (typeof e.data === "string" && e.data.indexOf("tab:") === 0) go(e.data.slice(4)); });
  show(location.hash.slice(1));
})();
</script>
"""


def render():
    buttons = "".join('<button type="button" role="tab" id="t-%s">%s</button>' % (k, label) for k, label, _ in TABS)
    frames = "".join('<iframe id="f-%s" title="%s" srcdoc="%s"%s></iframe>' % (k, label, html.escape(page(p), quote=True),
                                                                             "" if i == 0 else " hidden")
                     for i, (k, label, p) in enumerate(TABS))
    ids = "[" + ",".join('"%s"' % k for k, _, _ in TABS) + "]"
    return SHELL.replace("__BUTTONS__", buttons).replace("__FRAMES__", frames).replace("__IDS__", ids)


def main():
    OUT.write_text(render(), encoding="utf-8")
    print("Wrote", OUT.name, round(OUT.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
