import os, math, random, shutil

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = OUT + "/assets"
for d in ("headers", "buttons"):
    os.makedirs(f"{A}/{d}", exist_ok=True)

MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',system-ui,-apple-system,Roboto,'Helvetica Neue',Arial,sans-serif"

P = {
 "dark": dict(bg0="#04050a", bg1="#0a0c16", bg2="#151a33", fg="#f5f7ff", sub="#9ba3bd", mute="#5c647d",
              a1="#8b5cf6", a2="#22d3ee", a3="#f472b6", card="#0e1120", cop=".78", edge="#ffffff", orb=".95"),
 "light": dict(bg0="#f4f6fd", bg1="#e9edfb", bg2="#d9def5", fg="#0b0d14", sub="#4a5068", mute="#8a90a8",
              a1="#6d3df0", a2="#0891b2", a3="#db2777", card="#ffffff", cop=".85", edge="#000000", orb=".5"),
}

def hx(c): c=c.lstrip("#"); return [int(c[i:i+2],16) for i in (0,2,4)]
def mix(c1, c2, t):
    a, b = hx(c1), hx(c2)
    return "#%02x%02x%02x" % tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
def write(path, s): open(f"{A}/{path}", "w", encoding="utf-8").write(s)
SPL = 'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" keyTimes="0;.5;1"'

def bob(amp, dur, begin=0):
    return f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-amp};0 0" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite" {SPL}/>'

def cube(cx, cy, s, col, label=None, txt="#fff", fs=None):
    k = .866
    top = mix(col, "#ffffff", .30); left = col; right = mix(col, "#000000", .38)
    o = f'<polygon points="{cx},{cy-s} {cx+k*s},{cy-s/2} {cx},{cy} {cx-k*s},{cy-s/2}" fill="{top}"/>'
    o += f'<polygon points="{cx-k*s},{cy-s/2} {cx},{cy} {cx},{cy+s} {cx-k*s},{cy+s/2}" fill="{left}"/>'
    o += f'<polygon points="{cx},{cy} {cx+k*s},{cy-s/2} {cx+k*s},{cy+s/2} {cx},{cy+s}" fill="{right}"/>'
    o += f'<polyline points="{cx-k*s},{cy-s/2} {cx},{cy} {cx+k*s},{cy-s/2} M{cx},{cy} {cx},{cy+s}" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="1"/>'
    if label:
        fs = fs or s*.36
        o += f'<text transform="matrix(0.866,0.5,0,1,{cx-k*s:.2f},{cy-s/2:.2f})" x="{s/2:.2f}" y="{s*.68:.2f}" text-anchor="middle" font-family="{MONO}" font-weight="800" font-size="{fs:.1f}" fill="{txt}">{label}</text>'
    return o

def slab(cx, cy, s, h, col):
    k = .866
    top = mix(col, "#ffffff", .22); right = mix(col, "#000000", .42)
    return (f'<polygon points="{cx},{cy-s/2} {cx+k*s},{cy} {cx},{cy+s/2} {cx-k*s},{cy}" fill="{top}"/>'
            f'<polygon points="{cx-k*s},{cy} {cx},{cy+s/2} {cx},{cy+s/2+h} {cx-k*s},{cy+h}" fill="{col}"/>'
            f'<polygon points="{cx},{cy+s/2} {cx+k*s},{cy} {cx+k*s},{cy+h} {cx},{cy+s/2+h}" fill="{right}"/>'
            f'<polyline points="{cx-k*s},{cy} {cx},{cy+s/2} {cx+k*s},{cy}" fill="none" stroke="#fff" stroke-opacity=".3"/>')

def reveal_vals(events, T):
    """events: [(time, value)] -> (values, keyTimes) for discrete animation over cycle T"""
    ev = sorted(events, key=lambda e: e[0])
    if ev[0][0] > 0: ev = [(0, 0)] + ev
    vals = [str(v) for _, v in ev]; kts = [tt / T for tt, _ in ev]
    kts[0] = 0.0
    return ";".join(vals), ";".join(f"{min(k,1):.5f}" for k in kts)

# ---------------------------------------------------------------- HERO
def hero(t):
    c = P[t]; W, H, hz = 1000, 372, 246
    rnd = random.Random(7)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ShadowGaming100 | Developer, Builder, Founder">']
    o.append(f'''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c['bg0']}"/><stop offset=".7" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c['bg2']}"/><stop offset="1" stop-color="{c['bg0']}"/></linearGradient>
<radialGradient id="orb" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c['a3']}"/><stop offset=".55" stop-color="{c['a1']}"/><stop offset="1" stop-color="{c['a1']}" stop-opacity="0"/></radialGradient>
<linearGradient id="hz" x1="0" x2="1"><stop offset="0" stop-color="{c['a2']}" stop-opacity="0"/><stop offset=".5" stop-color="{c['a2']}"/><stop offset="1" stop-color="{c['a2']}" stop-opacity="0"/></linearGradient>
<linearGradient id="tg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1000" y2="0"><stop offset="0" stop-color="{c['fg']}"/><stop offset=".42" stop-color="{c['fg']}"/><stop offset=".5" stop-color="{c['a2']}"/><stop offset=".58" stop-color="{c['fg']}"/><stop offset="1" stop-color="{c['fg']}"/><animateTransform attributeName="gradientTransform" type="translate" from="-1000 0" to="1000 0" dur="7s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{c['a1']}"/><stop offset=".5" stop-color="{c['a2']}"/><stop offset="1" stop-color="{c['a3']}"/></linearGradient>
<clipPath id="sk"><rect width="{W}" height="{hz}"/></clipPath>
<clipPath id="fl"><rect y="{hz}" width="{W}" height="{H-hz}"/></clipPath>
<clipPath id="all"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>''')
    o.append('<g clip-path="url(#all)">')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    # stars
    for _ in range(46):
        x, y, r = rnd.uniform(10, 990), rnd.uniform(8, hz-30), rnd.choice([.8, 1, 1.3, 1.7])
        d = rnd.uniform(2, 5); b = rnd.uniform(0, 5)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{c["fg"]}" opacity=".2"><animate attributeName="opacity" values=".1;.9;.1" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/></circle>')
    # orb
    o.append(f'<g clip-path="url(#sk)"><circle cx="500" cy="{hz}" r="200" fill="url(#orb)" opacity="{c["orb"]}"><animate attributeName="r" values="196;206;196" dur="6s" repeatCount="indefinite" {SPL}/></circle>')
    for i, (yy, hh) in enumerate([(222, 2), (228, 3), (234, 4), (240, 6)]):
        o.append(f'<rect x="300" y="{yy}" width="400" height="{hh}" fill="{c["bg1"]}" opacity=".85"/>')
    o.append('</g>')
    # floor
    o.append(f'<rect y="{hz}" width="{W}" height="{H-hz}" fill="url(#floor)"/>')
    o.append(f'<g clip-path="url(#fl)" stroke="{c["a1"]}" stroke-opacity=".55" stroke-width="1">')
    for xb in range(-1400, 2500, 110):
        o.append(f'<line x1="500" y1="{hz}" x2="{xb}" y2="{H+40}"/>')
    o.append('</g>')
    N, dur = 9, 4.5
    o.append(f'<g clip-path="url(#fl)">')
    for k in range(N):
        ys = ";".join(f"{hz + (H-hz+6)*(u/12)**2.2:.1f}" for u in range(13))
        os_ = ";".join(f"{min(1,(u/12)*1.8):.2f}" for u in range(13))
        hs = ";".join(f"{.6+(u/12)*2.2:.2f}" for u in range(13))
        o.append(f'<rect x="0" width="{W}" fill="{c["a2"]}" y="{hz}" height=".6" opacity="0">'
                 f'<animate attributeName="y" values="{ys}" dur="{dur}s" begin="-{k*dur/N:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="{os_}" dur="{dur}s" begin="-{k*dur/N:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="height" values="{hs}" dur="{dur}s" begin="-{k*dur/N:.2f}s" repeatCount="indefinite"/></rect>')
    o.append('</g>')
    o.append(f'<rect x="0" y="{hz-1}" width="{W}" height="2.5" fill="url(#hz)"/>')
    o.append(f'<rect x="150" y="{hz-3}" width="700" height="7" fill="url(#hz)" opacity=".5" filter="url(#gl)"/>')
    # floating cubes
    for (x, y, s, col, amp, d, b) in [(135, 190, 34, c['a1'], 12, 5, 0), (868, 160, 28, c['a2'], 10, 4.2, 1.5),
                                      (265, 84, 15, c['a3'], 8, 3.6, .8), (742, 78, 17, c['a1'], 9, 4.8, 2.4)]:
        o.append(f'<g><ellipse cx="{x}" cy="{hz+22+(y>150)*0}" rx="{s*.9:.0f}" ry="{s*.22:.0f}" fill="{col}" opacity=".22" filter="url(#gl)"/>'
                 f'{bob(amp, d, b)}{cube(x, y, s, col)}</g>')
    # title
    word = "SHADOWGAMING100"; fs = 54; cw = 43.5; x0 = 500 - cw*len(word)/2 + cw/2
    o.append(f'<g font-family="{MONO}" font-weight="800" font-size="{fs}" fill="url(#tg)" text-anchor="middle">')
    for i, ch in enumerate(word):
        o.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".5s" begin="{.1+i*.06:.2f}s" fill="freeze"/>'
                 f'<animateTransform attributeName="transform" type="translate" from="0 18" to="0 0" dur=".6s" begin="{.1+i*.06:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>'
                 f'<text x="{x0+i*cw:.1f}" y="150">{ch}</text></g>')
    o.append('</g>')
    o.append(f'<rect x="350" y="168" width="300" height="3" rx="1.5" fill="url(#bar)" opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".4s" begin="1.1s" fill="freeze"/><animate attributeName="width" from="0" to="300" dur=".9s" begin="1.1s" fill="freeze"/><animate attributeName="x" from="500" to="350" dur=".9s" begin="1.1s" fill="freeze"/></rect>')
    o.append(f'<text x="500" y="204" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="600" letter-spacing="8" fill="{c["sub"]}" opacity="0">DEVELOPER · BUILDER · FOUNDER<animate attributeName="opacity" from="0" to="1" dur=".8s" begin="1.3s" fill="freeze"/></text>')
    o.append('</g>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{c["edge"]}" stroke-opacity=".14"/>')
    o.append('</svg>')
    return "\n".join(o)

# ---------------------------------------------------------------- TYPING
LINES = ["Building digital experiences.", "Turning ideas into code.", "Founder of FreeHosts.", "Developer at Nemethic."]
def typing(t, width=720, height=48, size=19):
    c = P[t]; cw = size*.6; ch = .06; dl = .025; hold = 1.7
    T = 0; segs = []
    for s in LINES:
        text = "> " + s; n = len(text)
        segs.append((text, n, T)); T += n*ch + hold + n*dl + .35
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{" / ".join(LINES)}">']
    cur_ev = []
    for i, (text, n, t0) in enumerate(segs):
        w = n*cw; x0 = (width-w)/2
        ev = [(0, 0)] + [(t0+k*ch, k*cw) for k in range(n+1)]
        th = t0+n*ch+hold
        ev += [(th+k*dl, (n-k)*cw) for k in range(1, n+1)]
        vals, kts = reveal_vals(ev, T)
        cur_ev += [(tt, round(x0+v, 2)) for tt, v in ev]
        o.append(f'<clipPath id="c{i}"><rect x="{x0:.2f}" y="0" height="{height}" width="0"><animate attributeName="width" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite" values="{vals}" keyTimes="{kts}"/></rect></clipPath>')
        o.append(f'<g clip-path="url(#c{i})" font-family="{MONO}" font-weight="700" font-size="{size}"><text x="{x0:.2f}" y="{height/2+size*.34:.2f}" xml:space="preserve" textLength="{w:.2f}" lengthAdjust="spacing"><tspan fill="{c["a1"]}">&gt; </tspan><tspan fill="{c["fg"]}">{LINES[i]}</tspan></text></g>')
    # cursor follows
    cur_ev.sort(key=lambda e: e[0])
    cx_vals, cx_k = reveal_vals([(max(0, a), b) for a, b in cur_ev], T)
    o.append(f'<rect y="{height/2-size*.62:.1f}" width="{size*.5:.1f}" height="{size*1.2:.1f}" fill="{c["a2"]}"><animate attributeName="x" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite" values="{cx_vals}" keyTimes="{cx_k}"/><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur=".9s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    o.append('</svg>')
    return "\n".join(o)

# ---------------------------------------------------------------- SECTION HEADERS
HEADERS = [("about", "01", "ABOUT ME"), ("roles", "02", "WHAT I DO"), ("stack", "03", "TECH STACK"),
           ("featured", "04", "FEATURED PROJECT"), ("stats", "05", "GITHUB STATISTICS"),
           ("world", "06", "3D CONTRIBUTION WORLD"), ("snake", "07", "CONTRIBUTION SNAKE"), ("trophies", "08", "TROPHIES")]
def header(t, num, title):
    c = P[t]; W, H = 1000, 70; fs = 24; adv = fs*.64 + 5
    tx = 78; tw = len(title)*adv; lx = tx + tw + 22
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">']
    o.append(f'''<defs><linearGradient id="ln" gradientUnits="userSpaceOnUse" x1="{lx:.0f}" y1="0" x2="{W-20}" y2="0"><stop offset="0" stop-color="{c['a1']}"/><stop offset=".6" stop-color="{c['a2']}"/><stop offset="1" stop-color="{c['a2']}" stop-opacity="0"/></linearGradient>
<filter id="gl" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3"/></filter></defs>''')
    o.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="3.6s" repeatCount="indefinite" {SPL}/>{cube(34, 33, 15, c["a1"])}</g>')
    o.append(f'<text x="{tx-14}" y="22" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="3" fill="{c["a2"]}">{num}</text>')
    o.append(f'<text x="{tx}" y="48" font-family="{SANS}" font-weight="800" font-size="{fs}" letter-spacing="5" fill="{c["fg"]}" opacity="0">{title}<animate attributeName="opacity" from="0" to="1" dur=".6s" fill="freeze"/></text>')
    L = W - 20 - lx
    o.append(f'<line x1="{lx:.0f}" y1="40" x2="{W-20}" y2="40" stroke="url(#ln)" stroke-width="2" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"><animate attributeName="stroke-dashoffset" from="100" to="0" dur="1.2s" fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1" keyTimes="0;1"/></line>')
    for r, op, f in ((3.2, 1, ""), (7, .5, ' filter="url(#gl)"')):
        o.append(f'<circle r="{r}" cy="40" fill="{c["a2"]}" opacity="{op}"{f}><animate attributeName="cx" values="{lx:.0f};{W-20}" dur="3.6s" begin="1.2s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1" keyTimes="0;1"/><animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;.1;.85;1" dur="3.6s" begin="1.2s" repeatCount="indefinite"/></circle>')
    o.append('</svg>')
    return "\n".join(o)

# ---------------------------------------------------------------- TERMINAL (same in both themes)
def terminal():
    W, H = 1000, 250; cw = 8.6; fs = 14.5
    rows = [("cmd", "whoami"), ("out", "ShadowGaming100"), ("cmd", "cat roles.txt"), ("out", "Founder @ FreeHosts  ·  Developer @ Nemethic"),
            ("cmd", "echo $STACK"), ("out", "JavaScript / Node.js / PostgreSQL"), ("cmd", "./build --purpose"), ("out", "Building digital experiences. [ OK ]")]
    T = 17.0; t = .8; ytop = 82; lh = 17; x0 = 36
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal: ShadowGaming100, Founder at FreeHosts, Developer at Nemethic, JavaScript Node.js PostgreSQL">']
    o.append('''<defs><linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#8b5cf6"/><stop offset=".5" stop-color="#22d3ee"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0d18"/><stop offset="1" stop-color="#141830"/></linearGradient></defs>''')
    o.append(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="14" fill="url(#bg)"/>')
    o.append(f'<rect x="8" y="8" width="{W-16}" height="34" rx="14" fill="#1b1f38"/><rect x="8" y="30" width="{W-16}" height="12" fill="#1b1f38"/>')
    for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        o.append(f'<circle cx="{34+i*22}" cy="25" r="6" fill="{col}"/>')
    o.append(f'<text x="500" y="30" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#7d86a8" letter-spacing="2">shadow@gaming100: ~</text>')
    o.append(f'<rect x="8" y="42" width="{W-16}" height="1.5" fill="url(#bar)" opacity=".7"/>')
    cur = []
    y = ytop
    for i, (kind, text) in enumerate(rows):
        n = len(text) + (11 if kind == "cmd" else 0)
        speed = .07 if kind == "cmd" else .018
        ev = [(0, 0)] + [(t+k*speed, round(k*9.4, 2)) for k in range(n+1)] + [(t+n*speed+.01, 900)]
        vals, kts = reveal_vals(ev, T)
        o.append(f'<clipPath id="r{i}"><rect x="{x0}" y="{y-16}" height="22" width="0"><animate attributeName="width" calcMode="discrete" dur="{T}s" repeatCount="indefinite" values="{vals}" keyTimes="{kts}"/></rect></clipPath>')
        if kind == "cmd":
            o.append(f'<g clip-path="url(#r{i})" font-family="{MONO}" font-size="{fs}" font-weight="600"><text x="{x0}" y="{y}" xml:space="preserve"><tspan fill="#22d3ee">shadow</tspan><tspan fill="#7d86a8">@</tspan><tspan fill="#8b5cf6">~</tspan><tspan fill="#f472b6"> $ </tspan><tspan fill="#f5f7ff">{text}</tspan></text></g>')
        else:
            o.append(f'<g clip-path="url(#r{i})" font-family="{MONO}" font-size="{fs}" font-weight="600"><text x="{x0}" y="{y}" fill="#c9d1f0" xml:space="preserve">{text}</text></g>')
        cur += [(t+k*speed, x0+(k+(0 if kind=="cmd" else 0))*cw) for k in range(n+1)]
        ypos = y
        t += n*speed + (.5 if kind == "cmd" else .9)
        y += lh*(1 if kind == "cmd" else 1.25)
    # note: command prefix is wider than reveal grid, so use textLength-free approx; prefix width fixed
    o.append(f'<text x="{W-34}" y="{H-24}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5c647d" letter-spacing="2">UTF-8  ·  ZSH</text>')
    o.append('</svg>')
    return "\n".join(o)

# ---------------------------------------------------------------- TECH CUBES
TECH = [("JS", "JavaScript", "#e8c500", "#111"), ("NODE", "Node.js", "#3f9b3f", "#fff"), ("DJS", "Discord.js", "#5865f2", "#fff"),
        ("EX", "Express", "#7b818c", "#fff"), ("NX", "Next.js", "#1c2230", "#fff"), ("PG", "PostgreSQL", "#3b7ab8", "#fff"), ("CF", "Cloudflare", "#f38020", "#fff")]
def stack(t):
    c = P[t]; W, H = 1000, 270
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack: JavaScript, Node.js, Discord.js, Express, Next.js, PostgreSQL, Cloudflare">']
    o.append(f'<defs><filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter><linearGradient id="pl" x1="0" x2="1"><stop offset="0" stop-color="{c["a1"]}" stop-opacity="0"/><stop offset=".5" stop-color="{c["a1"]}" stop-opacity=".5"/><stop offset="1" stop-color="{c["a2"]}" stop-opacity="0"/></linearGradient></defs>')
    o.append(f'<rect x="40" y="198" width="920" height="2" fill="url(#pl)"/>')
    for i, (lab, name, col, tc) in enumerate(TECH):
        x = 500 + (i-3)*138; d = 3.6 + (i % 3)*.5; b = i*.55
        s = 42
        o.append(f'<ellipse cx="{x}" cy="192" rx="{s*.95:.0f}" ry="{s*.2:.0f}" fill="{col}" opacity=".35" filter="url(#gl)"><animate attributeName="rx" values="{s*.95:.0f};{s*.7:.0f};{s*.95:.0f}" dur="{d}s" begin="-{b}s" repeatCount="indefinite" {SPL}/><animate attributeName="opacity" values=".35;.15;.35" dur="{d}s" begin="-{b}s" repeatCount="indefinite" {SPL}/></ellipse>')
        o.append(f'<g>{bob(16, d, b)}{cube(x, 95, s, col, lab, tc, fs=(15 if len(lab)<3 else 12))}</g>')
        o.append(f'<text x="{x}" y="236" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="{c["sub"]}">{name}</text>')
    o.append('</svg>')
    return "\n".join(o)

# ---------------------------------------------------------------- ROLE CARDS
def card_frame(x, y, w, h, c, idn, dur=7):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{c["card"]}" fill-opacity="{c["cop"]}" stroke="{c["edge"]}" stroke-opacity=".12"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="none" stroke="url(#acc)" stroke-width="2.2" pathLength="100" stroke-dasharray="22 78" stroke-linecap="round">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="-100" dur="{dur}s" repeatCount="indefinite"/></rect>')
def acc_defs(c):
    return (f'<linearGradient id="acc" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["a1"]}"/><stop offset=".5" stop-color="{c["a2"]}"/><stop offset="1" stop-color="{c["a3"]}"/></linearGradient>'
            f'<filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>')
def roles(t):
    c = P[t]; W, H = 1000, 240
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="01 Founder: FreeHosts. 02 Developer: Nemethic.">', f'<defs>{acc_defs(c)}</defs>']
    data = [(10, "01 / FOUNDER", "FreeHosts", ["Building FreeHosts, a community-driven", "directory for discovering free hosting."], 0),
            (510, "02 / DEVELOPER", "Nemethic", ["Developer at Nemethic.", "JavaScript · Node.js · PostgreSQL"], 1)]
    for (x, lab, title, desc, kind) in data:
        o.append(card_frame(x, 10, 480, 220, c, kind, 7+kind))
        ix, iy = x+92, 118
        o.append(f'<ellipse cx="{ix}" cy="{iy+66}" rx="52" ry="12" fill="{c["a1"]}" opacity=".3" filter="url(#gl)"/>')
        if kind == 0:
            for j in range(3):
                o.append(f'<g>{bob(6, 3.2, j*.6)}{slab(ix, iy+30-j*30+0, 52, 16, mix(c["a1"], c["a2"], j/2))}</g>')
        else:
            o.append(f'<g>{bob(10, 3.8)}{cube(ix, iy, 46, c["a1"], "&lt;/&gt;", "#fff", 15)}</g>')
        o.append(f'<text x="{x+180}" y="68" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="3" fill="{c["a2"]}">{lab}</text>')
        o.append(f'<text x="{x+180}" y="116" font-family="{SANS}" font-size="40" font-weight="800" fill="{c["fg"]}">{title}</text>')
        for i, d in enumerate(desc):
            o.append(f'<text x="{x+180}" y="{150+i*22}" font-family="{SANS}" font-size="14.5" fill="{c["sub"]}">{d}</text>')
    o.append('</svg>')
    return "\n".join(o)

# ---------------------------------------------------------------- FEATURED
def featured(t):
    c = P[t]; W, H = 1000, 330
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Featured project: FreeHosts, a community-driven directory for discovering free hosting providers. freehosts.eu">']
    o.append(f'<defs>{acc_defs(c)}<clipPath id="cc"><rect x="10" y="10" width="980" height="310" rx="18"/></clipPath><linearGradient id="tg" x1="0" x2="1"><stop offset="0" stop-color="{c["fg"]}"/><stop offset="1" stop-color="{c["a2"]}"/></linearGradient></defs>')
    o.append(card_frame(10, 10, 980, 310, c, 0, 10))
    o.append(f'<g clip-path="url(#cc)"><circle cx="200" cy="170" r="130" fill="{c["a1"]}" opacity=".25" filter="url(#gl)"><animate attributeName="cx" values="160;260;160" dur="9s" repeatCount="indefinite" {SPL}/></circle>'
             f'<circle cx="860" cy="260" r="110" fill="{c["a2"]}" opacity=".16" filter="url(#gl)"><animate attributeName="cy" values="240;300;240" dur="7s" repeatCount="indefinite" {SPL}/></circle></g>')
    cx = 205
    o.append(f'<ellipse cx="{cx}" cy="285" rx="120" ry="24" fill="{c["a1"]}" opacity=".35" filter="url(#gl)"/>')
    # rack: 4 slabs floating
    for j in range(4):
        cy = 232 - j*46
        col = mix(c["a1"], c["a2"], j/3)
        led = "".join(
            f'<circle r="3" fill="{c["a2"] if (j+q)%2 else c["a3"]}" cx="{cx-.866*80*(.14+.15*q):.1f}" cy="{cy+40*(.14+.15*q)+7:.1f}"><animate attributeName="opacity" values="1;.15;1" dur="{1.2+.4*q}s" begin="-{j*.3+q*.2:.1f}s" repeatCount="indefinite"/></circle>'
            for q in range(3))
        o.append(f'<g>{bob(9, 3.4, j*.5)}{slab(cx, cy, 80, 22, col)}{led}</g>')
    # data packets
    for k in range(5):
        px = cx + (k-2)*22
        o.append(f'<circle cx="{px}" r="3" fill="{c["a2"]}"><animate attributeName="cy" values="48;8" dur="2.4s" begin="-{k*.5:.1f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;0" dur="2.4s" begin="-{k*.5:.1f}s" repeatCount="indefinite"/></circle>')
    tx = 410
    o.append(f'<text x="{tx}" y="96" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="4" fill="{c["a2"]}">FEATURED PROJECT</text>')
    o.append(f'<text x="{tx}" y="160" font-family="{SANS}" font-size="64" font-weight="900" fill="url(#tg)">FreeHosts</text>')
    o.append(f'<text x="{tx}" y="198" font-family="{SANS}" font-size="17" fill="{c["sub"]}">A community-driven directory for discovering</text>')
    o.append(f'<text x="{tx}" y="222" font-family="{SANS}" font-size="17" fill="{c["sub"]}">free hosting providers.</text>')
    o.append(f'<g><rect x="{tx}" y="246" width="262" height="44" rx="22" fill="url(#acc)"/>'
             f'<rect x="{tx}" y="246" width="262" height="44" rx="22" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;.18;0" dur="2.6s" repeatCount="indefinite"/></rect>'
             f'<text x="{tx+28}" y="273" font-family="{MONO}" font-size="13" font-weight="800" letter-spacing="2" fill="#fff">EXPLORE FREEHOSTS</text>'
             f'<path d="M{tx+222} 276 L{tx+234} 264 M{tx+224} 263.5 H{tx+235} V275" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g>')
    o.append('</svg>')
    return "\n".join(o)

# ---------------------------------------------------------------- BUTTONS
GH = "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
def icon_g(name, col):
    if name == "github": return f'<path fill="{col}" d="{GH}"/>'
    if name == "freehosts": return f'<g fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3.5" width="18" height="7" rx="2"/><rect x="3" y="13.5" width="18" height="7" rx="2"/><path d="M7 7h.01M7 17h.01M11 7h6M11 17h6"/></g>'
    return f'<g fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="m3.5 7.5 8.5 6 8.5-6"/></g>'
def button(t, name, label, w):
    c = P[t]; H = 52
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {H}" width="{w}" height="{H}" role="img" aria-label="{label}">
<defs><linearGradient id="acc" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['a1']}"/><stop offset=".5" stop-color="{c['a2']}"/><stop offset="1" stop-color="{c['a3']}"/></linearGradient></defs>
<rect x="2" y="2" width="{w-4}" height="{H-4}" rx="24" fill="{c['card']}" fill-opacity="{c['cop']}" stroke="{c['edge']}" stroke-opacity=".16"/>
<rect x="2" y="2" width="{w-4}" height="{H-4}" rx="24" fill="none" stroke="url(#acc)" stroke-width="2.2" pathLength="100" stroke-dasharray="26 74" stroke-linecap="round"><animate attributeName="stroke-dashoffset" from="0" to="-100" dur="4.5s" repeatCount="indefinite"/></rect>
<g transform="translate(24 14) scale(1)">{icon_g(name, c['fg'])}</g>
<text x="58" y="31.5" font-family="{MONO}" font-size="14" font-weight="800" letter-spacing="2" fill="{c['fg']}">{label}</text></svg>'''

# ---------------------------------------------------------------- FOOTER
def footer(t):
    c = P[t]; W, H = 1000, 150
    def wave(amp, per, y, col, op, dur, ph):
        pts = []; x = -per
        d = f"M{x} {y}"
        while x < W + per:
            d += f" Q{x+per/4} {y-amp} {x+per/2} {y} T{x+per} {y}"; x += per
        d += f" V{H} H{-per} Z"
        return f'<path d="{d}" fill="{col}" opacity="{op}"><animateTransform attributeName="transform" type="translate" from="0 0" to="{per} 0" dur="{dur}s" begin="-{ph}s" repeatCount="indefinite"/></path>'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="© ShadowGaming100">',
         f'<defs><linearGradient id="w1" x1="0" x2="1"><stop offset="0" stop-color="{c["a1"]}"/><stop offset="1" stop-color="{c["a2"]}"/></linearGradient><linearGradient id="w2" x1="1" x2="0"><stop offset="0" stop-color="{c["a3"]}"/><stop offset="1" stop-color="{c["a1"]}"/></linearGradient></defs>',
         wave(14, 400, 78, "url(#w2)", .35, 11, 2), wave(18, 500, 92, "url(#w1)", .5, 8, 0), wave(12, 300, 108, "url(#w1)", .8, 6, 3),
         f'<rect y="116" width="{W}" height="{H-116}" fill="{c["bg0"]}" opacity=".0"/>',
         f'<text x="500" y="58" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" letter-spacing="8" fill="{c["sub"]}">© SHADOWGAMING100</text>',
         '</svg>']
    return "\n".join(o)

# ---------------------------------------------------------------- WRITE ALL
for f in os.listdir(A):
    if f.startswith(("banner", "typing", "footer", "divider")): os.remove(f"{A}/{f}")

for t in ("dark", "light"):
    write(f"hero.{t}.svg", hero(t)); write(f"typing.{t}.svg", typing(t)); write(f"footer.{t}.svg", footer(t))
    write(f"stack.{t}.svg", stack(t)); write(f"roles.{t}.svg", roles(t)); write(f"featured.{t}.svg", featured(t))
    for key, num, title in HEADERS: write(f"headers/{key}.{t}.svg", header(t, num, title))
    for name, label, w in (("github", "GITHUB", 168), ("freehosts", "FREEHOSTS", 196), ("contact", "CONTACT", 168)):
        write(f"buttons/{name}.{t}.svg", button(t, name, label, w))
write("terminal.svg", terminal())
print(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(A) for f in fs if f.endswith(".svg")) // 1024, "KB svg")
