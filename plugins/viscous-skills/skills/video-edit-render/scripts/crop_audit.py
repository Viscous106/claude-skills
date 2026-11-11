"""Show what a fit=crop / photo crop keeps: source frame with the kept window drawn on it.
usage: crop_audit.py OUTDIR PLAN.json [PLAN.json ...]   (VLOG_FOOTAGE = footage root)
Writes OUTDIR/<plan>_NN.jpg sheets (one row per cropped segment, frames at 10/50/90 %)
and prints a line per segment with the number of detected faces outside the window."""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

footage = Path(os.environ["VLOG_FOOTAGE"])
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
TW = 400  # thumb width
HAAR = os.environ.get("HAAR") or (getattr(getattr(cv2, "data", None), "haarcascades", "") + "haarcascade_frontalface_default.xml")
import threading
_tl = threading.local()


def cascade():
    if not hasattr(_tl, "c"):
        _tl.c = cv2.CascadeClassifier(HAAR)
    return _tl.c
tmp = Path(tempfile.mkdtemp())


def grab(seg, t, i):
    p = tmp / f"{abs(hash((seg.get('src'), t)))}_{i}.png"
    if "photo" in seg:
        src = Path(seg["photo"]) if Path(seg["photo"]).is_absolute() else footage / seg["photo"]
        Image.open(src).convert("RGB").save(p)
        return p
    pre = {90: ["transpose=1"], -90: ["transpose=2"], 180: ["hflip,vflip"]}.get(seg.get("rotate", 0), [])
    if seg.get("tilt"):
        pre.append(f"rotate={seg['tilt']}*PI/180:ow=iw:oh=ih,scale=iw*1.3:-2,crop=iw/1.3:ih/1.3")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", str(t), "-i", str(footage / seg["src"]),
                    "-frames:v", "1", "-vf", ",".join(pre + ["scale=1280:-2"]), str(p)], check=True)
    return p


def window(sw, sh, W, H, z, focus):
    r = max(W * z / sw, H * z / sh)
    iw, ih = sw * r, sh * r
    x0 = (iw - W) * focus / iw
    y0 = (ih - H) / 2 / ih
    return x0, y0, x0 + W / iw, y0 + H / ih


def audit(plan_path):
    plan = json.load(open(plan_path))
    W, H = plan["width"], plan["height"]
    rows = []
    for n, seg in enumerate(plan["segments"]):
        is_photo = "photo" in seg
        if is_photo and seg.get("fit") == "blur":
            continue
        if not is_photo and seg.get("fit", "blur") != "crop":
            continue
        if is_photo:
            ts = [0]
        else:
            ts = [seg["in"] + (seg["out"] - seg["in"]) * f for f in (0.1, 0.5, 0.9)]
        rows.append((n, seg, ts))

    def do(row):
        n, seg, ts = row
        thumbs, outside, total = [], 0, 0
        for k, t in enumerate(ts):
            fp = grab(seg, t, f"{n}_{k}")
            im = Image.open(fp).convert("RGB")
            sw, sh = im.size
            if "photo" in seg:
                box = window(sw, sh, W * 2, H * 2, 1.0, seg.get("focus", 0.5))
            else:
                box = window(sw, sh, W, H, seg.get("zoom", 1.0), seg.get("focus", 0.5))
            g = cv2.cvtColor(cv2.imread(str(fp)), cv2.COLOR_BGR2GRAY)
            faces = cascade().detectMultiScale(g, 1.1, 6, minSize=(max(24, sw // 40),) * 2)
            th = im.resize((TW, round(sh * TW / sw)))
            d = ImageDraw.Draw(th)
            s = TW / sw
            for (x, y, w, h) in faces:
                cx, cy = (x + w / 2) / sw, (y + h / 2) / sh
                inside = box[0] <= cx <= box[2] and box[1] <= cy <= box[3]
                total += 1
                outside += not inside
                d.rectangle((x * s, y * s, (x + w) * s, (y + h) * s), outline=(0, 255, 0) if inside else (255, 0, 0), width=3)
            d.rectangle((box[0] * TW, box[1] * th.height, box[2] * TW, box[3] * th.height), outline=(255, 230, 0), width=4)
            thumbs.append(th)
        return n, seg, thumbs, outside, total

    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(do, rows))
    font = ImageFont.load_default(size=20)
    name = Path(plan_path).stem
    per = 6
    for p in range(0, len(res), per):
        chunk = res[p:p + per]
        rh = max(max(t.height for t in r[2]) for r in chunk) + 30
        sheet = Image.new("RGB", (TW * 3 + 20, rh * len(chunk)), (30, 30, 30))
        d = ImageDraw.Draw(sheet)
        for j, (n, seg, thumbs, o, tot) in enumerate(chunk):
            src = seg.get("src") or seg.get("photo")
            d.text((6, j * rh + 4), f"#{n} {Path(src).parent.name}/{Path(src).name} "
                   f"{seg.get('in', '')}-{seg.get('out', '')} focus={seg.get('focus', 0.5)}"
                   f"{' faces-out=%d/%d' % (o, tot) if tot else ''}", fill=(255, 0, 0) if o else (255, 255, 255), font=font)
            for k, th in enumerate(thumbs):
                sheet.paste(th, (k * (TW + 10), j * rh + 28))
        sheet.save(out / f"{name}_{p // per:02d}.jpg", quality=85)
    for n, seg, thumbs, o, tot in res:
        print(f"{name}\t#{n}\t{seg.get('src') or seg.get('photo')}\t{seg.get('in', '')}-{seg.get('out', '')}\t"
              f"focus={seg.get('focus', 0.5)}\tfaces_out={o}/{tot}")


for pp in sys.argv[2:]:
    audit(pp)
