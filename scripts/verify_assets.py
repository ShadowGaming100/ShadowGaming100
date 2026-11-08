#!/usr/bin/env python3
"""Validate README-local assets and enforce smooth, infinite-looping GIFs."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
LOOPING_GIFS = [
    (ROOT / "assets" / "hero.dark.gif", 150),
    (ROOT / "assets" / "hero.light.gif", 150),
    (ROOT / "assets" / "typing.dark.gif", 700),
    (ROOT / "assets" / "typing.light.gif", 700),
    (ROOT / "assets" / "terminal.gif", 1200),
    (ROOT / "assets" / "featured.dark.gif", 150),
    (ROOT / "assets" / "featured.light.gif", 150),
    (ROOT / "assets" / "snake.dark.gif", 150),
    (ROOT / "assets" / "snake.light.gif", 150),
]
IMAGE_RE = re.compile(
    r"\./(?:assets|profile-3d-contrib)/[A-Za-z0-9_./-]+\.(?:svg|gif|png|webp)",
    re.IGNORECASE,
)


def verify_gif_loop_forever(path, max_duration=150):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to validate generated GIFs") from exc

    data = path.read_bytes()
    if not data.startswith((b"GIF87a", b"GIF89a")):
        raise RuntimeError(f"Invalid GIF: {path}")
    if b"NETSCAPE2.0" not in data:
        raise RuntimeError(f"GIF does not loop forever: {path}")

    with Image.open(path) as image:
        if image.info.get("loop") != 0:
            raise RuntimeError(f"GIF is not configured for infinite looping: {path}")
        if not getattr(image, "is_animated", False) or image.n_frames < 20:
            raise RuntimeError(f"GIF is not a animated sequence: {path}")
        durations = []
        for frame in range(image.n_frames):
            image.seek(frame)
            durations.append(image.info.get("duration", 0))
        if min(durations) < 30 or max(durations) > max_duration:
            raise RuntimeError(
                f"GIF frame timing is inconsistent: {path} "
                f"({min(durations)}–{max(durations)}ms)"
            )


def main():
    if not README.is_file():
        raise RuntimeError("README.md is missing")

    for gif, max_duration in LOOPING_GIFS:
        if not gif.is_file() or gif.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty animated GIF: {gif.relative_to(ROOT)}")
        verify_gif_loop_forever(gif, max_duration=max_duration)
        print(f"Looping GIF verified: {gif.relative_to(ROOT)}")

    references = sorted(set(IMAGE_RE.findall(README.read_text(encoding="utf-8"))))
    if not references:
        raise RuntimeError("No local README image references were found")

    missing = []
    for reference in references:
        asset = ROOT / reference[2:]
        if not asset.is_file() or asset.stat().st_size == 0:
            missing.append(reference)
            continue
        suffix = asset.suffix.lower()
        data = asset.read_bytes()
        if suffix == ".svg" and b"<svg" not in data[:2048]:
            raise RuntimeError(f"Invalid SVG image: {reference}")
        if suffix == ".gif" and not data.startswith((b"GIF87a", b"GIF89a")):
            raise RuntimeError(f"Invalid GIF image: {reference}")
        if suffix == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError(f"Invalid PNG image: {reference}")
        print(f"OK: {reference}")

    if missing:
        raise RuntimeError("Missing README image(s): " + ", ".join(missing))

    print(f"Validated {len(references)} local README image references.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise
