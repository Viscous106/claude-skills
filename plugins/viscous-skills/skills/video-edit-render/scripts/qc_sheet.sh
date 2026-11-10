#!/usr/bin/env bash
# qc_sheet.sh VIDEO STEP COLS HEIGHT OUT.jpg -> timestamped grid of the whole render (one frame per STEP s)
set -euo pipefail
v="$1"; step="$2"; cols="$3"; h="$4"; out="$5"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v")
rows=$(python3 -c "import math;print(math.ceil($dur/$step/$cols))")
ffmpeg -nostdin -v error -y -i "$v" -vf "fps=1/$step,scale=-2:$h,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${cols}x${rows}:padding=3" -frames:v 1 "$out"
