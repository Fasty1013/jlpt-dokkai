"""Generate site icons from the header monogram (white 読 on vermilion #d03b2b).

Usage: python tools/make_icons.py [path/to/font]
Default font: Yu Mincho Demibold (Windows), close to the header's 'Noto Serif JP' 700.
Output (static/icons/):
  favicon.ico            16/32/48, rounded square (browser tab)
  icon-32.png            32x32, rounded square (<link rel="icon">)
  apple-touch-icon.png   180x180, full bleed (iOS rounds it itself)
  icon-192.png, icon-512.png  full bleed, glyph inside the 80% maskable safe zone (manifest)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "icons")
FONT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Windows\Fonts\yumindb.ttf"
BG = (0xD0, 0x3B, 0x2B, 255)
FG = (255, 255, 255, 255)
GLYPH = "読"
SS = 8  # supersampling factor


def render(size: int, rounded: bool, glyph_ratio: float) -> Image.Image:
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=int(big / 6), fill=BG)
    else:
        d.rectangle([0, 0, big, big], fill=BG)
    font = ImageFont.truetype(FONT, int(big * glyph_ratio))
    l, t, r, b = d.textbbox((0, 0), GLYPH, font=font)
    x = (big - (r - l)) / 2 - l
    y = (big - (b - t)) / 2 - t
    d.text((x, y), GLYPH, font=font, fill=FG)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    # Tab icons: big glyph so it stays readable at 16 px.
    tab = {s: render(s, rounded=True, glyph_ratio=0.80) for s in (16, 32, 48)}
    tab[48].save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)],
                 append_images=[tab[16], tab[32]])
    tab[32].save(os.path.join(OUT, "icon-32.png"))
    render(180, rounded=False, glyph_ratio=0.62).save(os.path.join(OUT, "apple-touch-icon.png"))
    for s in (192, 512):
        render(s, rounded=False, glyph_ratio=0.58).save(os.path.join(OUT, f"icon-{s}.png"))
    for name in sorted(os.listdir(OUT)):
        print(name, os.path.getsize(os.path.join(OUT, name)), "bytes")


if __name__ == "__main__":
    main()
