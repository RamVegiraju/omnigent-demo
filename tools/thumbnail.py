"""Thumbnail generation tool for the `marketer` sub-agent.

Resolved by Omnigent as the dotted callable ``tools.thumbnail.generate_thumbnail``
(see agents/marketer/config.yaml). Omnigent puts the launch CWD on sys.path[0],
so run the demo from inside this project directory for the import to resolve.

Spend guards (image generation is the expensive OpenAI call and is NOT tracked
by Omnigent's cost_budget policy, so it is bounded here):
  - a hard per-process cap on how many images may be generated (_MAX_IMAGES);
  - bounded retry-with-backoff on 429s (honors Retry-After) so a transient
    rate limit can't turn into an unbounded retry storm.
"""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path

from openai import OpenAI, RateLimitError

# YouTube thumbnails are 16:9 (1280x720). gpt-image-1's nearest landscape size
# is 1536x1024 (3:2); generate at that and crop to 16:9 if you want exact specs.
_IMAGE_MODEL = "gpt-image-1"
_IMAGE_SIZE = "1536x1024"

# --- Spend / rate guards -------------------------------------------------
_MAX_IMAGES = 2          # hard cap on image generations per process (per run)
_MAX_RETRIES = 3         # attempts on a 429 before giving up (no infinite loop)
_BACKOFF_BASE = 5.0      # seconds; exponential base for backoff
_BACKOFF_CAP = 30.0      # seconds; never wait longer than this between attempts

_images_generated = 0    # module-level counter, per process


def _retry_after_seconds(err: RateLimitError) -> float | None:
    """Return the Retry-After header (seconds) from a 429, if the server sent one."""
    resp = getattr(err, "response", None)
    if resp is None:
        return None
    val = resp.headers.get("retry-after")
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def generate_thumbnail(prompt: str, out_path: str = "marketing/thumbnail.png") -> str:
    """Generate a YouTube thumbnail PNG from a text prompt and save it to disk.

    Uses OpenAI's image model. Authenticates from OPENAI_API_KEY. The key is
    passed explicitly and no base_url is set, so image generation always hits
    api.openai.com even if OPENAI_BASE_URL points elsewhere (e.g. a Databricks
    gateway that doesn't serve image models).

    Bounded by a per-run image cap and bounded retry/backoff to protect the
    OpenAI budget. Returns a human-readable status string (never raises).
    """
    global _images_generated

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY is not set; cannot generate the thumbnail."

    # Hard spend guard: refuse once the per-run cap is reached. This is what
    # stops a misbehaving agent (or a retry storm) from running up image spend.
    if _images_generated >= _MAX_IMAGES:
        return (
            f"ERROR: image-generation cap reached ({_MAX_IMAGES} per run). Refusing "
            f"to spend more on OpenAI image generation. Reuse the existing "
            f"marketing/thumbnail.png, or restart the session to reset the cap."
        )

    client = OpenAI(api_key=api_key)

    result = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            result = client.images.generate(
                model=_IMAGE_MODEL,
                prompt=prompt,
                size=_IMAGE_SIZE,
                n=1,
            )
            break
        except RateLimitError as exc:
            if attempt == _MAX_RETRIES:
                return (
                    f"ERROR: OpenAI rate limit (429) persisted after {_MAX_RETRIES} "
                    f"attempts. STOP retrying — let the per-minute token window reset "
                    f"and try again later (raising the org TPM limit avoids this). "
                    f"Detail: {str(exc)[:160]}"
                )
            wait = _retry_after_seconds(exc) or min(
                _BACKOFF_CAP, _BACKOFF_BASE * (2 ** (attempt - 1))
            )
            time.sleep(wait)
        except Exception as exc:  # any other API error -> clean tool error, no retry
            return f"ERROR generating image: {type(exc).__name__}: {str(exc)[:160]}"

    if result is None or not result.data or not result.data[0].b64_json:
        return "ERROR: image API returned no image data."

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(result.data[0].b64_json))
    _images_generated += 1
    return (
        f"Thumbnail saved to {out.resolve()} ({_IMAGE_SIZE}, 3:2 — crop to "
        f"1280x720 for exact YouTube 16:9). "
        f"[{_images_generated}/{_MAX_IMAGES} image(s) used this run]"
    )
