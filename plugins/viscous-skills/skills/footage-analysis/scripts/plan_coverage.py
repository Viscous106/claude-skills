"""Per source clip in a plan: duration, used windows, and transcript speech outside them."""
import json, sys, csv
from pathlib import Path
from collections import OrderedDict
root = Path(__file__).resolve().parents[1]
plan = json.load(open(sys.argv[1]))
dur = {}
for row in csv.reader(open(root / "probe.tsv"), delimiter="\t"):
    dur[row[1]] = float(row[2]) if row[2] != "-" else 0
used = OrderedDict()
chap_of = {}
for i, s in enumerate(plan["segments"]):
    if "src" not in s: continue
    used.setdefault(s["src"], []).append((s["in"], s["out"]))
    if "audio" in s:
        a = s["audio"]; used.setdefault(a["src"] + " [audio]", []).append((a["in"], a["in"] + s["out"] - s["in"]))
for src, wins in used.items():
    clean = src.replace(" [audio]", "")
    stem = clean.replace("/", "__").replace(" ", "_").rsplit(".", 1)[0]
    tj = root / "transcripts_en" / f"{stem}.json"
    segs = []
    if tj.exists():
        d = json.load(open(tj))
        segs = [(x["start"], x["end"], x["text"].strip()) for x in d.get("segments", d if isinstance(d, list) else [])
                if x.get("no_speech_prob", 0) < 0.6 and x.get("avg_logprob", 0) > -1.0]
    out = [(a, b, t) for a, b, t in segs if not any(w0 - 0.3 <= a and b <= w1 + 0.3 for w0, w1 in wins)]
    tot = sum(b - a for a, b, _ in out)
    print(f"\n### {src}  dur={dur.get(clean, '?')}  used={[(round(a,1), round(b,1)) for a,b in wins]}  unused_speech={tot:.0f}s{'' if tj.exists() else '  (no transcript)'}")
    for a, b, t in out:
        print(f"   [{a:6.1f}-{b:6.1f}] {t[:110]}")
