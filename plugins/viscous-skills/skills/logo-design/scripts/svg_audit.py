"""Check logo SVGs for things that break a master file. Standard library only.

    python svg_audit.py mark1.svg [mark2.svg ...]

Flags, per file:
  ERROR  live <text>, embedded rasters (<image>), filters, masks, clip paths,
         foreignObject, scripts, a missing viewBox
  WARN   more than 3 distinct colours, gradients, strokes thinner than 8% of the
         mark's width (will not read at 24 px), file over 8 KB, more than 400
         path commands, coordinates with more than 2 decimals, no <title>
Exit code is 1 if any file has an ERROR.
"""

import re
import sys
import xml.etree.ElementTree as ET

BANNED = {"text": "live text, outline it", "image": "embedded raster", "filter": "filter effect",
          "mask": "mask", "clipPath": "clip path", "foreignObject": "foreignObject", "script": "script"}
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)")


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def audit(path: str) -> bool:
    raw = open(path, encoding="utf-8").read()
    root = ET.fromstring(raw)
    errors, warns = [], []

    vb = root.get("viewBox")
    if not vb:
        errors.append("no viewBox (will not scale)")
        width = None
    else:
        width = float(vb.split()[2])

    tags = {local(el.tag) for el in root.iter()}
    for tag, why in BANNED.items():
        if tag in tags:
            errors.append(f"<{tag}>: {why}")
    if tags & {"linearGradient", "radialGradient"}:
        warns.append("gradient: keep for a colour variant only, the master should be flat")
    if "title" not in tags:
        warns.append("no <title> (add one, with role=\"img\", for accessibility)")

    colors = {c.lower() for c in COLOR.findall(raw)}
    if len(colors) > 3:
        shown = ", ".join(sorted(colors)[:6]) + (", ..." if len(colors) > 6 else "")
        warns.append(f"{len(colors)} colours: {shown}")

    if width:
        for el in root.iter():
            sw = el.get("stroke-width")
            if sw and el.get("stroke") not in (None, "none"):
                try:
                    if float(sw) < 0.08 * width * 0.5:
                        warns.append(f"stroke-width {sw} is thin for a {width:g}-unit mark; check it at 24 px")
                        break
                except ValueError:
                    pass

    size = len(raw.encode())
    if size > 8192:
        warns.append(f"{size / 1024:.1f} KB: run svgo --multipass, or rebuild with fewer nodes")
    cmds = sum(len(re.findall(r"[MLHVCSQTAZmlhvcsqtaz]", d)) for d in re.findall(r'\sd="([^"]*)"', raw))
    if cmds > 400:
        warns.append(f"{cmds} path commands: traced or over-detailed; rebuild from primitives")
    if re.search(r"\d\.\d{3,}", raw):
        warns.append("coordinates with 3+ decimals: snap to the grid")

    status = "ERROR" if errors else ("WARN" if warns else "OK")
    print(f"{status:5}  {path}")
    for e in errors:
        print(f"       error: {e}")
    for w in warns:
        print(f"       warn:  {w}")
    return not errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ok = all([audit(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
