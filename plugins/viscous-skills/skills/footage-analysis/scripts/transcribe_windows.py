"""Transcribe specific windows: transcribe_windows.py LANG CLIP:START-END ... (fast path, no temperature fallback)."""
import sys

import librosa
from faster_whisper import WhisperModel
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lang = sys.argv[1]
import os
model = WhisperModel(os.environ.get("MODEL", "large-v3"), device="cpu", compute_type="int8", cpu_threads=14)
for spec in sys.argv[2:]:
    clip, span = spec.split(":")
    a, b = map(float, span.split("-"))
    y, _ = librosa.load(str(root / "audio" / f"{clip}.wav"), sr=16000, offset=a, duration=b - a)
    segs, _ = model.transcribe(y, language=lang, beam_size=5, temperature=0.0, vad_filter=True,
                               condition_on_previous_text=False)
    print(f"## {clip} {a}-{b}", flush=True)
    for s in segs:
        print(f"[{s.start + a:7.2f}-{s.end + a:7.2f}] lp={s.avg_logprob:5.2f} {s.text.strip()}", flush=True)
