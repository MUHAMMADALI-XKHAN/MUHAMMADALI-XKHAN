from pathlib import Path
import json
import re
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup


USERNAME = "MUHAMMADALI-XKHAN"
URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT = Path("data/contributions.json")


def fetch_html():
    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.text


def parse_contributions(html):
    soup = BeautifulSoup(html, "html.parser")

    days = []

    for cell in soup.select("td.ContributionCalendar-day"):
        day = cell.get("data-date")
        level = cell.get("data-level")

        if not day:
            continue

        try:
            level = int(level or 0)
        except ValueError:
            level = 0

        text = cell.get("aria-label", "")

        match = re.search(r"(\d[\d,]*) contribution", text)

        if match:
            count = int(match.group(1).replace(",", ""))
        else:
            count = 0

        days.append({
            "date": day,
            "count": count,
            "level": level,
        })

    return days


def calculate_stats(days):
    if not days:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
            "monthly_totals": {},
        }

    sorted_days = sorted(days, key=lambda x: x["date"])

    current_streak = 0
    longest_streak = 0
    running_streak = 0

    best_day = max(
        sorted_days,
        key=lambda x: x["count"]
    )

    previous = None

    for item in sorted_days:
        current = date.fromisoformat(item["date"])

        if item["count"] > 0:
            if previous and current == previous + timedelta(days=1):
                running_streak += 1
            else:
                running_streak = 1

            longest_streak = max(
                longest_streak,
                running_streak
            )
        else:
            running_streak = 0

        previous = current

    today = date.today()

    lookup = {
        date.fromisoformat(x["date"]): x["count"]
        for x in sorted_days
    }

    cursor = today

    while lookup.get(cursor, 0) > 0:
        current_streak += 1
        cursor -= timedelta(days=1)

    monthly_totals = {}

    for item in sorted_days:
        month = item["date"][:7]
        monthly_totals[month] = (
            monthly_totals.get(month, 0)
            + item["count"]
        )

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
    }


def main():
    print(f"Fetching contributions for {USERNAME}...")

    html = fetch_html()

    days = parse_contributions(html)

    if not days:
        raise RuntimeError(
            "No contribution cells were found."
        )

    stats = calculate_stats(days)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    payload = {
        "username": USERNAME,
        "fetched_at": __import__("datetime").datetime.now().isoformat(),
        "days": days,
        "stats": stats,
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2
        ),
        encoding="utf-8"
    )

    total = sum(
        item["count"]
        for item in days
    )

    print(
        f"Done: {OUTPUT} "
        f"({len(days)} days, {total:,} contributions)"
    )


if __name__ == "__main__":
    main()