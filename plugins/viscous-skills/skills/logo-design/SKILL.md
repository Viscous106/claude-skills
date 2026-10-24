---
name: logo-design
description: Use when the user wants a logo, brand mark, wordmark, favicon, app icon or social avatar designed, refined, judged or exported — including reproducing a reference image they like, building a full logo system for a website or app, or checking a mark for originality.
---

# Logo design

A logo is not designed to be charming, it is designed to identify (Paul Rand). The
marks that last are one idea, reducible to one glyph, monochrome first, readable at
16 px, and drawn together with the brand's type. Studio process, the dev-tool and web3
case studies, and the evidence behind every rule below are in `reference.md`.

## Rules learned the hard way

1. **The user's references are the brief, not a draft to correct.** When they send an
   image they like, reproduce what they like first (see "Working from a reference"),
   show it next to the original, and only then propose changes, one at a time, with a
   reason. Never hand back a different design and explain why theirs was wrong.
2. **Brief before drawing.** No concepts until `brief.md` exists and the user agreed to it.
3. **Drawing SVG by code is drawing blind.** Render and look after every change
   (`render_check.sh`). Judge at real sizes, never only at 500 px.
4. **Black first, colour last.** Settle the form in one colour; colour is a later layer.
5. **Diverge, then converge.** One designer converges on one look. Generate concepts in
   parallel subagents, each with a different lens, then shortlist with the user.
6. **Rounds end in a decision.** Every round goes to the picker and ends with the user's
   stars and note. Read `picks.json`; do not ask them to retype choices.
7. **Say plainly when your own work fails.** If a concept reads as something else
   (arrows, a D-pad, a pendant), say so and drop or fix it before showing it.

## Phase 0: brief (write `brief.md`, confirm with the user)

- What the company does, in one sentence a stranger understands, and the one idea the
  mark must carry. Goals list (3-6) every option will be judged against.
- 3-5 personality words. Audience. Where the mark lives: favicon, nav, app icon,
  avatar, docs, slides, print.
- The existing design system: read the repo for tokens (colours, fonts, radius, icon
  stroke). The mark must share its stroke, terminals and corner logic with the UI icons
  and its proportions with the brand typeface.
- Category clichés and owned shapes to avoid (`reference.md`, "Avoid list"), plus the
  user's own likes and dislikes and any references, saved into the working folder.

## Phase 1: ideas (cheap, wide)

1. **Word map**: branch from the core idea through synonyms, objects, verbs, metaphors.
2. **Shumate grid**: 4 sources (what the company does, its ideals, the name, abstract)
   x 3 mark types (wordmark, lettermark, symbol) = 12 cells. Fill each with 3 one-line
   ideas: 36 ideas as text before any SVG.
3. **Parallel lenses**: spawn 4-5 subagents at once, each with the brief and one lens
   (literal object, letterform from the name, abstract geometry, negative space,
   the brand's own UI or type detail promoted to a symbol). Each draws 4-6 monochrome
   thumbnails as SVG with `currentColor`, runs `render_check.sh` on them, and drops the
   ones that fail at 16 px.
4. Put the survivors (8-15) in one folder with `captions.json` and start the picker.

## Phase 2: routes

The user stars favourites. Develop 3-5 **routes**, each one idea with a one-line
rationale tied to the goals list. Show each in context: favicon in a browser tab, nav
bar next to the wordmark, app icon, avatar, light and dark. One route can be
wordmark-led; for many dev brands the wordmark is primary and the symbol is shorthand.

## Phase 3: build the chosen route properly

- `viewBox="0 0 256 256"` master on an 8- or 16-unit grid; 4-8% padding; coordinates to
  at most 2 decimals; exact angles (0/15/30/45/60/90).
- Build from 2-3 primitives (circle, rounded rect, polygon, arcs). Fewest anchors that
  hold the shape. One stroke weight, one terminal style, one corner-radius family across
  mark and wordmark. A monoline stroke must be at least 8% of the mark's width to read
  at 24 px.
- Optical corrections: round and pointed forms overshoot flat edges by 1-3% (points up
  to 5%); a circle needs about 11% more extent than a square to look equal; horizontals
  slightly thinner than verticals; centre slightly above the geometric centre; the
  white-on-dark version a touch thinner than the dark-on-light one.
- Master file: no `<text>` (outline it with `outline_text.py`), no rasters, filters,
  masks or clip paths; strokes expanded to fills at the end (`inkscape` actions or
  `picosvg`); `role="img"` and `<title>`; `svgo --multipass`.
- Wordmark: start from the brand typeface, adjust only what earns its place (one letter
  echoing the symbol, tightened spacing). Kern by eye; flip the word upside down to judge
  spacing without reading it. Fix the mark-to-cap-height ratio and the gap per lockup.

## Phase 4: test (every iteration)

`render_check.sh` (light, dark, 64/32/16 px, silhouette, squint blur) and `svg_audit.py`.
Also: does it read without the name; can someone redraw it from a one-line description;
mirrored and rotated, does it read as something unintended; next to 3-5 strong logos
from the category at the same size, does it hold its own (shelf test).

## Phase 5: originality

Reverse image search (Google Lens, TinEye); WIPO Global Brand Database image search
with Vienna codes; USPTO design search codes (no image search there). Compare against
the owned-shape list. Log near matches in the folder and tell the user. AI-generated
images are not copyrightable in the US on their own; a human rebuild strengthens the
claim. Recommend a professional clearance search before any trademark filing.

## Phase 6: the logo system (deliver as files, not just a picture)

- Symbol, wordmark, horizontal lockup, stacked lockup; each in colour, black, white.
- Rules: clear space and minimum size expressed in units of the mark itself.
- `export_set.sh`: `icon.svg` (follows dark mode), `favicon.ico`, `apple-touch-icon.png`,
  `icon-192/512.png`, maskable 512, 1024 avatar, manifest, `<head>` tags.
- Social share image 1200x630; README header; product code component that draws the
  symbol with `currentColor`; a short `brand.md` with all of the above.

## Working from a reference image

1. Trace it to see its structure: `vtracer --input ref.png --output ref.svg --colormode color --mode spline`.
   The trace is a reference, never the master (hundreds of colours, thousands of nodes).
2. Rebuild it from primitives on the grid, as close as possible, and render it next to
   the original. Ask the user what is right and wrong before changing anything.
3. Then offer the simplified flat version for small sizes as a separate file.

## Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `render_check.sh OUT.png a.svg ...` | contact sheet: light, dark, 64/32/16 px, silhouette, squint blur |
| `svg_audit.py a.svg ...` | master-file errors and warnings (text, rasters, colours, size, nodes) |
| `outline_text.py FONT TEXT --weight 600` | wordmark as SVG outlines with cap and x-height |
| `export_set.sh mark.svg out/ FG BG DARK_FG` | favicon, app icon and avatar set with manifest and tags |
| `node picker.mjs DIR --name Brand` | local shortlist page; stars and note land in `DIR/picks.json` |

Tools on NixOS: `magick` is on PATH; get the rest with
`nix shell nixpkgs#librsvg nixpkgs#vtracer nixpkgs#resvg nixpkgs#svgo nixpkgs#inkscape`.
For fontTools use `uv run --with fonttools --with brotli python ...`. Nix needs the
daemon socket and the picker needs a reachable port: in a per-command sandbox, run those
commands unsandboxed. Keep all work in one project folder, never only in a temp dir.
