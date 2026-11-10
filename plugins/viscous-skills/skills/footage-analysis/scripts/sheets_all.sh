#!/usr/bin/env bash
# frames/<key>.jpg: 24 keyframe-sampled, timestamped frames per clip listed in probe.tsv (skips Cat Cafe)
root=/home/viscous/Viscous/Mumbai; cd "$(dirname "$0")/.."; mkdir -p frames
while IFS=$'\t' read -r folder rel dur w h rot aud ct; do
  [ "$folder" = "Cat Cafe" ] && continue
  key=$(echo "${folder}__$(basename "${rel%.*}")" | tr ' ' '_')
  [ -s "frames/$key.jpg" ] && continue
  step=$(python3 -c "print($dur/24.5)")  # tile only emits a full 6x4 grid
  skip=(); python3 -c "import sys; sys.exit($dur < 60)" && skip=(-skip_frame nokey)
  ffmpeg -nostdin -v error -y "${skip[@]}" -i "$root/$rel" -map 0:v:0 \
    -vf "fps=1/$step,scale=-2:240,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=6x4:padding=4,format=yuvj420p" \
    -frames:v 1 "frames/$key.jpg" || echo "FAIL $key"
done < probe.tsv
