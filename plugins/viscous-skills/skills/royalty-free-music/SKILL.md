---
name: royalty-free-music
description: Use when a video, vlog, Reel or Short needs background music the user is allowed to publish — finding free/CC tracks, downloading them, matching mood and tempo to the edit, and writing the attribution text. Part of the vlog-maker playbook.
---

# Royalty-free music for video

## Sources that download with plain HTTP (no login, no bot checks)

| Source | Licence | Download | Credit needed |
|---|---|---|---|
| incompetech.com (Kevin MacLeod) | CC BY 4.0 | `https://incompetech.com/music/royalty-free/mp3-royaltyfree/<Title>.mp3` (URL-encode the title) | **Yes**, in the description |
| freepd.com | CC0 / public domain | site pages | No (nice to add) |
| YouTube Audio Library | YT-only licence | manual, needs the user's YouTube login | depends on track |
| Pixabay Music | Pixabay licence | needs a browser session | No |

Do not spoof user-agents or scrape around bot checks; if a site refuses plain `curl`, pick
another source or ask the user to download the track into `edit/music/`.
Instagram Reels: tracks added inside the Instagram app are licensed by Instagram; an
uploaded CC BY track is fine but put the credit in the caption.

## Picking tracks

Known-good incompetech tracks for light, cute, day-out vlogs:
- **Carefree** (~96 bpm, ukulele, sunny) — intros, travel, endings, Reels.
- **Fluffing a Duck** (~81 bpm, comedic bassoon) — funny animal chaos, fails.
- **Sneaky Snitch** (~86 bpm, pizzicato) — sneaking, cats stalking, "plot" moments.
- **Bossa Antigua** (~144 bpm feel, lounge bossa) — café / restaurant ambience under talk.
- **Life of Riley** (~103 bpm, cheerful) — upbeat montages.
- **Wallpaper** (~92 bpm, chill groove) — calm b-roll, loud: keep volume low.
- Overused, avoid unless asked: Monkeys Spinning Monkeys, Sneaky Snitch on every video.

Run `scripts/music_beats.py` (from `footage-analysis` env; it lives with the vlog project
scripts) → `music/beats.json` with bpm, beat times and a per-second energy curve. Cut
Reels on beats (every 2 or 4 beats), start music at a phrase start (a beat where energy
rises), and end on a beat or with a 1.5–2 s fade.

## Levels

- Under dialogue: −24 to −20 dB below speech; in `render.py` that is `vol` 0.12–0.2
  with `duck: true` (sidechain compression dips it further while people talk).
- Music-only stretches (no dialogue): `vol` 0.3–0.45.
- Final mix is loudness-normalised to −14 LUFS (YouTube/Instagram reference).

## Attribution text (CC BY, incompetech)

```
"<Title>" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/
```
Put one block per track in the YouTube description and Reel caption, and in the
end card credits if there is one.
