"""Turn a word into SVG outlines, so a wordmark renders the same without the font installed.

    python outline_text.py FONT TEXT [--weight 600] [--size 64] [--tracking -0.01] [--fill currentColor]

FONT is a .ttf/.otf/.woff file (static or variable; variable fonts are instanced
at --weight). --tracking is in em, like CSS letter-spacing. Prints a complete
SVG whose viewBox is tight to the advance width and the font's ascender/descender,
plus the cap height and x-height (as an XML comment) for lining the word up with a mark.

Needs fontTools (plus brotli for .woff2):
    uv run --with fonttools --with brotli python outline_text.py ...
or on NixOS without uv:
    nix shell --impure --expr 'with import <nixpkgs> {}; python3.withPackages (p: [ p.fonttools p.brotli ])' \
      -c python3 outline_text.py ...
Get Google fonts from github.com/google/fonts (ofl/<family>/) or @fontsource packages.
"""

import argparse

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("text")
    ap.add_argument("--weight", type=float, default=600)
    ap.add_argument("--size", type=float, default=64)
    ap.add_argument("--tracking", type=float, default=0.0)
    ap.add_argument("--fill", default="currentColor")
    a = ap.parse_args()

    font = TTFont(a.font)
    if "fvar" in font:
        from fontTools.varLib.instancer import instantiateVariableFont

        font = instantiateVariableFont(font, {"wght": a.weight})

    glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    scale = a.size / font["head"].unitsPerEm
    hhea, os2 = font["hhea"], font["OS/2"]
    ascent, descent = hhea.ascent * scale, -hhea.descent * scale

    pen = SVGPathPen(glyphs)
    x = 0.0
    for i, ch in enumerate(a.text):
        name = cmap[ord(ch)]
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, ascent)))
        x += hmtx[name][0] * scale
        if i < len(a.text) - 1:
            x += a.tracking * a.size

    w, h = round(x, 2), round(ascent + descent, 2)
    cap = round(os2.sCapHeight * scale, 2)
    xh = round(os2.sxHeight * scale, 2)
    print(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
        f"<!-- baseline y={round(ascent, 2)} cap-height={cap} x-height={xh} -->"
        f'<path fill="{a.fill}" d="{pen.getCommands()}"/></svg>'
    )


if __name__ == "__main__":
    main()
