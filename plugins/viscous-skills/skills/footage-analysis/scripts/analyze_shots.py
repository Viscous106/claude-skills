"""Per-0.5s shot quality for every clip: sharpness, camera motion, brightness, loudness.

Writes analysis/<clip>.csv and analysis/summary.json listing the steadiest usable stretches
(>=2s where the frame is sharp and the camera is not whipping around).
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import cv2
import librosa
import numpy as np

root = Path(__file__).resolve().parents[1]
src_dir, out_dir = root.parent, root / "analysis"
out_dir.mkdir(exist_ok=True)
STEP = 0.5


def frame_stats(path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    every = max(1, round(fps * STEP))
    prev, rows, i = None, [], 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if i % every == 0:
            _, f = cap.retrieve()
            g = cv2.cvtColor(cv2.resize(f, (320, int(320 * f.shape[0] / f.shape[1]))), cv2.COLOR_BGR2GRAY)
            sharp = cv2.Laplacian(g, cv2.CV_64F).var()
            motion = 0.0 if prev is None else float(np.mean(np.abs(g.astype(np.int16) - prev.astype(np.int16))))
            rows.append({"t": round(i / fps, 2), "sharp": round(sharp, 1), "motion": round(motion, 2),
                         "bright": round(float(g.mean()), 1)})
            prev = g
        i += 1
    return rows


def loudness(path, n):
    wav = root / "audio" / f"{path.stem}.wav"
    y, sr = librosa.load(str(wav), sr=16000)
    hop = int(sr * STEP)
    rms = librosa.feature.rms(y=y, frame_length=hop, hop_length=hop, center=False)[0]
    db = 20 * np.log10(np.maximum(rms, 1e-5))
    return [round(float(db[k]), 1) if k < len(db) else -100.0 for k in range(n)]


summary = {}
clips = sorted(src_dir.glob("*.mp4")) if len(sys.argv) < 2 else [Path(p) for p in sys.argv[1:]]
for clip in clips:
    rows = frame_stats(clip)
    for r, db in zip(rows, loudness(clip, len(rows))):
        r["db"] = db
    with open(out_dir / f"{clip.stem}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["t", "sharp", "motion", "bright", "db"])
        w.writeheader()
        w.writerows(rows)
    sharp = np.array([r["sharp"] for r in rows])
    motion = np.array([r["motion"] for r in rows])
    # "usable" = sharper than this clip's 35th percentile and calmer than its 70th percentile motion
    good = (sharp >= np.percentile(sharp, 35)) & (motion <= np.percentile(motion, 70))
    stretches, start = [], None
    for k, g in enumerate(list(good) + [False]):
        if g and start is None:
            start = k
        elif not g and start is not None:
            if (k - start) * STEP >= 2:
                stretches.append([rows[start]["t"], round(rows[k - 1]["t"] + STEP, 2)])
            start = None
    summary[clip.stem] = {"duration": round(len(rows) * STEP, 1), "median_sharp": float(np.median(sharp)),
                          "median_motion": float(np.median(motion)), "steady_stretches": stretches}
    print(clip.stem, len(stretches), "steady stretches", flush=True)

(out_dir / "summary.json").write_text(json.dumps(summary, indent=1))
