"""Build plans/<cut>.json for the Mumbai trip: the YouTube vlog and one Reel per place.

Sources are relative to the Mumbai folder (render with VLOG_FOOTAGE=/home/viscous/Viscous/Mumbai).
Captions live once per clip in captions.py (source-clip time); every segment picks up the lines that
fall inside its in/out window, so trimming a segment never needs caption edits.
"""
import json
from pathlib import Path

from captions import CAP

edit = Path(__file__).resolve().parents[1]

CREDIT = "Music: Kevin MacLeod (incompetech.com) · CC BY 4.0"
EDITOR = "Edited and Produced by Yash Virulkar"


def clip(src, a, b, cap=True, audio=None, **kw):
    seg = {"src": src, "in": a, "out": b, **kw}
    if audio:  # (src, in) of another clip whose sound plays under this picture
        seg["audio"] = {"src": audio[0], "in": audio[1], **({"vol": audio[2]} if len(audio) > 2 else {})}
    if cap:
        csrc, c0 = (audio[0], audio[1]) if audio else (src, a)
        span = (b - a) / kw.get("speed", 1.0)
        subs = [[round(s - c0, 2), round(e - c0, 2), t] for s, e, t in CAP.get(csrc, [])
                if s >= c0 - 0.3 and s < c0 + span - 0.4]
        if subs:
            seg["subs"] = [[max(s, 0), min(e, span), t] for s, e, t in subs]
    return seg


def photo(name, dur=2.5, **kw):
    return {"photo": name, "dur": dur, **kw}


def pop(text, start=0.2, end=2.0, y=0.25):
    return {"text": text, "style": "Pop", "start": start, "end": end, "y": y}


def label(text, start=0.3, end=2.8, pos=None):
    d = {"text": text, "style": "Label", "start": start, "end": end}
    if pos:
        d["pos"] = pos
    return d


def title(text, sub=None, start=0.3, end=3.5, credits=None):
    d = {"text": text, "start": start, "end": end}
    if sub:
        d["sub"] = sub
    if credits:
        d["credits"] = credits
    return d


def dur(seg):
    return seg["dur"] if "photo" in seg else (seg["out"] - seg["in"]) / seg.get("speed", 1.0)


def assemble(name, w, h, chapters):
    segs, music, t = [], [], 0.0
    for ch in chapters:
        start = t
        for s in ch["segments"]:
            segs.append(s)
            t += dur(s)
        for m in ch.get("music", []):
            length = (t - start) + m.get("extra", 0)
            music.append({"src": f"music/{m['track']}.mp3", "at": round(start + m.get("offset", 0), 2),
                          "from": m.get("from", 0), "dur": round(length - m.get("offset", 0), 2),
                          "vol": m["vol"], "fade": m.get("fade", 1.2)})
        print(f"  {ch['name']:<14} {start:7.1f} → {t:7.1f}  ({t - start:5.1f}s)")
    plan = {"name": name, "width": w, "height": h, "fps": 30, "duck": True, "segments": segs, "music": music}
    (edit / "plans").mkdir(exist_ok=True)
    (edit / "plans" / f"{name}.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    print(f"{name}: {len(segs)} segments, {t:.1f}s ({t / 60:.1f} min)")
    return plan


TR, GH, JU, GE = "travel/", "Guest House/", "Juhu Beach/", "General/"
EG, JI, MD, SH, CC = "Eth Global/", "Jio convection/", "Marine drive/", "shayari/", "Cat Cafe/"
GFX = str(edit / "gfx") + "/"  # made by make_wincard.py; absolute paths win over the footage root


def gx(folder, n):
    return f"{folder}GX0{n}_enhanced.mp4"


# ================================================================= YouTube 16:9 trip vlog
SPECIAL = (20.7, 23.4)  # WA0143: just "...kuch toh special hua aaj" (the chocolate-shake talk before it is out)
yt = [
    {"name": "hook", "segments": [
        clip(MD + "VID-20261108-WA0141.mp4", 20.0, 29.4, titles=[label("Marine Drive · 7 Nov", 0.2, 2.6),
                                                                 pop("Ek phone call...", 1.0, 4.5, 0.18)]),
    ]},
    {"name": "title", "music": [{"track": "Life of Riley", "vol": 0.40, "fade": 0.8}],
     "segments": [
         clip(TR + "VID-20261108-WA0154.mp4", 0.0, 6.0, vol=0.0, fade_in=0.3,
              titles=[title("Mumbai Trip", "BLR → MUM · 5 DIN · 5 DOST", 0.4, 5.8)]),
     ]},
    {"name": "departure", "music": [{"track": "Life of Riley", "from": 6.0, "vol": 0.12}],
     "segments": [
         clip(GE + "b0925541a84ad47f742431fcb83a402bdbe49f5c9aed5514350f53bdbdd6d869.mp4", 0.0, 5.0, vol=0,
              titles=[pop("4 din pehle...", 0.2, 2.2, 0.2)]),
         clip(TR + "GX010075.MP4", 0.0, 15.0, titles=[label("Yash", 9.0, 12.9)]),  # ends on "Hi bolo guys!"
         # the bird got Yash's tee on the way (GX010085), then Div tells the story at the bus stand
         clip(TR + "GX010085.MP4", 0.0, 1.9, titles=[pop("Chidiya ne beat kar di!", 0.3, 3.9, 0.2)]),
         photo(GFX + "bird_hold.jpg", 2.0, kenburns="in"),
         clip(TR + "GX010090.MP4", 0.8, 31.0, titles=[pop("Shubh sanket?!", 10.2, 13.5, 0.2)]),
         clip(TR + "GX010093.MP4", 0.2, 39.3, titles=[label("Soham", 9.0, 13.0), label("Abhinav", 23.4, 27.6),
                                                      label("Divija & Div", 33.2, 37.8)]),
         clip(TR + "GX010093.MP4", 43.5, 52.8, rotate=-90),
     ]},
    {"name": "busnight", "music": [{"track": "Meditation Impromptu 01", "vol": 0.09, "fade": 1.5}],
     "segments": [
         clip(TR + "VID-20261108-WA0118.mp4", 6.6, 8.9, vol=0.2),
         clip(gx(TR, 10027), 0.0, 17.3),
         clip(TR + "VID-20261108-WA0147.mp4", 24.5, 51.0),
         clip(gx(SH, 10040), 0.5, 20.4, titles=[pop("Bus mein shayari session", 0.2, 2.6, 0.18)]),
         clip(gx(SH, 10041), 1.0, 11.3),
         # the rest of the take is on 041's sound; its picture swings to a stranger, so it plays over the
         # window view from 038 (nobody on screen talking -> no lip-sync mismatch)
         clip(gx(SH, 10038), 0.4, 11.8, audio=(gx(SH, 10041), 11.3)),
         clip(gx(SH, 10038), 20.4, 34.3, titles=[pop("FRIEND-ZONED!", 1.0, 4.0, 0.22)]),
         clip(gx(SH, 10042), 0.1, 47.3, titles=[pop("Shayari, part 2", 0.3, 2.8, 0.18)]),
     ]},
    {"name": "dawn", "music": [{"track": "Easy Lemon", "vol": 0.22, "fade": 1.5}],
     "segments": [
         clip(TR + "VID-20261104-WA0043.mp4", 0.5, 5.5, vol=0),
         clip(gx(TR, 10002), 0.0, 2.2, vol=0),
         clip(gx(TR, 10048), 0.0, 19.5),
     ]},
    {"name": "expressway", "music": [{"track": "Hyperfun", "vol": 0.42, "fade": 1.5}],
     "segments": [
         clip(gx(TR, 10017), 6.8, 12.0, vol=0, titles=[pop("Mumbai–Pune Expressway", 0.3, 2.8, 0.2)]),
         clip(gx(TR, 10016), 0.0, 18.0, speed=3.0),
         clip(gx(TR, 10020), 24.0, 36.0, speed=2.0),
         clip(gx(TR, 10020), 36.0, 51.0, speed=1.5),
         clip(gx(TR, 10022), 0.0, 7.0, vol=0),
         clip(TR + "VID-20261104-WA0054.mp4", 0.0, 6.0, vol=0, titles=[pop("Mumbai pahunch gaye!", 0.3, 4.0, 0.22)]),
     ]},
    {"name": "guesthouse", "music": [{"track": "Local Forecast - Elevator", "vol": 0.12, "fade": 1.5}],
     "segments": [
         clip(GH + "GG010004_enhanced.mp4", 0.0, 2.8, vol=0.4, titles=[label("Hamara hotel", 0.2, 2.8)]),
         clip(gx(GH, 10117), 0.0, 20.6),
         clip(gx(GH, 10131), 26.9, 33.0, vol=0.3, cap=False),
     ]},
    {"name": "juhu", "music": [{"track": "Easy Lemon", "from": 20.0, "vol": 0.13, "fade": 1.5}],
     "segments": [
         clip(gx(TR, 10051), 0.0, 5.5, vol=0.3),
         clip(gx(GE, 10049), 1.2, 19.0),  # 19-44 asks strangers on the street: left out
         clip(gx(JU, 10053), 0.0, 3.0, vol=0.3),
         clip(gx(TR, 10061), 0.0, 4.0, vol=0.2),
         clip(gx(TR, 10061), 113.0, 122.0, vol=0.2, titles=[title("Juhu Beach", "DAY 1 · 4 NOV", 0.4, 6.0)]),
         clip(gx(JU, 10073), 1.0, 24.3),
         clip(gx(JU, 10071), 0.0, 4.0, vol=0.3),
         clip(gx(JU, 10085), 0.0, 6.8, titles=[pop("Kulfi cheers!", 0.1, 1.6, 0.2)]),
         clip(gx(JU, 10093), 0.0, 7.1, vol=0.8),
         clip(gx(JU, 10094), 0.0, 7.0, vol=0.6),
         clip(gx(JU, 10074), 17.0, 22.0, vol=0.5),
         clip(gx(JU, 10103), 0.0, 21.0),
         clip(gx(JU, 10103), 21.0, 35.5, rotate=90),
         clip(gx(JU, 10108), 0.0, 5.0, vol=0.3),
         clip(gx(JU, 10110), 27.7, 33.0, audio=(gx(JU, 10115), 0.2)),  # "ecstatic... okay" over the stalls
         clip(gx(JU, 10110), 47.3, 51.0, audio=(gx(JU, 10115), 5.5)),
         clip(gx(JU, 10110), 6.4, 7.6, audio=(gx(JU, 10115), 9.2)),
     ]},
    {"name": "hackmorning", "music": [{"track": "Funkorama", "vol": 0.11, "fade": 1.5}],
     "segments": [
         clip(GH + "VID-20261108-WA0098.mp4", 2.0, 41.0),
         clip(gx(GH, 10131), 9.0, 17.3, audio=(gx(GH, 10131), 2.9)),
         clip(gx(GH, 10142), 0.6, 7.3),
         clip(gx(GH, 10131), 26.9, 38.4, audio=(gx(GH, 10142), 7.3)),
         clip(gx(GH, 10123), 0.0, 12.9, rotate=90),
         clip(gx(TR, 10161), 0.0, 4.0, vol=0.2),
         clip(gx(TR, 10167), 22.4, 27.0, vol=0.2, titles=[pop("BKC", 0.3, 3.5, 0.22)]),
     ]},
    {"name": "ethday", "music": [{"track": "Pamgaea", "vol": 0.14, "fade": 1.5}],
     "segments": [
         photo(EG + "GOPR0172_enhanced.png", 5.0, fit="blur", titles=[
             title("ETHGlobal Mumbai", "JIO WORLD CONVENTION CENTRE", 0.2, 2.4),
             label("Yash", 2.4, 5.0, (0.36, 0.66)), label("Abhinav", 2.5, 5.0, (0.49, 0.27)),
             label("Div", 2.6, 5.0, (0.555, 0.72)), label("Divija", 2.7, 5.0, (0.645, 0.19)),
             label("Soham", 2.8, 5.0, (0.73, 0.66))]),
         clip(gx(EG, 10175), 0.0, 5.0, vol=0.3, cap=False),
         clip(gx(EG, 10178), 0.0, 5.7, vol=0.4, cap=False, titles=[pop("Devcon badge banao!", 0.3, 3.0, 0.2)]),
         clip(gx(EG, 10187), 0.0, 5.0, vol=0.5, cap=False),
         clip(gx(EG, 10193), 0.0, 10.5, vol=0.4, cap=False, titles=[pop("Hacking shuru!", 0.5, 3.0, 0.2)]),
         clip(gx(EG, 10197), 0.5, 5.0, vol=0.3, cap=False),
     ]},
    {"name": "ethnight", "music": [{"track": "Thinking Music", "vol": 0.10, "fade": 1.5}],
     "segments": [
         clip(JI + "VID_20261105_223559.mp4", 22.0, 28.0, vol=0.3, cap=False),
         clip(gx(EG, 10206), 0.0, 8.0, vol=0.3, cap=False),
         clip(gx(EG, 10204), 0.5, 66.5),
         clip(gx(JI, 10222), 15.0, 70.0, titles=[pop("4 AM: building explore", 0.2, 4.8, 0.2)]),
         clip(gx(JI, 10222), 155.0, 203.0),
         clip(gx(EG, 10223), 0.0, 16.9),
         clip(gx(EG, 10234), 1.8, 13.5, rotate=-90, titles=[pop("Soham.exe has stopped", 0.3, 3.5, 0.2)]),
         photo(EG + "GOPR0229_enhanced.png", 2.0, fit="blur"),
     ]},
    {"name": "ethjudge", "music": [{"track": "Pamgaea", "from": 60.0, "vol": 0.14, "fade": 1.5}],
     "segments": [
         clip(gx(EG, 10246), 0.5, 6.5),
         clip(gx(EG, 10247), 2.5, 6.2, vol=0.3, cap=False),
         clip(gx(EG, 10248), 3.5, 6.2, vol=0.3, cap=False),
         clip(EG + "VID-20261108-WA0123.mp4", 0.0, 7.1, vol=0.4, cap=False, titles=[pop("Mehendi break", 0.3, 2.4, 0.2)]),
         clip(EG + "VID-20261108-WA0012.mp4", 0.0, 15.0, vol=0.5, cap=False,
              titles=[pop("Judging time!", 0.3, 2.8, 0.2)]),
         photo(EG + "WhatsApp Image 2026-11-09 at 9.38.17 PM.jpeg", 3.0, fit="blur",
               titles=[pop("Hackathon: DONE!", 0.3, 2.8, 0.15)]),
         clip(gx(TR, 10256), 3.5, 30.0),
         clip(gx(TR, 10261), 35.6, 45.0, speed=1.5, vol=0),
     ]},
    {"name": "jio", "music": [{"track": "Wholesome", "vol": 0.12, "fade": 1.5}],
     "segments": [
         clip(JI + "VID_20261107_144321.mp4", 3.0, 11.0, vol=0, titles=[pop("Jio World Centre", 0.3, 3.0, 0.2)]),
         clip(JI + "VID-20261107-WA0001.mp4", 0.0, 55.2),
         clip(JI + "VID-20261108-WA0142.mp4", 0.0, 29.0),
         clip(JI + "VID-20261107-WA0002.mp4", 0.0, 89.1, titles=[label("Soham", 0.3, 3.0)]),
     ]},
    {"name": "marine_calm", "music": [{"track": "Dreamer", "vol": 0.12, "fade": 1.5}],
     "segments": [
         clip(MD + "VID-20261108-WA0141.mp4", 0.0, 20.0, titles=[title("Marine Drive", "7 NOV · RAAT", 0.4, 4.5)]),
     ]},
    {"name": "marine_call", "segments": [
        clip(MD + "VID-20261108-WA0141.mp4", 20.0, 29.4, titles=[
            pop("...tabhi Divija ka phone aaya", 0.1, 3.0, 0.18), label("Divija", 0.6, 3.0),
            pop("RESULT AA GAYA!", 6.4, 9.3, 0.18)]),
    ]},
    {"name": "marine_win", "music": [{"track": "Inspired", "vol": 0.30, "fade": 1.0}],
     "segments": [
         photo(GFX + "win_card_16x9.jpg", 5.5, focus=0.5),
     ]},
    {"name": "marine_react", "music": [{"track": "Inspired", "from": 8.0, "vol": 0.09, "fade": 1.5}],
     "segments": [
         clip(MD + "VID-20261108-WA0143.mp4", SPECIAL[0], SPECIAL[1]),  # "...kuch toh special hua aaj"
         clip(MD + "VID-20261108-WA0146.mp4", 0.0, 22.0),               # Div: "hum jeet chuke hai!"
         clip(MD + "VID-20261108-WA0146.mp4", 22.5, 35.0, mute=[[4.5, 5.6]]),
         clip(MD + "VID-20261108-WA0146.mp4", 35.0, 53.0),
         clip(MD + "VID-20261108-WA0143.mp4", 48.8, 72.5),
         clip(MD + "VID-20261108-WA0149.mp4", 0.0, 72.0),  # 72-93 is about the money (sponsored): left out
         photo(MD + "IMG-20261108-WA0061_enhanced.png", 3.0),
         clip(MD + "VID-20261108-WA0146.mp4", 53.0, 66.5),  # ends on Div's flying kiss
     ]},
    {"name": "oneam", "music": [{"track": "Fluffing a Duck", "vol": 0.12, "fade": 1.0}],
     "segments": [
         clip(GH + "Snapchat-1984466552.mp4", 0.0, 12.0, vol=0.6),
         clip(GH + "VID-20261108-WA0148.mp4", 0.0, 76.5, titles=[pop("1 AM: celebration waffles", 0.2, 4.3, 0.2)]),
     ]},
    {"name": "checkout", "music": [{"track": "Carefree", "vol": 0.11, "fade": 1.5}],
     "segments": [
         # skips 22.3-28.6 ("this is a fisheries research center": names the institute)
         # and 62.4-68.2 ("by the way, we got this from ENS Partner Track")
         clip(gx(GH, 10273), 0.1, 22.3, titles=[pop("8 Nov · last day", 0.2, 2.6, 0.2)]),
         clip(gx(GH, 10273), 28.6, 62.4),
         clip(gx(GH, 10273), 68.2, 123.4),
     ]},
    {"name": "catcafe", "music": [{"track": "Carefree", "from": 40.0, "vol": 0.13, "fade": 1.5}],
     "segments": [
         clip(gx(CC, 10274), 0.5, 7.9, titles=[label("Yash", 0.4, 2.8)]),
         clip(gx(CC, 10275), 0.0, 6.0, titles=[title("Cat Café Studio", "ANDHERI WEST", 0.4, 5.6)]),
         clip(gx(CC, 10275), 38.5, 48.0, titles=[label("Takishi", 6.0, 9.0)]),
         clip(gx(CC, 10288), 13.0, 25.0),
         clip(gx(CC, 10290), 0.0, 11.5),
         clip(gx(CC, 10291), 1.5, 7.5, vol=0.4, titles=[pop("Cone of shame", 0.5, 2.5, 0.2)]),
         clip(gx(CC, 10308), 0.0, 10.4, titles=[label("Sheena", 5.4, 8.4)]),
         photo(CC + "GOPR0309_enhanced.png", 3.0, focus=0.6,
               titles=[pop("Full cat café vlog channel pe!", 0.2, 2.9, 0.2)]),
         clip(gx(CC, 10319), 0.2, 4.0, vol=0.7),
     ]},
    {"name": "lastday", "music": [{"track": "Heartwarming", "vol": 0.16, "fade": 1.5, "extra": 0}],
     "segments": [
         clip(gx(TR, 10325), 0.0, 1.0, vol=0.3),
         clip(gx(TR, 10334), 3.0, 4.3, vol=0.3),
         clip(gx(MD, 10321), 4.5, 42.0),
     ]},
    {"name": "outro", "music": [{"track": "Heartwarming", "from": 22.0, "vol": 0.34, "fade": 2.0}],
     "segments": [
         clip(TR + "VID-20261108-WA0154.mp4", 9.9, 18.4, vol=0),
         photo(JU + "IMG-20261108-WA0069_enhanced.png", 3.0, fit="blur"),
         photo(EG + "WhatsApp Image 2026-11-09 at 9.38.08 PM.jpeg", 2.5, fit="blur"),
         photo(MD + "IMG-20261108-WA0085_enhanced.png", 2.5),
         photo(JU + "DSC_0016_enhanced.png", 7.0, fit="blur", titles=[title("Thanks for watching!", EDITOR, 0.3, 6.8,
                                                              credits=[CREDIT])]),
     ]},
]

# ================================================================= Reels 9:16 (one per place)
def end_card(text, sub):
    return {"text": text, "sub": sub, "credits": [EDITOR], "start": 0.2}


C = dict(fit="crop")  # landscape sources fill the vertical frame; aim with focus=


def B(zoom, focus):
    """people side by side / a big selfie face: show the middle 1/zoom of the width over a blurred fill"""
    return dict(fit="blur", zoom=zoom, focus=focus)


reel_travel = [
    {"name": "talk", "music": [{"track": "Life of Riley", "vol": 0.16, "fade": 1.0}], "segments": [
        clip(GE + "b0925541a84ad47f742431fcb83a402bdbe49f5c9aed5514350f53bdbdd6d869.mp4", 0.0, 3.0, vol=0, **C,
             titles=[pop("Bengaluru → Mumbai", 0.2, 2.9, 0.18)]),
        clip(TR + "GX010075.MP4", 0.0, 15.0, **B(1.4, 0.2), titles=[label("Yash", 9.0, 12.9)]),
        clip(TR + "GX010085.MP4", 0.0, 1.9, **B(1.3, 0.4), titles=[pop("Chidiya ne beat kar di!", 0.3, 3.3, 0.30)]),
        photo(GFX + "bird_hold.jpg", 1.5, fit="blur", zoom=1.3, focus=0.4),
        clip(TR + "GX010090.MP4", 0.8, 24.0, **B(1.15, 0.5), titles=[pop("Shubh sanket?!", 10.2, 13.5, 0.30)]),
        clip(TR + "GX010093.MP4", 0.2, 4.6, **B(1.3, 0.5)),
        clip(TR + "GX010093.MP4", 9.0, 30.5, **B(1.3, 0.45), titles=[label("Soham", 0.0, 4.0), label("Abhinav", 14.4, 18.6)]),
        clip(TR + "GX010093.MP4", 33.5, 39.2, **B(1.3, 0.5), titles=[label("Divija & Div", 0.2, 5.0)]),
        clip(TR + "VID-20261108-WA0118.mp4", 7.0, 8.9, vol=0, focus=0.5, **C),
        clip(gx(TR, 10027), 0.0, 7.0, focus=0.5, **C),
        clip(TR + "VID-20261108-WA0147.mp4", 46.0, 50.5, vol=0.4, focus=0.45, **C,
             titles=[pop("Overnight sleeper bus", 0.1, 3.4, 0.30)]),
        clip(gx(TR, 10048), 0.0, 19.5, **B(1.2, 0.5)),
    ]},
    {"name": "ride", "music": [{"track": "Hyperfun", "vol": 0.40, "fade": 1.0}], "segments": [
        clip(gx(TR, 10002), 0.0, 2.2, vol=0, **C),
        clip(gx(TR, 10017), 6.8, 12.0, vol=0, **C, titles=[pop("Mumbai–Pune Expressway", 0.2, 3.0, 0.30)]),
        clip(gx(TR, 10016), 0.0, 15.0, speed=3.0, focus=0.5, **C),
        clip(gx(TR, 10020), 30.0, 36.0, speed=2.0, focus=0.5, **C),
        clip(gx(TR, 10020), 40.0, 49.0, speed=1.5, focus=0.5, **C),
        clip(gx(TR, 10022), 0.0, 4.0, vol=0, focus=0.55, **C),
        clip(TR + "VID-20261108-WA0154.mp4", 9.9, 15.0, vol=0, focus=0.5, **C),
        clip(TR + "VID-20261104-WA0054.mp4", 0.0, 3.4, vol=0, focus=0.5, fade_out=0.4, **C,
             titles=[{**end_card("Mumbai!", "BLR → MUM · BY BUS"), "end": 3.4}]),
    ]},
]

reel_juhu = [
    {"name": "reel", "music": [{"track": "Easy Lemon", "vol": 0.16, "fade": 1.0}], "segments": [
        clip(gx(JU, 10053), 6.0, 9.0, vol=0.2, focus=0.3, **C, titles=[pop("POV: Mumbai, day 1", 0.1, 2.9, 0.18)]),
        clip(gx(GE, 10049), 1.2, 19.0, **B(1.2, 0.5)),
        clip(gx(TR, 10061), 113.0, 122.0, vol=0.2, focus=0.5, **C, titles=[pop("Juhu Beach!", 0.4, 4.0, 0.30)]),
        clip(gx(JU, 10073), 1.0, 18.3, focus=0.5, **C),
        clip(gx(JU, 10073), 18.3, 24.3, **B(1.0, 0.5)),
        clip(gx(JU, 10071), 1.0, 3.5, vol=0.2, focus=0.4, **C),
        clip(gx(JU, 10085), 0.0, 6.8, **B(1.3, 0.45), titles=[pop("Kulfi cheers!", 0.1, 1.8, 0.30)]),
        clip(gx(JU, 10093), 0.0, 7.1, vol=0.8, **B(2.0, 0.4)),
        clip(gx(JU, 10094), 0.0, 7.0, vol=0.6, focus=0.5, **C),
        clip(gx(JU, 10074), 17.0, 22.0, vol=0.3, focus=0.5, **C),
        clip(gx(JU, 10103), 0.0, 21.0, **B(1.0, 0.5)),
        clip(gx(JU, 10103), 21.0, 35.5, rotate=90, **C),
        clip(gx(JU, 10083), 8.5, 11.5, vol=0, focus=0.65, **C),
        clip(gx(JU, 10108), 0.0, 3.5, focus=0.6, audio=(gx(JU, 10115), 0.2), **C),
        clip(gx(JU, 10110), 28.0, 31.0, focus=0.5, audio=(gx(JU, 10115), 3.7), **C),
        clip(gx(JU, 10110), 47.3, 51.0, focus=0.5, fade_out=0.4, audio=(gx(JU, 10115), 6.7), **C,
             titles=[{**end_card("Juhu Beach", "MUMBAI · DAY 1"), "start": 0.3, "end": 3.7}]),
    ]},
]

reel_eth = [
    {"name": "reel", "music": [{"track": "Pamgaea", "vol": 0.14, "fade": 1.0}], "segments": [
        photo(EG + "GOPR0172_enhanced.png", 3.0, fit="blur", zoom=1.25, focus=0.5,
              titles=[pop("5 dost. 1 hackathon.", 0.1, 3.0, 0.18)]),
        clip(gx(EG, 10178), 0.0, 5.7, vol=0.3, cap=False, **C, titles=[pop("Devcon badge banao!", 0.3, 3.0, 0.30)]),
        clip(gx(EG, 10193), 0.5, 10.5, vol=0.3, focus=0.4, cap=False, **C, titles=[pop("Hacking shuru!", 0.5, 3.0, 0.30)]),
        clip(gx(EG, 10206), 0.0, 8.0, vol=0.3, cap=False, focus=0.5, **C, titles=[pop("Raat ke 3 baje...", 0.2, 3.5, 0.30)]),
        clip(gx(EG, 10204), 0.5, 12.0, focus=0.5, **C),
        clip(gx(EG, 10204), 12.0, 54.5, **B(1.2, 0.55)),
        clip(gx(EG, 10204), 54.5, 66.5, focus=0.5, **C),
        clip(gx(JI, 10222), 15.0, 30.0, speed=3.0, focus=0.5, **C, titles=[pop("4 AM: building explore", 0.2, 4.8, 0.30)]),
        clip(gx(JI, 10222), 186.0, 200.0, speed=2.0, focus=0.5, **C),
        clip(gx(EG, 10223), 0.0, 16.9, **B(1.2, 0.6)),
        clip(gx(EG, 10234), 1.8, 13.5, rotate=-90, **C, titles=[pop("Soham.exe has stopped", 0.3, 3.5, 0.30)]),
        clip(gx(EG, 10246), 0.5, 6.5, focus=0.5, **C),
        clip(EG + "VID-20261108-WA0123.mp4", 0.0, 7.1, vol=0.4, cap=False, **C, titles=[pop("Mehendi break", 0.3, 2.6, 0.30)]),
        clip(EG + "VID-20261108-WA0012.mp4", 0.0, 15.0, vol=0.4, cap=False, **B(1.1, 0.5),
             titles=[pop("Judging!", 0.2, 2.8, 0.30)]),
        photo(EG + "WhatsApp Image 2026-11-09 at 9.38.17 PM.jpeg", 3.0, fit="blur",
              titles=[pop("Hackathon: DONE!", 0.3, 2.8, 0.30)]),
        photo(GFX + "win_card_9x16.jpg", 4.5, focus=0.5,
              titles=[{**end_card("ETHGlobal Mumbai", "BUILD ON ARKIV · $1,000"), "start": 0.4, "end": 4.5}]),
    ]},
]

reel_jio = [
    {"name": "reel", "music": [{"track": "Wholesome", "vol": 0.16, "fade": 1.0}], "segments": [
        clip(JI + "VID_20261105_223559.mp4", 24.0, 28.0, vol=0, focus=0.5, **C,
             titles=[pop("Jio World Centre, Mumbai", 0.2, 3.8, 0.18)]),
        photo(EG + "GOPR0173_enhanced.png", 2.0, focus=0.5),
        clip(gx(EG, 10187), 0.0, 5.0, vol=0.2, focus=0.5, cap=False, **C, titles=[pop("Devcon talks", 0.2, 2.8, 0.30)]),
        clip(gx(EG, 10192), 3.5, 6.0, vol=0, focus=0.5, cap=False, **C),
        clip(JI + "VID_20261107_144321.mp4", 3.0, 11.0, vol=0, **C),
        clip(JI + "VID-20261107-WA0001.mp4", 0.0, 30.0, focus=0.5, **C),
        clip(JI + "VID-20261107-WA0001.mp4", 50.5, 55.2, **B(1.2, 0.5)),
        clip(JI + "VID-20261108-WA0142.mp4", 0.0, 15.0, focus=0.5, **C),
        clip(JI + "VID-20261108-WA0142.mp4", 22.0, 29.0, **B(1.1, 0.5)),
        clip(JI + "VID-20261107-WA0002.mp4", 0.0, 48.4, **B(1.4, 0.5), titles=[label("Soham", 0.2, 3.8)]),
        clip(JI + "VID-20261107-WA0002.mp4", 67.0, 89.1, **B(1.4, 0.5)),
        clip(JI + "VID-20261108-WA0115.mp4", 42.0, 46.0, vol=0, focus=0.5, **C),
        photo(JI + "IMG-20261108-WA0076_enhanced.png", 2.0, focus=0.5),
        photo(JI + "IMG_20261107_144239_HDR_enhanced.png", 3.5, focus=0.5,
              titles=[{**end_card("Jio World Centre", "DEVCON · MUMBAI"), "end": 3.5}]),
    ]},
]

reel_guesthouse = [
    {"name": "reel", "music": [{"track": "Funkorama", "vol": 0.12, "fade": 1.0}], "segments": [
        clip(GH + "GG010004_enhanced.mp4", 0.0, 2.8, vol=0.2, focus=0.5, **C,
             titles=[pop("Hamara Mumbai ghar", 0.1, 2.8, 0.18)]),
        photo(GH + "GOPR0014_enhanced.png", 1.5, focus=0.5),
        clip(gx(GH, 10117), 0.0, 9.5, **B(1.3, 0.5)),
        clip(GH + "VID-20261108-WA0098.mp4", 2.0, 20.0, focus=0.5, **C),
        clip(GH + "VID-20261108-WA0098.mp4", 29.5, 41.0, focus=0.5, **C),
        clip(gx(GH, 10131), 9.0, 17.3, focus=0.5, audio=(gx(GH, 10131), 2.9), **C),
        clip(gx(GH, 10132), 0.0, 1.3, vol=0.2, **C),
        photo(GH + "GOPR0137_enhanced.png", 0.8, focus=0.0),
        photo(GH + "GOPR0134_enhanced.png", 0.8, focus=1.0),
        photo(GH + "GOPR0136_enhanced.png", 0.8, focus=0.5),
        clip(gx(GH, 10142), 0.6, 7.3, **C),
        clip(gx(GH, 10131), 26.9, 38.4, focus=0.5, audio=(gx(GH, 10142), 7.3), **C),
        clip(gx(GH, 10123), 0.0, 12.9, rotate=90, focus=0.4, **C, titles=[pop("Hackathon mode: ON", 8.5, 12.5, 0.30)]),
        clip(GH + "Snapchat-1984466552.mp4", 0.0, 12.0, vol=0.5, cap=False, **C),
        clip(GH + "VID-20261108-WA0148.mp4", 6.0, 43.9, **B(1.2, 0.5), titles=[pop("1 AM: celebration waffles", 0.2, 4.0, 0.30)]),
        clip(GH + "VID-20261108-WA0148.mp4", 46.5, 50.2, **B(1.2, 0.5)),
        clip(gx(GH, 10273), 3.1, 9.1, **B(1.8, 0.6)),
        clip(gx(GH, 10273), 44.0, 62.4, focus=0.5, **C),
        clip(gx(GH, 10273), 110.5, 123.4, fade_out=0.4, **B(1.3, 0.3),
             titles=[{**end_card("Hamara Hotel", "MUMBAI"), "start": 8.0, "end": 12.9}]),
    ]},
]

reel_marine = [
    {"name": "reel", "music": [{"track": "Dreamer", "vol": 0.14, "fade": 1.0}], "segments": [
        clip(MD + "VID-20261108-WA0141.mp4", 0.0, 20.0, focus=0.5, **C,
             titles=[pop("Hackathon khatam. Marine Drive.", 0.2, 4.0, 0.18)]),
        clip(MD + "VID-20261108-WA0141.mp4", 20.0, 29.4, focus=0.5, **C,
             titles=[pop("...tabhi Divija ka phone aaya", 0.1, 2.6, 0.30), label("Divija", 0.3, 2.6)]),
    ]},
    {"name": "win", "music": [{"track": "Inspired", "vol": 0.12, "fade": 1.0}], "segments": [
        photo(GFX + "win_card_9x16.jpg", 3.5, focus=0.5),
        clip(MD + "VID-20261108-WA0143.mp4", SPECIAL[0], SPECIAL[1], **B(1.8, 0.75)),
        clip(MD + "VID-20261108-WA0146.mp4", 0.0, 14.0, **B(2.0, 0.1)),
        clip(MD + "VID-20261108-WA0146.mp4", 14.0, 22.5, **B(2.0, 0.25)),
        clip(MD + "VID-20261108-WA0146.mp4", 22.5, 35.0, mute=[[4.5, 5.6]], **B(2.0, 0.3)),
        clip(MD + "VID-20261108-WA0146.mp4", 35.0, 53.0, **B(1.15, 0.4)),
        clip(MD + "VID-20261108-WA0149.mp4", 15.0, 31.4, **B(1.2, 0.35)),
        clip(MD + "VID-20261108-WA0149.mp4", 41.5, 53.8, **B(1.3, 0.5)),
        clip(MD + "VID-20261108-WA0149.mp4", 53.8, 64.4, **B(1.05, 0.5)),
        clip(MD + "VID-20261108-WA0146.mp4", 53.0, 63.3, fade_out=0.4, **B(2.0, 0.15),
             titles=[{**end_card("ETHGlobal Mumbai", "2ND PLACE · BUILD ON ARKIV"), "start": 5.3, "end": 10.3}]),
    ]},
]

reel_shayari = [
    {"name": "reel", "music": [{"track": "Meditation Impromptu 01", "vol": 0.10, "fade": 1.5}], "segments": [
        clip(gx(SH, 10040), 0.5, 20.4, **B(1.3, 0.5), titles=[pop("Sleeper bus shayari", 0.2, 2.8, 0.18)]),
        clip(gx(SH, 10041), 1.0, 11.3, **B(1.3, 0.5)),
        clip(gx(SH, 10038), 0.4, 11.8, focus=0.5, audio=(gx(SH, 10041), 11.3), **C),
        clip(gx(SH, 10038), 20.4, 34.3, focus=0.5, **C, titles=[pop("FRIEND-ZONED!", 1.0, 4.0, 0.30)]),
        clip(gx(SH, 10042), 0.1, 42.0, focus=0.5, **C, titles=[pop("Shayari, part 2", 0.3, 2.8, 0.30)]),
        clip(gx(SH, 10042), 42.9, 44.0, speed=0.2, focus=0.5, audio=(gx(SH, 10042), 42.0), fade_out=0.6, **C),
    ]},
]

if __name__ == "__main__":
    assemble("trip_youtube", 1920, 1080, yt)
    for name, chapters in [("reel_travel", reel_travel), ("reel_juhu", reel_juhu), ("reel_ethglobal", reel_eth),
                           ("reel_jio", reel_jio), ("reel_guesthouse", reel_guesthouse),
                           ("reel_marinedrive", reel_marine), ("reel_shayari", reel_shayari)]:
        assemble(name, 1080, 1920, chapters)
