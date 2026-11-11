"""Local web app for the Medibank China social media agent.

Runs on your own computer: a small web server plus a page in your browser. The page talks to
this server, and the server calls the Claude API with the same skills and knowledge base the
Claude Code plugin uses. On top of that, Claude can run the repository's tools directly:

  * search_creators   - search the scouted creator library (creators/scouted/*.csv)
  * compliance_check  - keyword compliance scan (tools/compliance_scan.py)
  * make_post         - write a full post and render image cards (tools/make_post.py)
  * edit_video        - cut a short video from clips on this computer (tools/video_edit.py, needs ffmpeg)
  * probe_video       - read the length and size of a clip
  * web_search        - server-side web search, for trends

Start it:
    python -m social_agent web              # opens http://localhost:8787
    python -m social_agent web --port 9000 --no-browser

API key: paste it in the page (kept in memory; tick "remember" to save it in
~/.medibank-social-agent/config.json, readable only by you), or set ANTHROPIC_API_KEY before starting.
"""

import json
import os
import shutil
import sys
import threading
import traceback
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from . import cli

ROOT = cli.ROOT
OUT_DIR = ROOT / "outputs" / "web"
CONFIG = Path.home() / ".medibank-social-agent" / "config.json"
PAGE = Path(__file__).with_name("web_page.html")
MAX_TOOL_ROUNDS = 12

sys.path.insert(0, str(ROOT / "tools"))
import compliance_scan  # noqa: E402
import creator_library  # noqa: E402

RUNNER_NOTE = (
    "You are running inside the Medibank social agent's local web app. You can call these tools "
    "yourself: search_creators (the real scouted creator library), compliance_check, make_post "
    "(renders finished image cards and post.md), edit_video and probe_video (ffmpeg on the user's "
    "computer; clips are local file paths the user gives you), and web_search. Prefer doing the work "
    "with a tool over describing how to do it: when asked for creators, call search_creators and "
    "recommend named creators from the results; when asked for a post, call make_post with a full "
    "spec. Live searching inside the Xiaohongshu app is not available here; say so if asked, and "
    "offer the library plus the tested search method in references/creator-finding.md. Reply in the "
    "user's language. Sub-skills referenced by name are the skills/<name>/SKILL.md files above."
)

PLATFORM_ENUM = cli.PLATFORMS

TOOLS = [
    {
        "name": "search_creators",
        "description": (
            "Search the scouted creator library (real accounts found by hand, view only). Returns "
            "matching creators with followers, city, identity, content focus, score /100, status and "
            "profile URL, best score first. Use it whenever the user wants creators to work with."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["any", "Shortlist", "Watch", "Exclude", "Reference"],
                           "description": "Library status; 'any' for all."},
                "max_followers": {"type": "integer", "description": "Upper follower limit; 0 for no limit."},
                "city": {"type": "string", "description": "City text to match, e.g. Sydney; empty for any."},
                "keyword": {"type": "string",
                            "description": "Text to match in identity, content focus or category; empty for any."},
                "limit": {"type": "integer", "description": "Maximum rows to return (1-30)."},
            },
            "required": ["status", "max_followers", "city", "keyword", "limit"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "compliance_check",
        "description": "Run the keyword compliance scanner on a draft. Returns a green/yellow/red verdict with each hit and its rule.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The full draft text."},
                "platform": {"type": "string", "enum": PLATFORM_ENUM},
            },
            "required": ["text", "platform"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "make_post",
        "description": (
            "Turn a finished post into ready-to-publish files: renders the cover and content cards as "
            "PNG in Medibank colours, writes post.md and runs the compliance scan. Spec fields: platform, "
            "account ('brand' or 'creator'), pillar, title, titles (list), body, hashtags (list), "
            "cover {headline, sub}, cards [{heading, body}], end {line, next, question}, evidence (list "
            "of E- row IDs). Returns the verdict and the image URLs to show the user."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "spec": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": PLATFORM_ENUM},
                        "account": {"type": "string", "enum": ["brand", "creator"]},
                        "pillar": {"type": "string"},
                        "title": {"type": "string"},
                        "titles": {"type": "array", "items": {"type": "string"}},
                        "body": {"type": "string"},
                        "hashtags": {"type": "array", "items": {"type": "string"}},
                        "cover": {"type": "object"},
                        "cards": {"type": "array", "items": {"type": "object"}},
                        "end": {"type": "object"},
                        "evidence": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["platform", "title", "body"],
                }
            },
            "required": ["spec"],
        },
    },
    {
        "name": "edit_video",
        "description": (
            "Cut a short vertical video with ffmpeg on this computer. Plan fields: platform (douyin, "
            "wechat-channels, xiaohongshu), clips [{file, start, end}] with absolute local paths, optional "
            "subtitles (path to .srt), title {headline, sub, seconds}, end {next, line, question, seconds}, "
            "music (path or null), grade (true for the Medibank colour tone). Returns the video URL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Short file name for the output, no extension."},
                "plan": {"type": "object"},
            },
            "required": ["name", "plan"],
        },
    },
    {
        "name": "probe_video",
        "description": "Read the duration and size of a local video clip before planning an edit.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Absolute path of the clip."}},
            "required": ["path"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 10},
]


# ---------------------------------------------------------------- tool implementations

def _int(row, key):
    try:
        return int(str(row.get(key, "0")).replace(",", "") or 0)
    except ValueError:
        return 0


def tool_search_creators(status="any", max_followers=0, city="", keyword="", limit=10):
    rows = creator_library.load()
    out = []
    for r in rows:
        if status != "any" and r.get("Status") != status:
            continue
        if max_followers and _int(r, "Followers") > max_followers:
            continue
        if city and city.lower() not in r.get("City", "").lower():
            continue
        hay = " ".join(r.get(k, "") for k in ("Identity", "Content Focus", "Category", "Source Keyword")).lower()
        if keyword and keyword.lower() not in hay:
            continue
        out.append(r)
    out.sort(key=lambda r: _int(r, "Score (/100)"), reverse=True)
    limit = max(1, min(int(limit or 10), 30))
    keep = ["Library ID", "Platform", "Nickname", "Followers", "Tier", "City", "Identity", "Content Focus",
            "Ad / Collab Signals", "Red Flags", "Score (/100)", "Status", "Profile URL"]
    return {"total_in_library": len(rows), "matches": len(out),
            "creators": [{k: r.get(k, "") for k in keep} for r in out[:limit]]}


def tool_compliance_check(text, platform):
    worst, hits = compliance_scan.scan(text, platform=platform)
    return {"verdict": compliance_scan.VERDICT[worst], "report": compliance_scan.format_report(worst, hits, platform)}


def _url(path):
    return "/outputs/" + path.relative_to(OUT_DIR).as_posix()


def tool_make_post(spec):
    import make_post

    for key in ("platform", "title", "body"):
        if not spec.get(key):
            return {"error": f"spec is missing '{key}'"}
    folder = OUT_DIR / "posts" / make_post.slugify(spec["title"])
    worst, images = make_post.build(spec, folder)
    return {"verdict": compliance_scan.VERDICT[worst],
            "compliance": (folder / "compliance.txt").read_text(encoding="utf-8"),
            "post_md": _url(folder / "post.md"),
            "images": [_url(folder / n) for n in images]}


def tool_edit_video(name, plan):
    import video_edit

    if not shutil.which("ffmpeg"):
        return {"error": "ffmpeg is not installed on this computer (Mac: brew install ffmpeg; Windows: winget install ffmpeg)."}
    if not plan.get("clips"):
        return {"error": "The plan has no clips."}
    missing = [c.get("file") for c in plan["clips"] if not Path(str(c.get("file", ""))).is_file()]
    if missing:
        return {"error": "These clip files were not found: " + ", ".join(map(str, missing))}
    folder = OUT_DIR / "videos"
    folder.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch for ch in name if ch.isalnum() or ch in "-_一-鿿") or "video"
    plan_path = folder / f"{safe}.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    out = folder / f"{safe}.mp4"
    try:
        video_edit.main([str(plan_path), "--out", str(out)])
    except SystemExit as e:
        return {"error": f"Video render failed: {e}"}
    info = video_edit.probe(out)
    return {"video": _url(out), "seconds": round(info["duration"], 1), "size": f"{info['width']}x{info['height']}"}


def tool_probe_video(path):
    import video_edit

    if not shutil.which("ffprobe"):
        return {"error": "ffmpeg/ffprobe is not installed on this computer."}
    if not Path(path).is_file():
        return {"error": f"File not found: {path}"}
    return video_edit.probe(path)


TOOL_FUNCS = {
    "search_creators": tool_search_creators,
    "compliance_check": tool_compliance_check,
    "make_post": tool_make_post,
    "edit_video": tool_edit_video,
    "probe_video": tool_probe_video,
}


def run_tool(name, args):
    func = TOOL_FUNCS.get(name)
    if not func:
        return {"error": f"unknown tool {name}"}, True
    try:
        return func(**args), False
    except Exception as e:  # report tool failures back to Claude instead of crashing the turn
        traceback.print_exc()
        return {"error": f"{type(e).__name__}: {e}"}, True


# ---------------------------------------------------------------- agent session

class Agent:
    def __init__(self):
        self.lock = threading.Lock()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY") or self._saved_key()
        self.messages = []
        self.system = None

    @staticmethod
    def _saved_key():
        try:
            return json.loads(CONFIG.read_text(encoding="utf-8")).get("api_key")
        except (OSError, ValueError):
            return None

    def set_key(self, key, remember):
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        client.models.retrieve(cli.MODEL)  # raises AuthenticationError on a bad key
        self.api_key = key
        if remember:
            CONFIG.parent.mkdir(parents=True, exist_ok=True)
            CONFIG.write_text(json.dumps({"api_key": key}), encoding="utf-8")
            try:
                os.chmod(CONFIG, 0o600)
            except OSError:
                pass

    def forget_key(self):
        self.api_key = None
        try:
            CONFIG.unlink()
        except OSError:
            pass

    def reset(self):
        self.messages = []

    def _call(self, client):
        with client.beta.messages.stream(
            model=cli.MODEL,
            max_tokens=32000,
            system=self.system,
            messages=self.messages,
            tools=TOOLS,
            output_config={"effort": "medium"},
            cache_control={"type": "ephemeral"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            return stream.get_final_message()

    def chat(self, user_text):
        import anthropic

        if not self.api_key:
            return {"error": "No API key yet. Paste your Anthropic API key at the top of the page, "
                             "or use the Demo tabs (creators, compliance scan, sample post) which need no key."}
        with self.lock:
            if self.system is None:
                self.system = cli.build_system_prompt(RUNNER_NOTE)
            client = anthropic.Anthropic(api_key=self.api_key)
            start = len(self.messages)
            self.messages.append({"role": "user", "content": user_text})
            steps, files, texts = [], [], []
            try:
                for _ in range(MAX_TOOL_ROUNDS):
                    final = self._call(client)
                    self.messages.append({"role": "assistant", "content": final.content})
                    texts += [b.text for b in final.content if b.type == "text"]
                    if final.stop_reason == "pause_turn":
                        continue  # long server-side search; resend and it resumes
                    if final.stop_reason == "refusal":
                        texts.append("[The model declined this request. Rephrase it or check it with Legal.]")
                        break
                    if final.stop_reason != "tool_use":
                        break
                    results = []
                    for block in final.content:
                        if block.type != "tool_use":
                            continue
                        args = block.input if isinstance(block.input, dict) else {}
                        result, is_error = run_tool(block.name, args)
                        steps.append({"tool": block.name, "error": is_error or "error" in result})
                        files += [{"type": "image", "url": u} for u in result.get("images", [])]
                        if result.get("video"):
                            files.append({"type": "video", "url": result["video"]})
                        if result.get("post_md"):
                            files.append({"type": "file", "url": result["post_md"], "label": "post.md"})
                        results.append({"type": "tool_result", "tool_use_id": block.id,
                                        "content": json.dumps(result, ensure_ascii=False), "is_error": is_error})
                    self.messages.append({"role": "user", "content": results})
                else:
                    texts.append("[Stopped after many tool steps. Ask me to continue if needed.]")
            except anthropic.APIError as e:
                del self.messages[start:]  # drop the failed turn so the next one starts clean
                if isinstance(e, anthropic.AuthenticationError):
                    return {"error": "The API key was rejected. Paste a valid key at the top of the page."}
                if isinstance(e, anthropic.RateLimitError):
                    return {"error": "Rate limited by the API. Wait a minute and try again."}
                if isinstance(e, anthropic.APIConnectionError):
                    return {"error": "Could not reach the Claude API. Check the internet connection."}
                if isinstance(e, anthropic.APIStatusError):
                    return {"error": f"API error {e.status_code}: {e.message}"}
                return {"error": f"API error: {e}"}
            reply = "\n\n".join(t for t in texts if t.strip())
            worst, hits = compliance_scan.scan(reply) if reply else (0, [])
            return {"reply": reply, "steps": steps, "files": files,
                    "scan": compliance_scan.VERDICT[worst] if reply else None}


AGENT = Agent()


# ---------------------------------------------------------------- HTTP server

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass

    def _json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return {}

    def _local_only(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        if host not in ("localhost", "127.0.0.1"):
            self._json({"error": "local access only"}, 403)
            return False
        return True

    def do_GET(self):
        if not self._local_only():
            return
        path = unquote(urlparse(self.path).path)
        if path == "/":
            data = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif path == "/api/status":
            key = AGENT.api_key
            self._json({"has_key": bool(key), "key_hint": f"…{key[-4:]}" if key else "",
                        "model": cli.MODEL, "ffmpeg": bool(shutil.which("ffmpeg")),
                        "creators": len(creator_library.load()), "today": date.today().isoformat()})
        elif path.startswith("/outputs/"):
            target = (OUT_DIR / path[len("/outputs/"):]).resolve()
            if OUT_DIR.resolve() not in target.parents or not target.is_file():
                self.send_error(404)
                return
            types = {".png": "image/png", ".mp4": "video/mp4", ".md": "text/plain; charset=utf-8",
                     ".txt": "text/plain; charset=utf-8", ".json": "application/json"}
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", types.get(target.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def do_POST(self):
        if not self._local_only():
            return
        path = urlparse(self.path).path
        body = self._body()
        if path == "/api/key":
            import anthropic
            key = (body.get("key") or "").strip()
            if not key:
                return self._json({"error": "Paste a key first."}, 400)
            try:
                AGENT.set_key(key, bool(body.get("remember")))
            except anthropic.AuthenticationError:
                return self._json({"error": "That key was rejected by the Claude API."}, 400)
            except anthropic.APIConnectionError:
                return self._json({"error": "Could not reach the Claude API to check the key."}, 502)
            except anthropic.APIStatusError as e:
                return self._json({"error": f"API error {e.status_code}: {e.message}"}, 502)
            return self._json({"ok": True, "key_hint": f"…{key[-4:]}"})
        if path == "/api/forget-key":
            AGENT.forget_key()
            return self._json({"ok": True})
        if path == "/api/reset":
            AGENT.reset()
            return self._json({"ok": True})
        if path == "/api/demo/creators":
            return self._json(tool_search_creators(
                body.get("status") or "any", int(body.get("max_followers") or 0),
                body.get("city") or "", body.get("keyword") or "", int(body.get("limit") or 10)))
        if path == "/api/demo/scan":
            text = (body.get("text") or "").strip()
            if not text:
                return self._json({"error": "Paste a draft first."}, 400)
            return self._json(tool_compliance_check(text, body.get("platform") or "xiaohongshu"))
        if path == "/api/demo/post":
            spec = json.loads((ROOT / "examples" / "post_spec.json").read_text(encoding="utf-8"))
            result = tool_make_post(spec)
            result["title"] = spec["title"]
            result["body"] = spec["body"]
            return self._json(result)
        if path == "/api/chat":
            text = (body.get("message") or "").strip()
            if not text:
                return self._json({"error": "Type a request first."}, 400)
            return self._json(AGENT.chat(text))
        self.send_error(404)


def serve(port=8787, open_browser=True):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"Medibank social agent is running at {url}  (Ctrl-C to stop)")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0
