"""Builds assets/snake.light.svg and assets/snake.dark.svg.

Reads the contribution calendar of PROFILE_USER from the GitHub GraphQL API
(GITHUB_TOKEN), draws it as raised 3D bars and animates a snake eating them.
If the API call fails an empty grid is drawn so the README image never breaks.
"""
import json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
USER = os.environ.get("PROFILE_USER", "ShadowGaming100")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
SANS = "-apple-system,'Segoe UI',system-ui,Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "dark":  dict(bg="#0d1117", card="#161b22", line="#30363d", fg="#e6edf3", sub="#8b949e", snake="#2f81f7",
                  levels=["#1c2128", "#0e4429", "#006d32", "#26a641", "#39d353"]),
    "light": dict(bg="#ffffff", card="#f6f8fa", line="#d0d7de", fg="#1f2328", sub="#59636e", snake="#0969da",
                  levels=["#e6eaef", "#9be9a8", "#40c463", "#30a14e", "#216e39"]),
}
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
HEIGHT = [0, 7, 14, 22, 32]

def fetch():
    q = ("query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions "
         "weeks{contributionDays{contributionCount contributionLevel weekday}}}}}}")
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-snake"})
    with urllib.request.urlopen(req, timeout=30) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["weekday"], LEVEL.get(d["contributionLevel"], 0), d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    return weeks, cal["totalContributions"]

def empty():
    return [[(d, 0, 0) for d in range(7)] for _ in range(53)], 0

def mix(a, b, t):
    pa = [int(a[i:i+2], 16) for i in (1, 3, 5)]; pb = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(pa[i] + (pb[i]-pa[i])*t) for i in range(3))

def build(theme, weeks, total, demo=False):
    c = THEMES[theme]
    W, H = 1000, 270
    CX, CW = 16.4, 13.2            # column pitch / cell width
    RX, RY = 5.9, -9.4             # row pitch (one step toward the back)
    DX, DY = 4.9, -7.9             # cell depth vector
    X0, YB = 47, 208               # origin of the front row
    CELL = 0.05                    # seconds the snake needs per cell
    START, HOLD = .8, 3.2

    def pos(w, row):
        return X0 + w*CX + row*RX, YB + row*RY

    # the snake sweeps the grid row by row (front row first), reversing direction each row
    lvl_at = {}
    for w, days in enumerate(weeks):
        for wd, lvl, cnt in days: lvl_at[(w, 6 - wd)] = lvl
    nweeks = len(weeks)
    order = []
    for r in range(7):
        ws = range(nweeks) if r % 2 == 0 else range(nweeks - 1, -1, -1)
        for w in ws: order.append((w, r, lvl_at.get((w, r), -1)))   # -1: no such day (partial week)
    n = len(order); move = n*CELL; T = round(START + move + HOLD, 2)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Snake eating my GitHub contributions">']
    o.append(f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="8" fill="{c["card"]}" stroke="{c["line"]}" stroke-width="1.5"/>')
    # base tiles, back rows first so nearer rows paint over them
    draw = sorted([t for t in order if t[2] >= 0], key=lambda t: (-t[1], t[0]))
    eat_time = {(w, r): START + i*CELL for i, (w, r, l) in enumerate(order)}
    for w, r, lvl in draw:
        x, y = pos(w, r)
        o.append(f'<polygon points="{x:.1f},{y:.1f} {x+CW:.1f},{y:.1f} {x+CW+DX:.1f},{y+DY:.1f} {x+DX:.1f},{y+DY:.1f}" fill="{c["levels"][0]}"/>')
    for w, r, lvl in draw:
        if lvl == 0: continue
        x, y = pos(w, r); h = HEIGHT[lvl]; col = c["levels"][lvl]
        top = mix(col, "#ffffff", .22); side = mix(col, "#000000", .35)
        t0 = eat_time[(w, r)]
        a, b = t0/T, (t0+.35)/T
        o.append(f'<g><animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;{a:.4f};{b:.4f};.985;1" dur="{T}s" repeatCount="indefinite"/>'
                 f'<polygon points="{x:.1f},{y-h:.1f} {x+CW:.1f},{y-h:.1f} {x+CW:.1f},{y:.1f} {x:.1f},{y:.1f}" fill="{col}"/>'
                 f'<polygon points="{x+CW:.1f},{y-h:.1f} {x+CW+DX:.1f},{y-h+DY:.1f} {x+CW+DX:.1f},{y+DY:.1f} {x+CW:.1f},{y:.1f}" fill="{side}"/>'
                 f'<polygon points="{x:.1f},{y-h:.1f} {x+CW:.1f},{y-h:.1f} {x+CW+DX:.1f},{y-h+DY:.1f} {x+DX:.1f},{y-h+DY:.1f}" fill="{top}"/></g>')
    # snake path through the cell centres
    pts = []
    for w, r, lvl in order:
        x, y = pos(w, r); pts.append((x + CW/2 + DX/2, y + DY/2 - 7))
    path = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    K = 20; lag = CELL
    snk = c["snake"]
    o.append(f'<g><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.01;.975;.995;1" dur="{T}s" repeatCount="indefinite"/>')
    last = n - 1
    dk = f"{K}"
    off = f"{K};{K};{K-last};{K-last}"
    kt = f"0;{START/T:.5f};{(START+last*CELL)/T:.5f};1"
    for width, col in ((12, mix(snk, "#000000", .45)), (8, snk)):
        o.append(f'<path d="{path}" pathLength="{last}" fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{dk} {last+K+5}">'
                 f'<animate attributeName="stroke-dashoffset" values="{off}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite" calcMode="linear"/></path>')
    head = mix(snk, "#ffffff", .3)
    o.append(f'<g><animateMotion path="{path}" dur="{T}s" repeatCount="indefinite" calcMode="linear" keyPoints="0;0;1;1" keyTimes="{kt}" rotate="auto"/>'
             f'<circle r="7.5" fill="{head}"/><circle cx="3.2" cy="-3.8" r="2.4" fill="#fff"/><circle cx="3.2" cy="3.8" r="2.4" fill="#fff"/>'
             f'<circle cx="4" cy="-3.8" r="1.2" fill="#0d1117"/><circle cx="4" cy="3.8" r="1.2" fill="#0d1117"/></g>')
    o.append('</g>')
    # caption + legend
    label = "no contribution data yet" if demo else f"{total:,} contributions in the last year"
    o.append(f'<text x="40" y="250" font-family="{SANS}" font-size="18" fill="{c["sub"]}">{label}</text>')
    lx = 800
    o.append(f'<text x="{lx-12}" y="250" text-anchor="end" font-family="{SANS}" font-size="16" fill="{c["sub"]}">Less</text>')
    for i, lc in enumerate(c["levels"]):
        o.append(f'<rect x="{lx+i*22}" y="236" width="16" height="16" rx="3" fill="{lc}"/>')
    o.append(f'<text x="{lx+5*22+8}" y="250" font-family="{SANS}" font-size="16" fill="{c["sub"]}">More</text>')
    o.append('</svg>')
    return "\n".join(o)

def main():
    demo = False
    try:
        weeks, total = fetch()
    except Exception as e:
        print(f"::warning::Could not read contributions ({e}); drawing an empty grid", file=sys.stderr)
        weeks, total = empty(); demo = True
    os.makedirs(OUT, exist_ok=True)
    for t in THEMES:
        with open(os.path.join(OUT, f"snake.{t}.svg"), "w", encoding="utf-8") as f:
            f.write(build(t, weeks, total, demo))
    print("snake written", len(weeks), "weeks", total, "contributions")

if __name__ == "__main__":
    main()
