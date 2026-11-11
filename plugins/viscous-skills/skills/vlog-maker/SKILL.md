---
name: vlog-maker
description: Use when the user wants a vlog, travel/day-out video, YouTube video, Instagram Reel or Short made from their own raw footage (GoPro/phone clips, photos, existing audio) — analysing what was shot, writing the script and edit plan, choosing music, and rendering the final cuts. Master playbook; loads footage-analysis, video-edit-render and royalty-free-music as needed.
---

# Vlog maker playbook

Turn a folder of raw clips and photos into a finished vlog (YouTube 16:9) and a short
(Reel/Short 9:16), with real dialogue, captions, music and title cards — all rendered
locally with ffmpeg, no GUI editor.

Sibling skills, load when you reach that phase:
- `footage-analysis` — tool env, probing, audio extraction, Whisper transcription (incl.
  Hinglish), contact sheets, shot-quality scores.
- `video-edit-render` — the JSON edit-plan format and `render.py` (aspect fitting, rotation,
  stabilisation, captions, music ducking, loudness), plus frame-level QA.
- `royalty-free-music` — finding tracks the user is allowed to use and crediting them.

## Workflow

1. **Ingest and look** (`footage-analysis`). Probe every file, extract audio, start
   transcription in the background, make a contact sheet per clip and a sheet of the
   photos, and actually look at every one. Write down per clip: what happens, who is
   in it, orientation problems (sideways clips), shaky/blurry stretches, duplicates.
2. **Ask only what changes the edit** — in one round, as soon as you have looked:
   - platform(s) and length per cut (YouTube 3–5 min / Reel ≤60 s is a common pair, but ask:
     a trip vlog can run 30 min and Reels up to 3 min, and a 60 s Reel of a dialogue-heavy
     place feels rushed);
   - narration: real dialogue only, real lines re-used over b-roll, user-recorded VO,
     or AI VO — and what to do with silent stretches (music is the usual answer);
   - language of the dialogue (Hinglish? → see `footage-analysis` for transcription);
   - names for on-screen labels (ask which person is who; never guess from looks);
   - captioned, clean, or both (render both if unsure — it is a flag, not a re-edit);
   - music: user-supplied vs. you source free tracks.
3. **Footage log** → `edit/footage_log.md`: one row per usable moment with clip, in/out,
   what's seen, what's said (from the transcript), quality score. This is the raw
   material the script is written from.
4. **Story + script** → `edit/script.md`. Structure that works for a day-out vlog:
   - **Hook (0–8 s):** the single best moment (cat on shoulder, the reaction laugh),
     then a title card. Never open on the commute.
   - **Journey (short):** getting there, 1–3 real lines ("so guys, we're going to…").
   - **Arrival / place reveal:** wide establishing shots, signage, a name+place title.
   - **Main chapters:** 3–5 beats, each built around one real dialogue moment and
     covered with b-roll; chapter titles only if the video is > 3 min.
   - **Emotional peak:** the moment the user cares most about (ask if unclear).
   - **Wrap:** goodbye line, a "why go" note (e.g. adoption board), end card + credits.
   Reel: hook in the first 1.5 s, one idea, 12–20 cuts of 1.5–3 s on the music beat,
   2–4 dialogue snippets max, text overlays carry the story, loopable last frame.
   Write captions in the speakers' own register (Hinglish in Roman script for a
   Hinglish vlog — not Devanagari, not translated English).
5. **Edit plan** → `edit/plans/<cut>.json` (format in `video-edit-render`). Pick in/out
   points from the steady stretches in `analysis/summary.json` and your own frame checks.
   Cut on action, keep each b-roll shot 1.5–4 s, let real dialogue play uncut.
   Don't hand-write the JSON: write a small `edit/scripts/build_plans.py` with chapters
   (segments + a music cue per chapter) so music `at`/`dur` are computed from real segment
   lengths and captions are given in source-clip time (`rel()` converts). Worked example:
   `examples/build_plans_catcafe.py` (+ `examples/script_catcafe.md`, the matching script).
   Reel beats: `B = 60/bpm`, shot length `n*B` (4 beats ≈ 2.5 s at 96 bpm).
   Fonts: download OFL fonts into `edit/fonts/` from
   `raw.githubusercontent.com/google/fonts/main/ofl/<family>/…` (Baloo 2 for Hinglish
   captions, Poppins for labels/pops, Pacifico for titles).
6. **Draft render** (`--draft`), QC sheet (`qc_sheet.sh`), read it, fix, re-check the
   fixed spots; then final renders: each cut × {captions, no captions}. "No captions"
   = dialogue subtitles off, title cards and pops kept (`--titles off` removes those too).
7. **Deliver**: the renders, the script, credits text for the description (music
   attribution is mandatory for CC BY tracks), and a list of anything that needs the
   user (e.g. a VO line to record).

## Whole-trip vlogs (many folders, many people)

Worked example: `examples/build_plans_mumbai_trip.py` (27-min YouTube cut + 7 place
Reels from 9 folders) with `examples/captions_mumbai_trip.py` and
`examples/captions_en_mumbai_trip.py` (copy them as `captions.py` / `captions_en.py`).
- Ask first: one trip vlog vs. one per place vs. both; the story order; who is who.
  For names, number the faces on one group photo (`who_is_who.jpg`) and ask the user to
  confirm the mapping in a single question — agents' guesses from outfits disagree.
  Self-introductions on camera ("Hi guys, I am Soham") are the best place for labels.
- Structure: hook = the emotional peak as a 9 s teaser (e.g. the scream when the result
  call comes), title card, then chronological chapters, each with its own music cue;
  the peak scene gets the most time and a custom highlight graphic (see
  `examples/make_highlight_card.py`).
- Captions: keep them in one table per source clip (`CAP[path] = [[s, e, text]]`, source
  time); `clip()` picks the lines inside each segment's window, including VO borrowed via
  `audio=`. Trimming then never needs caption edits. Ask early whether captions should be in
  the spoken Hinglish or in English: the Mumbai user switched to English after the first full
  cut. Keep `CAP` as spoken and add an `EN` map (`examples/captions_en_mumbai_trip.py`) that
  `clip()` applies, skipping clips whose lines must stay as said (poetry, songs). Lines nobody can make out stay
  uncaptioned; on-screen Pop text can carry the story there instead.
- Play self-introduction clips whole in the long cut (every member's "Hi guys, I am…" and
  the "stay tuned" sign-off), even with a few shaky seconds — users miss them when trimmed
  to the first speaker, and the name labels belong on those intros.
- Before moving a clip's audio onto b-roll because the log calls its picture weak, look at
  the clip yourself at 2 fps. A log once called a walking clip "path shot, finger in the
  corner" when every member turned to the camera to give their rating; the cut showed only
  the first two, and the user asked for everyone's answer with their face.
- Voice-only clips (camera on a window, speaker off screen): ask whose voice it is. A second
  recitation of the same poem was taken for the on-screen reciter's take and replaced with his
  audio, which hid that a different friend recited it.
- Reels: run the crop audit (`video-edit-render`) before the final render; groups and
  moving selfie faces get `fit: blur` + `zoom`, not `fit: crop`.
- Keep private moments out (sleeping people unless the user OKs it, strangers' faces,
  copyrighted films on a laptop, forwarded trailers) and bleep swearing with `mute`.
- Thumbnail: Polaroid collage of 4–6 moments with the hook in big type
  (`examples/make_thumbnail_collage.py`). Pacifico has no arrow glyph: write "to".
- Deliverables: the renders, description with chapters (timestamps from the builder's
  per-chapter printout), one caption per Reel, thumbnail; music credits for every track.

## Rules learned the hard way

- Transcripts of noisy café/street audio hallucinate repeated lines ("I don't know ×6")
  — treat low-confidence and repeated segments as noise and verify by listening-proxy
  (loudness in `analysis/*.csv`) before captioning them.
- Whisper auto-detects Hinglish as English and silently *translates* it. Transcribe
  with `language="hi"` and romanise yourself.
- Check clip orientation on the contact sheet; GoPro clips filmed sideways need
  `rotate`. Vertical sources in a 16:9 cut get `fit: blur`; landscape sources in a
  9:16 cut usually want `fit: crop` with a `focus` on the subject.
- Duplicated WhatsApp forwards are common — compare durations and frames, drop copies.
- Never invent dialogue in captions. If a line is unclear, leave it uncaptioned or
  ask the user.
- Ask before using anyone's voice for AI cloning; prefer real lines + music.
