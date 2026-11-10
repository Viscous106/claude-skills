#!/usr/bin/env bash
# probe every video under the Mumbai folder -> TSV: folder, file, duration, w, h, rotation, has_audio, creation_time
root="$1"
find "$root" -type f \( -iname '*.mp4' -o -iname '*.mov' \) -not -path '*/content/*' | sort | while read -r f; do
  rel="${f#$root/}"
  j=$(ffprobe -v error -show_entries format=duration:format_tags=creation_time:stream=codec_type,width,height:stream_side_data=rotation -of json "$f")
  python3 - "$rel" "$j" <<'PY'
import json,sys
rel,j=sys.argv[1],json.loads(sys.argv[2])
v=[s for s in j.get("streams",[]) if s.get("codec_type")=="video"]
a=any(s.get("codec_type")=="audio" for s in j.get("streams",[]))
rot=""
if v:
    for sd in v[0].get("side_data_list",[]) or []:
        if "rotation" in sd: rot=sd["rotation"]
fmt=j.get("format",{})
print("\t".join(x or "-" for x in (map(str,[rel.split("/")[0], rel, round(float(fmt.get("duration",0)),1), v[0].get("width") if v else "", v[0].get("height") if v else "", rot, int(a), fmt.get("tags",{}).get("creation_time","")])))
PY
done
