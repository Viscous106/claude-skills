#!/usr/bin/env bash
# photos/<folder>_<n>.jpg: labelled grids of every photo per folder, 36 per sheet
root=/home/viscous/Viscous/Mumbai; cd "$(dirname "$0")/.."
for d in "$root"/*/; do
  name=$(basename "$d" | tr ' ' '_'); [ "$name" = Cat_Cafe ] && continue
  mapfile -t files < <(find "$d" -type f \( -iname '*.png' -o -iname '*.jp*g' \) -not -path '*/content/*' | sort)
  for ((i=0; i<${#files[@]}; i+=36)); do
    python3 scripts/photo_sheet.py "photos/${name}_$((i/36+1)).jpg" "${files[@]:i:36}"
  done
done
