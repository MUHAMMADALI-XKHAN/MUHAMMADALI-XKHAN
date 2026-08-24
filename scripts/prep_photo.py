from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        sys.exit(1)

    source = Path(sys.argv[1])

    if not source.exists():
        print(f"File not found: {source}")
        sys.exit(1)

    print("Removing background...")

    with open(source, "rb") as f:
        input_data = f.read()

    output_data = remove(input_data)

    # Convert the background-removed image to RGBA
    image = Image.open(__import__("io").BytesIO(output_data)).convert("RGBA")

    # White background
    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    white.alpha_composite(image)

    # Convert to grayscale
    gray = cv2.cvtColor(
        np.array(white.convert("RGB")),
        cv2.COLOR_RGB2GRAY
    )

    # Improve local contrast using CLAHE
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Keep background white
    rgba = np.array(white)
    alpha = np.array(image.getchannel("A"))

    enhanced_rgba = np.dstack([
        enhanced,
        enhanced,
        enhanced,
        alpha
    ])

    # Pixels outside the subject become pure white
    enhanced_rgba[alpha < 10] = [255, 255, 255, 255]

    output = Image.fromarray(enhanced_rgba.astype(np.uint8), "RGBA")
    output_path = Path("source-prepped.png")
    output.save(output_path)

    print(f"Done: {output_path}")


if __name__ == "__main__":
    main()