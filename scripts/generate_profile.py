#!/usr/bin/env python3
"""Generate and validate every ShadowGaming100 profile asset in one script."""

from __future__ import annotations
import re
def _run_artwork():
    """Run the artwork stage."""
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
        # Simple Icons uses the canonical slug "css" (not "css3").
        # The old slug returned 404 from every CDN and aborted the build.
        "css": ("css", "1572B6"), "node": ("nodedotjs", "5FA04E"),
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

def _run_animated_gifs():
    """Run the animated gifs stage."""
    """Create lightweight, smoothly animated GIF versions of README motion artwork."""

    import math
    import re
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

def _run_all_time_graphs():
    """Run the all time graphs stage."""
    """Generate a 3D contribution calendar covering the account's full available history."""
    import datetime as dt
    import json
    import os
    import sys
    import urllib.error
    import urllib.request
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    OUT = ROOT / "profile-3d-contrib"
    API = "https://api.github.com/graphql"


    def request_json(url, token=None, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ShadowGaming100-profile-assets",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            url, data=data, headers=headers, method="POST" if data else "GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            raise RuntimeError(
                f"GitHub API returned HTTP {exc.code}: {body[:500]}"
            ) from exc


    def fetch_year(token, username, year, through):
        start = dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc)
        end = min(
            dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc),
            through,
        )
        query = """
        query($login: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $from, to: $to) {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
          }
        }
        """
        result = request_json(
            API,
            token,
            {
                "query": query,
                "variables": {
                    "login": username,
                    "from": start.isoformat().replace("+00:00", "Z"),
                    "to": end.isoformat().replace("+00:00", "Z"),
                },
            },
        )
        if result.get("errors"):
            messages = "; ".join(
                error.get("message", "unknown") for error in result["errors"]
            )
            raise RuntimeError("GitHub GraphQL error: " + messages)
        user = result.get("data", {}).get("user")
        if not user:
            raise RuntimeError(f"GitHub user not found: {username}")
        calendar = user["contributionsCollection"]["contributionCalendar"]
        calendar["weeks"] = [
            {
                "contributionDays": [
                    day
                    for day in week.get("contributionDays", [])
                    if dt.date(year, 1, 1)
                    <= dt.date.fromisoformat(day["date"])
                    <= end.date()
                ]
            }
            for week in calendar.get("weeks", [])
        ]
        return calendar


    def shade(theme, count):
        palettes = {
            "dark": ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"],
            "light": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        }
        palette = palettes[theme]
        if count <= 0:
            return palette[0]
        if count <= 2:
            return palette[1]
        if count <= 5:
            return palette[2]
        if count <= 9:
            return palette[3]
        return palette[4]


    def cube(x, y, count, theme):
        fill = shade(theme, count)
        height = 1.5 if count == 0 else min(13, 3 + count * 1.25)
        half_w, half_h = 5.2, 3.2
        top_y = y - height
        top = (
            f"{x},{top_y} {x+half_w},{top_y+half_h} "
            f"{x},{top_y+2*half_h} {x-half_w},{top_y+half_h}"
        )
        left = (
            f"{x-half_w},{top_y+half_h} {x},{top_y+2*half_h} "
            f"{x},{y+2*half_h} {x-half_w},{y+half_h}"
        )
        right = (
            f"{x},{top_y+2*half_h} {x+half_w},{top_y+half_h} "
            f"{x+half_w},{y+half_h} {x},{y+2*half_h}"
        )
        left_fill, right_fill = (
            ("#0a3520", "#092d1c")
            if theme == "dark"
            else ("#238b45", "#176b36")
        )
        opacity = "1" if count else (".62" if theme == "dark" else ".8")
        return (
            f'<g opacity="{opacity}"><polygon points="{left}" fill="{left_fill}"/>'
            f'<polygon points="{right}" fill="{right_fill}"/>'
            f'<polygon points="{top}" fill="{fill}"/></g>'
        )


    def render(years, theme, through, title="ALL-TIME CONTRIBUTION HISTORY", subtitle=None):
        width = 920
        margin_x = 94
        week_step = 15.0
        day_step = 14.0
        year_gap = 178
        top = 100
        height = top + len(years) * year_gap + 30
        if theme == "dark":
            bg, fg, muted, border = "#0d1117", "#e6edf3", "#8b949e", "#30363d"
        else:
            bg, fg, muted, border = "#ffffff", "#1f2328", "#59636e", "#d0d7de"

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="All-time 3D GitHub contribution history">',
            f'<rect width="{width}" height="{height}" rx="12" fill="{bg}"/>',
            f'<text x="34" y="42" font-family="system-ui,sans-serif" font-size="24" font-weight="700" fill="{fg}">{title}</text>',
            f'<text x="34" y="68" font-family="system-ui,sans-serif" font-size="13" fill="{muted}">{subtitle or ("From the first available contribution through " + through.date().isoformat())}</text>',
        ]

        for index, (year, calendar) in enumerate(years):
            base_y = top + index * year_gap
            total = calendar.get("totalContributions", 0)
            svg.append(
                f'<text x="34" y="{base_y+18}" font-family="system-ui,sans-serif" font-size="17" font-weight="700" fill="{fg}">{year}</text>'
            )
            svg.append(
                f'<text x="34" y="{base_y+38}" font-family="system-ui,sans-serif" font-size="11" fill="{muted}">{total:,} contributions</text>'
            )
            svg.append(
                f'<line x1="{margin_x-16}" y1="{base_y+4}" x2="{width-30}" y2="{base_y+4}" stroke="{border}" stroke-width="1"/>'
            )
            for week_index, week in enumerate(calendar.get("weeks", [])):
                for day in week.get("contributionDays", []):
                    date = dt.date.fromisoformat(day["date"])
                    x = margin_x + week_index * week_step
                    y = base_y + 58 + date.weekday() * day_step
                    svg.append(
                        cube(x, y, int(day.get("contributionCount", 0)), theme)
                    )

        svg.append("</svg>")
        return "\n".join(svg)


    def main():
        token = os.environ.get("GITHUB_TOKEN")
        username = os.environ.get("USERNAME", "ShadowGaming100")
        if not token:
            raise RuntimeError("GITHUB_TOKEN is required")

        user = request_json(f"https://api.github.com/users/{username}", token)
        created = dt.datetime.fromisoformat(
            user["created_at"].replace("Z", "+00:00")
        ).date()
        through = dt.datetime.now(dt.timezone.utc)
        first_year = created.year
        current_year = through.year
        years = []

        for year in range(first_year, current_year + 1):
            print(
                f"Fetching {username}'s {year} contribution calendar...",
                flush=True,
            )
            years.append((year, fetch_year(token, username, year, through)))

        OUT.mkdir(parents=True, exist_ok=True)
        calendars = {year: calendar for year, calendar in years}

        # 1. Current calendar year and 2. previous calendar year.
        for year in (current_year, current_year - 1):
            calendar = calendars.get(year)
            if calendar is None:
                continue
            date_range = (
                f"January 1 – {through.date().isoformat()}"
                if year == current_year
                else "January 1 – December 31"
            )
            subtitle = (
                f"{calendar.get('totalContributions', 0):,} contributions · "
                f"{date_range}"
            )
            for theme, prefix in (("light", "profile"), ("dark", "profile-night")):
                (OUT / f"{prefix}-{year}.svg").write_text(
                    render([(year, calendar)], theme, through,
                           f"{year} CONTRIBUTIONS", subtitle),
                    encoding="utf-8",
                )

        total = sum(
            calendar.get("totalContributions", 0)
            for _year, calendar in years
        )
        span = f"{first_year}–{current_year} · {total:,} contributions"

        # 3. All Years: every available calendar year combined in one image.
        # 4. All Time: the complete available history, from account creation
        #    through today. It uses the same complete yearly data, but has its
        #    own explicitly labelled output for the README.
        combined_outputs = (
            ("all-years", "ALL YEARS — CALENDAR CONTRIBUTIONS"),
            ("all-time", "ALL-TIME CONTRIBUTION HISTORY"),
        )
        for suffix, title in combined_outputs:
            subtitle = (
                f"{span} · through {through.date().isoformat()}"
            )
            for theme, prefix in (("light", "profile"), ("dark", "profile-night")):
                (OUT / f"{prefix}-{suffix}.svg").write_text(
                    render(years, theme, through, title, subtitle),
                    encoding="utf-8",
                )

        # Remove obsolete individual-year SVGs; retain only current/previous.
        keep_years = {current_year, current_year - 1}
        for old_svg in OUT.glob("profile-*.svg"):
            match = re.fullmatch(r"profile-(?:night-)?(\d{4})\.svg", old_svg.name)
            if match and int(match.group(1)) not in keep_years:
                old_svg.unlink(missing_ok=True)

        # Keep exactly four contribution sections in the README.
        readme = ROOT / "README.md"
        if readme.is_file():
            content = readme.read_text(encoding="utf-8")
            start_marker = "<!-- CONTRIBUTION-YEARS:START -->"
            end_marker = "<!-- CONTRIBUTION-YEARS:END -->"
            if start_marker in content and end_marker in content:
                entries = [
                    start_marker,
                    "",
                    f"  **Current Year — {current_year} Calendar Contributions**",
                    "",
                    "  <picture>",
                    f'    <source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-{current_year}.svg" />',
                    f'    <img src="./profile-3d-contrib/profile-{current_year}.svg" width="100%" alt="3D GitHub contribution graph for calendar year {current_year}" />',
                    "  </picture>",
                    "",
                    f"  **Last Year — {current_year - 1} Calendar Contributions**",
                    "",
                    "  <picture>",
                    f'    <source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-{current_year - 1}.svg" />',
                    f'    <img src="./profile-3d-contrib/profile-{current_year - 1}.svg" width="100%" alt="3D GitHub contribution graph for calendar year {current_year - 1}" />',
                    "  </picture>",
                    "",
                    "  **All Years — Combined Calendar Contributions**",
                    "",
                    "  <picture>",
                    '    <source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-all-years.svg" />',
                    '    <img src="./profile-3d-contrib/profile-all-years.svg" width="100%" alt="All available calendar years combined into one 3D contribution image" />',
                    "  </picture>",
                    "",
                    "  **All Time — Complete Available Contribution History**",
                    "",
                    "  <picture>",
                    '    <source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-all-time.svg" />',
                    '    <img src="./profile-3d-contrib/profile-all-time.svg" width="100%" alt="Complete available 3D GitHub contribution history through today" />',
                    "  </picture>",
                    "",
                    end_marker,
                ]
                before, remainder = content.split(start_marker, 1)
                _old, after = remainder.split(end_marker, 1)
                readme.write_text(
                    before + "\n".join(entries) + after,
                    encoding="utf-8",
                )

        print(
            f"Generated exactly four contribution sections: {current_year}, "
            f"{current_year - 1}, All Years, and All Time "
            f"({first_year}–{current_year}; {total:,} contributions)."
        )

    if __name__ == "__main__":
        try:
            main()
        except Exception as exc:
            print(f"::error::{exc}", file=sys.stderr)
            raise

def _run_contribution_snake():
    """Run the contribution snake stage."""
    """Generate a smooth, infinitely looping contribution snake GIF from GitHub data."""

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

def _run_asset_validation():
    """Run the asset validation stage."""
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

def main():
    """Run all generation stages and validate the final README assets."""
    _run_artwork()
    _run_all_time_graphs()
    _run_contribution_snake()
    _run_animated_gifs()
    _run_asset_validation()


if __name__ == "__main__":
    main()
