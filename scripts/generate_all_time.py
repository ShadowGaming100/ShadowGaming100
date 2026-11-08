#!/usr/bin/env python3
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

    # Every calendar year gets the same isometric design and both themes.
    for year, calendar in years:
        subtitle = f"{calendar.get('totalContributions', 0):,} contributions · January 1 – {through.date().isoformat() if year == current_year else 'December 31'}"
        (OUT / f"profile-{year}.svg").write_text(
            render([(year, calendar)], "light", through, f"{year} CONTRIBUTIONS", subtitle),
            encoding="utf-8",
        )
        (OUT / f"profile-night-{year}.svg").write_text(
            render([(year, calendar)], "dark", through, f"{year} CONTRIBUTIONS", subtitle),
            encoding="utf-8",
        )

    (OUT / "profile-all-time.svg").write_text(
        render(years, "light", through), encoding="utf-8"
    )
    (OUT / "profile-night-all-time.svg").write_text(
        render(years, "dark", through), encoding="utf-8"
    )

    # Keep the README's yearly list synchronized with the years generated above.
    readme = ROOT / "README.md"
    if readme.is_file():
        content = readme.read_text(encoding="utf-8")
        start_marker = "<!-- CONTRIBUTION-YEARS:START -->"
        end_marker = "<!-- CONTRIBUTION-YEARS:END -->"
        if start_marker in content and end_marker in content:
            entries = [start_marker, ""]
            for year, _calendar in reversed(years):
                entries.extend([
                    f"  **{year} — Calendar year contributions**",
                    "",
                    "  <picture>",
                    f'    <source media="(prefers-color-scheme: dark)" srcset="./profile-3d-contrib/profile-night-{year}.svg" />',
                    f'    <img src="./profile-3d-contrib/profile-{year}.svg" width="100%" alt="3D GitHub contribution graph for calendar year {year}" />',
                    "  </picture>",
                    "",
                ])
            entries.append(end_marker)
            before, remainder = content.split(start_marker, 1)
            _old, after = remainder.split(end_marker, 1)
            readme.write_text(before + "\n".join(entries) + after, encoding="utf-8")

    print(
        f"Generated matching light/dark yearly contribution graphs and all-time graph: "
        f"{first_year}–{current_year} ({len(years)} calendar years)."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise
