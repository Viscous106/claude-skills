"""Render an edit plan (JSON) into a finished vlog with ffmpeg.

usage: render.py PLAN.json [--subs on|off] [--titles on|off] [--draft] [--out NAME]

Plan format (times in seconds, source paths relative to the footage folder):
{
  "name": "youtube", "width": 1920, "height": 1080, "fps": 30,
  "segments": [
    {"src": "GX010274_enhanced.mp4", "in": 0.5, "out": 4.0,
     "rotate": 0,            # 90 / -90 / 180 to fix sideways footage
     "fit": "blur",          # blur (blurred-fill bars) | crop (fill frame) | pad (black bars)
     "focus": 0.5,           # horizontal crop centre for fit=crop, or for fit=blur with zoom > 1 (0 left .. 1 right)
     "zoom": 1.0,            # extra punch-in; with fit=blur, zoom z shows the middle 1/z of a 16:9 source's width
                             # over the blurred fill (two people side by side / a big selfie face in a Reel)
     "speed": 1.0,           # 2.0 = double speed (audio muted unless keep_audio_on_speed)
     "stabilize": false,     # vid.stab two-pass
     "vol": 1.0,             # clip audio gain; 0 mutes
     "fade_in": 0, "fade_out": 0,
     "subs": [[0.2, 2.1, "Toh guys, hum ja rahe hai cat cafe!"]],   # relative to segment start
     "title": {"text": "Cat Cafe Studio", "sub": "Andheri West, Mumbai", "credits": ["smaller line"],
               "start": 0, "end": 3, "style": "Title"}
    },
    {"photo": "GOPR0309_enhanced.png", "dur": 2.5, "kenburns": "in"}   # still with slow zoom
  ],
  "music": [{"src": "music/Carefree.mp3", "at": 0, "from": 0, "dur": 30, "vol": 0.22, "fade": 1.5}],
  "duck": true               # music dips under dialogue
}
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

edit = Path(__file__).resolve().parents[1]
footage = Path(os.environ.get("VLOG_FOOTAGE", edit.parent))  # source paths resolve against this
work = edit / "build"
fonts = edit / "fonts"


def sh(cmd):
    if os.environ.get("VLOG_DEBUG"):
        print(" ".join(f"'{c}'" if " " in str(c) or ";" in str(c) else str(c) for c in cmd), file=sys.stderr)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-3000:]}")
    return r.stdout


def has_audio(path):
    return bool(sh(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                    "-of", "csv=p=0", str(path)]).strip())


def fit_chain(W, H, fit, zoom, focus):
    """Video filter that turns any input into exactly WxH."""
    if fit == "crop":
        return (f"scale={W}*{zoom}:{H}*{zoom}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H}:(iw-{W})*{focus}:(ih-{H})/2,setsar=1")
    if fit == "pad":
        return (f"scale={W}*{zoom}:{H}*{zoom}:force_original_aspect_ratio=decrease,"
                f"crop='min(iw,{W})':'min(ih,{H})',pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1")
    # blur: sharp foreground over a blurred, darkened copy that fills the frame
    return (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"boxblur=40:5,eq=brightness=-0.08[bg];[b]scale={W}*{zoom}:{H}*{zoom}:force_original_aspect_ratio=decrease,"
            f"crop='min(iw,{W})':'min(ih,{H})':(iw-ow)*{focus}:(ih-oh)/2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1")


def render_segment(i, seg, plan, draft):
    W, H, fps = plan["width"], plan["height"], plan["fps"]
    pic = {k: v for k, v in seg.items() if k not in ("subs", "titles")}  # burned in later, not part of the segment
    dur = seg_duration(seg, fps)
    raw = seg.get("dur", 2.5) if "photo" in seg else (seg["out"] - seg["in"]) / seg.get("speed", 1.0)
    if abs(raw - dur) > 1e-6:  # frame-rounded length: segments cached before the rounding must not be reused
        pic["_frames"] = round(dur * fps)
    key = hashlib.sha1(json.dumps([pic, W, H, fps, draft], sort_keys=True).encode()).hexdigest()[:10]
    out = work / f"{plan['name']}_{i:03d}_{key}.mp4"
    if out.exists():
        return out
    part = out.with_name(out.stem + ".part.mp4")  # renamed when complete: a killed render never leaves a cached half-file
    enc = ["-c:v", "libx264", "-preset", "ultrafast" if draft else "medium", "-crf", "28" if draft else "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

    if "photo" in seg:
        frames = round(dur * fps)
        z = "min(1+0.0009*on,1.15)" if seg.get("kenburns", "in") == "in" else "max(1.15-0.0009*on,1)"
        focus = seg.get("focus", 0.5)
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2}:(iw-{W*2})*{focus}:(ih-{H*2})/2,"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={fps},setsar=1")
        if seg.get("fit") == "blur":
            vf = f"fps={fps}," + fit_chain(W, H, "blur", seg.get("zoom", 1.0), seg.get("focus", 0.5))
        sh(["ffmpeg", "-nostdin", "-y", "-v", "error", "-loop", "1", "-t", str(dur), "-i", str(footage / seg["photo"]),
            "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex", f"[0:v]{vf},fade=t=in:d=0.25,fade=t=out:st={dur-0.25}:d=0.25[v]",
            "-map", "[v]", "-map", "1:a", "-t", str(dur), "-r", str(fps), *enc, str(part)])
        part.replace(out)
        return out

    src = footage / seg["src"]
    t0, t1 = seg["in"], seg["out"]
    speed = seg.get("speed", 1.0)
    pre = []
    rot = seg.get("rotate", 0)
    if rot == 90:
        pre.append("transpose=1")
    elif rot == -90:
        pre.append("transpose=2")
    elif rot == 180:
        pre.append("hflip,vflip")
    if seg.get("tilt"):  # straighten a tilted horizon (degrees, + = clockwise), then crop off the corners
        a = seg["tilt"]
        pre.append(f"rotate={a}*PI/180:ow=iw:oh=ih,scale=iw*1.3:-2,crop=iw/1.3:ih/1.3")
    if seg.get("stabilize") and not draft:
        trf = work / f"{out.stem}.trf"
        sh(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", str(src),
            "-map", "0:v:0", "-vf", ",".join(pre + [f"vidstabdetect=shakiness=8:accuracy=15:result='{trf}'"]),
            "-f", "null", "-"])
        pre.append(f"vidstabtransform=input='{trf}':smoothing=20:zoom=4,unsharp=5:5:0.6")
    if speed != 1.0:
        pre.append(f"setpts=PTS/{speed}")
    grade = seg.get("grade", "eq=saturation=1.08:contrast=1.03")
    chain = ",".join(pre + [grade]) if pre or grade else "null"
    vf = f"[0:v:0]{chain},fps={fps},{fit_chain(W, H, seg.get('fit', 'blur'), seg.get('zoom', 1.0), seg.get('focus', 0.5))}"
    fi, fo = seg.get("fade_in", 0), seg.get("fade_out", 0)
    if fi:
        vf += f",fade=t=in:d={fi}"
    if fo:
        vf += f",fade=t=out:st={dur - fo}:d={fo}"
    vf += ",tpad=stop_mode=clone:stop_duration=1[v]"  # a source that ends early holds its last frame to the full length

    vol = seg.get("vol", 1.0)
    if speed != 1.0 and not seg.get("keep_audio_on_speed"):
        vol = 0
    # "audio": {"src": ..., "in": t} plays another clip's sound under this picture (VO over b-roll)
    alt = seg.get("audio")
    asrc, ain0 = (footage / alt["src"], ["-ss", str(alt["in"]), "-t", str(dur), "-i", str(footage / alt["src"])]) if alt else (src, [])
    if alt:
        vol, speed_a = alt.get("vol", 1.0), 1.0
    else:
        speed_a = speed
    mutes = "".join(f"volume=enable='between(t,{a},{b})':volume=0," for a, b in seg.get("mute", []))
    if has_audio(asrc) and vol > 0:
        ai = "1:a:0" if alt else "0:a:0"
        af = f"[{ai}]atempo={speed_a}," if speed_a != 1.0 else f"[{ai}]"
        af += f"{mutes}highpass=f=80,volume={vol},apad,atrim=0:{dur},afade=t=in:d={max(fi, 0.05)},afade=t=out:st={max(dur - max(fo, 0.08), 0)}:d={max(fo, 0.08)}[a]"
        amap, ain = ["-map", "[a]"], ain0
    else:
        af, ain, amap = "", ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"], ["-map", "1:a"]
    if alt and not af:
        ain = ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
    fc = vf + (";" + af if af else "")
    sh(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", str(src), *ain,
        "-filter_complex", fc, "-map", "[v]", *amap, "-t", str(dur), "-r", str(fps), *enc, str(part)])
    part.replace(out)
    return out


def segment_wav(part):
    """A segment's sound as 48 kHz stereo PCM, exactly as long as the slot the concat demuxer gives the segment.

    That slot is the container duration, not the video stream's: when a source clip ends before the planned
    out-point the picture is a few frames short, the join leaves that gap, and the sound must keep it too.
    """
    wav = part.with_name(part.stem + ".slot.wav")
    if wav.exists():
        return wav
    vdur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "csv=p=0", str(part)], capture_output=True, text=True).stdout.strip()
    tmp = wav.with_name(wav.stem + ".part.wav")
    sh(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(part), "-map", "0:a:0",
        "-af", f"aresample=48000,apad,atrim=0:{vdur}", "-ac", "2", "-c:a", "pcm_s16le", str(tmp)])
    tmp.replace(wav)
    return wav


def seg_duration(seg, fps=30):
    """Segment length rounded to whole frames: picture and sound get exactly this many frames' worth.

    A beat-cut length like 2.508 s would otherwise give 75 frames (2.500 s) of picture but 2.508 s of sound,
    and the final constant-frame-rate encode drops those sub-frame gaps: the sound drifted later shot by shot.
    """
    raw = seg.get("dur", 2.5) if "photo" in seg else (seg["out"] - seg["in"]) / seg.get("speed", 1.0)
    return round(raw * fps) / fps


def ass_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(plan, path, subs_on, titles_on):
    W, H = plan["width"], plan["height"]
    vertical = H > W
    sub_size = int(H * (0.062 if vertical else 0.092))
    title_size = int(H * (0.085 if vertical else 0.15))
    sub_margin = int(H * (0.22 if vertical else 0.07))
    header = f"""[Script Info]
ScriptType: v4.00+
ScaledBorderAndShadow: yes
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Baloo 2,{sub_size},&H00FFFFFF,&H000000FF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,{max(3, sub_size // 12)},2,2,60,60,{sub_margin},1
Style: Title,Pacifico,{title_size},&H00FFFFFF,&H000000FF,&H00502A8C,&H80000000,0,0,0,0,100,100,0,0,1,{max(4, title_size // 14)},3,5,80,80,0,1
Style: TitleSub,Poppins SemiBold,{int(title_size * 0.42)},&H00FFFFFF,&H000000FF,&H00101010,&H80000000,-1,0,0,0,100,100,1,0,1,3,2,5,80,80,0,1
Style: Label,Poppins ExtraBold,{int(sub_size * 1.05)},&H00FFFFFF,&H000000FF,&H00000000,&HB05A2BE0,-1,0,0,0,100,100,1,0,3,14,0,{1 if not vertical else 8},50,50,{int(H*0.06) if not vertical else int(H*0.12)},1
Style: Credit,Poppins SemiBold,{int(title_size * (0.36 if vertical else 0.25))},&H00FFFFFF,&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,1,0,1,2,2,5,60,60,0,1
Style: Pop,Poppins ExtraBold,{int(title_size * 0.62)},&H0000E5FF,&H000000FF,&H00101010,&H80000000,-1,0,0,0,100,100,1,0,1,{max(4, title_size // 16)},3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines, t = [], 0.0
    for seg in plan["segments"]:
        d = seg_duration(seg, plan["fps"])
        if subs_on:
            for s, e, text in seg.get("subs", []):
                lines.append(f"Dialogue: 0,{ass_time(t + s)},{ass_time(t + min(e, d))},Sub,,0,0,0,,{text}")
        for ti in (seg.get("titles") or ([seg["title"]] if "title" in seg else [])):
            if not titles_on:
                continue
            s, e = t + ti.get("start", 0), t + min(ti.get("end", d), d)
            style = ti.get("style", "Title")
            fade = r"{\fad(300,300)}"
            if style == "Title":
                cy = H * (0.42 if not vertical else 0.38)
                pos = rf"{{\pos({W/2},{cy})\fad(400,400)}}"
                lines.append(f"Dialogue: 1,{ass_time(s)},{ass_time(e)},Title,,0,0,0,,{pos}{ti['text']}")
                y = cy + title_size * 0.95
                if ti.get("sub"):
                    pos2 = rf"{{\pos({W/2},{y})\fad(400,400)}}"
                    lines.append(f"Dialogue: 1,{ass_time(s + 0.3)},{ass_time(e)},TitleSub,,0,0,0,,{pos2}{ti['sub']}")
                    y += title_size * 0.62
                for k, credit in enumerate(ti.get("credits", [])):  # smaller lines under the title block
                    pos3 = rf"{{\pos({W/2},{y + k * title_size * 0.4})\fad(400,400)}}"
                    lines.append(f"Dialogue: 1,{ass_time(s + 0.5)},{ass_time(e)},Credit,,0,0,0,,{pos3}{credit}")
            elif style == "Pop":
                pos = rf"{{\pos({W/2},{H * ti.get('y', 0.3)})\fad(150,250)\t(0,180,\fscx115\fscy115)\t(180,320,\fscx100\fscy100)}}"
                lines.append(f"Dialogue: 2,{ass_time(s)},{ass_time(e)},Pop,,0,0,0,,{pos}{ti['text']}")
            elif "pos" in ti:  # explicit placement as fractions of the frame, centred on the point
                px, py = ti["pos"]
                lines.append(f"Dialogue: 2,{ass_time(s)},{ass_time(e)},{style},,0,0,0,,"
                             rf"{{\an5\pos({W * px:.0f},{H * py:.0f})\fad(300,300)}}{ti['text']}")
            else:
                lines.append(f"Dialogue: 2,{ass_time(s)},{ass_time(e)},{style},,0,0,0,,{fade}{ti['text']}")
        t += d
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--subs", default="on")
    ap.add_argument("--titles", default="on")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=1, help="segments rendered in parallel")
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text())
    work.mkdir(exist_ok=True)
    (edit / "renders").mkdir(exist_ok=True)

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=a.jobs) as pool:  # each segment is an independent ffmpeg run
        futs = [pool.submit(render_segment, i, seg, plan, a.draft) for i, seg in enumerate(plan["segments"])]
        parts = []
        for i, f in enumerate(futs):
            parts.append(f.result())
            print(f"segment {i + 1}/{len(futs)}", flush=True)
    lst = work / f"{plan['name']}_concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = work / f"{plan['name']}_joined.mp4"
    sh(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    # Dialogue bed: never decode the audio of the stream-copied join. Every AAC segment carries ~21-43 ms of
    # encoder priming/padding that the concat keeps, so the sound drifted later and later (3.5 s by the end
    # of a 112-segment cut). Instead each segment's audio is decoded on its own, cut/padded to exactly its
    # picture length, and the PCM pieces are joined sample-exact.
    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        wavs = list(pool.map(segment_wav, parts))
    wlst = work / f"{plan['name']}_dlg_concat.txt"
    wlst.write_text("".join(f"file '{w}'\n" for w in wavs))
    dlg = work / f"{plan['name']}_dialogue.wav"
    sh(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(wlst), "-c", "copy", str(dlg)])

    ass = work / f"{plan['name']}_{a.subs}{a.titles}.ass"
    total = write_ass(plan, ass, a.subs == "on", a.titles == "on")

    # audio: dialogue bed + music tracks (optionally ducked under dialogue) -> loudness normalised
    inputs, fc, mus = ["-i", str(dlg)], [], []
    for k, m in enumerate(plan.get("music", [])):
        # -stream_loop: a cue longer than the rest of its track wraps round to the start instead of going silent
        inputs += ["-stream_loop", "-1", "-ss", str(m.get("from", 0)), "-t", str(m["dur"]), "-i", str(edit / m["src"])]
        f = m.get("fade", 1.5)
        fc.append(f"[{k + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={m.get('vol', 0.22)},"
                  f"afade=t=in:d={f},afade=t=out:st={m['dur'] - f}:d={f},adelay={int(m.get('at', 0) * 1000)}:all=1[m{k}]")
        mus.append(f"[m{k}]")
    if mus:
        # pad/trim the music bed to the exact timeline length: if it ends early, sidechaincompress stops
        # reading the dialogue key, asplit's buffer fills and the whole graph deadlocks
        fc.append(f"{''.join(mus)}amix=inputs={len(mus)}:normalize=0:duration=longest,"
                  f"apad=whole_dur={total:.3f},atrim=0:{total:.3f}[mus]")
        if plan.get("duck", True):
            fc.append("[0:a]asplit[dlg][key]")
            fc.append("[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[ducked]")
            fc.append("[dlg][ducked]amix=inputs=2:normalize=0:duration=first[mix]")
        else:
            fc.append("[0:a][mus]amix=inputs=2:normalize=0:duration=first[mix]")
    else:
        fc.append("[0:a]anull[mix]")
    # 1) audio-only pass -> wav. Mixing 8 audio inputs and the video in one graph stalls ffmpeg's
    #    interleaving, so the mix is rendered on its own and muxed afterwards (also reused across subs on/off).
    mix_key = hashlib.sha1(";".join(fc + inputs + [str(a.draft), wlst.read_text()]).encode()).hexdigest()[:10]
    mixed = work / f"{plan['name']}_mix_{mix_key}.wav"
    if not mixed.exists():
        measure = ";".join(fc + ["[mix]loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json[aout]"])
        r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *inputs, "-filter_complex", measure,
                            "-map", "[aout]", "-f", "null", "-"], capture_output=True, text=True)
        m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
        apply = ";".join(fc + [f"[mix]loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                               f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                               f"offset={m['target_offset']}:linear=true,aresample=48000[aout]"])
        sh(["ffmpeg", "-nostdin", "-y", "-v", "error", *inputs, "-filter_complex", apply, "-map", "[aout]",
            "-c:a", "pcm_s16le", str(mixed)])

    # 2) video pass: burn titles/captions, mux the finished mix
    esc = str(ass).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    fdir = str(fonts).replace(":", "\\:").replace("'", "\\'")
    suffix = a.out or f"{plan['name']}{'' if a.subs == 'on' else '_nocaptions'}{'_draft' if a.draft else ''}"
    out = edit / "renders" / f"{suffix}.mp4"
    sh(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(joined), "-i", str(mixed),
        "-filter_complex", f"[0:v]subtitles='{esc}':fontsdir='{fdir}'[vout]",
        "-map", "[vout]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast" if a.draft else "slow",
        "-crf", "26" if a.draft else "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", str(out)])
    print(f"wrote {out} ({total:.1f}s)")


if __name__ == "__main__":
    main()
