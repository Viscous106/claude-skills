"""Tempo, duration, energy curve and beat times for each track in edit/music -> music/beats.json."""
import json
from pathlib import Path

import librosa
import numpy as np

music = Path(__file__).resolve().parents[1] / "music"
out = {}
for mp3 in sorted(music.glob("*.mp3")):
    y, sr = librosa.load(str(mp3), sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    bt = librosa.frames_to_time(beats, sr=sr)
    rms = librosa.feature.rms(y=y, hop_length=sr)[0]  # ~1 value per second
    out[mp3.name] = {
        "duration": round(len(y) / sr, 1),
        "bpm": round(float(np.atleast_1d(tempo)[0]), 1),
        "beats": [round(float(t), 2) for t in bt],
        "energy_per_s": [round(float(v), 3) for v in rms],
    }
    e = np.array(out[mp3.name]["energy_per_s"])
    print(f"{mp3.name:36s} {out[mp3.name]['duration']:6.1f}s {out[mp3.name]['bpm']:6.1f} bpm  "
          f"energy mean {e.mean():.3f} (quiet<{np.percentile(e, 20):.3f})")
(music / "beats.json").write_text(json.dumps(out))
