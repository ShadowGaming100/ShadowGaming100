#!/usr/bin/env python3
"""Generate a multi-year 3D contribution calendar from GitHub's GraphQL API."""
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
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ShadowGaming100-profile-assets"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}: {body[:500]}") from exc


def fetch_year(token, username, year):
    query = f'''query {{
      user(login: "{username}") {{
        contributionsCollection(from: "{year}-01-01T00:00:00Z", to: "{year}-12-31T23:59:59Z") {{
          contributionCalendar {{
            totalContributions
            weeks {{ contributionDays {{ date contributionCount }} }}
          }}
        }}
      }}
    }}'''
    result = request_json(API, token, {"query": query})
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + "; ".join(e.get("message", "unknown") for e in result["errors"]))
    user = result.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {username}")
    return user["contributionsCollection"]["contributionCalendar"]


def shade(theme, count):
    if theme == "dark":
        palette = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]
    else:
        palette = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
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
    # Small isometric voxel. More contributions raise the cube, not its footprint.
    fill = shade(theme, count)
    height = 1.5 if count == 0 else min(13, 3 + count * 1.25)
    half_w, half_h = 5.2, 3.2
    top_y = y - height
    top = f"{x},{top_y} {x+half_w},{top_y+half_h} {x},{top_y+2*half_h} {x-half_w},{top_y+half_h}"
    left = f"{x-half_w},{top_y+half_h} {x},{top_y+2*half_h} {x},{y+2*half_h} {x-half_w},{y+half_h}"
    right = f"{x},{top_y+2*half_h} {x+half_w},{top_y+half_h} {x+half_w},{y+half_h} {x},{y+2*half_h}"
    if theme == "dark":
        left_fill, right_fill = "#0a3520", "#092d1c"
    else:
        left_fill, right_fill = "#238b45", "#176b36"
    opacity = "1" if count else (".62" if theme == "dark" else ".8")
    return (f'<g opacity="{opacity}"><polygon points="{left}" fill="{left_fill}"/>'
            f'<polygon points="{right}" fill="{right_fill}"/>'
            f'<polygon points="{top}" fill="{fill}"/></g>')


def render(years, theme):
    width = 920
    margin_x = 94
    week_step = 15.0
    day_step = 14.0
    year_gap = 170
    top = 100
    height = top + len(years) * year_gap + 30
    if theme == "dark":
        bg, fg, muted, border = "#0d1117", "#e6edf3", "#8b949e", "#30363d"
    else:
        bg, fg, muted, border = "#ffffff", "#1f2328", "#59636e", "#d0d7de"

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="All-time 3D GitHub contribution history">']
    svg.append(f'<rect width="{width}" height="{height}" rx="12" fill="{bg}"/>')
    svg.append(f'<text x="34" y="42" font-family="system-ui, sans-serif" font-size="24" font-weight="700" fill="{fg}">ALL-TIME CONTRIBUTION HISTORY</text>')
    svg.append(f'<text x="34" y="68" font-family="system-ui, sans-serif" font-size="13" fill="{muted}">Every calendar year since the account was created</text>')

    for yi, (year, calendar) in enumerate(years):
        base_y = top + yi * year_gap
        total = calendar.get("totalContributions", 0)
        svg.append(f'<text x="34" y="{base_y+18}" font-family="system-ui, sans-serif" font-size="17" font-weight="700" fill="{fg}">{year}</text>')
        svg.append(f'<text x="34" y="{base_y+38}" font-family="system-ui, sans-serif" font-size="11" fill="{muted}">{total:,} contributions</text>')
        svg.append(f'<line x1="{margin_x-16}" y1="{base_y+4}" x2="{width-30}" y2="{base_y+4}" stroke="{border}" stroke-width="1"/>')
        for wi, week in enumerate(calendar.get("weeks", [])):
            for day in week.get("contributionDays", []):
                date = dt.date.fromisoformat(day["date"])
                x = margin_x + wi * week_step
                y = base_y + 58 + date.weekday() * day_step
                svg.append(cube(x, y, int(day.get("contributionCount", 0)), theme))

    svg.append('</svg>')
    return "\n".join(svg)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    username = os.environ.get("USERNAME", "ShadowGaming100")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")
    user = request_json(f"https://api.github.com/users/{username}", token)
    created = dt.date.fromisoformat(user["created_at"][:10])
    first_year = created.year
    current_year = dt.datetime.now(dt.timezone.utc).year
    years = []
    for year in range(first_year, current_year + 1):
        print(f"Fetching {username}'s {year} contribution calendar...", flush=True)
        years.append((year, fetch_year(token, username, year)))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "profile-all-time.svg").write_text(render(years, "light"), encoding="utf-8")
    (OUT / "profile-night-all-time.svg").write_text(render(years, "dark"), encoding="utf-8")
    print(f"Generated all-time contribution world: {len(years)} years")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise
