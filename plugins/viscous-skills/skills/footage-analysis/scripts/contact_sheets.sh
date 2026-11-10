#!/usr/bin/env bash
# One contact sheet per clip: 24 evenly spaced frames, each stamped with its source timestamp.
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p edit/frames
for f in *.mp4; do
  b="${f%.mp4}"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  step=$(python3 -c "print(max(0.5, $dur/24))")
  ffmpeg -nostdin -v error -y -i "$f" -map 0:v:0 -vf "fps=1/$step,scale=-2:240,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=6x4:padding=4" \
    -frames:v 1 "edit/frames/$b.jpg"
  echo "$b step=${step}s"
done
