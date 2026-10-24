#!/usr/bin/env bash
# Render logo SVGs the way people will actually see them, on one contact sheet.
#
#   render_check.sh OUT.png mark1.svg [mark2.svg ...]
#
# Each row is one mark: large on light, large on dark, then 64 / 32 / 16 px on
# light and dark, then a one-colour silhouette. Marks should draw with
# currentColor so the light/dark colours below apply; marks with baked-in
# colours still render, they just will not invert.
#
# Env overrides: LIGHT_BG, LIGHT_FG, DARK_BG, DARK_FG, LABEL_FONT.
# Accent colour: parts marked class="accent" (filled) or class="accent-line"
# (stroked) take LIGHT_ACCENT / DARK_ACCENT when set; otherwise they stay
# currentColor, so the same file is the one-colour and the accent version.
# (librsvg ignores CSS custom properties, so use classes, not var(--x).)
set -euo pipefail

if [ $# -lt 2 ]; then
  sed -n '2,12p' "$0"
  exit 1
fi

out=$1
shift

LIGHT_BG=${LIGHT_BG:-#F4F5F7}
LIGHT_FG=${LIGHT_FG:-#0E1018}
DARK_BG=${DARK_BG:-#0B0C0F}
DARK_FG=${DARK_FG:-#ECEEF2}
LABEL_FONT=${LABEL_FONT:-DejaVu-Sans}

if command -v rsvg-convert >/dev/null; then
  rsvg() { rsvg-convert "$@"; }
else
  rsvg() { nix shell nixpkgs#librsvg -c rsvg-convert "$@"; }
fi
command -v magick >/dev/null || { echo "needs ImageMagick (magick)" >&2; exit 1; }

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

css() { # fg name [accent]
  printf 'svg { color: %s; }\n' "$1" > "$work/$2.css"
  if [ -n "${3:-}" ]; then
    printf '.accent { fill: %s; } .accent-line { stroke: %s; }\n' "$3" "$3" >> "$work/$2.css"
  fi
}
css "$LIGHT_FG" light "${LIGHT_ACCENT:-}"
css "$DARK_FG" dark "${DARK_ACCENT:-}"

# Render one SVG at a size on a background colour, with currentColor set,
# centred in a square cell (default: the size plus a quarter of padding).
render() { # svg size theme bg out [cell]
  local cell=${6:-$(( $2 + $2 / 4 ))}
  rsvg -s "$work/$3.css" -w "$2" -h "$2" -a "$1" -o "$work/raw.png"
  magick "$work/raw.png" -background "$4" -gravity center -extent "${cell}x${cell}" -flatten "$5"
}

i=0
for svg in "$@"; do
  i=$((i + 1))
  name=$(basename "$svg" .svg)
  render "$svg" 220 light "$LIGHT_BG" "$work/$i-L.png"
  render "$svg" 220 dark "$DARK_BG" "$work/$i-D.png"
  for s in 64 32 16; do
    render "$svg" "$s" light "$LIGHT_BG" "$work/$i-L$s.png" 80
    render "$svg" "$s" dark "$DARK_BG" "$work/$i-D$s.png" 80
  done
  # Silhouette: every non-transparent pixel in one colour. Shows whether the
  # shape still reads without colour, gradients or inner detail.
  rsvg -s "$work/light.css" -w 120 -h 120 -a "$svg" -o "$work/raw.png"
  magick "$work/raw.png" -alpha extract -negate -background white -alpha off "$work/sil.png"
  # Squint test: the same silhouette, blurred. The idea should survive the blur.
  magick "$work/sil.png" -blur 0x5 "$work/blur.png"
  magick "$work/sil.png" "$work/blur.png" -background white -gravity center -append "$work/$i-S.png"

  magick \
    \( "$work/$i-L64.png" "$work/$i-L32.png" "$work/$i-L16.png" -background "$LIGHT_BG" -gravity center +append \) \
    \( "$work/$i-D64.png" "$work/$i-D32.png" "$work/$i-D16.png" -background "$DARK_BG" -gravity center +append \) \
    -append "$work/$i-small.png"
  magick "$work/$i-small.png" -background "$LIGHT_BG" -gravity center -extent "240x275" "$work/$i-small.png"
  magick "$work/$i-S.png" -background white -gravity center -extent 150x275 "$work/$i-S.png"
  magick "$work/$i-L.png" "$work/$i-D.png" "$work/$i-small.png" "$work/$i-S.png" \
    -background "$LIGHT_BG" -gravity center +append \
    -gravity northwest -background "$LIGHT_BG" -splice 0x24 \
    -font "$LABEL_FONT" -pointsize 15 -fill "#565C6B" -annotate +8+4 "$name" \
    "$work/row-$(printf '%03d' "$i").png"
done

magick "$work"/row-*.png -background "$LIGHT_BG" -append "$out"
echo "wrote $out ($i marks)"
