"""Build plans/youtube.json and plans/reel.json from the storyboard below (see script.md).

Each chapter is a list of segments; music cues are attached to chapters so their timeline
positions are computed from the real segment durations.
"""
import json
from pathlib import Path

edit = Path(__file__).resolve().parents[1]

CREDIT = "Music: Kevin MacLeod (incompetech.com) · CC BY 4.0"
EDITOR = "Edited and Produced by Yash Virulkar"


def clip(src, a, b, **kw):
    return {"src": f"{src}_enhanced.mp4" if src.startswith("GX") else f"{src}.mp4", "in": a, "out": b, **kw}


def photo(name, dur=2.2, **kw):
    full = f"{name}_enhanced.png"
    return {"photo": full, "dur": dur, **kw}


def pop(text, start=0.2, end=1.8, y=0.3):
    return {"text": text, "style": "Pop", "start": start, "end": end, "y": y}


def label(text, start=0.3, end=2.6):
    return {"text": text, "style": "Label", "start": start, "end": end}


def rel(subs, origin):
    """Transcript times are absolute in the source clip; captions are relative to the segment in-point."""
    return [[round(s - origin, 2), round(e - origin, 2), t] for s, e, t in subs]


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
    plan = {"name": name, "width": w, "height": h, "fps": 30, "duck": True, "segments": segs, "music": music}
    (edit / "plans" / f"{name}.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    print(f"{name}: {len(segs)} segments, {t:.1f}s")
    return plan


# ---------------------------------------------------------------- YouTube 16:9
yt = [
    {"name": "hook", "music": [{"track": "Fluffing a Duck", "vol": 0.30, "from": 0.0, "fade": 0.8}],
     "segments": [
         clip("GX010288", 93.2, 95.7, vol=0.3, titles=[pop("Aaj ka plan: BILLIYAAN!", 0.15, 2.4, 0.22)]),
         photo("GOPR0309", 2.0, focus=0.6, kenburns="out"),
         clip("GX010285", 32.0, 34.5, rotate=90, fit="crop", vol=0.6),
         clip("GX010290", 39.0, 41.8, vol=0.6),
     ]},
    {"name": "journey", "music": [{"track": "Carefree", "vol": 0.13, "from": 0.0}],
     "segments": [
         clip("GX010274", 0.5, 15.4, fade_in=0.3, stabilize=True, subs=rel([
             [0.75, 2.85, "Toh guys, basically abhi hum jaa rahe hai"],
             [2.85, 4.49, "cat cafe dekhne!"],
             [5.25, 7.87, "Kuch toh cool sa scenario hai wahan par"],
             [7.87, 13.21, "Cats ke saath baith ke apni dishes kha sakte hai"],
             [13.21, 15.30, "Toh dekhte hai cafe kaisa hai"],
         ], 0.5), titles=[label("Yash", 0.4, 2.8)]),
         clip("GX010274", 15.4, 24.0, stabilize=True, subs=rel([
             [15.41, 17.77, "Humein perfumes nahi lagane chahiye the"],
             [17.77, 19.67, "kyunki maine suna hai ki cats ko..."],
             [20.37, 21.87, "...strong smell pasand nahi"],
             [22.47, 23.63, "Yaar, chalo theek hai"],
         ], 15.4), titles=[label("Div", 0.3, 2.6)]),
     ]},
    {"name": "arrival", "music": [{"track": "Bossa Antigua", "vol": 0.16, "from": 2.0, "fade": 2.0}],
     "segments": [
         clip("GX010275", 0.0, 7.0, fade_in=0.4, titles=[{"text": "Cat Café Studio", "sub": "ANDHERI WEST · MUMBAI",
                                                           "start": 0.5, "end": 6.5}]),
         photo("IMG-20261108-WA0019", 2.4, fit="blur"),
         photo("IMG-20261108-WA0027", 2.0, fit="blur"),
         clip("GX010275", 8.0, 12.5),
         clip("GX010275", 13.0, 17.8, subs=rel([
             [14.77, 16.25, "Bahut galat time pe aaye, abhi so rahi hai"],
             [16.25, 17.55, "Nahi, bahut sahi time hai!"],
         ], 13.0)),
         photo("GOPR0283", 2.0, fit="blur"),
         clip("GX010275", 38.5, 48.0, titles=[pop("Pehla dost!", 0.4, 2.2, 0.2), label("Takishi", 6.0, 9.0)],
              subs=rel([[40.88, 42.10, "He's very friendly"]], 38.5)),
         clip("GX010275", 50.5, 58.0, subs=rel([
             [51.08, 51.66, "Takishi"], [52.60, 54.70, "Is it a Japanese name?"]], 50.5)),
         clip("GX010275", 67.5, 78.8, subs=rel([
             [68.44, 72.60, "He likes taking the attention of girls"],
             [72.86, 74.22, "Oh, really?"]], 67.5)),
         clip("GX010275", 88.8, 95.5, fade_out=0.3, subs=rel([
             [89.66, 91.86, "He's killing me!"]], 88.8)),
         clip("GX010277", 0.0, 3.2, vol=0.4),
         clip("GX010277", 9.6, 13.0, vol=0.4),
         clip("GX010276", 10.5, 13.3, rotate=90, vol=0.4),
         clip("GX010285", 0.0, 8.5, titles=[pop("Welcome committee!", 2.5, 5.0, 0.2)]),
         clip("GX010285", 32.0, 42.0, rotate=90, fit="crop"),
     ]},
    {"name": "catroom", "music": [{"track": "Carefree", "vol": 0.14, "from": 40.0, "fade": 1.5}],
     "segments": [
         clip("GX010288", 13.0, 25.0, titles=[{"text": "The Cat Room", "start": 0.2, "end": 2.0}], subs=rel([
             [13.04, 15.0, "Kaisa laga cat cafe?"], [15.04, 17.0, "Bahut chill hai!"],
             [19.04, 21.0, "Kaisa laga cat cafe?"], [21.04, 23.0, "Bahut hi cute hai!"],
             [23.04, 25.0, "Aur ye billi dekho, kitni cute hai ye"]], 13.0)),
         clip("GX010288", 42.0, 50.0, vol=0.5),
         clip("GX010288", 63.0, 69.0, vol=0.5),
         clip("GX010290", 0.0, 11.5, subs=rel([
             [0.76, 2.58, "Bhai saab, ye kitni pyaari hai!"], [2.58, 4.52, "Look at this"],
             [4.52, 8.68, "She's the queen cat"], [8.68, 11.46, "Kitne aesthetic tarike se so rahi hai"]], 0.0)),
     ]},
    {"name": "montage", "music": [{"track": "Fluffing a Duck", "vol": 0.32, "from": 4.0, "fade": 1.5}],
     "segments": [
         clip("GX010288", 93.4, 97.4, vol=0.4),
         clip("GX010291", 1.5, 7.5, vol=0.4, titles=[pop("Cone of shame", 0.5, 2.5, 0.2)]),
         clip("GX010288", 85.0, 90.5, vol=0.4),
         clip("GX010288", 71.0, 75.0, vol=0.4),
         photo("GOPR0292", 1.8),
         clip("GX010289", 1.0, 7.0, vol=0.4, titles=[pop("Belly rubs!", 0.4, 2.4, 0.2)]),
         clip("GX010289", 45.0, 51.0, vol=0.5, subs=rel([[47.74, 48.9, "Ye blind hai"]], 45.0)),
         photo("GOPR0294", 1.8),
         clip("GX010289", 64.0, 71.0, vol=0.4),
         clip("GX010290", 35.0, 44.0, vol=0.6),
         photo("GOPR0301", 1.8),
         photo("IMG-20261108-WA0045", 1.8, fit="blur"),
     ]},
    {"name": "div_orange", "music": [{"track": "Carefree", "vol": 0.12, "from": 70.0}],
     "segments": [
         clip("GX010308", 0.0, 13.8, titles=[label("Sheena", 5.4, 8.4)], subs=rel([
             [1.89, 4.31, "It's very casual, so it's rather comfortable over here"],
             [4.71, 6.17, "Sheena wants to sleep..."],
             [6.45, 8.53, "...and she wants me to keep petting her"],
             [9.65, 10.23, "You see?"]], 0.0)),
         photo("GOPR0307", 2.2),
     ]},
    {"name": "adoption", "music": [{"track": "Carefree", "vol": 0.32, "from": 86.0, "fade": 2.0, "extra": 22.1}],
     "segments": [
         photo("GOPR0309", 3.5, focus=0.6),
         clip("GX010289", 126.5, 136.5, rotate=-90, fit="crop", vol=0.6),
         photo("GOPR0316", 4.0, fit="blur", titles=[pop("Yahan ki cats adopt bhi kar sakte ho!", 0.4, 3.8, 0.2)]),
     ]},
    {"name": "wrap",  # music continues from the adoption cue
     "segments": [
         clip("GX010288", 0.0, 4.5, vol=0.3),
         clip("GX010319", 0.2, 8.5, vol=0.7, subs=rel([[0.46, 2.2, "Bye bye!"]], 0.2)),
         clip("GX010319", 12.0, 17.0, vol=0.5),
         photo("IMG-20261108-WA0054", 2.6, titles=[pop("Aur haan, pizza bhi mast tha!", 0.2, 2.5, 0.25)]),
         photo("GOPR0296", 5.0, titles=[{"text": "Thanks for watching!", "sub": EDITOR, "credits": [CREDIT],
                                          "start": 0.3, "end": 4.8}]),
     ]},
]

# ---------------------------------------------------------------- Reel 9:16 (cuts on Carefree beats)
B = 60 / 95.7  # one beat in seconds
R = lambda n: round(n * B, 3)  # n beats
reel = [
    {"name": "reel", "music": [{"track": "Carefree", "vol": 0.42, "from": 0.0, "fade": 1.0}],
     "segments": [
         clip("GX010288", 93.2, 93.2 + R(4), fit="crop", vol=0.2, titles=[pop("POV: Mumbai ka cat café", 0.1, R(4), 0.18)]),
         clip("GX010274", 0.6, 4.6, fit="crop", focus=0.4, subs=[[0.15, 2.25, "Toh guys, basically hum jaa rahe hai"],
                                                                 [2.25, 3.9, "cat cafe dekhne!"]]),
         clip("GX010275", 8.2, 8.2 + R(3), fit="crop", focus=0.35, vol=0.3),
         photo("IMG-20261108-WA0019", R(3), focus=0.5),
         clip("GX010275", 60.0, 60.0 + R(4), fit="crop", focus=0.5, vol=0.4, titles=[label("Takishi", 0.2, R(4))]),
         clip("GX010285", 35.5, 35.5 + R(4), rotate=90, fit="crop", focus=0.35, vol=0.6),
         clip("GX010288", 20.0, 20.0 + R(5), fit="crop", vol=0.7, subs=[[1.0, 3.0, "Bahut hi cute hai!"]]),
         clip("GX010288", 44.0, 44.0 + R(4), fit="crop", vol=0.3),
         clip("GX010288", 63.5, 63.5 + R(4), fit="crop", vol=0.3),
         clip("GX010288", 86.0, 86.0 + R(4), fit="crop", vol=0.3),
         clip("GX010289", 2.0, 2.0 + R(4), fit="crop", vol=0.3),
         clip("GX010289", 65.0, 65.0 + R(4), fit="crop", vol=0.3),
         clip("GX010290", 2.0, 2.0 + R(4), fit="crop", focus=0.45, vol=0.2, titles=[pop("the queen", 0.3, R(4), 0.2)]),
         clip("GX010308", 5.9, 9.0, fit="crop", focus=0.45, titles=[label("Sheena", 0.1, 2.6)], subs=[[0.55, 2.7, "she wants me to keep petting her"]]),
         photo("GOPR0309", R(4), focus=0.62),
         clip("GX010290", 42.5, 42.5 + R(4), fit="crop", focus=0.8, vol=0.5),
         photo("GOPR0316", R(4), focus=0.5, titles=[pop("Sab adopt kar sakte ho!", 0.2, R(4), 0.18)]),
         clip("GX010319", 5.2, 5.2 + R(4), fit="crop", focus=0.42, vol=0.3),
         clip("GX010319", 12.5, 12.5 + R(5), fit="crop", focus=0.55, fade_out=0.4, vol=0.3,
              titles=[{"text": "Cat Café Studio", "sub": "ANDHERI WEST · MUMBAI", "credits": [EDITOR],
                      "start": 0.2, "end": R(5)}]),
     ]},
]

if __name__ == "__main__":
    (edit / "plans").mkdir(exist_ok=True)
    assemble("youtube", 1920, 1080, yt)
    assemble("reel", 1080, 1920, reel)
