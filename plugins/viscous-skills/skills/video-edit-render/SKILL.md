---
name: video-edit-render
description: Use when you need to actually cut and render a video from an edit plan with ffmpeg — trimming clips, mixing 16:9 and 9:16 sources, rotating sideways footage, stabilising, Ken Burns on photos, burning captions/title cards, ducking music under dialogue, loudness normalising, and exporting YouTube and Reel versions with and without captions. Part of the vlog-maker playbook.
---

# Edit plan → rendered video

`scripts/render.py` (copy to `<footage>/edit/scripts/`, run inside the `footage-analysis`
tool env with `./run python3 scripts/render.py …`).

```
render.py plans/youtube.json [--subs on|off] [--titles on|off] [--draft] [--jobs N] [--out NAME]
```
Writes `edit/renders/<name>[_nocaptions][_draft].mp4`. Per-segment intermediates are
cached in `edit/build/` by a hash of the segment's *picture and sound* + output size
(`subs`/`titles` are excluded — they are burned in at the final pass), so caption and
title edits never re-encode segments. `--draft` = ultrafast encode, no stabilisation: use
it for every iteration, final render only at the end. `--jobs 4` renders segments in
parallel (a 120-segment trip vlog drafts in a few minutes instead of half an hour).

Footage spread over several folders (a whole trip): set `VLOG_FOOTAGE=<root>` and give
`src`/`photo` paths relative to it (`"Juhu Beach/GX010073_enhanced.mp4"`). An absolute
`photo` path also works — use it for generated graphics kept in the work dir.

## Plan format

```json
{
  "name": "youtube", "width": 1920, "height": 1080, "fps": 30, "duck": true,
  "segments": [
    {"src": "GX010274.mp4", "in": 0.5, "out": 4.0,
     "rotate": 0, "fit": "blur", "focus": 0.5, "zoom": 1.0, "speed": 1.0,
     "stabilize": false, "vol": 1.0, "fade_in": 0, "fade_out": 0,
     "grade": "eq=saturation=1.08:contrast=1.03",
     "subs": [[0.2, 2.1, "Toh guys, hum cat cafe ja rahe hai!"]],
     "titles": [{"text": "Cat Café Studio", "sub": "ANDHERI WEST · MUMBAI", "start": 0.3, "end": 3},
                {"text": "Yash", "style": "Label", "start": 0.3, "end": 2.5},
                {"text": "SO CUTE!!", "style": "Pop", "y": 0.3, "start": 0.2, "end": 1.6}]},
    {"photo": "GOPR0309.png", "dur": 2.5, "kenburns": "in", "focus": 0.6},
    {"photo": "end.png", "dur": 5, "titles": [{"text": "Thanks for watching!", "sub": "Edited and Produced by …",
                                               "credits": ["Music: … · CC BY 4.0"], "start": 0.3, "end": 4.8}]}
  ],
  "music": [{"src": "music/Carefree.mp3", "at": 0, "from": 0, "dur": 30, "vol": 0.22, "fade": 1.5}]
}
```
- Times in `subs`/`titles` are relative to the segment start; `music.at` is absolute
  timeline time, `from` is the offset into the track.
- `fit`: `blur` = foreground fitted over a blurred fill (vertical clip in 16:9 or vice
  versa), `crop` = fill the frame, `focus` 0..1 picks the horizontal crop centre (aim at
  the face/cat), `pad` = black bars.
- `rotate`: 90 / -90 / 180 for GoPro clips shot sideways (check the contact sheet).
- `speed` ≠ 1 mutes clip audio unless `keep_audio_on_speed`.
- `audio: {"src", "in", "vol"?}` plays another clip's sound under this picture — a VO line
  whose own picture is a finger/blur/extreme close-up goes over b-roll this way. Captions
  must then come from the audio clip (the example builder handles it).
- `mute: [[a, b], …]` silences segment-relative ranges (bleep a swear word; show
  `[beep]` in the caption).
- `tilt: deg` straightens a crooked horizon (rotates, then crops the corners away).
- Any `Label`/`Pop` can take `pos: [x, y]` (fractions of the frame, centred) — for a
  "meet the team" group photo put one label on each person's chest or above the head,
  staggered so neighbours don't overlap, and check the frame.
- Title styles: `Title` (Pacifico, centred, with optional `sub` line), `Label` (name
  tag, bottom-left / top in vertical), `Pop` (yellow punchy reaction text), `Sub`
  (dialogue captions, Baloo 2 — has Devanagari and Latin, good for Hinglish). A `Title`
  can carry `sub` (one line) and `credits` (list of smaller lines) for end cards.
  Fonts live in `edit/fonts/` (Google Fonts OFL: Baloo 2, Poppins, Pacifico) and are
  passed to libass via `fontsdir`.

## What the final pass does

1. concat the cached segments (all are re-encoded to identical codec/fps/size/48 kHz
   stereo, so the concat demuxer with `-c copy` is safe);
2. **audio-only pass → wav**: music tracks are trimmed, faded, delayed to `at`, mixed,
   padded to the exact timeline length, ducked with `sidechaincompress` keyed on the
   dialogue bed, then two-pass `loudnorm` to −14 LUFS / −1.5 dBTP. Cached by a hash of the
   graph, so the captions/no-captions renders share it;
3. **video pass**: burn the generated `.ass` (subs on/off, titles on/off), mux the wav,
   x264 CRF 18 `-preset slow`, `+faststart`.

Two deadlocks this design avoids (both looked like ffmpeg "hanging" at ~15 % CPU with a
partial output file that never grows):
- music bed shorter than the dialogue → `sidechaincompress` stops reading its key input,
  `asplit`'s buffer fills, the graph stalls. Fix: `apad=whole_dur=T,atrim=0:T` on the bed.
- 8 audio inputs + the video in one filter graph → interleaving stall at the muxer. Fix:
  render the audio mix separately, then mux.
If a render hangs, run with `VLOG_DEBUG=1` to print every ffmpeg command and re-run the
stuck one by hand with `-stats` to see the timestamp where it stops.

Timing: a 4.5-min 1080p draft takes ~1 min on 16 cores; finals take several minutes each.
Don't run renders while a Whisper job is using every core.

## QA — always look at the result

- Long cuts: `scripts/qc_parts.sh renders/x.mp4 300 4 10 8 108 frames/qc` → one grid per
  5 minutes (a single grid of a 15-min vlog is too small to read).
  Typical trip-vlog misses: white title over a white screenshot (unreadable), a pop text
  sitting on the wrong part of a graphic (make a custom highlight graphic instead),
  a vertical Label colliding with a Pop at the top of a Reel (Pop y ≥ 0.28 there),
  an ending on an extreme close-up (move its audio onto b-roll).
- `scripts/qc_sheet.sh renders/x.mp4 6 6 200 frames/qc.jpg` (YouTube: a frame every 6 s)
  or `… 2 13 300 …` (Reel: every 2 s) → one timestamped grid of the whole render. Read it: caption size/placement, crop focus on faces, rotation, title
  legibility, nothing covered by the Reel UI (keep text out of the bottom ~20 % and the
  right edge in 9:16). Typical misses found this way: a hook whose in-point is half a
  second before the hero subject appears; a rotated stretch that came out upside down;
  9:16 crops of 16:9 shots where `focus` lands on a wall instead of the person/cat —
  re-pick the moment rather than fight the crop when the subject sits low or at an edge.
- Re-check the specific fixed spots afterwards with single frames (`-ss T -frames:v 1`).
- `ffmpeg -i out.mp4 -af ebur128 -f null -` → integrated loudness ≈ −14 LUFS.
- `python3 scripts/peaks.py out.mp4 …` → max sample peak and the seconds above −1 dBFS,
  measured on the **decoded mp4**, not the wav. A loud music hit squashed against the
  loudnorm ceiling becomes a near-square wave, and AAC encoding then overshoots it by
  3–4 dB (we saw +2.2 dBFS from a −1.5 dBFS wav). Fix it with gain staging: lower that
  music cue's `vol`, and keep `TP=-2.0` in loudnorm. A limiter alone won't do it.
- `ffprobe` duration ≈ the plan's sum of segment durations.
- Reel ≤ 60 s (or the user's limit); YouTube within the agreed range.

## ffmpeg gotchas met

- ASS font sizes read small: ≈9 % of height for 16:9 captions, ≈6 % for 9:16;
  set `ScaledBorderAndShadow: yes`.
- Paths with spaces/colons inside `subtitles=` must be escaped (`:` → `\:`, quote).
- Photos of mixed sizes break `tile`/glob inputs; normalise each with scale+crop first.
- `vidstabdetect` needs its own pass; write the `.trf` per segment.
- Phone clips may be HEVC at 30 fps vs GoPro 29.97 — always pass `fps=` in the chain.
