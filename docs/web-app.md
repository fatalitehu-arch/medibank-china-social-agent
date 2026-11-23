# Local web app

A browser version of the agent for people who don't use Claude Code. It runs on your own
computer and uses the same skills, knowledge base and tools as the plugin.

## Start it

Needs **Python 3.10 or newer**. The Python that comes with macOS (3.9) is too old: install
Python 3.12 from https://www.python.org/downloads/ first.


* **Mac:** double-click `start-web-mac.command`. The first time, macOS says the file was "Not
  Opened": click **Done** (not Move to Bin), open **System Settings → Privacy & Security**, scroll
  down, click **Open Anyway** next to the file name, enter your password and click **Open Anyway**
  again. After that a double-click is enough.
* **Windows:** double-click `start-web-windows.bat`.
* **Any system:** `python3.12 -m pip install -r requirements.txt`, then `python3.12 -m social_agent web`.

The page opens at http://localhost:8787. Only this computer can reach it.

The page has four tabs:

* **How to use** (opens first): what the agent does, how to use it here with or without an API
  key, better ways to use it (Claude Code, Claude.ai Project, Codex, command line), and how to
  edit it or move it to Medibank's own private GitHub repository.
* **Overview**: the welcome page, how we find creators, and the creator library (`portfolio.html`).
* **Agent**: the chat (needs an API key).
* **Demo**: creator search, compliance scan, sample post and sample video, with no key.

## API key

The app calls the **Claude API** (Anthropic), so it needs an Anthropic API key. This is not a
Claude.ai or Claude Code subscription: create the key at https://console.anthropic.com
(Settings → API keys) and add billing there. Usage is charged to whoever owns the key.

* Paste the key in the bar at the top of the page and click **Connect**. It is checked once and
  kept in memory until you close the app.
* Tick **remember on this computer** to save it in `~/.medibank-social-agent/config.json`
  (readable only by your user account). **Forget key** deletes it.
* Or set `ANTHROPIC_API_KEY` before starting; the app uses it automatically.

For a demo, connect your own key; afterwards click **Forget key**, and the next person connects theirs.

## What it can do

| Ask for | What happens |
|---|---|
| Creators to work with | Searches the scouted creator library (`creators/scouted/`) and recommends named creators |
| A post | Writes the full post and renders the image cards in Medibank colours (`outputs/web/posts/`) |
| A compliance check | Runs the keyword scanner, then reviews the draft against the rules |
| A content plan, brief, comment replies | Uses the matching sub-skill |
| Trends | Searches the web |
| A short video | Cuts your clips with ffmpeg (give the full file paths; needs ffmpeg installed) |

Live searching inside the Xiaohongshu app is not built in yet: the app recommends from the
library and explains the tested search method (`references/creator-finding.md`).
