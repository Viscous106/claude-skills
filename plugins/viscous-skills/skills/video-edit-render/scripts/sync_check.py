"""Measure audio/picture sync of a render: where does a segment's own sound sit in the final audio?

usage: sync_check.py PLAN.json RENDER.mp4 [N]   (VLOG_FOOTAGE = footage root)
Picks N dialogue segments spread over the timeline, cross-correlates the source clip's audio with the render's
audio around the segment's timeline position and prints the lag (+ = sound late). In sync = |lag| < 0.04 s.
Both are high-passed at 80 Hz like the render; without that, engine/bus rumble swamps the match and fakes lags.
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import fftconvolve

SR = 4000
R = 4.0  # search room either side, seconds


def pcm(path, start, dur):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{max(start, 0):.3f}", "-t", f"{dur:.3f}",
                          "-i", path, "-map", "0:a:0", "-af", "highpass=f=80", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64)
    return x - x.mean() if len(x) else x


def main():
    plan, render = json.load(open(sys.argv[1])), sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    root = os.environ.get("VLOG_FOOTAGE", ".")
    t, cands = 0.0, []
    for s in plan["segments"]:
        d = s.get("dur", 2.5) if "photo" in s else (s["out"] - s["in"]) / s.get("speed", 1.0)
        d = round(d * plan.get("fps", 30)) / plan.get("fps", 30)  # render.py rounds every segment to whole frames
        if "src" in s and "audio" not in s and s.get("speed", 1.0) == 1.0 and s.get("vol", 1.0) >= 0.8 and d >= 3:
            cands.append((t, s, d))
        t += d
    if not cands:
        sys.exit("no segment with its own sound and >= 3 s long to measure")
    picks = [cands[round(i)] for i in np.linspace(0, len(cands) - 1, min(n, len(cands)))]
    for t0, s, d in picks:
        w = min(d - 1.0, 8.0)
        ref = pcm(os.path.join(root, s["src"]), s["in"] + 0.5, w)          # the clip's own sound
        st = max(t0 + 0.5 - R, 0.0)
        got = pcm(render, st, w + 2 * R)                                   # render, +-R s search room
        if len(ref) < SR or len(got) < len(ref):
            continue
        c = fftconvolve(got, ref[::-1], mode="valid")                       # cross-correlation via FFT
        norm = np.sqrt(fftconvolve(got ** 2, np.ones(len(ref)), mode="valid").clip(0) * (ref ** 2).sum()) + 1e-9
        k = int(np.argmax(c / norm))
        print(f"{t0:8.1f}s  {s['src'][-28:]:28}  lag {k / SR - (t0 + 0.5 - st):+.3f}s  (match {c[k] / norm[k]:.2f})")


main()
