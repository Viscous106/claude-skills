"""Trip vlog thumbnail: Polaroid tiles of the best moments + big title. usage: make_thumb.py OUT.jpg"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

here = Path(__file__).resolve().parents[1]
M = Path("/home/viscous/Viscous/Mumbai")
W, H = 1280, 720
bold = lambda s: ImageFont.truetype(str(here / "fonts/Poppins-ExtraBold.ttf"), s)
script = lambda s: ImageFont.truetype(str(here / "fonts/Pacifico-Regular.ttf"), s)


def load(path, sat=1.22):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(sat)).enhance(1.06)


def crop_to(im, w, h, fx=0.5, fy=0.5, region=None):
    if region:
        x0, y0, x1, y1 = region
        im = im.crop((int(im.width * x0), int(im.height * y0), int(im.width * x1), int(im.height * y1)))
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = min(max(int(im.width * fx - w / 2), 0), im.width - w)
    y = min(max(int(im.height * fy - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def polaroid(photo, angle, border=12, bottom=12, caption=None, cap_size=28):
    w, h = photo.size
    card = Image.new("RGBA", (w + 2 * border, h + border + bottom), (255, 255, 255, 255))
    card.paste(photo, (border, border))
    if caption:
        d = ImageDraw.Draw(card)
        f = script(cap_size)
        d.text(((card.width - d.textlength(caption, font=f)) / 2, h + border - 6), caption, font=f, fill=(60, 40, 90))
    card = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 150), mask=card.split()[3])
    return card, shadow.filter(ImageFilter.GaussianBlur(10))


def place(canvas, tile, xy):
    card, shadow = tile
    canvas.alpha_composite(shadow, (xy[0] + 8, xy[1] + 12))
    canvas.alpha_composite(card, xy)


bg = crop_to(load(M / "Juhu Beach/GOPR0087_enhanced.png"), W, H, 0.5, 0.4).filter(ImageFilter.GaussianBlur(14))
canvas = ImageEnhance.Brightness(bg).enhance(0.5).convert("RGBA")

team = crop_to(load(M / "Eth Global/GOPR0172_enhanced.png"), 470, 352, 0.55, 0.42)
call = crop_to(load(here / "thumb/call.png", 1.35), 300, 225, 0.42, 0.45)
sunset = crop_to(load(M / "Juhu Beach/GOPR0087_enhanced.png"), 220, 220, 0.5, 0.5)
bridge = crop_to(load(here / "thumb/bridge.png"), 250, 165, 0.5, 0.5)
win = load(M / "Eth Global/Win/IMG-20261107-WA0006_enhanced.png", 1.0)
win = crop_to(win, 340, 104, 0.5, 0.5, region=(0.385, 0.605, 0.975, 0.915))

place(canvas, polaroid(bridge, 6, bottom=40, caption="BLR to MUM"), (30, 440))
place(canvas, polaroid(sunset, -6, bottom=40, caption="Juhu"), (300, 400))
place(canvas, polaroid(call, -4, bottom=46, caption="the call..."), (960, 360))
place(canvas, polaroid(team, 3, border=14, bottom=52, caption="the team", cap_size=32), (560, 18))
place(canvas, polaroid(win, -3, border=10, bottom=10), (590, 500))

img = canvas.convert("RGB")
draw = ImageDraw.Draw(img)


def text(xy, s, font, fill, stroke):
    draw.text((xy[0] + 5, xy[1] + 7), s, font=font, fill=(0, 0, 0), stroke_width=stroke, stroke_fill=(0, 0, 0))
    draw.text(xy, s, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


text((40, 20), "MUMBAI", bold(118), (255, 255, 255), 9)
text((40, 150), "HACKATHON", bold(74), (255, 214, 0), 7)
text((40, 240), "2nd PLACE!", bold(74), (255, 214, 0), 7)
tag, f = "ETHGlobal Mumbai", bold(30)
tw = draw.textlength(tag, font=f)
draw.rounded_rectangle((46, 345, 46 + tw + 40, 345 + 54), radius=27, fill=(140, 42, 200), outline=(0, 0, 0), width=3)
draw.text((66, 350), tag, font=f, fill=(255, 255, 255))

out = Path(sys.argv[1])
img.save(out, quality=92, optimize=True)
print(out, img.size, f"{out.stat().st_size / 1e6:.2f} MB")
