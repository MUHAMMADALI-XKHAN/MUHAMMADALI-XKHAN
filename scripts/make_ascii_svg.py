from pathlib import Path
import math

from PIL import Image


RAMP = " .`:-=+*cs#%@"
INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

# Character grid
WIDTH = 100

# Terminal-style character proportions
CHAR_ASPECT = 0.5

# Light gray monochrome text
TEXT_COLOR = "#B8B8B8"


def brightness_to_glyph(value):
    # White -> sparse, black -> dense
    index = int((255 - value) / 255 * (len(RAMP) - 1))
    return RAMP[index]


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Could not find {INPUT}")

    image = Image.open(INPUT).convert("L")

    width, height = image.size
    height_chars = max(
        1,
        round(height / width * WIDTH * CHAR_ASPECT)
    )

    image = image.resize(
        (WIDTH, height_chars),
        Image.Resampling.LANCZOS
    )

    pixels = image.load()

    font_size = 10
    line_height = 11

    svg_width = WIDTH * 6
    svg_height = height_chars * line_height

    rows = []

    for y in range(height_chars):
        text = ""

        for x in range(WIDTH):
            glyph = brightness_to_glyph(pixels[x, y])
            text += glyph

        rows.append(text)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_width}" height="{svg_height}" '
        f'viewBox="0 0 {svg_width} {svg_height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<style>'
        f'text {{ '
        f'font-family: "Courier New", monospace; '
        f'font-size: {font_size}px; '
        f'fill: {TEXT_COLOR}; '
        f'white-space: pre; '
        f'}}'
        f'</style>'
    ]

    # Each row gets its own clip and wipe animation.
    for y, text in enumerate(rows):
        yy = y * line_height + font_size

        clip_id = f"rowClip{y}"

        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{y * line_height}" '
            f'width="0" height="{line_height}">'
            f'<animate attributeName="width" '
            f'from="0" to="{svg_width}" '
            f'dur="1.1s" begin="{y * 0.035:.3f}s" '
            f'fill="freeze"/>'
            f'</rect>'
            f'</clipPath>'
        )

        parts.append(
            f'<text x="0" y="{yy}" clip-path="url(#{clip_id})">'
            f'{escape_xml(text)}'
            f'</text>'
        )

    parts.append("</svg>")

    OUTPUT.write_text(
        "\n".join(parts),
        encoding="utf-8"
    )

    print(f"Done: {OUTPUT}")


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    main()