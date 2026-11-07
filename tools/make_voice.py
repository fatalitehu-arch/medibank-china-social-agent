#!/usr/bin/env python3
"""Voice-over for a motion_video storyboard: one mp3 per spoken line ("say"), Microsoft Edge neural voices.

Needs internet and `pip install edge-tts`. Run it on a computer that can reach speech.platform.bing.com
(some cloud sandboxes can't).

Usage:
    python tools/make_voice.py examples/motion_storyboard.json                    # -> voice/xiaoxiao/01.mp3 ...
    python tools/make_voice.py board.json --voice zh-CN-YunxiNeural --name yunxi --rate +8%
Good Mandarin voices: zh-CN-XiaoxiaoNeural (warm female), zh-CN-YunxiNeural (young male),
zh-CN-XiaoyiNeural (lively female), zh-CN-YunjianNeural (deep male).
"""

import argparse
import asyncio
import json
from pathlib import Path


def lines(board):
    return [s.replace("{", "").replace("}", "") for sc in board["scenes"] for s in sc.get("say", [])]


async def make(texts, voice, rate, folder):
    import edge_tts
    folder.mkdir(parents=True, exist_ok=True)
    for i, text in enumerate(texts, 1):
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, voice, rate=rate).save(str(folder / f"{i:02d}.mp3"))
                break
            except Exception as err:  # network hiccups
                if attempt == 3:
                    raise
                print("retry", i, err)
                await asyncio.sleep(2 * (attempt + 1))
        print(f"{i:02d} {text}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("board")
    p.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    p.add_argument("--name", default="xiaoxiao", help="sub-folder name under voice/")
    p.add_argument("--rate", default="+8%")
    args = p.parse_args(argv)
    board_path = Path(args.board)
    board = json.loads(board_path.read_text(encoding="utf-8"))
    folder = board_path.resolve().parent / "voice" / args.name
    asyncio.run(make(lines(board), args.voice, args.rate, folder))
    print(f"Wrote {folder}. Set \"voice\": {{\"dir\": \"voice/{args.name}\"}} in the storyboard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
