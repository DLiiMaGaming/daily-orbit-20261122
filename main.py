#!/usr/bin/env python3
"""Entry program for the Daily Orbit front page (news-image-20261122).

The entry image is entry.png, shipped beside this file. This program
copies it to the output directory as entry.png, which is what the
competition harness expects. Standard library only.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
import sys


def find_image():
    """Locate entry.png beside this file, falling back to /bot/entry.png."""
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in (os.path.join(here, "entry.png"), "/bot/entry.png"):
        if os.path.isfile(candidate):
            return candidate
    return None


def main():
    src = find_image()
    if src is None:
        print("entry.png not found beside main.py or at /bot/entry.png",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # copyfile preserves the bytes exactly, so the output is the entry.
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
