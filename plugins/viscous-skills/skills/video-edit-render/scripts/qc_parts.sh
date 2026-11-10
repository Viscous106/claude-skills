#!/usr/bin/env bash
# qc_parts.sh VIDEO PARTLEN STEP COLS ROWS HEIGHT OUTPREFIX -> one timestamped grid per PARTLEN seconds
v="$1"; len="$2"; step="$3"; cols="$4"; rows="$5"; h="$6"; pre="$7"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v")
n=$(python3 -c "import math;print(math.ceil($dur/$len))")
for ((p=0; p<n; p++)); do
  s=$((p*len))
  ffmpeg -nostdin -v error -y -ss "$s" -t "$len" -copyts -i "$v" \
    -vf "fps=1/$step,scale=-2:$h,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${cols}x${rows}:padding=3" \
    -frames:v 1 "${pre}_$p.jpg"
done
