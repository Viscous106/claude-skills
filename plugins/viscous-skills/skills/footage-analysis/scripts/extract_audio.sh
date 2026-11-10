#!/usr/bin/env bash
# audio/<key>.wav for every clip in probe.tsv with audio; key = folder__stem (spaces -> _)
root=/home/viscous/Viscous/Mumbai; cd "$(dirname "$0")/.."; mkdir -p audio
while IFS=$'\t' read -r folder rel dur w h rot aud ct; do
  [ "$aud" = 1 ] || continue
  key=$(echo "${folder}__$(basename "${rel%.*}")" | tr ' ' '_')
  [ -s "audio/$key.wav" ] || ffmpeg -nostdin -v error -y -i "$root/$rel" -map 0:a:0 -ac 1 -ar 16000 "audio/$key.wav"
done < probe.tsv
