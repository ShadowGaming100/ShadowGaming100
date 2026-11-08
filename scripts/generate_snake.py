#!/usr/bin/env python3
"""Generate a smooth, infinitely looping contribution snake GIF from GitHub data."""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
API = "https://api.github.com/graphql"
WIDTH, HEIGHT = 1060, 190
CELL, GAP = 13, 4
STEP = CELL + GAP
LEFT, TOP = 66, 62
FPS_MS = 50
SUBFRAMES = 2
BODY_LENGTH = 7


def github_json(token: str, username: str) -> dict:
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": username}}).encode()
    request = urllib.request.Request(
        API,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "ShadowGaming100-profile-assets",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"GitHub GraphQL returned HTTP {exc.code}: "
            f"{exc.read().decode('utf-8', 'replace')[:400]}"
        ) from exc
    if result.get("errors"):
        raise RuntimeError("; ".join(e.get("message", "GraphQL error") for e in result["errors"]))
    user = result.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {username}")
    return user["contributionsCollection"]["contributionCalendar"]


def load_font(size: int):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def cell_color(count: int, theme="dark"):
    if theme == "light":
        if count <= 0: return (235, 237, 240)
        if count <= 2: return (155, 233, 168)
        if count <= 5: return (64, 196, 99)
        if count <= 9: return (48, 161, 78)
        return (33, 110, 57)
    if count <= 0: return (22, 27, 34)
    if count <= 2: return (14, 68, 41)
    if count <= 5: return (0, 109, 50)
    if count <= 9: return (38, 166, 65)
    return (57, 211, 83)


def build_grid(calendar: dict):
    days = {}
    for week in calendar.get("weeks", []):
        for day in week.get("contributionDays", []):
            days[day["date"]] = int(day.get("contributionCount", 0))

    # GitHub's calendar is a column-per-week grid, Sunday through Saturday.
    dates = sorted(days)
    if not dates:
        raise RuntimeError("GitHub returned an empty contribution calendar")
    first = dt.date.fromisoformat(dates[0])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    values = [[0 for _ in range(7)] for _ in range(53)]
    for date_text, count in days.items():
        date = dt.date.fromisoformat(date_text)
        week = (date - start).days // 7
        weekday = (date.weekday() + 1) % 7
        if 0 <= week < 53:
            values[week][weekday] = count
    return values


def make_path():
    # Serpentine route: every grid cell is visited exactly once.
    path = []
    for row in range(7):
        columns = range(53) if row % 2 == 0 else range(52, -1, -1)
        for column in columns:
            path.append((LEFT + column * STEP, TOP + row * STEP))
    return path


def render_frame(grid, path, progress: float, title_font, small_font, theme="dark"):
    bg = "#0d1117" if theme == "dark" else "#ffffff"
    border = "#30363d" if theme == "dark" else "#d0d7de"
    fg = "#e6edf3" if theme == "dark" else "#1f2328"
    muted = "#8b949e" if theme == "dark" else "#59636e"
    image = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, WIDTH - 2, HEIGHT - 2), radius=10, outline=border, width=2)
    draw.text((LEFT, 20), "CONTRIBUTION SNAKE", font=title_font, fill=fg)
    draw.text((WIDTH - LEFT, 25), "SHADOWGAMING100", font=small_font, fill=muted, anchor="ra")

    # Draw the contribution grid, keeping eaten cells empty for a clear eat effect.
    consumed = max(0, int(progress))
    for column in range(53):
        for row in range(7):
            x, y = LEFT + column * STEP, TOP + row * STEP
            route_index = row * 53 + (column if row % 2 == 0 else 52 - column)
            count = grid[column][row]
            color = (bg if count > 0 else ("#ebedf0" if theme == "light" else "#161b22")) if route_index < consumed and count > 0 else cell_color(count, theme)
            draw.rounded_rectangle((x, y, x + CELL, y + CELL), radius=3, fill=color)

    segment = min(progress, len(path) - 1)
    head_index = int(segment)
    fraction = segment - head_index
    x1, y1 = path[head_index]
    if head_index + 1 < len(path):
        x2, y2 = path[head_index + 1]
        hx, hy = x1 + (x2 - x1) * fraction, y1 + (y2 - y1) * fraction
    else:
        hx, hy = x1, y1

    # Tail follows the same route, with rounded segments and a bright head.
    for offset in range(BODY_LENGTH, 0, -1):
        index = head_index - offset
        if index < 0:
            continue
        bx, by = path[index]
        draw.rounded_rectangle(
            (bx - 1, by - 1, bx + CELL + 1, by + CELL + 1),
            radius=5,
            fill=(47, 129, 247),
            outline=(121, 192, 255),
            width=1,
        )
    draw.rounded_rectangle(
        (hx - 2, hy - 2, hx + CELL + 2, hy + CELL + 2),
        radius=6,
        fill="#f0883e",
        outline="#ffcc66",
        width=2,
    )
    # Two tiny eyes make the direction of travel visible.
    draw.ellipse((hx + 3, hy + 3, hx + 5, hy + 5), fill="#0d1117")
    draw.ellipse((hx + 8, hy + 3, hx + 10, hy + 5), fill="#0d1117")
    return image


def main():
    token = os.environ.get("GITHUB_TOKEN")
    username = os.environ.get("USERNAME", "ShadowGaming100")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required to generate the contribution snake")

    calendar = github_json(token, username)
    grid = build_grid(calendar)
    path = make_path()
    total = len(path)
    title_font = load_font(15)
    small_font = load_font(10)

    for theme in ("dark", "light"):
        frame_count = (total - 1) * SUBFRAMES + 1
        sample_indices = range(0, frame_count, max(1, frame_count // 24))
        samples = [
            render_frame(grid, path, index / SUBFRAMES, title_font, small_font, theme)
            .resize((265, 48))
            for index in sample_indices
        ]
        palette_sheet = Image.new("RGB", (265, 48 * len(samples)), "#000000")
        for index, sample in enumerate(samples):
            palette_sheet.paste(sample, (0, index * 48))
        palette = palette_sheet.quantize(colors=128, method=Image.Quantize.MEDIANCUT)

        # Quantize every frame against one shared palette to prevent colour flicker.
        frames = []
        for step in range(frame_count):
            frame = render_frame(
                grid, path, step / SUBFRAMES, title_font, small_font, theme
            )
            frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))

        output = ASSETS / f"snake.{theme}.gif"
        frames[0].save(
            output,
            save_all=True,
            append_images=frames[1:],
            duration=FPS_MS,
            loop=0,
            disposal=1,
            optimize=True,
        )
        data = output.read_bytes()
        if b"NETSCAPE2.0" not in data:
            raise RuntimeError(f"The generated {theme} snake GIF is missing its infinite-loop extension")
        print(
            f"Generated {output.relative_to(ROOT)}: {len(frames)} frames, "
            f"{calendar.get('totalContributions', 0)} contributions, loop=forever"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise
