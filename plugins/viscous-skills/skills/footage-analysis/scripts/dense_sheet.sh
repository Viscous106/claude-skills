#!/usr/bin/env bash
# dense_sheet.sh CLIP STEP_SECONDS COLS HEIGHT -> edit/frames/<clip>_dense.jpg (whole clip, one frame per STEP)
set -euo pipefail
cd "$(dirname "$0")/../.."
f="$1"; step="$2"; cols="$3"; h="${4:-240}"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
rows=$(python3 -c "import math;print(math.ceil($dur/$step/$cols))")
ffmpeg -nostdin -v error -y -i "$f" -map 0:v:0 -vf "fps=1/$step,scale=-2:$h,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${cols}x${rows}:padding=3" \
  -frames:v 1 "edit/frames/${f%.mp4}_dense.jpg"
