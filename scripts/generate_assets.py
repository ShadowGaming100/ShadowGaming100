
import os
import math
import base64

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = OUT + "/assets"

for directory in ("headers", "buttons", "stack"):
    os.makedirs(f"{A}/{directory}", exist_ok=True)

MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,'Segoe UI',system-ui,Roboto,'Helvetica Neue',Arial,sans-serif"

P = {
    "dark": dict(
        bg="#0d1117", card="#161b22", line="#30363d",
        fg="#e6edf3", sub="#8b949e", acc="#2f81f7",
        cube="#6e7681", grid="#e6edf3", gop=".16"
    ),
    "light": dict(
        bg="#ffffff", card="#f6f8fa", line="#d0d7de",
        fg="#1f2328", sub="#59636e", acc="#0969da",
        cube="#8c959f", grid="#1f2328", gop=".14"
    ),
}

ICON_PATH = A + "/freehosts-icon.png"


def icon_uri():
    try:
        data = open(ICON_PATH, "rb").read()
    except OSError:
        return None

    if data[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif data[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif data[:4] == b"\x00\x00\x01\x00":
        mime = "image/x-icon"
    elif data.lstrip()[:5] in (b"<svg ", b"<?xml"):
        mime = "image/svg+xml"
    else:
        return None

    return f"data:{mime};base64," + base64.b64encode(data).decode()


URI = icon_uri()


def fh_logo(x, y, size, c):
    if URI:
        return (
            f'<image href="{URI}" xlink:href="{URI}" '
            f'x="{x}" y="{y}" width="{size}" height="{size}" '
            f'preserveAspectRatio="xMidYMid meet"/>'
        )

    radius = size * .18
    return (
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" '
        f'rx="{radius:.1f}" fill="{c["acc"]}"/>'
        f'<text x="{x+size/2}" y="{y+size*.65}" '
        f'text-anchor="middle" font-family="{SANS}" '
        f'font-size="{size*.42:.0f}" font-weight="800" '
        f'fill="#fff">FH</text>'
    )


def hx(color):
    color = color.lstrip("#")
    return [int(color[i:i + 2], 16) for i in (0, 2, 4)]


def mix(c1, c2, amount):
    a, b = hx(c1), hx(c2)
    return "#%02x%02x%02x" % tuple(
        round(a[i] + (b[i] - a[i]) * amount)
        for i in range(3)
    )


def write(path, content):
    with open(f"{A}/{path}", "w", encoding="utf-8") as file:
        file.write(content)


SPL = (
    'calcMode="spline" '
    'keySplines="0.45 0 0.55 1;0.45 0 0.55 1" '
    'keyTimes="0;.5;1"'
)


def bob(amp, duration, begin=0):
    return (
        f'<animateTransform attributeName="transform" '
        f'type="translate" values="0 0;0 {-amp};0 0" '
        f'dur="{duration}s" begin="-{begin}s" '
        f'repeatCount="indefinite" {SPL}/>'
    )


def cube(cx, cy, size, color, label=None, text_color="#fff", fs=None):
    k = .866
    top = mix(color, "#ffffff", .30)
    right = mix(color, "#000000", .38)

    output = (
        f'<polygon points="{cx},{cy-size} {cx+k*size},{cy-size/2} '
        f'{cx},{cy} {cx-k*size},{cy-size/2}" fill="{top}"/>'
    )
    output += (
        f'<polygon points="{cx-k*size},{cy-size/2} {cx},{cy} '
        f'{cx},{cy+size} {cx-k*size},{cy+size/2}" fill="{color}"/>'
    )
    output += (
        f'<polygon points="{cx},{cy} {cx+k*size},{cy-size/2} '
        f'{cx+k*size},{cy+size/2} {cx},{cy+size}" fill="{right}"/>'
    )

    if label:
        fs = fs or size * .36
        output += (
            f'<text transform="matrix(0.866,0.5,0,1,'
            f'{cx-k*size:.2f},{cy-size/2:.2f})" '
            f'x="{size/2:.2f}" y="{size*.68:.2f}" '
            f'text-anchor="middle" font-family="{MONO}" '
            f'font-weight="800" font-size="{fs:.1f}" '
            f'fill="{text_color}">{label}</text>'
        )

    return output


def slab(cx, cy, size, height, color):
    k = .866
    top = mix(color, "#ffffff", .22)
    right = mix(color, "#000000", .38)

    return (
        f'<polygon points="{cx},{cy-size/2} {cx+k*size},{cy} '
        f'{cx},{cy+size/2} {cx-k*size},{cy}" fill="{top}"/>'
        f'<polygon points="{cx-k*size},{cy} {cx},{cy+size/2} '
        f'{cx},{cy+size/2+height} {cx-k*size},{cy+height}" '
        f'fill="{color}"/>'
        f'<polygon points="{cx},{cy+size/2} {cx+k*size},{cy} '
        f'{cx+k*size},{cy+height} {cx},{cy+size/2+height}" '
        f'fill="{right}"/>'
    )


def reveal_vals(events, duration):
    events = sorted(events, key=lambda event: event[0])

    if events[0][0] > 0:
        events = [(0, 0)] + events

    values = [str(value) for _, value in events]
    key_times = [time / duration for time, _ in events]
    key_times[0] = 0.0

    return (
        ";".join(values),
        ";".join(f"{min(value, 1):.5f}" for value in key_times)
    )


def box(width, height, c, x=1, y=1, radius=8):
    return (
        f'<rect x="{x}" y="{y}" width="{width-2*x}" '
        f'height="{height-2*y}" rx="{radius}" '
        f'fill="{c["card"]}" stroke="{c["line"]}" '
        f'stroke-width="1.5"/>'
    )


# ------------------------------------------------------------
# HERO


def hero(theme):
    c = P[theme]
    width, height, horizon = 1000, 300, 196

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" '
        f'aria-label="ShadowGaming100 | Developer, Builder, Founder">'
    ]

    output.append(
        f'<defs><clipPath id="all"><rect width="{width}" '
        f'height="{height}" rx="10"/></clipPath>'
        f'<clipPath id="floor"><rect y="{horizon}" '
        f'width="{width}" height="{height-horizon}"/></clipPath>'
        f'</defs>'
    )

    output.append('<g clip-path="url(#all)">')
    output.append(f'<rect width="{width}" height="{height}" fill="{c["card"]}"/>')

    output.append(
        f'<g clip-path="url(#floor)" stroke="{c["grid"]}" '
        f'stroke-opacity="{c["gop"]}" stroke-width="1">'
    )

    for x in range(-1400, 2500, 120):
        output.append(
            f'<line x1="500" y1="{horizon}" '
            f'x2="{x}" y2="{height+40}"/>'
        )

    output.append('</g>')

    for index in range(7):
        positions = ";".join(
            f"{horizon + (height-horizon+6)*(step/12)**2.2:.1f}"
            for step in range(13)
        )
        opacities = ";".join(
            f"{min(1, (step/12)*2)*float(c['gop'])*1.8:.3f}"
            for step in range(13)
        )

        output.append(
            f'<rect x="0" width="{width}" height="1" '
            f'fill="{c["grid"]}" y="{horizon}" opacity="0">'
            f'<animate attributeName="y" values="{positions}" '
            f'dur="5s" begin="-{index*5/7:.2f}s" '
            f'repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{opacities}" '
            f'dur="5s" begin="-{index*5/7:.2f}s" '
            f'repeatCount="indefinite"/></rect>'
        )

    output.append('</g>')
    output.append(
        f'<rect y="{horizon}" width="{width}" height="1.5" '
        f'fill="{c["line"]}"/>'
    )

    for x, y, size, color, amplitude, duration, begin in [
        (140, 150, 34, c["cube"], 10, 5, 0),
        (862, 128, 28, c["acc"], 9, 4.4, 1.6),
    ]:
        output.append(
            f'<g>{bob(amplitude, duration, begin)}'
            f'{cube(x, y, size, color)}</g>'
        )

    output.append(
        f'<text x="500" y="118" text-anchor="middle" '
        f'font-family="{MONO}" font-weight="800" font-size="56" '
        f'letter-spacing="6" fill="{c["fg"]}" opacity="0">'
        f'SHADOWGAMING100'
        f'<animate attributeName="opacity" from="0" to="1" '
        f'dur=".9s" fill="freeze"/></text>'
    )

    output.append(
        f'<text x="500" y="164" text-anchor="middle" '
        f'font-family="{MONO}" font-size="22" font-weight="600" '
        f'letter-spacing="5" fill="{c["sub"]}" opacity="0">'
        f'DEVELOPER · BUILDER · FOUNDER'
        f'<animate attributeName="opacity" from="0" to="1" '
        f'dur=".9s" begin=".4s" fill="freeze"/></text>'
    )

    output.append('</g>')
    output.append(
        f'<rect x=".75" y=".75" width="{width-1.5}" '
        f'height="{height-1.5}" rx="10" fill="none" '
        f'stroke="{c["line"]}" stroke-width="1.5"/>'
    )
    output.append('</svg>')

    return "\n".join(output)


# ------------------------------------------------------------
# TYPING ANIMATION


LINES = [
    "Building digital experiences.",
    "Turning ideas into code.",
    "Founder of FreeHosts.",
    "Always learning new things.",
]


def typing(theme, width=760, height=60, size=28):
    c = P[theme]
    char_width = size * .6
    char_time = .06
    delete_time = .025
    hold_time = 1.7

    duration = 0
    segments = []

    for line in LINES:
        text = "> " + line
        length = len(text)
        segments.append((text, length, duration))
        duration += length * char_time + hold_time + length * delete_time + .35

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" '
        f'aria-label="Building digital experiences">'
    ]

    cursor_events = []

    for index, (text, length, start) in enumerate(segments):
        text_width = length * char_width
        x = (width - text_width) / 2

        events = [(0, 0)]
        events += [
            (start + step * char_time, step * char_width)
            for step in range(length + 1)
        ]

        erase_start = start + length * char_time + hold_time
        events += [
            (erase_start + step * delete_time, (length-step)*char_width)
            for step in range(1, length + 1)
        ]

        values, key_times = reveal_vals(events, duration)
        cursor_events += [
            (time, round(x + value, 2))
            for time, value in events
        ]

        output.append(
            f'<clipPath id="typing{index}">'
            f'<rect x="{x:.2f}" y="0" height="{height}" width="0">'
            f'<animate attributeName="width" calcMode="discrete" '
            f'dur="{duration:.2f}s" repeatCount="indefinite" '
            f'values="{values}" keyTimes="{key_times}"/>'
            f'</rect></clipPath>'
        )

        output.append(
            f'<g clip-path="url(#typing{index})" '
            f'font-family="{MONO}" font-weight="700" '
            f'font-size="{size}">'
            f'<text x="{x:.2f}" y="{height/2+size*.34:.2f}" '
            f'xml:space="preserve" textLength="{text_width:.2f}" '
            f'lengthAdjust="spacing">'
            f'<tspan fill="{c["acc"]}">&gt; </tspan>'
            f'<tspan fill="{c["fg"]}">{LINES[index]}</tspan>'
            f'</text></g>'
        )

    cursor_values, cursor_times = reveal_vals(cursor_events, duration)

    output.append(
        f'<rect y="{height/2-size*.62:.1f}" '
        f'width="{size*.5:.1f}" height="{size*1.2:.1f}" '
        f'fill="{c["fg"]}">'
        f'<animate attributeName="x" calcMode="discrete" '
        f'dur="{duration:.2f}s" repeatCount="indefinite" '
        f'values="{cursor_values}" keyTimes="{cursor_times}"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" '
        f'keyTimes="0;.5;.5;1" dur="1s" '
        f'repeatCount="indefinite" calcMode="discrete"/>'
        f'</rect>'
    )

    output.append('</svg>')
    return "\n".join(output)


# ------------------------------------------------------------
# SECTION HEADERS


HEADERS = [
    ("about", "01", "About me"),
    ("roles", "02", "What I do"),
    ("stack", "03", "Tech stack"),
    ("featured", "04", "Featured project"),
    ("stats", "05", "GitHub statistics"),
    ("world", "06", "3D contribution world"),
    ("snake", "07", "Contribution snake"),
    ("trophies", "08", "Trophies"),
]


def header(theme, number, title, width=760, font_size=35):
    c = P[theme]
    height = 76 if width > 500 else 70
    number_size = 22 if width > 500 else 20
    title_x = 58 if width > 500 else 50

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" aria-label="{title}">'
        f'<text x="8" y="50" font-family="{MONO}" '
        f'font-size="{number_size}" font-weight="700" '
        f'fill="{c["acc"]}">{number}</text>'
        f'<text x="{title_x}" y="52" font-family="{SANS}" '
        f'font-size="{font_size}" font-weight="700" '
        f'fill="{c["fg"]}">{title}</text>'
        f'<rect x="8" y="{height-8}" width="{width-16}" '
        f'height="1.5" fill="{c["line"]}"/>'
        f'</svg>'
    )


# ------------------------------------------------------------
# TERMINAL ANIMATION


TERM_DESKTOP = [
    ("cmd", "whoami"),
    ("out", "Founder & Developer"),
    ("cmd", "current-project"),
    ("out", "FreeHosts v2"),
    ("cmd", "interests"),
    ("out", "Web Development · APIs · Discord Bots"),
    ("cmd", "status"),
    ("out", "Always learning..."),
]

TERM_MOBILE = [
    ("cmd", "whoami"),
    ("out", "Founder & Developer"),
    ("cmd", "current-project"),
    ("out", "FreeHosts v2"),
    ("cmd", "status"),
    ("out", "Always learning..."),
]


def terminal(width, rows):
    font_size = 20
    char_width = 12.9
    duration = 10.0
    current_time = .8
    x_start = 36

    y_positions = []
    y = 98

    for index, (kind, _) in enumerate(rows):
        y_positions.append(y)
        next_kind = rows[index + 1][0] if index + 1 < len(rows) else None
        y += 28 if kind == "cmd" or next_kind == "out" else 36

    height = y_positions[-1] + 24

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" '
        f'aria-label="Terminal: Founder and Developer, FreeHosts v2">'
    ]

    output.append(
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" '
        f'rx="8" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>'
    )

    output.append(
        f'<path d="M1 50 V9 a8 8 0 0 1 8 -8 H{width-9} '
        f'a8 8 0 0 1 8 8 V50 Z" fill="#161b22"/>'
        f'<rect x="1" y="50" width="{width-2}" height="1.5" '
        f'fill="#30363d"/>'
    )

    for index in range(3):
        output.append(
            f'<circle cx="{34+index*26}" cy="26" r="7" fill="#30363d"/>'
        )

    output.append(
        f'<text x="{width//2 + (30 if width < 600 else 0)}" y="33" '
        f'text-anchor="middle" font-family="{MONO}" '
        f'font-size="16" fill="#8b949e">shadow@gaming100: ~</text>'
    )

    for index, (kind, text) in enumerate(rows):
        y = y_positions[index]
        command = kind == "cmd"
        displayed_length = len(text) + (11 if command else 0)
        speed = .07 if command else .018

        events = [(0, 0)]
        events += [
            (current_time + step * speed, round(step * char_width, 2))
            for step in range(displayed_length + 1)
        ]
        events.append((current_time + displayed_length * speed + .01, 900))

        values, key_times = reveal_vals(events, duration)

        output.append(
            f'<clipPath id="terminal{index}">'
            f'<rect x="{x_start}" y="{y-24}" height="32" width="0">'
            f'<animate attributeName="width" calcMode="discrete" '
            f'dur="{duration}s" repeatCount="indefinite" '
            f'values="{values}" keyTimes="{key_times}"/>'
            f'</rect></clipPath>'
        )

        if command:
            output.append(
                f'<g clip-path="url(#terminal{index})" '
                f'font-family="{MONO}" font-size="{font_size}" '
                f'font-weight="700">'
                f'<text x="{x_start}" y="{y}" xml:space="preserve">'
                f'<tspan fill="#3fb950">shadow</tspan>'
                f'<tspan fill="#8b949e">@</tspan>'
                f'<tspan fill="#2f81f7">~</tspan>'
                f'<tspan fill="#8b949e"> $ </tspan>'
                f'<tspan fill="#e6edf3">{text}</tspan>'
                f'</text></g>'
            )
        else:
            output.append(
                f'<g clip-path="url(#terminal{index})" '
                f'font-family="{MONO}" font-size="{font_size}" '
                f'font-weight="600">'
                f'<text x="{x_start}" y="{y}" fill="#c9d1d9" '
                f'xml:space="preserve">{text}</text></g>'
            )

        current_time += displayed_length * speed + (
            .5 if command else .7
        )

    output.append('</svg>')
    return "\n".join(output)


# ------------------------------------------------------------
# TECH STACK


TECH = [
    # Languages
    ("js", "JS", "JavaScript", "Language", "#e8c500", "#111"),
    ("ts", "TS", "TypeScript", "Language", "#3178c6", "#fff"),
    ("py", "PY", "Python", "Language", "#3776ab", "#fff"),
    ("html", "HTML", "HTML", "Markup", "#e34f26", "#fff"),
    ("css", "CSS", "CSS", "Styles", "#1572b6", "#fff"),

    # Runtime and frameworks
    ("node", "NODE", "Node.js", "Runtime", "#3f9b3f", "#fff"),
    ("djs", "DJS", "Discord.js", "Bots", "#5865f2", "#fff"),
    ("express", "EX", "Express.js", "Framework", "#7b818c", "#fff"),
    ("next", "NX", "Next.js", "Framework", "#24292f", "#fff"),
    ("fastify", "FT", "Fastify", "Framework", "#00a98f", "#fff"),

    # Databases
    ("pg", "PG", "PostgreSQL", "Database", "#3b7ab8", "#fff"),
    ("mysql", "SQL", "MySQL", "Database", "#00758f", "#fff"),
    ("mongo", "MDB", "MongoDB", "Database", "#47a248", "#fff"),

    # Infrastructure
    ("cf", "CF", "Cloudflare", "Infrastructure", "#f38020", "#fff"),

    # Tools
    ("git", "GIT", "Git", "Tool", "#f05032", "#fff"),
    ("github", "GH", "GitHub", "Platform", "#6e7681", "#fff"),
    ("gha", "GHA", "GitHub Actions", "Automation", "#2088ff", "#fff"),
]


def tile(theme, index):
    c = P[theme]
    key, label, name, category, color, text_color = TECH[index]

    width, height = 140, 190
    duration = 3.6 + (index % 3) * .5
    begin = index * .55
    size = 40

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" '
        f'aria-label="{name}: {category}">'
    ]

    output.append(
        f'<ellipse cx="70" cy="128" rx="{size*.9:.0f}" '
        f'ry="{size*.2:.0f}" fill="{c["fg"]}" opacity=".12">'
        f'<animate attributeName="rx" '
        f'values="{size*.9:.0f};{size*.65:.0f};{size*.9:.0f}" '
        f'dur="{duration}s" begin="-{begin}s" '
        f'repeatCount="indefinite" {SPL}/></ellipse>'
    )

    output.append(
        f'<g>{bob(12, duration, begin)}'
        f'{cube(70, 62, size, color, label, text_color, '
        f'fs=(19 if len(label) < 3 else 14))}</g>'
    )

    output.append(
        f'<text x="70" y="162" text-anchor="middle" '
        f'font-family="{SANS}" font-size="20" font-weight="700" '
        f'fill="{c["fg"]}">{name}</text>'
    )

    output.append(
        f'<text x="70" y="184" text-anchor="middle" '
        f'font-family="{SANS}" font-size="16" '
        f'fill="{c["sub"]}">{category}</text>'
    )

    output.append('</svg>')
    return "\n".join(output)


# ------------------------------------------------------------
# ROLE CARDS


def role_card(theme, kind):
    c = P[theme]
    width, height = 495, 250

    if kind == 0:
        label = "Founder"
        title = "FreeHosts"
        description = [
            "Building a people-centered directory",
            "for discovering free hosting."
        ]
    else:
        label = "Developer"
        title = "Independent"
        description = [
            "Frontend and backend development.",
            "APIs · Discord bots · Infrastructure"
        ]

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" '
        f'aria-label="{label}: {title}">',
        box(width, height, c)
    ]

    icon_x, icon_y = 82, 122

    if kind == 0:
        output.append(
            f'<ellipse cx="{icon_x}" cy="{icon_y+56}" '
            f'rx="40" ry="8" fill="{c["fg"]}" opacity=".1"/>'
            f'<g>{bob(6, 3.6)}'
            f'{fh_logo(icon_x-46, icon_y-46, 92, c)}</g>'
        )
    else:
        output.append(
            f'<g>{bob(8, 3.8)}'
            f'{cube(icon_x, icon_y, 44, c["acc"], "&lt;/&gt;", "#fff", 16)}'
            f'</g>'
        )

    output.append(
        f'<text x="170" y="62" font-family="{SANS}" '
        f'font-size="20" font-weight="600" '
        f'fill="{c["acc"]}">{label}</text>'
    )

    output.append(
        f'<text x="170" y="116" font-family="{SANS}" '
        f'font-size="42" font-weight="700" '
        f'fill="{c["fg"]}">{title}</text>'
    )

    for index, line in enumerate(description):
        output.append(
            f'<text x="170" y="{152+index*30}" '
            f'font-family="{SANS}" font-size="19" '
            f'fill="{c["sub"]}">{line}</text>'
        )

    output.append('</svg>')
    return "\n".join(output)


# ------------------------------------------------------------
# FEATURED PROJECT


def featured(theme):
    c = P[theme]
    width, height = 1000, 350

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" '
        f'aria-label="Featured project: FreeHosts, freehosts.eu">'
    ]

    output.append(box(width, height, c))

    center_x = 200

    output.append(
        f'<ellipse cx="{center_x}" cy="290" rx="90" ry="16" '
        f'fill="{c["fg"]}" opacity=".1">'
        f'<animate attributeName="rx" values="90;70;90" '
        f'dur="4s" repeatCount="indefinite" {SPL}/></ellipse>'
    )

    output.append(
        f'<g>{bob(12, 4)}'
        f'{fh_logo(center_x-100, 70, 200, c)}</g>'
    )

    text_x = 410

    output.append(
        f'<text x="{text_x}" y="84" font-family="{SANS}" '
        f'font-size="22" font-weight="600" '
        f'fill="{c["acc"]}">freehosts.eu</text>'
    )

    output.append(
        f'<text x="{text_x}" y="160" font-family="{SANS}" '
        f'font-size="76" font-weight="800" '
        f'fill="{c["fg"]}">FreeHosts</text>'
    )

    output.append(
        f'<text x="{text_x}" y="205" font-family="{SANS}" '
        f'font-size="25" fill="{c["sub"]}">'
        f'A community-driven directory for</text>'
    )

    output.append(
        f'<text x="{text_x}" y="238" font-family="{SANS}" '
        f'font-size="25" fill="{c["sub"]}">'
        f'discovering free hosting providers.</text>'
    )

    output.append(
        f'<rect x="{text_x}" y="268" width="270" height="52" '
        f'rx="6" fill="{c["acc"]}"/>'
        f'<text x="{text_x+26}" y="302" font-family="{SANS}" '
        f'font-size="22" font-weight="600" fill="#fff">'
        f'Explore FreeHosts</text>'
        f'<path d="M{ text_x+228 } 306 L{ text_x+242 } 292 '
        f'M{ text_x+230 } 291 H{ text_x+243 } V{ text_x+304 }" '
        f'fill="none" stroke="#fff" stroke-width="2.4" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )

    output.append('</svg>')
    return "\n".join(output)


def featured_mobile(theme):
    c = P[theme]
    width, height = 600, 600

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" '
        f'aria-label="Featured project: FreeHosts, freehosts.eu">'
    ]

    output.append(box(width, height, c))

    output.append(
        f'<ellipse cx="300" cy="238" rx="84" ry="15" '
        f'fill="{c["fg"]}" opacity=".1">'
        f'<animate attributeName="rx" values="84;66;84" '
        f'dur="4s" repeatCount="indefinite" {SPL}/></ellipse>'
    )

    output.append(
        f'<g>{bob(10, 4)}{fh_logo(205, 52, 190, c)}</g>'
    )

    output.append(
        f'<text x="300" y="300" text-anchor="middle" '
        f'font-family="{SANS}" font-size="28" font-weight="600" '
        f'fill="{c["acc"]}">freehosts.eu</text>'
    )

    output.append(
        f'<text x="300" y="378" text-anchor="middle" '
        f'font-family="{SANS}" font-size="78" font-weight="800" '
        f'fill="{c["fg"]}">FreeHosts</text>'
    )

    for index, line in enumerate([
        "A community-driven directory",
        "for discovering free",
        "hosting providers."
    ]):
        output.append(
            f'<text x="300" y="{428+index*38}" '
            f'text-anchor="middle" font-family="{SANS}" '
            f'font-size="30" fill="{c["sub"]}">{line}</text>'
        )

    output.append(
        f'<rect x="110" y="520" width="380" height="60" '
        f'rx="8" fill="{c["acc"]}"/>'
        f'<text x="300" y="560" text-anchor="middle" '
        f'font-family="{SANS}" font-size="28" '
        f'font-weight="600" fill="#fff">Explore FreeHosts</text>'
    )

    output.append('</svg>')
    return "\n".join(output)


# ------------------------------------------------------------
# CUSTOM BUTTONS
#
# Each button uses a custom geometric symbol instead of an
# imported icon font or a generic icon library.


def button(theme, name, label, width=190):
    c = P[theme]
    height = 64
    face_height = 54

    if name == "github":
        face = c["fg"]
        edge = mix(c["fg"], c["bg"], .55)
        text_color = c["bg"]
        symbol_color = c["bg"]
    elif name == "freehosts":
        face = c["acc"]
        edge = mix(c["acc"], "#000000", .4)
        text_color = "#ffffff"
        symbol_color = "#ffffff"
    else:
        face = c["card"]
        edge = c["line"]
        text_color = c["fg"]
        symbol_color = c["fg"]

    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" aria-label="{label}">'
    ]

    output.append(
        f'<rect x="1" y="6" width="{width-2}" '
        f'height="{face_height}" rx="11" fill="{edge}"/>'
    )

    stroke = (
        f' stroke="{c["line"]}" stroke-width="1.5"'
        if name == "contact" else ""
    )

    output.append(
        f'<rect x="1" y="2" width="{width-2}" '
        f'height="{face_height}" rx="11" fill="{face}"{stroke}/>'
    )

    center_y = 2 + face_height / 2

    if name == "github":
        # Custom connected-node mark.
        output.append(
            f'<g transform="translate(25 {center_y-14})" '
            f'fill="none" stroke="{symbol_color}" '
            f'stroke-width="2.5" stroke-linecap="round">'
            f'<path d="M7 7 L19 7 L19 20 M7 7 L7 20"/>'
            f'<circle cx="7" cy="7" r="4" fill="{symbol_color}"/>'
            f'<circle cx="19" cy="7" r="4" fill="{symbol_color}"/>'
            f'<circle cx="7" cy="20" r="4" fill="{symbol_color}"/>'
            f'</g>'
        )

    elif name == "freehosts":
        output.append(
            f'<g transform="translate(23 {center_y-15})" '
            f'fill="none" stroke="{symbol_color}" '
            f'stroke-width="2.2" stroke-linejoin="round">'
            f'<path d="M15 1 L28 8.5 L28 23.5 L15 31 '
            f'L2 23.5 L2 8.5 Z"/>'
            f'<path d="M2 8.5 L15 16 L28 8.5 M15 16 V31"/>'
            f'</g>'
        )

    else:
        # Custom envelope outline.
        output.append(
            f'<g transform="translate(24 {center_y-13})" '
            f'fill="none" stroke="{symbol_color}" '
            f'stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">'
            f'<rect x="1" y="2" width="27" height="21" rx="4"/>'
            f'<path d="M2 5 L14.5 15 L27 5"/>'
            f'</g>'
        )

    output.append(
        f'<text x="65" y="{center_y+8:.1f}" '
        f'font-family="{SANS}" font-size="20" '
        f'font-weight="700" fill="{text_color}">{label}</text>'
    )

    output.append('</svg>')
    return "\n".join(output)


# ------------------------------------------------------------
# FOOTER


def footer(theme):
    c = P[theme]
    width, height = 1000, 70

    return f'''<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
viewBox="0 0 {width} {height}" width="{width}" height="{height}"
role="img" aria-label="© ShadowGaming100">
<rect x="8" y="10" width="{width-16}" height="1.5"
fill="{c['line']}"/>
<text x="500" y="48" text-anchor="middle"
font-family="{SANS}" font-size="20"
fill="{c['sub']}">© ShadowGaming100</text>
</svg>'''


# ------------------------------------------------------------
# GENERATE ASSETS


os.makedirs(f"{A}/stack", exist_ok=True)

# Remove only generated assets that are recreated below.
for filename in os.listdir(A):
    if filename.startswith((
        "banner",
        "typing",
        "footer",
        "divider",
        "hero",
        "roles",
        "stack."
    )):
        path = f"{A}/{filename}"
        if os.path.isfile(path):
            os.remove(path)


for theme in ("dark", "light"):
    write(f"hero.{theme}.svg", hero(theme))
    write(f"typing.{theme}.svg", typing(theme))
    write(f"footer.{theme}.svg", footer(theme))

    write(f"featured.{theme}.svg", featured(theme))
    write(f"featured.m.{theme}.svg", featured_mobile(theme))

    write(f"role.founder.{theme}.svg", role_card(theme, 0))
    write(f"role.developer.{theme}.svg", role_card(theme, 1))

    for index, technology in enumerate(TECH):
        write(
            f"stack/{technology[0]}.{theme}.svg",
            tile(theme, index)
        )

    for key, number, title in HEADERS:
        write(
            f"headers/{key}.{theme}.svg",
            header(theme, number, title)
        )
        write(
            f"headers/{key}.m.{theme}.svg",
            header(theme, number, title, width=420, font_size=30)
        )

    for name, label in (
        ("github", "GitHub"),
        ("freehosts", "FreeHosts"),
        ("contact", "Contact")
    ):
        write(
            f"buttons/{name}.{theme}.svg",
            button(theme, name, label)
        )


write("terminal.svg", terminal(760, TERM_DESKTOP))
write("terminal.m.svg", terminal(440, TERM_MOBILE))

total_size = sum(
    os.path.getsize(os.path.join(directory, filename))
    for directory, _, filenames in os.walk(A)
    for filename in filenames
    if filename.endswith(".svg")
)

print(f"Generated SVG assets: {total_size // 1024} KB")
print(f"Generated {len(TECH)} technology icons in light and dark themes.")
