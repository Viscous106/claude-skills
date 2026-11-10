"""Tile photos into labelled overview sheets: photo_sheet.py OUT.jpg IMG..."""
import sys
from PIL import Image, ImageDraw, ImageOps

out, paths = sys.argv[1], sys.argv[2:]
cell, cols = 320, 6
rows = (len(paths) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rows * cell), "black")
for i, p in enumerate(paths):
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    im.thumbnail((cell - 6, cell - 22))
    x, y = (i % cols) * cell, (i // cols) * cell
    sheet.paste(im, (x + (cell - im.width) // 2, y + 20))
    ImageDraw.Draw(sheet).text((x + 4, y + 4), "/".join(p.split("/")[-2:]) if "/Win/" in p or "/merch/" in p else p.split("/")[-1].replace("_enhanced.png", ""), fill="yellow")
sheet.save(out, quality=85)
