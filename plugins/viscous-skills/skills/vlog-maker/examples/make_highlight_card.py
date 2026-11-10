"""Prize card graphic: the ETHGlobal Arkiv card on a blurred backdrop, Mergit's row outlined, '2nd PLACE!' above."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

src = Image.open("/home/viscous/Viscous/Mumbai/Eth Global/Win/IMG-20261107-WA0006_enhanced.png").convert("RGB")
BOX = (0.383, 0.613, 0.970, 0.910)  # Mergit's 2nd-place row, as fractions of the card


def make(W, H, out, card_w_frac, title_y):
    bg = src.resize((W, H)).filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.35)
    cw = int(W * card_w_frac)
    ch = int(cw * src.height / src.width)
    x0, y0 = (W - cw) // 2, int(H * title_y) + int(H * (0.12 if W > H else 0.07))
    bg.paste(src.resize((cw, ch), Image.LANCZOS), (x0, y0))
    d = ImageDraw.Draw(bg)
    bx = (x0 + BOX[0] * cw, y0 + BOX[1] * ch, x0 + BOX[2] * cw, y0 + BOX[3] * ch)
    for k in range(7):
        d.rounded_rectangle((bx[0] - 8 - k, bx[1] - 8 - k, bx[2] + 8 + k, bx[3] + 8 + k), radius=22, outline=(255, 214, 0))
    f = ImageFont.truetype("fonts/Poppins-ExtraBold.ttf", int(H * (0.09 if W > H else 0.055)))
    t = "2nd PLACE!"
    d.text(((W - d.textlength(t, font=f)) / 2, H * title_y), t, font=f, fill=(255, 214, 0), stroke_width=6, stroke_fill=(0, 0, 0))
    bg.save(out, quality=94)


make(1920, 1080, "gfx/win_card_16x9.jpg", 0.74, 0.015)
make(1080, 1920, "gfx/win_card_9x16.jpg", 0.96, 0.555)
