#!/usr/bin/env python3
"""Deterministically render the YouTube thumbnail via gpt-image-1.

DECOUPLED from the OpenAI agent on purpose. The marketer (gpt-5.5 on the
openai-agents harness) cannot reliably emit a function_call for an image tool —
the OpenAI Agents SDK crashes with "function_call provided without its required
reasoning item (400)" before the tool ever runs. So image rendering is moved
OUT of the agent loop into this plain script, which the reliable claude-sdk
orchestrator invokes via shell after the marketer writes the prompt.

Reads the image prompt from marketing/thumbnail_prompt.txt (or --prompt) and
writes marketing/thumbnail.png. Reuses tools/thumbnail.py (cap + backoff).

Run from the project root so `tools` imports, with OPENAI_API_KEY set:
    python make_thumbnail.py
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# --- Environment self-heal (MUST run before importing openai via tools.thumbnail)
# Omnigent is installed under Python 3.14, but this script may run under a
# different system python (e.g. 3.12). If omnigent's 3.14 site-packages leak in
# via PYTHONPATH, the 3.12 interpreter tries to load 3.14-compiled extensions
# (e.g. jiter's `jiter.jiter`, a dependency of openai) and crashes with
# ModuleNotFoundError before any image call. Strip those contaminating entries
# so the script always uses THIS interpreter's own packages.
_bad = [p for p in sys.path if "python3.14" in p or "Cellar/omnigent" in p]
for _p in _bad:
    sys.path.remove(_p)
os.environ.pop("PYTHONPATH", None)

from tools.thumbnail import generate_thumbnail

DEFAULT_PROMPT_FILE = "marketing/thumbnail_prompt.txt"
DEFAULT_OUT = "marketing/thumbnail.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the YouTube thumbnail via gpt-image-1.")
    ap.add_argument("--prompt", help="Image prompt text (overrides --prompt-file).")
    ap.add_argument("--prompt-file", default=DEFAULT_PROMPT_FILE,
                    help=f"File holding the image prompt (default: {DEFAULT_PROMPT_FILE}).")
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help=f"Output PNG path (default: {DEFAULT_OUT}).")
    args = ap.parse_args()

    prompt = (args.prompt or "").strip()
    if not prompt:
        pf = Path(args.prompt_file)
        if not pf.exists():
            print(f"ERROR: no --prompt given and prompt file '{pf}' not found.", file=sys.stderr)
            return 2
        prompt = pf.read_text(encoding="utf-8").strip()
    if not prompt:
        print("ERROR: the image prompt is empty.", file=sys.stderr)
        return 2

    result = generate_thumbnail(prompt, out_path=args.out)
    print(result)
    # generate_thumbnail returns a human-readable string; treat ERROR-prefixed
    # results as a non-zero exit so the orchestrator's shell call sees the failure.
    return 1 if result.startswith("ERROR") else 0


if __name__ == "__main__":
    raise SystemExit(main())
