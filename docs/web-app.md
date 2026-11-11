# Local web app

A browser version of the agent for people who don't use Claude Code. It runs on your own
computer and uses the same skills, knowledge base and tools as the plugin.

## Start it

* **Mac:** double-click `start-web-mac.command` (first time: right-click → Open, because macOS
  blocks scripts from unknown developers).
* **Windows:** double-click `start-web-windows.bat`.
* **Any system:** `pip install -r requirements.txt`, then `python -m social_agent web`.

The page opens at http://localhost:8787. Only this computer can reach it.

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
