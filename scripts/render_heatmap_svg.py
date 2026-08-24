from pathlib import Path
import json
from datetime import date


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]

CELL = 12
GAP = 3
WEEKS = 53
DAYS = 7

GRID_X = 30
GRID_Y = 35

WIDTH = GRID_X + WEEKS * (CELL + GAP) + 20
HEIGHT = GRID_Y + DAYS * (CELL + GAP) + 85


def load_data():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT}"
        )

    return json.loads(
        INPUT.read_text(encoding="utf-8")
    )


def build_lookup(data):
    return {
        item["date"]: item
        for item in data["days"]
    }


def render_grid(lookup):
    parts = []

    for week in range(WEEKS):
        for day in range(DAYS):
            index = week * 7 + day

            if index >= len(lookup):
                continue

    # Sort all dates so the grid follows chronological order.
    items = sorted(
        lookup.values(),
        key=lambda x: x["date"]
    )

    # Keep the latest 371 days.
    items = items[-371:]

    for index, item in enumerate(items):
        week = index // 7
        day = index % 7

        x = GRID_X + week * (CELL + GAP)
        y = GRID_Y + day * (CELL + GAP)

        level = max(
            0,
            min(5, int(item.get("level", 0)))
        )

        color = PALETTE[level]

        parts.append(
            f'''
            <rect
                x="{x}"
                y="{y}"
                width="{CELL}"
                height="{CELL}"
                rx="3"
                fill="{color}"
                opacity="0"
                style="animation-delay:{index * 0.003:.3f}s"
            />
            '''
        )

    return parts


def main():
    data = load_data()
    lookup = build_lookup(data)

    total = sum(
        item["count"]
        for item in data["days"]
    )

    stats = data.get("stats", {})

    current_streak = stats.get(
        "current_streak",
        0
    )

    longest_streak = stats.get(
        "longest_streak",
        0
    )

    parts = [
        f'''
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="{WIDTH}"
            height="{HEIGHT}"
            viewBox="0 0 {WIDTH} {HEIGHT}"
        >

        <style>
            rect[data-cell="true"] {{
                animation: reveal 0.35s ease-out forwards;
                transform-origin: center;
            }}

            @keyframes reveal {{
                from {{
                    opacity: 0;
                    transform: translate(-4px, -4px);
                }}

                to {{
                    opacity: 1;
                    transform: translate(0, 0);
                }}
            }}

            text {{
                font-family:
                    -apple-system,
                    BlinkMacSystemFont,
                    "Segoe UI",
                    sans-serif;
            }}
        </style>

        <rect
            width="100%"
            height="100%"
            rx="12"
            fill="#0d1117"
        />

        <text
            x="30"
            y="22"
            font-size="13"
            font-weight="600"
            fill="#f0f6fc"
        >
            GitHub Contributions
        </text>
        '''
    ]

    # Contribution cells
    cell_index = 0

    items = sorted(
        lookup.values(),
        key=lambda x: x["date"]
    )[-371:]

    for index, item in enumerate(items):
        week = index // 7
        day = index % 7

        x = GRID_X + week * (CELL + GAP)
        y = GRID_Y + day * (CELL + GAP)

        level = max(
            0,
            min(5, int(item.get("level", 0)))
        )

        color = PALETTE[level]

        parts.append(
            f'''
            <rect
                data-cell="true"
                x="{x}"
                y="{y}"
                width="{CELL}"
                height="{CELL}"
                rx="3"
                fill="{color}"
                style="animation-delay:{cell_index * 0.003:.3f}s"
            />
            '''
        )

        cell_index += 1

    legend_y = GRID_Y + DAYS * (CELL + GAP) + 18

    parts.append(
        f'''
        <text
            x="{GRID_X}"
            y="{legend_y}"
            font-size="10"
            fill="#8b949e"
        >
            Less
        </text>
        '''
    )

    legend_x = GRID_X + 35

    for level, color in enumerate(PALETTE):
        x = legend_x + level * (CELL + GAP)

        parts.append(
            f'''
            <rect
                x="{x}"
                y="{legend_y - 9}"
                width="{CELL}"
                height="{CELL}"
                rx="3"
                fill="{color}"
            />
            '''
        )

    parts.append(
        f'''
        <text
            x="{legend_x + 6 * (CELL + GAP) + 4}"
            y="{legend_y}"
            font-size="10"
            fill="#8b949e"
        >
            More
        </text>

        <text
            x="{GRID_X}"
            y="{HEIGHT - 30}"
            font-size="11"
            fill="#8b949e"
        >
            {total:,} contributions in the last year
        </text>

        <text
            x="{GRID_X}"
            y="{HEIGHT - 13}"
            font-size="10"
            fill="#6e7681"
        >
            Current streak: {current_streak} days
            • Longest streak: {longest_streak} days
        </text>

        </svg>
        '''
    )

    OUTPUT.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )

    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    main()