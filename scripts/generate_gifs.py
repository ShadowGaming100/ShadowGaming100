#!/usr/bin/env python3
"""Create lightweight, smoothly animated GIF versions of README motion artwork."""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 1000, 300
DARK = {
    "bg": "#161b22", "fg": "#e6edf3", "sub": "#8b949e",
    "grid": "#e6edf3", "line": "#30363d", "accent": "#2f81f7",
    "cube": "#6e7681",
}
LIGHT = {
    "bg": "#f6f8fa", "fg": "#1f2328", "sub": "#59636e",
    "grid": "#1f2328", "line": "#d0d7de", "accent": "#0969da",
    "cube": "#8c959f",
}


def font(size, bold=False):
    names = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    )
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def cube(draw, cx, cy, size, color):
    x = size * .866
    top = (cx, cy - size)
    right_top = (cx + x, cy - size / 2)
    center = (cx, cy)
    left_top = (cx - x, cy - size / 2)
    bottom = (cx, cy + size)
    right_bottom = (cx + x, cy + size / 2)
    left_bottom = (cx - x, cy + size / 2)
    base = hex_rgb(color)
    lighten = tuple(min(255, int(v * 1.28)) for v in base)
    darken = tuple(max(0, int(v * .62)) for v in base)
    draw.polygon([top, right_top, center, left_top], fill=lighten)
    draw.polygon([left_top, center, bottom, left_bottom], fill=base)
    draw.polygon([center, right_top, right_bottom, bottom], fill=darken)


def hero_frame(theme, frame, title_font, sub_font):
    c = theme
    image = Image.new("RGB", (WIDTH, HEIGHT), c["bg"])
    draw = ImageDraw.Draw(image)
    hz = 196
    draw.rounded_rectangle((1, 1, WIDTH - 2, HEIGHT - 2), radius=10, outline=c["line"], width=2)

    # Perspective floor and moving horizontal scan lines.
    for xb in range(-1400, 2500, 120):
        draw.line((500, hz, xb, HEIGHT + 40), fill=c["grid"], width=1)
    phase = (frame / 24) * math.pi * 2
    for row in range(7):
        y = hz + 4 + row * 15 + math.sin(phase - row * .65) * 2
        draw.line((0, y, WIDTH, y), fill=c["grid"], width=1)

    cube(draw, 140, 150 + math.sin(phase) * 10, 34, c["cube"])
    cube(draw, 862, 128 + math.sin(phase + 1.6) * 9, 28, c["accent"])

    title = "SHADOWGAMING100"
    tagline = "DEVELOPER  ·  BUILDER  ·  FOUNDER"
    draw.text((500, 105), title, font=title_font, fill=c["fg"], anchor="mm")
    draw.text((500, 158), tagline, font=sub_font, fill=c["sub"], anchor="mm")
    return image


def save_loop(frames, output, duration):
    # All frames use the first frame's palette to prevent colour flicker.
    samples = frames[::max(1, len(frames) // 24)]
    sample_sheet = Image.new("RGB", (250, 75 * len(samples)), "#000000")
    for index, frame in enumerate(samples):
        sample_sheet.paste(frame.convert("RGB").resize((250, 75)), (0, index * 75))
    palette = sample_sheet.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    normalized = []
    for frame in frames:
        normalized.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
    normalized[0].save(
        output,
        save_all=True,
        append_images=normalized[1:],
        duration=duration,
        loop=0,
        disposal=1,
        optimize=True,
    )
    if b"NETSCAPE2.0" not in output.read_bytes():
        raise RuntimeError(f"GIF loop extension missing: {output.name}")


def generate_hero():
    for name, theme in (("dark", DARK), ("light", LIGHT)):
        frames = [
            hero_frame(theme, frame, font(38, True), font(16, True))
            for frame in range(24)
        ]
        save_loop(frames, ASSETS / f"hero.{name}.gif", 50)


def typing_frames(theme, name):
    c = theme
    messages = [
        "Building digital experiences.",
        "Turning ideas into code.",
        "Founder of FreeHosts.",
        "Developer at Nemethic.",
    ]
    regular = font(27, True)
    frames = []
    for message in messages:
        full = "> " + message
        type_count = max(20, len(full))
        for count in range(0, len(full) + 1, max(1, math.ceil(len(full) / 24))):
            image = Image.new("RGB", (760, 64), c["bg"])
            draw = ImageDraw.Draw(image)
            visible = full[:count]
            draw.text((380, 32), visible, font=regular, fill=c["fg"], anchor="mm")
            frames.append(image)
        for _ in range(7):
            image = Image.new("RGB", (760, 64), c["bg"])
            ImageDraw.Draw(image).text((380, 32), full, font=regular, fill=c["fg"], anchor="mm")
            frames.append(image)
        for count in range(len(full), -1, -max(1, math.ceil(len(full) / 24))):
            image = Image.new("RGB", (760, 64), c["bg"])
            ImageDraw.Draw(image).text((380, 32), full[:count], font=regular, fill=c["fg"], anchor="mm")
            frames.append(image)
    save_loop(frames, ASSETS / f"typing.{name}.gif", 65)



def featured_frame(theme, frame, title_font, body_font, small_font):
    c = theme
    image = Image.new("RGB", (1000, 350), c["bg"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, 998, 348), radius=8, fill=c["bg"], outline=c["line"], width=2)

    bob = math.sin(frame / 24 * math.pi * 2) * 10
    icon_path = ASSETS / "freehosts-icon.png"
    try:
        logo = Image.open(icon_path).convert("RGBA").resize((190, 190), Image.Resampling.LANCZOS)
        image.paste(logo, (105, int(65 + bob)), logo)
    except (OSError, ValueError):
        # Brand-coloured server mark fallback if the remote icon is unavailable.
        x0, y0 = 120, int(105 + bob)
        draw.rounded_rectangle((x0, y0, x0 + 160, y0 + 58), radius=12, fill="#0969da")
        draw.rounded_rectangle((x0, y0 + 72, x0 + 160, y0 + 130), radius=12, fill="#0969da")
        for yy in (y0 + 29, y0 + 101):
            draw.ellipse((x0 + 18, yy - 5, x0 + 28, yy + 5), fill="#ffffff")
            draw.line((x0 + 48, yy, x0 + 138, yy), fill="#ffffff", width=5)

    draw.text((410, 65), "freehosts.eu", font=small_font, fill=c["accent"])
    draw.text((410, 95), "FreeHosts", font=title_font, fill=c["fg"])
    draw.text((410, 205), "A community-driven directory for", font=body_font, fill=c["sub"])
    draw.text((410, 240), "discovering free hosting providers.", font=body_font, fill=c["sub"])
    draw.rounded_rectangle((410, 270, 680, 322), radius=7, fill=c["accent"])
    draw.text((436, 284), "Explore FreeHosts", font=small_font, fill="#ffffff")
    draw.line((650, 306, 666, 290), fill="#ffffff", width=3)
    draw.line((651, 290, 666, 290), fill="#ffffff", width=3)
    draw.line((666, 290, 666, 305), fill="#ffffff", width=3)
    return image


def generate_featured():
    for name, theme in (("dark", DARK), ("light", LIGHT)):
        frames = [
            featured_frame(theme, frame, font(64, True), font(22), font(20, True))
            for frame in range(24)
        ]
        save_loop(frames, ASSETS / f"featured.{name}.gif", 50)


def generate_typing():
    typing_frames(DARK, "dark")
    typing_frames(LIGHT, "light")



def generate_terminal():
    width, height = 760, 340
    rows = [
        ("$ whoami", "ShadowGaming100"),
        ("$ cat roles.txt", "Founder @ FreeHosts  ·  Developer @ Nemethic"),
        ("$ echo $STACK", "JavaScript / Node.js / PostgreSQL"),
        ("$ ./build --purpose", "Building digital experiences. [ OK ]"),
    ]
    mono = font(17, True)
    # Keep a short pause at the end, then repeat the terminal typing sequence.
    events = []
    cursor = 0
    for command, output in rows:
        events.append((cursor, command, "command"))
        cursor += max(1, math.ceil(len(command) / 3))
        events.append((cursor + 2, output, "output"))
        cursor += max(1, math.ceil(len(output) / 3)) + 5
    total = cursor + 12
    frames = []
    for frame_no in range(total):
        image = Image.new("RGB", (width, height), "#0d1117")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=8, fill="#0d1117", outline="#30363d", width=2)
        draw.rounded_rectangle((2, 2, width - 2, 50), radius=8, fill="#161b22")
        draw.rectangle((2, 40, width - 2, 51), fill="#161b22")
        for i in range(3):
            draw.ellipse((27 + i * 26, 19, 41 + i * 26, 33), fill="#30363d")
        draw.text((width // 2, 26), "shadow@gaming100: ~", font=font(14), fill="#8b949e", anchor="mm")

        y = 82
        for start, text, kind in events:
            if frame_no < start:
                continue
            count = min(len(text), max(0, (frame_no - start) * 3))
            visible = text[:count]
            color = "#e6edf3" if kind == "command" else "#c9d1d9"
            if kind == "command":
                draw.text((34, y), "$ ", font=mono, fill="#3fb950")
                draw.text((58, y), visible[2:], font=mono, fill=color)
            else:
                draw.text((34, y), visible, font=mono, fill=color)
            y += 31
        draw.text((width - 28, height - 18), "UTF-8", font=font(11), fill="#6e7681", anchor="ra")
        frames.append(image)
    save_loop(frames, ASSETS / "terminal.gif", 70)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_hero()
    generate_typing()
    generate_terminal()
    generate_featured()
    print("Generated looping hero, typing, terminal, and featured GIFs for README playback.")


if __name__ == "__main__":
    main()
