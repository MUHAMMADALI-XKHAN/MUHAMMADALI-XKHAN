from pathlib import Path
import os
import html


OUTPUT = Path("info-card.svg")
STATIC = os.getenv("STATIC") == "1"

ROWS = [
    ("Now", "BSCS • 7th Semester"),
    ("Prev", "Python • C# • C++ • SQL"),
    ("Stack", "React • Next.js • Flutter • ASP.NET"),
    ("Highlights", "GitHub • Projects • Freelance"),
]

WIDTH = 520
HEIGHT = 245

parts = [
    f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{WIDTH}" height="{HEIGHT}"
        viewBox="0 0 {WIDTH} {HEIGHT}">
        <rect width="100%" height="100%" rx="14"
              fill="#111111" stroke="#333333"/>

        <rect x="0" y="0" width="{WIDTH}" height="42"
              rx="14" fill="#1c1c1c"/>

        <rect x="0" y="28" width="{WIDTH}" height="14"
              fill="#1c1c1c"/>

        <circle cx="20" cy="21" r="6" fill="#ff5f56"/>
        <circle cx="40" cy="21" r="6" fill="#ffbd2e"/>
        <circle cx="60" cy="21" r="6" fill="#27c93f"/>

        <text x="85" y="27"
              font-family="monospace"
              font-size="15"
              font-weight="bold"
              fill="#eeeeee">
            MUHAMMADALI-XKHAN
        </text>
    '''
]

for i, (key, value) in enumerate(ROWS):
    y = 78 + i * 38
    delay = i * 0.12

    animation = "" if STATIC else f'''
        <animate attributeName="opacity"
                 from="0" to="1"
                 dur="0.35s"
                 begin="{delay:.2f}s"
                 fill="freeze"/>
        <animateTransform
                 attributeName="transform"
                 type="translate"
                 from="-12 0"
                 to="0 0"
                 dur="0.35s"
                 begin="{delay:.2f}s"
                 fill="freeze"/>
    '''

    parts.append(
        f'''
        <g opacity="{'1' if STATIC else '0'}">
            {animation}

            <text x="30" y="{y}"
                  font-family="monospace"
                  font-size="14"
                  font-weight="bold"
                  fill="#8be9fd">
                {html.escape(key)}
            </text>

            <text x="145" y="{y}"
                  font-family="monospace"
                  font-size="14"
                  fill="#dddddd">
                {html.escape(value)}
            </text>
        </g>
        '''
    )

parts.append("</svg>")

OUTPUT.write_text("\n".join(parts), encoding="utf-8")

print(f"Done: {OUTPUT}")