import os, math, base64, html, re, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = OUT + "/assets"
for d in ("headers", "buttons"):
    os.makedirs(f"{A}/{d}", exist_ok=True)

MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,'Segoe UI',system-ui,Roboto,'Helvetica Neue',Arial,sans-serif"

# Flat palette taken from GitHub's own light and dark themes so it sits naturally on the page.
P = {
 "dark":  dict(bg="#0d1117", card="#161b22", line="#30363d", fg="#e6edf3", sub="#8b949e", acc="#2f81f7", cube="#6e7681", grid="#e6edf3", gop=".16"),
 "light": dict(bg="#ffffff", card="#f6f8fa", line="#d0d7de", fg="#1f2328", sub="#59636e", acc="#0969da", cube="#8c959f", grid="#1f2328", gop=".14"),
}

ICON_PATH = A + "/freehosts-icon.png"
def icon_uri():
    """Real FreeHosts icon, downloaded by the workflow. None if missing or not an image."""
    try: b = open(ICON_PATH, "rb").read()
    except OSError: return None
    if b[:8] == b"\x89PNG\r\n\x1a\n": m = "image/png"
    elif b[:3] == b"\xff\xd8\xff": m = "image/jpeg"
    elif b[:4] == b"\x00\x00\x01\x00": m = "image/x-icon"
    elif b.lstrip()[:5] in (b"<svg ", b"<?xml"): m = "image/svg+xml"
    else: return None
    return f"data:{m};base64," + base64.b64encode(b).decode()
URI = icon_uri()
def fh_logo(x, y, size, c):
    if URI:
        return f'<image href="{URI}" xlink:href="{URI}" x="{x}" y="{y}" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet"/>'
    r = size*.18  # fallback tile if the download failed
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{r:.1f}" fill="{c["acc"]}"/><text x="{x+size/2}" y="{y+size*.65}" text-anchor="middle" font-family="{SANS}" font-size="{size*.42:.0f}" font-weight="800" fill="#fff">FH</text>'

def hx(c): c = c.lstrip("#"); return [int(c[i:i+2], 16) for i in (0, 2, 4)]
def mix(c1, c2, t):
    a, b = hx(c1), hx(c2)
    return "#%02x%02x%02x" % tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
def write(path, s): open(f"{A}/{path}", "w", encoding="utf-8").write(s)
SPL = 'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" keyTimes="0;.5;1"'

def bob(amp, dur, begin=0):
    return f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-amp};0 0" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite" {SPL}/>'

def cube(cx, cy, s, col, label=None, txt="#fff", fs=None):
    k = .866
    top = mix(col, "#ffffff", .30); right = mix(col, "#000000", .38)
    o = f'<polygon points="{cx},{cy-s} {cx+k*s},{cy-s/2} {cx},{cy} {cx-k*s},{cy-s/2}" fill="{top}"/>'
    o += f'<polygon points="{cx-k*s},{cy-s/2} {cx},{cy} {cx},{cy+s} {cx-k*s},{cy+s/2}" fill="{col}"/>'
    o += f'<polygon points="{cx},{cy} {cx+k*s},{cy-s/2} {cx+k*s},{cy+s/2} {cx},{cy+s}" fill="{right}"/>'
    if label:
        fs = fs or s*.36
        o += f'<text transform="matrix(0.866,0.5,0,1,{cx-k*s:.2f},{cy-s/2:.2f})" x="{s/2:.2f}" y="{s*.68:.2f}" text-anchor="middle" font-family="{MONO}" font-weight="800" font-size="{fs:.1f}" fill="{txt}">{label}</text>'
    return o

def slab(cx, cy, s, h, col):
    k = .866
    top = mix(col, "#ffffff", .22); right = mix(col, "#000000", .38)
    return (f'<polygon points="{cx},{cy-s/2} {cx+k*s},{cy} {cx},{cy+s/2} {cx-k*s},{cy}" fill="{top}"/>'
            f'<polygon points="{cx-k*s},{cy} {cx},{cy+s/2} {cx},{cy+s/2+h} {cx-k*s},{cy+h}" fill="{col}"/>'
            f'<polygon points="{cx},{cy+s/2} {cx+k*s},{cy} {cx+k*s},{cy+h} {cx},{cy+s/2+h}" fill="{right}"/>')

def reveal_vals(events, T):
    ev = sorted(events, key=lambda e: e[0])
    if ev[0][0] > 0: ev = [(0, 0)] + ev
    vals = [str(v) for _, v in ev]; kts = [tt / T for tt, _ in ev]
    kts[0] = 0.0
    return ";".join(vals), ";".join(f"{min(k,1):.5f}" for k in kts)

def box(w, h, c, x=1, y=1, r=8):
    return f'<rect x="{x}" y="{y}" width="{w-2*x}" height="{h-2*y}" rx="{r}" fill="{c["card"]}" stroke="{c["line"]}" stroke-width="1.5"/>'

# ------------------------------------------------------------ HERO
def hero(t):
    """Fast static SVG fallback; README uses the animated GIF counterpart."""
    c = P[t]; W, H, hz = 1000, 300, 196
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ShadowGaming100 | Developer, Builder, Founder">']
    o.append(f'<defs><clipPath id="all"><rect width="{W}" height="{H}" rx="10"/></clipPath><clipPath id="fl"><rect y="{hz}" width="{W}" height="{H-hz}"/></clipPath></defs>')
    o.append('<g clip-path="url(#all)">')
    o.append(f'<rect width="{W}" height="{H}" fill="{c["card"]}"/>')
    o.append(f'<g clip-path="url(#fl)" stroke="{c["grid"]}" stroke-opacity="{c["gop"]}" stroke-width="1">')
    for xb in range(-1400, 2500, 120):
        o.append(f'<line x1="500" y1="{hz}" x2="{xb}" y2="{H+40}"/>')
    for row in range(7):
        y = hz + 4 + row * 15
        o.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    o.append('</g>')
    o.append(f'<rect y="{hz}" width="{W}" height="1.5" fill="{c["line"]}"/>')
    o.append(cube(140, 150, 34, c["cube"]))
    o.append(cube(862, 128, 28, c["acc"]))
    o.append(f'<text x="500" y="118" text-anchor="middle" font-family="{MONO}" font-weight="800" font-size="56" letter-spacing="6" fill="{c["fg"]}">SHADOWGAMING100</text>')
    o.append(f'<text x="500" y="164" text-anchor="middle" font-family="{MONO}" font-size="22" font-weight="600" letter-spacing="5" fill="{c["sub"]}">DEVELOPER · BUILDER · FOUNDER</text>')
    o.append('</g>')
    o.append(f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="10" fill="none" stroke="{c["line"]}" stroke-width="1.5"/>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ TYPING
LINES = ["Building digital experiences.", "Turning ideas into code.", "Founder of FreeHosts.", "Developer at Nemethic."]
def typing(t, width=760, height=60, size=28):
    c = P[t]; cw = size*.6; ch = .06; dl = .025; hold = 1.7
    T = 0; segs = []
    for s in LINES:
        text = "> " + s; n = len(text)
        segs.append((text, n, T)); T += n*ch + hold + n*dl + .35
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{" / ".join(LINES)}">']
    cur = []
    for i, (text, n, t0) in enumerate(segs):
        w = n*cw; x0 = (width-w)/2
        ev = [(0, 0)] + [(t0+k*ch, k*cw) for k in range(n+1)]
        th = t0+n*ch+hold
        ev += [(th+k*dl, (n-k)*cw) for k in range(1, n+1)]
        vals, kts = reveal_vals(ev, T)
        cur += [(tt, round(x0+v, 2)) for tt, v in ev]
        o.append(f'<clipPath id="c{i}"><rect x="{x0:.2f}" y="0" height="{height}" width="0"><animate attributeName="width" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite" values="{vals}" keyTimes="{kts}"/></rect></clipPath>')
        o.append(f'<g clip-path="url(#c{i})" font-family="{MONO}" font-weight="700" font-size="{size}"><text x="{x0:.2f}" y="{height/2+size*.34:.2f}" xml:space="preserve" textLength="{w:.2f}" lengthAdjust="spacing"><tspan fill="{c["acc"]}">&gt; </tspan><tspan fill="{c["fg"]}">{LINES[i]}</tspan></text></g>')
    cx_vals, cx_k = reveal_vals([(max(0, a), b) for a, b in cur], T)
    o.append(f'<rect y="{height/2-size*.62:.1f}" width="{size*.5:.1f}" height="{size*1.2:.1f}" fill="{c["fg"]}"><animate attributeName="x" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite" values="{cx_vals}" keyTimes="{cx_k}"/><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ SECTION HEADERS
HEADERS = [("about", "01", "About me"), ("roles", "02", "What I do"), ("stack", "03", "Tech stack"),
           ("featured", "04", "Featured project"), ("stats", "05", "GitHub statistics"),
           ("world", "06", "3D contribution world"), ("snake", "07", "Contribution snake"), ("trophies", "08", "Trophies")]
def header(t, num, title, W=760, fs=35):
    c = P[t]; H = 76 if W > 500 else 70
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">']
    num_fs = 22 if W > 500 else 20
    o.append(f'<text x="8" y="50" font-family="{MONO}" font-size="{num_fs}" font-weight="700" fill="{c["acc"]}">{num}</text>')
    o.append(f'<text x="{58 if W > 500 else 50}" y="52" font-family="{SANS}" font-size="{fs}" font-weight="700" fill="{c["fg"]}">{title}</text>')
    o.append(f'<rect x="8" y="{H-8}" width="{W-16}" height="1.5" fill="{c["line"]}"/>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ TERMINAL
TERMINAL_LINES = [
    ("cmd", "$ whoami"), ("out", "Founder & Developer"),
    ("cmd", "$ current-project"), ("out", "FreeHosts v2"),
    ("cmd", "$ interests"), ("out", "Web Development • APIs • Discord Bots"),
    ("cmd", "$ status"), ("out", "Always learning..."),
]

def terminal(mobile=False):
    W, H = (360, 300) if mobile else (760, 330)
    fs = 12 if mobile else 19
    line_h = 27 if mobile else 31
    left = 18 if mobile else 34
    top = 82 if mobile else 94
    max_chars = max(len(text) for _, text in TERMINAL_LINES)
    char_w = fs * (0.61 if mobile else 0.60)
    available = W - left * 2
    if max_chars * char_w > available:
        fs = available / (max_chars * (0.61 if mobile else 0.60))
    type_seconds = [0.72, 0.62, 0.86, 0.48, 0.92, 1.45, 0.62, 0.80]
    starts, cursor = [], 0.65
    for duration in type_seconds:
        starts.append(cursor)
        cursor += duration + 0.20
    cycle = cursor + 1.0
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal animation: Founder and Developer, FreeHosts v2, Web Development, APIs, Discord Bots, Always learning.">',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>',
         f'<path d="M1 47 V10 a9 9 0 0 1 9 -9 H{W-10} a9 9 0 0 1 9 9 V47 Z" fill="#161b22"/>',
         f'<path d="M1 47 H{W-1}" stroke="#30363d"/>']
    for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        o.append(f'<circle cx="{22+i*19}" cy="24" r="5" fill="{col}"/>')
    o.append(f'<text x="{W/2}" y="29" text-anchor="middle" font-family="{MONO}" font-size="{11 if mobile else 14}" fill="#8b949e">shadow@profile: ~</text>')
    for i, ((kind, text), begin, duration) in enumerate(zip(TERMINAL_LINES, starts, type_seconds)):
        y = top + i * line_h
        width = min(available, len(text) * fs * 0.61 + 4)
        vals = f"0;0;{width:.1f};{width:.1f};0"
        kts = f"0;{begin/cycle:.5f};{(begin+duration)/cycle:.5f};0.99900;1"
        clip = f"terminal-line-{i}"
        o.append(f'<clipPath id="{clip}"><rect x="{left}" y="{y-fs}" width="0" height="{line_h}"><animate attributeName="width" values="{vals}" keyTimes="{kts}" dur="{cycle:.2f}s" repeatCount="indefinite"/></rect></clipPath>')
        fill = "#3fb950" if kind == "cmd" else "#e6edf3"
        weight = "700" if kind == "cmd" else "500"
        o.append(f'<text x="{left}" y="{y}" clip-path="url(#{clip})" font-family="{MONO}" font-size="{fs:.1f}" font-weight="{weight}" fill="{fill}" xml:space="preserve">{html.escape(text)}</text>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ TECH STACK
TECH = [
    ("js", "JavaScript", "Language", "#f1d44b", "JS"),
    ("ts", "TypeScript", "Language", "#3178c6", "TS"),
    ("py", "Python", "Language", "#3776ab", "PY"),
    ("html", "HTML", "Language", "#e34f26", "5"),
    ("css", "CSS", "Language", "#1572b6", "3"),
    ("node", "Node.js", "Runtime", "#43853d", "N"),
    ("djs", "Discord.js", "Library", "#5865f2", "D"),
    ("express", "Express.js", "Framework", "#555b66", "EX"),
    ("next", "Next.js", "Framework", "#24292f", "N"),
    ("fastify", "Fastify", "Framework", "#202a2e", "F"),
    ("pg", "PostgreSQL", "Database", "#4169e1", "PG"),
    ("mysql", "MySQL", "Database", "#00758f", "SQL"),
    ("mongo", "MongoDB", "Database", "#47a248", "M"),
    ("cf", "Cloudflare", "Infrastructure", "#f38020", "CF"),
    ("git", "Git", "Tool", "#f05032", "G"),
    ("github", "GitHub", "Tool", "#24292f", "GH"),
    ("gha", "GitHub Actions", "Tool", "#2088ff", "A"),
]

# Official Simple Icons slugs and brand colours. These logos are fetched by
# GitHub Actions and embedded into generated local SVGs, so README rendering
# never depends on a third-party image host.
SIMPLE_ICONS = {
    "js": ("javascript", "F7DF1E"), "ts": ("typescript", "3178C6"),
    "py": ("python", "3776AB"), "html": ("html5", "E34F26"),
    "css": ("css3", "1572B6"), "node": ("nodedotjs", "5FA04E"),
    "djs": ("discord", "5865F2"), "express": ("express", "FFFFFF"),
    "next": ("nextdotjs", "FFFFFF"), "fastify": ("fastify", "FFFFFF"),
    "pg": ("postgresql", "4169E1"), "mysql": ("mysql", "4479A1"),
    "mongo": ("mongodb", "47A248"), "cf": ("cloudflare", "F38020"),
    "git": ("git", "F05032"), "github": ("github", "FFFFFF"),
    "gha": ("githubactions", "2088FF"),
}
_ICON_PATHS = {}


def simple_icon_path(key):
    """Return a validated Simple Icons path, with independent CDN fallbacks.

    The jsDelivr and unpkg URLs use the official simple-icons package and a
    pinned major version. The Simple Icons colour CDN is retained as a final
    fallback, but a 404 from that service must not abort the whole build.
    """
    if key in _ICON_PATHS:
        return _ICON_PATHS[key]

    slug, brand = SIMPLE_ICONS[key]
    urls = (
        f"https://cdn.jsdelivr.net/npm/simple-icons@v16/icons/{slug}.svg",
        f"https://unpkg.com/simple-icons@v16/icons/{slug}.svg",
        f"https://cdn.simpleicons.org/{slug}/{brand}",
    )
    errors = []

    for url in urls:
        # A missing icon on one CDN is not a reason to fail while another
        # official mirror may still have it. Retry only transient failures.
        for attempt in range(2):
            try:
                request = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "ShadowGaming100-profile-assets/1.0",
                        "Accept": "image/svg+xml,text/plain,*/*",
                    },
                )
                with urllib.request.urlopen(request, timeout=15) as response:
                    source = response.read(250_000).decode("utf-8")

                if "<svg" not in source.lower():
                    raise RuntimeError(f"{url} did not return an SVG document")

                paths = re.findall(
                    r'<path\b[^>]*\bd\s*=\s*["\']([^"\']+)["\'][^>]*/?>',
                    source,
                    flags=re.IGNORECASE,
                )
                if not paths:
                    raise RuntimeError(f"{url} returned an SVG without a path")

                _ICON_PATHS[key] = paths
                return paths

            except urllib.error.HTTPError as exc:
                errors.append(f"{url}: HTTP {exc.code}")
                # 4xx responses are permanent for this URL; try the next CDN.
                if 400 <= exc.code < 500 and exc.code != 429:
                    break
                if attempt == 1:
                    break
            except (OSError, UnicodeError, urllib.error.URLError, RuntimeError) as exc:
                errors.append(f"{url}: {exc}")
                if attempt == 1:
                    break

    detail = "; ".join(errors[-len(urls):])
    raise RuntimeError(
        f"Unable to download the official {key} ({slug}) logo from any configured CDN. "
        f"Tried jsDelivr, unpkg, and Simple Icons CDN. {detail}"
    )


def tech_icon(theme, key, name, color, mark):
    c = P[theme]
    paths = simple_icon_path(key)
    # Monochrome marks invert between themes so they remain legible.
    logo_color = color
    if key in ("express", "next", "github"):
        logo_color = "#ffffff" if theme == "dark" else "#24292f"
    logo = "".join(
        f'<path d="{path}" fill="{logo_color}"/>'
        for path in paths
    )
    mark_svg = f'<svg x="31" y="31" width="42" height="42" viewBox="0 0 24 24" aria-hidden="true">{logo}</svg>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 104 104" width="104" height="104" role="img" aria-label="{html.escape(name)}">
<rect x="1" y="1" width="102" height="102" rx="18" fill="{c['card']}" stroke="{c['line']}" stroke-width="2"/>
{mark_svg}
</svg>"""


def tile(theme, index):
    key, name, category, color, mark = TECH[index]
    return tech_icon(theme, key, name, color, mark)

# ------------------------------------------------------------ ROLE CARDS
def role_card(t, kind):
    c = P[t]; W, H = 495, 250
    lab, title, desc = (("Founder", "FreeHosts", ["Community-driven directory", "of free hosting providers."]) if kind == 0
                        else ("Developer", "Nemethic", ["Developer at Nemethic.", "JavaScript · Node.js", "PostgreSQL"]))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{lab}: {title}">', box(W, H, c)]
    ix, iy = 82, 122
    if kind == 0:
        o.append(f'<ellipse cx="{ix}" cy="{iy+56}" rx="40" ry="8" fill="{c["fg"]}" opacity=".1"/><g>{bob(6, 3.6)}{fh_logo(ix-46, iy-46, 92, c)}</g>')
    else:
        o.append(f'<g>{bob(8, 3.8)}{cube(ix, iy, 44, c["acc"], "&lt;/&gt;", "#fff", 16)}</g>')
    o.append(f'<text x="170" y="62" font-family="{SANS}" font-size="20" font-weight="600" fill="{c["acc"]}">{lab}</text>')
    o.append(f'<text x="170" y="116" font-family="{SANS}" font-size="48" font-weight="700" fill="{c["fg"]}">{title}</text>')
    for q, d in enumerate(desc):
        o.append(f'<text x="170" y="{152+q*30}" font-family="{SANS}" font-size="22" fill="{c["sub"]}">{d}</text>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ FEATURED
def featured(t):
    c = P[t]; W, H = 1000, 350
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Featured project: FreeHosts, a community-driven directory for discovering free hosting providers. freehosts.eu">']
    o.append(box(W, H, c))
    cx = 200
    o.append(f'<ellipse cx="{cx}" cy="290" rx="90" ry="16" fill="{c["fg"]}" opacity=".1"><animate attributeName="rx" values="90;70;90" dur="4s" repeatCount="indefinite" {SPL}/></ellipse>')
    o.append(f'<g>{bob(12, 4)}{fh_logo(cx-100, 70, 200, c)}</g>')
    tx = 410
    o.append(f'<text x="{tx}" y="84" font-family="{SANS}" font-size="22" font-weight="600" fill="{c["acc"]}">freehosts.eu</text>')
    o.append(f'<text x="{tx}" y="160" font-family="{SANS}" font-size="76" font-weight="800" fill="{c["fg"]}">FreeHosts</text>')
    o.append(f'<text x="{tx}" y="205" font-family="{SANS}" font-size="25" fill="{c["sub"]}">A community-driven directory for</text>')
    o.append(f'<text x="{tx}" y="238" font-family="{SANS}" font-size="25" fill="{c["sub"]}">discovering free hosting providers.</text>')
    o.append(f'<rect x="{tx}" y="268" width="270" height="52" rx="6" fill="{c["acc"]}"/>'
             f'<text x="{tx+26}" y="302" font-family="{SANS}" font-size="22" font-weight="600" fill="#fff">Explore FreeHosts</text>'
             f'<path d="M{tx+228} 306 L{tx+242} 292 M{tx+230} 291 H{tx+243} V304" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ FEATURED (phone layout)
def featured_m(t):
    c = P[t]; W, H = 600, 600
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Featured project: FreeHosts, a community-driven directory for discovering free hosting providers. freehosts.eu">']
    o.append(box(W, H, c))
    o.append(f'<ellipse cx="300" cy="238" rx="84" ry="15" fill="{c["fg"]}" opacity=".1"><animate attributeName="rx" values="84;66;84" dur="4s" repeatCount="indefinite" {SPL}/></ellipse>')
    o.append(f'<g>{bob(10, 4)}{fh_logo(205, 52, 190, c)}</g>')
    o.append(f'<text x="300" y="300" text-anchor="middle" font-family="{SANS}" font-size="28" font-weight="600" fill="{c["acc"]}">freehosts.eu</text>')
    o.append(f'<text x="300" y="378" text-anchor="middle" font-family="{SANS}" font-size="78" font-weight="800" fill="{c["fg"]}">FreeHosts</text>')
    for q, d in enumerate(["A community-driven directory", "for discovering free", "hosting providers."]):
        o.append(f'<text x="300" y="{428+q*38}" text-anchor="middle" font-family="{SANS}" font-size="30" fill="{c["sub"]}">{d}</text>')
    o.append(f'<rect x="110" y="520" width="380" height="60" rx="8" fill="{c["acc"]}"/>'
             f'<text x="300" y="560" text-anchor="middle" font-family="{SANS}" font-size="28" font-weight="600" fill="#fff">Explore FreeHosts</text>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ BUTTONS
GH = "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
def button(t, name, label, w=230):
    """Solid buttons with a raised bottom edge. All the same width so they stack neatly on phones."""
    c = P[t]; H = 64; fh = 54
    if name == "github":   face, edge, txt, ic = c["fg"], mix(c["fg"], c["bg"], .55), c["bg"], c["bg"]
    elif name == "freehosts": face, edge, txt, ic = c["acc"], mix(c["acc"], "#000000", .4), "#ffffff", None
    else:                  face, edge, txt, ic = c["card"], c["line"], c["fg"], c["fg"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {H}" width="{w}" height="{H}" role="img" aria-label="{label}">']
    o.append(f'<rect x="1" y="6" width="{w-2}" height="{fh}" rx="12" fill="{edge}"/>')
    stroke = f' stroke="{c["line"]}" stroke-width="1.5"' if name == "contact" else ""
    o.append(f'<rect x="1" y="2" width="{w-2}" height="{fh}" rx="12" fill="{face}"{stroke}/>')
    cy = 2 + fh/2
    if name == "github":
        o.append(f'<g transform="translate(26 {cy-15:.1f}) scale(1.25)"><path fill="{ic}" d="{GH}"/></g>')
    elif name == "freehosts":
        o.append(f'<rect x="22" y="{cy-19:.1f}" width="38" height="38" rx="9" fill="#fff"/>{fh_logo(26, cy-15, 30, c)}')
    else:
        o.append(f'<g transform="translate(26 {cy-15:.1f}) scale(1.25)" fill="none" stroke="{ic}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="m3.5 7.5 8.5 6 8.5-6"/></g>')
    tx = 76 if name != "freehosts" else 76
    o.append(f'<text x="{tx}" y="{cy+8:.1f}" font-family="{SANS}" font-size="24" font-weight="700" fill="{txt}">{label}</text>')
    o.append('</svg>')
    return "\n".join(o)

# ------------------------------------------------------------ FOOTER
def footer(t):
    c = P[t]; W, H = 1000, 70
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="© ShadowGaming100">
<rect x="8" y="10" width="{W-16}" height="1.5" fill="{c['line']}"/>
<text x="500" y="48" text-anchor="middle" font-family="{SANS}" font-size="20" fill="{c['sub']}">© ShadowGaming100</text></svg>'''

# ------------------------------------------------------------ WRITE
os.makedirs(f"{A}/stack", exist_ok=True)
# Fetch all official brand marks concurrently so a slow CDN cannot delay every tile.
with ThreadPoolExecutor(max_workers=12) as workers:
    list(workers.map(simple_icon_path, [tech[0] for tech in TECH]))
for t in ("dark", "light"):
    write(f"hero.{t}.svg", hero(t)); write(f"typing.{t}.svg", typing(t)); write(f"footer.{t}.svg", footer(t))
    write(f"featured.{t}.svg", featured(t)); write(f"featured.m.{t}.svg", featured_m(t))
    write(f"role.founder.{t}.svg", role_card(t, 0)); write(f"role.developer.{t}.svg", role_card(t, 1))
    for i, tech in enumerate(TECH): write(f"stack/{tech[0]}.{t}.svg", tile(t, i))
    for key, num, title in HEADERS:
        write(f"headers/{key}.{t}.svg", header(t, num, title))
        write(f"headers/{key}.m.{t}.svg", header(t, num, title, W=420, fs=30))
    for name, label in (("github", "GitHub"), ("freehosts", "FreeHosts"), ("contact", "Contact")):
        write(f"buttons/{name}.{t}.svg", button(t, name, label))
write("terminal.svg", terminal(False))
write("terminal.m.svg", terminal(True))
print(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(A) for f in fs if f.endswith(".svg")) // 1024, "KB svg")
