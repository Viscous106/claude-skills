#!/usr/bin/env bash
# Build the full icon set for a website from one master mark.
#
#   export_set.sh MARK.svg OUT_DIR [FG] [BG] [DARK_FG]
#
#   MARK.svg  the symbol, square viewBox, drawn with currentColor
#   FG / BG   colours for the solid app tiles (default ink on porcelain white)
#   DARK_FG   colour of the browser-tab icon when the browser is in dark mode
#
# Writes, following https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs
#   icon.svg               browser tab icon, switches colour with prefers-color-scheme
#   favicon.ico            32 + 16 px fallback for old browsers and some crawlers
#   apple-touch-icon.png   180 px, solid background, iOS adds its own rounding
#   icon-192.png icon-512.png         web app manifest icons
#   icon-512-maskable.png  mark kept inside the 80% safe zone for Android masks
#   avatar-1024.png        GitHub / X / Discord avatar, safe for a circular crop
#   head.html manifest.webmanifest    the tags and manifest that reference them
set -euo pipefail

if [ $# -lt 2 ]; then
  sed -n '2,19p' "$0"
  exit 1
fi

mark=$1
out=$2
FG=${3:-#0E1018}
BG=${4:-#FFFFFF}
DARK_FG=${5:-#ECEEF2}

if command -v rsvg-convert >/dev/null; then
  rsvg() { rsvg-convert "$@"; }
else
  rsvg() { nix shell nixpkgs#librsvg -c rsvg-convert "$@"; }
fi
command -v magick >/dev/null || { echo "needs ImageMagick (magick)" >&2; exit 1; }

mkdir -p "$out"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
printf 'svg { color: %s; }\n' "$FG" > "$work/fg.css"

# Mark on a solid square tile. pad = share of the tile left empty on each side.
tile() { # size pad out
  local inner
  inner=$(awk -v s="$1" -v p="$2" 'BEGIN { printf "%d", s * (1 - 2 * p) }')
  rsvg -s "$work/fg.css" -w "$inner" -h "$inner" -a "$mark" -o "$work/m.png"
  magick -size "$1x$1" "xc:$BG" "$work/m.png" -gravity center -composite "$3"
}

# Browser tab icon: the mark itself, with a colour that follows the theme.
sed -E "0,/<svg[^>]*>/s//&<style>svg{color:$FG}@media (prefers-color-scheme:dark){svg{color:$DARK_FG}}<\/style>/" \
  "$mark" > "$out/icon.svg"

tile 32 0.06 "$work/32.png"
tile 16 0.04 "$work/16.png"
magick "$work/16.png" "$work/32.png" "$out/favicon.ico"
tile 180 0.16 "$out/apple-touch-icon.png"
tile 192 0.14 "$out/icon-192.png"
tile 512 0.14 "$out/icon-512.png"
tile 512 0.22 "$out/icon-512-maskable.png"
tile 1024 0.2 "$out/avatar-1024.png"

cat > "$out/manifest.webmanifest" <<EOF
{
  "icons": [
    { "src": "/icon-192.png", "type": "image/png", "sizes": "192x192" },
    { "src": "/icon-512.png", "type": "image/png", "sizes": "512x512" },
    { "src": "/icon-512-maskable.png", "type": "image/png", "sizes": "512x512", "purpose": "maskable" }
  ]
}
EOF

cat > "$out/head.html" <<'EOF'
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
EOF

ls -1 "$out"
