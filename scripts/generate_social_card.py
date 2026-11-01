"""Render the documentation's share image using its logo, typography, and signal plot."""

from pathlib import Path

import matplotlib
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/assets/social/lzsuite.png"
FONTS = Path(matplotlib.get_data_path()) / "fonts/ttf"


def font(size, *, bold=False, mono=False):
    """Load the bundled fonts so the poster can be reproduced on every platform."""
    family = "DejaVuSansMono" if mono else "DejaVuSans"
    suffix = "-Bold" if bold else ""
    return ImageFont.truetype(str(FONTS / f"{family}{suffix}.ttf"), size)


def main():
    """Create a 1200 by 630 PNG with a readable title and the existing hero graphic."""
    background, text, muted, border = "#151a22", "#e2e8f2", "#adb9cc", "#343e4e"
    card = Image.new("RGB", (1200, 630), background)
    draw = ImageDraw.Draw(card)
    logo = Image.open(ROOT / "docs/assets/favicon.png").convert("RGBA")
    logo.thumbnail((52, 52), Image.Resampling.LANCZOS)
    card.paste(logo, (60, 52), logo)
    draw.text((128, 51), "lzsuite", font=font(42, bold=True), fill=text)
    draw.text((905, 69), "Python 3.10+ · MIT", font=font(18), fill=muted)

    draw.text((60, 187), "Lempel–Ziv analysis", font=font(48, bold=True), fill=text)
    draw.text((60, 249), "for NumPy arrays.", font=font(48, bold=True), fill=text)
    draw.text((63, 353), "Discretization, complexity,", font=font(24), fill=muted)
    draw.text((63, 388), "entropy, and information distance.", font=font(24), fill=muted)

    draw.rounded_rectangle((715, 169, 1140, 477), radius=10, outline=border, width=2)
    draw.text((737, 186), "Mean binarization", font=font(19, bold=True), fill=text)
    plot = Image.open(ROOT / "docs/assets/figures/dark/hero.png").convert("RGB")
    plot.thumbnail((395, 150), Image.Resampling.LANCZOS)
    card.paste(plot, (730 + (395 - plot.width) // 2, 222))
    draw.line((716, 375, 1139, 375), fill=border, width=1)
    draw.text((738, 398), "lzs.h(data, axis=0)", font=font(22, mono=True), fill="#a0c0ff")
    draw.text((738, 438), "(2000, 4, 3) → (4, 3)", font=font(18, mono=True), fill=muted)

    draw.line((60, 530, 1140, 530), fill=border, width=1)
    draw.text((63, 555), "el3ssar.github.io/lzsuite", font=font(20), fill=muted)
    draw.text((919, 555), "pip install lzsuite", font=font(18, mono=True), fill=text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    card.save(OUT, optimize=True)
    print(f"Generated {OUT.relative_to(ROOT)} ({card.width} × {card.height})")


if __name__ == "__main__":
    main()
