---
name: footage-analysis
description: Use when you need to understand a folder of raw video/photos before editing — probing files, extracting and transcribing audio (Whisper, including Hinglish/Hindi-English speech), making timestamped contact sheets, finding steady/sharp stretches, or spotting sideways and duplicate clips. Part of the vlog-maker playbook.
---

# Footage analysis

Everything runs from an `edit/` folder inside the footage folder. Copy this skill's
`scripts/` there as `edit/scripts/`, and `env.nix` + `run` as `edit/env.nix`, `edit/run`.

```
<footage>/            raw clips + photos (never modified)
<footage>/edit/
  env.nix, run        tool environment (ffmpeg-full, faster-whisper, opencv, librosa, scenedetect)
  scripts/            these scripts
  audio/              16 kHz mono wav per clip
  transcripts*/       <clip>.json (segments + word timings) and <clip>.txt
  frames/             contact sheets
  analysis/           per-0.5 s quality CSVs + summary.json
```

## Tool environment (NixOS)

`./run <cmd>` enters a `nix shell` built from `env.nix`. Two gotchas it handles:
- the host `LD_LIBRARY_PATH` (pipewire/alsa) points at a newer glibc than nixpkgs'
  ffmpeg → "GLIBC_2.43 not found"; `run` unsets it.
- the path contains spaces, so `env.nix` is imported as `(/. + "<abs path>")`.
nix needs the daemon socket and `~/.cache/nix`, so these commands must run outside the
Bash sandbox. On non-Nix systems: `pip install faster-whisper opencv-python librosa`
plus a system ffmpeg built with libass, libvidstab and fontconfig.

## Steps

1. **Probe**: `ffprobe -show_entries format=duration:stream=codec_type,width,height,r_frame_rate`
   for every clip. Note mixed aspect ratios (GoPro 1920×1080 vs 608×1080 vertical
   crops vs phone 480×854) and identical durations (likely duplicate forwards).
2. **Audio**: `ffmpeg -i clip -map 0:a:0 -ac 1 -ar 16000 edit/audio/<clip>.wav`.
3. **Transcribe** (background, it is slow on CPU — ~1× real time for large-v3 int8):
   `./run python3 scripts/transcribe.py <model> <language|auto> <out_subdir>`
   - English-only footage: `large-v3-turbo auto transcripts`.
   - **Hinglish**: auto-detect calls it English and turbo *translates* Hindi words into
     English ("Is he washed?"). Run `large-v3 hi transcripts_hi` (full model; turbo is
     weak at Hindi) to get what was actually said in Devanagari + English, then
     romanise it yourself into Hinglish ("Toh guys, hum cat cafe ja rahe hai").
     Keep the English pass too — it tells you the meaning, the Hindi pass the words.
   - Discard segments with `no_speech_prob > 0.6`, `avg_logprob < -1.0`, or the same
     short line repeated 3+ times in a row (hallucination on background noise). Hindi mode
     on noisy audio also invents "सब्सक्राइब सब्सक्राइब" and "बहुत बहुत बहुत…" — drop those.
   - **Speed**: the full-file pass with default temperature fallback can crawl (~0.05× real
     time on noisy café audio: every chunk is re-decoded up to 6 times). Once you know which
     moments the edit uses, run `scripts/transcribe_windows.py hi CLIP:START-END …`
     instead — temperature 0, no word timings, only the windows you need; minutes, not hours.
   - When someone speaks English in a Hinglish vlog, the Hindi pass garbles it; take that
     line from the English pass. Pick per line, not per file.
   - The large-v3 download (3.1 GB) can stall silently: if the `.incomplete` blob stops
     growing, kill the process, delete stale `.incomplete`/`.locks`, and re-run
     `huggingface_hub.snapshot_download("Systran/faster-whisper-large-v3")` — it resumes.
   - Never caption a line you could not verify; list doubtful lines for the user to confirm.
4. **Look**: `./run scripts/contact_sheets.sh` (24 timestamped frames per clip) and
   `./run python3 scripts/photo_sheet.py out.jpg <photos…>` (labelled photo grid;
   ffmpeg's tile filter breaks on photos of mixed sizes, so use this). Read every sheet.
   Record sideways clips (`rotate`), the subject of each shot, and the best moments.
   For long clips also run `scripts/dense_sheet.sh CLIP STEP COLS HEIGHT` (one frame every
   2–3 s) to pick exact in/out points. When the camera was held sideways for part of a
   clip, extract a few frames of that stretch with `transpose=1` and read them: if text or
   a logo reads upside down, that stretch needs `rotate: -90` instead of `90`. The
   direction can differ between stretches of the same clip.
   Inline `drawtext=text='%{pts\:hms}'` breaks inside `bash -c '…'` quoting — use the
   script files, which quote it correctly.
5. **Score**: `./run python3 scripts/analyze_shots.py` → per-0.5 s `sharp` (Laplacian
   variance), `motion` (mean frame diff), `bright`, `db` (loudness) and per-clip
   `steady_stretches` (≥2 s sharp and calm, relative to that clip). Use it to pick in/out
   points; whip-pans and blur show as motion spikes and sharpness dips.

6. **Music**: `./run python3 scripts/music_beats.py` → `music/beats.json` (bpm, beat
   times, energy per second) for every track in `edit/music/` — see `royalty-free-music`.

## Many folders at once (a whole trip)

Keep one work dir for the trip and name every derived file `<Folder>__<stem>` (spaces →
`_`) so clips with the same GoPro number in different folders don't collide:
- `scripts/probe_all.sh <root> > probe.tsv` — every clip: folder, path, duration, size,
  rotation tag, has-audio, creation time. Empty fields are written as `-` because bash
  `read` with a tab IFS collapses consecutive tabs and shifts the columns.
- `scripts/extract_audio.sh` and `scripts/sheets_all.sh` work from `probe.tsv`;
  `scripts/photo_sheets_all.sh` makes 36-photo grids per folder (subfolders labelled).
- Contact sheets: ffmpeg's `tile` only emits a *full* grid — a clip shorter than
  24 × step gives no image at all, so step = dur/24.5; `-skip_frame nokey` only for
  clips over a minute; end the chain with `format=yuvj420p` (WhatsApp clips are
  limited-range and mjpeg refuses them).
- GoPro file numbers are not chronological across cameras/days — order by content and
  ask the user for the story order early.
- Logging 150 clips: hand each folder group to a parallel subagent with the people key
  and the story order, and have each write `logs/<group>.md` (clip | orientation | who |
  moments with timestamps | problems | usability | quotes) plus a Reel shot list. Read
  the logs, not the sheets, to write the script; spot-check the claims that matter
  (rotation direction, who's who) with single frames.
- Hinglish windows on CPU: `large-v3` crawled at ~0.05× real time with other load;
  `MODEL=large-v3-turbo scripts/transcribe_windows.py hi …` is ~10× faster. Turbo in
  Hindi mode loops (`कर दो कर दो…`) on noisy stretches — take the words from it where
  it's clean and the timings/meaning from the English pass.

Process hygiene: never `pkill -f <pattern>` in the same shell command whose own text
contains the pattern — it kills your own shell (exit 144). Kill by PID from `pgrep -a`.

Output of this phase is a footage log (clip, in/out, what's seen, what's said, quality)
that the script is written from — see `vlog-maker`.
