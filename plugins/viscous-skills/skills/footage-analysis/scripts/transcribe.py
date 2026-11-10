"""Transcribe every wav in edit/audio with faster-whisper, writing word-timed JSON + readable TXT."""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

root = Path(__file__).resolve().parents[1]
# usage: transcribe.py [model] [language|auto] [out_subdir]
model_name = sys.argv[1] if len(sys.argv) > 1 else "large-v3-turbo"
language = None if len(sys.argv) < 3 or sys.argv[2] == "auto" else sys.argv[2]
audio_dir, out_dir = root / "audio", root / (sys.argv[3] if len(sys.argv) > 3 else "transcripts")
out_dir.mkdir(exist_ok=True)

model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=14)

for wav in sorted(audio_dir.glob("*.wav")):
    out_json = out_dir / f"{wav.stem}.json"
    if out_json.exists():
        continue
    segments, info = model.transcribe(
        str(wav), language=language, task="transcribe", word_timestamps=True, vad_filter=True,
        beam_size=5, condition_on_previous_text=False,
    )
    segs = [
        {
            "start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
            "avg_logprob": round(s.avg_logprob, 3), "no_speech_prob": round(s.no_speech_prob, 3),
            "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)}
                      for w in (s.words or [])],
        }
        for s in segments
    ]
    out_json.write_text(json.dumps({"file": wav.stem, "language": info.language,
                                    "language_prob": round(info.language_probability, 2),
                                    "duration": info.duration, "segments": segs}, ensure_ascii=False, indent=1))
    lines = [f"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text']}" for s in segs]
    (out_dir / f"{wav.stem}.txt").write_text(f"# {wav.stem} lang={info.language} ({info.language_probability:.2f})\n"
                                             + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"{wav.stem}: {info.language} {len(segs)} segs", flush=True)
