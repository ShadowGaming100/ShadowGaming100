#!/usr/bin/env python3
"""Validate README-local images and enforce infinite looping on generated snake GIFs."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SNAKES = [ROOT / "assets" / "snake.dark.gif", ROOT / "assets" / "snake.light.gif"]
IMAGE_RE = re.compile(
    r"\./(?:assets|profile-3d-contrib)/[A-Za-z0-9_./-]+\.(?:svg|gif|png|webp)",
    re.IGNORECASE,
)


def make_gif_loop_forever(path):
    try:
        from PIL import Image, ImageSequence
    except ImportError as exc:
        raise RuntimeError("Pillow is required to validate and normalize GIF looping") from exc

    with Image.open(path) as source:
        frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(source)]
        durations = [
            frame.info.get("duration", source.info.get("duration", 100))
            for frame in ImageSequence.Iterator(source)
        ]
        if not frames:
            raise RuntimeError(f"No frames found in {path}")

    palette_frames = [
        frame.convert("RGB").quantize(method=Image.Quantize.MEDIANCUT)
        for frame in frames
    ]
    palette_frames[0].save(
        path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=True,
    )

    data = path.read_bytes()
    if b"NETSCAPE2.0" not in data:
        raise RuntimeError(f"GIF looping extension was not written: {path}")


def main():
    if not README.is_file():
        raise RuntimeError("README.md is missing")

    for snake in SNAKES:
        if not snake.is_file() or snake.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty snake GIF: {snake.relative_to(ROOT)}")
        make_gif_loop_forever(snake)
        print(f"Looping GIF verified: {snake.relative_to(ROOT)}")

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
